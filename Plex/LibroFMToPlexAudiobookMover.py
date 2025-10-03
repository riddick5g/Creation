#!/usr/bin/env python3
"""
LibroFM to Plex Audiobook Mover
Moves .m4b files from download folder to Plex, creating individual folders for each book.
"""

import os
import shutil
from pathlib import Path

# ============ CONFIGURATION ============
# Change these paths to match your setup
SOURCE_FOLDER = "C:\Users\chris\Downloads"  # Where Libro.fm downloads go
PLEX_DESTINATION = "D:\Plexy"  # Your Plex audiobooks folder
# =======================================

def move_audiobooks(source_dir, dest_dir, dry_run=False):
    """
    Move .m4b files from source to destination, creating a folder for each book.
    
    Args:
        source_dir: Path to folder containing downloaded .m4b files
        dest_dir: Path to Plex audiobooks library
        dry_run: If True, only show what would be done without moving files
    """
    source_path = Path(source_dir)
    dest_path = Path(dest_dir)
    
    # Validate paths
    if not source_path.exists():
        print(f"❌ Error: Source folder does not exist: {source_dir}")
        return
    
    if not dest_path.exists():
        print(f"❌ Error: Destination folder does not exist: {dest_dir}")
        return
    
    # Find all .m4b files
    m4b_files = list(source_path.glob("*.m4b"))
    
    if not m4b_files:
        print(f"ℹ️  No .m4b files found in {source_dir}")
        return
    
    print(f"Found {len(m4b_files)} audiobook(s) to process:\n")
    
    # Process each file
    for m4b_file in m4b_files:
        # Get filename without extension for folder name
        book_name = m4b_file.stem
        
        # Create destination folder path
        book_folder = dest_path / book_name
        destination_file = book_folder / m4b_file.name
        
        print(f"📚 {m4b_file.name}")
        print(f"   → Creating folder: {book_folder}")
        print(f"   → Moving to: {destination_file}")
        
        if not dry_run:
            try:
                # Create the book folder
                book_folder.mkdir(parents=True, exist_ok=True)
                
                # Move the file
                shutil.move(str(m4b_file), str(destination_file))
                print(f"   ✅ Successfully moved!\n")
                
            except Exception as e:
                print(f"   ❌ Error moving file: {e}\n")
        else:
            print(f"   [DRY RUN - no changes made]\n")
    
    if dry_run:
        print("\n⚠️  This was a dry run. Set dry_run=False to actually move files.")

def main():
    print("=" * 60)
    print("LibroFM to Plex Audiobook Mover")
    print("=" * 60)
    print(f"\nSource: {SOURCE_FOLDER}")
    print(f"Destination: {PLEX_DESTINATION}\n")
    
    # Set to True to test without moving files
    DRY_RUN = True
    
    if DRY_RUN:
        print("🔍 Running in DRY RUN mode (no files will be moved)\n")
    
    move_audiobooks(SOURCE_FOLDER, PLEX_DESTINATION, dry_run=DRY_RUN)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()