import os
import json
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtCore import QObject, QSize

FRAME_PACK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "frame_pack")
ANIMATIONS_DIR = os.path.join(FRAME_PACK_DIR, "animations")
METADATA_PATH = os.path.join(FRAME_PACK_DIR, "metadata.json")

# State string mappings to exact extracted animation directories
ANIMATION_STATE_MAPPING = {
    "IDLE": "idle",
    "BLINK_LOOK": "blink_look",
    "SIT": "sit",
    "STAND_UP": "stand_up",
    "WALK": "walk",
    "WALK_RIGHT": "walk",
    "WALK_LEFT": "walk",
    "FAST_WALK": "fast_walk",
    "RUN": "run",
    "RUN_RIGHT": "run",
    "RUN_LEFT": "run",
    "SPRINT": "sprint",
    "TURN": "turn",
    "SNIFF": "sniff",
    "SCRATCH": "scratch",
    "STRETCH": "stretch",
    "YAWN": "yawn",
    "LIE_DOWN": "lie_down",
    "SLEEP": "sleep",
    "WAKE_UP": "wake_up",
    "WAKE": "wake_up",
    "PLAY": "play",
    "TAIL_WAG": "tail_wag",
    "HAPPY": "happy",
    "PETTED": "happy",
    "EXCITED": "excited",
    "CHASE_BALL": "chase_ball",
    "BALL_CHASE": "chase_ball",
    "CATCH_BALL": "catch_ball",
    "CARRY_BALL": "carry_ball",
    "DROP_BALL": "drop_ball",
    "WAIT_FOR_THROW": "wait_for_throw",
    "EAT": "eat",
    "DRINK": "drink",
    "ENTER_HOUSE": "enter_house",
    "SLEEP_WALK": "enter_house",
    "EXIT_HOUSE": "exit_house",
    "SLEEP_INSIDE": "sleep_inside"
}

# FPS Configuration per state
ANIMATION_FPS = {
    "IDLE": 8,
    "BLINK_LOOK": 10,
    "SIT": 8,
    "STAND_UP": 10,
    "WALK": 12,
    "WALK_RIGHT": 12,
    "WALK_LEFT": 12,
    "FAST_WALK": 14,
    "RUN": 16,
    "RUN_RIGHT": 16,
    "RUN_LEFT": 16,
    "SPRINT": 20,
    "TURN": 10,
    "SNIFF": 8,
    "SCRATCH": 12,
    "STRETCH": 8,
    "YAWN": 8,
    "LIE_DOWN": 8,
    "SLEEP": 5,
    "WAKE_UP": 10,
    "WAKE": 10,
    "PLAY": 12,
    "TAIL_WAG": 12,
    "HAPPY": 10,
    "PETTED": 10,
    "EXCITED": 14,
    "CHASE_BALL": 16,
    "BALL_CHASE": 16,
    "CATCH_BALL": 12,
    "CARRY_BALL": 12,
    "DROP_BALL": 10,
    "WAIT_FOR_THROW": 8,
    "EAT": 8,
    "DRINK": 8,
    "ENTER_HOUSE": 10,
    "SLEEP_WALK": 10,
    "EXIT_HOUSE": 10,
    "SLEEP_INSIDE": 5
}

class FramePackRegistry:
    def __init__(self, target_height=72):
        self.target_height = target_height
        self.cached_pixmaps = {}
        self.cached_anchors = {}
        self.load_and_cache_all()

    def load_and_cache_all(self):
        print("Caching all extracted animation pack frames with anchor normalization...")
        for state_key, anim_folder in ANIMATION_STATE_MAPPING.items():
            folder_path = os.path.join(ANIMATIONS_DIR, anim_folder)
            if not os.path.exists(folder_path):
                continue

            files = sorted([f for f in os.listdir(folder_path) if f.startswith("frame_") and f.endswith(".png")])
            if not files:
                continue

            flip = ("LEFT" in state_key or state_key == "SLEEP_WALK" or state_key == "ENTER_HOUSE")
            key = (state_key, flip)

            pixmaps = []
            for f in files:
                file_path = os.path.join(folder_path, f)
                pix = QPixmap(file_path)

                # High quality smooth scaling preserving ratio
                if pix.height() != self.target_height:
                    pix = pix.scaledToHeight(self.target_height)

                if flip:
                    pix = pix.transformed(QTransform().scale(-1, 1))

                pixmaps.append(pix)

            self.cached_pixmaps[key] = pixmaps

    def get_frames(self, state_name, facing_right=True):
        state_key = str(state_name).upper().replace("PUPPYSTATE.", "")
        flip = not facing_right if ("LEFT" not in state_key and "RIGHT" not in state_key) else ("LEFT" in state_key)
        
        # Override for specific directional states
        if state_key in ("SLEEP_WALK", "ENTER_HOUSE"):
            flip = True
        elif state_key in ("EXIT_HOUSE", "WAKE"):
            flip = False

        key = (state_key, flip)
        if key in self.cached_pixmaps:
            return self.cached_pixmaps[key]

        # Fallback to non-flipped if key not found
        key_noflip = (state_key, False)
        return self.cached_pixmaps.get(key_noflip, [QPixmap(72, 72)])

    def get_fps(self, state_name):
        state_key = str(state_name).upper().replace("PUPPYSTATE.", "")
        return ANIMATION_FPS.get(state_key, 10)
