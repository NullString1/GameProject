import pygame
import time
import sys
from math import gcd

class coords(tuple):
    def __new__(cls, *args):
        if type(args[0]) in [int, float]:
            return tuple.__new__(cls, args)
        else:
            return tuple.__new__(cls, args[0])

    def __add__(self, c):
        return coords(*([sum(x) for x in zip(self, c)]))

    def __truediv__(self, c):
        if type(c) in [int, float]:
            return coords(*[x for x in map(lambda b: int(b/c), self)])
        elif type(c) in [tuple, list, coords]:
            return coords(*[int(a/b) for a,b in zip(self,c)])
        else:
            raise TypeError

    def __setitem__(self, key, value):
        a=[x for x in self]
        a[key]=value
        return coords(a)

class eventHandler():
    def __init__(self, chtr, surface):
        self.chtr = chtr
        self.surface = surface

    def hEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.chtr.up()
                if event.key == pygame.K_DOWN:
                    self.chtr.down()
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                 [btn.onClick() for btn in btns if btn.rect.collidepoint(pygame.mouse.get_pos())]
                     
        self.chtr.draw()
        [btn.draw() for btn in btns]
class gobject():
    def __init__(self, surface):
        #self.img = pygame.image.load(imgpath)
        #self.img = pygame.transform.scale(self.img, (50, 80))
        #self.imgfile = imgpath
        self.surface = surface
        self.pos = coords(self.surface.get_size())/2

    def setposr(self, xy): #Move relative
        self.pos += coords(xy)

    def setpos(self, xy): #Move absolute
        self.pos = coords(xy)

    def draw(self):
        self.surface.fill((255,255,255))
        self.surface.blit(self.img, self.pos)
        #pygame.display.update()


class entity(gobject):
    def __init__(self, surface, imgpath):
        gobject.__init__(self, surface)
        self.img = pygame.image.load(imgpath)
        self.img = pygame.transform.scale(self.img, (50, 80))
        self.imgfile = imgpath

    def move(self, xy):
        final=self.pos+xy
        while self.pos != final:
            if self.pos[0] > self.surface.get_size()[0]:
                self.setpos((-50, self.pos[1]))
                break
            #print(f"{self.pos=} {xy=} {final=}")
            #print(self.pos + xy)
            if xy[0] > 0:
                self.setposr(coords(1, 0))
                xy[0] -=1
            if xy[0] < 0:
                self.setposr(coords(-1, 0))
                xy[0] +=1
            if xy[1] > 0:
                self.setposr(coords(0, 1))
                xy[1] -=1
            if xy[1] < 0:
                self.setposr(coords(0, -1))
                xy[1] +=1
            self.draw()
            clock.tick()

class chtr(entity):
    def __init__(self, surface, imgpath):
        entity.__init__(self, surface, imgpath)
        self.img = pygame.transform.scale(self.img, coords(surface.get_size())/(26, 9))
        self.pos = coords(self.surface.get_size())/2
        self.speed = 50

    def up(self):
        self.move(coords(0, -self.speed))

    def down(self):
        self.move(coords(0, self.speed))

class button(gobject):
    def __init__(self, surface, size):
        gobject.__init__(self, surface)
        self.bsurface = pygame.Surface(size)
        self.bsurface.fill([0,0,0])
        self.rect = pygame.Rect(self.pos[0], self.pos[1], size[0], size[1])
        self.surface.blit(self.bsurface, self.pos)

    def draw(self):
        self.surface.blit(self.bsurface, self.pos)


    def onClick(self):
        print("Clicked")

def showMenu(surface):
    font = pygame.font.Font("Arial.ttf", 30)
    title = font.render("Duck Game", True, [255,255,255])
    
clock = pygame.time.Clock()
btns = []
def main():

    pygame.init()

    surface = pygame.display.set_mode((1280,720))
    pygame.display.set_caption("Game")
    
    pygame.draw.rect(surface, (255,255,255), [0,0, *surface.get_size()])

    duck = chtr(surface, "duck.png")
    eHandler = eventHandler(duck, surface)

    duck.draw()
    
    playing = True

    btns.append(button(surface, (200,200)))
    while playing:
        eHandler.hEvents()
        pygame.display.update()
        duck.move(coords(0, 3))
        duck.move(coords(10, 0))
        clock.tick(60)

if __name__ == "__main__":
    main()
