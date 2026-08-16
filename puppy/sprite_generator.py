import os
import math
from PIL import Image, ImageDraw

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
REF_IMAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts_image.png")

def generate_puppy_sprites():
    puppy_dir = os.path.join(ASSETS_DIR, "puppy")
    os.makedirs(puppy_dir, exist_ok=True)

    W, H = 72, 72

    COAT_PALETTES = {
        "Brown & Cream": {
            "main": (212, 140, 75, 255),
            "dark": (168, 98, 42, 255),
            "cream": (248, 238, 216, 255)
        },
        "White": {
            "main": (245, 245, 248, 255),
            "dark": (220, 220, 225, 255),
            "cream": (255, 255, 255, 255)
        },
        "Golden": {
            "main": (238, 185, 75, 255),
            "dark": (205, 145, 40, 255),
            "cream": (254, 244, 210, 255)
        },
        "Black & White": {
            "main": (45, 45, 50, 255),
            "dark": (25, 25, 30, 255),
            "cream": (245, 245, 248, 255)
        }
    }

    C_EYE = (30, 20, 15, 255)
    C_EYE_SHINE = (255, 255, 255, 255)
    C_NOSE = (40, 25, 20, 255)
    C_TONGUE = (245, 120, 140, 255)
    C_COLLAR = (45, 120, 230, 255)
    C_TAG = (255, 215, 0, 255)
    C_SHADOW = (0, 0, 0, 45)

    def draw_quadruped_puppy(draw, pose="IDLE", frame=0, facing_right=True, coat="Brown & Cream"):
        pal = COAT_PALETTES.get(coat, COAT_PALETTES["Brown & Cream"])
        c_main, c_dark, c_cream = pal["main"], pal["dark"], pal["cream"]

        shadow_w = 44 if pose in ("WALK", "RUN", "EAT", "DRINK") else 38
        shadow_h = 10
        sy = H - 10
        sx = (W - shadow_w) // 2
        draw.ellipse([sx, sy - shadow_h//2, sx + shadow_w, sy + shadow_h//2], fill=C_SHADOW)

        bounce = 0
        if pose == "WALK":
            bounce = 1 if frame % 2 == 1 else 0
        elif pose == "RUN":
            bounce = -3 if frame in (1, 4) else 2
        elif pose in ("EAT", "DRINK"):
            bounce = 2 if frame % 2 == 1 else 0

        bx, by = W // 2, H - 24 + bounce

        if pose == "WALK":
            fl_off = math.sin(frame * math.pi / 3) * 6
            fr_off = -fl_off
            rl_off = -fl_off
            rr_off = fl_off
        elif pose == "RUN":
            fl_off = math.sin(frame * math.pi / 3) * 10
            fr_off = -fl_off
            rl_off = -fl_off
            rr_off = fl_off
        else:
            fl_off = fr_off = rl_off = rr_off = 0

        if not facing_right:
            fl_off, fr_off, rl_off, rr_off = -fl_off, -fr_off, -rl_off, -rr_off

        # Adjust torso and head height for SIT and SAD poses
        if pose in ("SIT", "SAD"):
            by += 4  # Lower rear body for sitting posture

        # 1. Tail
        tail_wag = math.sin(frame * 1.5) * 8 if pose in ("HAPPY", "WALK", "RUN", "EXCITED", "EAT") else (-2 if pose == "SAD" else 2)
        tx = bx - 18 if facing_right else bx + 18
        draw.ellipse([tx - 4, by - 8 + tail_wag, tx + 4, by + 2 + tail_wag], fill=c_dark)

        # 2. Back Legs / Sitting Paws
        if pose in ("SIT", "SAD"):
            # Folded rear paws for cute sitting posture
            draw.ellipse([bx - 16, by + 2, bx - 4, by + 12], fill=c_dark)
            draw.ellipse([bx + 4, by + 2, bx + 16, by + 12], fill=c_dark)
        else:
            draw.ellipse([bx - 14 + rl_off, by + 2, bx - 6 + rl_off, by + 12], fill=c_dark)
            draw.ellipse([bx + 6 + fl_off, by + 2, bx + 14 + fl_off, by + 12], fill=c_dark)

        # 3. Body Torso
        draw.ellipse([bx - 20, by - 10, bx + 16, by + 8], fill=c_main)
        draw.ellipse([bx - 14, by - 4, bx + 14, by + 8], fill=c_cream)

        # 4. Front Legs
        if pose in ("SIT", "SAD"):
            # Vertical front paws for sitting upright
            draw.ellipse([bx - 10, by + 4, bx - 2, by + 16], fill=c_cream)
            draw.ellipse([bx + 2, by + 4, bx + 10, by + 16], fill=c_cream)
        else:
            draw.ellipse([bx - 16 + rr_off, by + 4, bx - 8 + rr_off, by + 14], fill=c_cream)
            draw.ellipse([bx + 4 + fr_off, by + 4, bx + 12 + fr_off, by + 14], fill=c_cream)

        # 5. Collar
        cx = bx + (8 if facing_right else -8)
        draw.rectangle([cx - 4, by - 12, cx + 4, by - 8], fill=C_COLLAR)
        draw.ellipse([cx - 2, by - 8, cx + 2, by - 4], fill=C_TAG)

        # 6. Head
        hx = bx + (14 if facing_right else -14)
        hy = by - 14 + (1 if bounce > 0 else -1)

        if pose in ("SIT", "HAPPY", "EXCITED"):
            hy -= 4  # Upright attentive head position
        elif pose == "SAD":
            hy += 4   # Drooping head position

        if pose in ("EAT", "DRINK", "SNIFF"):
            hy += 8
            hx += (6 if facing_right else -6)
        elif pose == "SLEEP":
            hy += 8
        elif pose == "YAWN":
            hy -= 2

        draw.ellipse([hx - 14, hy - 14, hx + 14, hy + 12], fill=c_main)

        ear_bounce = 3 if pose in ("WALK", "RUN") and frame % 2 == 1 else 0
        if pose == "SAD": ear_bounce += 4  # Droopy ears
        draw.ellipse([hx - 18, hy - 10 + ear_bounce, hx - 8, hy + 8 + ear_bounce], fill=c_dark)
        draw.ellipse([hx + 8, hy - 10 + ear_bounce, hx + 18, hy + 8 + ear_bounce], fill=c_dark)

        mx = hx + (4 if facing_right else -4)
        draw.ellipse([mx - 8, hy - 2, mx + 8, hy + 10], fill=c_cream)
        draw.ellipse([mx - 3, hy, mx + 3, hy + 5], fill=C_NOSE)

        if pose == "SLEEP":
            draw.arc([hx - 9, hy - 5, hx - 2, hy + 2], 20, 160, fill=C_EYE, width=2)
            draw.arc([hx + 2, hy - 5, hx + 9, hy + 2], 20, 160, fill=C_EYE, width=2)
        elif pose == "SAD":
            # Sad droopy eyes + tear drop
            draw.arc([hx - 9, hy - 5, hx - 2, hy + 2], 200, 340, fill=C_EYE, width=2)
            draw.arc([hx + 2, hy - 5, hx + 9, hy + 2], 200, 340, fill=C_EYE, width=2)
            # Blue tear drop
            draw.ellipse([mx + 6, hy + 2, mx + 10, hy + 8], fill=(80, 160, 245, 255))
        elif pose == "YAWN":
            draw.arc([hx - 9, hy - 5, hx - 2, hy + 2], 20, 160, fill=C_EYE, width=2)
            draw.arc([hx + 2, hy - 5, hx + 9, hy + 2], 20, 160, fill=C_EYE, width=2)
            draw.ellipse([mx - 4, hy + 4, mx + 4, hy + 11], fill=C_EYE)
            draw.ellipse([mx - 2, hy + 6, mx + 2, hy + 12], fill=C_TONGUE)
        else:
            ex1, ex2 = hx - 8, hx + 2
            ey = hy - 6
            draw.ellipse([ex1, ey, ex1 + 6, ey + 8], fill=C_EYE)
            draw.ellipse([ex2, ey, ex2 + 6, ey + 8], fill=C_EYE)

            draw.ellipse([ex1 + 2, ey + 2, ex1 + 4, ey + 4], fill=C_EYE_SHINE)
            draw.ellipse([ex2 + 2, ey + 2, ex2 + 4, ey + 4], fill=C_EYE_SHINE)

            if pose in ("HAPPY", "EXCITED", "PLAY", "PETTED", "EAT", "DRINK"):
                draw.arc([mx - 4, hy + 3, mx + 4, hy + 9], 0, 180, fill=C_EYE, width=2)
                draw.ellipse([mx - 2, hy + 5, mx + 2, hy + 10], fill=C_TONGUE)

    states = {
        "IDLE": 6,
        "WALK_RIGHT": 6,
        "WALK_LEFT": 6,
        "RUN_RIGHT": 6,
        "RUN_LEFT": 6,
        "SIT": 4,
        "SNIFF": 4,
        "HAPPY": 6,
        "SLEEP": 4,
        "PETTED": 4,
        "PLAY": 6,
        "STRETCH": 4,
        "YAWN": 4,
        "EAT": 6,
        "DRINK": 6,
        "SAD": 4
    }

    for coat_name in COAT_PALETTES.keys():
        coat_slug = coat_name.lower().replace(" & ", "_").replace(" ", "_")
        for state_name, num_frames in states.items():
            state_dir = os.path.join(puppy_dir, coat_slug, state_name.lower())
            os.makedirs(state_dir, exist_ok=True)

            facing_right = "LEFT" not in state_name
            pose = state_name.split("_")[0]

            for f in range(num_frames):
                img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                draw_quadruped_puppy(draw, pose=pose, frame=f, facing_right=facing_right, coat=coat_name)

                filename = os.path.join(state_dir, f"frame_{f}.png")
                img.save(filename)

    print("Four-legged quadruped puppy sprites generated successfully!")

def generate_house_sprites():
    house_dir = os.path.join(ASSETS_DIR, "house")
    os.makedirs(house_dir, exist_ok=True)

    W, H = 110, 110

    img_day = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img_day)

    draw.ellipse([5, H - 20, W - 5, H - 5], fill=(0, 0, 0, 60))
    draw.rectangle([20, 45, W - 20, H - 15], fill=(185, 122, 67, 255), outline=(120, 70, 30, 255), width=2)
    for y in range(55, H - 15, 12):
        draw.line([21, y, W - 21, y], fill=(150, 95, 45, 255), width=1)

    draw.ellipse([38, 52, W - 38, H - 15], fill=(40, 25, 20, 255))
    draw.rectangle([38, 70, W - 38, H - 15], fill=(40, 25, 20, 255))

    roof_pts = [(W // 2, 8), (10, 48), (W - 10, 48)]
    draw.polygon(roof_pts, fill=(160, 54, 35, 255), outline=(100, 30, 20, 255))
    draw.line([(W // 2, 6), (6, 50)], fill=(230, 200, 160, 255), width=4)
    draw.line([(W // 2, 6), (W - 6, 50)], fill=(230, 200, 160, 255), width=4)
    draw.rectangle([72, 18, 84, 36], fill=(130, 80, 50, 255), outline=(80, 45, 25, 255))

    # Red Food Bowl & Blue Water Bowl
    draw.ellipse([10, H - 22, 24, H - 12], fill=(220, 60, 50, 255)) # Food
    draw.ellipse([26, H - 22, 40, H - 12], fill=(60, 130, 220, 255)) # Water

    draw.ellipse([14, 52, 24, 62], fill=(255, 220, 100, 255), outline=(150, 100, 30, 255))

    img_day.save(os.path.join(house_dir, "house.png"))

    img_night = img_day.copy()
    draw_n = ImageDraw.Draw(img_night)
    draw_n.ellipse([38, 52, W - 38, H - 15], fill=(255, 180, 70, 200))
    draw_n.rectangle([38, 70, W - 38, H - 15], fill=(255, 180, 70, 200))
    draw_n.ellipse([14, 52, 24, 62], fill=(255, 240, 160, 255))

    img_night.save(os.path.join(house_dir, "house_sleeping.png"))

def generate_toy_sprites():
    toys_dir = os.path.join(ASSETS_DIR, "toys")
    os.makedirs(toys_dir, exist_ok=True)

    W, H = 32, 32

    # Red Ball
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, H - 6, W - 4, H - 2], fill=(0, 0, 0, 50))
    draw.ellipse([2, 2, W - 4, H - 4], fill=(255, 70, 60, 255), outline=(180, 30, 20, 255), width=2)
    draw.line([6, 14, W - 8, 14], fill=(255, 220, 50, 255), width=3)
    img.save(os.path.join(toys_dir, "ball_red.png"))

    # Blue Ball
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, H - 6, W - 4, H - 2], fill=(0, 0, 0, 50))
    draw.ellipse([2, 2, W - 4, H - 4], fill=(50, 140, 245, 255), outline=(20, 80, 180, 255), width=2)
    draw.line([6, 14, W - 8, 14], fill=(255, 255, 255, 255), width=3)
    img.save(os.path.join(toys_dir, "ball_blue.png"))

    # Bone
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, H - 6, W - 4, H - 2], fill=(0, 0, 0, 40))
    draw.rectangle([8, 12, 24, 20], fill=(245, 240, 230, 255), outline=(180, 175, 165, 255))
    draw.ellipse([4, 8, 12, 16], fill=(245, 240, 230, 255))
    draw.ellipse([4, 16, 12, 24], fill=(245, 240, 230, 255))
    draw.ellipse([20, 8, 28, 16], fill=(245, 240, 230, 255))
    draw.ellipse([20, 16, 28, 24], fill=(245, 240, 230, 255))
    img.save(os.path.join(toys_dir, "bone.png"))

    # Rope
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, H - 6, W - 4, H - 2], fill=(0, 0, 0, 40))
    draw.line([6, 22, 26, 8], fill=(230, 160, 60, 255), width=6)
    draw.ellipse([4, 18, 12, 26], fill=(210, 80, 60, 255))
    draw.ellipse([20, 4, 28, 12], fill=(60, 150, 210, 255))
    img.save(os.path.join(toys_dir, "rope.png"))

    # Teddy Bear
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, H - 6, W - 4, H - 2], fill=(0, 0, 0, 50))
    draw.ellipse([8, 12, 24, 28], fill=(175, 115, 60, 255))
    draw.ellipse([10, 4, 22, 16], fill=(175, 115, 60, 255))
    draw.ellipse([6, 2, 12, 8], fill=(140, 90, 45, 255))
    draw.ellipse([20, 2, 26, 8], fill=(140, 90, 45, 255))
    draw.ellipse([12, 16, 20, 24], fill=(235, 190, 140, 255))
    img.save(os.path.join(toys_dir, "teddy.png"))

def generate_all_assets():
    generate_puppy_sprites()
    generate_house_sprites()
    generate_toy_sprites()

if __name__ == "__main__":
    generate_all_assets()
