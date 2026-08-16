import os
import sys
import unittest
from PySide6.QtWidgets import QApplication

# Set path to src
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

app = QApplication.instance() or QApplication(sys.argv)

class TestCutePuppyCore(unittest.TestCase):
    def test_imports(self):
        """Test core module imports"""
        from cute_puppy.platform.common import get_version, get_asset_path
        from cute_puppy.storage import SettingsManager
        from cute_puppy.physics import MovementPhysics
        from cute_puppy.pet.state import PuppyState, StateMachine
        from cute_puppy.behavior import PersonalityController, Mood
        
        self.assertEqual(get_version(), "1.0.0")

    def test_settings_load_save(self):
        """Test configuration save and load state"""
        from cute_puppy.storage import SettingsManager
        sm = SettingsManager()
        sm.set("test_key", "test_val")
        self.assertEqual(sm.get("test_key"), "test_val")

    def test_movement_physics(self):
        """Test ball and puppy physics update loop"""
        from cute_puppy.physics import MovementPhysics
        phys = MovementPhysics(100, 100)
        phys.set_target(200, 200)
        dist, spd = phys.update_physics()
        self.assertGreater(spd, 0.0)

    def test_puppy_state_machine(self):
        """Test state machine state changes"""
        from cute_puppy.pet.state import PuppyState, StateMachine
        sm = StateMachine(PuppyState.IDLE)
        sm.set_state(PuppyState.RUN)
        self.assertEqual(sm.current_state, PuppyState.RUN)

    def test_animation_controller(self):
        """Test animation frame loading and cache"""
        from cute_puppy.storage import SettingsManager
        from cute_puppy.animation import AnimationController
        from cute_puppy.pet.state import PuppyState
        sm = SettingsManager()
        anim = AnimationController(sm)
        frame = anim.get_current_frame(PuppyState.IDLE, facing_right=True)
        self.assertFalse(frame.isNull())

if __name__ == "__main__":
    unittest.main()
