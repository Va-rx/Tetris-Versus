import sys

import time
from button import Button
from settings import *

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Tetris Versus")

press_event_active = False  # potrzebne do funkcji
fliped = False
flip_timer = time.time()
changed1_keys_timer, changed2_keys_timer = time.time(), time.time()


class Figure:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        if random.random() < SPECIAL_FIGURE_PERCENTAGE:
            figure = random.choice(list(SPECIAL_FIGURES))
            self.type = TYPE_FIGURE.SPECIAL
            self.special_type = figure
        else:
            figure = NORMAL_FIGURES()
            self.type = TYPE_FIGURE.NORMAL
            self.special_type = None
        if random.random() < NON_ROTATIVE_PERCENTAGE:
            self.rotative = "non_rotative"
        else:
            self.rotative = "rotative"
        self.base = figure.base
        self.color = figure.color

    #  Obracanie figury
    def rotate(self):
        if self.rotative == "non_rotative":
            return
        pivot = PIVOT_POS
        positions = []
        result = []
        for num in self.base:
            positions.append((num % 5, num // 5))
        for pos in positions:
            x, y = pos
            new_x = 2 - (y - pivot[1])
            new_y = 2 + (x - pivot[0])
            result.append(5 * new_y + new_x)
        self.base = result


class Tetris:
    def __init__(self, height, width, map, id, nick):
        self.height = height
        self.width = width
        self.id = id

        self.isBridge = False

        self.x = MAP_SET_X
        self.y = MAP_SET_Y

        self.field = map

        self.bridge_start = BRIDGE_START
        self.bridge_end = BRIDGE_END
        self.bridge_width = BRIDGE_WIDTH

        self.speed = SPEED

        self.nick = nick

        self.going = True
        self.figure = None

    def new_figure(self, ind):
        if ind == 0:
            self.figure = Figure(3, 0)
        else:
            self.figure = Figure(17, 0)

    def can_bridge(self, x, y):
        if y > self.height - 1 or \
                x > 2 * self.width + 3 or \
                x < 0 or \
                (x > self.width - 1 and x < self.width + self.bridge_width) and (
                y < self.bridge_start or y > self.bridge_end) or \
                self.field[y][x] != 0:
            return True

    def can_not_bridge(self, x, y):
        if y > self.height - 1 or \
                x > 2 * self.width + 3 or \
                x < 0 or \
                (x > self.width - 1) and (x < self.width + self.bridge_width) or \
                self.field[y][x] != 0:
            return True

    def inters(self):
        for i in range(5):
            for j in range(5):
                if i * 5 + j in self.figure.base:
                    if (self.figure.type == TYPE_FIGURE.SPECIAL) and self.isBridge:
                        if self.can_bridge(j + self.figure.x, i + self.figure.y):
                            return True
                    else:
                        if self.can_not_bridge(j + self.figure.x, i + self.figure.y):
                            return True
        return False

    def part_clear(self, start_point):
        for i in range(1, self.height):
            flag = True
            for j in range(start_point, start_point + self.width):
                if self.field[i][j] == 0 or self.field[i][j] == SPECIAL_FIGURES_COLORS.GRAY:
                    flag = False
                    break
            if flag:
                if self is game1:
                    game1.speed += 2
                    game2.speed -= 2
                else:
                    game1.speed -= 2
                    game2.speed += 2
                color = self.field[i][start_point]
                x2speed = True
                for i1 in range(i, 1, -1):
                    for j in range(start_point, start_point + self.width):
                        if self.field[i1][j] != color:
                            x2speed = False
                        self.field[i1][j] = self.field[i1 - 1][j]
                if x2speed:
                    if self is game1:
                        game1.speed += 3
                        game2.speed -= 3
                    else:
                        game1.speed -= 3
                        game2.speed += 3
                else:
                    if self is game1:
                        game1.speed += 2
                        game2.speed -= 2
                    else:
                        game1.speed -= 2
                        game2.speed += 2


    def break_lines(self):
        self.part_clear(0)
        self.part_clear(self.width + self.bridge_width)


    def drop(self):
        while not self.inters():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def fall(self):
        self.figure.y += 1
        if self.inters():
            self.figure.y -= 1
            self.freeze()

    def bomb_explosion(self, x, y):
        for a in range(3):
            for b in range(3):
                if y - 1 + a >= 0 and x - 1 + b >= 0 and y - 1 + a < self.height and x - 1 + b < 2 * self.width + self.bridge_width:
                    self.field[y - 1 + a][x - 1 + b] = 0

    def freeze(self):
        for i in range(5):
            for j in range(5):
                if i * 5 + j in self.figure.base:
                    if self.figure.special_type == SPECIAL_FIGURES.S_BOMB:
                        self.bomb_explosion(j + self.figure.x, i + self.figure.y)
                    else:
                        self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        if self.figure.special_type != SPECIAL_FIGURES.S_BOMB:
            self.break_lines()
        self.new_figure(self.id)
        if self.inters():
            self.going = False

    def move(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.inters():
            self.figure.x = old_x

    def rotate(self):
        old_fig = self.figure.base
        self.figure.rotate()
        if self.inters():
            self.figure.base = old_fig


def create_new_object(game):
    if game.figure is None:
        game.new_figure(game.id)


def create_map(game):
    for i in range(game.height):
        for j in range(game.width):
            pygame.draw.rect(screen, GRAY, [game.x + TILE * j, game.y + TILE * i, TILE, TILE], 1)
    for i in range(game.height):
        for j in range(game.bridge_width + game.width, game.bridge_start + 2 * game.width):
            pygame.draw.rect(screen, GRAY, [game.x + TILE * j, game.y + TILE * i, TILE, TILE], 1)
    if game.isBridge:
        for i in range(game.bridge_start, game.bridge_end + 1):
            for j in range(game.width, game.bridge_start + game.width):
                pygame.draw.rect(screen, GRAY, [game.x + TILE * j, game.y + TILE * i, TILE, TILE], 1)
    

def handle_movement(event, keys, game):
    global press_event_active, board2_reversed, board1_reversed, changed1_keys_timer, changed2_keys_timer  # , KEYS1_NOW,KEYS2_NOW
    if event.type == pygame.KEYDOWN:
        if event.key == keys[1]:
            game.drop()
        if event.key == keys[0]:
            game.rotate()
        if event.key == keys[2]:
            game.move(-1)
        if event.key == keys[3]:
            game.move(1)

        if event.key == SP_KEY1 and press_event_active:
            press_event_active = False
            changed2_keys_timer = time.time() + CHANGED_KEYS_TIME
            change_keys(KEYS2_NOW)
        if event.key == SP_KEY2 and press_event_active:
            press_event_active = False
            changed1_keys_timer = time.time() + CHANGED_KEYS_TIME
            change_keys(KEYS1_NOW)


def actual_figure(game):
    global fliped
    whole_width = 2 * game.width + game.bridge_width
    if game.figure is not None:
        for i in range(5):
            for j in range(5):
                p = i * 5 + j
                if p in game.figure.base:
                    if fliped:
                        block=pygame.draw.rect(screen, game.figure.color.value,
                                        [game.x + TILE * (whole_width-(j + game.figure.x) - 1) + 1,
                                        game.y + TILE * (i + game.figure.y) + 1,
                                        TILE - 2, TILE - 2])
                    else:
                        block=pygame.draw.rect(screen, game.figure.color.value,
                                        [game.x + TILE * (j + game.figure.x) +1,
                                        game.y + TILE * (i + game.figure.y) + 1,
                                        TILE - 2, TILE - 2])
                    if game.figure.rotative == "non_rotative":
                        pygame.draw.rect(screen, (255, 51, 255), block, width=3)


def whole_figures(game):
    global fliped
    whole_width = 2 * game.width + game.bridge_width
    for i in range(game.height):
        for j in range(2 * game.width + game.bridge_width):
            if game.field[i][j] != 0:
                if fliped:
                    pygame.draw.rect(screen, game.field[i][j].value,
                                    [game.x + TILE * (whole_width - (j+1)) + 1 , game.y + TILE * i + 1, TILE - 2, TILE - 1])
                else:
                    pygame.draw.rect(screen, game.field[i][j].value,
                                    [game.x + TILE * j + 1 , game.y + TILE * i + 1, TILE - 2, TILE - 1])


def open_close_bridge(game, is_bridge_opened):
    if is_bridge_opened:
        for i in range(game.bridge_start, game.bridge_end):
            for j in range(game.width, game.width + game.bridge_width):
                game.field[i][j] = 0
        return False
    else:
        return True


def decide_about_event():
    if random.random() < 0.03:
        return True
    return False


def new_press_event():
    new_x = random.randint(0, 725)
    new_y = random.randint(0, 575)
    return new_x, new_y


def change_keys(keys):
    random.shuffle(keys)

def decide_about_event2():
    global flip_timer
    if random.random() < 0.01:
        flip_timer = time.time() + FLIP_EVENT_TIME
        return True
    return False

def play(nick1, nick2):
    global press_event_active, event_x, event_y, changed1_keys_timer, changed2_keys_timer, KEYS1_NOW, KEYS2_NOW,flip_timer,fliped
    clock = pygame.time.Clock()
    MAP = [[0 for _ in range(2 * MAP_WIDTH + BRIDGE_WIDTH)] for _ in range(MAP_HEIGHT)]
    global game1
    global game2
    game1 = Tetris(MAP_HEIGHT, MAP_WIDTH, MAP, 0, nick1)
    game2 = Tetris(MAP_HEIGHT, MAP_WIDTH, MAP, 1, nick2)


    run = True
    counter = 0
    font = pygame.font.SysFont('Calibri', 25, True, False)
    text_event = font.render("Press!", True, BLACK)
    press_event_active = False
    event_x, event_y = 0, 0
    counter1, counter2 = 0, 0

    # Bridge
    bridge_timer = time.time() + BRIDGE_TIME

    while run:
        # Tworzenie nowej figury
        create_new_object(game1)
        create_new_object(game2)

        # mierzanie czasu
        clock.tick(FPS)
        current_time = time.time()

        if current_time >= bridge_timer:
            game1.isBridge = game2.isBridge = open_close_bridge(game1, game1.isBridge)
            #   print(game1.isBridge)
            bridge_timer = current_time + BRIDGE_TIME

        if current_time >= changed1_keys_timer:
            KEYS1_NOW = PLAYER1_KEYS.copy()
        if current_time >= changed2_keys_timer:
            KEYS2_NOW = PLAYER2_KEYS.copy()
        if current_time >= flip_timer:
            fliped = False

        counter += 1
        if counter > SPEED:
            counter = 0

        # if counter % SPEED == 1 and game1.going and game2.going:
        #     game1.fall()
        #     game2.fall()
        counter1 += 1
        counter2 += 1
        if counter1 > game1.speed:
            counter1 = 0
        if counter2 > game2.speed:
            counter2 = 0
        if counter1 % game1.speed == 1 and game1.going and game2.going:
            game1.fall()
        if counter2 % game2.speed == 1 and game1.going and game2.going:
            game2.fall()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            handle_movement(event, KEYS1_NOW, game1)
            handle_movement(event, KEYS2_NOW, game2)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                main_menu()

        screen.fill(WHITE)

        create_map(game1)
        whole_figures(game1)
        actual_figure(game1)
        actual_figure(game2)

        if press_event_active:
            screen.blit(text_event, [event_x, event_y])
        else:
            if counter % SPEED == 1 and game1.going and game2.going:
                press_event_active = decide_about_event()
                if press_event_active:
                    event_x, event_y = new_press_event()

        if not fliped:
            if counter % SPEED == 1 and game1.going and game2.going:
                fliped = decide_about_event2()

        if not game1.going or not game2.going:
            run = False
            # wyswietl kto wygral!!!
            font = pygame.font.SysFont('Calibri', 50, True, False)
            if not game2.going:
                text = font.render("Wygrał {}".format(game1.nick), True, WHITE)
                prepend_to_file(game1.nick + ', ' + game2.nick)
            else:
                text = font.render("Wygrał {}".format(game2.nick), True, WHITE)
                prepend_to_file(game2.nick + ', ' + game1.nick)
            screen.blit(pygame.image.load("assets/background.jpg"), (-40, 0))
            screen.blit(text, [265,80])
            pygame.display.update()
            time.sleep(5)
            main_menu()

        pygame.display.update()

    pygame.quit()


def main_menu():
    while True:
        screen.blit(pygame.image.load("assets/background.jpg"), (-40, 0))

        menu_mouse_pos = pygame.mouse.get_pos()

        play_button = Button(image=pygame.image.load("assets/button.png"), pos=(390, 110), text_input="PLAY",
                             font=pygame.font.SysFont('Arial', 60),
                             base_color="#00CC66", hover_color="#00FF80")
        settings_button = Button(image=pygame.image.load("assets/button.png"), pos=(390, 250), text_input="RULES",
                                 font=pygame.font.SysFont('Arial', 60),
                                 base_color="#00CC66", hover_color="#00FF80")
        scoreboard_button = Button(image=pygame.image.load("assets/button.png"), pos=(390, 390), text_input="SCOREBOARD",
                                   font=pygame.font.SysFont('Arial', 60),
                                   base_color="#00CC66", hover_color="#00FF80")
        controls_button = Button(image=pygame.image.load("assets/button.png"), pos=(390, 530), text_input="CONTROLS",
                                   font=pygame.font.SysFont('Arial', 60),
                                   base_color="#00CC66", hover_color="#00FF80")

        for button in [play_button, settings_button, scoreboard_button, controls_button]:
            button.change_color(menu_mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.check_for_input(menu_mouse_pos):
                    insert_names()
                if settings_button.check_for_input(menu_mouse_pos):
                    settings()
                if scoreboard_button.check_for_input(menu_mouse_pos):
                    scoreboard()
                if controls_button.check_for_input(menu_mouse_pos):
                    controls_menu()
        pygame.display.update()


def insert_names():
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 32)

    input_box1_color = pygame.Color('lightskyblue3')
    input_box2_color = pygame.Color('lightskyblue3')

    user1_nick = ''
    user2_nick = ''

    input_box1_active = False
    input_box2_active = False

    while True:
        screen.fill((30, 30, 30))

        menu_mouse_pos = pygame.mouse.get_pos()

        play_button = Button(image=pygame.image.load("assets/button.png"), pos=(390, 110), text_input="PLAY",
                             font=pygame.font.SysFont('Arial', 60),
                             base_color="#00CC66", hover_color="#00FF80")
        play_button.change_color(menu_mouse_pos)
        play_button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.check_for_input(menu_mouse_pos):
                    play(user1_nick, user2_nick)
                input_box1_rect = pygame.draw.rect(screen, input_box1_color, pygame.Rect(390, 200, 140, 32), 2)
                input_box2_rect = pygame.draw.rect(screen, input_box2_color, pygame.Rect(390, 240, 140, 32), 2)

                if input_box1_rect.collidepoint(event.pos):
                    input_box1_active = not input_box1_active
                else:
                    input_box1_active = False

                if input_box2_rect.collidepoint(event.pos):
                    input_box2_active = not input_box2_active
                else:
                    input_box2_active = False

            if event.type == pygame.KEYDOWN:
                if input_box1_active:
                    if event.key == pygame.K_BACKSPACE:
                        user1_nick = user1_nick[:-1]
                    else:
                        user1_nick += event.unicode

                if input_box2_active:
                    if event.key == pygame.K_BACKSPACE:
                        user2_nick = user2_nick[:-1]
                    else:
                        user2_nick += event.unicode

        input_box1_rect = pygame.draw.rect(screen, input_box1_color, pygame.Rect(390, 200, 140, 32), 2)
        input_box2_rect = pygame.draw.rect(screen, input_box2_color, pygame.Rect(390, 240, 140, 32), 2)

        txt_surface1 = font.render(user1_nick, True, pygame.Color('white'))
        txt_surface2 = font.render(user2_nick, True, pygame.Color('white'))

        screen.blit(txt_surface1, (input_box1_rect.x + 5, input_box1_rect.y + 5))
        screen.blit(txt_surface2, (input_box2_rect.x + 5, input_box2_rect.y + 5))

        label_font = pygame.font.Font(None, 32) # font for the labels
        label1 = label_font.render("Gracz 1: ", True, pygame.Color('white'))
        label2 = label_font.render("Gracz 2: ", True, pygame.Color('white'))

        screen.blit(label1, (input_box1_rect.x - 100, input_box1_rect.y + 5))
        screen.blit(label2, (input_box2_rect.x - 100, input_box2_rect.y + 5))

        input_box1_rect.w = max(50, txt_surface1.get_width() + 10)
        input_box2_rect.w = max(50, txt_surface2.get_width() + 10)

        pygame.display.flip()

def make_text(key):
    font = pygame.font.SysFont('Calibri', 25, True, False)
    try:
        character = chr(key)
    except ValueError:
        character = " "
    return font.render(character, True, WHITE)
    
def controls_menu():
    global PLAYER1_KEYS,PLAYER2_KEYS,SP_KEY2,SP_KEY1
    font = pygame.font.SysFont('Calibri', 25, True, False)
    text1 = font.render("Podstawowe przyciski gracza pierwszego to W, S, A, D oraz 1.", True, WHITE)
    text2 = font.render("Podstawowe przyciski gracza pierwszego to strzałki oraz enter.", True, WHITE)
    text3 = font.render("Ustawienie przycisków gracza 1:", True, WHITE)
    text4 = font.render("Ustawienie przycisków gracza 2:", True, WHITE)
    font = pygame.font.SysFont('Calibri', 22, True, False)
    text5 = font.render("Aby ustawić wciśnij przycisk, a następnie klawisz który ma zostać ustawiony.", True, WHITE)
    text6 = make_text(PLAYER1_KEYS[0])
    text7 = make_text(PLAYER1_KEYS[1])
    text8 = make_text(PLAYER1_KEYS[2])
    text9 = make_text(PLAYER1_KEYS[3])
    text10 = make_text(SP_KEY1)
    text11 = make_text(PLAYER2_KEYS[0])
    text12 = make_text(PLAYER2_KEYS[1])
    text13 = make_text(PLAYER2_KEYS[2])
    text14 = make_text(PLAYER2_KEYS[3])
    text15 = make_text(SP_KEY2)
    while True:
        screen.blit(pygame.image.load("assets/background.jpg"), (-40, 0))
        screen.blit(text1, [80,80])
        screen.blit(text2, [80,110])
        screen.blit(text3, [20,170])
        screen.blit(text4, [460,170])
        screen.blit(text5, [80,560])
        screen.blit(text6, [280,220])
        screen.blit(text7, [280,290])
        screen.blit(text8, [280,360])
        screen.blit(text9, [280,430])
        screen.blit(text10, [280,500])
        screen.blit(text11, [730,220])
        screen.blit(text12, [730,290])
        screen.blit(text13, [730,360])
        screen.blit(text14, [730,430])
        screen.blit(text15, [730,500])
        
        menu_mouse_pos = pygame.mouse.get_pos()
        back_button = Button(image=pygame.image.load("assets/smaller_button.png"), pos=(700, 35),
                                   text_input="BACK",
                                   font=pygame.font.SysFont('Arial', 60),
                                   base_color="#00CC66", hover_color="#00FF80")
        up1_button = Button(image=pygame.image.load("assets/smaller_button.png"), pos=(160, 230),
                                   text_input="UP",
                                   font=pygame.font.SysFont('Arial', 60),
                                   base_color="#00CC66", hover_color="#00FF80")
        down1_button = Button(image=pygame.image.load("assets/smaller_button.png"), pos=(160, 300),
                                   text_input="DOWN",
                                   font=pygame.font.SysFont('Arial', 60),
                                   base_color="#00CC66", hover_color="#00FF80")
        left1_button = Button(image=pygame.image.load("assets/smaller_button.png"), pos=(160, 370),
                                   text_input="LEFT",
                                   font=pygame.font.SysFont('Arial', 60),
                                   base_color="#00CC66", hover_color="#00FF80")
        right1_button = Button(image=pygame.image.load("assets/smaller_button.png"), pos=(160, 440),
                                   text_input="RIGHT",
                                   font=pygame.font.SysFont('Arial', 60),
                                   base_color="#00CC66", hover_color="#00FF80")
        sp1_button = Button(image=pygame.image.load("assets/smaller_button.png"), pos=(160, 510),
                                   text_input="SPECIAL",
                                   font=pygame.font.SysFont('Arial', 60),
                                   base_color="#00CC66", hover_color="#00FF80")
        
        up2_button = Button(image=pygame.image.load("assets/smaller_button.png"), pos=(610,230),
                                   text_input="UP",
                                   font=pygame.font.SysFont('Arial', 60),
                                   base_color="#00CC66", hover_color="#00FF80")
        down2_button = Button(image=pygame.image.load("assets/smaller_button.png"), pos=(610, 300),
                                   text_input="DOWN",
                                   font=pygame.font.SysFont('Arial', 60),
                                   base_color="#00CC66", hover_color="#00FF80")
        left2_button = Button(image=pygame.image.load("assets/smaller_button.png"), pos=(610, 370),
                                   text_input="LEFT",
                                   font=pygame.font.SysFont('Arial', 60),
                                   base_color="#00CC66", hover_color="#00FF80")
        right2_button = Button(image=pygame.image.load("assets/smaller_button.png"), pos=(610, 440),
                                   text_input="RIGHT",
                                   font=pygame.font.SysFont('Arial', 60),
                                   base_color="#00CC66", hover_color="#00FF80")
        sp2_button = Button(image=pygame.image.load("assets/smaller_button.png"), pos=(610, 510),
                                   text_input="SPECIAL",
                                   font=pygame.font.SysFont('Arial', 60),
                                   base_color="#00CC66", hover_color="#00FF80")
        
        for button in [back_button,up1_button,up2_button,down1_button,down2_button,left1_button,left2_button,right1_button,right2_button,sp1_button,sp2_button]:
            button.change_color(menu_mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.check_for_input(menu_mouse_pos):
                    main_menu()
                if up1_button.check_for_input(menu_mouse_pos):
                    set_control(0,PLAYER1_KEYS)
                if up2_button.check_for_input(menu_mouse_pos):
                    set_control(0,PLAYER2_KEYS)
                if down1_button.check_for_input(menu_mouse_pos):
                    set_control(1,PLAYER1_KEYS)
                if down2_button.check_for_input(menu_mouse_pos):
                    set_control(1,PLAYER2_KEYS)
                if left1_button.check_for_input(menu_mouse_pos):
                    set_control(2,PLAYER1_KEYS)
                if left2_button.check_for_input(menu_mouse_pos):
                    set_control(2,PLAYER2_KEYS)
                if right1_button.check_for_input(menu_mouse_pos):
                    set_control(3,PLAYER1_KEYS)
                if right2_button.check_for_input(menu_mouse_pos):
                    set_control(3,PLAYER2_KEYS)
                if sp1_button.check_for_input(menu_mouse_pos):
                    set_control(4,0)
                if sp2_button.check_for_input(menu_mouse_pos):
                   set_control(4,1)
                
        pygame.display.update()


def set_control(id, keys):
    global SP_KEY2, SP_KEY1
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                main_menu()
            if event.type == pygame.KEYDOWN:
                if id == 4:
                    if keys == 0:
                        SP_KEY1 = event.key
                    else:
                        SP_KEY2 = event.key
                else:
                    keys[id] = event.key
                controls_menu()


def settings():
    while True:
        screen.blit(pygame.image.load("assets/rules.png"), (0, 0))

        menu_mouse_pos = pygame.mouse.get_pos()

        back_button = Button(image=pygame.image.load("assets/smaller_button.png"), pos=(700, 35),
                                   text_input="BACK",
                                   font=pygame.font.SysFont('Arial', 60),
                                   base_color="#00CC66", hover_color="#00FF80")

        for button in [back_button]:
            button.change_color(menu_mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.check_for_input(menu_mouse_pos):
                    main_menu()
        pygame.display.update()


def prepend_to_file(new_line):
    file_name = 'result.txt'
    with open(file_name, 'r') as file:
        lines = file.readlines()

    lines.insert(0, new_line + "\n")

    if len(lines) > 5:
        lines = lines[:-1]

    with open(file_name, 'w') as file:
        file.writelines(lines)


def scoreboard():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.Font(None, 32) # Font for the table
    WHITE = (255, 255, 255)
    while True:
        screen.blit(pygame.image.load("assets/background.jpg"), (0, 0))

        menu_mouse_pos = pygame.mouse.get_pos()

        back_button = Button(image=pygame.image.load("assets/smaller_button.png"), pos=(700, 35),
                             text_input="BACK",
                             font=pygame.font.SysFont('Arial', 60),
                             base_color="#00CC66", hover_color="#00FF80")

        for button in [back_button]:
            button.change_color(menu_mouse_pos)
            button.update(screen)

        with open('result.txt', 'r') as f:
            lines = f.readlines()

        # Render headers
        win_text = font.render("WYGRANA", True, WHITE)
        lose_text = font.render("PRZEGRANA", True, WHITE)

        screen.blit(win_text, (200, 100))
        screen.blit(lose_text, (400, 100))

        for i, line in enumerate(lines):
            win, lose = line.strip().split(',')
            win_text = font.render(win, True, WHITE)
            lose_text = font.render(lose, True, WHITE)

            screen.blit(win_text, (200, 130 + i*30))
            screen.blit(lose_text, (400, 130 + i*30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.check_for_input(menu_mouse_pos):
                    main_menu()

        pygame.display.update()



if __name__ == "__main__":
    main_menu()
