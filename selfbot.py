#!/usr/bin/env python3
"""
CROCODILE SELF-BOT v6.0
- Edit token inside app (no manual config editing)
- Token management menu
"""

import requests
import json
import time
import os
import sys
import re
from datetime import datetime

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
VERSION = "6.0"
CONFIG_FILE = os.path.join(BASE_PATH, "config_multi.json")
THEME_FILE = os.path.join(BASE_PATH, "theme.json")

try:
    with open(os.path.join(BASE_PATH, "version.txt"), 'w') as f:
        f.write(VERSION)
except:
    pass

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'

def loading_animation(text="Loading", duration=1):
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end = time.time() + duration
    i = 0
    while time.time() < end:
        sys.stdout.write(f"\r{CYAN}{chars[i % len(chars)]} {text}{RESET}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * 40 + "\r")

def pulse_animation():
    chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂", "▁"]
    return chars[int(time.time() * 5) % len(chars)]

def progress_bar(current, total, width=25):
    percent = current / total if total > 0 else 0
    filled = int(width * percent)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {int(percent * 100)}%"

THEMES = {
    "crocodile": {"p": GREEN, "s": '\033[38;5;34m', "a": YELLOW, "w": YELLOW, "e": RED, "r": RESET},
    "blue": {"p": '\033[94m', "s": CYAN, "a": '\033[36m', "w": YELLOW, "e": RED, "r": RESET},
    "red": {"p": RED, "s": YELLOW, "a": MAGENTA, "w": YELLOW, "e": RED, "r": RESET},
    "purple": {"p": MAGENTA, "s": CYAN, "a": GREEN, "w": YELLOW, "e": RED, "r": RESET},
    "orange": {"p": '\033[38;5;214m', "s": '\033[38;5;208m', "a": YELLOW, "w": YELLOW, "e": RED, "r": RESET}
}

C = THEMES["crocodile"]

def load_theme():
    global C
    if os.path.exists(THEME_FILE):
        try:
            with open(THEME_FILE, 'r') as f:
                theme_name = json.load(f).get('theme', 'crocodile')
                if theme_name in THEMES:
                    C = THEMES[theme_name]
                    return theme_name
        except:
            pass
    C = THEMES["crocodile"]
    return "crocodile"

def save_theme(theme_name):
    try:
        with open(THEME_FILE, 'w') as f:
            json.dump({"theme": theme_name}, f)
        return True
    except:
        return False

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    clear()
    print(f"""
{C['p']}╔══════════════════════════════════════════════════════════════════╗
║         🐊 CROCODILE SELF-BOT v{VERSION} 🐊                              ║
╚══════════════════════════════════════════════════════════════════╝
{RESET}""")

def get_channel_info(token, channel_id):
    headers = {"Authorization": token}
    try:
        url = f"https://discord.com/api/v9/channels/{channel_id}"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def fetch_guild_emojis(token, guild_id):
    headers = {"Authorization": token}
    try:
        url = f"https://discord.com/api/v9/guilds/{guild_id}/emojis"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def build_emoji_map_for_guild(token, guild_id):
    emoji_map = {}
    emojis = fetch_guild_emojis(token, guild_id)
    for emoji in emojis:
        name = emoji['name']
        emoji_id = emoji['id']
        animated = emoji.get('animated', False)
        if animated:
            emoji_map[f":{name}:"] = f"<a:{name}:{emoji_id}>"
        else:
            emoji_map[f":{name}:"] = f"<:{name}:{emoji_id}>"
    return emoji_map

def refresh_emoji_map_for_channel(token, channel_id):
    channel_info = get_channel_info(token, channel_id)
    if channel_info and channel_info.get('guild_id'):
        guild_id = channel_info['guild_id']
        emoji_map = build_emoji_map_for_guild(token, guild_id)
        return emoji_map, guild_id
    return {}, None

def convert_emojis(message, emoji_map):
    if not emoji_map:
        return message
    converted = message
    for emoji_code, emoji_format in sorted(emoji_map.items(), key=lambda x: len(x[0]), reverse=True):
        converted = converted.replace(emoji_code, emoji_format)
    return converted

def extract_only_emojis(text):
    custom_pattern = r'<a?:\w+:\d+>'
    unicode_pattern = r'[\U00010000-\U0010ffff]|[\u2600-\u27BF]|[\uE000-\uF8FF]|\u00a9|\u00ae|\u2000-\u3300|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff]'
    custom_emojis = re.findall(custom_pattern, text)
    unicode_emojis = re.findall(unicode_pattern, text)
    all_emojis = custom_emojis + unicode_emojis
    return ' '.join(all_emojis)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(f"{C['p']}✅ Loaded {len(config.get('channels', []))} channels{RESET}")
            return config
    else:
        print(f"{C['w']}⚠️ No config found. Creating new...{RESET}")
        return {"token": "", "channels": [], "global_interval": 30}

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def test_token(token):
    if not token or len(token) < 50:
        return False, None
    try:
        headers = {"Authorization": token.strip()}
        r = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=10)
        if r.status_code == 200:
            return True, r.json()
        return False, None
    except:
        return False, None

def verify_token(config):
    if not config.get("token"):
        print(f"{C['w']}⚠️ No token found!{RESET}")
        return change_token_menu(config)
    
    print(f"{C['s']}🔑 Verifying token...{RESET}")
    loading_animation("Checking credentials", 1)
    
    valid, data = test_token(config['token'])
    
    if valid:
        print(f"{C['p']}✅ Token VALID! Logged in as: {data['username']}{RESET}")
        return config
    else:
        print(f"{C['e']}❌ Token INVALID or EXPIRED!{RESET}")
        return change_token_menu(config)

def change_token_menu(config):
    """NEW: Menu to change/update token - NO RESTART NEEDED"""
    print(f"\n{C['s']}┌─────────────────────────────────────────────────────────────────┐")
    print(f"│  🔑 TOKEN MANAGEMENT")
    print(f"├─────────────────────────────────────────────────────────────────┤{RESET}")
    
    current_token = config.get('token', '')
    if current_token:
        print(f"{C['s']}   Current token: {current_token[:20]}...{current_token[-10:]}{RESET}")
    else:
        print(f"{C['w']}   Current token: NOT SET{RESET}")
    
    print(f"\n{C['p']}   Options:{RESET}")
    print(f"     1. Enter new token")
    print(f"     2. Clear token (start fresh)")
    print(f"     3. Cancel")
    
    choice = input(f"\n{C['s']}Choose (1-3): {RESET}").strip()
    
    if choice == "1":
        new_token = input(f"{C['s']}Enter your Discord token: {RESET}").strip()
        print(f"{C['s']}Verifying...{RESET}")
        loading_animation("Testing token", 1)
        valid, data = test_token(new_token)
        
        if valid:
            config['token'] = new_token
            save_config(config)
            print(f"{C['p']}✅ Token updated! Welcome {data['username']}{RESET}")
            input(f"{C['s']}Press Enter to continue...{RESET}")
            return config
        else:
            print(f"{C['e']}❌ Invalid token! Token not saved.{RESET}")
            input(f"{C['s']}Press Enter to continue...{RESET}")
            return config
    
    elif choice == "2":
        config['token'] = ""
        save_config(config)
        print(f"{C['p']}✅ Token cleared! Run setup again.{RESET}")
        input(f"{C['s']}Press Enter to continue...{RESET}")
        return config
    
    else:
        print(f"{C['w']}Cancelled{RESET}")
        input(f"{C['s']}Press Enter...{RESET}")
        return config

def send_message(token, channel_id, raw_message, emoji_map, pure_emoji_mode):
    converted = convert_emojis(raw_message, emoji_map)
    if pure_emoji_mode:
        final_message = extract_only_emojis(converted)
        if not final_message:
            return False, "No emojis found"
    else:
        final_message = converted
    
    headers = {"Authorization": token.strip(), "Content-Type": "application/json"}
    try:
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        r = requests.post(url, headers=headers, json={"content": final_message}, timeout=15)
        if r.status_code in [200, 201]:
            return True, "Success"
        elif r.status_code == 401:
            return False, "Token invalid"
        elif r.status_code == 403:
            return False, "No permission"
        elif r.status_code == 404:
            return False, "Channel not found"
        elif r.status_code == 429:
            return False, "Rate limited"
        else:
            return False, f"Error {r.status_code}"
    except Exception as e:
        return False, str(e)

def add_channel(config):
    print(f"\n{C['s']}➕ ADD NEW CHANNEL{RESET}\n")
    
    channel_id = input(f"Channel ID: {RESET}").strip()
    if not channel_id:
        print(f"{C['e']}Cancelled{RESET}")
        return
    
    try:
        channel_id = int(channel_id)
    except ValueError:
        print(f"{C['e']}Invalid channel ID!{RESET}")
        return
    
    print(f"\n{C['s']}SELECT MODE:{RESET}")
    print(f"  {C['p']}1{RESET}. Normal mode (text + emojis)")
    print(f"  {C['w']}2{RESET}. Pure emoji mode (no text, only emojis)")
    
    mode_choice = input(f"\nChoose (1 or 2): {RESET}").strip()
    pure_emoji_mode = (mode_choice == "2")
    
    if pure_emoji_mode:
        print(f"\n{C['w']}⚠️ PURE EMOJI MODE: Text will be removed, only emojis sent!{RESET}")
    
    print(f"\n{C['s']}🔍 Fetching custom emojis from server...{RESET}")
    loading_animation("Scanning server", 1)
    emoji_map, guild_id = refresh_emoji_map_for_channel(config['token'], channel_id)
    
    if emoji_map:
        print(f"{C['p']}✅ Found {len(emoji_map)} custom emojis{RESET}")
    else:
        print(f"{C['w']}⚠️ No custom emojis found. Only Unicode emojis will work.{RESET}")
    
    print(f"\n{C['s']}ENTER YOUR MESSAGE{RESET}")
    print(f"  💡 Use :emoji_name: for custom server emojis")
    if pure_emoji_mode:
        print(f"  ⚠️ Regular text will be removed automatically!")
    print(f"  📝 Type 'END' on a new line when finished")
    print(f"  📋 Type 'LIST' to see available emojis\n")
    
    lines = []
    while True:
        line = input()
        if line == "END":
            break
        if line == "LIST" and emoji_map:
            print(f"\n{C['p']}Available emojis:{RESET}")
            for ec, ef in list(emoji_map.items())[:30]:
                print(f"   {ec} -> {ef}")
            if len(emoji_map) > 30:
                print(f"   ... and {len(emoji_map) - 30} more")
            print()
            continue
        lines.append(line)
    
    raw_message = "\n".join(lines)
    if not raw_message.strip():
        raw_message = "W trade +rep 🔥"
    
    converted = convert_emojis(raw_message, emoji_map)
    
    print(f"\n{C['s']}MESSAGE PREVIEW:{RESET}")
    if pure_emoji_mode:
        final_preview = extract_only_emojis(converted)
        print(f"  Raw: {raw_message[:60]}")
        print(f"  Converted: {converted[:60]}")
        print(f"  Final (emoji only): {final_preview[:60]}")
    else:
        print(f"  {converted[:200]}")
    
    print(f"\n{C['s']}Interval in seconds:{RESET}")
    interval_input = input(f"Enter number (or press Enter for {config['global_interval']}): {RESET}").strip()
    interval = int(interval_input) if interval_input else config['global_interval']
    
    config['channels'].append({
        "channel_id": channel_id,
        "raw_message": raw_message,
        "interval": interval,
        "enabled": True,
        "last_sent": None,
        "guild_id": guild_id,
        "emoji_map": emoji_map,
        "pure_emoji_mode": pure_emoji_mode
    })
    
    save_config(config)
    mode_text = "PURE EMOJI MODE" if pure_emoji_mode else "NORMAL MODE"
    print(f"\n{C['p']}✅ Channel {channel_id} added in {mode_text}!{RESET}")

def list_channels(config):
    if not config['channels']:
        print(f"{C['w']}No channels configured yet.{RESET}")
        return
    
    print(f"\n{C['s']}📋 CONFIGURED CHANNELS:{RESET}")
    for i, ch in enumerate(config['channels']):
        status = f"{C['p']}ENABLED{RESET}" if ch['enabled'] else f"{C['e']}DISABLED{RESET}"
        mode = f"{C['w']}PURE{RESET}" if ch.get('pure_emoji_mode', False) else f"{C['s']}NORMAL{RESET}"
        print(f"\n  {i+1}. {status} {mode}")
        print(f"     Channel: {ch['channel_id']}")
        msg_preview = ch.get('raw_message', '').replace('\n', ' ↵ ')[:60]
        print(f"     Message: {msg_preview}{'...' if len(ch.get('raw_message', '')) > 60 else ''}")
        print(f"     Interval: {ch['interval']}s")
        if ch.get('emoji_map'):
            print(f"     Emojis: {len(ch['emoji_map'])} loaded")
        if ch.get('last_sent'):
            print(f"     Last sent: {ch['last_sent']}")

def toggle_channel(config):
    if not config['channels']:
        print(f"{C['w']}No channels configured.{RESET}")
        return
    
    list_channels(config)
    try:
        choice = int(input(f"\nChannel number to toggle: {RESET}")) - 1
        if 0 <= choice < len(config['channels']):
            config['channels'][choice]['enabled'] = not config['channels'][choice]['enabled']
            status = "ENABLED" if config['channels'][choice]['enabled'] else "DISABLED"
            print(f"{C['p']}✅ Channel toggled to {status}{RESET}")
            save_config(config)
        else:
            print(f"{C['e']}Invalid number{RESET}")
    except:
        print(f"{C['e']}Invalid input{RESET}")

def remove_channel(config):
    if not config['channels']:
        print(f"{C['w']}No channels configured.{RESET}")
        return
    
    list_channels(config)
    try:
        choice = int(input(f"\nChannel number to remove: {RESET}")) - 1
        if 0 <= choice < len(config['channels']):
            removed = config['channels'].pop(choice)
            print(f"{C['p']}✅ Removed channel {removed['channel_id']}{RESET}")
            save_config(config)
        else:
            print(f"{C['e']}Invalid number{RESET}")
    except:
        print(f"{C['e']}Invalid input{RESET}")

def refresh_emojis(config):
    print(f"\n{C['s']}🔄 Refreshing emoji maps...{RESET}")
    total = len(config['channels'])
    for i, ch in enumerate(config['channels']):
        print(f"  [{i+1}/{total}] Scanning channel {ch['channel_id']}...", end="\r")
        emoji_map, guild_id = refresh_emoji_map_for_channel(config['token'], ch['channel_id'])
        ch['emoji_map'] = emoji_map
        ch['guild_id'] = guild_id
        time.sleep(0.3)
    print(f"\n{C['p']}✅ Emoji maps refreshed!{RESET}")
    save_config(config)

def send_to_all_channels_once(config):
    if not config['channels']:
        print(f"{C['w']}No channels configured.{RESET}")
        return
    
    enabled = [ch for ch in config['channels'] if ch['enabled']]
    if not enabled:
        print(f"{C['w']}No enabled channels.{RESET}")
        return
    
    print(f"\n{C['s']}📤 Sending to {len(enabled)} channels...{RESET}\n")
    
    success = 0
    fail = 0
    
    for i, ch in enumerate(enabled):
        print(f"  [{i+1}/{len(enabled)}] Sending to {ch['channel_id']}...", end=" ")
        
        emoji_map = ch.get('emoji_map', {})
        if not emoji_map and ch.get('guild_id'):
            emoji_map, _ = refresh_emoji_map_for_channel(config['token'], ch['channel_id'])
            ch['emoji_map'] = emoji_map
            save_config(config)
        
        ok, err = send_message(config['token'], ch['channel_id'], ch['raw_message'], emoji_map, ch.get('pure_emoji_mode', False))
        
        if ok:
            print(f"{C['p']}✓ Sent{RESET}")
            success += 1
            ch['last_sent'] = datetime.now().strftime('%H:%M:%S')
        else:
            print(f"{C['e']}✗ {err}{RESET}")
            fail += 1
        time.sleep(0.3)
    
    save_config(config)
    print(f"\n{C['p']}✅ Sent: {success} | Failed: {fail}{RESET}")
    input(f"Press Enter...")

def auto_send_all_channels(config):
    if not config['channels']:
        print(f"{C['w']}No channels configured.{RESET}")
        return
    
    enabled = [ch for ch in config['channels'] if ch['enabled']]
    if not enabled:
        print(f"{C['w']}No enabled channels.{RESET}")
        return
    
    print(f"\n{C['p']}🟢 AUTO-SEND STARTED{RESET}")
    print(f"{C['s']}   Channels: {len(enabled)}{RESET}")
    for ch in enabled:
        mode = "PURE" if ch.get('pure_emoji_mode', False) else "NORMAL"
        print(f"   [{mode}] {ch['channel_id']}: every {ch['interval']}s")
    print(f"\n   Press Ctrl+C to stop\n")
    
    last = {ch['channel_id']: 0 for ch in enabled}
    count = 0
    
    try:
        while True:
            now = time.time()
            for ch in enabled:
                if now - last.get(ch['channel_id'], 0) >= ch['interval']:
                    count += 1
                    print(f"{C['a']}[{datetime.now().strftime('%H:%M:%S')}] Sending to {ch['channel_id']}...{RESET}", end="\r")
                    
                    emoji_map = ch.get('emoji_map', {})
                    if not emoji_map and ch.get('guild_id'):
                        emoji_map, _ = refresh_emoji_map_for_channel(config['token'], ch['channel_id'])
                        ch['emoji_map'] = emoji_map
                        save_config(config)
                    
                    ok, err = send_message(config['token'], ch['channel_id'], ch['raw_message'], emoji_map, ch.get('pure_emoji_mode', False))
                    
                    if ok:
                        print(f"{C['p']}[{datetime.now().strftime('%H:%M:%S')}] ✓ Sent to {ch['channel_id']}{' ' * 20}{RESET}")
                        last[ch['channel_id']] = now
                        ch['last_sent'] = datetime.now().strftime('%H:%M:%S')
                        save_config(config)
                    else:
                        print(f"{C['e']}[{datetime.now().strftime('%H:%M:%S')}] ✗ Failed: {err}{' ' * 20}{RESET}")
                    time.sleep(0.5)
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{C['e']}🔴 STOPPED - {count} messages{RESET}")
        input("Press Enter...")

def change_theme():
    print(f"\n{C['s']}🎨 CHANGE THEME{RESET}")
    
    themes_list = list(THEMES.keys())
    current = load_theme()
    
    for i, theme in enumerate(themes_list):
        if theme == current:
            print(f"  {C['p']}{i+1}. {theme} ✓ (current){RESET}")
        else:
            print(f"  {i+1}. {theme}")
    
    print(f"\n  {len(themes_list)+1}. Cancel")
    
    choice = input(f"\nChoose theme (1-{len(themes_list)+1}): {RESET}").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(themes_list):
            theme_name = themes_list[idx]
            if save_theme(theme_name):
                print(f"{C['p']}✅ Theme changed to {theme_name}!{RESET}")
                print(f"{C['s']}   Theme will apply on next launch.{RESET}")
            else:
                print(f"{C['e']}❌ Failed to save theme!{RESET}")
        elif idx == len(themes_list):
            print(f"{C['w']}Cancelled{RESET}")
        else:
            print(f"{C['e']}Invalid choice{RESET}")
    except:
        print(f"{C['e']}Invalid input{RESET}")
    input("Press Enter...")

def show_help():
    print(f"""
{C['p']}📖 HELP - v{VERSION}{RESET}

{C['s']}NORMAL MODE:{RESET} Text + emojis together
{C['w']}PURE EMOJI MODE:{RESET} Only emojis (for servers that block text)

{C['s']}TOKEN MANAGEMENT:{RESET}
   - Use option 8 to change/update your token
   - No need to edit config_multi.json manually
   - Token is verified before saving

{C['s']}GET CHANNEL ID:{RESET}
   Settings -> Advanced -> Developer Mode ON
   Right-click channel -> Copy ID

{C['s']}GET TOKEN:{RESET}
   Chrome -> discord.com/app -> F12 -> Network tab
   Filter: /api -> click request -> authorization header
""")

def setup():
    banner()
    
    print(f"{C['w']}⚠️  WARNING: Self-bots violate Discord ToS{RESET}\n")
    confirm = input("Type 'YES' to continue: ")
    if confirm.upper() != "YES":
        sys.exit(0)
    
    token = input(f"\n{C['s']}Enter your Discord token: {RESET}").strip()
    
    loading_animation("Verifying token", 1)
    valid, data = test_token(token)
    if not valid:
        print(f"{C['e']}❌ Invalid token!{RESET}")
        retry = input("Try again? (y/n): ")
        if retry.lower() == 'y':
            return setup()
        sys.exit(0)
    
    config = {"token": token, "channels": [], "global_interval": 30}
    save_config(config)
    
    print(f"\n{C['p']}✅ Setup complete! Welcome {data['username']}{RESET}")
    input("Press Enter...")
    return config

def main():
    global C
    load_theme()
    
    banner()
    
    config = load_config()
    
    if not config.get("token"):
        config = setup()
    else:
        config = verify_token(config)
    
    while True:
        banner()
        
        enabled = sum(1 for ch in config['channels'] if ch.get('enabled', True))
        total = len(config['channels'])
        pure = sum(1 for ch in config['channels'] if ch.get('pure_emoji_mode', False))
        current_theme = load_theme()
        
        token_preview = config.get('token', '')
        if token_preview:
            token_display = f"{token_preview[:15]}...{token_preview[-8:]}"
        else:
            token_display = "NOT SET"
        
        pulse = pulse_animation()
        
        print(f"{C['s']}┌─────────────────────────────────────────────────────────────────┐")
        print(f"│  📊 STATUS DASHBOARD")
        print(f"├─────────────────────────────────────────────────────────────────┤")
        print(f"│  {C['p']}●{RESET} Channels: {total} total, {enabled} enabled")
        print(f"│  {C['w']}🔮{RESET} Pure emoji mode: {pure} channels")
        print(f"│  {C['s']}📝{RESET} Normal mode: {total - pure} channels")
        print(f"│  {C['a']}🎨{RESET} Theme: {current_theme}")
        print(f"│  {C['a']}🔑{RESET} Token: {token_display}")
        print(f"│  {C['a']}📂{RESET} Config path: {CONFIG_FILE}")
        print(f"│  {C['a']}💓{RESET} Status: {pulse} Active")
        print(f"└─────────────────────────────────────────────────────────────────┘{RESET}")
        
        print(f"""
{C['p']}╔══════════════════════════════════════════════════════════════════╗
║  MAIN MENU                                                          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  {C['a']}1{RESET}  📤 Send to ALL channels (once)                         ║
║  {C['a']}2{RESET}  🔄 Start AUTO-SEND (loop)                              ║
║  {C['a']}3{RESET}  ➕ Add a channel                                       ║
║  {C['a']}4{RESET}  📋 List all channels                                   ║
║  {C['a']}5{RESET}  🔘 Enable/Disable a channel                            ║
║  {C['a']}6{RESET}  🗑️ Remove a channel                                    ║
║  {C['a']}7{RESET}  🔄 Refresh emoji maps                                  ║
║  {C['a']}8{RESET}  🔑 CHANGE / UPDATE TOKEN (NEW!)                        ║
║  {C['a']}9{RESET}  🎨 Change theme                                        ║
║  {C['a']}0{RESET}  ❓ Help                                                ║
║  {C['a']}Q{RESET}  🚪 Exit                                                ║
║                                                                     ║
╚══════════════════════════════════════════════════════════════════╝
{RESET}""")
        
        choice = input(f"{C['s']}👉 Choose: {RESET}").strip().upper()
        
        if choice == "1":
            send_to_all_channels_once(config)
        elif choice == "2":
            auto_send_all_channels(config)
        elif choice == "3":
            add_channel(config)
            input("Press Enter...")
        elif choice == "4":
            list_channels(config)
            input("\nPress Enter...")
        elif choice == "5":
            toggle_channel(config)
            input("Press Enter...")
        elif choice == "6":
            remove_channel(config)
            input("Press Enter...")
        elif choice == "7":
            refresh_emojis(config)
            input("Press Enter...")
        elif choice == "8":
            print()
            config = change_token_menu(config)
        elif choice == "9":
            change_theme()
        elif choice == "0":
            show_help()
            input("\nPress Enter...")
        elif choice == "Q":
            print(f"\n{C['p']}👋 Goodbye!{RESET}")
            break
        else:
            print(f"{C['e']}Invalid choice{RESET}")
            input("Press Enter...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C['w']}Goodbye!{RESET}")
        sys.exit(0)