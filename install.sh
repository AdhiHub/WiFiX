#!/usr/bin/env bash

RED='\033[1;31m'; GREEN='\033[1;32m'; YELLOW='\033[1;33m'
CYAN='\033[1;36m'; RESET='\033[0m'

echo -e ""
echo -e "  ${RED}╔═══════════════════════════════════════════════╗${RESET}"
echo -e "  ${RED}║          ${GREEN}WiFiX${RED} - WiFi Auditor v1.0            ║${RESET}"
echo -e "  ${RED}║       ${YELLOW}Author: Adhithya J (AdhiHub)${RED}          ║${RESET}"
echo -e "  ${RED}╚═══════════════════════════════════════════════╝${RESET}"
echo -e ""

if [ "$(id -u)" != "0" ]; then
    echo -e "  ${YELLOW}[!] This script requires root privileges${RESET}"
    exec sudo bash "$0" "$@"
fi

echo -e "  ${CYAN}[*] Installing WiFiX...${RESET}\n"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="/usr/share/wifix"
LINK_PATH="/usr/local/bin/wifix"

if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
fi

mkdir -p "$INSTALL_DIR"

if command -v apt &>/dev/null; then
    apt install -y python3 python3-pip wireless-tools iw aircrack-ng 2>/dev/null || true
elif command -v pkg &>/dev/null; then
    pkg install python python-pip wireless-tools iw aircrack-ng -y 2>/dev/null || true
fi

cp "$SCRIPT_DIR/wifiX.py" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/wifiX.py"
ln -sf "$INSTALL_DIR/wifiX.py" "$LINK_PATH"
chmod +x "$LINK_PATH"

echo -e ""
echo -e "  ${GREEN}╔═══════════════════════════════════════════════╗${RESET}"
echo -e "  ${GREEN}║          Installation Complete!               ║${RESET}"
echo -e "  ${GREEN}╚═══════════════════════════════════════════════╝${RESET}"
echo -e ""
echo -e "  ${CYAN}Usage:${RESET}"
echo -e "  ${GREEN}wifix                         ${YELLOW}Interactive menu${RESET}"
echo -e "  ${GREEN}wifix scan                    ${YELLOW}Scan networks${RESET}"
echo -e "  ${GREEN}wifix password --ssid MyWiFi  ${YELLOW}Test weak passwords${RESET}"
echo -e "  ${GREEN}wifix recover                 ${YELLOW}Show saved passwords${RESET}"
echo -e "  ${GREEN}wifix handshake               ${YELLOW}Capture WPA handshake${RESET}"
echo -e "  ${GREEN}wifix monitor                 ${YELLOW}Real-time signal monitor${RESET}"
echo -e "  ${GREEN}wifix wps                     ${YELLOW}Check WPS status${RESET}"
echo -e "  ${GREEN}wifix clients                 ${YELLOW}Discover clients${RESET}"
echo -e "  ${GREEN}wifix deauth                  ${YELLOW}Detect deauth attacks${RESET}"
echo -e ""
echo -e "  ${RED}╔═══════════════════════════════════════════════╗${RESET}"
echo -e "  ${RED}║  Use at your own risk, developer assumes      ║${RESET}"
echo -e "  ${RED}║  NO liability. For educational purposes only. ║${RESET}"
echo -e "  ${RED}╚═══════════════════════════════════════════════╝${RESET}"
echo -e ""
