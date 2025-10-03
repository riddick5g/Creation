#!/usr/bin/env python3
"""
Audiobook Cover Art Downloader
Scans Plex audiobook folders and downloads missing cover art from iTunes and Open Library APIs.
"""

import os
import requests
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

# ============ CONFIGURATION ============
PLEX_AUDIOBOOKS_FOLDER = r"D:\Plexy"  # Your Plex audiobooks folder
COVER_FILENAME = "cover.jpg"  # What to name the cover art file
LOG_FILENAME = "cover_art_download.log"  # Log file name
# =======================================

class CoverArtDownloader:
    def __init__(self, audiobooks_path, cover_filename, log_path):
        self.audiobooks_path = Path(audiobooks_path)
        self.cover_filename = cover_filename
        self.log_path = Path(log_path)
        self.stats = {
            'total_folders': 0,
            'already_has_cover': 0,
            'downloaded_itunes': 0,
            'downloaded_openlibrary': 0,
            'failed': 0
        }
        
    def log(self, message, print_to_console=True):
        """Write message to log file and optionally print to console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        if print_to_console:
            print(message)
        
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(log_message + "\n")
    
    def search_itunes(self, book_title):
        """Search iTunes API for audiobook cover art."""
        try:
            # Clean up title for search
            search_term = quote(book_title)
            url = f"https://itunes.apple.com/search?term={search_term}&media=audiobook&limit=1"
            
            self.log(f"   🔍 Searching iTunes: {url}", print_to_console=False)
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('resultCount', 0) > 0:
                result = data['results'][0]
                # Get highest quality artwork (replace 100x100 with 600x600)
                artwork_url = result.get('artworkUrl100', '').replace('100x100', '600x600')
                
                if artwork_url:
                    self.log(f"   ✅ Found on iTunes: {artwork_url}", print_to_console=False)
                    return artwork_url
            
            self.log(f"   ❌ Not found on iTunes", print_to_console=False)
            return None
            
        except Exception as e:
            self.log(f"   ⚠️  iTunes search error: {e}", print_to_console=False)
            return None
    
    def search_openlibrary(self, book_title):
        """Search Open Library API for book cover art."""
        try:
            search_term = quote(book_title)
            url = f"https://openlibrary.org/search.json?title={search_term}&limit=1"
            
            self.log(f"   🔍 Searching Open Library: {url}", print_to_console=False)
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('numFound', 0) > 0:
                doc = data['docs'][0]
                cover_id = doc.get('cover_i')
                
                if cover_id:
                    # Get large cover image
                    artwork_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                    self.log(f"   ✅ Found on Open Library: {artwork_url}", print_to_console=False)
                    return artwork_url
            
            self.log(f"   ❌ Not found on Open Library", print_to_console=False)
            return None
            
        except Exception as e:
            self.log(f"   ⚠️  Open Library search error: {e}", print_to_console=False)
            return None
    
    def download_image(self, url, destination):
        """Download image from URL to destination path."""
        try:
            response = requests.get(url, timeout=15, stream=True)
            response.raise_for_status()
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
            
        except Exception as e:
            self.log(f"   ❌ Download error: {e}")
            return False
    
    def has_cover_art(self, folder_path):
        """Check if folder already has cover art."""
        common_cover_names = [
            'cover.jpg', 'cover.jpeg', 'cover.png',
            'folder.jpg', 'folder.jpeg', 'folder.png',
            'poster.jpg', 'poster.jpeg', 'poster.png'
        ]
        
        for cover_name in common_cover_names:
            if (folder_path / cover_name).exists():
                return True
        return False
    
    def process_folders(self, dry_run=False):
        """Process all audiobook folders."""
        self.log("=" * 70)
        self.log("Audiobook Cover Art Downloader")
        self.log("=" * 70)
        self.log(f"Audiobooks folder: {self.audiobooks_path}")
        self.log(f"Cover filename: {self.cover_filename}")
        self.log(f"Log file: {self.log_path}")
        
        if dry_run:
            self.log("\n🔍 DRY RUN MODE - No files will be downloaded\n")
        else:
            self.log("")
        
        if not self.audiobooks_path.exists():
            self.log(f"❌ Error: Audiobooks folder does not exist: {self.audiobooks_path}")
            return
        
        # Get all subdirectories (each should be a book folder)
        book_folders = [f for f in self.audiobooks_path.iterdir() if f.is_dir()]
        
        if not book_folders:
            self.log("ℹ️  No book folders found")
            return
        
        self.log(f"Found {len(book_folders)} book folder(s)\n")
        
        for folder in sorted(book_folders):
            self.stats['total_folders'] += 1
            book_title = folder.name
            
            self.log(f"📚 {book_title}")
            
            # Check if already has cover
            if self.has_cover_art(folder):
                self.log(f"   ✓ Already has cover art")
                self.stats['already_has_cover'] += 1
                self.log("")
                continue
            
            # Search for cover art
            artwork_url = None
            source = None
            
            # Try iTunes first
            artwork_url = self.search_itunes(book_title)
            if artwork_url:
                source = 'iTunes'
            else:
                # Fallback to Open Library
                artwork_url = self.search_openlibrary(book_title)
                if artwork_url:
                    source = 'Open Library'
            
            if not artwork_url:
                self.log(f"   ❌ No cover art found")
                self.stats['failed'] += 1
                self.log("")
                continue
            
            # Download the cover art
            cover_path = folder / self.cover_filename
            
            if dry_run:
                self.log(f"   [DRY RUN] Would download from {source}: {artwork_url}")
                self.log(f"   [DRY RUN] Would save to: {cover_path}")
            else:
                self.log(f"   📥 Downloading from {source}...")
                if self.download_image(artwork_url, cover_path):
                    self.log(f"   ✅ Saved to: {cover_path}")
                    if source == 'iTunes':
                        self.stats['downloaded_itunes'] += 1
                    else:
                        self.stats['downloaded_openlibrary'] += 1
                else:
                    self.stats['failed'] += 1
            
            self.log("")
            
            # Be nice to the APIs
            time.sleep(0.5)
        
        # Print summary
        self.log("=" * 70)
        self.log("SUMMARY")
        self.log("=" * 70)
        self.log(f"Total folders processed: {self.stats['total_folders']}")
        self.log(f"Already had cover art: {self.stats['already_has_cover']}")
        self.log(f"Downloaded from iTunes: {self.stats['downloaded_itunes']}")
        self.log(f"Downloaded from Open Library: {self.stats['downloaded_openlibrary']}")
        self.log(f"Failed to find: {self.stats['failed']}")
        self.log("=" * 70)

def main():
    # Set to True to test without downloading
    DRY_RUN = True
    
    downloader = CoverArtDownloader(
        audiobooks_path=PLEX_AUDIOBOOKS_FOLDER,
        cover_filename=COVER_FILENAME,
        log_path=LOG_FILENAME
    )
    
    downloader.process_folders(dry_run=DRY_RUN)

if __name__ == "__main__":
    main()