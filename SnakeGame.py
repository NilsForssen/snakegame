import random,time,os,sys
import pygame as pg
from pygame import Surface
from pygame.locals import *

class Resources():
    def __init__(self):
        self.imageLibrary = {}
        self.fontLibrary = {}
        self.turnSwitch = {
            (0,90):90,
            (0,270):180,
            (90,180):180,
            (90,0):270,
            (180,90):0,
            (180,270):270,
            (270,0):0,
            (270,180):90
        }
        
    def image(self,path):
        image = self.imageLibrary.get(path)
        if image == None:
            canonicalizedPath = path.replace("/", os.sep).replace("\\", os.sep)
            image = pg.image.load(canonicalizedPath)
            self.imageLibrary[path] = image
        return image

    def font(self,path,size):
        font = self.fontLibrary.get(path)
        if font == None:
            font = pg.font.Font(path,size)
            self.fontLibrary[path] = font
        return font


class Snake():
    def __init__(self,square = 25):
        self.square = square
        self.dx = 0
        self.dy = 1
        self.headx = 0
        self.heady = 0
        self.applex = 0
        self.appley = 0
        self.direction = 180
        self.dead = False

        self.screen = pg.display.get_surface()
        self.screenRect = self.screen.get_rect()
        self.screenW = self.screen.get_width()
        self.screenH = self.screen.get_height()
        
        self.get = Resources()
        self.headImg = pg.transform.smoothscale(self.get.image("Images/SnakeHead.png"),(self.square,self.square))
        self.bodyImg = pg.transform.smoothscale(self.get.image("Images/SnakeBody.png"),(self.square,self.square))
        self.turnImg = pg.transform.smoothscale(self.get.image("Images/SnakeTurn.png"),(self.square,self.square))
        self.tailImg = pg.transform.smoothscale(self.get.image("Images/SnakeTail.png"),(self.square,self.square))
        self.appleImg = pg.transform.smoothscale(self.get.image("Images/Apple.png"),(self.square,self.square))
        self.backImg = pg.transform.smoothscale(self.get.image("Images/BackGround.png"),(self.screenW,self.screenH))
        self.countdownFont = self.get.font("Fonts/Countdown.ttf",200)

        self.snakeBody = [(-500,-500),(-500,-500)]
        self.snakeLength = len(self.snakeBody)
        self.directionList = [(0,180,self.tailImg),(0,180,self.tailImg)]
        
        self.addApple()

    def runSnake(self):
        self.headx += self.square*self.dx
        self.heady += self.square*self.dy
        self.snakeBody.insert(0,(self.headx-(self.square*self.dx),self.heady-(self.square*self.dy)))
        if self.directionList[0][1] == self.direction:
            self.directionList.insert(0,(self.direction,self.direction,self.bodyImg))
        else:
            self.directionList.insert(0,(self.get.turnSwitch.get((self.directionList[0][1],self.direction)),self.direction,self.turnImg))
        self.snakeBody.pop()
        self.directionList.pop()
        self.snakeLength = len(self.snakeBody)
        for cordinate in self.snakeBody:
            if cordinate == (self.headx,self.heady):
                self.dead = True
                break
        if self.headx < 0 or self.headx == self.screenW or self.heady < 0 or self.heady == self.screenH:
            self.dead = True
        elif (self.headx,self.heady) == (self.applex,self.appley):
            if self.snakeLength < 2:
                self.snakeBody.append((self.headx-(self.square*self.dx),self.heady-(self.square*self.dy)))
                self.directionList.append((0,self.directionList[self.snakeLength-1][1],self.bodyImg))
            else:
                self.snakeBody.append((self.snakeBody[self.snakeLength-1][0]-(self.snakeBody[self.snakeLength-1][0]-self.snakeBody[self.snakeLength-2][0]),self.snakeBody[self.snakeLength-1][1]-(self.snakeBody[self.snakeLength-1][1]-self.snakeBody[self.snakeLength-2][1])))
                self.directionList.append((0,self.directionList[self.snakeLength-1][1],self.bodyImg))
            self.addApple()
        return self.dead

    def addApple(self):
        hit = True
        while hit:
            x = random.choice([possibleSpawn for possibleSpawn in range(self.screenW) if possibleSpawn % self.square == 0])
            y = random.choice([possibleSpawn for possibleSpawn in range(self.screenH) if possibleSpawn % self.square == 0])
            for cordinate in self.snakeBody:
                if cordinate == (x,y):
                    hit = True
                    break
                else:
                    hit = False
        self.applex = x
        self.appley = y
    
    def drawField(self):
        self.screen.blit(self.backImg,self.screenRect)

    def drawSnakeGame(self):
        self.drawField()
        self.screen.blit(self.appleImg,(self.applex,self.appley))
        for body in range(self.snakeLength-1):
            pass
            self.screen.blit(pg.transform.rotate(self.directionList[body][2],self.directionList[body][0]),self.snakeBody[body])
        self.screen.blit(pg.transform.rotate(self.tailImg,self.directionList[len(self.directionList)-1][1]),self.snakeBody[self.snakeLength-1])
        self.screen.blit(pg.transform.rotate(self.headImg,self.direction),(self.headx,self.heady))
    
    def drawCountdown(self,text,alpha=255,color=Color("red")):
        textSurface = self.countdownFont.render(text,True,color)
        alphaImg = pg.Surface(textSurface.get_rect().size,pg.SRCALPHA)
        alphaImg.fill((255,255,255,alpha))
        textSurface.blit(alphaImg,(0,0),special_flags=pg.BLEND_RGBA_MULT)
        textRect = textSurface.get_rect(center = self.screenRect.center)
        self.screen.blit(textSurface,textRect)

        
class Game():
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((400,400))
        self.snakeFunctions = Snake()
        self.gameSpeed = 8
        self.countdownLength = 3
        self.framesPerCount = 100
        self.clock = pg.time.Clock()
        self.running = True
        
    def gameLoop(self):
        self.countDown()
        while self.running:
            self.userEvents()
            if self.snakeFunctions.runSnake():
                self.running = False
            self.snakeFunctions.drawSnakeGame()
            pg.display.flip()
            self.clock.tick(self.gameSpeed)
        print(self.snakeFunctions.snakeLength+1)
            
    def countDown(self):
        for number in range(self.countdownLength):
            if not self.running:
                break
            number = str(self.countdownLength-number)
            for frame in range(self.framesPerCount):
                self.userEvents()
                if not self.running:
                    break
                self.snakeFunctions.drawField()
                self.snakeFunctions.drawCountdown(number,round(255-((255/self.framesPerCount)*frame),0))
                pg.display.flip()
                self.clock.tick(100)
    
    def userEvents(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                break
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_d and self.snakeFunctions.dy != 0:
                    self.snakeFunctions.dx = 1
                    self.snakeFunctions.dy = 0
                    self.snakeFunctions.direction = 270
                    break
                elif event.key == pg.K_a and self.snakeFunctions.dy != 0:
                    self.snakeFunctions.dx = -1
                    self.snakeFunctions.dy = 0
                    self.snakeFunctions.direction = 90
                    break
                elif event.key == pg.K_s and self.snakeFunctions.dx != 0:
                    self.snakeFunctions.dx = 0
                    self.snakeFunctions.dy = 1
                    self.snakeFunctions.direction = 180
                    break
                elif event.key == pg.K_w and self.snakeFunctions.dx != 0:
                    self.snakeFunctions.dx = 0
                    self.snakeFunctions.dy = -1
                    self.snakeFunctions.direction = 0
                    break
                elif event.key == pg.K_SPACE:
                    self.gameLoop()
                    
x = Game()
x.gameLoop()
pg.quit()
