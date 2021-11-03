import pygame
import random
import threading
import time
from configparser import ConfigParser


class coords(tuple):
    def __new__(cls, *args):  # creates a new coords object
        if type(args[0]) in [int, float]:
            return tuple.__new__(cls, args)
        else:
            return tuple.__new__(cls, args[0])

    def __add__(self, c):  # adds two coords objects together
        return coords(*([sum(x) for x in zip(self, c)]))

    def __sub__(self, c):  # sutracts two coords objects from eachother
        return coords(*[int(a-b) for a, b in zip(self, c)])

    def __truediv__(self, c):  # divides one coords object by another
        if type(c) in [int, float]:
            return coords(*[x for x in map(lambda b: int(b/c), self)])
        elif type(c) in [tuple, list, coords]:
            return coords(*[int(a/b) for a, b in zip(self, c)])
        else:
            raise TypeError

    def __mul__(self, c):  # multiplies two coords objects
        if type(c) in [int, float]:
            return coords(*[x for x in map(lambda b: int(b*c), self)])
        elif type(c) in [tuple, list, coords]:
            return coords(*[int(a*b) for a, b in zip(self, c)])
        else:
            raise TypeError

    def __setitem__(self, key, value):  # Sets value at key in coords object
        a = [x for x in self]
        a[key] = value
        return coords(a)


class eventHandler():  # Game event handler
    def __init__(self, chtr, surface, configp):  # Initalise event handler
        self.chtr = chtr
        self.surface = surface
        self.btns = []
        self.blockpairs = []
        self.configp = configp

    def hEvents(self):  # Main handler
        for event in pygame.event.get():  # Loop through new events
            if event.type == pygame.QUIT:  # If event is quit, save score and close
                quitgame()
            if event.type == pygame.MOUSEBUTTONDOWN:  # If event is mouse click, check if click is in bounds of a button and the button is visible then call button's onClick
                [btn.onClick() for btn in self.btns if btn.rect.collidepoint(
                    pygame.mouse.get_pos()) and btn.isvisible]

        if playing:
            k = pygame.key.get_pressed()  # Get pressed keys
            if k[pygame.K_UP]:
                self.chtr.up()
            if k[pygame.K_DOWN]:
                self.chtr.down()
            if self.chtr.pos[1] > wsize[1]:  # If player hits floor
                self.chtr.onCollision()

            # for blck in self.blcks:
            #    if blck.rect.collidepoint(self.chtr.pos-blck.pos):
            #        self.chtr.onCollision()
            #        break
            # [self.chtr.onCollision() for blck in self.blcks if blck.rect.collidepoint(
            #    self.chtr.pos-blck.pos)]

            [blckpair.checkcollision(self.chtr)  # Loop through all blocks and check for a collision with player
             for blckpair in self.blockpairs]
            #[print(f"{self.chtr.pos=}, {blck.pos=}, {blck.rect.collidepoint(self.chtr.pos)=}") for blck in self.blcks]
            #[print(f"{blck.rect.collidepoint(coords(self.chtr.pos)-blck.pos)=}, {blck.pos=}, {blck.pos+blck.size=}") for blck in self.blcks]

            self.chtr.draw()  # Draw character
            [blckpair.reset()  # Reset blockpair when it reaches edge of screen
             for blckpair in self.blockpairs if blckpair.x < -20]
            [blckpair.draw() for blckpair in self.blockpairs]  # Draw blockpairs

        #[self.blcks.remove(blck) for blck in self.blcks if blck.pos[0]<-20]
        [btn.draw() for btn in self.btns]  # Draw buttons

    def addBlockpair(self, bp):  # Add a blockpair to the list
        self.blockpairs.append(bp)

    def addButton(self, btn):  # Add a button to the list
        self.btns.append(btn)

    def remButton(self, btn):  # Remove a button from the list
        self.btns.remove(btn)

    def clearBtns(self):  # Clear button list
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

    def move(self, xy):  # Move gobject smoothly (move and draw in small steps)
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


class entity(gobject):  # Entity class
    def __init__(self, surface, imgpath):
        gobject.__init__(self, surface)
        self.img = pygame.image.load(imgpath)
        self.img = pygame.transform.scale(self.img, (50, 80))
        self.imgfile = imgpath

    def draw(self):  # Draw entity to screen
        self.surface.blit(self.img, self.pos)


class chtr(entity):  # Character class
    def __init__(self, surface, imgpath):
        entity.__init__(self, surface, imgpath)
        self.size = wsize/(26, 9)  # Set size relative to window size
        self.img = pygame.transform.scale(
            self.img, self.size)
        self.pos = wsize/2  # Set position in middle of screen
        self.rect = pygame.Rect(*self.pos + (-5, 15),
                                *self.size - (5, 10))  # Create hitbox
        self.blockspeed = 10
        self.invuln = False
        self.score = 0
        self.points = 0

    def draw(self):
        entity.draw(self)
        if self.invuln:  # If character has an extra life
            itext = font.render("Extra Life", True, [0, 0, 0])
            self.surface.blit(itext, wsize - (130, 80))
        stext = font.render(f"Speed: {self.blockspeed}", True, [
                            0, 0, 0])  # Render game text
        score = font.render(f"Score: {duck.score}", True, [0, 0, 0])
        points = font.render(f"Points: {duck.points}", True, [0, 0, 0])
        self.surface.blit(score, (50, 50))  # Blit text onto surface
        self.surface.blit(points, (50, 75))
        self.surface.blit(stext, wsize - (130, 40))
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1] + 5
        #self.rect = pygame.Rect(*self.pos, *self.size)
        #pygame.draw.rect(self.surface, [0, 0, 0], self.rect, 2)
        # print(f"{self.score=}")

    def up(self):  # Move character up
        self.move(coords(0, -15))

    def down(self):  # Move character down
        self.move(coords(0, 8))

    def reset(self):  # Reset character to centre screen
        self.setpos(wsize/2)

    def upgLife(self):  # Life upgrade
        self.invuln = True
        self.points -= 50
        itext = font.render("Extra Life", True, [0, 0, 0])
        self.surface.blit(itext, wsize - (130, 80))
        pygame.display.update()

    def upgSpeed(self):  # Speed upgrade
        if self.blockspeed > 7:
            self.blockspeed -= 1
            self.points -= 10
        stext = font.render(f"Speed: {self.blockspeed}", True, [0, 0, 0])
        self.surface.blit(stext, wsize - (130, 40))
        pygame.display.update()

    def onCollision(self):  # Handle collisions
        if self.invuln:
            self.invuln = False
            self.setpos(wsize/2)
            self.draw()
        else:
            self.reset()
            # print("collision")
            eHandler.blockpairs = []
            showMenu(self.surface)


class block(gobject):  # Block object
    def __init__(self, /, surface, colour=(120, 0, 0), size=(40, 250), top=True):
        gobject.__init__(self, surface)
        self.bsurface = pygame.Surface(size)  # Create surface for block
        self.bsurface.fill(colour)
        self.colour = colour
        self.size = size
        self.top = top
        if self.top:
            self.opos = coords(wsize[0], 0)
        else:
            self.opos = coords(wsize[0], wsize[1]-self.size[1])
        self.pos = self.opos
        self.rect = pygame.Rect(*self.pos, *self.size)  # Create block hitbox
        self.draw()

    def draw(self):  # Blit block surface to main surface
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        self.surface.blit(self.bsurface, self.pos)

    def setx(self, x):  # Set x of block
        self.pos = coords(x, self.pos[1])
    # def reset(self):
    #    self.setpos(coords(self.opos))
    #    self.draw()


class blockpair():  # blockpair object
    def __init__(self, /, surface):
        self.surface = surface
        self.h = random.randint(100, 500)  # Random block height
        self.top = block(surface, top=True, size=(
            40, self.h))  # Creates top block
        self.bottom = block(surface, top=False, size=(
            40, wsize[1]-self.h-200))  # Creates bottom block
        self.x = wsize[1]
        self.rect = pygame.Rect(
            wsize[0], self.h, 40, wsize[1]-self.h-200)  # Create safe hitbox
        self.disabled = False

    def setx(self, x):  # Set x of blockpair
        self.x = x
        self.top.setx(x)
        self.bottom.setx(x)

    def move(self, dx):  # Move blockpair
        self.top.move(coords(dx, 0))
        self.bottom.move(coords(dx, 0))
        self.rect.left = self.top.pos[0]
        self.x = self.top.pos[0]
        if self.x < wsize[0]/2-50:
            self.disabled = False
        # print(
        #    f"{self.rect.x=}, {self.x=}, {self.top.pos[0]=}, {self.bottom.pos[0]=}")

    def draw(self):  # Draw blockpair
        self.top.draw()
        self.bottom.draw()
        #font = pygame.font.SysFont("arial", 30)
        #h = font.render(f"{self.h}", True, [0, 0, 0])
        #self.surface.blit(h, (self.x-60, 50))

    def reset(self):  # Reset block pair with new blocks and new size
        self.h = random.randint(100, 500)
        #h = 500
        self.top = block(surface, top=True, size=(40, self.h))
        self.bottom = block(surface, top=False, size=(40, wsize[1]-self.h-200))
        # self.top.setx(wsize[0])
        # self.bottom.setx(wsize[0])
        self.x = wsize[0]
        self.disabled = False

    def checkcollision(self, chtr: chtr):  # Check collisions with blocks and safe box
        if self.rect.colliderect(chtr.rect) and not self.disabled:
            chtr.score += 1
            chtr.points += 1
            self.disabled = True

        if self.top.rect.colliderect(chtr.rect):
            chtr.onCollision()
            self.disabled = True

        if self.bottom.rect.colliderect(chtr.rect):
            chtr.onCollision()
            self.disabled = True


class button(bobject):  # UI button object
    def __init__(self, /, surface, pos, text, func, size=None, tcolour=[0, 0, 0], bcolour=[120, 120, 120], tsize=20):
        bobject.__init__(self, surface)
        font = pygame.font.SysFont("arial", tsize)  # Font for button text
        btext = font.render(text, True, tcolour)
        if size == None:
            size = coords(btext.get_size())*1.3
        self.pos = pos
        self.bsurface = pygame.Surface(size)
        self.bsurface.fill(bcolour)
        #self.bsurface.blit(btext, coords(size[0]-btext.get_width(), size[1]-btext.get_height())/2)
        self.bsurface.blit(btext, (coords(size)-btext.get_size())/2)
        self.rect = pygame.Rect(
            self.pos[0], self.pos[1], size[0], size[1])  # Button click box
        self.func = func
        self.draw()

    def draw(self):  # Blit button surface to main surface
        self.isvisible = True
        self.surface.blit(self.bsurface, self.pos)

    def onClick(self):  # Call button function
        self.func()


def showMenu(surface):  # Draw game menu
    global playing
    playing = False
    font = pygame.font.SysFont("arial", 30)  # Draw all menu text
    pygame.draw.rect(surface, (255, 255, 255), [0, 0, *surface.get_size()])
    title = font.render("Duck Game", True, [0, 0, 0])
    points = font.render(f"Points: {duck.points}", True, [0, 0, 0])
    if duck.invuln:
        itext = font.render("Extra Life", True, [0, 0, 0])
        surface.blit(itext, wsize - (130, 80))
    stext = font.render(f"Speed: {duck.blockspeed}", True, [0, 0, 0])
    surface.blit(stext, wsize - (130, 40))
    eHandler.clearBtns()  # Clear button list
    eHandler.addButton(button(surface, wsize/2+(30, 0), "Start Game",  # Add buttons to list
                       lambda: exec("play(surface)")))
    eHandler.addButton(button(surface, wsize/2+(150, 0),
                       "Upgrades", lambda: exec("showUpgrades(surface)")))
    eHandler.addButton(button(surface, wsize/2-(30, 0), "Exit", quitgame))
    surface.blit(title, (wsize[0]/2, 50))
    surface.blit(points, (50, 50))
    pygame.display.update()  # Update display
    while True:
        eHandler.hEvents()  # Run event handler to listen for clicks


def wait(e, t):  # Helper function to run passed function in set time
    time.sleep(t)
    exec(e, globals())


def play(surface):
    global playing
    global threads
    playing = True
    pygame.draw.rect(surface, (255, 255, 255), [0, 0, *wsize])
    eHandler.clearBtns()
    duck.draw()
    while [thread for thread in threads if thread.is_alive()] != []:
        time.sleep(0.1)  # Ensure no threads are running, wait if they are
    eHandler.blockpairs = []
    threads = []
    eHandler.addBlockpair(blockpair(surface))  # Add inital block pair
    threads.append(threading.Thread(target=wait, args=(  # Threaded wait 1 second
        "eHandler.addBlockpair(blockpair(surface))", 1)))  # before adding next blockpair
    threads.append(threading.Thread(target=wait, args=(
        "eHandler.addBlockpair(blockpair(surface))", 2)))
    [thread.start() for thread in threads]

    duck.score = 0
    while playing:
        pygame.draw.rect(surface, (255, 255, 255), [
                         0, 0, *wsize])  # Blank screen
        eHandler.hEvents()  # Call event handler
        duck.move(coords(0, 6))  # Move character down
        [blckpair.move(-duck.blockspeed)
         for blckpair in eHandler.blockpairs]  # Move all blockpairs
        #duck.move(coords(10, 0))
        pygame.display.update()  # Update screen
        clock.tick(60)


def showUpgrades(surface):  # Show upgrades menu
    global playing
    playing = False
    font = pygame.font.SysFont("arial", 30)
    title = font.render("Duck Game", True, [0, 0, 0])
    pygame.draw.rect(surface, (255, 255, 255), [0, 0, *wsize])
    eHandler.clearBtns()
    if duck.points > 10:  # Draw speed upgrade if character has enough points
        eHandler.addButton(button(surface, wsize/2+(0, 0),
                           "Decrease speed (10p)", duck.upgSpeed))
    if duck.points > 50:  # Draw life upgrade if character has enough points
        eHandler.addButton(button(surface, wsize/2+(220, 0),
                                  "Extra life (50p)", duck.upgLife))
    eHandler.addButton(button(surface, wsize/2-(150, 0),
                       "Back to menu", lambda: exec("showMenu(surface)")))
    surface.blit(title, (wsize[0]/2, 50))
    pygame.display.update()
    while True:
        eHandler.hEvents()  # Handle events to listen for button clicks

def quitgame():
    configp.set("duck", "points", str(duck.points))
    with open("duck.cfg", "w") as f:
        configp.write(f)
    pygame.quit()
    quit()

pygame.init()  # Start pygame
clock = pygame.time.Clock()
wsize = coords(1280, 720)  # Set window size
surface = pygame.display.set_mode(wsize)
pygame.draw.rect(surface, (255, 255, 255), [0, 0, *wsize])
pygame.display.set_caption("Game")
duck = chtr(surface, "duck.png")  # Create character
configp = ConfigParser()  # Create configparser to load and save points
try:
    with open("duck.cfg", "r") as f:
        configp.read_file(f)
    if configp.has_section("duck"):
        duck.points = configp.getint("duck", "points")
except Exception as e:
    print(f"Error: {e}")

# If section in config doesn't exist, then create it
if not configp.has_section("duck"):
    configp.add_section("duck")
    configp.set("duck", "points", str(0))
eHandler = eventHandler(duck, surface, configp)  # Create event handler
font = pygame.font.SysFont("arial", 30)
playing = False
threads = []


def main():
    showMenu(surface)


if __name__ == "__main__":
    main()
