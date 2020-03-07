import sys, pygame, os
from pygame.locals import *

SIZE = WIDTH, HEIGHT = 1000, 1000
SCREENRECT = pygame.Rect(0, 0, WIDTH, HEIGHT)
ALIEN_RELOAD = 12

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

def load_image(name):
    try:
        image = pygame.image.load(name)
    except pygame.error:
        print('Cannot load image: ', name)
        raise SystemExit(str("error"))
    image = pygame.transform.rotozoom(image, 0, 3)
    image = image.convert_alpha()
    return image, image.get_rect()

class Ship(pygame.sprite.Sprite):
    speed = 5
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = load_image("sprites/Ship_White.png")
        self.rect.center = (WIDTH/2, HEIGHT-(self.rect.height/1.25))
        self.rect.inflate(30, 30)
        self.reloading = 0
    
    def move(self, direction):
        #-1=left 0=nothing 1=right
        if(self.rect.left > 0 and self.rect.right < WIDTH or\
         self.rect.left <= 0 and direction == 1 or\
         self.rect.left >= WIDTH and direction == -1):
            self.rect.move_ip([direction*self.speed, 0])
        

    def gunpos(self):
        pos = self.rect.centerx
        return pos, self.rect.top

class Rocket(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = load_image("sprites/rocket_0001.png")
        self.rect.midbottom = pos

    def update(self):
        self.rect.move_ip([0, -10])

class Alien(pygame.sprite.Sprite):
    speed = 7
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = load_image("sprites/Fly_0001.png")
        self.rect.right = WIDTH
        self.facing = -1 * Alien.speed

    def update(self):
        self.rect.move_ip(self.facing, 0)
        if(not SCREENRECT.contains(self.rect)):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self, self.containers)
        explosion_uris = [ "sprites/enemy_explosion_0001.png", "sprites/enemy_explosion_0002.png", "sprites/enemy_explosion_0003.png", "sprites/enemy_explosion_0004.png" ]
        self.images = []
        for img in explosion_uris:
                img = pygame.image.load(img)
                img = pygame.transform.rotozoom(img, 0, 3)
                img = img.convert_alpha()
                self.images.append(img)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.img_idx = 0
        self.img_tot = 4

    def update(self):
        self.img_idx += 1
        if(self.img_idx >= self.img_tot):
            self.kill()
        else:
            self.image = self.images[self.img_idx]
        

#todo: load images before class init
def main():
    pygame.init()

    # decorate game window
    pygame.display.set_caption('Galaga')

    # set up screen
    screen = pygame.display.set_mode(SIZE)
    background = pygame.Surface(SIZE)
    background = background.convert()
    background.fill(BLACK)

    # initialize game groups
    rockets = pygame.sprite.Group()
    aliens = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()

    # assign default groups to each sprite class
    Ship.containers = all
    Rocket.containers = rockets, all
    Alien.containers = aliens, all
    Explosion.containers = all

    # create some starting values
    clock = pygame.time.Clock()

    # starting variables
    alienreload = ALIEN_RELOAD

    # init sprites
    ship = Ship()
    Alien()

    while 1:
        for event in pygame.event.get():
            if(event.type == QUIT or \
                (event.type == KEYDOWN and event.key == K_ESCAPE)): return 

        keystate = pygame.key.get_pressed()

        # clear the last drawn sprites
        all.clear(screen, background)
        # update all sprites
        all.update()

        direction = keystate[K_RIGHT] - keystate[K_LEFT]
        ship.move(direction)
        
        # Firing logic, forced to lift spacebar before you can fire next shot
        firing = keystate[K_SPACE]
        if not ship.reloading and firing:
            Rocket(ship.gunpos())
        ship.reloading = firing

        # Create new aliens
        if(alienreload):
            alienreload -= 1
        else:
            Alien()
            alienreload = ALIEN_RELOAD
            
        # Detect collisions
        for alien in pygame.sprite.groupcollide(rockets, aliens, 1, 1):
            Explosion(alien)


        #draw the scene
        dirty = all.draw(screen)
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()