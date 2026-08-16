ACHIEVEMENTS_LIST = {
    "first_day": ("Welcome Home!", "Started Cute Puppy for the very first time!"),
    "good_boy": ("Good Boy!", "Petted your puppy 10 times!"),
    "best_friends": ("Best Friends", "Reached 90+ Affection level!"),
    "ball_champ": ("Fetch Champion", "Played fetch 5 times!"),
    "home_sweet_home": ("Home Sweet Home", "Puppy visited its cozy house!"),
    "pro_napper": ("Pro Napper", "Let puppy rest inside its house!")
}

class AchievementsManager:
    def __init__(self, settings_manager, speech_bubble=None):
        self.settings = settings_manager
        self.speech = speech_bubble

    def unlock(self, achievement_key: str, center_pos=None):
        unlocked = self.settings.get("unlocked_achievements", [])
        if achievement_key not in unlocked and achievement_key in ACHIEVEMENTS_LIST:
            unlocked.append(achievement_key)
            self.settings.set("unlocked_achievements", unlocked)
            title, desc = ACHIEVEMENTS_LIST[achievement_key]
            if self.speech and center_pos:
                self.speech.show_message(f"🏆 UNLOCKED:\n{title}!", center_pos, duration_ms=4000)
            return True
        return False
