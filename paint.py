import pygame
from PIL import Image
import numpy as np
from os import listdir, remove
from os.path import isfile, join
from random import choice
import sys
import shutil

sys.path.insert(0,"./model")
from model import get_image


class App:

    def __init__(self):
        self.scaleAppX = 2
        self.scaleAppY = 2
        self.imageNameOut = 'drawing'
        self.imageNameIn = 'drawing'

        self.menuWidth = 125
        self.picture = None

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
        cursor = 0
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

        input_active = False
        currentfunc = None
        text = ""
        blink = 0
        maxblink = 50
        showBlink = True

        shouldUpdate = True
        overlayActive = False

        ####### ICONS #########

        icons = {
            "undo": pygame.image.load("./assets/undo.png"),
            "redo": pygame.image.load("./assets/redo.png"),
            "clear": pygame.image.load("./assets/clear.png"),
            "import": pygame.image.load("./assets/import.png"),
            "save": pygame.image.load("./assets/save.png"),
            "random": pygame.image.load("./assets/random.png"),
        }
        
        #### HELP VARS #########
        # Color picking menu
        sizeY = 20
        margin = 5
        startpos = 20

        #### HELP FUNCTIONS ####
        def drawColors():
            """
            Draw color menu
            """
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
            """
            Transforms 2 points such that pygame can understand them
            """
            # pygame is shitty with getting rectangles right
            # they should be from top left to bottom right
            leftup = (min(x[0],y[0]), min(x[1],y[1]))
            rightdown = (max(x[0],y[0]),max(x[1],y[1]))
            return leftup, rightdown

        def drawRectangles():
            """
            Draws every element currently in cache (drawings)
            """
            pygame.draw.rect(screen, colors[0], [self.menuWidth, 0, 256*self.scaleAppX, 256*self.scaleAppY])
            # Draws drawn rectangles
            for i in drawings[:cursor]:
                try:
                    firstpos, secondpos, color = i
                    pygame.draw.rect(screen, color, [firstpos[0],firstpos[1],secondpos[0]-firstpos[0],secondpos[1]-firstpos[1]])
                except: # imported picture
                    randomimage = pygame.transform.scale(i[list(i.keys())[0]], (256*self.scaleAppX, 256*self.scaleAppY))
                    rect = randomimage.get_rect()
                    rect = rect.move((self.menuWidth, 0))
                    screen.blit(randomimage, rect)

            if firstPointSelected:
                p = list(pygame.mouse.get_pos())
                p[0] = min(max(p[0],self.menuWidth),self.menuWidth + 256*self.scaleAppX)
                fp, sp = getRectsFromPoints(firstPos, p)
                pygame.draw.rect(screen, selectedColor, [fp[0],fp[1],sp[0]-fp[0],sp[1]-fp[1]])
   
        def gridToImage():
            """
            Saves an image of your work as well as a cache file to retrieve it later to work on
            """
            # Image drawing
            grid = [[colors[0] for i in range(256)] for j in range(256)]
            for i in range(256):
                for j in range(256):
                    grid[i][j] = screen.get_at((self.menuWidth + j * self.scaleAppX, i * self.scaleAppY))


            output_image = Image.fromarray(np.uint8(grid)).convert('RGB')
            output_image.save("./drawings/"+self.imageNameOut+".jpg")
            
            # Image result
            shutil.copy("./drawings/~wcache.out.jpg", "./drawings/"+self.imageNameOut+".out.jpg")

            # Undo
            with open("./drawings/"+self.imageNameOut+".cache.txt","w+") as f:
                print(drawings)
                for item in drawings[:cursor]:
                    if type(item) == tuple:
                        a,b,c = item
                        f.write(' '.join([str(x) for x in a]) + " " + ' '.join([str(x) for x in b]) + " " + ' '.join([str(x) for x in c]) + "\n")
                    else:
                        print(item)
                        f.write(list(item.keys())[0]+"\n")
        
        def importWork():
            """
            Imports cache file 
            """
            lst = []
            with open("./drawings/"+self.imageNameIn+".cache.txt","r") as f:
                lines = [x.rstrip() for x in f.readlines()]
                for i in lines:
                    try:
                        # Try to extract numbers, else, its a file name
                        entry = [int(x) for x in i.split()]
                        entry = ((entry[0],entry[1]),(entry[2],entry[3]),(entry[4],entry[5],entry[6]))
                        lst.append(entry)
                    except:
                        lst.append({i:pygame.image.load("./random/"+i)})
            return lst

        def drawResult():
            """
            Draws the picture the model has made
            """
            if self.picture != None:
                picture = pygame.transform.scale(self.picture, (256*self.scaleAppX, 256*self.scaleAppY))
                rect = picture.get_rect()
                rect = rect.move((256*self.scaleAppX + self.menuWidth, 0))
                screen.blit(picture, rect)
            
        def drawGUI():
            """
            Draws few lines and icons
            """
            # Dividing middle line input|output
            pygame.draw.line(screen, (255,255,255), (256*self.scaleAppX + self.menuWidth,0),(256*self.scaleAppX + self.menuWidth,256*self.scaleAppY))
            # Color menu | input
            pygame.draw.line(screen, (255,255,255), (self.menuWidth-1, 0), (self.menuWidth-1,self.scaleAppY*256))

            # Icons
            
            starty = (sizeY+margin)*len(colors) + startpos

            icon = icons["redo"]
            icon = pygame.transform.scale(icon, (self.menuWidth//2,self.menuWidth//2))
            screen.blit(icon,(0,starty))
            icon = icons["undo"]
            icon = pygame.transform.scale(icon, (self.menuWidth//2,self.menuWidth//2))
            screen.blit(icon,(self.menuWidth//2,starty))
            icon = icons["save"]
            icon = pygame.transform.scale(icon, (self.menuWidth//2,self.menuWidth//2))
            screen.blit(icon,(0,starty + self.menuWidth//2))
            icon = icons["import"]
            icon = pygame.transform.scale(icon, (self.menuWidth//2,self.menuWidth//2))
            screen.blit(icon,(self.menuWidth//2,starty+self.menuWidth//2))
            icon = icons["clear"]
            icon = pygame.transform.scale(icon, (self.menuWidth//2,self.menuWidth//2))
            screen.blit(icon,(0,starty + 2*self.menuWidth//2))
            icon = icons["random"]
            icon = pygame.transform.scale(icon, (self.menuWidth//2,self.menuWidth//2))
            screen.blit(icon,(self.menuWidth//2,starty + 2*self.menuWidth//2))
        
        def drawOverlay():
            s = pygame.Surface((256*self.scaleAppX,256*self.scaleAppY))        # the size of your rect
            s.set_alpha(64) 

            pygame.draw.rect(s, colors[0], [0, 0, 256*self.scaleAppX, 256*self.scaleAppY])
            # Draws drawn rectangles
            for i in drawings[:cursor]:
                try:
                    firstpos, secondpos, color = i
                    pygame.draw.rect(s, color, [firstpos[0]-self.menuWidth,firstpos[1],secondpos[0]-firstpos[0],secondpos[1]-firstpos[1]])
                except: # imported picture
                    randomimage = pygame.transform.scale(i[list(i.keys())[0]], (256*self.scaleAppX, 256*self.scaleAppY))
                    rect = randomimage.get_rect()
                    rect = rect.move((0, 0))
                    s.blit(randomimage, rect)

            if firstPointSelected:
                p = list(pygame.mouse.get_pos())
                p[0] = min(max(p[0],self.menuWidth),self.menuWidth + 256*self.scaleAppX)
                fp, sp = getRectsFromPoints(firstPos, p)
                pygame.draw.rect(s, selectedColor, [fp[0],fp[1],sp[0]-fp[0],sp[1]-fp[1]])
            
            screen.blit(s,(self.menuWidth+256*self.scaleAppX,0))

        #### BUTTON FUNCTIONS ##
        def clearDrawings():
            """
            Clears cache
            """
            # remove all drawings
            drawings.clear()

        def generateModelImage():
            """
            Model stub: should import image generated by model
            """
            # Save image: gridToImage()
            
            grid = [[colors[0] for i in range(256)] for j in range(256)]

            for i in range(256):
                for j in range(256):
                    grid[i][j] = screen.get_at((self.menuWidth + j * self.scaleAppX, i * self.scaleAppY))


            output_image = Image.fromarray(np.uint8(grid)).convert('RGB')
            output_image.save("./drawings/~wcache.jpg")
            
            # Pass image:
            get_image('~wcache.jpg')

            # generated image load:

            try:
                # Image
                self.picture = pygame.image.load("./drawings/~wcache.out.jpg")
            except Exception as e:
                print(e)

        def getRandom():
            """
            Gets random image from /random
            """
            onlyfiles = [f for f in listdir('./random/') if isfile(join('./random', f))]
            file = choice(onlyfiles)
            drawings.append({file:pygame.image.load("./random/"+file)})
        
        def inputText():
            """
            Text input once importing or exporting
            """
            # Alpha layer
            s = pygame.Surface(size)        # the size of your rect
            s.set_alpha(128)                # alpha level
            s.fill((255,255,255))           # this fills the entire surface
            screen.blit(s, (0,0))           # (0,0) are the top-left coordinates

            textFont = pygame.font.Font(None, 30*self.scaleAppX)
            if showBlink:
                text_surf = textFont.render(text+"|.jpg", True, (0, 0, 0))
            else:
                text_surf = textFont.render(text+".jpg", True, (0, 0, 0))
            screen.blit(text_surf, text_surf.get_rect(center = (self.menuWidth + (256*self.scaleAppX)//2, size[1]//2)))


        # -------- Main Program Loop -----------
        while not done:
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    try:
                        remove("./drawings/~wcache.jpg")
                        remove("./drawings/~wcache.out.jpg")
                    except:pass
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
                            drawings[cursor:] = []
                            drawings.append((rectstart, sizes, selectedColor))
                            cursor += 1

                            # for automatic image generation:
                            shouldUpdate = True

                    elif posx <= self.menuWidth and posy <= (sizeY+margin)*len(colors) + startpos:
                        # Get starting pos off
                        posy -= startpos
                        ind = min(len(colors)-1, posy//(margin+sizeY))
                        selectedColor = colors[ind]

                    elif posx <= self.menuWidth and posy > (sizeY+margin)*len(colors) + startpos:
                        starty = posy - ((sizeY+margin)*len(colors) + startpos)
                        if posx <= self.menuWidth//2:
                            iconpos = starty//(self.menuWidth//2)
                            if iconpos == 0: #REDO
                                if cursor < len(drawings):
                                    cursor += 1
                                    shouldUpdate = True
                                else:
                                    print("Nothing to redo!")
                            elif iconpos == 1: #SAVE
                                input_active = True
                                currentfunc = "save"
                                text = ""
                            elif iconpos == 2: #CLEAR
                                clearDrawings()
                                shouldUpdate = True
                                cursor = 0
                        else:
                            iconpos = starty//(self.menuWidth//2)
                            if iconpos == 0: # UNDO
                                if cursor > 0:
                                    cursor -= 1
                                    shouldUpdate = True
                                else:
                                    print("Nothing to undo!")
                            elif iconpos == 1: #IMPORT
                                input_active = True
                                currentfunc = "import"
                                text = ""
                            elif iconpos == 2: #RANDOM
                                drawings[cursor:] = []
                                getRandom()
                                cursor += 1
                                shouldUpdate = True
                    
                    elif posx >= self.menuWidth + self.scaleAppX*256:
                        # Overlay
                        overlayActive = not overlayActive

                elif event.type == pygame.KEYDOWN and input_active: 
                    # For the input bar
                    showBlink = True
                    blink = 0
                    if event.key == pygame.K_RETURN:
                        input_active = False
                        shouldUpdate = True
                    elif event.key == pygame.K_BACKSPACE:
                        text =  text[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        input_active = False
                        currentfunc = None
                    else:
                        text += event.unicode
                        
            
            screen.fill((0,0,0))

            drawColors()
            drawRectangles()
            drawResult()
            drawGUI()

            if shouldUpdate:
                shouldUpdate = False
                generateModelImage()

            if input_active:
                blink = blink + 1
                if blink > maxblink:
                    blink = 0
                    showBlink = not showBlink
                inputText()
            elif currentfunc != None:
                if currentfunc == "save":
                    self.imageNameOut = text
                    gridToImage()
                elif currentfunc == "import":
                    self.imageNameIn = text
                    drawings = importWork()
                    cursor = len(drawings)
                    shouldUpdate = True
                    
                currentfunc = None
            
            if overlayActive:
                drawOverlay()

            # Blit to screen
            pygame.display.update()
            clock.tick(clocktick)
            
        
        # Close the window and quit.
        pygame.quit()




if __name__ == "__main__":
    app = App()
    app.draw()