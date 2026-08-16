import math
import time
from PySide6.QtWidgets import QWidget, QMenu, QApplication
from PySide6.QtCore import Qt, QPoint, QTimer, QRect
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush

class BallState:
    RESTING = "RESTING"
    ROLLING = "ROLLING"
    BOUNCING = "BOUNCING"
    THROWN = "THROWN"
    AIRBORNE = "AIRBORNE"
    STOPPED = "STOPPED"
    TARGETED = "TARGETED"
    CAUGHT = "CAUGHT"
    CARRIED = "CARRIED"
    DROPPED = "DROPPED"

class ToyWindow(QWidget):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings = settings_manager

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.base_w, self.base_h = 32, 32
        self.setFixedSize(self.base_w, self.base_h)

        self.state = BallState.RESTING
        self.x_pos = 200.0
        self.y_pos = 200.0
        self.vx = 0.0
        self.vy = 0.0
        self.gravity = 0.45
        self.bounce_factor = 0.65
        self.friction = 0.95

        self.drag_start = QPoint()
        self.drag_time = 0.0
        self.is_dragging = False

        self.puppy = None

        self.physics_timer = QTimer(self)
        self.physics_timer.setInterval(16) # ~60 FPS
        self.physics_timer.timeout.connect(self.update_physics)
        self.physics_timer.start()

        self.hide()

    def spawn(self, x, y):
        self.x_pos = float(x)
        self.y_pos = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.state = BallState.RESTING
        self.move(int(self.x_pos), int(self.y_pos))
        self.show()

    def throw_ball(self, target_x, target_y, force=1.0):
        self.state = BallState.THROWN
        dx = target_x - self.x_pos
        dy = target_y - self.y_pos
        dist = max(1.0, math.hypot(dx, dy))
        spd = min(22.0, (dist * 0.12) * force)
        self.vx = (dx / dist) * spd
        self.vy = (dy / dist) * spd - 4.0 # Initial arc boost

    def update_physics(self):
        if not self.isVisible() or self.is_dragging:
            return

        screen = QApplication.primaryScreen()
        geom = screen.availableGeometry() if screen else QRect(0, 0, 1920, 1080)

        ground_y = float(geom.bottom() - self.height() - 10)

        if self.state in (BallState.THROWN, BallState.AIRBORNE, BallState.BOUNCING, BallState.ROLLING):
            # Apply gravity if airborne
            if self.y_pos < ground_y:
                self.vy += self.gravity
                self.state = BallState.AIRBORNE
            else:
                self.y_pos = ground_y
                if abs(self.vy) > 1.5:
                    self.vy = -self.vy * self.bounce_factor
                    self.state = BallState.BOUNCING
                    if self.puppy and hasattr(self.puppy, 'sound') and abs(self.vy) > 3.0:
                        self.puppy.sound.play_toy()
                else:
                    self.vy = 0.0
                    self.state = BallState.ROLLING

            # Apply rolling friction
            self.vx *= self.friction
            self.vy *= self.friction

            self.x_pos += self.vx
            self.y_pos += self.vy

            # Screen bounds clamping & bounce off screen edges
            if self.x_pos < geom.left():
                self.x_pos = float(geom.left())
                self.vx = -self.vx * self.bounce_factor
            elif self.x_pos > geom.right() - self.width():
                self.x_pos = float(geom.right() - self.width())
                self.vx = -self.vx * self.bounce_factor

            if abs(self.vx) < 0.2 and abs(self.vy) < 0.2 and self.y_pos >= ground_y:
                self.vx = 0.0
                self.vy = 0.0
                self.state = BallState.RESTING

            self.move(int(self.x_pos), int(self.y_pos))

    def center_pos(self) -> QPoint:
        return QPoint(int(self.x_pos + self.width() // 2), int(self.y_pos + self.height() // 2))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start = event.globalPosition().toPoint()
            self.drag_time = time.time()

    def mouseMoveEvent(self, event):
        if self.is_dragging and (event.buttons() & Qt.LeftButton):
            cur = event.globalPosition().toPoint()
            self.x_pos = float(cur.x() - self.width() // 2)
            self.y_pos = float(cur.y() - self.height() // 2)
            self.move(int(self.x_pos), int(self.y_pos))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            dt = max(0.05, time.time() - self.drag_time)
            release_pos = event.globalPosition().toPoint()
            dx = release_pos.x() - self.drag_start.x()
            dy = release_pos.y() - self.drag_start.y()

            # Throw strength depends on drag distance & velocity
            drag_dist = math.hypot(dx, dy)
            if drag_dist > 15:
                self.vx = max(-20.0, min(20.0, dx / (dt * 15.0)))
                self.vy = max(-20.0, min(20.0, dy / (dt * 15.0)))
                self.state = BallState.THROWN

                if self.puppy:
                    self.puppy.trigger_fetch_routine()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Contact shadow
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 40))
        painter.drawEllipse(4, self.height() - 8, self.width() - 8, 6)

        # Vibrant Tennis Ball
        painter.setPen(QPen(QColor(40, 90, 20), 1.5))
        painter.setBrush(QColor(180, 230, 40)) # Neon yellow green
        painter.drawEllipse(4, 2, self.width() - 8, self.height() - 10)

        # White seam curved line
        painter.setPen(QPen(QColor(255, 255, 255), 1.5))
        painter.drawArc(6, 4, 14, 20, 30 * 16, 120 * 16)
