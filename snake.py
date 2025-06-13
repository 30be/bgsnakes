from re import A
import sys
import time
import threading
import queue
import tty
import random
from functools import cache

SIZE = 15
cell_width, cell_height = 4, 2
autoplay = True


def add(place, velocity):
    return (place[0] + velocity[0], place[1] + velocity[1])


colors = [32, 34, 35, 36, 37]
snakes = []


class Snake:
    def __init__(self):
        self.body = []
        while not self.body or any(self.body[0] in snake.body for snake in snakes):
            self.body = [(random.randint(0, SIZE - 1), random.randint(0, SIZE - 1))]
        self.velocity = (0, 1)
        self.color = random.choice(colors) if colors else 32
        if self.color in colors:
            colors.remove(self.color)

    def update(self):
        global apple
        self.body.append(
            (self.body[-1][0] + self.velocity[0], self.body[-1][1] + self.velocity[1])
        )
        if not any(apple.body in self.body for apple in apples):
            self.body.pop(0)

    def play(self):
        dist_field = [[10000 for _ in range(SIZE)] for _ in range(SIZE)]
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

        def build_df(source):
            for direction in directions:
                new = add(source, direction)
                if (
                    check(new)
                    and dist_field[source[0]][source[1]] + 1
                    < dist_field[new[0]][new[1]]
                ):
                    dist_field[new[0]][new[1]] = dist_field[source[0]][source[1]] + 1
                    build_df(new)

        for apple in apples:
            dist_field[apple.body[0]][apple.body[1]] = 0
            build_df(apple.body)

        def f(dir):
            if check(new := add(self.body[-1], dir)):
                return dist_field[new[0]][new[1]]
            return 20000

        self.velocity = min(directions, key=f)


class Apple:
    def __init__(self):
        self.body = (random.randint(0, SIZE - 1), random.randint(0, SIZE - 1))

    def update(self):
        while any(self.body in snake.body for snake in snakes):
            self.body = (random.randint(0, SIZE - 1), random.randint(0, SIZE - 1))


snakes = [Snake() for _ in range(3)]
apples = [Apple() for _ in range(3)]


def draw_snakes():
    for i in range(SIZE):
        for _ in range(cell_height):
            for j in range(SIZE):
                for snake in snakes:
                    if (i, j) in snake.body:
                        print(f"\033[1;{snake.color}m#\033[0m" * cell_width, end="")
                        break
                else:
                    if any((i, j) == a.body for a in apples):
                        print("\033[1;33m*\033[0m" * cell_width, end="")
                    else:
                        print("\033[1;31m.\033[0m" * cell_width, end="")
            print("\r")


def check(place):
    return (
        not any(place in snake.body for snake in snakes)
        and 0 <= place[0] < SIZE
        and 0 <= place[1] < SIZE
    )


@cache
def get_input():
    input_queue = queue.Queue()
    tty.setraw(sys.stdin.fileno())

    def read_input_thread():
        while True:
            try:
                input_queue.put(sys.stdin.read(1))
            except:
                return

    threading.Thread(target=read_input_thread).start()
    return lambda: input_queue.get(block=False) if input_queue.qsize() else None


def handle_input():
    global velocity, autoplay
    # if autoplay:
    # velocity = self.play()
    key = get_input()()
    if key is not None:
        # if key == "w" and self.velocity != (1, 0):
        #     velocity = (-1, 0)
        # elif key == "s" and self.velocity != (-1, 0):  # Down
        #     velocity = (1, 0)
        # elif key == "a" and self.velocity != (0, 1):  # Left
        #     velocity = (0, -1)
        # elif key == "d" and self.velocity != (0, -1):  # Right
        #     velocity = (0, 1)
        if key == "e":
            autoplay = not autoplay
        elif key == "n":
            snakes.append(Snake())
        elif key in "qcxz":
            quit()


while True:
    print("\033[0H", end="")
    for i in range(len(snakes)):
        snakes[i].play()
        if not check(add(snakes[i].body[-1], snakes[i].velocity)):
            if snakes[i].color not in colors:
                colors.append(snakes[i].color)
            del snakes[i]
            break
        snakes[i].update()
        for a in apples:
            a.update()
    draw_snakes()
    handle_input()
    time.sleep(0.05)
