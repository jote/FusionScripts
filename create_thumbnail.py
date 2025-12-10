#!/usr/bin/env python3

"""
HOW TO USE:

This script generates a thumbnail from a video file at a specified timecode
and creates a new video file with the thumbnail embedded as attached_pic.

REQUIREMENTS:
- ffmpeg
- ffprobe
- Python 3.6+

USAGE:
    python3 create_thumbnail.py -i <input_file> -o <output_name> <timecode>

ARGUMENTS:
    -i, --input    Input video file path
    -o, --output   Output file name (without extension)
    timecode       Timecode in HH:MM:SS:FF format (Hours:Minutes:Seconds:Frames)

EXAMPLE:
    python3 create_thumbnail.py -i video.mp4 -o output "1:00:00:11"

OUTPUT:
    - thumbnail.png                  (Extracted thumbnail image)
    - output_1_00_00_11.mp4         (Video with embedded thumbnail)

NOTES:
    - The script automatically detects the video's frame rate
    - If the video has a timecode track, it calculates relative frame positions
    - Timecode format must be HH:MM:SS:FF (e.g., "01:00:00:11" for 1 hour, 0 min, 0 sec, 11 frames)
"""

import argparse
import subprocess
import sys
import os
import json

def get_timecode_start(input_file):
    """Get starting timecode from input video file"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream_tags=timecode',
        '-of', 'json',
        input_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        if 'streams' in data and len(data['streams']) > 0:
            tags = data['streams'][0].get('tags', {})
            timecode = tags.get('timecode', '00:00:00:00')
            print(f"Detected timecode start: {timecode}")
            return timecode
        return '00:00:00:00'
        
    except Exception as e:
        print(f"Warning: Could not get timecode, assuming 00:00:00:00")
        return '00:00:00:00'

def get_frame_rate(input_file):
    """Get frame rate from input video file"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=r_frame_rate',
        '-of', 'json',
        input_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        fps_str = data['streams'][0]['r_frame_rate']
        
        # Convert fraction to decimal (e.g., "30000/1001" -> 29.97)
        num, den = map(int, fps_str.split('/'))
        fps = num / den
        
        print(f"Detected frame rate: {fps_str} ({fps:.6f} fps)")
        return fps
        
    except Exception as e:
        print(f"Error: Failed to get frame rate - {e}", file=sys.stderr)
        sys.exit(1)

def parse_timecode(timecode):
    """Parse HH:MM:SS:FF format to hours, minutes, seconds, frames"""
    parts = timecode.split(':')
    
    if len(parts) != 4:
        print(f"Error: Invalid timecode format '{timecode}'. Expected HH:MM:SS:FF", file=sys.stderr)
        sys.exit(1)
    
    try:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        frames = int(parts[3])
        return hours, minutes, seconds, frames
    except ValueError:
        print(f"Error: Invalid timecode format '{timecode}'. All parts must be integers", file=sys.stderr)
        sys.exit(1)

def calculate_frame_number(hours, minutes, seconds, frames, fps):
    """Calculate absolute frame number from timecode"""
    total_seconds = hours * 3600 + minutes * 60 + seconds
    frame_number = int(total_seconds * fps) + frames
    return frame_number

def calculate_relative_frame_number(target_timecode, start_timecode, fps):
    """Calculate relative frame number from target timecode and start timecode"""
    # Parse target timecode
    target_parts = target_timecode.split(':')
    target_h, target_m, target_s, target_f = map(int, target_parts)
    target_frame = calculate_frame_number(target_h, target_m, target_s, target_f, fps)
    
    # Parse start timecode
    start_parts = start_timecode.split(':')
    start_h, start_m, start_s, start_f = map(int, start_parts)
    start_frame = calculate_frame_number(start_h, start_m, start_s, start_f, fps)
    
    # Calculate relative frame number
    relative_frame = target_frame - start_frame
    
    return relative_frame, target_frame, start_frame

def generate_thumbnail(input_file, frame_number, fps, output_file):
    """Generate thumbnail at specified frame number"""
    # Calculate seconds from frame number
    seconds = frame_number / fps
    
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-ss', str(seconds),
        '-vframes', '1',
        '-y',
        output_file
    ]
    
    print(f"\nStep 1: Generating thumbnail image...")
    print(f"Frame number: {frame_number}, Time: {seconds:.6f} seconds")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Thumbnail generated: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to generate thumbnail - {e}", file=sys.stderr)
        return False

def generate_video_with_thumbnail(input_file, thumbnail_file, output_file):
    """Generate video with embedded thumbnail"""
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-i', thumbnail_file,
        '-map', '0:v',
        '-map', '0:a',
        '-map', '-0:d',
        '-map', '1:v',
        '-c', 'copy',
        '-disposition:2', 'attached_pic',
        '-y',
        output_file
    ]
    
    print(f"\nStep 2: Generating video with embedded thumbnail...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Video generated: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to generate video - {e}", file=sys.stderr)
        return False

def display_file_info(output_file):
    """Display file information using ffprobe"""
    cmd = ['ffprobe', output_file]
    
    print(f"\nStep 3: Displaying generated file information...")
    print("=" * 50)
    
    subprocess.run(cmd)
    
    print("=" * 50)

def main():
    parser = argparse.ArgumentParser(
        description='Generate thumbnail and video with embedded thumbnail from specified timecode',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Example:
  %(prog)s -i input.mp4 -o output "1:00:00:11"
  
Output:
  - thumbnail.png
  - output_1_00_00_11.mp4
'''
    )
    
    parser.add_argument('-i', '--input', required=True, help='Input video file')
    parser.add_argument('-o', '--output', required=True, help='Output file name (without extension)')
    parser.add_argument('timecode', help='Timecode in HH:MM:SS:FF format')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.isfile(args.input):
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Get current directory
    current_dir = os.getcwd()
    
    print(f"Original timecode: {args.timecode} (HH:MM:SS:FF)")
    
    # Get frame rate
    fps = get_frame_rate(args.input)
    
    # Get timecode start
    start_timecode = get_timecode_start(args.input)
    
    # Calculate relative frame number
    relative_frame, target_frame, start_frame = calculate_relative_frame_number(
        args.timecode, start_timecode, fps
    )
    
    print(f"Target frame number: {target_frame}")
    print(f"Start frame number: {start_frame}")
    print(f"Relative frame number: {relative_frame}")
    
    if relative_frame < 0:
        print(f"Error: Target timecode {args.timecode} is before start timecode {start_timecode}", file=sys.stderr)
        sys.exit(1)
    
    # Generate file names
    formatted_time = args.timecode.replace(':', '_')
    thumbnail_file = os.path.join(current_dir, 'thumbnail.png')
    output_file = os.path.join(current_dir, f"{args.output}_{formatted_time}.mp4")
    
    print(f"\nStarting process...")
    print(f"Input file: {args.input}")
    print(f"Output file: {output_file}")
    print(f"Thumbnail file: {thumbnail_file}")
    
    # Generate thumbnail
    if not generate_thumbnail(args.input, relative_frame, fps, thumbnail_file):
        sys.exit(1)
    
    # Generate video with embedded thumbnail
    if not generate_video_with_thumbnail(args.input, thumbnail_file, output_file):
        sys.exit(1)
    
    # Display file information
    display_file_info(output_file)
    
    print("\nProcess completed!")
    print("Generated files:")
    print(f"  - {thumbnail_file}")
    print(f"  - {output_file}")

if __name__ == '__main__':
    main()
