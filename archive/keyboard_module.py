import pygame


def init():
    pygame.init()
    win = pygame.display.set_mode((500, 500))


def getKey(key_name):
    ans = False
    for event in pygame.event.get():
        pass
    key_input = pygame.key.get_pressed()
    my_key = getattr(pygame, 'K_{}'.format(key_name))
    if key_input[my_key]:
        ans = True
    pygame.display.update()
    return ans


def main():
    if getKey("LEFT"):
        print("Left key pressed")
    if getKey("RIGHT"):
        print("Right key pressed")


if __name__ == '__main__':
    init()
    while True:
        main()
