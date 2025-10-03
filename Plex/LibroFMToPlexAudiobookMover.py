#!/usr/bin/env python3
"""
LibroFM to Plex Audiobook Mover
Moves .m4b files from download folder to Plex, creating individual folders for each book.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# ============ CONFIGURATION ============
# Change these paths to match your setup
SOURCE_FOLDER = r"C:\Users\chris\Downloads"  # Where Libro.fm downloads go
PLEX_DESTINATION = r"D:\Plexy"  # Your Plex audiobooks folder
LOG_FILENAME = "librofm_mover.log"  # Log file name
# =======================================

def log(message, log_path, print_to_console=True):
    """Write message to log file and optionally print to console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    
    if print_to_console:
        print(message)
    
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")

def move_audiobooks(source_dir, dest_dir, log_path, dry_run=False):
    """
    Move .m4b files from source to destination, creating a folder for each book.
    
    Args:
        source_dir: Path to folder containing downloaded .m4b files
        dest_dir: Path to Plex audiobooks library
        log_path: Path to log file
        dry_run: If True, only show what would be done without moving files
    """
    source_path = Path(source_dir)
    dest_path = Path(dest_dir)
    
    # Validate paths
    if not source_path.exists():
        log(f"❌ Error: Source folder does not exist: {source_dir}", log_path)
        return
    
    if not dest_path.exists():
        log(f"❌ Error: Destination folder does not exist: {dest_dir}", log_path)
        return
    
    # Find all .m4b files
    m4b_files = list(source_path.glob("*.m4b"))
    
    if not m4b_files:
        log(f"ℹ️  No .m4b files found in {source_dir}", log_path)
        return
    
    log(f"Found {len(m4b_files)} audiobook(s) to process:", log_path)
    log("", log_path)
    
    # Process each file
    for m4b_file in m4b_files:
        # Get filename without extension for folder name
        book_name = m4b_file.stem
        
        # Create destination folder path
        book_folder = dest_path / book_name
        destination_file = book_folder / m4b_file.name
        
        log(f"📚 {m4b_file.name}", log_path)
        log(f"   → Creating folder: {book_folder}", log_path)
        log(f"   → Moving to: {destination_file}", log_path)
        
        if not dry_run:
            try:
                # Create the book folder
                book_folder.mkdir(parents=True, exist_ok=True)
                
                # Move the file
                shutil.move(str(m4b_file), str(destination_file))
                log(f"   ✅ Successfully moved!", log_path)
                log("", log_path)
                
            except Exception as e:
                log(f"   ❌ Error moving file: {e}", log_path)
                log("", log_path)
        else:
            log(f"   [DRY RUN - no changes made]", log_path)
            log("", log_path)
    
    if dry_run:
        log("⚠️  This was a dry run. Set dry_run=False to actually move files.", log_path)

def main():
    log_path = Path(LOG_FILENAME)
    
    log("=" * 60, log_path)
    log("LibroFM to Plex Audiobook Mover", log_path)
    log("=" * 60, log_path)
    log(f"Source: {SOURCE_FOLDER}", log_path)
    log(f"Destination: {PLEX_DESTINATION}", log_path)
    log(f"Log file: {log_path}", log_path)
    log("", log_path)
    
    # Set to True to test without moving files
    DRY_RUN = True
    
    if DRY_RUN:
        log("🔍 Running in DRY RUN mode (no files will be moved)", log_path)
        log("", log_path)
    
    move_audiobooks(SOURCE_FOLDER, PLEX_DESTINATION, log_path, dry_run=DRY_RUN)
    
    log("=" * 60, log_path)

if __name__ == "__main__":
    main()