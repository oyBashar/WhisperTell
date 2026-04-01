#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════╗
# ║              WhisperTell v2.0                                ║
# ║   Serverless Chat — LAN + Worldwide via Public MQTT Relay    ║
# ║   Author  : oyBashar (github.com/oyBashar)                   ║
# ║   License : MIT                                              ║
# ╚══════════════════════════════════════════════════════════════╝
#
# MODES:
#   LAN Mode   — UDP broadcast, no internet needed, same Wi-Fi only
#   World Mode — Public MQTT relay, works anywhere on the planet
#
# World Mode uses broker.hivemq.com (free, no account, no setup)
# Nothing is stored — messages are in-transit only.

import socket
import threading
import json
import time
import sys
import os
from datetime import datetime

# ── Try importing paho-mqtt (needed for World Mode only) ──────
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

# ── Ports (LAN mode) ──────────────────────────────────────────
DISCOVERY_PORT     = 55150
MESSAGE_PORT       = 55151
BROADCAST_INTERVAL = 4
PEER_TIMEOUT       = 14

# ── MQTT (World Mode) ─────────────────────────────────────────
MQTT_BROKER  = "broker.hivemq.com"
MQTT_PORT    = 1883
MQTT_ROOT    = "whispertell/v2"   # namespace prefix

# ── ANSI ──────────────────────────────────────────────────────
C = {
    "reset": "\033[0m", "bold": "\033[1m", "dim": "\033[2m",
    "cyan": "\033[96m", "green": "\033[92m", "yellow": "\033[93m",
    "magenta": "\033[95m", "red": "\033[91m", "white": "\033[97m",
    "grey": "\033[90m", "blue": "\033[94m", "orange": "\033[33m",
}

def clr(color, text):
    return f"{C.get(color,'')}{text}{C['reset']}"

def ts():
    return datetime.now().strftime("%H:%M")

def clear():
    os.system("clear")

def hr(char="─", width=46):
    print("  " + clr("grey", char * width))


# ══════════════════════════════════════════════════════════════
#  LAN Backend
# ══════════════════════════════════════════════════════════════
class LANBackend:
    def __init__(self, nickname, on_message):
        self.nickname   = nickname
        self.on_message = on_message
        self.peers      = {}
        self.channels   = []
        self.running    = True
        self.lock       = threading.Lock()
        self.my_ip      = self._local_ip()

    def _local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]; s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def start(self):
        for fn in (self._broadcaster, self._disc_listener, self._tcp_listener):
            threading.Thread(target=fn, daemon=True).start()

    def stop(self):
        self.running = False

    # ── Discovery ─────────────────────────────────────────────
    def _broadcaster(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while self.running:
            pkt = json.dumps({"type":"announce","nick":self.nickname,
                              "ip":self.my_ip,"port":MESSAGE_PORT,
                              "channels":self.channels,"t":time.time()}).encode()
            try:
                sock.sendto(pkt, ("<broadcast>", DISCOVERY_PORT))
            except Exception: pass
            time.sleep(BROADCAST_INTERVAL)
        sock.close()

    def _disc_listener(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try: sock.bind(("", DISCOVERY_PORT))
        except OSError as e:
            print(clr("red", f"\n  [!] UDP port {DISCOVERY_PORT} busy: {e}")); return
        sock.settimeout(1)
        while self.running:
            try:
                raw, _ = sock.recvfrom(4096)
                msg = json.loads(raw.decode())
                if msg.get("type") == "announce" and msg["nick"] != self.nickname:
                    with self.lock:
                        self.peers[msg["nick"]] = {
                            "ip": msg["ip"], "port": msg["port"],
                            "channels": msg.get("channels",[]),
                            "last_seen": time.time()
                        }
            except socket.timeout:
                with self.lock:
                    stale = [n for n,p in self.peers.items()
                             if time.time()-p["last_seen"] > PEER_TIMEOUT]
                    for n in stale: del self.peers[n]
            except Exception: pass
        sock.close()

    def _tcp_listener(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try: srv.bind(("", MESSAGE_PORT))
        except OSError as e:
            print(clr("red", f"\n  [!] TCP port {MESSAGE_PORT} busy: {e}")); return
        srv.listen(20); srv.settimeout(1)
        while self.running:
            try:
                conn, _ = srv.accept()
                threading.Thread(target=self._handle, args=(conn,), daemon=True).start()
            except socket.timeout: pass
            except Exception: pass
        srv.close()

    def _handle(self, conn):
        try:
            data = conn.recv(8192).decode()
            self.on_message(json.loads(data))
        except Exception: pass
        finally: conn.close()

    # ── Send helpers ──────────────────────────────────────────
    def _tcp_send(self, ip, port, payload):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3); s.connect((ip, port))
            s.sendall(json.dumps(payload).encode()); s.close()
            return True
        except Exception: return False

    def send_channel(self, channel, content, mtype="channel"):
        payload = {"type": mtype, "from": self.nickname,
                   "channel": channel, "content": content, "t": time.time()}
        with self.lock:
            targets = [(p["ip"], p["port"]) for n, p in self.peers.items()
                       if channel in p.get("channels", [])]
        for ip, port in targets:
            threading.Thread(target=self._tcp_send,
                             args=(ip, port, payload), daemon=True).start()

    def send_dm(self, nick, content):
        with self.lock:
            peer = self.peers.get(nick)
        if not peer:
            return False
        payload = {"type":"dm","from":self.nickname,
                   "to":nick,"content":content,"t":time.time()}
        return self._tcp_send(peer["ip"], peer["port"], payload)

    def get_peers(self):
        with self.lock:
            return dict(self.peers)

    def get_available_channels(self):
        channels = set()
        with self.lock:
            for p in self.peers.values():
                for ch in p.get("channels", []):
                    channels.add(ch)
        return sorted(channels)

    def join_channel(self, ch):
        if ch not in self.channels:
            self.channels.append(ch)

    def leave_channel(self, ch):
        if ch in self.channels:
            self.channels.remove(ch)

    def info(self):
        return self.my_ip


# ══════════════════════════════════════════════════════════════
#  MQTT (World) Backend
# ══════════════════════════════════════════════════════════════
class MQTTBackend:
    def __init__(self, nickname, on_message):
        self.nickname   = nickname
        self.on_message = on_message
        self.channels   = []
        self.peers      = {}
        self.lock       = threading.Lock()
        self.running    = True
        self.connected  = False
        self._client    = None

    def start(self):
        client = mqtt.Client(client_id=f"wt_{self.nickname}_{int(time.time())}",
                             clean_session=True)
        client.on_connect    = self._on_connect
        client.on_message    = self._on_mqtt_message
        client.on_disconnect = self._on_disconnect
        self._client = client
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        except Exception as e:
            print(clr("red", f"\n  [!] MQTT connect failed: {e}\n"
                              f"      Check your internet connection.\n"))
            return
        client.loop_start()
        # Presence broadcast
        threading.Thread(target=self._presence_loop, daemon=True).start()

    def stop(self):
        self.running = False
        if self._client:
            self._client.disconnect()
            self._client.loop_stop()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            # Subscribe to presence and DMs
            client.subscribe(f"{MQTT_ROOT}/presence")
            client.subscribe(f"{MQTT_ROOT}/dm/{self.nickname}")
        else:
            print(clr("red", f"\n  [!] MQTT error rc={rc}"))

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False

    def _on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic   = msg.topic
            ptype   = payload.get("type","")
            sender  = payload.get("from","?")

            if sender == self.nickname:
                return  # ignore own messages

            if ptype == "presence":
                with self.lock:
                    self.peers[sender] = {
                        "channels":  payload.get("channels",[]),
                        "last_seen": time.time(),
                        "ip":        payload.get("ip","🌍 Internet")
                    }
                return

            self.on_message(payload)
        except Exception: pass

    def _presence_loop(self):
        while self.running:
            if self.connected:
                pkt = json.dumps({
                    "type":     "presence",
                    "from":     self.nickname,
                    "channels": self.channels,
                    "ip":       "🌍 Internet",
                    "t":        time.time()
                })
                try:
                    self._client.publish(f"{MQTT_ROOT}/presence", pkt)
                except Exception: pass

                # Evict stale peers
                with self.lock:
                    stale = [n for n, p in self.peers.items()
                             if time.time() - p["last_seen"] > 20]
                    for n in stale: del self.peers[n]

            time.sleep(5)

    def send_channel(self, channel, content, mtype="channel"):
        payload = json.dumps({"type": mtype, "from": self.nickname,
                              "channel": channel, "content": content,
                              "t": time.time()})
        try:
            self._client.publish(f"{MQTT_ROOT}/channel/{channel}", payload)
        except Exception: pass

    def send_dm(self, nick, content):
        payload = json.dumps({"type":"dm","from":self.nickname,
                              "to":nick,"content":content,"t":time.time()})
        try:
            self._client.publish(f"{MQTT_ROOT}/dm/{nick}", payload)
            return True
        except Exception: return False

    def get_peers(self):
        with self.lock:
            return dict(self.peers)

    def get_available_channels(self):
        channels = set()
        with self.lock:
            for p in self.peers.values():
                for ch in p.get("channels", []):
                    channels.add(ch)
        return sorted(channels)

    def join_channel(self, ch):
        if ch not in self.channels:
            self.channels.append(ch)
            try:
                self._client.subscribe(f"{MQTT_ROOT}/channel/{ch}")
            except Exception: pass

    def leave_channel(self, ch):
        if ch in self.channels:
            self.channels.remove(ch)
            try:
                self._client.unsubscribe(f"{MQTT_ROOT}/channel/{ch}")
            except Exception: pass

    def info(self):
        return "🌍 Worldwide (MQTT)"


# ══════════════════════════════════════════════════════════════
#  WhisperTell App
# ══════════════════════════════════════════════════════════════
class WhisperTell:
    def __init__(self):
        self.nickname       = ""
        self.backend        = None
        self.mode           = "menu"     # menu | channel | dm
        self.active_channel = None
        self.active_dm      = None
        self.running        = True
        self._notifs        = []

    # ── Message Handler ───────────────────────────────────────
    def _on_message(self, msg):
        mtype   = msg.get("type","")
        sender  = msg.get("from","?")
        content = msg.get("content","")
        channel = msg.get("channel","")
        stamp   = ts()

        if mtype == "channel":
            if self.mode == "channel" and self.active_channel == channel:
                print(f"\r\033[2K  {clr('grey',stamp)} "
                      f"{clr('yellow',f'#{channel}')} "
                      f"{clr('cyan',sender)}: {content}")
                print(f"  {clr('green','▶')} ", end="", flush=True)
            else:
                self._notifs.append(msg)
                if self.mode == "menu":
                    self._flash(msg)

        elif mtype == "dm":
            if self.mode == "dm" and self.active_dm == sender:
                print(f"\r\033[2K  {clr('grey',stamp)} "
                      f"{clr('magenta',sender)}: {content}")
                print(f"  {clr('green','▶')} ", end="", flush=True)
            else:
                self._notifs.append(msg)
                if self.mode == "menu":
                    self._flash(msg)

        elif mtype == "system":
            if self.mode == "channel" and self.active_channel == channel:
                print(f"\r\033[2K  {clr('grey', f'  ⟡ {content}')}")
                print(f"  {clr('green','▶')} ", end="", flush=True)

    def _flash(self, msg):
        mtype   = msg.get("type","")
        sender  = msg.get("from","?")
        channel = msg.get("channel","")
        preview = msg.get("content","")[:38]
        if mtype == "channel":
            print(f"\n  {clr('grey','[ping]')} {clr('yellow',f'#{channel}')} "
                  f"{clr('cyan',sender)}: {preview}")
        elif mtype == "dm":
            print(f"\n  {clr('grey','[DM]')} {clr('magenta',sender)}: {preview}")

    # ── Banner ────────────────────────────────────────────────
    def _banner(self):
        clear()
        print()
        print(clr("cyan",
            "  ░██╗░░░░░░░██╗██╗░░██╗██╗░██████╗██████╗░\n"
            "  ░██║░░██╗░░██║██║░░██║██║██╔════╝██╔══██╗\n"
            "  ░╚██╗████╗██╔╝███████║██║╚█████╗░██████╔╝\n"
            "  ░░████╔═████║░██╔══██║██║░╚═══██╗██╔═══╝░\n"
            "  ░░╚██╔╝░╚██╔╝░██║░░██║██║██████╔╝██║░░░░░\n"
            "  ░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚═╝╚═════╝░╚═╝░░░░░"
        ))
        print(clr("cyan",
            "  ████████╗███████╗██╗░░░░░██╗░░░░░\n"
            "  ╚══██╔══╝██╔════╝██║░░░░░██║░░░░░\n"
            "  ░░░██║░░░█████╗░░██║░░░░░██║░░░░░\n"
            "  ░░░██║░░░██╔══╝░░██║░░░░░██║░░░░░\n"
            "  ░░░██║░░░███████╗███████╗███████╗\n"
            "  ░░░╚═╝░░░╚══════╝╚══════╝╚══════╝"
        ))
        print()
        print(f"  {clr('yellow','v2.0')}  {clr('grey','·')}  "
              f"{clr('grey','by')} {clr('cyan','oyBashar')}  "
              f"{clr('grey','·')}  "
              f"{clr('grey','github.com/oyBashar/WhisperTell')}")
        print()

    # ── Mode Select ───────────────────────────────────────────
    def _select_mode(self):
        hr("═")
        print(f"  {clr('yellow','SELECT CONNECTION MODE')}")
        hr()
        print(f"  {clr('white','[1]')}  {clr('cyan','LAN Mode')}    "
              f"{clr('grey','— same Wi-Fi only, no internet')}")
        print(f"  {clr('white','[2]')}  {clr('green','World Mode')}  "
              f"{clr('grey','— anywhere on Earth via MQTT')}")
        hr("═")
        print()

        while True:
            raw = input(f"  {clr('cyan','▶ Mode [1/2]')}: ").strip()
            if raw == "1":
                return "lan"
            elif raw == "2":
                if not MQTT_AVAILABLE:
                    print(clr("red",
                        "\n  [!] paho-mqtt not installed.\n"
                        "      Run: pip install paho-mqtt\n"
                        "      Termux: pip install paho-mqtt\n"))
                    continue
                return "world"
            else:
                print(clr("grey", "  Please enter 1 or 2."))

    # ── Main Menu ─────────────────────────────────────────────
    def _menu(self):
        peers  = self.backend.get_peers()
        net    = self.backend.info()
        online = len(peers)
        color  = "green" if online else "grey"
        badge  = clr(color, f"{online} online")

        print()
        hr("═")
        print(f"  {clr('yellow','◈')} {clr('white', self.nickname)}  "
              f"{clr('grey', net)}  ·  {badge}")
        hr()
        print(f"  {clr('white','[1]')}  {clr('cyan','Direct Message')}  "
              f"  {clr('grey','(private chat)')}")
        print(f"  {clr('white','[2]')}  {clr('cyan','Make Channel')}    "
              f"  {clr('grey','(create & join room)')}")
        print(f"  {clr('white','[3]')}  {clr('cyan','Join Channel')}    "
              f"  {clr('grey','(browse open rooms)')}")
        print(f"  {clr('white','[4]')}  {clr('cyan','Peer List')}       "
              f"  {clr('grey','(who is online)')}")
        print(f"  {clr('white','[q]')}  {clr('grey','Quit')}")
        hr("═")
        print()

    # ── Peer List ─────────────────────────────────────────────
    def _show_peers(self):
        peers = self.backend.get_peers()
        print()
        if not peers:
            print(clr("grey", "  No peers visible yet. Give it a moment…"))
        else:
            print(clr("cyan", f"  {len(peers)} peer(s) online:\n"))
            for nick, info in peers.items():
                chs = "  ".join(clr("yellow", f"#{c}") for c in info.get("channels",[]))
                loc = info.get("ip", "?")
                print(f"  {clr('green','◉')} {clr('white', nick):<20s}  "
                      f"{clr('grey', loc)}")
                if chs:
                    print(f"      {chs}")
        print()
        input(clr("grey", "  [Enter to return] "))

    # ── DM ────────────────────────────────────────────────────
    def _do_dm(self):
        peers = self.backend.get_peers()
        peer_list = list(peers.keys())

        if not peer_list:
            print(clr("red", "\n  No peers online yet. Try again in a moment.\n"))
            time.sleep(1.5); return

        print(f"\n  {clr('cyan','Who do you want to message?')}\n")
        for i, nick in enumerate(peer_list, 1):
            print(f"  {clr('white',f'[{i}]')} {nick}")
        print()

        raw = input(f"  {clr('green','▶ Nickname or number')}: ").strip()
        if not raw: return

        if raw.isdigit():
            idx = int(raw) - 1
            target = peer_list[idx] if 0 <= idx < len(peer_list) else raw
        else:
            target = raw

        if target not in self.backend.get_peers():
            print(clr("red", f"\n  '{target}' not found.\n"))
            time.sleep(1); return

        self.mode      = "dm"
        self.active_dm = target
        clear()
        print()
        hr("═")
        print(f"  {clr('magenta','💬 DM')} {clr('grey','▸')} {clr('white', target)}"
              f"  {clr('grey','    exit = leave')}")
        hr("═")
        print(f"  {clr('grey','Start typing. Messages are delivered directly.')}")
        print()

        while self.running:
            try:
                text = input(f"  {clr('green','▶')} ")
            except (EOFError, KeyboardInterrupt): break
            if text.strip().lower() == "exit": break
            if text.strip():
                ok = self.backend.send_dm(target, text.strip())
                if ok:
                    print(f"\r\033[2K  {clr('grey', ts())} "
                          f"{clr('green','You')} → {clr('magenta', target)}: {text.strip()}")
                else:
                    print(clr("red", f"  Could not reach {target}."))

        self.mode = "menu"; self.active_dm = None
        print(f"\n  {clr('grey','Left DM.')}\n"); time.sleep(0.5)

    # ── Channel: Make ─────────────────────────────────────────
    def _do_make_channel(self):
        print()
        raw = input(f"  {clr('cyan','Channel name')} {clr('grey','#')}").strip()
        channel = raw.lstrip("#").replace(" ", "-").lower()
        if not channel: return
        self.backend.join_channel(channel)
        self._enter_channel(channel)

    # ── Channel: Join ─────────────────────────────────────────
    def _do_join_channel(self):
        available = self.backend.get_available_channels()
        print()

        if available:
            print(clr("cyan", "  Open channels:\n"))
            for i, ch in enumerate(available, 1):
                print(f"  {clr('white',f'[{i}]')} {clr('yellow',f'#{ch}')}")
            print()
            raw = input(f"  {clr('green','▶ Enter number or name')}: ").strip()
            if not raw: return
            if raw.isdigit():
                idx = int(raw) - 1
                channel = available[idx] if 0 <= idx < len(available) else raw
            else:
                channel = raw.lstrip("#").replace(" ","-").lower()
        else:
            print(clr("grey", "  No channels visible yet. Type a name to create one."))
            raw = input(f"  {clr('cyan','Channel name')} {clr('grey','#')}").strip()
            channel = raw.lstrip("#").replace(" ","-").lower()

        if not channel: return
        self.backend.join_channel(channel)
        self._enter_channel(channel)

    def _enter_channel(self, channel):
        self.mode           = "channel"
        self.active_channel = channel
        clear()
        print()
        hr("═")
        print(f"  {clr('yellow','📡')} {clr('white', f'#{channel}')}"
              f"  {clr('grey','    exit = leave channel')}")
        hr("═")
        print(f"  {clr('grey','Joined. Say something.')}")
        print()

        self.backend.send_channel(channel, f"{self.nickname} joined #{channel}", mtype="system")

        while self.running:
            try:
                text = input(f"  {clr('green','▶')} ")
            except (EOFError, KeyboardInterrupt): break
            cmd = text.strip()
            if cmd.lower() == "exit":
                self.backend.send_channel(channel,
                    f"{self.nickname} left #{channel}", mtype="system")
                break
            if cmd:
                print(f"\r\033[2K  {clr('grey', ts())} {clr('green','You')}: {cmd}")
                self.backend.send_channel(channel, cmd)

        self.backend.leave_channel(channel)
        self.mode = "menu"; self.active_channel = None
        print(f"\n  {clr('grey','Left channel.')}\n"); time.sleep(0.5)

    # ── Run ───────────────────────────────────────────────────
    def run(self):
        self._banner()

        # Nickname
        hr()
        while not self.nickname:
            nick = input(f"  {clr('cyan','Your Nickname')}: ").strip()
            if 1 <= len(nick) <= 24:
                self.nickname = nick
            else:
                print(clr("red", "  Nickname must be 1–24 characters."))

        print()
        conn_mode = self._select_mode()

        # Start backend
        if conn_mode == "lan":
            self.backend = LANBackend(self.nickname, self._on_message)
            label = clr("blue", "LAN Mode")
        else:
            self.backend = MQTTBackend(self.nickname, self._on_message)
            label = clr("green", "World Mode (MQTT)")

        self.backend.start()

        print(f"\n  {clr('green','✓')} Connected — {label}")
        print(f"  {clr('grey', 'Discovering peers…  (give it 5–10 seconds)')}\n")
        time.sleep(1.5)

        # Menu loop
        while self.running:
            clear()
            self._banner()
            self._menu()
            try:
                choice = input(f"  {clr('cyan','▶ Choice')}: ").strip().lower()
            except (EOFError, KeyboardInterrupt): break

            if   choice == "1": self._do_dm()
            elif choice == "2": self._do_make_channel()
            elif choice == "3": self._do_join_channel()
            elif choice == "4": self._show_peers()
            elif choice in ("q","quit","exit"): break

        self.running = False
        self.backend.stop()
        print(f"\n  {clr('cyan','Goodbye!')}  {clr('grey','— WhisperTell by oyBashar')}\n")


# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        WhisperTell().run()
    except KeyboardInterrupt:
        print(f"\n  {clr('grey','Interrupted. Bye!')}\n")
        sys.exit(0)
