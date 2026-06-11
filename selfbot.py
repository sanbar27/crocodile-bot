#!/usr/bin/env python3
"""
CROCODILE SELF-BOT v5.4
- Finds config_multi.json in the SAME folder as the EXE
- Auto-update system
"""

import requests
import json
import time
import os
import sys
import re
import shutil
from datetime import datetime

# Version
VERSION = "5.4"
UPDATE_URL = "https://raw.githubusercontent.com/crocodile-bot/updates/main/selfbot.py"
VERSION_URL = "https://raw.githubusercontent.com/crocodile-bot/updates/main/version.json"

# ============================================================
# THEMES
# ============================================================
THEMES = {
    "crocodile": {
        "primary": '\033[92m',
        "secondary": '\033[38;5;34m',
        "accent": '\033[93m',
        "warning": '\033[93m',
        "error": '\033[91m',
        "reset": '\033[0m'
    },
    "blue": {
        "primary": '\033[94m',
        "secondary": '\033[96m',
        "accent": '\033[36m',
        "warning": '\033[93m',
        "error": '\033[91m',
        "reset": '\033[0m'
    },
    "red": {
        "primary": '\033[91m',
        "secondary": '\033[93m',
        "accent": '\033[95m',
        "warning": '\033[93m',
        "error": '\033[91m',
        "reset": '\033[0m'
    },
    "purple": {
        "primary": '\033[95m',
        "secondary": '\033[96m',
        "accent": '\033[92m',
        "warning": '\033[93m',
        "error": '\033[91m',
        "reset": '\033[0m'
    }
}

# Get the correct path for config files (same folder as EXE)
def get_base_path():
    """Get the base path where the EXE is located"""
    if getattr(sys, 'frozen', False):
        # Running as compiled EXE
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
CONFIG_FILE = os.path.join(BASE_PATH, "config_multi.json")
THEME_FILE = os.path.join(BASE_PATH, "theme.json")

# Current theme
C = THEMES["crocodile"]

def load_theme():
    global C
    if os.path.exists(THEME_FILE):
        with open(THEME_FILE, 'r') as f:
            theme_name = json.load(f).get('theme', 'crocodile')
            if theme_name in THEMES:
                C = THEMES[theme_name]
                return theme_name
    C = THEMES["crocodile"]
    return "crocodile"

def save_theme(theme_name):
    with open(THEME_FILE, 'w') as f:
        json.dump({"theme": theme_name}, f)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_for_updates():
    """Check if a new version is available online"""
    try:
        response = requests.get(VERSION_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get('version', VERSION)
            changelog = data.get('changelog', 'No changelog provided')
            download_url = data.get('url', UPDATE_URL)
            
            if latest_version != VERSION:
                return True, latest_version, changelog, download_url
    except:
        pass
    return False, None, None, None

def download_update(download_url):
    """Download the latest version"""
    try:
        print(f"{C['warning']}📥 Downloading update...{C['reset']}")
        response = requests.get(download_url, timeout=10)
        if response.status_code == 200:
            # Save to a temp file
            temp_file = os.path.join(BASE_PATH, "selfbot_update.py")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # If running as EXE, save the new script for next time
            if getattr(sys, 'frozen', False):
                print(f"{C['secondary']}   Update downloaded. Please replace your EXE manually.{C['reset']}")
                print(f"{C['warning']}   (EXE files cannot self-update, download new version from source){C['reset']}")
                return False
            else:
                # Running as script, can replace itself
                shutil.copy(temp_file, sys.argv[0])
                os.remove(temp_file)
                return True
    except Exception as e:
        print(f"{C['error']}   Update failed: {e}{C['reset']}")
    return False

def perform_update():
    """Handle the update process"""
    clear_screen()
    print(f"""
{C['primary']}╔═══════════════════════════════════════════════════════════════╗
║                    UPDATE AVAILABLE!                                    ║
╚═══════════════════════════════════════════════════════════════╝
{C['reset']}""")
    
    has_update, new_version, changelog, download_url = check_for_updates()
    
    if has_update:
        print(f"{C['warning']}Version {VERSION} → {new_version}{C['reset']}\n")
        print(f"{C['secondary']}Changelog:{C['reset']}")
        print(changelog)
        print()
        
        choice = input(f"{C['primary']}Update now? (y/n): {C['reset']}").strip().lower()
        
        if choice == 'y':
            if download_update(download_url):
                print(f"{C['primary']}✅ Update complete! Restarting...{C['reset']}")
                time.sleep(2)
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print(f"{C['error']}❌ Update failed!{C['reset']}")
                input("Press Enter to continue...")

def load_config():
    """Load config from config_multi.json in the EXE's folder"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(f"{C['primary']}✅ Loaded config from {CONFIG_FILE}{C['reset']}")
            print(f"{C['secondary']}   Found {len(config.get('channels', []))} channels{C['reset']}")
            return config
    else:
        print(f"{C['warning']}⚠️ No config file found at: {CONFIG_FILE}{C['reset']}")
        print(f"{C['secondary']}   Creating new config file...{C['reset']}")
        return {
            "token": "",
            "channels": [],
            "global_interval": 30
        }

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def test_token(token):
    headers = {"Authorization": token}
    try:
        response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"{C['primary']}✅ Token VALID! Logged in as: {user_data['username']}{C['reset']}")
            return True, user_data
        else:
            print(f"{C['error']}❌ Token INVALID! (Status: {response.status_code}){C['reset']}")
            return False, None
    except Exception as e:
        print(f"{C['error']}❌ Error: {e}{C['reset']}")
        return False, None

def get_channel_info(token, channel_id):
    headers = {"Authorization": token}
    try:
        url = f"https://discord.com/api/v9/channels/{channel_id}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def fetch_guild_emojis(token, guild_id):
    headers = {"Authorization": token}
    try:
        url = f"https://discord.com/api/v9/guilds/{guild_id}/emojis"
        response = requests.get(url, headers=headers)
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

def convert_emojis(message, emoji_map):
    if not emoji_map:
        return message
    
    converted = message
    for emoji_code, emoji_format in sorted(emoji_map.items(), key=lambda x: len(x[0]), reverse=True):
        converted = converted.replace(emoji_code, emoji_format)
    
    return converted

def extract_only_emojis(text):
    custom_emoji_pattern = r'<a?:\w+:\d+>'
    unicode_emoji_pattern = r'[\U00010000-\U0010ffff]|[\u2600-\u27BF]|[\uE000-\uF8FF]|\u00a9|\u00ae|\u2000-\u3300|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff]'
    
    custom_emojis = re.findall(custom_emoji_pattern, text)
    unicode_emojis = re.findall(unicode_emoji_pattern, text)
    
    all_emojis = custom_emojis + unicode_emojis
    return ' '.join(all_emojis)

def send_message(token, channel_id, raw_message, emoji_map, pure_emoji_mode):
    converted = convert_emojis(raw_message, emoji_map)
    
    if pure_emoji_mode:
        final_message = extract_only_emojis(converted)
        if not final_message:
            return False, "No emojis found"
    else:
        final_message = converted
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    payload = {"content": final_message}
    
    try:
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200 or response.status_code == 201:
            return True, "Success"
        elif response.status_code == 401:
            return False, "Invalid token"
        elif response.status_code == 403:
            return False, "No permission"
        elif response.status_code == 404:
            return False, "Channel not found"
        elif response.status_code == 429:
            return False, "Rate limited!"
        else:
            return False, f"Error {response.status_code}"
    except Exception as e:
        return False, str(e)

def refresh_emoji_map_for_channel(token, channel_id):
    channel_info = get_channel_info(token, channel_id)
    if channel_info and channel_info.get('guild_id'):
        guild_id = channel_info['guild_id']
        emoji_map = build_emoji_map_for_guild(token, guild_id)
        return emoji_map, guild_id
    return {}, None

def add_channel(config):
    print(f"\n{C['secondary']}┌─────────────────────────────────────────────────────────────────┐")
    print(f"│  ➕ ADD NEW CHANNEL")
    print(f"└─────────────────────────────────────────────────────────────────┘{C['reset']}\n")
    
    channel_id = input(f"{C['secondary']}Channel ID: {C['reset']}").strip()
    if not channel_id:
        print(f"{C['error']}Cancelled{C['reset']}")
        return
    
    try:
        channel_id = int(channel_id)
    except ValueError:
        print(f"{C['error']}Invalid channel ID!{C['reset']}")
        return
    
    print(f"\n{C['secondary']}┌─────────────────────────────────────────────────────────────────┐")
    print(f"│  SELECT MODE")
    print(f"├─────────────────────────────────────────────────────────────────┤")
    print(f"│  {C['primary']}1{C['reset']}. Normal mode (text + emojis)")
    print(f"│  {C['warning']}2{C['reset']}. Pure emoji mode (no text, only emojis)")
    print(f"└─────────────────────────────────────────────────────────────────┘{C['reset']}")
    
    mode_choice = input(f"\n{C['secondary']}Choose (1 or 2): {C['reset']}").strip()
    pure_emoji_mode = (mode_choice == "2")
    
    if pure_emoji_mode:
        print(f"\n{C['warning']}⚠️ PURE EMOJI MODE: Regular text will be removed!{C['reset']}")
    
    print(f"\n{C['secondary']}🔍 Fetching custom emojis...{C['reset']}")
    emoji_map, guild_id = refresh_emoji_map_for_channel(config['token'], channel_id)
    
    if emoji_map:
        print(f"{C['primary']}✅ Found {len(emoji_map)} custom emojis{C['reset']}")
    
    print(f"\n{C['secondary']}┌─────────────────────────────────────────────────────────────────┐")
    print(f"│  ENTER YOUR MESSAGE")
    print(f"├─────────────────────────────────────────────────────────────────┤")
    print(f"│  💡 Use :emoji_name: for custom server emojis")
    if pure_emoji_mode:
        print(f"│  ⚠️ Regular text will be removed automatically!")
    print(f"│  📝 Type 'END' on a new line when finished")
    print(f"│  📋 Type 'LIST' to see available emojis")
    print(f"└─────────────────────────────────────────────────────────────────┘{C['reset']}")
    
    lines = []
    while True:
        line = input()
        if line == "END":
            break
        if line == "LIST" and emoji_map:
            print(f"\n{C['primary']}Available emojis:{C['reset']}")
            for ec, ef in list(emoji_map.items())[:30]:
                print(f"   {ec} → {ef}")
            if len(emoji_map) > 30:
                print(f"   ... and {len(emoji_map) - 30} more")
            print()
            continue
        lines.append(line)
    
    raw_message = "\n".join(lines)
    
    if not raw_message.strip():
        raw_message = "W trade +rep 🔥"
    
    converted = convert_emojis(raw_message, emoji_map)
    
    print(f"\n{C['secondary']}┌─────────────────────────────────────────────────────────────────┐")
    print(f"│  MESSAGE PREVIEW")
    print(f"├─────────────────────────────────────────────────────────────────┤{C['reset']}")
    
    if pure_emoji_mode:
        final_preview = extract_only_emojis(converted)
        print(f"{C['warning']}   Raw: {raw_message[:60]}{C['reset']}")
        print(f"{C['secondary']}   Converted: {converted[:60]}{C['reset']}")
        print(f"{C['primary']}   Final (emoji only): {final_preview[:60]}{C['reset']}")
    else:
        print(f"{C['primary']}   {converted[:200]}{C['reset']}")
    
    print(f"{C['secondary']}└─────────────────────────────────────────────────────────────────┘{C['reset']}")
    
    print(f"\n{C['secondary']}Interval in seconds:{C['reset']}")
    interval_input = input(f"Enter number (or press Enter for {config['global_interval']}): {C['reset']}").strip()
    
    if interval_input:
        try:
            interval = int(interval_input)
        except ValueError:
            interval = config['global_interval']
    else:
        interval = config['global_interval']
    
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
    print(f"\n{C['primary']}✅ Channel {channel_id} added in {mode_text}!{C['reset']}")

def list_channels(config):
    if not config['channels']:
        print(f"{C['warning']}No channels configured yet.{C['reset']}")
        return
    
    print(f"\n{C['secondary']}┌─────────────────────────────────────────────────────────────────┐")
    print(f"│  📋 CONFIGURED CHANNELS")
    print(f"├─────────────────────────────────────────────────────────────────┤{C['reset']}")
    
    for i, ch in enumerate(config['channels']):
        status = f"{C['primary']}● ENABLED{C['reset']}" if ch['enabled'] else f"{C['error']}○ DISABLED{C['reset']}"
        
        if ch.get('pure_emoji_mode', False):
            mode = f"{C['warning']}[PURE EMOJI]{C['reset']}"
        else:
            mode = f"{C['secondary']}[NORMAL]{C['reset']}"
        
        print(f"\n  {C['accent']}{i+1}.{C['reset']} {status} {mode}")
        print(f"     📍 Channel: {ch['channel_id']}")
        msg_preview = ch.get('raw_message', '').replace('\n', ' ↵ ')[:60]
        print(f"     💬 Message: {msg_preview}{'...' if len(ch.get('raw_message', '')) > 60 else ''}")
        print(f"     ⏱️ Interval: {ch['interval']} seconds")
        if ch.get('last_sent'):
            print(f"     📅 Last sent: {ch['last_sent']}")
    
    print(f"{C['secondary']}└─────────────────────────────────────────────────────────────────┘{C['reset']}")

def toggle_channel(config):
    if not config['channels']:
        print(f"{C['warning']}No channels configured.{C['reset']}")
        return
    
    list_channels(config)
    try:
        choice = int(input(f"\n{C['secondary']}Channel number to toggle: {C['reset']}")) - 1
        if 0 <= choice < len(config['channels']):
            config['channels'][choice]['enabled'] = not config['channels'][choice]['enabled']
            status = "ENABLED" if config['channels'][choice]['enabled'] else "DISABLED"
            print(f"{C['primary']}✅ Channel toggled to {status}{C['reset']}")
            save_config(config)
        else:
            print(f"{C['error']}Invalid number{C['reset']}")
    except ValueError:
        print(f"{C['error']}Invalid input{C['reset']}")

def remove_channel(config):
    if not config['channels']:
        print(f"{C['warning']}No channels configured.{C['reset']}")
        return
    
    list_channels(config)
    try:
        choice = int(input(f"\n{C['secondary']}Channel number to remove: {C['reset']}")) - 1
        if 0 <= choice < len(config['channels']):
            removed = config['channels'].pop(choice)
            print(f"{C['primary']}✅ Removed channel {removed['channel_id']}{C['reset']}")
            save_config(config)
        else:
            print(f"{C['error']}Invalid number{C['reset']}")
    except ValueError:
        print(f"{C['error']}Invalid input{C['reset']}")

def send_to_all_channels_once(config):
    if not config['channels']:
        print(f"{C['warning']}No channels configured.{C['reset']}")
        return
    
    enabled_channels = [ch for ch in config['channels'] if ch['enabled']]
    if not enabled_channels:
        print(f"{C['warning']}No enabled channels.{C['reset']}")
        return
    
    print(f"\n{C['secondary']}📤 Sending to {len(enabled_channels)} channels...{C['reset']}\n")
    
    success_count = 0
    fail_count = 0
    
    for ch in enabled_channels:
        emoji_map = ch.get('emoji_map', {})
        if not emoji_map and ch.get('guild_id'):
            emoji_map, _ = refresh_emoji_map_for_channel(config['token'], ch['channel_id'])
            ch['emoji_map'] = emoji_map
            save_config(config)
        
        raw_msg = ch.get('raw_message', '')
        pure_mode = ch.get('pure_emoji_mode', False)
        
        mode_icon = "🔮" if pure_mode else "📝"
        print(f"  {mode_icon} Sending to {ch['channel_id']}...", end=" ")
        
        success, error = send_message(config['token'], ch['channel_id'], raw_msg, emoji_map, pure_mode)
        
        if success:
            print(f"{C['primary']}✓ Sent{C['reset']}")
            success_count += 1
            ch['last_sent'] = datetime.now().strftime('%H:%M:%S')
        else:
            print(f"{C['error']}✗ Failed: {error}{C['reset']}")
            fail_count += 1
        
        time.sleep(0.5)
    
    save_config(config)
    
    print(f"\n{C['primary']}✅ Sent to {success_count} channels{C['reset']}")
    if fail_count > 0:
        print(f"{C['error']}❌ Failed: {fail_count} channels{C['reset']}")
    
    input(f"{C['secondary']}Press Enter to continue...{C['reset']}")

def auto_send_all_channels(config):
    if not config['channels']:
        print(f"{C['warning']}No channels configured.{C['reset']}")
        return
    
    enabled = [ch for ch in config['channels'] if ch['enabled']]
    if not enabled:
        print(f"{C['warning']}No enabled channels.{C['reset']}")
        return
    
    print(f"\n{C['primary']}🟢 AUTO-SEND STARTED{C['reset']}")
    print(f"{C['secondary']}   Channels: {len(enabled)}{C['reset']}")
    for ch in enabled:
        mode = "PURE" if ch.get('pure_emoji_mode', False) else "NORMAL"
        print(f"   [{mode}] {ch['channel_id']}: every {ch['interval']}s")
    print(f"\n   Press Ctrl+C to stop\n")
    
    last_sent = {ch['channel_id']: 0 for ch in enabled}
    count = 0
    
    try:
        while True:
            current_time = time.time()
            
            for ch in enabled:
                if current_time - last_sent.get(ch['channel_id'], 0) >= ch['interval']:
                    count += 1
                    print(f"{C['accent']}[{datetime.now().strftime('%H:%M:%S')}] Sending to {ch['channel_id']}{C['reset']}")
                    
                    emoji_map = ch.get('emoji_map', {})
                    if not emoji_map and ch.get('guild_id'):
                        emoji_map, _ = refresh_emoji_map_for_channel(config['token'], ch['channel_id'])
                        ch['emoji_map'] = emoji_map
                        save_config(config)
                    
                    raw_msg = ch.get('raw_message', '')
                    pure_mode = ch.get('pure_emoji_mode', False)
                    success, error = send_message(config['token'], ch['channel_id'], raw_msg, emoji_map, pure_mode)
                    
                    if success:
                        print(f"  {C['primary']}✓ Sent{C['reset']}")
                        last_sent[ch['channel_id']] = current_time
                        ch['last_sent'] = datetime.now().strftime('%H:%M:%S')
                        save_config(config)
                    else:
                        print(f"  {C['error']}✗ Failed: {error}{C['reset']}")
                    
                    time.sleep(0.5)
            
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{C['error']}🔴 STOPPED - {count} messages sent{C['reset']}")
        input(f"{C['secondary']}Press Enter to continue...{C['reset']}")

def refresh_emojis(config):
    print(f"\n{C['secondary']}🔄 Refreshing emoji maps...{C['reset']}")
    for ch in config['channels']:
        emoji_map, guild_id = refresh_emoji_map_for_channel(config['token'], ch['channel_id'])
        ch['emoji_map'] = emoji_map
        ch['guild_id'] = guild_id
        time.sleep(0.5)
    save_config(config)
    print(f"{C['primary']}✅ Emoji maps refreshed!{C['reset']}")

def change_theme():
    print(f"\n{C['secondary']}┌─────────────────────────────────────────────────────────────────┐")
    print(f"│  🎨 CHANGE THEME")
    print(f"├─────────────────────────────────────────────────────────────────┤{C['reset']}")
    
    themes_list = list(THEMES.keys())
    for i, theme in enumerate(themes_list):
        current = load_theme()
        if theme == current:
            print(f"  {C['primary']}{i+1}. {theme} ✓{C['reset']}")
        else:
            print(f"  {i+1}. {theme}")
    
    choice = input(f"\n{C['secondary']}Choose theme (1-{len(themes_list)}): {C['reset']}").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(themes_list):
            theme_name = themes_list[idx]
            save_theme(theme_name)
            print(f"{C['primary']}✅ Theme changed to {theme_name}! Restart to apply.{C['reset']}")
            input(f"{C['secondary']}Press Enter to restart...{C['reset']}")
            os.execv(sys.executable, [sys.executable] + sys.argv)
    except:
        print(f"{C['error']}Invalid choice{C['reset']}")

def show_help():
    print(f"""
{C['primary']}┌─────────────────────────────────────────────────────────────────┐
│  📖 HELP & TUTORIAL                                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  {C['accent']}NORMAL MODE:{C['reset']}                                                 │
│     - Text + emojis together                                      │
│     - Use :emoji: for custom server emojis                        │
│                                                                   │
│  {C['accent']}PURE EMOJI MODE:{C['reset']}                                              │
│     - For servers that BLOCK text messages                        │
│     - ONLY emojis are sent, text is removed                       │
│                                                                   │
│  {C['accent']}EXAMPLE:{C['reset']}                                                    │
│     Normal: **LOOKING FOR** :LF: :Dragon:                         │
│     Pure:   <:LF:ID> <:Dragon:ID> (text removed)                  │
│                                                                   │
│  {C['accent']}HOW TO GET CHANNEL ID:{C['reset']}                                          │
│     Settings → Advanced → Developer Mode ON                       │
│     Right-click channel → Copy ID                                 │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘{C['reset']}""")

def setup_wizard():
    clear_screen()
    print_banner()
    
    print(f"{C['warning']}⚠️  WARNING: Self-bots violate Discord ToS{C['reset']}\n")
    
    confirm = input(f"{C['secondary']}Type 'YES' to continue: {C['reset']}")
    if confirm.upper() != "YES":
        sys.exit(0)
    
    token = input(f"\n{C['secondary']}Enter your Discord token: {C['reset']}").strip()
    
    valid, user_data = test_token(token)
    if not valid:
        retry = input(f"{C['secondary']}Try again? (y/n): {C['reset']}")
        if retry.lower() == 'y':
            return setup_wizard()
        sys.exit(0)
    
    config = {
        "token": token,
        "channels": [],
        "global_interval": 30
    }
    
    save_config(config)
    
    print(f"\n{C['primary']}✅ Setup complete! Welcome {user_data['username']}{C['reset']}")
    input(f"{C['secondary']}Press Enter to continue...{C['reset']}")
    
    return config

def print_banner():
    print(f"""
{C['primary']}╔══════════════════════════════════════════════════════════════════╗
║                                                                          ║
║         🐊 CROCODILE SELF-BOT v{VERSION} 🐊                              ║
║                                                                          ║
║     ┌─────────────────────────────────────────────────────────┐         ║
║     │  Dual Mode: Normal + Pure Emoji (for strict servers)   │         ║
║     └─────────────────────────────────────────────────────────┘         ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
{C['reset']}""")

def main():
    global C
    load_theme()
    
    clear_screen()
    print_banner()
    
    # Check for updates (only if not running from EXE or manual check)
    print(f"{C['secondary']}🔍 Checking for updates...{C['reset']}")
    has_update, new_version, changelog, _ = check_for_updates()
    if has_update:
        print(f"{C['warning']}⚠️ Update available: v{new_version}{C['reset']}")
        update_choice = input(f"{C['primary']}Update now? (y/n): {C['reset']}").strip().lower()
        if update_choice == 'y':
            perform_update()
            return
    
    config = load_config()
    
    # If no token in config, run setup
    if not config.get("token"):
        config = setup_wizard()
    else:
        # Test token on startup
        print(f"\n{C['secondary']}🔑 Verifying token...{C['reset']}")
        valid, user_data = test_token(config['token'])
        if not valid:
            print(f"{C['error']}⚠️ Token may be expired. You may need to re-enter it.{C['reset']}")
            input(f"{C['secondary']}Press Enter to continue...{C['reset']}")
    
    while True:
        clear_screen()
        print_banner()
        
        enabled_count = sum(1 for ch in config['channels'] if ch.get('enabled', True))
        total_count = len(config['channels'])
        pure_count = sum(1 for ch in config['channels'] if ch.get('pure_emoji_mode', False))
        current_theme = load_theme()
        
        print(f"{C['secondary']}┌─────────────────────────────────────────────────────────────────┐")
        print(f"│  📊 STATUS DASHBOARD")
        print(f"├─────────────────────────────────────────────────────────────────┤")
        print(f"│  {C['primary']}●{C['reset']} Channels: {total_count} total, {enabled_count} enabled")
        print(f"│  {C['warning']}🔮{C['reset']} Pure emoji mode: {pure_count} channels")
        print(f"│  {C['secondary']}📝{C['reset']} Normal mode: {total_count - pure_count} channels")
        print(f"│  {C['accent']}🎨{C['reset']} Theme: {current_theme}")
        print(f"│  {C['accent']}📂{C['reset']} Config path: {CONFIG_FILE}")
        print(f"└─────────────────────────────────────────────────────────────────┘{C['reset']}")
        
        print(f"""
{C['primary']}╔══════════════════════════════════════════════════════════════════╗
║  MAIN MENU                                                          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  {C['accent']}1{C['reset']}  📤 Send to ALL channels (once)                         ║
║  {C['accent']}2{C['reset']}  🔄 Start AUTO-SEND (loop)                              ║
║  {C['accent']}3{C['reset']}  ➕ Add a channel                                       ║
║  {C['accent']}4{C['reset']}  📋 List all channels                                   ║
║  {C['accent']}5{C['reset']}  🔘 Enable/Disable a channel                            ║
║  {C['accent']}6{C['reset']}  🗑️ Remove a channel                                    ║
║  {C['accent']}7{C['reset']}  🔄 Refresh emoji maps                                  ║
║  {C['accent']}8{C['reset']}  🔑 Test token                                          ║
║  {C['accent']}9{C['reset']}  🎨 Change theme                                        ║
║  {C['accent']}0{C['reset']}  ❓ Help                                                ║
║  {C['accent']}U{C['reset']}  🔄 Check for updates                                   ║
║  {C['accent']}Q{C['reset']}  🚪 Exit                                                ║
║                                                                     ║
╚══════════════════════════════════════════════════════════════════╝
{C['reset']}""")
        
        choice = input(f"{C['secondary']}👉 Choose: {C['reset']}").strip().upper()
        
        if choice == "1":
            send_to_all_channels_once(config)
        elif choice == "2":
            auto_send_all_channels(config)
        elif choice == "3":
            add_channel(config)
            input(f"{C['secondary']}Press Enter...{C['reset']}")
        elif choice == "4":
            list_channels(config)
            input(f"\n{C['secondary']}Press Enter...{C['reset']}")
        elif choice == "5":
            toggle_channel(config)
            input(f"{C['secondary']}Press Enter...{C['reset']}")
        elif choice == "6":
            remove_channel(config)
            input(f"{C['secondary']}Press Enter...{C['reset']}")
        elif choice == "7":
            refresh_emojis(config)
            input(f"{C['secondary']}Press Enter...{C['reset']}")
        elif choice == "8":
            print()
            test_token(config['token'])
            input(f"{C['secondary']}Press Enter...{C['reset']}")
        elif choice == "9":
            change_theme()
        elif choice == "0":
            show_help()
            input(f"{C['secondary']}Press Enter...{C['reset']}")
        elif choice == "U":
            perform_update()
        elif choice == "Q":
            print(f"\n{C['primary']}👋 Goodbye!{C['reset']}")
            break
        else:
            print(f"{C['error']}Invalid choice{C['reset']}")
            input(f"{C['secondary']}Press Enter...{C['reset']}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C['warning']}Goodbye!{C['reset']}")
        sys.exit(0)