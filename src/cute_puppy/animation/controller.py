import os
from PySide6.QtGui import QPixmap, QTransform
from cute_puppy.pet.state import PuppyState
from cute_puppy.animation.sprite_generator import generate_all_assets
from cute_puppy.platform.common import get_base_dir

ASSETS_DIR = os.path.join(get_base_dir(), "assets", "puppy")

class AnimationController:
    """
    AnimationCache: High-performance frame cache manager.
    Pre-processes and caches scaled pixmaps for both right and left facing directions once.
    Prevents reading, decoding, or scaling PNG assets on every render frame.
    """
    def __init__(self, settings_manager):
        self.settings = settings_manager
        self.frames = {}
        self.current_frame_index = 0
        self.load_all_sprites()

    def load_all_sprites(self):
        generate_all_assets()

        coat = self.settings.get("coat_style", "Brown & Cream")
        coat_slug = coat.lower().replace(" & ", "_").replace(" ", "_")
        coat_dir = os.path.join(ASSETS_DIR, coat_slug)
        if not os.path.exists(coat_dir):
            coat_dir = os.path.join(ASSETS_DIR, "brown_cream")

        scale = self.settings.size_scale
        target_w = max(36, int(72 * scale))
        target_h = max(36, int(72 * scale))

        mapping = {
            PuppyState.IDLE: ("idle", False),
            PuppyState.SIT: ("sit", False),
            PuppyState.SNIFF: ("sniff", False),
            PuppyState.HAPPY: ("happy", False),
            PuppyState.PETTED: ("petted", False),
            PuppyState.SLEEP: ("sleep", False),
            PuppyState.PLAY: ("play", False),
            PuppyState.STRETCH: ("stretch", False),
            PuppyState.YAWN: ("yawn", False),
            PuppyState.EAT: ("eat", False),
            PuppyState.DRINK: ("drink", False),
            PuppyState.SAD: ("sad", False),
            PuppyState.WALK: ("walk_right", False),
            PuppyState.WALK_RIGHT: ("walk_right", False),
            PuppyState.WALK_LEFT: ("walk_right", False),
            PuppyState.FAST_WALK: ("run_right", False),
            PuppyState.RUN: ("run_right", False),
            PuppyState.RUN_RIGHT: ("run_right", False),
            PuppyState.RUN_LEFT: ("run_right", False),
            PuppyState.SPRINT: ("run_right", False),
            PuppyState.TURN: ("walk_right", False),
            PuppyState.SLEEP_WALK: ("walk_right", True),
            PuppyState.ENTER_HOUSE: ("walk_right", True),
            PuppyState.EXIT_HOUSE: ("walk_right", False),
            PuppyState.WAKE: ("idle", False),
            PuppyState.EXCITED: ("happy", False),
            PuppyState.BALL_CHASE: ("run_right", False),
            PuppyState.CATCH_BALL: ("happy", False),
            PuppyState.CARRY_BALL: ("run_right", False),
            PuppyState.DROP_BALL: ("sit", False),
            PuppyState.WAIT_FOR_THROW: ("sit", False),
        }

        self.frames.clear()

        for state, (folder, default_flip) in mapping.items():
            dir_path = os.path.join(coat_dir, folder)
            raw_pixmaps = []
            if os.path.exists(dir_path):
                files = sorted([f for f in os.listdir(dir_path) if f.endswith(".png")])
                for f in files:
                    pix = QPixmap(os.path.join(dir_path, f))
                    if default_flip:
                        pix = pix.transformed(QTransform().scale(-1, 1))
                    if pix.width() != target_w or pix.height() != target_h:
                        pix = pix.scaled(target_w, target_h)
                    raw_pixmaps.append(pix)
            if not raw_pixmaps:
                raw_pixmaps = [QPixmap(target_w, target_h)]

            right_list = raw_pixmaps
            left_list = [p.transformed(QTransform().scale(-1, 1)) for p in raw_pixmaps]

            self.frames[state] = {
                True: right_list,
                False: left_list
            }

    def get_current_frame(self, state: PuppyState, facing_right=True) -> QPixmap:
        state_dict = self.frames.get(state, self.frames.get(PuppyState.IDLE, {}))
        frames_list = state_dict.get(facing_right, [])
        if not frames_list:
            scale = self.settings.size_scale
            return QPixmap(int(72 * scale), int(72 * scale))
        idx = self.current_frame_index % len(frames_list)
        return frames_list[idx]

    def advance_frame(self):
        self.current_frame_index += 1

    def get_fps(self, state: PuppyState):
        if state in (PuppyState.RUN, PuppyState.RUN_RIGHT, PuppyState.RUN_LEFT, PuppyState.SPRINT, PuppyState.BALL_CHASE):
            return 24
        elif state in (PuppyState.WALK, PuppyState.WALK_RIGHT, PuppyState.WALK_LEFT, PuppyState.FAST_WALK):
            return 16
        elif state == PuppyState.SLEEP:
            return 4
        return 12
