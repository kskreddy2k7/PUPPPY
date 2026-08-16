import os
import random
import math
import time
from PySide6.QtWidgets import QWidget, QMenu, QInputDialog, QApplication
from PySide6.QtCore import Qt, QPoint, QTimer, QRect, Signal
from PySide6.QtGui import QPainter, QCursor, QAction, QColor, QFont, QPixmap

from cute_puppy.pet.state import PuppyState, StateMachine
from cute_puppy.physics.movement import MovementPhysics
from cute_puppy.animation.controller import AnimationController
from cute_puppy.ui.speech_bubble import SpeechBubble
from cute_puppy.behavior.personality import PersonalityController, Mood
from cute_puppy.behavior.brain import PetBrain
from cute_puppy.behavior.achievements import AchievementsManager
from cute_puppy.behavior.wellness import WellnessEngine

class PuppyWindow(QWidget):
    request_settings_signal = Signal()
    request_customization_signal = Signal()
    request_achievements_signal = Signal()

    def __init__(self, settings_manager, sound_manager, house_window, toy_window, parent=None):
        super().__init__(parent)
        self.settings = settings_manager
        self.sound = sound_manager
        self.house = house_window
        self.toy = toy_window

        self.house.puppy = self
        if self.toy:
            self.toy.puppy = self

        self.facing_right = True

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.size_scale = self.settings.size_scale
        base_w, base_h = int(72 * self.size_scale), int(72 * self.size_scale)
        self.setFixedSize(base_w, base_h)

        # Core Engines
        self.state_machine = StateMachine(PuppyState.IDLE)
        self.physics = MovementPhysics(300, 300)
        self.anim = AnimationController(self.settings)
        self.speech = SpeechBubble()

        self.personality = PersonalityController(self.settings)
        self.brain = PetBrain(self.settings)
        self.achievements = AchievementsManager(self.settings, self.speech)

        self.achievements.unlock("first_day", self.geometry().center())

        self.pet_count = 0
        self.play_count = 0
        self.owner_throw_pos = QPoint(400, 400)

        # Timers
        self.game_timer = QTimer(self)
        self.game_timer.setInterval(30)
        self.game_timer.timeout.connect(self.game_loop)

        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(140)
        self.anim_timer.timeout.connect(self.anim_loop)

        self.autonomous_timer = QTimer(self)
        self.autonomous_timer.setInterval(4000)
        self.autonomous_timer.timeout.connect(self.trigger_autonomous_behavior)

        self.last_cursor_pos = QCursor.pos()
        self.last_input_time = time.time()
        self.is_paused = False
        self.is_photo_mode = False
        self.is_carrying_toy = False
        self.hearts = []

        self.move(300, 300)
        self.physics.x = 300.0
        self.physics.y = 300.0

        self.wellness = WellnessEngine(self.settings, self)

        self.game_timer.start()
        self.anim_timer.start()
        self.autonomous_timer.start()

        QTimer.singleShot(1500, self.wellness.trigger_startup_greeting)

    def game_loop(self):
        if self.is_paused:
            return

        state = self.state_machine.current_state

        cursor_pos = QCursor.pos()
        cursor_dx = cursor_pos.x() - self.last_cursor_pos.x()
        cursor_dy = cursor_pos.y() - self.last_cursor_pos.y()
        dist_moved = math.hypot(cursor_dx, cursor_dy)
        if dist_moved > 2:
            self.last_input_time = time.time()
        self.last_cursor_pos = cursor_pos

        if dist_moved > 5 and state in (PuppyState.SLEEP, PuppyState.SLEEP_WALK):
            if self.house.is_sleeping_inside or state == PuppyState.SLEEP_WALK:
                self.wake_up_routine()
                return

        if self.settings.get("smart_idle_sleep", True) and (time.time() - self.last_input_time > 120.0):
            if state not in (PuppyState.SLEEP, PuppyState.SLEEP_WALK):
                self.start_silent_home_routine()
                return

        speed_factor = self.settings.speed_factor

        if state == PuppyState.SLEEP_WALK:
            door_pos = self.house.get_door_global_pos()
            self.physics.set_target(door_pos.x() - self.width() // 2, door_pos.y() - self.height() // 2)
            dist, speed = self.physics.update_physics(is_running=False, speed_factor=speed_factor)
            self.move(self.physics.pos[0], self.physics.pos[1])
            if dist < 15:
                self.enter_house_sequence()
            return

        elif state == PuppyState.EXIT_HOUSE:
            self.move(self.physics.pos[0], self.physics.pos[1])
            return

        elif self.toy and state in (PuppyState.BALL_CHASE, PuppyState.RUN_RIGHT, PuppyState.RUN_LEFT):
            if self.is_carrying_toy:
                target_x = self.owner_throw_pos.x() - self.width() // 2
                target_y = self.owner_throw_pos.y() - self.height() // 2
                self.physics.set_target(target_x, target_y)
                dist, speed = self.physics.update_physics(is_running=True, speed_factor=speed_factor)
                self.move(self.physics.pos[0], self.physics.pos[1])

                self.toy.move(self.x() + (36 if self.facing_right else 8), self.y() + 24)

                if dist < 30:
                    self.is_carrying_toy = False
                    self.toy.vx = 0.0
                    self.toy.vy = 0.0
                    self.state_machine.set_state(PuppyState.HAPPY)
                    self.speech.show_message("Again? 🎾", self.geometry().center())
                    self.sound.play_happy()
                    self.personality.update_metrics(delta_happiness=15)
                    self.play_count += 1
                    if self.play_count >= 5:
                        self.achievements.unlock("ball_champ", self.geometry().center())
                return
            else:
                toy_c = self.toy.center_pos()
                self.physics.set_target(toy_c.x() - self.width() // 2, toy_c.y() - self.height() // 2)
                dist, speed = self.physics.update_physics(is_running=True, speed_factor=speed_factor)
                self.move(self.physics.pos[0], self.physics.pos[1])

                dx_target = toy_c.x() - self.x()
                if abs(dx_target) > 12:
                    self.facing_right = (dx_target > 0)

                if dist < 25:
                    self.is_carrying_toy = True
                    self.sound.play_toy()
                    self.speech.show_message("I got it! 🐾", self.geometry().center())
                    self.owner_throw_pos = QCursor.pos()
                return

        elif self.settings.get("follow_cursor", True) and state not in (PuppyState.PETTED, PuppyState.PLAY, PuppyState.SNIFF, PuppyState.STRETCH, PuppyState.YAWN, PuppyState.EAT, PuppyState.DRINK):
            pred_x = cursor_pos.x() + cursor_dx * 0.3
            pred_y = cursor_pos.y() + cursor_dy * 0.3
            target_x = pred_x - (self.width() // 2)
            target_y = pred_y - (self.height() // 2)
            self.physics.set_target(target_x, target_y)

            is_fast = dist_moved > 15
            dist, speed = self.physics.update_physics(is_running=is_fast, speed_factor=speed_factor)
            self.move(self.physics.pos[0], self.physics.pos[1])

            dx_target = target_x - self.x()
            if abs(dx_target) > 18:
                self.facing_right = (dx_target > 0)

            speed_cat = self.physics.get_speed_category(speed, dist_moved)

            if dist < 20 or speed_cat == "IDLE":
                if state not in (PuppyState.SNIFF, PuppyState.HAPPY):
                    self.state_machine.set_state(PuppyState.SIT)
            else:
                if speed_cat == "SPRINT":
                    self.state_machine.set_state(PuppyState.SPRINT)
                elif speed_cat == "RUN":
                    self.state_machine.set_state(PuppyState.RUN_RIGHT if self.facing_right else PuppyState.RUN_LEFT)
                elif speed_cat == "FAST_WALK":
                    self.state_machine.set_state(PuppyState.FAST_WALK)
                else:
                    self.state_machine.set_state(PuppyState.WALK_RIGHT if self.facing_right else PuppyState.WALK_LEFT)

        self.speech.update_position(self.geometry().center())
        self.update_hearts()

    def anim_loop(self):
        self.anim.advance_frame()
        state = self.state_machine.current_state

        if state == PuppyState.SLEEP:
            target_fps = 4
        elif state in (PuppyState.IDLE, PuppyState.SIT):
            target_fps = 15
        elif state in (PuppyState.RUN, PuppyState.SPRINT, PuppyState.BALL_CHASE):
            target_fps = 60
        else:
            target_fps = 30

        interval = max(16, int(1000 / target_fps))
        if self.anim_timer.interval() != interval:
            self.anim_timer.setInterval(interval)

        self.update()

    def trigger_fetch_routine(self):
        if self.state_machine.current_state == PuppyState.SLEEP:
            self.wake_up_routine()
        self.owner_throw_pos = QCursor.pos()
        self.is_carrying_toy = False
        self.state_machine.set_state(PuppyState.BALL_CHASE)
        self.speech.show_message("Fetch! 🎾", self.geometry().center())

    def start_eating_routine(self):
        bowl_pos = self.house.get_bowl_global_pos()
        self.physics.set_target(bowl_pos.x() - self.width() // 2, bowl_pos.y() - self.height() // 2)
        self.state_machine.set_state(PuppyState.WALK)
        self.speech.show_message("Going to eat... 🍖", self.geometry().center(), 2000)

        def arrive_and_eat():
            self.state_machine.set_state(PuppyState.EAT)
            self.speech.show_message("Yum yum~ 🍖", self.geometry().center(), 3000)
            self.sound.play_eat()
            self.settings.set("hunger", 0)

            def return_to_cursor():
                cur = QCursor.pos()
                self.physics.set_target(cur.x() - self.width() // 2, cur.y() - self.height() // 2)
                self.state_machine.set_state(PuppyState.HAPPY)
                self.speech.show_message("Back to you! 🐾", self.geometry().center(), 2000)

            QTimer.singleShot(3000, return_to_cursor)

        QTimer.singleShot(2500, arrive_and_eat)

    def start_drinking_routine(self):
        bowl_pos = self.house.get_bowl_global_pos()
        self.physics.set_target(bowl_pos.x() - self.width() // 2, bowl_pos.y() - self.height() // 2)
        self.state_machine.set_state(PuppyState.WALK)
        self.speech.show_message("Going for water... 💧", self.geometry().center(), 2000)

        def arrive_and_drink():
            self.state_machine.set_state(PuppyState.DRINK)
            self.speech.show_message("Slurp slurp~ 💧", self.geometry().center(), 3000)
            self.sound.play_drink()
            self.settings.set("thirst", 0)

            def return_to_cursor():
                cur = QCursor.pos()
                self.physics.set_target(cur.x() - self.width() // 2, cur.y() - self.height() // 2)
                self.state_machine.set_state(PuppyState.HAPPY)
                self.speech.show_message("Refreshed! 🐾", self.geometry().center(), 2000)

            QTimer.singleShot(3000, return_to_cursor)

        QTimer.singleShot(2500, arrive_and_drink)

    def trigger_autonomous_behavior(self):
        if hasattr(self, 'wellness'):
            self.wellness.check_wellness_reminders()

        if not self.settings.get("random_wandering", True) or self.is_paused:
            return

        state = self.state_machine.current_state
        if state in (PuppyState.SLEEP, PuppyState.SLEEP_WALK, PuppyState.EXIT_HOUSE, PuppyState.PETTED, PuppyState.BALL_CHASE, PuppyState.EAT, PuppyState.DRINK):
            return

        action = self.brain.decide_autonomous_action()
        if action == "EAT":
            self.start_eating_routine()
            return
        elif action == "DRINK":
            self.start_drinking_routine()
            return
        elif action == "SLEEP":
            self.start_sleep_routine()
            return

        r = random.random()
        if r < 0.20:
            self.state_machine.set_state(PuppyState.SIT)
        elif r < 0.35:
            self.state_machine.set_state(PuppyState.SNIFF)
        elif r < 0.50:
            self.state_machine.set_state(PuppyState.STRETCH)
        elif r < 0.70:
            self.state_machine.set_state(PuppyState.HAPPY)
            if self.settings.get("random_speech", True):
                phrases = ["woof! ♡", "hehe!", "boop!", "I'm Here! ♡", "Let's Play!", "♡"]
                self.speech.show_message(random.choice(phrases), self.geometry().center())
        else:
            self.state_machine.set_state(PuppyState.IDLE)

    def start_silent_home_routine(self):
        if self.state_machine.current_state in (PuppyState.SLEEP, PuppyState.SLEEP_WALK):
            return
        self.state_machine.set_state(PuppyState.SLEEP_WALK)

    def start_sleep_routine(self):
        if self.state_machine.current_state == PuppyState.SLEEP:
            return
        self.state_machine.set_state(PuppyState.YAWN)
        self.speech.show_message("Going home to sleep... 💤", self.geometry().center(), 2500)

        def walk_home():
            self.state_machine.set_state(PuppyState.SLEEP_WALK)

        QTimer.singleShot(1200, walk_home)

    def enter_house_sequence(self):
        self.state_machine.set_state(PuppyState.SLEEP)
        self.hide()
        self.house.set_sleeping(True)
        self.sound.play_sleep()
        self.personality.update_metrics(delta_energy=40)
        self.achievements.unlock("home_sweet_home", self.house.geometry().center())
        self.achievements.unlock("pro_napper", self.house.geometry().center())

    def wake_up_routine(self):
        if not self.house.is_sleeping_inside:
            return
        self.house.set_sleeping(False)
        door_pos = self.house.get_door_global_pos()
        self.physics.x = float(door_pos.x() - self.width() // 2)
        self.physics.y = float(door_pos.y() - self.height() // 2)
        self.move(self.physics.pos[0], self.physics.pos[1])
        self.show()

        self.state_machine.set_state(PuppyState.STRETCH)
        self.sound.play_wake()
        self.speech.show_message("Yawn~ Good Morning! ☀️", self.geometry().center(), 3000)

        def finish_wake():
            self.state_machine.set_state(PuppyState.HAPPY)
            self.sound.play_happy()

        QTimer.singleShot(1500, finish_wake)
        QTimer.singleShot(3000, lambda: self.state_machine.set_state(PuppyState.IDLE))

    def play_with_toy_routine(self):
        if self.state_machine.current_state == PuppyState.SLEEP:
            self.wake_up_routine()
        
        spawn_x = self.x() + 80
        spawn_y = self.y() + 10
        self.toy.spawn(spawn_x, spawn_y)
        self.trigger_fetch_routine()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.state_machine.set_state(PuppyState.EXCITED)
            self.sound.play_happy()
            self.speech.show_message("JUMP! 🎉 BOING!", self.geometry().center(), 2500)
            self.hearts.append([self.width() // 2, 10, 255, 1.0])
            self.hearts.append([self.width() // 2 - 15, -10, 255, 1.0])
            self.hearts.append([self.width() // 2 + 15, -10, 255, 1.0])

            def finish_jump():
                self.state_machine.set_state(PuppyState.HAPPY)

            QTimer.singleShot(1500, finish_jump)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_being_petted = True
            self.pet_start_time = time.time()
            self.state_machine.set_state(PuppyState.PETTED)
            self.sound.play_happy()
            self.hearts.append([self.width() // 2, 10, 255, 1.0])

            self.pet_count += 1
            self.personality.update_metrics(delta_affection=5, delta_happiness=5)

            if self.settings.get("affection", 60) >= 90:
                self.achievements.unlock("best_friends", self.geometry().center())
            if self.pet_count >= 10:
                self.achievements.unlock("good_boy", self.geometry().center())

            phrases = ["Hehe ❤️", "woof! ♡", "boop!", "yay!", "pet me!", "♡"]
            self.speech.show_message(random.choice(phrases), self.geometry().center())

        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if hasattr(self, 'is_being_petted') and self.is_being_petted:
                self.is_being_petted = False
                hold_duration = time.time() - getattr(self, 'pet_start_time', time.time())
                if hold_duration > 2.0:
                    self.personality.update_metrics(delta_affection=15, delta_happiness=15)
                    self.speech.show_message("Super Happy! ❤️", self.geometry().center(), 2500)
                    self.sound.play_happy()
                QTimer.singleShot(800, lambda: self.state_machine.set_state(PuppyState.IDLE))

    def update_hearts(self):
        new_h = []
        for h in self.hearts:
            h[1] -= 1.5
            h[2] -= 10
            if h[2] > 0:
                new_h.append(h)
        self.hearts = new_h

    def toggle_photo_mode(self):
        self.is_photo_mode = not self.is_photo_mode
        if self.is_photo_mode:
            self.speech.hide()

    def show_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        name = self.settings.get("puppy_name", "Milo")

        title_act = QAction(f"🐶 {name}", self)
        title_act.setEnabled(False)
        menu.addAction(title_act)

        mood_act = QAction(f"❤️ Mood: {self.personality.current_mood.value}", self)
        mood_act.setEnabled(False)
        menu.addAction(mood_act)

        menu.addSeparator()

        dnd_act = QAction("🌙 Do Not Disturb Mode", self)
        dnd_act.setCheckable(True)
        dnd_act.setChecked(not self.settings.get("follow_cursor", True))
        dnd_act.triggered.connect(lambda c: self.settings.set("follow_cursor", not c))
        menu.addAction(dnd_act)

        feed_act = QAction("🍖 Feed Puppy", self)
        feed_act.triggered.connect(self.start_eating_routine)
        menu.addAction(feed_act)

        water_act = QAction("💧 Give Water", self)
        water_act.triggered.connect(self.start_drinking_routine)
        menu.addAction(water_act)

        ball_act = QAction("🎾 Throw Ball (Fetch)", self)
        ball_act.triggered.connect(self.play_with_toy_routine)
        menu.addAction(ball_act)

        sleep_act = QAction("😴 Sleep", self)
        sleep_act.triggered.connect(self.start_sleep_routine)
        menu.addAction(sleep_act)

        wake_act = QAction("🌅 Wake Up", self)
        wake_act.triggered.connect(self.wake_up_routine)
        menu.addAction(wake_act)

        menu.addSeparator()

        rename_act = QAction("✏ Rename Puppy", self)
        rename_act.triggered.connect(self.rename_puppy_dialog)
        menu.addAction(rename_act)

        pause_text = "▶ Resume" if self.is_paused else "⏸ Pause / Rest"
        pause_act = QAction(pause_text, self)
        pause_act.triggered.connect(self.toggle_pause)
        menu.addAction(pause_act)

        color_menu = menu.addMenu("🎨 Dog Fur Color")
        for coat_name in ["Brown & Cream", "White", "Golden", "Black & White"]:
            act = QAction(coat_name, self)
            if self.settings.get("coat_style", "Brown & Cream") == coat_name:
                act.setCheckable(True)
                act.setChecked(True)
            act.triggered.connect(lambda _, c=coat_name: self.change_coat_color(c))
            color_menu.addAction(act)

        size_menu = menu.addMenu("🔍 Puppy Size")
        for sz in ["Tiny", "Small", "Normal", "Large", "Giant"]:
            act = QAction(sz, self)
            if self.settings.get("puppy_size", "Small") == sz:
                act.setCheckable(True)
                act.setChecked(True)
            act.triggered.connect(lambda _, s=sz: self.change_puppy_size(s))
            size_menu.addAction(act)

        expr_act = QAction("😊 Express Emotion", self)
        expr_act.triggered.connect(self.trigger_random_expression)
        menu.addAction(expr_act)

        menu.addSeparator()

        exit_act = QAction("❌ Exit", self)
        exit_act.triggered.connect(QApplication.quit)

        menu.exec(pos)

    def change_coat_color(self, coat_name: str):
        self.settings.set("coat_style", coat_name)
        self.anim.load_all_sprites()
        self.update()
        self.speech.show_message(f"Fur changed to {coat_name}! 🐶", self.geometry().center())

    def change_puppy_size(self, new_size: str):
        self.settings.set("puppy_size", new_size)
        self.size_scale = self.settings.size_scale
        w, h = int(72 * self.size_scale), int(72 * self.size_scale)
        self.setFixedSize(w, h)
        self.anim.load_all_sprites()
        self.speech.show_message(f"Size changed to {new_size}! 🐾", self.geometry().center())

    def trigger_random_expression(self):
        exprs = [
            (PuppyState.HAPPY, "Woof! So Happy! ♡", self.sound.play_happy),
            (PuppyState.SAD, "Aww... Sad puppy 🥺", self.sound.play_step),
            (PuppyState.EXCITED, "Yay! Let's Play! 🎉", self.sound.play_happy),
            (PuppyState.STRETCH, "Ahhh~ Stretching! 🐾", self.sound.play_step),
            (PuppyState.YAWN, "Yawn~ So comfy! 🥱", self.sound.play_wake),
            (PuppyState.SNIFF, "Sniff sniff... 🌸", self.sound.play_step),
            (PuppyState.SIT, "Sitting nicely! 🐶", self.sound.play_bark)
        ]
        state, msg, snd = random.choice(exprs)
        self.state_machine.set_state(state)
        self.speech.show_message(msg, self.geometry().center())
        snd()
        self.hearts.append([self.width() // 2, 10, 255, 1.0])
        QTimer.singleShot(2500, lambda: self.state_machine.set_state(PuppyState.IDLE))

    def rename_puppy_dialog(self):
        cur_name = self.settings.get("puppy_name", "Milo")
        new_name, ok = QInputDialog.getText(self, "Rename Puppy", "Enter cute new name:", text=cur_name)
        if ok and new_name.strip():
            self.settings.set("puppy_name", new_name.strip())
            self.house.update()
            self.speech.show_message(f"Hi! I'm {new_name.strip()}! ♡", self.geometry().center())

    def toggle_pause(self):
        self.is_paused = not self.is_paused

    def moveEvent(self, event):
        super().moveEvent(event)
        if hasattr(self, 'speech') and self.speech:
            self.speech.update_position(self.geometry().center())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        state = self.state_machine.current_state
        pixmap = self.anim.get_current_frame(state, facing_right=self.facing_right)
        painter.drawPixmap(0, 0, self.width(), self.height(), pixmap)

        if not self.is_photo_mode:
            painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
            for h in self.hearts:
                painter.setPen(QColor(255, 80, 120, max(0, h[2])))
                painter.drawText(QPoint(int(h[0]), int(h[1])), "♥")
