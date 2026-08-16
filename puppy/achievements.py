import os
from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QFont

ACHIEVEMENTS_LIST = {
    "first_day": ("🐾 First Day Together", "Started your journey with Milo!"),
    "ball_champ": ("🎾 Ball Champion", "Played with the toy 5 times!"),
    "home_sweet_home": ("🏠 Home Sweet Home", "Milo completed a peaceful sleep routine!"),
    "best_friends": ("❤️ Best Friends", "Reached 90+ affection with Milo!"),
    "pro_napper": ("😴 Professional Napper", "Milo slept peacefully in his house!"),
    "good_boy": ("🐶 Good Boy", "Petted Milo 10 times!")
}

class AchievementsManager:
    def __init__(self, settings_manager, speech_bubble=None):
        self.settings = settings_manager
        self.speech = speech_bubble

    def unlock(self, achievement_id: str, pos: QPoint = None):
        unlocked = self.settings.get("unlocked_achievements", [])
        if achievement_id not in unlocked and achievement_id in ACHIEVEMENTS_LIST:
            unlocked.append(achievement_id)
            self.settings.set("unlocked_achievements", unlocked)
            title, desc = ACHIEVEMENTS_LIST[achievement_id]
            print(f"Achievement Unlocked: {achievement_id} - {desc}")
            if self.speech and pos:
                self.speech.show_message(f"🏆 {title}!", pos, duration_ms=4000)
