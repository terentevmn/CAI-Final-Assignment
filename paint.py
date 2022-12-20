import pygame
from PIL import Image
import numpy as np

def draw() -> None:

    ##### PYGAME INIT ######
    BLACK = (0, 0, 0)
    W,M = 30,10
    pygame.init()
    size = (256*2 * 2,256*2 + 40)

    screen = pygame.display.set_mode(size)
    done = False
    clock = pygame.time.Clock()
    clocktick = 60
    ########################

    ###### PROGRAM VARS ####

    drawings = []
    colors = [
        (213,71,40), #RED
        (70, 232, 208), # CYAN
        (5, 42, 241), # BLUE
        (10, 124, 244), # lighter blue
        (174, 220, 143), # green
        (58, 47, 156), # purple
        (103, 38, 99), # wine color
        (11, 92, 239), # in between blue
        (78, 55, 195) # lighter purple
    ]

    firstPointSelected = False
    firstPos = None
    selectedColor = colors[0]
    outputarray = [[(0,0,0) for i in range(256)] for j in range(256)]
    
    def drawColors():
        # Draws color picker
        for i in range(len(colors)):
            pygame.draw.rect(screen, colors[i], [i*40, 256*2, 40, 40])
            if colors[i] == selectedColor:
                pygame.draw.rect(screen, (255,255,255), [i*40, 256*2, 40, 40], 2)

    def getRectsFromPoints(x,y):
        # pygame is shitty with getting rectangles right
        # they should be from top left to bottom right
        leftup = (min(x[0],y[0]), min(x[1],y[1]))
        rightdown = (max(x[0],y[0]),max(x[1],y[1]))
        return leftup, rightdown

    def drawRectangles():
        # Draws drawn rectangles
        for firstpos, secondpos, color in drawings:
            pygame.draw.rect(screen, color, [firstpos[0],firstpos[1],secondpos[0]-firstpos[0],secondpos[1]-firstpos[1]])

        if firstPointSelected:
            fp, sp = getRectsFromPoints(firstPos, pygame.mouse.get_pos())
            pygame.draw.rect(screen, selectedColor, [fp[0],fp[1],sp[0]-fp[0],sp[1]-fp[1]])

    def drawOutputImage():
        for i in range(256):
            for j in range(256):
                pygame.draw.rect(screen, outputarray[i][j], [256*2 + j*2, i*2, 2, 2])
        
        
    def gridToImage():
        grid = [[(0,0,0) for i in range(256)] for j in range(256)]
        for fp, sp, cl in drawings:
            for i in range(fp[0]//2,sp[0]//2+1):
                for j in range(fp[1]//2,sp[1]//2+1):
                    grid[i][j] = cl
        output_image = Image.fromarray(np.uint8(grid))
        output_image.save("drawing.jpg")
        
    def imageToGrid():
        imageFound = False
        try:
            image = Image.open("drawing.jpg")
            imageFound = True
        except:
            pass
        
        if not imageFound:
            return 
        
        imageout = np.asarray(image)
        for i in range(256):
            for j in range(256):
                outputarray[i][j] = tuple(imageout[i][j])

        
    # -------- Main Program Loop -----------
    while not done:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                posx,posy = pygame.mouse.get_pos()
                if 0 <= posx < 256*2 and 0 <= posy < 256*2:
                    # Is within board:
                    if not firstPointSelected:
                        # First point select
                        firstPointSelected = True
                        firstPos = (posx,posy)
                    else:
                        # In the process of a rectangle, save it with current color
                        firstPointSelected = False
                        secondPos = (posx,posy)
                        
                        rectstart,sizes = getRectsFromPoints(firstPos, secondPos)
                        drawings.append((rectstart, sizes, selectedColor))

                elif posy > 256*2:
                    ind = min(posx//40, len(colors)-1) # prevents index errors
                    selectedColor = colors[ind]


            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    # UNDO
                    if len(drawings) > 0:
                        drawings.pop()
                    else:
                        print("Nothing to undo!")
                elif event.key == pygame.K_SPACE:
                    gridToImage()
                elif event.key == pygame.K_LEFT:
                    imageToGrid()

        
        screen.fill(BLACK)
        
        drawColors()
        drawRectangles()
        drawOutputImage()
        
        # GUI
        pygame.draw.line(screen, (255,255,255), (256*2,0),(256*2,256*2+40))
        pygame.draw.line(screen, (255,255,255), (0, 256*2), (256*2, 256*2))
        

        
        # Blit to screen
        pygame.display.update()

        clock.tick(clocktick)

        
    
    # Close the window and quit.
    pygame.quit()

draw()