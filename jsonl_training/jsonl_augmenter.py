"""
FIXED converter with better error handling
Use this AFTER running the diagnostic script
"""

import json
import base64
import cv2
from pathlib import Path
import time

def convert_bbox(x1, y1, x2, y2):
    """Convert x1,y1,x2,y2 to x,y,width,height"""
    return [int(x1), int(y1), int(x2-x1), int(y2-y1)]

def extract_and_encode_frame_robust(video_path, frame_num, max_size=1024, retry=True):
    """
    Extract frame with robust error handling
    """
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        print(f"    ❌ Cannot open video: {video_path}")
        return None
    
    # Method 1: Direct frame seek
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = cap.read()
    
    if not ret and retry:
        # Method 2: Try reading sequentially (slower but more reliable)
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        for i in range(frame_num + 1):
            ret, frame = cap.read()
            if not ret:
                break
    
    cap.release()
    
    if not ret or frame is None:
        return None
    
    # Resize if needed
    height, width = frame.shape[:2]
    if max(height, width) > max_size:
        scale = max_size / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        frame = cv2.resize(frame, (new_width, new_height))
    
    # Encode to JPEG
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
    success, buffer = cv2.imencode('.jpg', frame, encode_param)
    
    if not success:
        return None
    
    img_b64 = base64.b64encode(buffer).decode('utf-8')
    return img_b64

def create_jsonl_entry(image_b64, threat_detected, threat_type, confidence, position, description):
    """Create a single JSONL entry"""
    prompt = """Analyze this image for emergency threats. Provide a JSON response with this structure:
{
  "threat_detected": true or false,
  "threat_type": "fire" or "attacker" or "none",
  "confidence": 0.0 to 1.0,
  "position": [x, y, width, height],
  "description": "brief description"
}

Threat types:
- "fire": Look for flames, smoke, orange/red glow, heat distortion
- "attacker": Look for weapons, aggressive postures, violent actions
- "none": No threats detected

Estimate bounding box [x, y, width, height] in pixels if threat found.
Only respond with the JSON, no additional text."""
    
    response_obj = {
        "threat_detected": threat_detected,
        "threat_type": threat_type,
        "confidence": confidence,
        "position": position,
        "description": description
    }
    
    entry = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            },
            {
                "role": "assistant",
                "content": json.dumps(response_obj)
            }
        ]
    }
    
    return entry

def convert_video_to_jsonl(dataset_json_path, video_path, video_name, output_file, 
                           sample_negatives=True, max_samples=None):
    """
    ROBUST converter with better error handling
    
    Args:
        dataset_json_path: Path to dataset.json
        video_path: Path to video file
        video_name: Which dataset to use ("bench11" or "bench12")
        output_file: Output .jsonl file
        sample_negatives: Only keep 20% of negative examples
        max_samples: Maximum number of samples (None = all)
    """
    print("="*70)
    print("STARTING CONVERSION")
    print("="*70)
    
    # Verify video exists and is readable
    video_path = Path(video_path)
    if not video_path.exists():
        print(f"❌ ERROR: Video file not found: {video_path}")
        print(f"   Current directory: {Path.cwd()}")
        return
    
    # Quick video check
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"❌ ERROR: Cannot open video: {video_path}")
        print(f"   Try converting with: ffmpeg -i {video_path.name} -c:v libx264 fixed_{video_path.name}")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    
    print(f"✓ Video: {video_path.name}")
    print(f"  Frames: {total_frames}, FPS: {fps:.2f}")
    
    # Load dataset
    with open(dataset_json_path, 'r') as f:
        dataset = json.load(f)
    
    if video_name not in dataset:
        print(f"❌ ERROR: '{video_name}' not found in dataset")
        print(f"   Available: {list(dataset.keys())}")
        return
    
    frames_data = dataset[video_name]
    print(f"✓ Dataset: {video_name}")
    print(f"  Annotated frames: {len(frames_data)}")
    
    # Filter frames to process
    frames_to_process = []
    for frame_data in frames_data:
        frame_num = frame_data['frame_num']
        objects = frame_data['objects']
        
        # Skip if frame number is beyond video length
        if frame_num >= total_frames:
            continue
        
        # Sample negatives
        if sample_negatives and len(objects) == 0:
            import random
            if random.random() > 0.2:
                continue
        
        frames_to_process.append(frame_data)
    
    if max_samples:
        frames_to_process = frames_to_process[:max_samples]
    
    print(f"  Processing: {len(frames_to_process)} frames")
    print("="*70)
    
    # Process frames
    jsonl_entries = []
    failed_count = 0
    
    for idx, frame_data in enumerate(frames_to_process, 1):
        frame_num = frame_data['frame_num']
        objects = frame_data['objects']
        
        if idx % 5 == 0 or idx == 1:
            print(f"Processing frame {idx}/{len(frames_to_process)} (frame #{frame_num})...")
        
        # Extract frame
        image_b64 = extract_and_encode_frame_robust(video_path, frame_num)
        
        if image_b64 is None:
            failed_count += 1
            if failed_count <= 3:  # Only show first few errors
                print(f"  ⚠️  Failed to extract frame {frame_num}")
            continue
        
        # Create JSONL entry
        if len(objects) == 0:
            entry = create_jsonl_entry(
                image_b64=image_b64,
                threat_detected=False,
                threat_type="none",
                confidence=0.0,
                position=[],
                description="No threat detected"
            )
        else:
            # Take largest object
            main_obj = max(objects, key=lambda x: (x['x2']-x['x1'])*(x['y2']-x['y1']))
            threat_class = main_obj['class']
            bbox = convert_bbox(main_obj['x1'], main_obj['y1'], 
                              main_obj['x2'], main_obj['y2'])
            
            if threat_class == 'fire':
                entry = create_jsonl_entry(
                    image_b64=image_b64,
                    threat_detected=True,
                    threat_type="fire",
                    confidence=0.95,
                    position=bbox,
                    description="Fire detected with visible flames"
                )
            elif threat_class == 'smoke':
                entry = create_jsonl_entry(
                    image_b64=image_b64,
                    threat_detected=True,
                    threat_type="fire",
                    confidence=0.85,
                    position=bbox,
                    description="Smoke detected indicating potential fire"
                )
        
        jsonl_entries.append(entry)
    
    # Write to file
    if len(jsonl_entries) == 0:
        print("\n❌ ERROR: No frames were successfully processed!")
        print("   Possible issues:")
        print("   1. Frame numbers in dataset don't match video")
        print("   2. Video codec not supported")
        print("   3. Video file is corrupted")
        return
    
    with open(output_file, 'w') as f:
        for entry in jsonl_entries:
            f.write(json.dumps(entry) + '\n')
    
    # Summary
    print("\n" + "="*70)
    print("✅ CONVERSION COMPLETE!")
    print("="*70)
    print(f"Output file: {output_file}")
    print(f"Total examples: {len(jsonl_entries)}")
    print(f"Failed frames: {failed_count}")
    
    positives = sum(1 for e in jsonl_entries 
                   if json.loads(e['messages'][1]['content'])['threat_detected'])
    print(f"\nBreakdown:")
    print(f"  🔥 Threats detected: {positives}")
    print(f"  ✓ No threats: {len(jsonl_entries) - positives}")
    print("="*70)


# USAGE
if __name__ == "__main__":
    convert_video_to_jsonl(
        dataset_json_path="dataset.json",
        video_path="bench11.mp4",        # ← YOUR VIDEO FILE
        video_name="bench11",            # ← WHICH DATASET ("bench11" or "bench12")
        output_file="fire_training.jsonl",
        sample_negatives=True,
        max_samples=None  # Set to 50 for quick test, None for all
    )