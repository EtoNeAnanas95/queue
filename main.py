from tkinter import *
import time
import random
# подрубил библиотеки и создал и настроил игровое поле
tk = Tk()
tk.title("Games")
tk.resizable(0, 0)
tk.wm_attributes("-topmost", 1)
canvas = Canvas(tk, width=500, height=400, highlightthickness=0)
canvas.pack()
tk.update()
# создал класс мяча, который настраивается из нутри с помощью конструктора def
class Ball:
    def __int__(self, canvas, paddle, score, color):
        self.canvas = canvas
        self.paddle = paddle
        self.score = score
        self.id = canvas.create_oval(10, 10, 25, 25, fill=color)
        self.canvas.move(self.id, 245, 100)
        starts = [-2, -1, 1, 2]
        random.shuffle(starts)
        self.x = starts[0]
        self.y = -2
        self.canvas_height = self.canvas.winfo_height()
        self.canvas_width = self.canvas.winfo_width()
        self.hit_bottom = False
    def hit_paddle(self, pos):
        paddle_pos = self.canvas.coords(self.paddle.id)
        if pos[2] >= paddle_pos[0] and pos[0] <= paddle_pos[3]:
            if pos[3] >= paddle_pos[1] and pos [3] <= paddle_pos[3]:
                self.score.hit()
                return True
        return False
    def draw(self):
        self.canvas.move(self.id, self.x, self.y)
        pos = self.canvas.coords(self.id)
        if pos[1] <= 0:
            self.y = 2
        if pos[3] >= self.canvas_height:
            self.hit_bottom = True
            canvas.create_text(250, 120, text="Вы проиграли", font=("courier", 30), fill="red")
        if self.hit_paddle(pos) == True:
            self.y = -2
        if pos[0] <= 0:
            self.x = 2
        if pos[2] >= self.canvas_width:
            self.x = -2
#  Описываем класс Paddle, который отвечает за платформы
class Paddle:
    def __init__(self, canvas, color):
        self.canvas = canvas
        # создаём прямоугольную платформу 10 на 100 пикселей, закрашиваем выбранным цветом и получаем её внутреннее имя
        self.id = canvas.create_rectangle(0, 0, 100, 10, fill=color)
        # задаём список возможных стартовых положений платформы
        start_1 = [40, 60, 90, 120, 150, 180, 200]
        # перемешиваем их
        random.shuffle(start_1)
        # выбираем первое из перемешанных
        self.starting_point_x = start_1[0]
        # перемещаем платформу в стартовое положение
        self.canvas.move(self.id, self.starting_point_x, 300)
        # пока платформа никуда не движется, поэтому изменений по оси х нет
        self.x = 0
        # платформа узнаёт свою ширину
        self.canvas_width = self.canvas.winfo_width()
        # задаём обработчик нажатий
        # если нажата стрелка вправо — выполняется метод turn_right()
        self.canvas.bind_all('<KeyPress-Right>', self.turn_right)
        # если стрелка влево — turn_left()
        self.canvas.bind_all('<KeyPress-Left>', self.turn_left)
        # пока игра не началась, поэтому ждём
        self.started = False
        # как только игрок нажмёт Enter — всё стартует
        self.canvas.bind_all('<KeyPress-Return>', self.start_game)
    # движемся вправо
    def turn_right(self, event):
        # будем смещаться правее на 2 пикселя по оси х
        self.x = 2
    # движемся влево
    def turn_left(self, event):
        # будем смещаться левее на 2 пикселя по оси х
        self.x = -2
    # игра начинается
    def start_game(self, event):
        # меняем значение переменной, которая отвечает за старт
        self.started = True
    # метод, который отвечает за движение платформы
    def draw(self):
        # сдвигаем нашу платформу на заданное количество пикселей
        self.canvas.move(self.id, self.x, 0)
        # получаем координаты холста
        pos = self.canvas.coords(self.id)
        # если мы упёрлись в левую границу
        if pos[0] <= 0:
            # останавливаемся
            self.x = 0
        # если упёрлись в правую границу
        elif pos[2] >= self.canvas_width:
            # останавливаемся
            self.x = 0


#  Описываем класс Score, который отвечает за отображение счетов
class Score:
    # конструктор
    def __init__(self, canvas, color):
        # в самом начале счёт равен нулю
        self.score = 0
        # будем использовать наш холст
        self.canvas = canvas
        # создаём надпись, которая показывает текущий счёт, делаем его нужно цвета и запоминаем внутреннее имя этой надписи
        self.id = canvas.create_text(450, 10, text=self.score, font=('Courier', 15), fill=color)

    # обрабатываем касание платформы
    def hit(self):
        # увеличиваем счёт на единицу
        self.score += 1
        # пишем новое значение счёта
        self.canvas.itemconfig(self.id, text=self.score)
# создаём объект — зелёный счёт
score = Score(canvas, 'green')
# создаём объект — белую платформу
paddle = Paddle(canvas, 'White')
# создаём объект — красный шарик
ball = Ball(canvas, paddle, score, 'red')
# пока шарик не коснулся дна
while not ball.hit_bottom:
    # если игра началась и платформа может двигаться
    if paddle.started == True:
        # двигаем шарик
        ball.draw()
        # двигаем платформу
        paddle.draw()
    # обновляем наше игровое поле, чтобы всё, что нужно, закончило рисоваться
    tk.update_idletasks()
    # обновляем игровое поле, и смотрим за тем, чтобы всё, что должно было быть сделано — было сделано
    tk.update()
    # замираем на одну сотую секунды, чтобы движение элементов выглядело плавно
    time.sleep(0.01)
# если программа дошла досюда, значит, шарик коснулся дна. Ждём 3 секунды, пока игрок прочитает финальную надпись, и завершаем игру
time.sleep(3)