import time
import random
from datetime import datetime

class WellnessEngine:
    def __init__(self, settings_manager, puppy_window):
        self.settings = settings_manager
        self.puppy = puppy_window

        self.last_water_time = time.time()
        self.last_eye_time = time.time()
        self.last_stretch_time = time.time()
        self.last_move_time = time.time()
        self.last_posture_time = time.time()

    def get_time_based_greeting(self) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 11:
            greetings = ["Good morning! ☀️", "Good morning! Ready for a great day? 🐾", "Rise and shine! ☀️"]
        elif 11 <= hour < 16:
            greetings = ["Good afternoon! ☀️", "Hope your day is going great! 🐶"]
        elif 16 <= hour < 21:
            greetings = ["Good evening! 🌇", "Unwinding for the day? 🐾"]
        else:
            greetings = ["Working late? Take care of yourself! 🌙", "Good night! 🌙"]
        return random.choice(greetings)

    def trigger_startup_greeting(self):
        msg = self.get_time_based_greeting()
        self.puppy.speech.show_message(msg, self.puppy.geometry().center(), duration_ms=4500)

    def check_wellness_reminders(self):
        if not self.settings.get("wellness_enabled", True) or self.puppy.is_paused:
            return

        # Quiet hours check
        hour = datetime.now().hour
        quiet_start = self.settings.get("quiet_start", 23)
        quiet_end = self.settings.get("quiet_end", 7)
        if hour >= quiet_start or hour < quiet_end:
            return

        now = time.time()

        # Water reminder (approx 60-120 mins, default interval settings)
        water_interval = self.settings.get("water_interval_min", 60) * 60
        if now - self.last_water_time > water_interval:
            self.last_water_time = now
            self.trigger_water_reminder()
            return

        # Eye break (approx 45-60 mins)
        eye_interval = self.settings.get("eye_interval_min", 45) * 60
        if now - self.last_eye_time > eye_interval:
            self.last_eye_time = now
            self.trigger_eye_reminder()
            return

        # Stretch break (approx 60-90 mins)
        stretch_interval = self.settings.get("stretch_interval_min", 60) * 60
        if now - self.last_stretch_time > stretch_interval:
            self.last_stretch_time = now
            self.trigger_stretch_reminder()
            return

    def trigger_water_reminder(self):
        self.puppy.speech.show_message("Water break? 💧", self.puppy.geometry().center(), duration_ms=3500)
        self.puppy.start_drinking_routine()

    def trigger_eye_reminder(self):
        from puppy.state import PuppyState
        self.puppy.state_machine.set_state(PuppyState.SIT)
        self.puppy.speech.show_message("Rest your eyes! 👀", self.puppy.geometry().center(), duration_ms=3500)

    def trigger_stretch_reminder(self):
        from puppy.state import PuppyState
        self.puppy.state_machine.set_state(PuppyState.STRETCH)
        self.puppy.speech.show_message("Let's stretch! 🧘", self.puppy.geometry().center(), duration_ms=3500)
