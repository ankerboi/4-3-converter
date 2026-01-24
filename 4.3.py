#!/usr/bin/env python3
"""
4:3 to 16:9 Video Converter
Drag and drop a 4:3 video onto this script to stretch it to 16:9
Auto-downloads ffmpeg if needed
"""
import sys
import os
import subprocess
import zipfile
import urllib.request
import platform

def get_ffmpeg_path():
    """Get the path to ffmpeg executable"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_dir = os.path.join(script_dir, 'ffmpeg')
    
    if platform.system() == 'Windows':
        return os.path.join(ffmpeg_dir, 'bin', 'ffmpeg.exe')
    else:
        return os.path.join(ffmpeg_dir, 'ffmpeg')

def download_ffmpeg():
    """Download and extract ffmpeg"""
    print("\n" + "=" * 60)
    print("FFmpeg not found - downloading...")
    print("=" * 60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_dir = os.path.join(script_dir, 'ffmpeg')
    
    try:
        system = platform.system()
        
        if system == 'Windows':
            # Download FFmpeg for Windows
            url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
            zip_path = os.path.join(script_dir, 'ffmpeg.zip')
            
            print("Downloading FFmpeg (this may take a few minutes)...")
            urllib.request.urlretrieve(url, zip_path, reporthook=download_progress)
            
            print("\nExtracting FFmpeg...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(script_dir)
            
            # Find the extracted folder (it has a version number in the name)
            extracted_folders = [f for f in os.listdir(script_dir) if f.startswith('ffmpeg-') and os.path.isdir(os.path.join(script_dir, f))]
            if extracted_folders:
                extracted_path = os.path.join(script_dir, extracted_folders[0])
                # Rename to simple 'ffmpeg' folder
                if os.path.exists(ffmpeg_dir):
                    import shutil
                    shutil.rmtree(ffmpeg_dir)
                os.rename(extracted_path, ffmpeg_dir)
            
            # Clean up zip file
            os.remove(zip_path)
            
            print("✓ FFmpeg downloaded and installed successfully!\n")
            return True
            
        else:
            print("Auto-download only works on Windows.")
            print("Please install ffmpeg manually:")
            print("  Mac: brew install ffmpeg")
            print("  Linux: sudo apt install ffmpeg")
            return False
            
    except Exception as e:
        print(f"\n✗ Error downloading FFmpeg: {e}")
        print("\nPlease install ffmpeg manually:")
        print("  Download from: https://ffmpeg.org/download.html")
        return False

def download_progress(block_num, block_size, total_size):
    """Show download progress"""
    downloaded = block_num * block_size
    percent = min(downloaded * 100 / total_size, 100)
    sys.stdout.write(f'\rProgress: {percent:.1f}%')
    sys.stdout.flush()

def check_ffmpeg():
    """Check if ffmpeg is available, download if needed"""
    # First check if ffmpeg is in system PATH
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      check=True)
        return 'ffmpeg'  # Use system ffmpeg
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Check if we have a local ffmpeg
    local_ffmpeg = get_ffmpeg_path()
    if os.path.exists(local_ffmpeg):
        return local_ffmpeg
    
    # Need to download ffmpeg
    if download_ffmpeg():
        local_ffmpeg = get_ffmpeg_path()
        if os.path.exists(local_ffmpeg):
            return local_ffmpeg
    
    return None

def convert_video(input_path):
    """Convert a 4:3 video to 16:9 by stretching it"""
    
    # Check if file exists
    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}")
        return False
    
    # Check for ffmpeg and download if needed
    ffmpeg_exe = check_ffmpeg()
    if not ffmpeg_exe:
        print("\n" + "!" * 60)
        print("ERROR: Could not get ffmpeg!")
        print("!" * 60)
        return False
    
    # Create output filename
    filename, ext = os.path.splitext(input_path)
    output_path = f"{filename}_16-9{ext}"
    
    print(f"Converting: {os.path.basename(input_path)}")
    print(f"Output will be: {os.path.basename(output_path)}")
    print("\nProcessing... (this may take a while)")
    
    # FFmpeg command to stretch video from 4:3 to 16:9
    # This forces the video to exactly 1920x1080, stretching it to fill the frame
    command = [
        ffmpeg_exe,
        '-i', input_path,
        '-vf', 'scale=1920:1080,setsar=1',  # Force exact size, no aspect ratio preservation
        '-c:a', 'copy',  # Copy audio without re-encoding
        '-y',  # Overwrite output file if it exists
        output_path
    ]
    
    try:
        # Run ffmpeg
        result = subprocess.run(command, 
                               stderr=subprocess.PIPE, 
                               text=True)
        
        if result.returncode == 0:
            print(f"\n✓ Success! Converted video saved as:")
            print(f"  {output_path}")
            return True
        else:
            print("\n✗ Conversion failed!")
            print("Error details:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"\n✗ Error during conversion: {e}")
        return False

def main():
    print("=" * 60)
    print("4:3 to 16:9 Video Converter")
    print("=" * 60)
    print()
    
    # Check if a file was dragged onto the script
    if len(sys.argv) < 2:
        print("Usage: Drag and drop a video file onto this script")
        print("Or run: python script.py <video_file>")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Get the input file path and clean it up
    input_path = sys.argv[1]
    
    # Remove quotes if present (Windows sometimes adds them)
    input_path = input_path.strip('"').strip("'")
    
    print(f"Received file: {input_path}")
    print()
    
    # Convert the video
    success = convert_video(input_path)
    
    # Wait for user input before closing
    print()
    input("Press Enter to exit...")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()