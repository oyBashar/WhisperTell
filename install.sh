#!/usr/bin/env bash
# WhisperTell — Quick Installer
# Author: oyBashar (github.com/oyBashar)
# Usage: bash install.sh

set -e

CYAN="\033[96m"; GREEN="\033[92m"; YELLOW="\033[93m"
RED="\033[91m"; GREY="\033[90m"; RESET="\033[0m"

echo -e "${CYAN}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║    WhisperTell v2.0 — Installer      ║"
echo "  ║    by oyBashar · github.com/oyBashar ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${RESET}"

# Detect environment
if [ -d "/data/data/com.termux" ]; then ENV="termux"; else ENV="linux"; fi
echo -e "${YELLOW}  Platform: $ENV${RESET}\n"

# Python check
if ! command -v python3 &>/dev/null; then
    echo -e "${CYAN}  Installing Python 3…${RESET}"
    if [ "$ENV" = "termux" ]; then
        pkg install python -y
    elif command -v apt &>/dev/null; then
        sudo apt install python3 python3-pip -y
    elif command -v pacman &>/dev/null; then
        sudo pacman -S python python-pip --noconfirm
    else
        echo -e "${RED}  Could not auto-install Python. Please install Python 3 manually.${RESET}"
        exit 1
    fi
fi

PY=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}  ✓ Python $PY found${RESET}"

# pip check
if ! command -v pip3 &>/dev/null && ! command -v pip &>/dev/null; then
    if [ "$ENV" = "termux" ]; then pkg install python -y
    else sudo apt install python3-pip -y 2>/dev/null || true; fi
fi

# paho-mqtt
echo -e "${CYAN}  Installing paho-mqtt (for World Mode)…${RESET}"
python3 -m pip install paho-mqtt --quiet && \
    echo -e "${GREEN}  ✓ paho-mqtt installed${RESET}" || \
    echo -e "${YELLOW}  ⚠ paho-mqtt install failed — LAN Mode will still work${RESET}"

# chmod
chmod +x "$(dirname "$0")/whispertell.py"
echo -e "${GREEN}  ✓ whispertell.py is ready${RESET}"

echo ""
echo -e "${CYAN}  ────────────────────────────────────${RESET}"
echo -e "${GREEN}  Installation complete!${RESET}"
echo -e "${CYAN}  ────────────────────────────────────${RESET}"
echo ""
echo -e "  Launch with:  ${GREEN}python3 whispertell.py${RESET}"
echo ""
