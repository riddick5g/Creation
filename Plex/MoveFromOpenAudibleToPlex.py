#!/usr/bin/env python3
"""
OpenAudible Audiobook Organizer
Copies M4B audiobook files and their corresponding album art into organized folders,
renaming the art to "cover.jpg" for Plex compatibility.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# ============================================
# CONFIGURATION - Adjust these paths
# ============================================

# Source folder containing M4B audiobook files
M4B_SOURCE_FOLDER = r"example_path"

# Source folder containing album art (JPEG/JPG/PNG files)
ALBUM_ART_SOURCE_FOLDER = r"example_path"

# Destination folder where organized audiobooks will be placed
DESTINATION_FOLDER = r"example_path"

# Log file name (will append, not create timestamped files)
LOG_FILENAME = "openaudible_organizer.log"

# ============================================
# SCRIPT START
# ============================================

def log(message, log_path, print_to_console=True):
    """Write message to log file and optionally print to console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    
    if print_to_console:
        print(message)
    
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")

def find_matching_album_art(base_name, album_art_folder):
    """Find album art file matching the audiobook base name."""
    art_folder = Path(album_art_folder)
    extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
    
    for ext in extensions:
        art_file = art_folder / f"{base_name}{ext}"
        if art_file.exists():
            return art_file
    
    return None

def organize_audiobooks(m4b_source, art_source, destination, log_path, dry_run=False):
    """
    Organize M4B files and album art into Plex-compatible folder structure.
    
    Args:
        m4b_source: Path to folder containing M4B files
        art_source: Path to folder containing album art
        destination: Path to destination folder
        log_path: Path to log file
        dry_run: If True, only show what would be done without copying files
    """
    m4b_path = Path(m4b_source)
    art_path = Path(art_source)
    dest_path = Path(destination)
    
    log("=" * 70, log_path)
    log("OpenAudible Audiobook Organizer", log_path)
    log("=" * 70, log_path)
    log(f"M4B Source: {m4b_source}", log_path)
    log(f"Album Art Source: {art_source}", log_path)
    log(f"Destination: {destination}", log_path)
    log(f"Log file: {log_path}", log_path)
    
    if dry_run:
        log("\n🔍 DRY RUN MODE - No files will be copied\n", log_path)
    else:
        log("", log_path)
    
    # Validate source folders
    if not m4b_path.exists():
        log(f"❌ ERROR: M4B source folder does not exist: {m4b_source}", log_path)
        return
    
    if not art_path.exists():
        log(f"❌ ERROR: Album art source folder does not exist: {art_source}", log_path)
        return
    
    # Create destination folder if it doesn't exist
    if not dest_path.exists() and not dry_run:
        dest_path.mkdir(parents=True, exist_ok=True)
        log(f"Created destination folder: {destination}", log_path)
    
    # Get all M4B files
    m4b_files = list(m4b_path.glob("*.m4b"))
    
    if not m4b_files:
        log("ℹ️  No M4B files found in source folder", log_path)
        return
    
    log(f"Found {len(m4b_files)} M4B file(s) to process\n", log_path)
    
    stats = {
        'success': 0,
        'skipped': 0,
        'failures': 0
    }
    
    for m4b_file in sorted(m4b_files):
        try:
            # Get base name without extension (will be the folder name)
            base_name = m4b_file.stem
            
            # Create destination paths
            audiobook_folder = dest_path / base_name
            m4b_destination = audiobook_folder / m4b_file.name
            
            # Check if M4B file already exists in destination
            if m4b_destination.exists():
                # Compare file sizes
                source_size = m4b_file.stat().st_size
                dest_size = m4b_destination.stat().st_size
                
                if source_size == dest_size:
                    log(f"⏭️  Skipping (already exists): {base_name}", log_path)
                    stats['skipped'] += 1
                    continue
                else:
                    log(f"📚 Processing (file size mismatch): {base_name}", log_path)
            else:
                log(f"📚 Processing (new): {base_name}", log_path)
            
            # Create folder
            if dry_run:
                log(f"   [DRY RUN] Would create folder: {audiobook_folder}", log_path)
            else:
                audiobook_folder.mkdir(parents=True, exist_ok=True)
                log(f"   Created folder: {audiobook_folder}", log_path)
            
            # Copy M4B file
            if dry_run:
                log(f"   [DRY RUN] Would copy M4B file to: {m4b_destination}", log_path)
            else:
                shutil.copy2(m4b_file, m4b_destination)
                log(f"   Copied M4B file to: {m4b_destination}", log_path)
            
            # Look for matching album art
            album_art_file = find_matching_album_art(base_name, art_source)
            
            if album_art_file:
                cover_destination = audiobook_folder / "cover.jpg"
                
                if dry_run:
                    log(f"   [DRY RUN] Would copy album art: {album_art_file.name} -> cover.jpg", log_path)
                else:
                    shutil.copy2(album_art_file, cover_destination)
                    log(f"   Copied and renamed album art: {album_art_file.name} -> cover.jpg", log_path)
            else:
                log(f"   ⚠️  WARNING: No matching album art found for: {base_name}", log_path)
            
            stats['success'] += 1
            log("", log_path)
            
        except Exception as e:
            log(f"   ❌ ERROR processing {m4b_file.name}: {e}", log_path)
            stats['failures'] += 1
            log("", log_path)
    
    # Print summary
    log("=" * 70, log_path)
    log("SUMMARY", log_path)
    log("=" * 70, log_path)
    log(f"Successfully processed: {stats['success']}", log_path)
    log(f"Skipped (already exist): {stats['skipped']}", log_path)
    log(f"Failures: {stats['failures']}", log_path)
    log("=" * 70, log_path)

def main():
    # Set to True to test without copying files
    DRY_RUN = True
    
    log_path = Path(LOG_FILENAME)
    
    organize_audiobooks(
        m4b_source=M4B_SOURCE_FOLDER,
        art_source=ALBUM_ART_SOURCE_FOLDER,
        destination=DESTINATION_FOLDER,
        log_path=log_path,
        dry_run=DRY_RUN
    )

if __name__ == "__main__":
    main()