from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from math import hypot
import math, time, random

randint = random.randint


class GameWidget(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

        self.winx, self.winy = args[0], args[1]

        Window.size = (self.winx, self.winy)

        self.__init__local()

        # Request keyboard
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_key_down)

        self.eating_sound = SoundLoader.load('eat.wav')
        self.apple_arival_sound = SoundLoader.load('big_food.wav')
        self.end_game_sound = SoundLoader.load('end_game.wav')
        self.apple_missed_sound = None

        Clock.schedule_interval(self.update, 0.1)
        print("Window size: ", Window.size)

    def __init__local(self):
        random.seed(time.time())  # Initialize random seed
        angle = randint(0, 3) * math.pi / 2
        self.direction = (round(10 * math.cos(angle)), round(10 * math.sin(angle)))

        self.snake = [(randint(0, (self.winx - 5) // 10)*10, randint(0, (self.winy - 5) // 10)*10)]
        self.snake += [(self.snake[0][0] - self.direction[0] * i, self.snake[0][1] - self.direction[1] * i) for i in range(1, 3)]
        self.food = (randint(0, (self.winx - 5) // 10)*10, randint(0, (self.winy - 5) // 10)*10)

        self.score = 0
        self.food_count = 1
        self.big_food = None
        self.big_food_timer = None
        self.big_food_start_time = None

        self.pause = False

        self.executed = 3  # Used to track key execution 
                           # binary 11 means calculation and canvas update both executed

    def set_score_label(self, label):
        self.score_label = label

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_key_down)
        self._keyboard = None
    
    def on_key_down(self, keyboard, keycode, text, modifiers):
        if self.executed != 3: #now - self.last_key_time < self.debounce_time:
            return  # Too soon — ignore key

        key = keycode[1]
        if key == 'up' and self.direction != (0, -10):
            self.direction = (0, 10)
        elif key == 'down' and self.direction != (0, 10):
            self.direction = (0, -10)
        elif key == 'right' and self.direction != (-10, 0):
            self.direction = (10, 0)
        elif key == 'left' and self.direction != (10, 0):
            self.direction = (-10, 0)

        self.executed = 0  # Does not Allow next key press until the current one is executed


    def update(self, dt):
        if self.pause:
            return
        
        # Move snake
        head_x, head_y = self.snake[0]
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x) % self.winx, (head_y + dir_y) % self.winy) 
        self.snake.insert(0, new_head)
        self.executed |= 1  # Increment executed count
        # Check food collision
        if self.check_food_collision(new_head):
            self.spawn_food()
            # Keep tail (grow)
        else:
            self.snake.pop()  # Normal move (no growth)

        if new_head in self.snake[1:]:  # Check self-collision
            if self.end_game_sound:
                self.end_game_sound.play()
            self.update_canvas()
            self.score_label.text = f"[color=ff0000]Game Over!\n Score: {self.score}[/color]"
            self.pause = True
            Clock.schedule_once(self.resume, 5)

        self.update_canvas()

    def update_canvas(self):
        self.canvas.clear()
        with self.canvas:
            Color(162/255, 159/255, 39/255)  # Border
            Rectangle(pos=(0, 0), size=Window.size)

            Color(154/255, 150/255, 38/255)  # Background
            Rectangle(pos=(2, 2), size=(self.winx-4, self.winy-4))

            Color(50/255, 36/255, 31/255)  # Snake
            for segment in self.snake:
                Ellipse(pos=(segment[0]-1, segment[1]-1), size=(12, 12))  # ⭕️ Circle body
            self.executed |= 2  # Increment executed count

            Color(0.5, 0.3, 0)  # Food
            if self.big_food:
                Color(1, 0.7, 0.2)
                Ellipse(pos=self.big_food, size=(30, 30))
            else:
                Ellipse(pos=(self.food[0]-2, self.food[1]-2), size=(14, 14))  # ⭕️ Circular food
    def resume(self, dt):
        self.__init__local()
        self.score_label.text = f"[color=ffffff]Score: {self.score}[/color]"

    def spawn_food(self):
        if self.food_count > 0 and self.food_count % 6 == 0:
            # Spawn big food
            if self.apple_arival_sound:
                self.apple_arival_sound.play()
            while True:
                fx = randint(0, (self.winx - 15) // 10) * 10
                fy = randint(0, (self.winy - 15) // 10) * 10
                if (fx, fy) not in self.snake:
                    break
            self.big_food = (fx, fy)
            self.big_food_start_time = Clock.get_time()
            self.big_food_timer = Clock.schedule_once(self.remove_big_food, 10)
        else:
            while True:
                fx = randint(0, (self.winx - 5) // 10) * 10
                fy = randint(0, (self.winy - 5) // 10) * 10
                if (fx, fy) not in self.snake:
                    break
            self.food = (fx, fy)


    def check_food_collision(self, head_pos):
        hx, hy = head_pos
        if self.big_food:
            if hypot(hx - 10 - self.big_food[0], hy - 10 - self.big_food[1]) < 15:
                if self.eating_sound:
                    self.eating_sound.play()
                self.score += (50 if (Clock.get_time() - self.big_food_start_time) < 3 
                                  else round(50-(Clock.get_time()-self.big_food_start_time-3)*40/7))
                self.score_label.text = f"[color=ffffff]Score: {self.score}[/color]"
                self.food_count += 1
                self.big_food = None
                if self.big_food_timer:
                    self.big_food_timer.cancel()
                return True

        elif hypot(hx - self.food[0], hy - self.food[1]) < 5:
            if self.eating_sound:
                self.eating_sound.play()
            self.score += 5
            self.food_count += 1
            self.score_label.text = f"[color=ffffff]Score: {self.score}[/color]"
            return True
        return False
    
    def remove_big_food(self, dt):
        if self.apple_missed_sound:
            self.apple_missed_sound.play()
        self.big_food = None
        self.food_count += 1
        print("IN remove big food")
        self.spawn_food()


class SnakeApp(App):
    def build(self):

        win_x, win_y = 320, 400

        layout = FloatLayout(size=(win_x, win_y))

        # Game area
        game = GameWidget(win_x, win_y)

        layout.add_widget(game)

        # Score label on top-right
        label = Label(text="[color=ffffff]Score: 0[/color]",
                      markup=True,
                      font_size=30,
                      size_hint=(None, None),
                      size=(140, 60),
                      pos_hint={'right': 1, 'top': 1})
        layout.add_widget(label)
        game.set_score_label(label)

        return layout

if __name__ == '__main__':
    SnakeApp().run()
    # print(randint(0, 2))
