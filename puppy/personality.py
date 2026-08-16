from enum import Enum, auto
import random

class Mood(Enum):
    HAPPY = "Happy 😊"
    CALM = "Calm 😌"
    EXCITED = "Excited 🎉"
    SLEEPY = "Sleepy 🥱"
    BORED = "Bored 💤"
    PLAYFUL = "Playful 🎾"
    CURIOUS = "Curious 🤔"

class PersonalityController:
    def __init__(self, settings_manager):
        self.settings = settings_manager

    @property
    def current_mood(self) -> Mood:
        affection = self.settings.get("affection", 60)
        happiness = self.settings.get("happiness", 85)
        energy = self.settings.get("energy", 95)

        if energy < 30:
            return Mood.SLEEPY
        elif happiness > 80 and energy > 60:
            return Mood.PLAYFUL if random.random() < 0.5 else Mood.HAPPY
        elif happiness < 40:
            return Mood.BORED
        elif affection > 80:
            return Mood.EXCITED
        else:
            return Mood.CALM

    def update_metrics(self, delta_affection=0, delta_happiness=0, delta_energy=0):
        aff = max(0, min(100, self.settings.get("affection", 60) + delta_affection))
        hap = max(0, min(100, self.settings.get("happiness", 85) + delta_happiness))
        ene = max(0, min(100, self.settings.get("energy", 95) + delta_energy))

        self.settings.set("affection", aff)
        self.settings.set("happiness", hap)
        self.settings.set("energy", ene)
