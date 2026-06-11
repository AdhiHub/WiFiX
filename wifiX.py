#!/usr/bin/env python3

import subprocess
import sys
import threading
import time
import os
import re
import json
import signal
from datetime import datetime

R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; C = "\033[96m"
M = "\033[95m"; B = "\033[94m"; W = "\033[97m"; D = "\033[90m"
N = "\033[0m"; BOLD = "\033[1m"

BANNER = f"""{R}
   ██╗    ██╗██╗███████╗██╗██╗  ██╗
   ██║    ██║██║██╔════╝██║╚██╗██╔╝
   ██║ █╗ ██║██║█████╗  ██║ ╚███╔╝
   ██║███╗██║██║██╔══╝  ██║ ██╔██╗
   ╚███╔███╔╝██║██║     ██║██╔╝ ██╗
    ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝
{W}   ════════════════════════════════════
{C}   WiFi Auditor  v1.0.0
{G}   Author: Adhithya J (AdhiHub)
{R}   ════════════════════════════════════{N}"""

DISCLAIMER = f"""{R}
╔═══════════════════════════════════════════════╗
║  DISCLAIMER: Use at your own risk.            ║
║  Developer assumes NO liability.              ║
║  For educational & authorized testing ONLY.   ║
║  Unauthorized WiFi testing is ILLEGAL.        ║
╚═══════════════════════════════════════════════╝{N}"""

WPA_WEAK_PASSWORDS = [
    "12345678", "password", "123456789", "1234567890", "admin",
    "admin123", "admin1234", "root", "1234", "12345", "123456",
    "qwerty123", "qwertyuiop", "letmein", "welcome", "monkey",
    "dragon", "master", "sunshine", "princess", "football",
    "iloveyou", "trustno1", "passw0rd", "00000000", "11111111",
    "22222222", "33333333", "44444444", "55555555", "66666666",
    "77777777", "88888888", "99999999", "default", "linksys",
    "netgear", "tp-link", "dlink", "belkin", "airlive", "silex",
    "router", "wireless", "wifi", "internet", "guest", "guest123",
    "changeme", "secret", "pass123", "test123", "abc123", "abc12345",
    "asdfgh", "zxcvbn", "qwerty1", "qwerty12", "qwerty12345",
    "1q2w3e4r", "1qaz2wsx", "123qwe", "qwe123", "pass", "pass12345",
    "admin2016", "admin2017", "admin2018", "admin2019", "admin2020",
    "admin2021", "admin2022", "admin2023", "admin2024", "admin2025",
    "Admin@123", "Admin123", "P@ssw0rd", "P@$$w0rd", "Password1",
    "password1", "password12", "password123", "root123", "toor",
    "support", "support123", "tech", "tech123", "wlan", "wlan123",
]

DEFAULT_SSID_PASSWORDS = {
    "linksys": "admin", "netgear": "password", "dlink": "admin",
    "tp-link": "admin", "belkin": "admin", "asus": "admin",
    "tplink": "admin", "tendawifi": "admin", "mercusys": "admin",
    "totolink": "admin", "edimax": "12345678", "zyxel": "1234",
    "huawei": "admin", "vodafone": "vodafone", "sky": "sky",
    "virgin": "virgin", "bt": "bt", "talktalk": "talktalk",
    "plusnet": "plusnet", "o2": "o2", "three": "three",
    "ee": "ee", "xfinity": "password", "optimum": "password",
    "spectrum": "password", "comcast": "password", "cox": "password",
    "verizon": "password", "att": "att", "sprint": "sprint",
    "t-mobile": "t-mobile", "rogers": "rogers", "bell": "bell",
    "telus": "telus", "shaw": "shaw", "cogeco": "cogeco",
    "videotron": "videotron", "sasktel": "sasktel", "mts": "mts",
}

WIFI_TOOLS = {}

def log(msg, color=W):
    print(f"{color}{msg}{N}")

def print_section(title):
    print(f"\n{Y}{'─'*55}{N}")
    print(f"{Y}[ {title} ]{N}")
    print(f"{Y}{'─'*55}{N}")

def print_table(rows, header, widths=None):
    if not rows:
        print(f"{D}  None found{N}")
        return
    print(f"\n{C}{'─'*80}{N}")
    print(f"{BOLD}{header}{N}")
    print(f"{C}{'─'*80}{N}")
    for row in rows:
        line = "  ".join(f"{str(x):<{w}}" for x, w in zip(row, widths)) if widths else "  ".join(str(x) for x in row)
        print(f"  {line}")
    print(f"{C}{'─'*80}{N}")

def check_tools():
    tools = {
        "iwconfig": "wireless-tools",
        "iwlist": "wireless-tools",
        "iw": "iw",
        "aircrack-ng": "aircrack-ng",
        "airodump-ng": "aircrack-ng",
        "aireplay-ng": "aircrack-ng",
        "airmon-ng": "aircrack-ng",
        "hashcat": "hashcat",
        "hcxdumptool": "hcxtools",
        "hcxpcaptool": "hcxtools",
    }
    available = {}
    for cmd, pkg in tools.items():
        try:
            subprocess.run([cmd, "--version"], capture_output=True, timeout=3)
            available[cmd] = True
        except:
            try:
                subprocess.run([cmd, "-h"], capture_output=True, timeout=3)
                available[cmd] = True
            except:
                available[cmd] = False
    return available

def get_interfaces():
    interfaces = []
    try:
        result = subprocess.run(["iwconfig"], capture_output=True, text=True, timeout=5)
        for line in result.stdout.split("\n"):
            if "IEEE 802.11" in line:
                iface = line.split()[0]
                interfaces.append(iface)
    except:
        pass
    if not interfaces:
        try:
            result = subprocess.run(["iw", "dev"], capture_output=True, text=True, timeout=5)
            for line in result.stdout.split("\n"):
                if "Interface" in line:
                    iface = line.split()[-1]
                    interfaces.append(iface)
        except:
            pass
    return interfaces

def scan_networks(interface, timeout=15):
    networks = {}
    try:
        result = subprocess.run(["iwlist", interface, "scan"], capture_output=True, text=True, timeout=timeout)
        current_bssid = ""
        for line in result.stdout.split("\n"):
            line = line.strip()
            if line.startswith("Cell"):
                current_bssid = ""
                m = re.search(r'Address:\s*([0-9A-Fa-f:]{17})', line)
                if m:
                    current_bssid = m.group(1).upper()
                    networks[current_bssid] = {"bssid": current_bssid, "ssid": "", "channel": "", "signal": "", "encryption": "", "wps": ""}
            if "ESSID:" in line:
                ssid = line.split("ESSID:")[-1].strip().strip('"')
                if current_bssid and ssid:
                    networks[current_bssid]["ssid"] = ssid
            if "Channel:" in line:
                ch = line.split("Channel:")[-1].strip()
                if current_bssid and ch:
                    networks[current_bssid]["channel"] = ch
            if "Quality=" in line:
                q = re.search(r'Quality=(\d+)/(\d+)', line)
                if q and current_bssid:
                    quality = int(q.group(1))
                    max_q = int(q.group(2))
                    networks[current_bssid]["quality"] = f"{quality}/{max_q}"
                    networks[current_bssid]["signal_percent"] = int((quality / max_q) * 100)
            if "Signal level=" in line:
                s = re.search(r'Signal level=(-?\d+)', line)
                if s and current_bssid:
                    networks[current_bssid]["signal"] = f"{s.group(1)} dBm"
            if "Encryption" in line:
                if "WPA2" in line:
                    networks[current_bssid]["encryption"] = "WPA2"
                elif "WPA" in line:
                    networks[current_bssid]["encryption"] = "WPA"
                elif "WEP" in line:
                    networks[current_bssid]["encryption"] = "WEP"
                elif "Open" in line:
                    networks[current_bssid]["encryption"] = "Open"
            if "IE:" in line and "WPS" in line:
                networks[current_bssid]["wps"] = "Yes"
    except:
        pass
    return [n for n in networks.values() if n["ssid"]]

def scan_networks_fast(interface, timeout=10):
    networks = []
    try:
        result = subprocess.run(["iw", "dev", interface, "scan"], capture_output=True, text=True, timeout=timeout)
        current = {}
        for line in result.stdout.split("\n"):
            line = line.strip()
            if line.startswith("BSS"):
                if current.get("ssid"):
                    networks.append(current)
                current = {"bssid": "", "ssid": "", "channel": "", "signal": "", "encryption": ""}
                m = re.search(r'([0-9A-Fa-f:]{17})', line)
                if m:
                    current["bssid"] = m.group(1).upper()
            if "SSID:" in line:
                s = line.split("SSID:")[-1].strip()
                if s:
                    current["ssid"] = s
            if "freq:" in line:
                freq = line.split("freq:")[-1].strip()
                current["channel"] = freq_to_channel(int(freq)) if freq.isdigit() else freq
            if "signal:" in line:
                s = re.search(r'signal:\s*(-?\d+)', line)
                if s:
                    current["signal"] = f"{s.group(1)} dBm"
            if "WPA" in line or "RSN" in line:
                if "WPA1" in line or "wpa1" in line:
                    current["encryption"] = "WPA"
                elif "WPA2" in line or "wpa2" in line:
                    current["encryption"] = "WPA2"
                elif "WPA3" in line or "wpa3" in line:
                    current["encryption"] = "WPA3"
            if "group cipher" in line:
                if not current.get("encryption"):
                    current["encryption"] = "Unknown"
        if current.get("ssid"):
            networks.append(current)
    except:
        pass
    return networks

def freq_to_channel(freq):
    if freq < 2412:
        return 0
    if freq >= 2412 and freq <= 2484:
        return (freq - 2407) // 5
    if freq >= 4910 and freq <= 4980:
        return (freq - 4910) // 5 + 1
    if freq >= 5180 and freq <= 5825:
        return (freq - 5180) // 5 + 36
    return 0

def signal_strength_bar(dbm_str, width=15):
    try:
        dbm = int(dbm_str.replace(" dBm", ""))
        if dbm >= -50:
            filled = width
        elif dbm <= -100:
            filled = 0
        else:
            filled = int(((-dbm - 50) / -50) * width)
            filled = max(0, min(width, filled))
        bar = f"{G}{'█' * filled}{R}{'█' * (width - filled)}{N}"
        return bar
    except:
        return f"{D}{'░' * width}{N}"

def crack_wpa_wordlist(handshake_file, wordlist, ssid=""):
    if not os.path.isfile(handshake_file):
        return None, "Handshake file not found"
    if not os.path.isfile(wordlist):
        return None, "Wordlist file not found"

    if WIFI_TOOLS.get("aircrack-ng"):
        log(f"{C}[*] Using aircrack-ng to crack: {handshake_file}{N}")
        result = subprocess.run(
            ["aircrack-ng", "-w", wordlist, handshake_file],
            capture_output=True, text=True, timeout=600
        )
        output = result.stdout
        m = re.search(r'KEY FOUND!\s*\[\s*([^\]]+)\s*\]', output)
        if m:
            return m.group(1).strip(), output
        m = re.search(r'Passphrase not in dictionary', output)
        if m:
            return None, "Password not found in wordlist"
        return None, output
    else:
        return None, "aircrack-ng not installed"

def crack_wpa_pure(handshake_file, wordlist, ssid=""):
    if not WIFI_TOOLS.get("aircrack-ng"):
        log(f"{Y}[!] aircrack-ng not found, trying hashcat...{N}")

    word_count = 0
    try:
        with open(wordlist, "r", errors="ignore") as f:
            word_count = sum(1 for _ in f)
    except:
        pass

    log(f"{C}[*] Wordlist has {word_count} entries{N}")

    if WIFI_TOOLS.get("aircrack-ng"):
        result = subprocess.run(
            ["aircrack-ng", "-w", wordlist, handshake_file],
            capture_output=True, text=True, timeout=3600
        )
        output = result.stdout
        if "KEY FOUND" in output:
            m = re.search(r'\[\s*([^\]]+)\s*\]', output[output.index("KEY FOUND"):])
            if m:
                return m.group(1).strip()
        return None

    elif WIFI_TOOLS.get("hashcat"):
        log(f"{C}[*] Converting to hashcat format...{N}")
        hccapx = handshake_file + ".hccapx"
        if WIFI_TOOLS.get("hcxpcaptool"):
            subprocess.run(["hcxpcaptool", "-z", hccapx, handshake_file], capture_output=True, timeout=30)
        if os.path.isfile(hccapx):
            result = subprocess.run(
                ["hashcat", "-m", 22000, "-a", 0, hccapx, wordlist, "--show"],
                capture_output=True, text=True, timeout=3600
            )
            if result.stdout.strip():
                return result.stdout.strip().split(":")[-1]
    return None

def check_default_password(ssid):
    ssid_lower = ssid.lower().strip()
    for key, pwd in DEFAULT_SSID_PASSWORDS.items():
        if key in ssid_lower:
            return pwd
    return None

def try_weak_passwords(ssid, bssid=""):
    ssid_lower = ssid.lower().strip()
    candidates = []

    default_pwd = check_default_password(ssid)
    if default_pwd:
        candidates.append((default_pwd, f"Default password for {ssid_lower} routers"))

    if re.match(r'^[A-Za-z]{3}\d{3}$', ssid):
        candidates.append((ssid.lower(), "SSID used as password (3 letters + 3 digits pattern)"))

    for pwd in WPA_WEAK_PASSWORDS:
        candidates.append((pwd, "Common weak password"))

    words = re.split(r'[-_\s]', ssid_lower)
    for w in words:
        if len(w) >= 4 and w.isalpha():
            candidates.append((w + "123", f"SSID word + 123"))
            candidates.append((w + "1234", f"SSID word + 1234"))
            candidates.append((w + "2025", f"SSID word + year"))
            candidates.append((w + "2026", f"SSID word + year"))

    candidates.append((ssid_lower + "123", "SSID + 123"))
    candidates.append((ssid_lower + "1234", "SSID + 1234"))
    candidates.append((ssid_lower + "2025", "SSID + year"))
    candidates.append((ssid_lower + "2026", "SSID + year"))
    candidates.append((ssid_lower + "!", "SSID + !"))
    candidates.append((ssid_lower + "@", "SSID + @"))
    candidates.append((ssid_lower + "#", "SSID + #"))

    seen = set()
    unique = []
    for pwd, src in candidates:
        if pwd not in seen and 8 <= len(pwd) <= 64:
            seen.add(pwd)
            unique.append((pwd, src))
    return unique

def deauth_detect_mode():
    print_section("DEAUTH ATTACK DETECTOR")
    log(f"{Y}[!] Monitoring for deauthentication packets...{N}")
    log(f"{D}    Requires monitor mode interface (airmon-ng start wlan0){N}\n")

    iface = input(f"{G} Monitor interface (e.g., wlan0mon): {N}").strip()
    if not iface:
        return

    if not WIFI_TOOLS.get("airodump-ng"):
        log(f"{R}[!] airodump-ng not found. Install aircrack-ng.{N}")
        return

    log(f"\n{C}[*] Starting deauth detection on {iface}... Press Ctrl+C to stop.{N}")
    deauth_count = 0
    start_time = time.time()

    try:
        proc = subprocess.Popen(
            ["airodump-ng", iface, "--output-format", "csv", "-w", "/tmp/wifix_deauth"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        while True:
            time.sleep(2)
            deauth_count += 1
            elapsed = int(time.time() - start_time)
            sys.stdout.write(f"\r  {R}Deauth frames detected: {deauth_count}  {D}Time: {elapsed}s{N}  ")
            sys.stdout.flush()
    except KeyboardInterrupt:
        proc.terminate()
        log(f"\n\n{Y}Stopped. Total deauth frames: {deauth_count}{N}")
    except:
        log(f"{R}[!] Error monitoring deauth{N}")

def scan_mode():
    print_section("WIFI NETWORK SCAN")

    interfaces = get_interfaces()
    if not interfaces:
        log(f"{R}[!] No wireless interfaces found{N}")
        return

    log(f"{G}[+] Available interfaces: {', '.join(interfaces)}{N}")
    iface = input(f"{G} Interface [{interfaces[0]}]: {N}").strip() or interfaces[0]

    timeout_input = input(f"{G} Scan duration (seconds, default 10): {N}").strip()
    timeout = int(timeout_input) if timeout_input else 10

    log(f"\n{C}[*] Scanning networks on {iface} ({timeout}s)...{N}")

    networks = scan_networks(iface, timeout)
    if not networks:
        networks = scan_networks_fast(iface, timeout)

    if not networks:
        log(f"{Y}[!] No networks found. Try increasing scan time.{N}")
        return

    networks.sort(key=lambda x: int(x.get("signal_percent", 0) if x.get("signal_percent") else 0), reverse=True)

    print_section(f"NEARBY NETWORKS — {len(networks)} found")
    print(f"\n{'#':<4} {'SSID':<30} {'BSSID':<20} {'CH':<5} {'Signal':<10} {'Encryption':<8} {'WPS'}")
    print(f"{'─'*85}")
    for i, n in enumerate(networks, 1):
        ssid = n.get("ssid", "?")[:28]
        bssid = n.get("bssid", "?")[:17]
        ch = n.get("channel", "?")
        sig = n.get("signal", "? dBm")
        sig_bar = ""
        if "dBm" in sig:
            sig_bar = signal_strength_bar(sig)
        enc = n.get("encryption", "?")[:6]
        wps = f"{G}Yes{N}" if n.get("wps") == "Yes" else f"{D}No{N}"
        print(f" {C}{i:<3}{N} {W}{ssid:<28}{N} {D}{bssid:<18}{N} {C}{ch:<4}{N} {sig_bar} {sig:<8} {Y}{enc:<6}{N} {wps}")

    save = input(f"\n{G} Save scan results? (y/n): {N}").strip().lower()
    if save == "y":
        filename = f"wifix_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        fmt = input(f"{G} Format (txt/json): {N}").strip().lower()
        if fmt == "json":
            with open(f"{filename}.json", "w") as f:
                json.dump(networks, f, indent=2)
        else:
            with open(f"{filename}.txt", "w") as f:
                f.write(f"WiFiX Scan — {datetime.now()}\n{'='*60}\n")
                for n in networks:
                    f.write(f"{n['ssid']:30} {n['bssid']:20} CH{n['channel']:4} {n['signal']:10} {n['encryption']}\n")
        log(f"{G}[+] Saved to {filename}{N}")

    return networks, iface

def password_test_mode():
    print_section("WIFI PASSWORD TESTING")
    log(f"{Y}[!] FOR AUTHORIZED TESTING ONLY — Only test your own networks!{N}")

    method = input(f"\n{G} Method (1: Weak password check, 2: Wordlist crack, 3: Default DB): {N}").strip()

    if method == "3":
        ssid = input(f"{G} Enter SSID to check defaults for: {N}").strip()
        if not ssid:
            return
        pwd = check_default_password(ssid)
        if pwd:
            log(f"\n{G}[!] Default password found: {Y}{pwd}{N}")
            log(f"{D}    Matched router brand: {ssid.lower()}{N}")
        else:
            log(f"\n{Y}[!] No default password in database for this SSID{N}")
        return

    if method == "1":
        ssid = input(f"{G} Enter SSID: {N}").strip()
        if not ssid:
            return
        log(f"\n{C}[*] Generating password candidates for: {Y}{ssid}{N}")
        candidates = try_weak_passwords(ssid)
        print_section(f"PASSWORD CANDIDATES — {len(candidates)}")
        for i, (pwd, src) in enumerate(candidates[:30], 1):
            print(f"  {C}{i:<3}{N}  {Y}{pwd:<20}{N}  {D}{src}{N}")
        if len(candidates) > 30:
            print(f"  {D}... and {len(candidates) - 30} more{N}")

        log(f"\n{G}[!] These are common weak passwords. Try each on the WiFi network.{N}")

    elif method == "2":
        if not WIFI_TOOLS.get("aircrack-ng"):
            log(f"{Y}[!] aircrack-ng recommended for optimal cracking{N}")

        handshake = input(f"{G} Path to handshake file (.cap): {N}").strip()
        if not handshake or not os.path.isfile(handshake):
            log(f"{R}[!] File not found{N}")
            return

        wordlist_path = input(f"{G} Path to wordlist file: {N}").strip()
        if not wordlist_path or not os.path.isfile(wordlist_path):
            log(f"{R}[!] File not found{N}")
            return

        ssid = input(f"{G} Network SSID (optional): {N}").strip()

        log(f"\n{C}[*] Starting crack on {handshake}...{N}")
        log(f"{C}[*] Wordlist: {wordlist_path}{N}")
        log(f"{Y}[!] This may take a long time depending on wordlist size{N}\n")

        pwd = crack_wpa_pure(handshake, wordlist_path, ssid)
        if pwd:
            log(f"\n{G}╔═══════════════════════════════════════════╗{N}")
            log(f"{G}║  PASSWORD FOUND!                         ║{N}")
            log(f"{G}║  {Y}{pwd:^37}{G}  ║{N}")
            log(f"{G}╚═══════════════════════════════════════════╝{N}")
        else:
            log(f"\n{Y}[!] Password not found in wordlist{N}")

def password_recovery_mode():
    print_section("SAVED WIFI PASSWORDS")
    log(f"{Y}[!] Only shows passwords for networks your system has connected to{N}\n")

    found = []
    if sys.platform == "linux":
        for f in os.listdir("/etc/NetworkManager/system-connections/"):
            try:
                path = os.path.join("/etc/NetworkManager/system-connections/", f)
                with open(path, "r") as file:
                    content = file.read()
                ssid = f
                psk = ""
                m = re.search(r'psk=(.+)', content)
                if m:
                    psk = m.group(1).strip()
                if psk:
                    found.append((ssid, psk))
            except:
                pass
    elif sys.platform == "win32":
        result = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True, timeout=10)
        profiles = re.findall(r'All User Profile\s*:\s*(.+)', result.stdout)
        for profile in profiles:
            profile = profile.strip()
            result2 = subprocess.run(["netsh", "wlan", "show", "profile", profile, "key=clear"], capture_output=True, text=True, timeout=10)
            m = re.search(r'Key Content\s*:\s*(.+)', result2.stdout)
            if m:
                pwd = m.group(1).strip()
                found.append((profile, pwd))

    if found:
        print_table(found, f"{'SSID':<30} {'PASSWORD':<30}", [30, 30])
        save = input(f"\n{G} Save to file? (y/n): {N}").strip().lower()
        if save == "y":
            filename = f"wifix_passwords_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w") as f:
                for ssid, pwd in found:
                    f.write(f"{ssid}:{pwd}\n")
            log(f"{G}[+] Saved to {filename}{N}")
    else:
        log(f"{Y}[!] No saved WiFi passwords found{N}")

def capture_handshake_mode():
    print_section("WPA HANDSHAKE CAPTURE")
    log(f"{Y}[!] Only capture handshakes on networks you OWN!{N}")

    if not WIFI_TOOLS.get("airodump-ng"):
        log(f"{R}[!] airodump-ng not found. Install aircrack-ng.{N}")
        return

    iface = input(f"{G} Interface (must be in monitor mode, e.g., wlan0mon): {N}").strip()
    if not iface:
        return

    bssid = input(f"{G} Target BSSID (e.g., AA:BB:CC:DD:EE:FF): {N}").strip()
    if not bssid:
        return

    channel = input(f"{G} Channel: {N}").strip()
    if channel:
        subprocess.run(["iwconfig", iface, "channel", channel], capture_output=True, timeout=3)

    output_prefix = f"/tmp/wifix_handshake_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    log(f"\n{C}[*] Starting capture on {iface} targeting {bssid}...{N}")
    log(f"{Y}[!] Wait for a device to connect, or send a deauth packet{N}")
    log(f"{Y}[!] Press Ctrl+C when handshake is captured{N}\n")

    try:
        proc = subprocess.Popen(
            ["airodump-ng", "-c", channel, "--bssid", bssid,
             "-w", output_prefix, iface],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        start = time.time()
        while True:
            time.sleep(5)
            elapsed = int(time.time() - start)
            sys.stdout.write(f"\r  {C}[*] Capturing... {elapsed}s elapsed. Check for .cap file.{N}  ")
            sys.stdout.flush()
            for f in os.listdir("/tmp/"):
                if f.startswith(os.path.basename(output_prefix)) and f.endswith(".cap"):
                    if os.path.getsize(os.path.join("/tmp/", f)) > 100:
                        log(f"\n\n{G}[+] Handshake capture file: /tmp/{f}{N}")
                        proc.terminate()
                        return
    except KeyboardInterrupt:
        proc.terminate()
        log(f"\n{Y}[!] Capture stopped{N}")

def signal_monitor_mode():
    print_section("SIGNAL MONITOR")

    interfaces = get_interfaces()
    if not interfaces:
        log(f"{R}[!] No wireless interfaces found{N}")
        return

    iface = input(f"{G} Interface [{interfaces[0]}]: {N}").strip() or interfaces[0]
    target_bssid = input(f"{G} Target BSSID to monitor (or leave blank to scan all): {N}").strip()

    log(f"\n{C}[*] Monitoring signal on {iface}... Press Ctrl+C to stop.{N}\n")

    try:
        while True:
            networks = scan_networks(iface, 3)
            if not networks:
                networks = scan_networks_fast(iface, 3)

            os.system("clear" if os.name == "posix" else "cls")
            print(BANNER)
            print(f"\n{C}  Live Signal Monitor — Press Ctrl+C to exit{N}\n")
            print(f"  {'SSID':<30} {'BSSID':<20} {'CH':<5} {'Signal':<12} {'Bar':<20}")
            print(f"  {'─'*90}")

            if target_bssid:
                networks = [n for n in networks if n.get("bssid", "").upper() == target_bssid.upper()]

            for n in networks[:10]:
                ssid = n.get("ssid", "?")[:28]
                bssid = n.get("bssid", "?")[:17]
                ch = n.get("channel", "?")
                sig = n.get("signal", "? dBm")
                sig_bar = ""
                if "dBm" in sig:
                    sig_bar = signal_strength_bar(sig, 20)
                print(f"  {W}{ssid:<28}{N} {D}{bssid:<18}{N} {C}{ch:<4}{N} {Y}{sig:<10}{N} {sig_bar}")

            time.sleep(2)
    except KeyboardInterrupt:
        log(f"\n{Y}[!] Monitor stopped{N}")

def wps_check_mode():
    print_section("WPS STATUS CHECK")

    networks, iface = scan_mode()
    if not networks:
        return

    wps_networks = [n for n in networks if n.get("wps") == "Yes" or "WPS" in str(n)]
    if wps_networks:
        print_section(f"NETWORKS WITH WPS — {len(wps_networks)}")
        for n in wps_networks:
            ssid = n.get("ssid", "?")
            bssid = n.get("bssid", "?")
            sig = n.get("signal", "?")
            log(f"  {G}{ssid}{N}  {C}{bssid}{N}  {D}{sig}{N}")
    else:
        log(f"{Y}[!] No WPS-enabled networks detected (may not be advertised){N}")

def client_discover_mode():
    print_section("CLIENT DISCOVERY")
    log(f"{Y}[!] Only scan networks you own{N}")

    if not WIFI_TOOLS.get("airodump-ng"):
        log(f"{R}[!] airodump-ng required. Install aircrack-ng.{N}")
        return

    iface = input(f"{G} Monitor interface: {N}").strip()
    if not iface:
        return

    bssid = input(f"{G} Target BSSID (or leave blank for all): {N}").strip()
    output_prefix = "/tmp/wifix_clients"

    log(f"\n{C}[*] Discovering clients... (10s scan){N}")

    cmd = ["airodump-ng"]
    if bssid:
        cmd.extend(["--bssid", bssid])
    cmd.extend(["-w", output_prefix, iface])

    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(10)
    proc.terminate()

    clients = []
    for f_name in os.listdir("/tmp/"):
        if f_name.startswith(os.path.basename(output_prefix)) and f_name.endswith(".csv"):
            try:
                with open(f"/tmp/{f_name}", "r") as f:
                    lines = f.readlines()
                in_clients = False
                for line in lines:
                    if "Station MAC" in line:
                        in_clients = True
                        continue
                    if in_clients and line.strip():
                        parts = line.split(",")
                        if len(parts) >= 6:
                            mac = parts[0].strip()
                            bssid_client = parts[5].strip()
                            signal = parts[1].strip() if len(parts) > 1 else "?"
                            clients.append((mac, signal, bssid_client))
            except:
                pass

    if clients:
        print_table(clients, f"{'Client MAC':<20} {'Signal':<10} {'Connected To':<20}", [20, 10, 20])
    else:
        log(f"{Y}[!] No clients found. Wait longer or try during active usage.{N}")

def interactive_menu():
    WIFI_TOOLS.update(check_tools())

    while True:
        print(f"\n{BANNER}")
        print(f"{DISCLAIMER}\n")
        print(f" {W}┌─────────────────────────────────────────────┐{N}")
        print(f" {W}│  {C}1.{W}  Scan Networks       {D}[List nearby APs]{W}     │{N}")
        print(f" {W}│  {C}2.{W}  Password Testing    {D}[Weak + wordlist]{W}     │{N}")
        print(f" {W}│  {C}3.{W}  Saved Passwords     {D}[Recover stored]{W}      │{N}")
        print(f" {W}│  {C}4.{W}  Capture Handshake   {D}[WPA handshake]{W}       │{N}")
        print(f" {W}│  {C}5.{W}  Signal Monitor      {D}[Real-time RSSI]{W}     │{N}")
        print(f" {W}│  {C}6.{W}  WPS Check           {D}[WPS status]{W}          │{N}")
        print(f" {W}│  {C}7.{W}  Client Discovery    {D}[Find connected]{W}      │{N}")
        print(f" {W}│  {C}8.{W}  Deauth Detection    {D}[Monitor attacks]{W}    │{N}")
        print(f" {W}│  {C}0.{W}  Exit{N}                                      │{N}")
        print(f" {W}└─────────────────────────────────────────────┘{N}")

        choice = input(f"\n{G} WiFiX > {N}").strip()

        if choice == "1":
            scan_mode()
        elif choice == "2":
            password_test_mode()
        elif choice == "3":
            password_recovery_mode()
        elif choice == "4":
            capture_handshake_mode()
        elif choice == "5":
            signal_monitor_mode()
        elif choice == "6":
            wps_check_mode()
        elif choice == "7":
            client_discover_mode()
        elif choice == "8":
            deauth_detect_mode()
        elif choice == "0":
            log(f"\n{R}Exiting WiFiX. Stay legal.{N}")
            break
        else:
            log(f"{R}[!] Invalid option{N}")

        input(f"\n{D}Press Enter to continue...{N}")

def show_help():
    print(BANNER)
    print(DISCLAIMER)
    print(f"""
{Y}USAGE:{N}
  {W}wifx [mode] [options]{N}

{Y}MODES:{N}
  {C}scan{W}          Scan nearby WiFi networks
  {C}password{W}      Test weak passwords against SSID
  {C}recover{W}       Recover saved WiFi passwords
  {C}handshake{W}     Capture WPA handshake
  {C}monitor{W}       Real-time signal monitor
  {C}wps{W}           Check WPS status
  {C}clients{W}       Discover connected clients
  {C}deauth{W}        Detect deauth attacks

{Y}EXAMPLES:{N}
  {D}wifx{W}                       Interactive menu
  {D}wifx scan{W}                  Scan networks
  {D}wifx password --ssid MyWiFi{W}  Test weak passwords
  {D}wifx recover{W}               Show saved passwords
  {D}wifx handshake --bssid AA:BB:CC:DD:EE:FF{W}
  {D}wifx monitor{W}               Live signal monitor

{Y}OPTIONS:{N}
  {C}--ssid{W}   <name>    Target SSID
  {C}--bssid{W}  <mac>     Target BSSID
  {C}--iface{W}  <name>    Wireless interface
  {C}-w{W}       <file>    Wordlist file
  {C}-h{W}       --help    Show this help
{N}""")

def parse_args():
    WIFI_TOOLS.update(check_tools())

    if len(sys.argv) < 2:
        interactive_menu()
        return

    cmd = sys.argv[1].lower()

    if cmd in ("-h", "--help", "help"):
        show_help()
        return

    ssid = ""
    bssid = ""
    iface = ""
    wordlist = ""

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--ssid" and i + 1 < len(sys.argv):
            i += 1; ssid = sys.argv[i]
        elif arg == "--bssid" and i + 1 < len(sys.argv):
            i += 1; bssid = sys.argv[i]
        elif arg == "--iface" and i + 1 < len(sys.argv):
            i += 1; iface = sys.argv[i]
        elif arg in ("-w", "--wordlist") and i + 1 < len(sys.argv):
            i += 1; wordlist = sys.argv[i]
        i += 1

    if cmd == "scan":
        scan_mode()
    elif cmd in ("password", "pwd"):
        if ssid:
            candidates = try_weak_passwords(ssid)
            print_section(f"PASSWORD CANDIDATES — {len(candidates)}")
            for pwd, src in candidates[:20]:
                print(f"  {Y}{pwd:<20}{N}  {D}{src}{N}")
        else:
            password_test_mode()
    elif cmd == "recover":
        password_recovery_mode()
    elif cmd in ("handshake", "capture"):
        capture_handshake_mode()
    elif cmd == "monitor":
        signal_monitor_mode()
    elif cmd == "wps":
        wps_check_mode()
    elif cmd == "clients":
        client_discover_mode()
    elif cmd == "deauth":
        deauth_detect_mode()
    else:
        log(f"{R}[!] Unknown mode: {cmd}{N}")
        show_help()

if __name__ == "__main__":
    try:
        parse_args()
    except KeyboardInterrupt:
        log(f"\n{Y}[!] Interrupted by user{N}")
        sys.exit(0)
    except Exception as e:
        log(f"\n{R}[!] Error: {e}{N}")
        sys.exit(1)
