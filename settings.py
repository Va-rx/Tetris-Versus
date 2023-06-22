from enum import Enum
import pygame
import random

PLAYER1_KEYS = [ord('w'), ord('s'), ord('a'), ord('d')]
KEYS1_NOW = [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]
PLAYER2_KEYS = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
KEYS2_NOW = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
SP_KEY1 = ord('1')
SP_KEY2 = pygame.K_KP_ENTER
BRIDGE_START = 4
BRIDGE_END = 10
BRIDGE_WIDTH = 4


class TYPE_FIGURE(Enum):
    NORMAL = 0,
    SPECIAL = 1


class types(Enum):
    NORMAL = 0
    BOMB = 1
    WALL = 2
    BIG = 3


class NORMAL_FIGURES_COLORS(Enum):
    BLUE = (0, 0, 255),
    RED = (225, 0, 0)


class SPECIAL_FIGURES_COLORS(Enum):
    BLACK = (0, 0, 0),
    GREEN = (0, 255, 0),
    GRAY = (100, 100, 100)


WIDTH, HEIGHT = 800, 600
MAP_SET_X, MAP_SET_Y = 100, 60
MAP_WIDTH, MAP_HEIGHT = 10, 20
TILE = 25

SPEED = 20

FPS = 60

SPECIAL_FIGURE_PERCENTAGE = 0.2
NON_ROTATIVE_PERCENTAGE = 0.2

PIVOT = 12
PIVOT_POS = (2,2)

NORMAL_FIGURES_BASE = [
    ("rotative",[2, 7, 12, 17]),
    ("rotative",[11, 12, 17, 18]),
    ("rotative",[12, 13, 16, 17]),
    ("rotative",[7, 8, 12, 17]),
    ("rotative",[6, 7, 12, 17]),
    ("rotative",[7, 11, 12, 13]),
    ("non_rotative",[6, 7, 11, 12])
]


class NORMAL_FIGURES:
    def __init__(self):
        figure = random.choice(NORMAL_FIGURES_BASE)
        self.rotative = figure[0]
        self.base = figure[1]
        self.color = random.choice(list(NORMAL_FIGURES_COLORS))


class SPECIAL_FIGURES(Enum):
    S_WALL = [12], SPECIAL_FIGURES_COLORS.GRAY, "rotative"
    S_BOMB = [12], SPECIAL_FIGURES_COLORS.BLACK, "rotative"
    S_BIG = [2, 3, 7, 12, 17, 18], SPECIAL_FIGURES_COLORS.GREEN, "rotative"

    def __init__(self, figure, color,rotative):
        self.base = figure
        self.color = color
        self.rotative = rotative

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (0, 128, 0)

BRIDGE_TIME = 10  # seconds
CHANGED_KEYS_TIME = 5
FLIP_EVENT_TIME = 5