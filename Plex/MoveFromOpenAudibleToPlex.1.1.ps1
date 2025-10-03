# ============================================
# Audiobook Album Art Organizer Script
# ============================================
# This script copies M4B audiobook files and their corresponding album art
# into organized folders, renaming the art to "cover.jpg" for Plex compatibility

# ============================================
# CONFIGURATION - Adjust these paths
# ============================================

# Source folder containing M4B audiobook files
$m4bSourceFolder = "D:\iCloudDrive\AudioBooks\books"

# Source folder containing album art (JPEG/JPG files)
$albumArtSourceFolder = "D:\iCloudDrive\AudioBooks\cover"

# Destination folder where organized audiobooks will be placed
$destinationFolder = "D:\Plexy"

# ============================================
# SCRIPT START - DO NOT MODIFY BELOW
# ============================================

# Create log file with timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$logFile = Join-Path $destinationFolder "AudiobookOrganizer_$timestamp.log"

function Write-Log {
    param($Message)
    $logMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message"
    Write-Host $logMessage
    Add-Content -Path $logFile -Value $logMessage
}

Write-Log "=== Audiobook Organizer Script Started ==="
Write-Log "M4B Source: $m4bSourceFolder"
Write-Log "Album Art Source: $albumArtSourceFolder"
Write-Log "Destination: $destinationFolder"

# Validate source folders exist
if (-not (Test-Path $m4bSourceFolder)) {
    Write-Log "ERROR: M4B source folder does not exist: $m4bSourceFolder"
    exit 1
}

if (-not (Test-Path $albumArtSourceFolder)) {
    Write-Log "ERROR: Album art source folder does not exist: $albumArtSourceFolder"
    exit 1
}

# Create destination folder if it doesn't exist
if (-not (Test-Path $destinationFolder)) {
    New-Item -ItemType Directory -Path $destinationFolder -Force | Out-Null
    Write-Log "Created destination folder: $destinationFolder"
}

# Get all M4B files from source
$m4bFiles = Get-ChildItem -Path $m4bSourceFolder -Filter "*.m4b" -File

Write-Log "Found $($m4bFiles.Count) M4B file(s) to process"

$successCount = 0
$failureCount = 0

foreach ($m4bFile in $m4bFiles) {
    try {
        # Get the base name without extension (this will be the folder name)
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($m4bFile.Name)
        
        Write-Log "Processing: $baseName"
        
        # Create destination subfolder named after the M4B file
        $audiobookFolder = Join-Path $destinationFolder $baseName
        
        if (-not (Test-Path $audiobookFolder)) {
            New-Item -ItemType Directory -Path $audiobookFolder -Force | Out-Null
            Write-Log "  Created folder: $audiobookFolder"
        }
        
        # Copy M4B file to destination folder
        $m4bDestination = Join-Path $audiobookFolder $m4bFile.Name
        Copy-Item -Path $m4bFile.FullName -Destination $m4bDestination -Force
        Write-Log "  Copied M4B file to: $m4bDestination"
        
        # Look for matching album art (with same base name)
        $albumArtFiles = Get-ChildItem -Path $albumArtSourceFolder -Filter "$baseName.*" -File | 
                         Where-Object { $_.Extension -match '\.(jpg|jpeg|png)$' }
        
        if ($albumArtFiles.Count -gt 0) {
            # Use the first matching image file
            $albumArtFile = $albumArtFiles[0]
            
            # Destination path with "cover.jpg" name
            $coverDestination = Join-Path $audiobookFolder "cover.jpg"
            
            # Copy and rename the album art
            Copy-Item -Path $albumArtFile.FullName -Destination $coverDestination -Force
            Write-Log "  Copied and renamed album art: $($albumArtFile.Name) -> cover.jpg"
            
            $successCount++
        } else {
            Write-Log "  WARNING: No matching album art found for: $baseName"
            $successCount++  # Still count as success since M4B was copied
        }
        
    } catch {
        Write-Log "  ERROR processing $($m4bFile.Name): $($_.Exception.Message)"
        $failureCount++
    }
}

Write-Log "=== Script Completed ==="
Write-Log "Successfully processed: $successCount"
Write-Log "Failures: $failureCount"
Write-Log "Log file saved to: $logFile"