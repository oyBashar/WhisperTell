<div align="center">

# ⚡ WhisperTell // Anonymous Chat
▒▓█ W H ! $ P 3 R T 3 L L █▓▒
sy$tem.init() l0ading... ███▒▒▒ wh1sp3r_t3ll.exe c0nn3cting ▒▒▒ acc3$$: GR@NTED ⚡ ▒▒ 0101 // GL!TCH // 0101 ▒▒
`secure • anonymous • real-time`

</div>

**Serverless Terminal Chat — LAN & Worldwide**

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Termux%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square)]()
[![Author](https://img.shields.io/badge/Author-oyBashar-cyan?style=flat-square&logo=github)](https://github.com/oyBashar)

*No server setup. No accounts. No tracking. Just chat.*

</div>

---

## What is WhisperTell?

WhisperTell is a **terminal-based chat tool** you can run on Termux (Android), Linux, or macOS. It has two modes:

| Mode | Works where? | Internet needed? |
|------|-------------|------------------|
| 🔵 **LAN Mode** | Same Wi-Fi / hotspot only | ❌ No |
| 🟢 **World Mode** | Anywhere on Earth | ✅ Yes (free relay) |

**World Mode** uses [HiveMQ's free public MQTT broker](https://www.hivemq.com/public-mqtt-broker/) as a relay. You don't set up anything — it just works. Messages are in-transit only; nothing is stored.

---

## Screenshot Preview

```
  ╔════════════════════════════════════════════╗
  ◈ Bashar   🌍 Worldwide (MQTT)  ·  3 online
  ────────────────────────────────────────────
  [1]  Direct Message    (private chat)
  [2]  Make Channel      (create & join room)
  [3]  Join Channel      (browse open rooms)
  [4]  Peer List         (who is online)
  [q]  Quit
  ╚════════════════════════════════════════════╝

  ▶ Choice:
```

---

## Installation

### 📱 On Termux (Android) — Recommended

> Termux is a free terminal emulator for Android. Install it from [F-Droid](https://f-droid.org/en/packages/com.termux/) (recommended) or Google Play.

**Step 1 — Open Termux and update packages**
```bash
pkg update && pkg upgrade -y
```

**Step 2 — Install Python and Git**
```bash
pkg install python git -y
```

**Step 3 — Install paho-mqtt** *(needed for World Mode)*
```bash
pip install paho-mqtt
```

**Step 4 — Clone WhisperTell from GitHub**
```bash
git clone https://github.com/oyBashar/WhisperTell.git
```

**Step 5 — Go into the folder**
```bash
cd WhisperTell
```

**Step 6 — Make the script executable**
```bash
chmod +x whispertell.py
```

**Step 7 — Run it!**
```bash
python whispertell.py
```

---

### 🐧 On Linux (Ubuntu / Debian / Arch)

**Step 1 — Install Python 3 and Git**

Ubuntu/Debian:
```bash
sudo apt update && sudo apt install python3 python3-pip git -y
```

Arch Linux:
```bash
sudo pacman -S python python-pip git --noconfirm
```

**Step 2 — Install paho-mqtt**
```bash
pip3 install paho-mqtt
```

**Step 3 — Clone and run**
```bash
git clone https://github.com/oyBashar/WhisperTell.git
cd WhisperTell
python3 whispertell.py
```

---

### 🍎 On macOS

**Step 1 — Install Homebrew** *(if not already installed)*
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Step 2 — Install Python and Git**
```bash
brew install python git
```

**Step 3 — Install paho-mqtt**
```bash
pip3 install paho-mqtt
```

**Step 4 — Clone and run**
```bash
git clone https://github.com/oyBashar/WhisperTell.git
cd WhisperTell
python3 whispertell.py
```

---

### ⚡ Quick One-Liner (Termux / Linux)

```bash
git clone https://github.com/oyBashar/WhisperTell.git && cd WhisperTell && pip install paho-mqtt && python3 whispertell.py
```

---

## Step-by-Step Usage Guide

### Step 1 — Launch WhisperTell

```bash
python3 whispertell.py
```

The banner and nickname prompt will appear.

---

### Step 2 — Enter your Nickname

```
  Enter your Nickname: Bashar
```

- Must be 1–24 characters
- No spaces (use underscores if you want, e.g. `cool_bashar`)
- This is how others will see you

---

### Step 3 — Choose a Connection Mode

```
  ══════════════════════════════════════════
  SELECT CONNECTION MODE
  ──────────────────────────────────────────
  [1]  LAN Mode    — same Wi-Fi only, no internet
  [2]  World Mode  — anywhere on Earth via MQTT
  ══════════════════════════════════════════

  ▶ Mode [1/2]:
```

**Type `1` for LAN Mode** — if you and your friends are on the same Wi-Fi/hotspot.

**Type `2` for World Mode** — if you want to chat with people anywhere on the planet.

> 💡 Both people must use the **same mode** to see each other.

---

### Step 4 — The Main Menu

```
  ══════════════════════════════════════════
  ◈ Bashar   🌍 Worldwide (MQTT)  ·  2 online
  ──────────────────────────────────────────
  [1]  Direct Message    (private chat)
  [2]  Make Channel      (create & join room)
  [3]  Join Channel      (browse open rooms)
  [4]  Peer List         (who is online)
  [q]  Quit
  ══════════════════════════════════════════

  ▶ Choice:
```

Peers discovered automatically appear in the counter. Wait 5–10 seconds for them to show up.

---

### Option 1 — Direct Message (DM)

Send a **private message** directly to one person.

```
  ▶ Choice: 1

  Who do you want to message?

  [1] Ahmed
  [2] Sara

  ▶ Nickname or number: 1
```

You can type the number or the full nickname. Then just chat:

```
  💬 DM ▸ Ahmed    exit = leave
  ══════════════════════════════

  ▶ hey, you there?

  13:22  You → Ahmed: hey, you there?
  13:22  Ahmed: yeah! what's up?

  ▶ exit
```

Type `exit` to go back to the main menu.

---

### Option 2 — Make Channel

Create a **group chat room** with a custom name.

```
  ▶ Choice: 2

  Channel name #gaming
```

You are now inside `#gaming`. Anyone who joins the same channel name will see your messages.

```
  📡 #gaming    exit = leave
  ══════════════════════════

  Joined. Say something.

  ▶ anyone want to play?

  13:30  You: anyone want to play?
  13:30    ⟡ Sara joined #gaming
  13:31  Sara: yes! let's go

  ▶ exit
```

Type `exit` to leave the channel.

---

### Option 3 — Join Channel

Browse **existing open channels** or type a name manually.

```
  ▶ Choice: 3

  Open channels:

  [1] #gaming
  [2] #general
  [3] #random

  ▶ Enter number or name: 2
```

If no channels are listed yet, you can still type a name to create/join it directly.

---

### Option 4 — Peer List

See who is currently online and which channels they are in.

```
  2 peer(s) online:

  ◉ Ahmed    🌍 Internet
      #general  #gaming

  ◉ Sara     192.168.1.55
      #general
```

---

### Quitting WhisperTell

From the main menu, type `q` and press Enter:

```
  ▶ Choice: q

  Goodbye! — WhisperTell by oyBashar
```

---

## How It Works

### LAN Mode (same network)

```
  ┌───────────────────────────────────────────────────────┐
  │                Your Local Wi-Fi Network               │
  │                                                       │
  │  [Your Phone]  ── UDP broadcast ──▶  [Friend Phone]  │
  │  whispertell                          whispertell     │
  │                                                       │
  │  Discovery : UDP port 55150 (every 4 seconds)        │
  │  Messages  : TCP port 55151 (peer-to-peer direct)    │
  └───────────────────────────────────────────────────────┘
```

### World Mode (internet)

```
  ┌──────────────────────────────────────────────────────────┐
  │                      The Internet                        │
  │                                                          │
  │   [You]  ──── MQTT ────▶  [ HiveMQ Relay ]  ◀── [Friend]│
  │                         broker.hivemq.com                │
  │                         (free public broker)             │
  │                                                          │
  │   Topic: whispertell/v2/channel/{name}                   │
  │   Topic: whispertell/v2/dm/{nickname}                    │
  │   Topic: whispertell/v2/presence                         │
  └──────────────────────────────────────────────────────────┘
```

- Messages are **never stored** — they are live, in-transit only
- No account or API key required
- The broker is run by HiveMQ — it is a free, public, shared resource

---

## Ports Used (LAN Mode only)

| Port  | Protocol | Purpose           |
|-------|----------|-------------------|
| 55150 | UDP      | Peer discovery    |
| 55151 | TCP      | Message delivery  |

---

## Troubleshooting

**Peers not appearing in LAN Mode?**
- Make sure everyone is on the **same Wi-Fi network or hotspot**
- Some routers block broadcast between clients. Try turning one phone into a hotspot
- Wait at least 10 seconds for the first discovery cycle

**Peers not appearing in World Mode?**
- Check your internet connection
- Wait 10–15 seconds — peers appear after their first presence broadcast
- Make sure paho-mqtt is installed: `pip install paho-mqtt`

**paho-mqtt not found?**
```bash
pip install paho-mqtt
# or on Termux:
pip install paho-mqtt
```

**Port already in use (LAN Mode)?**
```bash
ss -ulnp | grep 55150   # Linux/Termux
```
Close any other running instance of WhisperTell.

**Permission denied?**
```bash
chmod +x whispertell.py
```

---

## Updating WhisperTell

```bash
cd WhisperTell
git pull
```

---

## Uninstalling

```bash
cd ..
rm -rf WhisperTell
```

---

## Contributing

Pull requests are welcome!

1. Fork this repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Make your changes and commit: `git commit -m "Add my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## License

MIT License — free to use, modify, and share.

---

## Credits

**Created by [oyBashar](https://github.com/oyBashar)**

> *Built for the terminal. Made for Termux. Works worldwide.*
> *No servers were harmed in the making of this tool.*
