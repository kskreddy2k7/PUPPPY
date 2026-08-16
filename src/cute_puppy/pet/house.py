import os
import time
from PySide6.QtWidgets import QWidget, QMenu, QApplication
from PySide6.QtCore import Qt, QPoint, QTimer, QRect
from PySide6.QtGui import QPixmap, QPainter, QFont, QColor, QAction
from cute_puppy.platform.common import get_asset_path

ASSET_DAY = get_asset_path("house", "house.png")
ASSET_NIGHT = get_asset_path("house", "house_sleeping.png")

class HouseWindow(QWidget):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings = settings_manager

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.pixmap_day = QPixmap(ASSET_DAY)
        if self.pixmap_day.isNull(): self.pixmap_day = QPixmap(110, 110)

        self.pixmap_night = QPixmap(ASSET_NIGHT)
        if self.pixmap_night.isNull(): self.pixmap_night = QPixmap(110, 110)

        self.base_w, self.base_h = 130, 140
        self.setFixedSize(self.base_w, self.base_h)
        self.is_sleeping_inside = False
        self.is_move_mode = False
        self.zzz_frame = 0

        self.current_scale = 1.0
        self.target_scale = 1.0
        self.last_interaction = time.time()
        self.drag_start_pos = QPoint()

        self.zzz_timer = QTimer(self)
        self.zzz_timer.setInterval(600)
        self.zzz_timer.timeout.connect(self.update_zzz)

        self.collapse_timer = QTimer(self)
        self.collapse_timer.setInterval(100)
        self.collapse_timer.timeout.connect(self.update_collapse_animation)
        self.collapse_timer.start()

        self.puppy = None
        self.load_saved_position()

    def load_saved_position(self):
        saved_x = self.settings.get("home_x")
        saved_y = self.settings.get("home_y")
        screen = QApplication.primaryScreen()
        geom = screen.availableGeometry() if screen else None

        if saved_x is not None and saved_y is not None and geom:
            x = max(geom.left(), min(int(saved_x), geom.right() - self.width()))
            y = max(geom.top(), min(int(saved_y), geom.bottom() - self.height()))
            self.move(x, y)
        else:
            if geom:
                self.move(geom.left() + 40, geom.bottom() - self.height() - 40)
            else:
                self.move(100, 500)

    def save_position(self):
        self.settings.set("home_x", self.x())
        self.settings.set("home_y", self.y())

    def set_sleeping(self, sleeping: bool):
        self.is_sleeping_inside = sleeping
        if sleeping:
            self.zzz_timer.start()
        else:
            self.zzz_timer.stop()
            self.zzz_frame = 0
        self.update()

    def update_zzz(self):
        self.zzz_frame = (self.zzz_frame + 1) % 4
        self.update()

    def update_collapse_animation(self):
        if self.is_move_mode:
            self.target_scale = 1.0
        elif time.time() - self.last_interaction > 7.0:
            self.target_scale = 0.82
        else:
            self.target_scale = 1.0

        if abs(self.current_scale - self.target_scale) > 0.01:
            self.current_scale += (self.target_scale - self.current_scale) * 0.15
            self.update()

    def enterEvent(self, event):
        self.last_interaction = time.time()
        self.target_scale = 1.0

    def mousePressEvent(self, event):
        self.last_interaction = time.time()
        self.target_scale = 1.0
        if event.button() == Qt.LeftButton:
            if self.is_move_mode:
                self.drag_start_pos = event.globalPosition().toPoint() - self.pos()
            else:
                self.show_house_menu(event.globalPosition().toPoint())
        elif event.button() == Qt.RightButton:
            self.show_house_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.is_move_mode and (event.buttons() & Qt.LeftButton):
            new_pos = event.globalPosition().toPoint() - self.drag_start_pos
            self.move(new_pos)
            self.save_position()

    def toggle_move_mode(self):
        self.is_move_mode = not self.is_move_mode
        if not self.is_move_mode:
            self.save_position()
        self.update()

    def toggle_mute_sound(self):
        cur = self.settings.get("sound_enabled", True)
        self.settings.set("sound_enabled", not cur)
        msg = "Muted 🔇" if cur else "Sounds On 🔊"
        if self.puppy:
            self.puppy.speech.show_message(msg, self.geometry().center())

    def show_house_menu(self, pos: QPoint):
        menu = QMenu(self)
        name = self.settings.get("puppy_name", "Milo")

        title_act = menu.addAction(f"🏠 {name}'s Home")
        title_act.setEnabled(False)
        menu.addSeparator()

        if self.is_sleeping_inside:
            wake_act = menu.addAction("🌅 Wake Up")
            if self.puppy: wake_act.triggered.connect(self.puppy.wake_up_routine)
        else:
            sleep_act = menu.addAction("😴 Sleep")
            if self.puppy: sleep_act.triggered.connect(self.puppy.start_sleep_routine)

            call_act = menu.addAction("🐶 Call Puppy Home")
            if self.puppy: call_act.triggered.connect(self.puppy.start_sleep_routine)

            feed_act = menu.addAction("🍖 Feed Puppy")
            if self.puppy: feed_act.triggered.connect(self.puppy.start_eating_routine)

            water_act = menu.addAction("💧 Give Water")
            if self.puppy: water_act.triggered.connect(self.puppy.start_drinking_routine)

            ball_act = menu.addAction("🎾 Throw Ball (Fetch)")
            if self.puppy: ball_act.triggered.connect(self.puppy.play_with_toy_routine)

        menu.addSeparator()

        if self.puppy:
            color_menu = menu.addMenu("🎨 Dog Fur Color")
            for coat_name in ["Brown & Cream", "White", "Golden", "Black & White"]:
                act = QAction(coat_name, self)
                if self.settings.get("coat_style", "Brown & Cream") == coat_name:
                    act.setCheckable(True)
                    act.setChecked(True)
                act.triggered.connect(lambda _, c=coat_name: self.puppy.change_coat_color(c))
                color_menu.addAction(act)

            size_menu = menu.addMenu("🔍 Puppy Size")
            for sz in ["Tiny", "Small", "Normal", "Large", "Giant"]:
                act = QAction(sz, self)
                if self.settings.get("puppy_size", "Small") == sz:
                    act.setCheckable(True)
                    act.setChecked(True)
                act.triggered.connect(lambda _, s=sz: self.puppy.change_puppy_size(s))
                size_menu.addAction(act)

            expr_act = menu.addAction("😊 Express Emotion")
            expr_act.triggered.connect(self.puppy.trigger_random_expression)

            follow_act = menu.addAction("🖱 Follow Cursor")
            follow_act.setCheckable(True)
            follow_act.setChecked(self.settings.get("follow_cursor", True))
            follow_act.triggered.connect(lambda c: self.settings.set("follow_cursor", c))

            rename_act = menu.addAction("✏ Rename Puppy")
            rename_act.triggered.connect(self.puppy.rename_puppy_dialog)

            is_muted = not self.settings.get("sound_enabled", True)
            mute_txt = "🔊 Unmute Sounds" if is_muted else "🔇 Mute Sounds"
            mute_act = menu.addAction(mute_txt)
            mute_act.setCheckable(True)
            mute_act.setChecked(is_muted)
            mute_act.triggered.connect(self.toggle_mute_sound)

            settings_act = menu.addAction("⚙ Settings")
            settings_act.triggered.connect(lambda: self.puppy.request_settings_signal.emit())

        move_txt = "📌 Lock Home Position" if self.is_move_mode else "✋ Move Home Location"
        move_act = menu.addAction(move_txt)
        move_act.triggered.connect(self.toggle_move_mode)

        menu.addSeparator()
        exit_act = menu.addAction("❌ Exit App")
        exit_act.triggered.connect(QApplication.quit)

        menu.exec(pos)

    def get_door_global_pos(self) -> QPoint:
        return QPoint(self.x() + self.width() // 2, self.y() + self.height() - 25)

    def get_bowl_global_pos(self) -> QPoint:
        return QPoint(self.x() + 30, self.y() + self.height() - 20)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        painter.save()
        scale = self.current_scale
        painter.scale(scale, scale)

        pix = self.pixmap_night if self.is_sleeping_inside else self.pixmap_day
        painter.drawPixmap(10, 20, 110, 110, pix)

        puppy_name = self.settings.get("puppy_name", "Milo").upper()
        sign_text = f"{puppy_name}'S HOME"

        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        painter.setPen(QColor(90, 50, 25))

        painter.setBrush(QColor(245, 225, 190))
        painter.drawRoundedRect(QRect(15, 110, 100, 18), 4, 4)
        painter.drawText(QRect(15, 110, 100, 18), Qt.AlignCenter, sign_text)

        if self.is_move_mode:
            painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
            painter.setPen(QColor(255, 60, 40))
            painter.drawText(QRect(0, 0, self.width(), 20), Qt.AlignCenter, "✋ DRAGGABLE")

        if self.is_sleeping_inside:
            painter.setFont(QFont("Segoe UI", 12, QFont.Bold))
            painter.setPen(QColor(100, 140, 240))
            zzz_str = "Z" * ((self.zzz_frame % 3) + 1)
            y_offset = (self.zzz_frame * 3)
            painter.drawText(QPoint(75, 30 - y_offset), zzz_str + " 💤")

        painter.restore()
