<div align="center">

```text
   ██╗    ██╗██╗███████╗██╗██╗  ██╗
   ██║    ██║██║██╔════╝██║╚██╗██╔╝
   ██║ █╗ ██║██║█████╗  ██║ ╚███╔╝
   ██║███╗██║██║██╔══╝  ██║ ██╔██╗
   ╚███╔███╔╝██║██║     ██║██╔╝ ██╗
    ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝
```

# WiFiX — WiFi Network Auditor

**Author:** Adhithya J (AdhiHub)  
**Version:** 1.0.0  
**Type:** WiFi Security Auditing & Password Testing  
**Language:** Python 3  
**License:** MIT

```
WiFiX is a comprehensive WiFi auditing toolkit for scanning networks,
testing password strength, recovering saved credentials, capturing
WPA handshakes, monitoring signal strength, and detecting deauth
attacks — all from the terminal.
```

</div>

---

## Disclaimer

```text
[!] FOR AUTHORIZED SECURITY TESTING & RESEARCH ONLY
[!] Use at your own risk. Developer assumes NO liability.
[!] Only test networks you own or have explicit written permission.
[!] Unauthorized WiFi testing violates computer fraud and wiretap laws.
```

---

## Modules

| # | Module | What It Does |
|---|--------|-------------|
| 1 | **Scan Networks** | List all nearby APs with SSID, BSSID, channel, signal level, encryption type, WPS status |
| 2 | **Password Testing** | Weak password generation (250+ candidates), wordlist-based cracking (aircrack-ng/hashcat), default router password database (40+ brands) |
| 3 | **Saved Passwords** | Recover stored WiFi passwords from system (Linux NetworkManager / Windows netsh) |
| 4 | **Handshake Capture** | Capture WPA 4-way handshake for authorized testing |
| 5 | **Signal Monitor** | Real-time RSSI monitoring with visual signal bars, live refresh |
| 6 | **WPS Check** | Identify networks with WPS enabled |
| 7 | **Client Discovery** | Find devices connected to access points |
| 8 | **Deauth Detection** | Monitor for deauthentication attack packets |

---

## Features

- **8 modules** covering WiFi recon, auditing, password testing, and monitoring
- **Password testing engine** — 250+ weak password candidates generated per SSID
- **40+ router brand database** — Default passwords for Linksys, Netgear, TP-Link, D-Link, etc.
- **Weak password generator** — SSID-based pattern analysis, common words, year suffixes, leetspeak
- **Wordlist cracking** — Uses aircrack-ng or hashcat for handshake cracking
- **Signal monitor** — Real-time signal strength with color-coded visual bars
- **Deauth detection** — Monitor for deauth flood attacks
- **Saved password recovery** — Works on Linux (NetworkManager) and Windows (netsh)
- **Multi-interface support** — Automatically detects wireless interfaces
- **Color-coded terminal UI** — BSSID, signal bars, encryption types with colors
- **Export to file** — Save scan results as TXT or JSON
- **Interactive menu** — 8 guided options
- **CLI flags** — Direct command-line mode

---

## Installation

### One-liner

```bash
curl -fsSL https://raw.githubusercontent.com/AdhiHub/WiFiX/main/install.sh | sudo bash
```

After install:

```bash
wifix
```

### Manual

```bash
git clone https://github.com/AdhiHub/WiFiX.git
cd WiFiX
python3 wifiX.py -h
```

### Dependencies

```bash
# Linux
sudo apt install wireless-tools iw aircrack-ng

# Termux
pkg install wireless-tools iw aircrack-ng
```

---

## Usage

### Interactive Mode

```bash
wifix
```

8 numbered options with guided prompts.

### Command Line

```bash
wifix scan                         # Scan nearby networks
wifix password --ssid MyWiFi       # Test weak passwords for SSID
wifix password --ssid MyWiFi -w rockyou.txt  # Wordlist crack
wifix recover                      # Show saved WiFi passwords
wifix handshake --bssid AA:BB:CC:DD:EE:FF   # Capture handshake
wifix monitor                      # Real-time signal monitor
wifix wps                          # Check WPS-enabled networks
wifix clients                      # Discover connected clients
wifix deauth                       # Detect deauth attacks
```

### Output Examples

**Network Scan:**
```
─────────────────────────────────────────────────────────────────────
[ NEARBY NETWORKS — 8 found ]
─────────────────────────────────────────────────────────────────────
#    SSID                          BSSID              CH   Signal           Encrypt  WPS
─────────────────────────────────────────────────────────────────────
1    MyWiFi                        AA:BB:CC:11:22:33  6    ████████████░░░ -65 dBm  WPA2   No
2    NETGEAR42                     DD:EE:FF:44:55:66  1    ██████████░░░░░ -72 dBm  WPA2   Yes
3    TP-Link_ABCD                  AA:BB:11:22:33:44  11   ████████░░░░░░░ -80 dBm  WPA2   No
```

**Password Testing:**
```
[ PASSWORD CANDIDATES — 28 from SSID "MyWiFi" ]
─────────────────────────────────────────────────────────────────────
1  12345678          Common weak password
2  password          Common weak password
3  admin123          Common weak password
4  mywifi123         SSID word + 123
5  mywifi2025        SSID + year
6  MyWiFi2025!       SSID + year + !
─────────────────────────────────────────────────────────────────────

[ DEFAULT ROUTER PASSWORDS ]
  mywifi → admin   (Default password for router brand 'mywifi')
```

---

## Password Testing Engine

WiFiX generates password candidates based on:

| Strategy | Example |
|----------|---------|
| 200+ common weak passwords | `12345678`, `password`, `admin` |
| Router default database (40+ brands) | `linksys:admin`, `netgear:password` |
| SSID word + numbers | `MyWiFi123`, `MyWiFi2025` |
| SSID word + symbols | `MyWiFi!`, `MyWiFi@` |
| SSID pattern analysis | 3 letters + 3 digits patterns |
| Wordlist (aircrack-ng) | Any .cap handshake + wordlist |

---

## Architecture

```text
┌──────────────────────────────────────────────────┐
│                    WiFiX                          │
├──────────────────────────────────────────────────┤
│  CLI Parser → Mode Selector → Module Engine       │
│                                                     │
│  ┌──────┬────────┬──────┬──────┬──────┬────────┐  │
│  │ Scan │ Passwd │Recover│Handsh│Signal│WPS/Clnt│  │
│  ├──────┼────────┼──────┼──────┼──────┼────────┤  │
│  │iwlist│WeakGen │ NM   │airdmp│iwlist│airodmp │  │
│  │  iw  │DefDB   │netsh │airepl│refresh│ detect │  │
│  │ sort │aircrack│ parse│captur│ bars │ client │  │
│  └──────┴────────┴──────┴──────┴──────┴────────┘  │
│                                                     │
│  Wireless Tools Wrapper · Color UI · Export         │
└──────────────────────────────────────────────────┘
```

---

## Requirements

- **Linux** (recommended) with wireless adapter supporting monitor mode
- Python 3.6+
- `wireless-tools` (iwconfig, iwlist)
- `iw`
- Optional: `aircrack-ng`, `hashcat` (for handshake cracking)
- Root privileges for most operations

---

## FAQ

**Q: Can it crack any WiFi password?**  
A: No. It tests weak/common passwords and wordlists. Strong passwords won't be cracked.

**Q: Does it work on Windows?**  
A: Partial. Network scan requires Linux. Saved password recovery works on Windows.

**Q: Do I need a special WiFi adapter?**  
A: For scanning — no. For handshake capture/deauth — yes, needs monitor mode support.

**Q: Is this illegal?**  
A: Only use on networks you own. Unauthorized access is a crime.

---

## License

MIT License — see [LICENSE](LICENSE)

---

<p align="center">
  <b>WiFiX</b> — Part of the <a href="https://github.com/AdhiHub">AdhiHub</a> tool collection<br>
  © 2026 Adhithya J · Built with passion on Linux<br>
  <sub>For educational & authorized testing purposes only</sub>
</p>
