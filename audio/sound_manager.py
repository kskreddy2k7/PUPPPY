import time
import random

class SoundManager:
    def __init__(self, settings_manager):
        self.settings = settings_manager

        # Cooldown timestamps for each sound category
        self.last_pet_time = 0
        self.last_bark_time = 0
        self.last_hunger_time = 0
        self.last_thirst_time = 0
        self.last_play_time = 0

    def _play_beeps(self, freq_list):
        if not self.settings.get("sound_enabled", True):
            return
        vol = self.settings.get("sound_volume", 60)
        if vol <= 0:
            return

        try:
            import winsound
            for freq, dur in freq_list:
                adjusted_freq = max(100, min(3500, int(freq)))
                winsound.Beep(adjusted_freq, int(dur))
        except Exception:
            pass

    # 1. REMOVE WALKING SOUNDS COMPLETELY (SILENT MOVEMENT)
    def play_step(self):
        # NO-OP: Movement is completely silent as requested
        pass

    # 2. SHORT CUTE PUPPY VOCALIZATIONS WITH COOLDOWNS & VARIATIONS
    def play_soft_whine(self):
        now = time.time()
        if now - self.last_hunger_time < 15.0:
            return
        self.last_hunger_time = now
        # Cute soft puppy whine sound variation
        var = random.choice([
            [(1100, 60), (1400, 90)],
            [(1250, 70), (1500, 80)],
            [(950, 80), (1200, 100)]
        ])
        self._play_beeps(var)

    def play_thirst_whine(self):
        now = time.time()
        if now - self.last_thirst_time < 15.0:
            return
        self.last_thirst_time = now
        # Soft gentle thirst whine
        self._play_beeps([(1300, 60), (1600, 90)])

    def play_bark(self):
        now = time.time()
        if now - self.last_bark_time < 3.0:
            return
        self.last_bark_time = now
        # Soft cute puppy bark ("woof!")
        self._play_beeps([(1450, 70), (1850, 80)])

    def play_happy(self):
        now = time.time()
        if now - self.last_pet_time < 2.5:
            return
        self.last_pet_time = now
        # Short cute happy yip ("yip!")
        var = random.choice([
            [(1600, 50), (2100, 70)],
            [(1750, 60), (2200, 80)]
        ])
        self._play_beeps(var)

    def play_toy(self):
        now = time.time()
        if now - self.last_play_time < 5.0:
            return
        self.last_play_time = now
        # Tiny excited puppy sound
        self._play_beeps([(1800, 50), (2300, 60)])

    def play_eat(self):
        # Very subtle chew/lick munching sound
        self._play_beeps([(750, 35)])

    def play_drink(self):
        # Subtle water licking sound
        self._play_beeps([(900, 35)])

    def play_sleep(self):
        # One soft cute yawn sound
        self._play_beeps([(550, 140), (420, 160)])

    def play_wake(self):
        # Tiny sleepy wake puppy sound
        self._play_beeps([(650, 70), (1100, 90)])
