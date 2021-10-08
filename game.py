import pygame
import random
import threading
import time


class coords(tuple):
    def __new__(cls, *args):
        if type(args[0]) in [int, float]:
            return tuple.__new__(cls, args)
        else:
            return tuple.__new__(cls, args[0])

    def __add__(self, c):
        return coords(*([sum(x) for x in zip(self, c)]))

    def __sub__(self, c):
        return coords(*[int(a-b) for a, b in zip(self, c)])

    def __truediv__(self, c):
        if type(c) in [int, float]:
            return coords(*[x for x in map(lambda b: int(b/c), self)])
        elif type(c) in [tuple, list, coords]:
            return coords(*[int(a/b) for a, b in zip(self, c)])
        else:
            raise TypeError

    def __mul__(self, c):
        if type(c) in [int, float]:
            return coords(*[x for x in map(lambda b: int(b*c), self)])
        elif type(c) in [tuple, list, coords]:
            return coords(*[int(a*b) for a, b in zip(self, c)])
        else:
            raise TypeError

    def __setitem__(self, key, value):
        a = [x for x in self]
        a[key] = value
        return coords(a)


class eventHandler():
    def __init__(self, chtr, surface):
        self.chtr = chtr
        self.surface = surface
        self.btns = []
        self.blcks = []

    def hEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                [btn.onClick() for btn in self.btns if btn.rect.collidepoint(
                    pygame.mouse.get_pos()) and btn.isvisible]

        if playing:
            k = pygame.key.get_pressed()
            if k[pygame.K_UP]:
                self.chtr.up()
            if k[pygame.K_DOWN]:
                self.chtr.down()
            if self.chtr.pos[1] > wsize[1]:
                self.chtr.onCollision()

            # for blck in self.blcks:
            #    if blck.rect.collidepoint(self.chtr.pos-blck.pos):
            #        self.chtr.onCollision()
            #        break
            # [self.chtr.onCollision() for blck in self.blcks if blck.rect.collidepoint(
            #    self.chtr.pos-blck.pos)]

            [self.chtr.onCollision()
             for blck in self.blcks if blck.rect.colliderect(self.chtr.rect)]
            #[print(f"{self.chtr.pos=}, {blck.pos=}, {blck.rect.collidepoint(self.chtr.pos)=}") for blck in self.blcks]
            #[print(f"{blck.rect.collidepoint(coords(self.chtr.pos)-blck.pos)=}, {blck.pos=}, {blck.pos+blck.size=}") for blck in self.blcks]

            self.chtr.draw()
            [blck.reset()
             for blck in self.blcks if blck.pos[0] < -20]
            [blck.draw() for blck in self.blcks]

        #[self.blcks.remove(blck) for blck in self.blcks if blck.pos[0]<-20]
        [btn.draw() for btn in self.btns]

    def addBlock(self, blck):
        self.blcks.append(blck)

    def addButton(self, btn):
        self.btns.append(btn)

    def remButton(self, btn):
        self.btns.remove(btn)

    def clearBtns(self):
        self.btns = []


class bobject():  # Base object
    def __init__(self, surface):
        self.surface = surface
        self.pos = wsize/2

    def setposr(self, xy):  # Move relative
        self.pos += coords(xy)

    def setpos(self, xy):  # Move absolute
        self.pos = coords(xy)


class gobject(bobject):  # Game object
    def __init__(self, surface):
        bobject.__init__(self, surface)

    def move(self, xy):
        final = self.pos+xy
        while self.pos != final:
            if self.pos[0] > self.surface.get_size()[0]:
                self.setpos((-50, self.pos[1]))
                break
            if xy[0] > 0:
                self.setposr(coords(1, 0))
                xy[0] -= 1
            if xy[0] < 0:
                self.setposr(coords(-1, 0))
                xy[0] += 1
            if xy[1] > 0:
                self.setposr(coords(0, 1))
                xy[1] -= 1
            if xy[1] < 0:
                self.setposr(coords(0, -1))
                xy[1] += 1
            self.draw()
            clock.tick()


class entity(gobject):
    def __init__(self, surface, imgpath):
        gobject.__init__(self, surface)
        self.img = pygame.image.load(imgpath)
        self.img = pygame.transform.scale(self.img, (50, 80))
        self.imgfile = imgpath

    def draw(self):
        self.surface.blit(self.img, self.pos)


class chtr(entity):
    def __init__(self, surface, imgpath):
        entity.__init__(self, surface, imgpath)
        self.size = wsize/(26, 9)
        self.img = pygame.transform.scale(
            self.img, self.size)
        self.pos = wsize/2
        self.rect = pygame.Rect(*self.pos, *self.size)
        self.speed = 8
        self.invuln = False

    def draw(self):
        entity.draw(self)
        if self.invuln:
            itext = font.render("Extra Life", True, [0, 0, 0])
            self.surface.blit(itext, wsize - (130, 80))
        stext = font.render(f"Speed: {self.speed}", True, [0, 0, 0])
        self.surface.blit(stext, wsize - (130, 40))
        self.rect = pygame.Rect(*self.pos, *self.size)
        pygame.draw.rect(surface, [0, 0, 0], self.rect, 2)

    def up(self):
        self.move(coords(0, -self.speed-3))

    def down(self):
        self.move(coords(0, self.speed))

    def reset(self):
        self.setpos(wsize/2)

    def upgLife(self):
        self.invuln = True
        itext = font.render("Extra Life", True, [0, 0, 0])
        self.surface.blit(itext, wsize - (130, 80))
        pygame.display.update()

    def upgSpeed(self):
        if self.speed > 10:
            self.speed -= 10
        stext = font.render(f"Speed: {self.speed}", True, [0, 0, 0])
        self.surface.blit(stext, wsize - (130, 40))
        pygame.display.update()

    def onCollision(self):
        if self.invuln:
            self.invuln = False
            self.setpos(wsize/2)
            self.draw()
        else:
            self.reset()
            print("collision")
            [blck.reset()
             for blck in eHandler.blcks]
            showMenu(self.surface)


class block(gobject):
    def __init__(self, /, surface, colour=(120, 0, 0), size=(40, 300), top=True):
        gobject.__init__(self, surface)
        self.colour = colour
        self.size = size
        self.top = top
        self.reset()

    def draw(self):
        self.surface.blit(self.bsurface, self.pos)

    def reset(self):
        self.bsurface = pygame.Surface(
            (self.size[0], random.randint(280, 300)))
        self.rect = pygame.draw.rect(self.bsurface, self.colour, [
                                     0, 0, *self.bsurface.get_size()])
        if self.top:
            y = 0
        else:
            y = self.surface.get_height()-self.bsurface.get_height()
        self.pos = coords(1240, y)


class button(bobject):
    def __init__(self, /, surface, pos, text, func, size=None, tcolour=[0, 0, 0], bcolour=[120, 120, 120], tsize=20):
        bobject.__init__(self, surface)
        font = pygame.font.SysFont("arial", tsize)
        btext = font.render(text, True, tcolour)
        if size == None:
            size = coords(btext.get_size())*1.3
        self.pos = pos
        self.bsurface = pygame.Surface(size)
        self.bsurface.fill(bcolour)
        #self.bsurface.blit(btext, coords(size[0]-btext.get_width(), size[1]-btext.get_height())/2)
        self.bsurface.blit(btext, (coords(size)-btext.get_size())/2)
        self.rect = pygame.Rect(self.pos[0], self.pos[1], size[0], size[1])
        self.func = func
        self.draw()

    def draw(self):
        self.isvisible = True
        self.surface.blit(self.bsurface, self.pos)

    def onClick(self):
        self.func()


def showMenu(surface):
    global playing
    playing = False
    font = pygame.font.SysFont("arial", 30)
    title = font.render("Duck Game", True, [0, 0, 0])
    pygame.draw.rect(surface, (255, 255, 255), [0, 0, *surface.get_size()])
    eHandler.clearBtns()
    eHandler.addButton(button(surface, wsize/2+(30, 0), "Start Game",
                       lambda: exec("play(surface)")))
    eHandler.addButton(button(surface, wsize/2+(150, 0),
                       "Upgrades", lambda: exec("showUpgrades(surface)")))
    eHandler.addButton(button(surface, wsize/2-(30, 0), "Exit", exit))
    surface.blit(title, (wsize[0]/2, 50))
    pygame.display.update()
    while True:
        eHandler.hEvents()


def wait(e, t):
    time.sleep(t)
    exec(e, globals())


def play(surface):
    global playing
    playing = True
    pygame.draw.rect(surface, (255, 255, 255), [0, 0, *wsize])
    eHandler.clearBtns()
    duck.draw()
    eHandler.addBlock(block(surface, top=True))
    eHandler.addBlock(block(surface, top=False))
    threading.Thread(target=wait, args=(
        "eHandler.addBlock(block(surface, top=True))", 1)).start()
    threading.Thread(target=wait, args=(
        "eHandler.addBlock(block(surface, top=False))", 1)).start()
    threading.Thread(target=wait, args=(
        "eHandler.addBlock(block(surface, top=True))", 2)).start()
    threading.Thread(target=wait, args=(
        "eHandler.addBlock(block(surface, top=False))", 2)).start()
    threading.Thread(target=wait, args=(
        "eHandler.addBlock(block(surface, top=True))", 3)).start()
    threading.Thread(target=wait, args=(
        "eHandler.addBlock(block(surface, top=False))", 3)).start()
    threading.Thread(target=wait, args=(
        "eHandler.addBlock(block(surface, top=True))", 4)).start()
    threading.Thread(target=wait, args=(
        "eHandler.addBlock(block(surface, top=False))", 4)).start()
    while playing:
        eHandler.hEvents()
        duck.move(coords(0, 3))
        [blck.move(coords(-5, 0)) for blck in eHandler.blcks]
        #duck.move(coords(10, 0))
        pygame.display.update()
        pygame.draw.rect(surface, (255, 255, 255), [0, 0, *wsize])
        clock.tick(60)


def showUpgrades(surface):
    global playing
    playing = False
    font = pygame.font.SysFont("arial", 30)
    title = font.render("Duck Game", True, [0, 0, 0])
    pygame.draw.rect(surface, (255, 255, 255), [0, 0, *wsize])
    eHandler.clearBtns()
    eHandler.addButton(button(surface, wsize/2+(0, 0),
                       "Decrease speed (10p)", duck.upgSpeed))
    eHandler.addButton(button(surface, wsize/2+(220, 0),
                       "Extra life (50p)", duck.upgLife))
    eHandler.addButton(button(surface, wsize/2-(150, 0),
                       "Back to menu", lambda: exec("showMenu(surface)")))
    surface.blit(title, (wsize[0]/2, 50))
    pygame.display.update()
    while True:
        eHandler.hEvents()


pygame.init()
clock = pygame.time.Clock()
wsize = coords(1280, 720)
surface = pygame.display.set_mode(wsize)
pygame.draw.rect(surface, (255, 255, 255), [0, 0, *wsize])
pygame.display.set_caption("Game")
duck = chtr(surface, "duck.png")
eHandler = eventHandler(duck, surface)
font = pygame.font.SysFont("arial", 30)
playing = False


def main():
    showMenu(surface)


if __name__ == "__main__":
    main()
