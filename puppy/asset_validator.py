import os
import json
from PIL import Image

FRAME_PACK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "frame_pack")
ANIMATIONS_DIR = os.path.join(FRAME_PACK_DIR, "animations")
METADATA_PATH = os.path.join(FRAME_PACK_DIR, "metadata.json")

EXPECTED_ANIMATIONS = [
    "idle", "blink_look", "sit", "stand_up", "walk", "fast_walk", "run", "sprint",
    "turn", "sniff", "scratch", "stretch", "yawn", "lie_down", "sleep", "wake_up",
    "play", "tail_wag", "happy", "excited", "chase_ball", "catch_ball", "carry_ball",
    "drop_ball", "wait_for_throw", "eat", "drink", "enter_house", "exit_house", "sleep_inside"
]

def validate_assets():
    if not os.path.exists(FRAME_PACK_DIR):
        raise FileNotFoundError(f"Frame pack directory missing at {FRAME_PACK_DIR}")

    if not os.path.exists(METADATA_PATH):
        raise FileNotFoundError(f"Frame pack metadata.json missing at {METADATA_PATH}")

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    print("--- ANIMATION FRAME PACK ASSET VALIDATION ---")
    print(f"Source: {meta.get('source', 'Unknown')}")
    print(f"Sheet dimensions: {meta.get('image_size', [])}")

    missing_count = 0
    total_frames = 0

    for anim in EXPECTED_ANIMATIONS:
        anim_folder = os.path.join(ANIMATIONS_DIR, anim)
        if not os.path.exists(anim_folder):
            print(f"❌ Missing animation directory: {anim_folder}")
            missing_count += 1
            continue

        files = sorted([f for f in os.listdir(anim_folder) if f.startswith("frame_") and f.endswith(".png")])
        expected_meta_frames = meta.get("animations", {}).get(anim, {}).get("frames", 0)

        if len(files) == 0:
            print(f"❌ No frame PNGs found in: {anim_folder}")
            missing_count += 1
        else:
            # Check transparency & bounds for first frame
            first_frame_path = os.path.join(anim_folder, files[0])
            with Image.open(first_frame_path) as img:
                w, h = img.size
                mode = img.mode
                if mode != "RGBA":
                    print(f"⚠️  Warning: {anim}/{files[0]} mode is {mode}, converting to RGBA")

            total_frames += len(files)
            print(f"[OK] {anim:15s}: {len(files):2d} frames (meta expected: {expected_meta_frames:2d}) - {w}x{h} px")

    if missing_count > 0:
        raise ValueError(f"Asset validation failed! {missing_count} animation folders missing or invalid.")

    print(f"ASSET VALIDATION COMPLETE! {len(EXPECTED_ANIMATIONS)} animation groups, {total_frames} total frames verified.")

if __name__ == "__main__":
    validate_assets()
