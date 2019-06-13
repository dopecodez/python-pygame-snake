#Author : Govind S

from pygame.locals import *
import pygame
import time
import collections
from random import randint

#declaring globals
step = 20
windowHeight = 600
windowWidth = 700

class Food:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x * step
        self.y = y * step

    #function to draw food
    def draw(self, surface, image):
        surface.blit(image, (self.x, self.y))


class Player:
    #using collections.deque to optimize performance
    x = collections.deque([])
    y = collections.deque([])
    direction = 3
    length = 3
    previousLength = 3

    def __init__(self, length):
        self.length = length
        self.previousLength = length
        for i in range(0, 5):
           self.x.append(step*i)
           self.y.append(step)

    def update(self):
        # update previous positions
        if self.previousLength == self.length:
            self.x.pop()
            self.y.pop()
        elif self.previousLength != self.length:
            self.previousLength = self.length

        # update position of head of snake, also handles movements from one end of screen to opposite end
        if self.x[0] < 0:
            self.x.appendleft(windowWidth)
        elif self.x[0] == windowWidth:
            self.x.appendleft(0)
        if self.y[0] == windowHeight:
            self.y.appendleft(0)
        elif self.y[0] < 0:
            self.y.appendleft(windowHeight)
        if self.direction == 0:
            self.x.appendleft(self.x[0] + step)
            self.y.appendleft(self.y[0])
        if self.direction == 1:
            self.x.appendleft(self.x[0] - step)
            self.y.appendleft(self.y[0])
        if self.direction == 2:
            self.y.appendleft(self.y[0] - step)
            self.x.appendleft(self.x[0])
        if self.direction == 3:
            self.y.appendleft(self.y[0] + step)
            self.x.appendleft(self.x[0])

    #functions to control direction, also checking whether snake is in opposite direction
    def move_right(self):
        if self.direction != 1:
            self.direction = 0

    def move_left(self):
        if self.direction != 0:
            self.direction = 1

    def move_up(self):
        if self.direction != 3:
            self.direction = 2

    def move_down(self):
        if self.direction != 2:
            self.direction = 3

    #function to draw snake
    def draw(self, surface, image):
        for i in range(0, self.length):
            surface.blit(image, (self.x[i], self.y[i]))


class Game:
    def __init__(self):
        #initialising music and text
        self.background_music = pygame.mixer.Sound("Sounds/background-music.wav")
        self.eat_sound = pygame.mixer.Sound("Sounds/eat-sound.wav")
        self.game_over_sound = pygame.mixer.Sound("Sounds/game-over-sound.wav")
        self.red = pygame.Color("red")
        self.font_game_over = pygame.font.SysFont("times new roman", 44)
        self.font_score = pygame.font.SysFont("times new roman", 20)

    #check if if collision occured between two sets of points
    def is_collision(self, x1, y1, x2, y2):
        if x1 == x2:
            if y1 == y2:
                return True
        return False

    #function to play game sounds using pygame.mixer channels
    def game_sound(self, s):
        #play game sounds
        if s == 0:
            pygame.mixer.Channel(0).play(self.background_music, loops=-1)
        elif s == 1:
            pygame.mixer.Channel(1).play(self.eat_sound)
        elif s == 2:
            pygame.mixer.Channel(0).stop()
            pygame.mixer.Channel(2).play(self.game_over_sound, loops=2)
    
    #function to draw game score
    def draw_game_score(self, surface, score):
        score_surface = self.font_score.render("Score : {}".format(score), True, self.red)
        score_position = score_surface.get_rect()
        score_position.midtop = (650, 10)
        surface.blit(score_surface, score_position)

    #function to draw game lost screen
    def draw_game_lost(self,surface,score):
        game_over_surface = self.font_game_over.render("Game over :(", True, self.red)
        game_over_position = game_over_surface.get_rect()
        game_over_position.midtop = (350, 250)
        surface.blit(game_over_surface, game_over_position)
        score_surface = self.font_score.render("Score : {}".format(score), True, self.red)
        score_position = score_surface.get_rect()
        score_position.midtop = (350, 300)
        surface.blit(score_surface, score_position)
        pygame.display.flip()

class App:
    player = 0
    food = 0
    initialKeyEvent = False

    def __init__(self):
        #initialising all classes
        self._running = True
        self._display_surf = None
        self._image_surf = None
        self.player = Player(3)
        self.food = Food(5, 5)
        self.score = 0
        pygame.init()
        pygame.mixer.init()
        self.game = Game()

    def on_init(self):
        self._display_surf = pygame.display.set_mode(
            (windowWidth, windowHeight), pygame.HWSURFACE)

        pygame.display.set_caption('Classic Snake')
        self._running = True
        #setting images and scaling to desired size
        self._image_surf = pygame.image.load("Images/square-icon.png").convert()
        self._food_surf = pygame.image.load("Images/green-dot.png").convert()
        self._image_surf = pygame.transform.scale(self._image_surf, (15, 15))
        self._food_surf = pygame.transform.scale(self._food_surf, (15, 15))

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    def on_loop(self):
        self.player.update()

        # check to see if snake eats food
        if self.game.is_collision(self.food.x, self.food.y, self.player.x[0], self.player.y[0]):
            self.game.game_sound(1)
            self.score = self.score + 1
            self.food.x = randint(0, 34) * step
            self.food.y = randint(0, 29) * step
            self.player.length = self.player.length + 1

        # check to see if snake collides with itself
        for i in range(3, self.player.length):
            if self.game.is_collision(self.player.x[0], self.player.y[0], self.player.x[i], self.player.y[i]):
                self.game.game_sound(2)
                self.game.draw_game_lost(self._display_surf, self.score)
                self._running = False
                self.on_cleanup(4)

    def on_render(self):
        if self._running:
            #function to call draw score, snake, and food
            white = [255, 255, 255]
            self._display_surf.fill(white)
            self.game.draw_game_score(self._display_surf, self.score)
            self.player.draw(self._display_surf, self._image_surf)
            self.food.draw(self._display_surf, self._food_surf)
            pygame.display.flip()

    #function to quit the game
    def on_cleanup(self, delay):
        time.sleep(delay)
        pygame.quit()

    #original logic goes here
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
        self.game.game_sound(0)
        while(self._running):
            pygame.event.pump()
            keys = pygame.key.get_pressed()

            #check which key is first pressed
            if keys[K_RIGHT] or keys[K_LEFT] or keys[K_DOWN] or keys[K_UP] or keys[K_ESCAPE]:
                self.initialKeyEvent = True

            if self.initialKeyEvent:
                if (keys[K_RIGHT]):
                    self.player.move_right()

                if (keys[K_LEFT]):
                    self.player.move_left()

                if (keys[K_UP]):
                    self.player.move_up()

                if (keys[K_DOWN]):
                    self.player.move_down()

                if (keys[K_ESCAPE]):
                    self._running = False

                self.initialKeyEvent = True
                self.on_loop()
            self.on_render()

            #reduces loop speed to a playable value, increase to decrease speed
            time.sleep(50.0 / 550.0)
        self.on_cleanup(0)


if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
