from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from math import hypot
from random import randint

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snake = [(100, 100), (90, 100), (80, 100)]
        self.direction = (10, 0)
        self.food = (200, 200)
        self.score = 0

        self.eat_sound = SoundLoader.load("eat.wav")

        # Request keyboard
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_key_down)

        Clock.schedule_interval(self.update, 0.2)

    def set_score_label(self, label):
        self.score_label = label

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_key_down)
        self._keyboard = None

    def on_key_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]
        if key == 'up' and self.direction != (0, -10):
            self.direction = (0, 10)
        elif key == 'down' and self.direction != (0, 10):
            self.direction = (0, -10)
        elif key == 'right' and self.direction != (-10, 0):
            self.direction = (10, 0)
        elif key == 'left' and self.direction != (10, 0):
            self.direction = (-10, 0)

    def check_food_collision(self, head_pos):
        hx, hy = head_pos
        fx, fy = self.food
        if hypot(hx - fx, hy - fy) < 2:
            if self.eat_sound:
                self.eat_sound.play()
            self.score += 5
            self.score_label.text = f"[color=ffffff]Score: {self.score}[/color]"
            return True
        return False

    def spawn_food(self):
        self.food = (randint(0, 29) * 10, randint(0, 39) * 10)

    def update(self, dt):
        # Move snake
        head_x, head_y = self.snake[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        self.snake.insert(0, new_head)

        if self.check_food_collision(new_head):
            self.spawn_food()
        else:
            self.snake.pop()

        # Redraw
        self.canvas.clear()
        with self.canvas:
            Color(0, 0.1, 0.1)
            Rectangle(pos=(0, 0), size=Window.size)
            Color(0, 1, 0)
            for segment in self.snake:
                Rectangle(pos=segment, size=(10, 10))
            Color(1, 0, 0)
            Rectangle(pos=self.food, size=(10, 10))


class SnakeApp(App):
    def build(self):
        layout = FloatLayout()

        # Game area
        game = GameWidget()
        layout.add_widget(game)

        # Score label on top-right
        label = Label(text="[color=ffffff]Score: 0[/color]",
                      markup=True,
                      font_size=20,
                      size_hint=(None, None),
                      size=(140, 40),
                      pos_hint={'right': 1, 'top': 1})
        layout.add_widget(label)
        game.set_score_label(label)

        return layout

if __name__ == '__main__':
    SnakeApp().run()
