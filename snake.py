from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
import math, time, random
import sqlite3
import os


randint = random.randint

class GameWidget(Widget):
    def __init__(self, winx, winy, grid_size=10):
        super().__init__()

        self.winx, self.winy = winx, winy
        self.grid_size = grid_size  # Size of the grid cells
        self.gridx = winx // grid_size
        self.gridy = winy // grid_size

        Window.size = (round(self.winx*0.8), round(self.winy*0.8))

        self.__init__local()

        # Request keyboard
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_key_down)

        self.eating_sound = SoundLoader.load('eat.wav')
        self.normal_point = 5  # Points for eating normal food
        self.apple_arival_sound = SoundLoader.load('big_food.wav')
        self.full_point = 50  # Points for eating big food within time limit
        self.full_point_time_limit = 3  # Time limit for full points on big food
        self.lower_point = 10  # Points for eating big food after time limit
        self.apple_vanish_time = 10  # Time after which big food disappears
        self.apple_missed_sound = None
        self.end_game_sound = SoundLoader.load('end_game.wav')
        self.pause_duration = 8  # Duration of pause after game over

        self.update_time = 0.1
        self.update_timer = Clock.schedule_interval(self.update, self.update_time)
        # Clock.schedule_interval(self.increase_update_time, 5)

        print("Window size: ", Window.size)

    def __init__local(self):
        random.seed(time.time())  # Initialize random seed
        angle = randint(0, 3) * math.pi / 2
        self.direction = (round(math.cos(angle)), round(math.sin(angle)))

        self.snake = [(randint(0, self.gridx-1), randint(0, self.gridy-1))]
        self.snake += [(self.snake[0][0] - self.direction[0] * i, self.snake[0][1] - self.direction[1] * i) for i in range(1, 3)]
       
        self.score = 0
        self.food_count = 1
        self.spawn_food()   # Spawn initial food

        self.big_food = None
        self.big_food_timer = None
        self.big_food_start_time = None

        self.pause = False

        self.executed =  True
    
    def increase_update_time(self, df):
        self.update_time *= 0.9
        # Clock.unschedule(self.update)
        self.update_timer.cancel()
        self.update_timer = Clock.schedule_interval(self.update, self.update_time)

    def set_score_label(self, label):
        self.score_label = label

    def set_high_score_label(self, label):
        self.high_score_label = label
    
    def set_score_saver(self, saver):
        self.score_saver = saver

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_key_down)
        self._keyboard = None
    
    def on_key_down(self, keyboard, keycode, text, modifiers):
        if not self.executed: 
            return  # Too soon — ignore key

        key = keycode[1]
        if key == 'up' and self.direction != (0, -1):
            self.direction = (0, 1)
            self.executed = False
        elif key == 'down' and self.direction != (0, 1):
            self.direction = (0, -1)
            self.executed = False
        elif key == 'right' and self.direction != (-1, 0):
            self.direction = (1, 0)
            self.executed = False
        elif key == 'left' and self.direction != (1, 0):
            self.direction = (-1, 0)
            self.executed = False

    def update(self, dt):
        if self.pause:
            return
        
        # Move snake
        head_x, head_y = self.snake[0]
        dir_x, dir_y = self.direction
        new_head = ((head_x + dir_x) % self.gridx, (head_y + dir_y) % self.gridy) 
        self.snake.insert(0, new_head)
        self.executed = True
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
            # self.score_label.text = f"[color=ff0000]Game Over!\n Score: {self.score}[/color]"
            self.score_label.text = f"[color=ff0000]Game Over![/color]"
            self.pause = True
            scores = self.score_saver()  # Save highscore
            msg = f"High Score: {scores[0][0]}" if scores else ""
            msg += "\n" + f"Your Score: {self.score}"
            self.high_score_label.text = f"[color=ffffff] {msg} [/color]"
            Clock.schedule_once(self.resume, self.pause_duration)

        self.update_canvas()

    def update_canvas(self):
        self.canvas.clear()
        with self.canvas:
            Color(162/255, 159/255, 39/255)  # Border
            Rectangle(pos=(0, 0), size=Window.size)

            Color(154/255, 150/255, 38/255)  # Background
            Rectangle(pos=(2, 2), size=(self.winx-4, self.winy-4))

            Color(70/255, 36/255, 31/255)  # Snake body
            body_extra = round(0.1 * self.grid_size)  # Extra size for head circle
            for segment in self.snake[1:]:
                Ellipse(pos=(segment[0]*self.grid_size-body_extra, segment[1]*self.grid_size-body_extra), size=(self.grid_size+2*body_extra, self.grid_size+2*body_extra))  # ⭕️ Circle body

            Color(50/255, 36/255, 31/255)  # Snake head 
            head_x, head_y = self.snake[0] # Snake head position
            head_extra = round(0.3 * self.grid_size)  # Extra size for head circle
            Ellipse(pos=(head_x*self.grid_size-head_extra, head_y*self.grid_size-head_extra), size=(self.grid_size+2*head_extra, self.grid_size+2*head_extra))  # ⭕️ Circle head
            Color(1, 1, 1)  # White color for head eye
            eye_size = round(0.2 * self.grid_size) # Size of the eye
            if self.direction[1] == 0:  # Right/Left direction
                x_offset = self.grid_size-eye_size if self.direction[0] == 1 else -eye_size
                eye1 = (head_x*self.grid_size+x_offset, head_y*self.grid_size)
                eye2 = (head_x*self.grid_size+x_offset, (head_y+1)*self.grid_size - 2*eye_size)
            else :  # Up/Down direction
                y_offset = self.grid_size-eye_size if self.direction[1] == 1 else -eye_size
                eye1 = (head_x*self.grid_size, head_y*self.grid_size+y_offset, )
                eye2 = ((head_x+1)*self.grid_size - 2*eye_size, head_y*self.grid_size+y_offset, )
            Ellipse(pos=eye1, size=(2*eye_size, 2*eye_size))  # ⭕️ Circle head eye
            Ellipse(pos=eye2, size=(2*eye_size, 2*eye_size))  # ⭕️ Circle head eye
            
            if self.big_food:
                Color(1, 0.7, 0.2)
                _extra = round(0.8 * self.grid_size)
                Ellipse(pos=(self.big_food[0]*self.grid_size-_extra, self.big_food[1]*self.grid_size-_extra), size=(self.grid_size+2*_extra, self.grid_size+2*_extra))
            else:
                Color(0.5, 0.3, 0)  # Food
                _extra = round(0.2 * self.grid_size)
                Ellipse(pos=(self.food[0]*self.grid_size-_extra, self.food[1]*self.grid_size-_extra), size=(self.grid_size+2*_extra, self.grid_size+2*_extra))
            
    def resume(self, dt):
        self.__init__local()
        self.score_label.text = f"[color=ffffff]Score: {self.score}[/color]"
        self.high_score_label.text = "[color=ffffff] [/color]"

    def spawn_food(self):
        if self.food_count > 0 and self.food_count % 6 == 0:
            # Spawn big food
            if self.apple_arival_sound:
                self.apple_arival_sound.play()
            while True:
                fx = randint(1, self.gridx-2)
                fy = randint(1, self.gridy-2)
                if (fx, fy) not in self.snake:
                    break
            self.big_food = (fx, fy)
            self.big_food_start_time = Clock.get_time()
            self.big_food_timer = Clock.schedule_once(self.remove_big_food, self.apple_vanish_time)
        else:
            while True:
                fx = randint(1, self.gridx-2)
                fy = randint(1, self.gridy-2)
                if (fx, fy) not in self.snake:
                    break
            self.food = (fx, fy)

    def check_food_collision(self, head_pos): 
        # Check if the snake's head collides with food
        if self.big_food:
            if abs(head_pos[0] - self.big_food[0]) + abs(head_pos[1] - self.big_food[1]) < 2:
                if self.eating_sound:
                    self.eating_sound.play()
                self.score += (self.full_point if (Clock.get_time() - self.big_food_start_time) < self.full_point_time_limit 
                                  else round(self.full_point - (Clock.get_time()-self.big_food_start_time-self.full_point_time_limit) *(self.full_point - self.lower_point) / (self.apple_vanish_time - self.full_point_time_limit)))
                self.score_label.text = f"[color=ffffff]Score: {self.score}[/color]"
                if self.big_food_timer:
                    self.big_food_timer.cancel()
                self.food_count += 1
                self.big_food = None
                return True

        elif self.food == head_pos:
            if self.eating_sound:
                self.eating_sound.play()
            self.score += self.normal_point
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
        self.init_db()  # Initialize database for highscores

        self.final_score = 0
        win_x, win_y = 1920, 1000
        grid_size = 40

        layout = FloatLayout(size=(win_x, win_y))

        # Game area
        self.game = GameWidget(win_x, win_y, grid_size=grid_size)  # 🔹 store in self
        layout.add_widget(self.game)

        # Score label on top-right
        label = Label(text="[color=ffffff]Score: 0[/color]",
                      markup=True,
                      font_size=30,
                      size_hint=(None, None),
                      size=(140, 60),
                      pos_hint={'left': 1, 'top': 1})
        layout.add_widget(label)
        self.game.set_score_label(label)

        high_score_label = Label(
                    text="[color=ffffff] [/color]",
                    markup=True,
                    font_size=30,
                    size_hint=(None, None),
                    size=(140, 60),
                    pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Center the label
                )
        layout.add_widget(high_score_label)
        self.game.set_high_score_label(high_score_label)
        self.game.set_score_saver(self.score_saver)
        return layout

    def on_stop(self):
        self.final_score = self.game.score

    def score_saver(self):
        player_name = "Player_X" #input()  # you can use a popup or input box for name
        self.save_highscore(player_name, self.game.score)
        # Show scores
        scores = []
        for name, score in self.get_highscores():
            # print(f"{name}: {score}")
            scores.append((score, name))
        return scores
    
    def init_db(self):
        self.db_path = "highscores.db"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS highscores (
                name TEXT,
                score INTEGER
            )
        ''')
        self.conn.commit()
    
    def save_highscore(self, name, score):
        # Insert the new score
        self.cursor.execute("INSERT INTO highscores (name, score) VALUES (?, ?)", (name, score))
        self.conn.commit()

        # Keep only top 5
        self.cursor.execute("SELECT * FROM highscores ORDER BY score DESC")
        top_5 = self.cursor.fetchall()[:5]

        self.cursor.execute("DELETE FROM highscores")
        self.cursor.executemany("INSERT INTO highscores (name, score) VALUES (?, ?)", top_5)
        self.conn.commit()

    def get_highscores(self):
        self.cursor.execute("SELECT name, score FROM highscores ORDER BY score DESC LIMIT 5")
        return self.cursor.fetchall()


if __name__ == '__main__':
    # while True:
    # if True:
    app = SnakeApp()
    app.run()
    print(f"Final Score: {app.final_score}")
    if app.final_score > 100:
        print("Good Score exiting...")

            # break
