import pygame

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
    selectedColor = colors[0]
    
    def drawColors():
        # Draws color picker
        for i in range(len(colors)):
            pygame.draw.rect(screen, colors[i], [i*40, 256*2, 40, 40])
            if colors[i] == selectedColor:
                pygame.draw.rect(screen, (255,255,255), [i*40, 256*2, 40, 40], 2)

    def drawLines():
        for i in range(256):
            for j in range(256):
                pygame.draw.rect(screen, grid[i][j], [j*2,i*2,2,2])


    drawing = False

    grid = [[0 for i in range(256)] for j in range(256)]
    linesdrawn = []


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
                    drawing = True
                    linesdrawn.append(selectedColor)
                    linesdrawn.append(set())


                elif posy > 256*2:
                    ind = min(posx//40, len(colors)-1) # prevents index errors
                    selectedColor = colors[ind]
                    print(selectedColor)

            elif event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                print(linesdrawn)
            elif event.type == pygame.MOUSEMOTION:
                if drawing:
                    linesdrawn[-1].add(pygame.mouse.get_pos())





            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    # UNDO
                    if len(linesdrawn) > 0:
                        linesdrawn.pop()
                        linesdrawn.pop()
                    else:
                        print("Nothing to undo!")


        
        screen.fill(BLACK)
        
        drawColors()
        drawGrid()
        # GUI
        pygame.draw.line(screen, (255,255,255), (256*2,0),(256*2,256*2+40))
        pygame.draw.line(screen, (255,255,255), (0, 256*2), (256*2, 256*2))
        

        
        # Blit to screen
        pygame.display.update()

        clock.tick(clocktick)

        
    
    # Close the window and quit.
    pygame.quit()

draw()