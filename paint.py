import pygame
from PIL import Image
import numpy as np



class App:

    def __init__(self):
        self.scaleAppX = 2
        self.scaleAppY = 2
        self.imageNameOut = 'drawng.png'
        self.imageNameIn = 'drawing.png'

        self.menuWidth = 125

    def draw(self) -> None:

        ##### PYGAME INIT ######
        pygame.init()
        size = (256*self.scaleAppX * 2 + self.menuWidth,256*self.scaleAppY)

        screen = pygame.display.set_mode(size)
        done = False
        clock = pygame.time.Clock()
        clocktick = 60
        font = pygame.font.Font(None, self.menuWidth//6)
        ########################

        ###### PROGRAM VARS ####

        drawings = []
        colors = [
            (0,6,217),              # BACKGROUND
            (14,60,251),            # WALL
            (165,1,0),              # DOOR
            (2,117,255),            # WINDOW
            (103,248,151),          # WINDOW SILL
            (30,255,221),           # WINDOW HEAD
            (238,236,40),           # SHUTTER
            (183,254,57),           # BALCONY
            (255, 146, 5),          # TRIM
            (254,67,4),             # CORNICE
            (245,2,0),              # COLUMN
            (0,201,255)             # ENTRANCE
        ]
        colorMeanings = ["Background", "Wall", "Door", "Window", "Window sill", "Window head", "Shutter",
                        "Balcony", "Trim", "Cornice", "Column", "Entrance"]

        firstPointSelected = False
        firstPos = None
        selectedColor = colors[0]
        outputarray = [[(0,0,0) for i in range(256)] for j in range(256)]
        
        #### HELP VARS #########
        # Color picking menu
        sizeY = 20
        margin = 5
        startpos = 20

        #### HELP FUNCTIONS ####
        def drawColors():
            pygame.draw.rect(screen, (255,255,255), [0,0,self.menuWidth,256*self.scaleAppY])
            # Draws color picker
            for i in range(len(colors)):
                # Draws the color
                if colors[i] == selectedColor:
                    pygame.draw.rect(screen, (0,0,0), [0,startpos + (margin+sizeY)*i,self.menuWidth,sizeY],1)
                pygame.draw.circle(screen, colors[i],(sizeY//2,(sizeY+margin)*i + sizeY//2 + startpos),sizeY//2)
                text = font.render(colorMeanings[i], True, (0,0,0))
                screen.blit(text, (sizeY,(sizeY+margin)*i + startpos))

        def getRectsFromPoints(x,y):
            # pygame is shitty with getting rectangles right
            # they should be from top left to bottom right
            leftup = (min(x[0],y[0]), min(x[1],y[1]))
            rightdown = (max(x[0],y[0]),max(x[1],y[1]))
            return leftup, rightdown

        def drawRectangles():
            pygame.draw.rect(screen, colors[0], [self.menuWidth, 0, 256*self.scaleAppX, 256*self.scaleAppY])
            # Draws drawn rectangles
            for firstpos, secondpos, color in drawings:
                pygame.draw.rect(screen, color, [firstpos[0],firstpos[1],secondpos[0]-firstpos[0],secondpos[1]-firstpos[1]])

            if firstPointSelected:
                p = list(pygame.mouse.get_pos())
                p[0] = max(p[0],self.menuWidth)
                fp, sp = getRectsFromPoints(firstPos, p)
                pygame.draw.rect(screen, selectedColor, [fp[0],fp[1],sp[0]-fp[0],sp[1]-fp[1]])

        def drawOutputImage():
            for i in range(256):
                for j in range(256):
                    pygame.draw.rect(screen, outputarray[i][j], [256*self.scaleAppX + j*self.scaleAppX + self.menuWidth, i*self.scaleAppY, self.scaleAppX, self.scaleAppY])
                
        def gridToImage():
            grid = [[colors[0] for i in range(256)] for j in range(256)]
            for fp, sp, cl in drawings:
                fp = [fp[0]-self.menuWidth,fp[1]]
                sp = [sp[0]-self.menuWidth,sp[1]]
                for i in range(fp[1]//self.scaleAppY,sp[1]//self.scaleAppY+1):
                    for j in range(fp[0]//self.scaleAppX,sp[0]//self.scaleAppX+1):
                        grid[i][j] = cl
            output_image = Image.fromarray(np.uint8(grid))
            output_image.save(self.imageNameOut)
            
        def imageToGrid():
            imageFound = False
            try:
                image = Image.open(self.imageNameIn)
                imageFound = True
            except:
                pass
            
            if not imageFound:
                return 
            
            imageout = np.asarray(image)
            for i in range(256):
                for j in range(256):
                    outputarray[i][j] = tuple(imageout[i][j])

        def drawGUI():
            # Dividing middle line input|output
            pygame.draw.line(screen, (255,255,255), (256*self.scaleAppX + self.menuWidth,0),(256*self.scaleAppX + self.menuWidth,256*self.scaleAppY))
            # Color menu | input
            pygame.draw.line(screen, (255,255,255), (self.menuWidth, 0), (self.menuWidth,self.scaleAppY*256))

               
        # -------- Main Program Loop -----------
        while not done:
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    posx,posy = pygame.mouse.get_pos()
                    if self.menuWidth <= posx < 256*self.scaleAppX + self.menuWidth and 0 <= posy < 256*self.scaleAppY:
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

                    elif posx <= self.menuWidth:
                        # Get starting pos off
                        posy -= startpos
                        ind = min(len(colors)-1, posy//(margin+sizeY))
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
                        

            
            screen.fill((0,0,0))
            
            drawColors()
            drawRectangles()
            drawOutputImage()
            drawGUI()

            # GUI
            

            # Blit to screen
            pygame.display.update()

            clock.tick(clocktick)

            
        
        # Close the window and quit.
        pygame.quit()




if __name__ == "__main__":
    app = App()
    app.draw()