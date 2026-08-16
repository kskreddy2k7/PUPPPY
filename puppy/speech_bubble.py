from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPoint, QRect, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QFont, QColor, QPen, QBrush, QPainterPath

class SpeechBubble(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.text = ""
        self.setFixedSize(130, 48)

        # Smooth Opacity Fade Effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.start_fade_out)

    def show_message(self, text: str, head_center_pos: QPoint, duration_ms: int = 3000):
        self.text = text.upper()
        self.update_position(head_center_pos)

        # 1. Pop In & Show
        self.opacity_effect.setOpacity(1.0)
        self.show()
        self.update()

        # 2. Start Idle duration timer
        self.hide_timer.start(duration_ms)

    def start_fade_out(self):
        # 5. Smooth Fade Out Animation -> Disappear
        self.fade_anim.stop()
        self.fade_anim.setDuration(400)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.finished.connect(self.hide)
        self.fade_anim.start()

    def update_position(self, head_center_pos: QPoint):
        if self.isVisible():
            self.move(head_center_pos.x() - self.width() // 2, head_center_pos.y() - self.height() - 4)

    def paintEvent(self, event):
        if not self.text:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw Crisp Pixel-Art Style Speech Bubble (matching reference sheet flow)
        path = QPainterPath()
        path.addRoundedRect(6, 4, 118, 30, 10, 10)

        # Tail pointing down to dog head
        tail_path = QPainterPath()
        tail_path.moveTo(58, 34)
        tail_path.lineTo(65, 42)
        tail_path.lineTo(72, 34)
        path.addPath(tail_path)

        # Crisp 2px black comic border & clean white background
        painter.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawPath(path)

        # Clear, high-contrast, easy-to-read bold text + emoji
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.setPen(QColor(10, 10, 15))
        text_rect = QRect(8, 5, 114, 28)
        painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, self.text)
