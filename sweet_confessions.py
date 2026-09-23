import tkinter as tk
import random
import math

# ======== CONFIG - EDIT THESE ========
CRUSH_NAME = "You"  # replace with their name
CONFESSION_TEXT = f"{CRUSH_NAME}, if there's a bug in my heart,\nthere's only one root cause: you."
QUESTION_TEXT = "Will you be my debugging partner for life?"
# ======================================

WIN_W, WIN_H = 500, 650


def rounded_rect_points(x1, y1, x2, y2, radius):
    """Build the point list for a rounded rectangle (used with create_polygon + smooth=True)."""
    return [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]


class SweetConfessionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("For You <3")
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)
        self.running = True

        # Everything - text, heart, both buttons - lives on ONE canvas.
        # That's what lets the "No" button roam absolutely anywhere in the
        # window, including right on top of the heart, instead of being
        # boxed into a small button area.
        self.main = tk.Canvas(root, width=WIN_W, height=WIN_H, bg="#1a1a2e", highlightthickness=0)
        self.main.pack(fill="both", expand=True)

        # ---- Static text ----
        self.main.create_text(
            WIN_W / 2, 55, text=CONFESSION_TEXT, fill="#ffffff",
            font=("Segoe UI", 14, "bold"), justify="center", tags="static_text"
        )
        self.main.create_text(
            WIN_W / 2, 345, text=QUESTION_TEXT, fill="#f4a6c1",
            font=("Segoe UI", 13), tags="static_text"
        )

        # ---- Heart (animated, beats via a scale pulse) ----
        self.heart_cx, self.heart_cy = WIN_W / 2, 200
        self.scale = 1.0
        self.growing = True
        self.draw_heart()
        self.animate_heart()

        # ---- YES button - resting size vs full-hover size ----
        # Tweak these two dicts to control how big/small the button gets:
        self.yes_base = {"w": 120, "h": 46, "font": 13}    # resting size
        self.yes_hover = {"w": 190, "h": 66, "font": 22}   # size at full hover
        self.yes_anim_speed = 0.22   # 0-1, how fast it eases per frame (higher = snappier)

        self.yes_cx, self.yes_cy = WIN_W / 2 - 70, 430
        self.yes_cur = dict(self.yes_base)     # current animated size (floats)
        self.yes_target = dict(self.yes_base)  # size it's easing towards

        # ---- NO button - roams randomly anywhere on the canvas ----
        self.no_size = {"w": 90, "h": 40, "font": 12}
        self.no_cx, self.no_cy = WIN_W / 2 + 90, 430

        self.draw_yes_button()
        self.draw_no_button()
        self.animate_yes_button()  # starts the smooth grow/shrink loop

        # YES: hover sets the grow target, leaving sets the shrink target, click answers
        self.main.tag_bind("yes_btn", "<Enter>", self.on_yes_enter)
        self.main.tag_bind("yes_btn", "<Leave>", self.on_yes_leave)
        self.main.tag_bind("yes_btn", "<Button-1>", lambda e: self.answer_yes())

        # NO: hover teleports it somewhere else in the whole window, and it
        # deliberately has NO click binding - it can never be pressed.
        self.main.tag_bind("no_btn", "<Enter>", self.dodge_no_button)

    # ---------- Heart, drawn with a parametric equation ----------
    def draw_heart(self):
        self.main.delete("heart")
        points = []
        steps = 100
        for i in range(steps):
            t = (i / steps) * 2 * math.pi
            x = 16 * (math.sin(t) ** 3)
            y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            x *= self.scale * 8
            y *= self.scale * 8
            points.append(self.heart_cx + x)
            points.append(self.heart_cy + y)
        self.main.create_polygon(points, fill="#e94560", outline="#ff6b81", width=2, tags="heart")
        # Keep the buttons and text visible on top, since the heart redraws
        # itself constantly and would otherwise cover whatever's underneath.
        self.main.tag_raise("static_text")
        self.main.tag_raise("yes_btn")
        self.main.tag_raise("no_btn")

    def animate_heart(self):
        if not self.running:
            return
        # Pulse effect - scale grows and shrinks
        if self.growing:
            self.scale += 0.01
            if self.scale >= 1.15:
                self.growing = False
        else:
            self.scale -= 0.01
            if self.scale <= 0.95:
                self.growing = True

        self.draw_heart()
        self.root.after(30, self.animate_heart)

    # ---------- YES button (rounded, smoothly grows/shrinks on hover) ----------
    def draw_yes_button(self):
        self.main.delete("yes_btn", "yes_txt")
        s = self.yes_cur
        cx, cy = self.yes_cx, self.yes_cy
        x1, y1 = cx - s["w"] / 2, cy - s["h"] / 2
        x2, y2 = cx + s["w"] / 2, cy + s["h"] / 2
        pts = rounded_rect_points(x1, y1, x2, y2, radius=s["h"] / 2)
        self.main.create_polygon(
            pts, smooth=True, fill="#e94560", outline="#ff6b81", width=2, tags="yes_btn"
        )
        self.main.create_text(
            cx, cy, text="Yes! 💖", fill="white",
            font=("Segoe UI", int(round(s["font"])), "bold"), tags=("yes_btn", "yes_txt")
        )

    def on_yes_enter(self, event):
        self.yes_target = dict(self.yes_hover)

    def on_yes_leave(self, event):
        self.yes_target = dict(self.yes_base)

    def animate_yes_button(self):
        if not self.running:
            return
        # Eases yes_cur towards yes_target a little bit each frame, so the
        # button glides smoothly instead of jumping straight to its size.
        changed = False
        for key in ("w", "h", "font"):
            diff = self.yes_target[key] - self.yes_cur[key]
            if abs(diff) > 0.3:
                self.yes_cur[key] += diff * self.yes_anim_speed
                changed = True
            elif self.yes_cur[key] != self.yes_target[key]:
                self.yes_cur[key] = self.yes_target[key]
                changed = True

        if changed:
            self.draw_yes_button()
            self.main.tag_raise("no_btn")  # never let it get buried under yes

        self.root.after(16, self.animate_yes_button)

    # ---------- NO button (rounded, teleports anywhere, never clickable) ----------
    def draw_no_button(self):
        self.main.delete("no_btn", "no_txt")
        s = self.no_size
        cx, cy = self.no_cx, self.no_cy
        x1, y1 = cx - s["w"] / 2, cy - s["h"] / 2
        x2, y2 = cx + s["w"] / 2, cy + s["h"] / 2
        pts = rounded_rect_points(x1, y1, x2, y2, radius=s["h"] / 2)
        self.main.create_polygon(
            pts, smooth=True, fill="#555555", outline="#777777", width=2, tags="no_btn"
        )
        self.main.create_text(
            cx, cy, text="No", fill="white",
            font=("Segoe UI", s["font"]), tags=("no_btn", "no_txt")
        )

    def dodge_no_button(self, event):
        # Teleports to a random spot ANYWHERE in the window - could land
        # beside the heart, on top of it, near the text, in a corner, etc.
        s = self.no_size
        margin = 10
        half_w, half_h = s["w"] / 2, s["h"] / 2
        self.no_cx = random.randint(int(half_w) + margin, WIN_W - int(half_w) - margin)
        self.no_cy = random.randint(int(half_h) + margin, WIN_H - int(half_h) - margin)
        self.draw_no_button()
        self.main.tag_raise("no_btn")

    # ---------- What happens after a click ----------
    def answer_yes(self):
        self.running = False  # stop the heart and yes button animations 
        self.clear_and_show("Yay! 🎉\nThanks for agreeing to be my\ndebugging partner for life!")

    def clear_and_show(self, message):
        self.main.delete("all")
        self.main.create_text(
            WIN_W / 2, WIN_H / 2, text=message, fill="#ffffff",
            font=("Segoe UI", 16, "bold"), justify="center"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = SweetConfessionApp(root)
    root.mainloop()