"""
Fast Instagram Stealth Video Editor - Enhanced Metadata Removal
==============================================================

Enhanced version with aggressive metadata removal including compressor/vendor info.
"""

import os
import random
import subprocess
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_processing.log'),
        logging.StreamHandler()
    ]
)

# Windows paths
# input_folder = r"C:\Users\Giuseppe Rizzo\Desktop\gr consulting\ecom\ORGANIC DROPSHIPPING\VIDEOS METADATA TEST\BEFORE"
# output_folder = r"C:\Users\Giuseppe Rizzo\Desktop\gr consulting\ecom\ORGANIC DROPSHIPPING\VIDEOS METADATA TEST\AFTER"
input_folder = r"C:\SampleProject\iphone_fiverr\input"
output_folder = r"C:\SampleProject\iphone_fiverr\output"
os.makedirs(output_folder, exist_ok=True)

# FAST parameter ranges - effective but quick to process
params = {
    "framerate": (29, 31),
    "video_bitrate": (2800, 3500),
    "audio_bitrate": (125, 135),
    "brightness": (-0.02, 0.02),
    "contrast": (0.96, 1.06),
    "saturation": (0.94, 1.08),
    "gamma": (0.95, 1.08),
    "zoom": (1.0, 1.02),
    "pixel_shift_x": (-2, 2),
    "pixel_shift_y": (-2, 2),
    "speed": (0.985, 1.015),
    "cut_start": (0.3, 1.0),
    "cut_end": (0.3, 1.2),
    "volume": (0.90, 1.10),
    "hue_shift": (-12, 12),
}

# FAST switches - All stealth features enabled
switches = {
    "eq": True,
    "zoom": True,
    "pixel_shift": True,
    "speed": False,
    "volume": True,
    "audio_pitch": True,
    "hue_shift": True,
    "simple_noise": True,
    "mirror_chance": False,
    "crop_variation": False,
    "random_resize": True,
    "metadata_strip": True,
    "aggressive_metadata_removal": True,  # New option
    "force_reencoding": True,  # Force re-encoding to remove embedded metadata
    "force_vendor_patch": True,  # After mux, patch MOV vendor 'FFMP' -> 'appl'
}

# Output mode: 'h264' (libx264), 'hevc' (libx265), or 'prores_apple' (ProRes with Apple vendor)
video_codec = 'h264'  # set to 'hevc' for iPhone-like HEVC, or 'prores_apple' for Apple vendor
# ffprobe -v quiet -show_format -show_streams "C:\SampleProject\iphone_fiverr\output\ig_pikuu_42854.mov"
# ProRes settings used when video_codec == 'prores_apple'
# Choose encoder: 'prores_aw' or 'prores_ks'. Some FFmpeg builds only honor vendor with one of them.
prores_encoder = 'prores_ks'   # use prores_ks by default; some builds honor vendor here better
prores_profile = '3'           # 0=proxy,1=lt,2=standard,3=hq,4=4444,5=4444xq (for prores_ks). '3' ~ HQ
prores_fourcc = 'apch'         # apcn=422 standard, apch=422 HQ, ap4h=4444, etc.
prores_qscale = '9'            # quality scale for prores_ks; prores_aw uses -qscale as well

def rv(param):
    return round(random.uniform(params[param][0], params[param][1]), 4)

def ri(param):
    return random.randint(params[param][0], params[param][1])

def get_video_duration(path):
    """Get video duration quickly"""
    try:
        cmd = f'ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return float(result.stdout.strip())
        return 30.0
    except:
        return 30.0

def get_advanced_metadata_flags():
    """Generate advanced metadata removal flags"""
    flags = [
        "-map_metadata", "-1",  # Remove all metadata
        "-map_chapters", "-1",  # Remove chapters
        "-fflags", "+bitexact",  # Bitexact mode
        "-flags:v", "+bitexact",  # Video bitexact
        "-flags:a", "+bitexact",  # Audio bitexact
    ]
    
    # Additional metadata clearing
    metadata_fields = [
        "title", "artist", "album", "date", "track", "genre", "comment",
        "encoder", "creation_time", "major_brand", "minor_version",
        "compatible_brands", "software", "make", "model", "location"
    ]
    
    for field in metadata_fields:
        flags.extend(["-metadata", f"{field}="])
    
    return flags

def patch_mov_vendor(file_path, old=b"FFMP", new=b"appl"):
    """Best-effort patch: replace first occurrence of old vendor with new in MOV file.
    This targets the MOV sample entry vendor field exported by ffprobe as tag:vendor_id.
    """
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        idx = data.find(old)
        if idx == -1:
            return False
        # Replace only the first occurrence to avoid unintended edits
        patched = data[:idx] + new + data[idx+len(old):]
        # Write back atomically
        tmp_path = file_path + ".tmp"
        with open(tmp_path, 'wb') as f:
            f.write(patched)
        os.replace(tmp_path, file_path)
        return True
    except Exception:
        return False

def get_codec_flags_for_stealth():
    """Get codec-specific flags to minimize metadata embedding"""
    return [
        "-c:v", "libx264",
        "-profile:v", "baseline",  # Use baseline profile (less metadata)
        "-level:v", "3.1",
        "-pix_fmt", "yuv420p",
        
        # x264 specific flags to remove branding/metadata
        "-x264-params", "nal-hrd=none:filler=0:aud=0:annexb=0",
        
        # Additional flags to minimize metadata
        "-write_tmcd", "0",  # Don't write timecode
        "-movflags", "+faststart+empty_moov",
        
        # Force specific settings that don't embed vendor info
        "-preset", "ultrafast",
        "-tune", "zerolatency",
    ]

def process_video(input_path, output_path):
    """Enhanced video processing with aggressive metadata removal"""
    filters_v = []
    filters_a = []

    print(f"⚡ Processing: {os.path.basename(input_path)}")

    # Get video duration
    video_duration = get_video_duration(input_path)

    # Color changes
    if switches["eq"]:
        brightness = rv('brightness')
        contrast = rv('contrast')
        saturation = rv('saturation')
        gamma = rv('gamma')
        filters_v.append(f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}:gamma={gamma}")
        print(f"   🎨 Color: b={brightness:.3f} c={contrast:.3f} s={saturation:.3f} g={gamma:.3f}")

    # Hue shift
    if switches["hue_shift"] and random.random() < 0.8:
        hue_degrees = ri("hue_shift")
        if abs(hue_degrees) > 3:
            filters_v.append(f"hue=h={hue_degrees}")
            print(f"   🌈 Hue shift: {hue_degrees}°")

    # Zoom
    if switches["zoom"] and random.random() < 0.6:
        zoom_factor = rv("zoom")
        if zoom_factor > 1.005:
            filters_v.append(f"scale=iw*{zoom_factor}:ih*{zoom_factor}:force_original_aspect_ratio=decrease:force_divisible_by=2,crop=iw:ih")
            print(f"   🔍 Zoom: {zoom_factor:.3f}x")

    # Pixel shift
    if switches["pixel_shift"] and random.random() < 0.7:
        shift_x, shift_y = ri("pixel_shift_x"), ri("pixel_shift_y")
        if abs(shift_x) > 0 or abs(shift_y) > 0:
            filters_v.append(f"pad=iw+4:ih+4:2:2,crop=iw-4:ih-4:{shift_x+2}:{shift_y+2}")
            print(f"   📐 Pixel shift: x={shift_x}, y={shift_y}")

    # Simple noise
    if switches["simple_noise"] and random.random() < 0.5:
        noise_strength = random.randint(2, 5)
        filters_v.append(f"noise=alls={noise_strength}:allf=t")
        print(f"   📺 Noise: strength={noise_strength}")

    # Force re-encoding for metadata removal (always apply slight filter)
    if switches["force_reencoding"] and not filters_v:
        # Apply minimal filter to force re-encoding
        filters_v.append("format=yuv420p")
        print("   🔄 Forced re-encoding for metadata removal")

    # Audio pitch
    if switches["audio_pitch"] and random.random() < 0.8:
        pitch_factor = round(random.uniform(0.998, 1.004), 4)
        if abs(pitch_factor - 1.0) > 0.001:
            filters_a.append(f"asetrate=44100*{pitch_factor},aresample=44100")
            print(f"   🎵 Audio pitch: {pitch_factor:.4f}x")

    # Volume changes
    if switches["volume"]:
        vol_change = rv("volume")
        if abs(vol_change - 1.0) > 0.02:
            filters_a.append(f"volume={vol_change}")
            print(f"   🔊 Volume: {vol_change:.3f}x")

    # Fixed 9:16 resize
    if switches["random_resize"]:
        w = random.choice([1080, 1200, 1350, 1440, 1620, 1800])
        h = int(w * 16 / 9)
        if w % 2 != 0: w += 1
        if h % 2 != 0: h += 1
        filters_v.append(f"scale={w}:{h}:flags=fast_bilinear")
        print(f"   📱 Resize: {w}x{h} (9:16)")

    # Combine filters
    filter_v = ",".join(filters_v) if filters_v else "format=yuv420p"  # Always apply at least format filter
    filter_a = ",".join(filters_a) if filters_a else "aformat=sample_fmts=fltp"  # Always apply audio format filter

    # Trimming
    ss = rv("cut_start")
    cut_end = rv("cut_end")
    duration = max(video_duration - ss - cut_end, 3.0)
    print(f"   ✂️ Trim: start={ss:.1f}s, end={cut_end:.1f}s, duration={duration:.1f}s")

    # Generate output path
    timestamp = int(time.time() * 1000) % 100000
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    unique_output = os.path.join(output_folder, f"ig_{base_name}_{timestamp}.mov")

    # Build FFmpeg command with enhanced metadata removal
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-ss", str(ss),
        "-i", input_path,
        "-t", str(duration),
        "-vf", filter_v,
        "-af", filter_a,
    ]

    # Video encoding flags based on codec
    if video_codec == 'prores_apple':
        # Apple ProRes with Apple vendor code (apl0). Larger files, but vendor can be set.
        if prores_encoder == 'prores_aw':
            command.extend([
                "-c:v", "prores_aw",
                "-pix_fmt", "yuv422p10le",
                "-r", str(ri("framerate")),
                "-vendor", "appl",            # Apple vendor code
                "-tag:v", prores_fourcc,       # FourCC e.g. apcn/apch
                "-qscale:v", prores_qscale,
            ])
        else:
            command.extend([
                "-c:v", "prores_ks",
                "-profile:v", prores_profile,  # ProRes profile index
                "-pix_fmt", "yuv422p10le",
                "-r", str(ri("framerate")),
                "-vendor", "appl",            # Apple vendor code
                "-tag:v", prores_fourcc,       # FourCC e.g. apcn/apch
                "-qscale:v", prores_qscale,    # Quality scale (lower is higher quality)
            ])
        # As a fallback for tools reading tags, also set stream metadata
        command.extend([
            "-metadata:s:v:0", "vendor_id=appl",
        ])
    elif video_codec == 'hevc':
        # iPhone-like HEVC
        command.extend([
            "-c:v", "libx265",
            "-pix_fmt", "yuv420p",
            "-b:v", f"{ri('video_bitrate')}k",
            "-r", str(ri("framerate")),
            "-tag:v", "hvc1",
            "-preset", "ultrafast",
            "-x265-params", "no-info=1",
        ])
    else:
        # Default H.264
        command.extend([
            "-c:v", "libx264",
            "-profile:v", "baseline",
            "-level:v", "3.1",
            "-pix_fmt", "yuv420p",
            "-b:v", f"{ri('video_bitrate')}k",
            "-r", str(ri("framerate")),
            "-tag:v", "avc1",
            "-preset", "ultrafast",
            "-crf", "24",
            "-tune", "zerolatency",
            "-x264-params", "info=0:nal-hrd=none:filler=0:aud=0:annexb=0",
        ])

    # Audio encoding
    if video_codec == 'prores_apple':
        # AAC is fine for size; PCM also acceptable but much larger. Keep AAC.
        command.extend([
            "-c:a", "aac",
            "-b:a", f"{ri('audio_bitrate')}k",
            "-profile:a", "aac_low",
        ])
    else:
        command.extend([
            "-c:a", "aac",
            "-b:a", f"{ri('audio_bitrate')}k",
            "-profile:a", "aac_low",
        ])

    # Container and processing flags
    command.extend([
        "-movflags", "+faststart+empty_moov",
        "-write_tmcd", "0",
        "-max_muxing_queue_size", "1024",
        "-fflags", "+genpts+bitexact",
        "-flags:v", "+bitexact",
        "-flags:a", "+bitexact",
        "-avoid_negative_ts", "make_zero",
        "-threads", "0",
        # Set MOV major brand to QuickTime explicitly
        "-brand", "qt",
    ])
    
    # Add aggressive metadata removal flags
    if switches["aggressive_metadata_removal"]:
        command.extend(get_advanced_metadata_flags())
        print("   🛡️ Aggressive metadata removal enabled")
    else:
        command.extend(["-map_metadata", "-1"])
    
    # Explicitly clear encoder tags on container and streams
    command.extend([
        "-metadata", "encoder=",
        "-metadata:s:v:0", "encoder=",
        "-metadata:s:a:0", "encoder=",
    ])

    # Set iPhone-like stream handler names (these are just labels)
    command.extend([
        "-metadata:s:v:0", "handler_name=Core Media Video",
        "-metadata:s:a:0", "handler_name=Core Media Audio",
    ])
    
    # Add output file and overwrite flag
    command.extend(["-y", unique_output])

    # Execute command
    start_time = time.time()
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=180)
        process_time = time.time() - start_time
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr[-200:]}")
            logging.error(f"FFmpeg error for {os.path.basename(input_path)}: {result.stderr}")
            return False, process_time
        if os.path.exists(unique_output):
            output_size = os.path.getsize(unique_output)
            input_size = os.path.getsize(input_path)
            size_ratio = output_size / input_size
            print(f"✅ Success in {process_time:.1f}s: {os.path.basename(unique_output)}")
            print(f"   📊 Size: {input_size//1024}KB → {output_size//1024}KB ({size_ratio:.2f}x)")
            
            # Optional: Patch vendor and verify metadata removal
            if switches.get("force_vendor_patch", False):
                if patch_mov_vendor(unique_output):
                    print("   🔧 Patched MOV vendor_id: FFMP → appl")
                else:
                    print("   🔧 Vendor patch skipped (marker not found)")
            if switches["aggressive_metadata_removal"]:
                details = verify_metadata_removal(unique_output)
                # Print a compact one-liner of key details if available
                if details:
                    brand = details.get("major_brand")
                    vtag = details.get("vendor_id_tag")
                    vctag = details.get("v_codec_tag_string")
                    vhdl = details.get("v_handler")
                    ahdl = details.get("a_handler")
                    summary_parts = []
                    if brand:
                        summary_parts.append(f"brand={brand}")
                    if vctag:
                        summary_parts.append(f"codec_tag={vctag}")
                    if vtag:
                        summary_parts.append(f"tag:vendor_id={vtag}")
                    if vhdl:
                        summary_parts.append(f"v_handler={vhdl}")
                    if ahdl:
                        summary_parts.append(f"a_handler={ahdl}")
                    if summary_parts:
                        print("   🧾 Details: " + ", ".join(summary_parts))
            
            return True, process_time
        else:
            print("❌ No output file created")
            return False, process_time
    except subprocess.TimeoutExpired:
        print("❌ Timeout (3min)")
        return False, 180
    except Exception as e:
        print(f"❌ Exception: {e}")
        logging.error(f"Exception processing {os.path.basename(input_path)}: {str(e)}")
        return False, 0

def verify_metadata_removal(file_path):
    """Verify that metadata has been removed. Only flag non-empty values.

    Returns a dict with selected details to report upstream.
    """
    try:
        cmd = f'ffprobe -v quiet -show_format -show_streams "{file_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            output = result.stdout
            suspicious_keys = {"encoder", "vendor_id", "compressor", "software", "creation_time"}
            found_nonempty = []
            vendor_id_tag = None
            major_brand = None
            minor_version = None
            compatible_brands = None
            v_handler = None
            a_handler = None
            v_codec_tag_string = None
            for line in output.splitlines():
                # print(line)
                if "=" in line:
                    key, val = line.split("=", 1)
                    # print(key, val)
                    key = key.strip().lower()
                    # print(key)
                    val = val.strip()
                    if key in suspicious_keys and val:
                        found_nonempty.append(f"{key}={val}")
                    # Capture ffprobe-exported tag name for mov vendor id
                    if key == "tag:vendor_id":
                        vendor_id_tag = val
                    elif key == "tag:major_brand":
                        major_brand = val
                    elif key == "tag:minor_version":
                        minor_version = val
                    elif key == "tag:compatible_brands":
                        compatible_brands = val
                    elif key == "tag:handler_name":
                        # first occurrence is usually video; store both when seen
                        if v_handler is None:
                            v_handler = val
                        elif a_handler is None:
                            a_handler = val
                    elif key == "codec_tag_string" and v_codec_tag_string is None:
                        # first stream printed by ffprobe is usually video
                        v_codec_tag_string = val
            if found_nonempty:
                print(f"   ⚠️ Some metadata may remain: {found_nonempty}")
            else:
                print(f"   ✅ Metadata removal verified")
            # Show MOV vendor tag when present (informational)
            if vendor_id_tag is not None:
                print(f"   ℹ️ MOV tag:vendor_id = {vendor_id_tag}")
            return {
                "vendor_id_tag": vendor_id_tag,
                "major_brand": major_brand,
                "minor_version": minor_version,
                "compatible_brands": compatible_brands,
                "v_handler": v_handler,
                "a_handler": a_handler,
                "v_codec_tag_string": v_codec_tag_string,
            }
    except:
        pass  # Silent fail for verification
    return None

def main():
    """Main processing function"""
    success_count = 0
    total_count = 0
    total_time = 0
    failed_files = []

    print("🚀 Starting ENHANCED Instagram Stealth Processing...")
    print("=" * 60)

    if not os.path.exists(input_folder):
        print(f"❌ Input folder doesn't exist: {input_folder}")
        return

    video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".flv"}
    video_files = [f for f in os.listdir(input_folder) if Path(f).suffix.lower() in video_extensions]

    if not video_files:
        print(f"❌ No video files found in {input_folder}")
        return

    print(f"📁 Found {len(video_files)} video files")
    print(f"🎛️ Active modifications:")
    for key, value in switches.items():
        if value:
            print(f"   ✅ {key}")
    print()

    start_total = time.time()
    for i, filename in enumerate(video_files, 1):
        total_count += 1
        input_path = os.path.join(input_folder, filename)
        print(f"\n[{i}/{len(video_files)}] {filename}")
        print("-" * 40)
        success, process_time = process_video(input_path, "")
        total_time += process_time
        if success:
            success_count += 1
        else:
            failed_files.append(filename)
        print("-" * 40)

    total_elapsed = time.time() - start_total
    print("=" * 60)
    print(f"🎉 ENHANCED STEALTH PROCESSING COMPLETE!")
    print(f"✅ Success: {success_count}/{total_count} videos")
    print(f"⏱️ Total time: {total_elapsed:.1f}s")
    print(f"⚡ Average per video: {total_time/total_count:.1f}s" if total_count > 0 else "")
    print(f"📁 Output: {output_folder}")

    if failed_files:
        print(f"\n❌ Failed Files ({len(failed_files)}):")
        for filename in failed_files:
            print(f"   • {filename}")

if __name__ == "__main__":
    main()
