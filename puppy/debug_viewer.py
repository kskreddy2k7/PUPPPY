import sys
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, QPushButton, QCheckBox
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QFont, QPixmap

from puppy.frame_pack_registry import FramePackRegistry, ANIMATION_STATE_MAPPING

class DebugAnimationViewer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🛠 Developer Animation Preview Viewer")
        self.setFixedSize(500, 480)

        self.registry = FramePackRegistry(target_height=90)
        self.current_state = "WALK"
        self.current_frame_idx = 0
        self.is_playing = True
        self.facing_right = True

        self.init_ui()

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.advance_frame)
        self.update_fps()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Header Title
        title = QLabel("🐶 Frame Pack Animation Viewer", self)
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Preview Display Box
        self.preview_box = QLabel(self)
        self.preview_box.setFixedSize(200, 160)
        self.preview_box.setStyleSheet("background-color: #222226; border: 2px solid #D48C4B; border-radius: 8px;")
        self.preview_box.setAlignment(Qt.AlignCenter)

        box_container = QHBoxLayout()
        box_container.addStretch()
        box_container.addWidget(self.preview_box)
        box_container.addStretch()
        layout.addLayout(box_container)

        # Status Label
        self.status_lbl = QLabel(self)
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
        layout.addWidget(self.status_lbl)

        # Controls Layout
        c_layout = QHBoxLayout()

        self.state_combo = QComboBox(self)
        self.state_combo.addItems(sorted(list(set(ANIMATION_STATE_MAPPING.keys()))))
        self.state_combo.setCurrentText("WALK")
        self.state_combo.currentTextChanged.connect(self.on_state_changed)
        c_layout.addWidget(self.state_combo)

        self.btn_play = QPushButton("⏸ Pause", self)
        self.btn_play.clicked.connect(self.toggle_play)
        c_layout.addWidget(self.btn_play)

        self.btn_prev = QPushButton("◀ Prev", self)
        self.btn_prev.clicked.connect(self.prev_frame)
        c_layout.addWidget(self.btn_prev)

        self.btn_next = QPushButton("Next ▶", self)
        self.btn_next.clicked.connect(self.next_frame)
        c_layout.addWidget(self.btn_next)

        layout.addLayout(c_layout)

        # Direction & FPS Controls
        f_layout = QHBoxLayout()

        self.chk_flip = QCheckBox("Flip Facing Left", self)
        self.chk_flip.toggled.connect(self.on_flip_toggled)
        f_layout.addWidget(self.chk_flip)

        f_layout.addWidget(QLabel("FPS:", self))
        self.fps_slider = QSlider(Qt.Horizontal, self)
        self.fps_slider.setRange(1, 30)
        self.fps_slider.setValue(12)
        self.fps_slider.valueChanged.connect(self.update_fps)
        f_layout.addWidget(self.fps_slider)

        self.fps_lbl = QLabel("12", self)
        f_layout.addWidget(self.fps_lbl)

        layout.addLayout(f_layout)

        # Close button
        btn_close = QPushButton("Close Viewer", self)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def on_state_changed(self, text):
        self.current_state = text
        self.current_frame_idx = 0
        self.fps_slider.setValue(self.registry.get_fps(self.current_state))
        self.update_preview()

    def on_flip_toggled(self, checked):
        self.facing_right = not checked
        self.update_preview()

    def toggle_play(self):
        self.is_playing = not self.is_playing
        self.btn_play.setText("⏸ Pause" if self.is_playing else "▶ Play")
        if self.is_playing:
            self.anim_timer.start()
        else:
            self.anim_timer.stop()

    def update_fps(self):
        fps = self.fps_slider.value()
        self.fps_lbl.setText(str(fps))
        interval = int(1000 / fps)
        self.anim_timer.setInterval(interval)
        if self.is_playing:
            self.anim_timer.start()

    def prev_frame(self):
        frames = self.registry.get_frames(self.current_state, self.facing_right)
        if frames:
            self.current_frame_idx = (self.current_frame_idx - 1) % len(frames)
            self.update_preview()

    def next_frame(self):
        frames = self.registry.get_frames(self.current_state, self.facing_right)
        if frames:
            self.current_frame_idx = (self.current_frame_idx + 1) % len(frames)
            self.update_preview()

    def advance_frame(self):
        if not self.is_playing:
            return
        frames = self.registry.get_frames(self.current_state, self.facing_right)
        if frames:
            self.current_frame_idx = (self.current_frame_idx + 1) % len(frames)
            self.update_preview()

    def update_preview(self):
        frames = self.registry.get_frames(self.current_state, self.facing_right)
        if not frames:
            return
        idx = self.current_frame_idx % len(frames)
        pix = frames[idx]
        self.preview_box.setPixmap(pix)

        fps = self.fps_slider.value()
        self.status_lbl.setText(f"State: {self.current_state} | Frame: {idx+1}/{len(frames)} | Size: {pix.width()}x{pix.height()} px | FPS: {fps}")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    viewer = DebugAnimationViewer()
    viewer.exec()
