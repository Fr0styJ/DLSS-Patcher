import os
import string
from ctypes import windll

TARGET_FILES = {"nvngx_dlss.dll", "nvngx_dlssd.dll", "nvngx_dlssg.dll"}

def get_available_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(f"{letter}:\\")
        bitmask >>= 1
    return drives

def extract_game_name(base_path, discovered_dir):
    # E.g., C:\SteamLibrary\steamapps\common\Cyberpunk 2077\bin\x64
    # base_path: C:\SteamLibrary\steamapps\common
    # discovered_dir: C:\SteamLibrary\steamapps\common\Cyberpunk 2077\bin\x64
    rel_path = os.path.relpath(discovered_dir, base_path)
    # The first component of the relative path is usually the game folder
    # In 'Cyberpunk 2077\bin\x64', it's 'Cyberpunk 2077'
    parts = rel_path.split(os.sep)
    if parts:
        return parts[0]
    return "Unknown Game"

def scan_for_games(progress_callback=None):
    found_games = []
    drives = get_available_drives()
    
    # Priority paths per drive
    priority_paths = [
        r"Steam\steamapps\common",
        r"SteamLibrary\steamapps\common",
        r"XboxGames",
        r"Program Files (x86)\Steam\steamapps\common",
        r"Epic Games",
        r"GOG Galaxy\Games"
    ]
    
    for drive in drives:
        for p_path in priority_paths:
            full_base = os.path.join(drive, p_path)
            if not os.path.exists(full_base):
                continue
            
            if progress_callback:
                progress_callback(f"Scanning {full_base}...")
                
            try:
                for root, dirs, files in os.walk(full_base):
                    file_set = set(f.lower() for f in files)
                    matched_dlls = file_set.intersection({f.lower() for f in TARGET_FILES})
                    
                    if matched_dlls:
                        game_name = extract_game_name(full_base, root)
                        
                        # Check if we already added this game directory to avoid duplicates
                        # Store dict with game_name, path, and found_dlls
                        existing = next((g for g in found_games if g['path'] == root), None)
                        if not existing:
                            found_games.append({
                                'name': game_name,
                                'path': root,
                                'dlls': list(matched_dlls)
                            })
                            if progress_callback:
                                progress_callback(f"Found {game_name} at {root}")
            except Exception as e:
                if progress_callback:
                    progress_callback(f"Error scanning {full_base}: {e}")
                    
    return found_games
