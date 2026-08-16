import time
import random

class PetBrain:
    def __init__(self, settings_manager):
        self.settings = settings_manager
        self.last_update_time = time.time()

    def update_needs(self):
        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now

        # Gradual need progression over time
        hunger = min(100, self.settings.get("hunger", 20) + dt * 0.15)
        thirst = min(100, self.settings.get("thirst", 20) + dt * 0.20)
        energy = max(0, self.settings.get("energy", 95) - dt * 0.10)
        happiness = max(0, self.settings.get("happiness", 85) - dt * 0.05)

        self.settings.set("hunger", hunger)
        self.settings.set("thirst", thirst)
        self.settings.set("energy", energy)
        self.settings.set("happiness", happiness)

    def decide_autonomous_action(self):
        self.update_needs()

        hunger = self.settings.get("hunger", 20)
        thirst = self.settings.get("thirst", 20)
        energy = self.settings.get("energy", 95)

        # Priority Needs Decision Tree
        if hunger > 75:
            return "EAT"
        elif thirst > 75:
            return "DRINK"
        elif energy < 25:
            return "SLEEP"
        else:
            return "WANDER"
