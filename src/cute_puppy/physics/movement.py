import math

class MovementPhysics:
    def __init__(self, x=100.0, y=100.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.ax = 0.0
        self.ay = 0.0
        self.target_x = float(x)
        self.target_y = float(y)
        
        self.ground_y = float(y)
        self.friction = 0.78
        self.accel = 0.85
        self.max_speed = 12.0

        self.current_speed_category = "IDLE"

    def set_target(self, tx, ty):
        self.target_x = float(tx)
        self.target_y = float(ty)

    def update_physics(self, is_running=False, speed_factor=1.0):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        if dist > 3.0:
            nx = dx / dist
            ny = dy / dist

            target_max_speed = (10.0 if is_running else 4.5) * speed_factor
            self.ax = nx * self.accel * speed_factor
            self.ay = ny * self.accel * speed_factor

            self.vx += self.ax
            self.vy += self.ay

            current_spd = math.hypot(self.vx, self.vy)
            if current_spd > target_max_speed:
                factor = target_max_speed / current_spd
                self.vx *= factor
                self.vy *= factor
        else:
            self.vx *= 0.5
            self.vy *= 0.5
            self.ax = 0.0
            self.ay = 0.0

        self.vx *= self.friction
        self.vy *= self.friction

        self.x += self.vx
        self.y += self.vy

        speed = math.hypot(self.vx, self.vy)
        return dist, speed

    def get_speed_category(self, speed: float, cursor_vel: float) -> str:
        combined = max(speed * 30.0, cursor_vel)
        cur = self.current_speed_category

        if cur == "SPRINT":
            if combined < 260: cur = "RUN"
        elif cur == "RUN":
            if combined > 300: cur = "SPRINT"
            elif combined < 150: cur = "FAST_WALK"
        elif cur == "FAST_WALK":
            if combined > 180: cur = "RUN"
            elif combined < 80: cur = "WALK"
        elif cur == "WALK":
            if combined > 100: cur = "FAST_WALK"
            elif combined < 30: cur = "IDLE"
        else: # IDLE
            if combined > 40: cur = "WALK"

        self.current_speed_category = cur
        return cur

    @property
    def pos(self):
        return int(self.x), int(self.y)
