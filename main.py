################################################################################
# main.py
#
# This file contains all the main game logic. It initializes the ghosts and
# provides a user interface.
#
# Name: Connor Frank
# Andrew ID: connorf
################################################################################


from boardObjs import *
from cmu_112_graphics import *
from ghostObjs import *


# set all the defaults for easy access here
def setDefaults(app):
    app.timerDelay = 300
    app.wallFill = "black"
    app.wallEdge = "blue"
    app.foodFill = "white"
    app.textColor = "white"
    app.wallThickness = 5
    app.margin = 30
    app.bottomSpace = 100
    app.cellSize = 50


# built-in function
def appStarted(app):
    app.view = app.prevView = 0
    setDefaults(app)
    # cherry source: https://www.pixilart.com/art/pac-man-cherry-79e94a34e56adb2
    app.fruit = app.loadImage("fruits/cherry.png")

    app.board = Board(
        app.width - 2 * app.margin,
        app.height - (app.margin + app.bottomSpace),
        app.cellSize,
    )
    app.pacmanRow = app.board.startRow
    app.pacmanCol = app.board.startCol
    app.pacmanDir = 0, 0
    app.nextDir = 0, 0
    app.pacmanChomp = True
    app.ghostEater = False
    app.ghostEaterCountdownStart = 15
    app.ghostEaterCountdown = app.ghostEaterCountdownStart
    app.win = False
    app.gameOver = False
    app.pause = False

    initGhosts(app)

    app.score = 0
    app.topScores = [0] * 9
    app.lives = 3
    app.numFruits = 0
    app.fruitCountdown = 50
    app.showFruit = False

    app.showSmallScore = False
    app.smallScoreCountdown = 0
    app.smallScorePos = 0, 0


# initialize all the ghosts
def initGhosts(app):
    app.ghosts = [Random(app.board)]
    app.ghosts.append(GreedyFront(app.board))
    app.ghosts.append(GreedyAt(app.board))
    app.ghosts.append(GreedyBehind(app.board))


# handle direction changes issued by WASD / arrows
def directionChange(app, dRow, dCol):
    prev = app.pacmanDir
    app.pacmanDir = dRow, dCol
    if not isValidMove(app, app.pacmanRow + dRow, app.pacmanCol + dCol):
        app.nextDir = app.pacmanDir
        app.pacmanDir = prev


# handle key presses
def keyPressed(app, event):
    if event.key == "h":
        app.pause = True
        app.view = 0
    elif event.key == "Escape":
        app.pause = not app.pause
        if app.view != 2:
            app.prevView = app.view
            app.view = 2
        else:
            app.view = app.prevView
        return

    if app.view == 0:
        if event.key == "Enter":
            topScores = app.topScores
            appStarted(app)
            app.topScores = topScores
            app.view = 1
    elif app.view == 1:
        if app.win and event.key == "n":
            score, topScores = app.score, app.topScores
            numFruits, lives = app.numFruits, app.lives
            appStarted(app)
            app.view = 1
            app.score, app.topScores = score, topScores
            app.numFruits, app.lives = numFruits, lives
        elif (app.gameOver and event.key == "n") or event.key == "r":
            topScores = app.topScores
            appStarted(app)
            app.topScores = topScores
            app.view = 1
        elif event.key == "Up" or event.key == "w":
            directionChange(app, -1, 0)
        elif event.key == "Down" or event.key == "s":
            directionChange(app, 1, 0)
        elif event.key == "Left" or event.key == "a":
            directionChange(app, 0, -1)
        elif event.key == "Right" or event.key == "d":
            directionChange(app, 0, 1)
    elif app.view == 2:
        if event.key == "Escape":
            app.view = 0


# returns whether a move is valid
def isValidMove(app, row, col):
    return app.board[row][col].pointVal >= 0


# initializes a small score on the board (not actually a class though)
def smallScoreInit(app, scoreAdd, countdown, row, col):
    app.score += scoreAdd
    app.smallScoreCountdown = countdown
    app.smallScorePos = row, col


# handles teleportation from one side to the other
def teleport(app, row, col):
    points = app.board[row][col].pointVal
    if points != 42:
        return row, col
    if col == 0:
        col = len(app.board[0]) - 1
    else:
        col = 0
    return row, col


# handles eating food and/or fruit
def eat(app):
    points = app.board[app.pacmanRow][app.pacmanCol].pointVal
    if points == 1:
        app.board[app.pacmanRow][app.pacmanCol] = Empty()
        app.score += points
        app.board.foodCount -= 1
    elif points == 2:  # magic food
        app.ghostEater = True
        app.ghostEaterCountdown = app.ghostEaterCountdownStart
        app.board[app.pacmanRow][app.pacmanCol] = Empty()
        app.board.foodCount -= 1
    elif points == 100:  # fruit
        smallScoreInit(app, 100, 4, app.pacmanRow, app.pacmanCol)
        app.numFruits += 1
        app.showFruit = False


# kills pacman when he collides with a ghost
def die(app):
    app.lives -= 1
    if app.lives == 0:
        app.gameOver = True
        app.topScores.append(app.score)
    app.pacmanRow = app.board.startRow
    app.pacmanCol = app.board.startCol
    app.pacmanDir = 0, 0
    initGhosts(app)


# refreshes the ghosts and checks for collisions
def refreshGhosts(app):
    for ghost in app.ghosts:
        if not ghost.jailed:
            dRow, dCol = app.pacmanDir
            if (ghost.row == app.pacmanRow and ghost.col == app.pacmanCol) or (
                ghost.row == app.pacmanRow + dRow
                and ghost.col == app.pacmanCol + dCol
            ):
                if app.ghostEater:
                    smallScoreInit(app, 100, 4, ghost.row, ghost.col)
                    ghost.resetJailTime()
                    ghost.row, ghost.col = app.board.ghostStarting
                else:
                    die(app)
                    return True
            # juggle the next row, prev row, and current row
            # this is the result of 1.5 hours of debugging and pain
            ghost.nextRow, ghost.nextCol = ghost.nextMove(app.board, app)
            ghost.nextRow, ghost.nextCol = teleport(
                app, ghost.nextRow, ghost.nextCol
            )
            ghost.prevRow, ghost.prevCol = ghost.row, ghost.col
            ghost.row, ghost.col = ghost.nextRow, ghost.nextCol
    return False


# sees whether pacman has won (no food left)
def checkForWin(app):
    if app.board.foodCount <= 0:
        app.win = True


# built-in function
def timerFired(app):
    if app.ghostEater:
        app.ghostEaterCountdown -= 1
        if app.ghostEaterCountdown == 0:
            app.ghostEater = False
            app.ghostEaterCountdown = app.ghostEaterCountdownStart
    if app.smallScoreCountdown > 0:
        app.showSmallScore = True
        app.smallScoreCountdown -= 1
    else:
        app.showSmallScore = False
    if not app.win and not app.gameOver:
        if not app.pause:
            app.pacmanChomp = not app.pacmanChomp
            app.fruitCountdown -= 1
            if app.fruitCountdown == 0:
                app.showFruit = True
            for ghost in app.ghosts:
                if ghost.jailTime == 0:
                    ghost.jailed = False
                else:
                    ghost.jailTime -= 1
            stop = refreshGhosts(app)
            # calculate next move and execute it
            if not stop:
                dRow, dCol = app.pacmanDir
                newRow = app.pacmanRow + dRow
                newCol = app.pacmanCol + dCol
                if isValidMove(app, newRow, newCol):
                    app.pacmanRow = newRow
                    app.pacmanCol = newCol
                    eat(app)
                else:
                    dRow, dCol = app.nextDir
                    newRow = app.pacmanRow + dRow
                    newCol = app.pacmanCol + dCol
                    if isValidMove(app, newRow, newCol):
                        app.pacmanRow = newRow
                        app.pacmanCol = newCol
                        eat(app)
                        app.pacmanDir = app.nextDir
                app.pacmanRow, app.pacmanCol = teleport(
                    app, app.pacmanRow, app.pacmanCol
                )
                checkForWin(app)
    elif app.win:
        app.wallEdge = "black" if app.wallEdge == "blue" else "blue"


# draws the board
def drawBoard(app, canvas):
    for i in range(len(app.board)):
        for j in range(len(app.board[i])):
            obj = app.board[i][j]
            x, y = app.board.getCenter(i, j, int(app.margin))
            r = obj.size
            if isinstance(obj, Wall):
                canvas.create_rectangle(
                    x - r,
                    y - r,
                    x + r,
                    y + r,
                    fill=app.wallFill,
                    outline=app.wallEdge,
                    width=app.wallThickness,
                )
            elif isinstance(obj, Food):
                canvas.create_oval(
                    x - r, y - r, x + r, y + r, outline=None, fill=app.foodFill
                )
            elif isinstance(obj, Teleportation):
                pass
            elif isinstance(obj, Fruit) and app.showFruit:
                drawFruit(app, canvas, x, y)


# draws a bar below the board
def drawBar(app, canvas):
    board = app.board
    middle, height = board.getCenter(
        board.rows - 1, (board.cols // 2) - 1, app.margin
    )
    height += (board.cellSize // 2) + app.margin
    canvas.create_text(
        app.margin,
        height,
        text=f"SCORE: {app.score}",
        font="Arial 40 bold",
        fill=app.textColor,
        anchor="nw",
    )
    canvas.create_text(
        middle,
        height,
        text=f"LIVES: {app.lives}",
        font="Arial 40 bold",
        fill=app.textColor,
        anchor="nw",
    )
    drawFruitCounter(app, canvas)


# draws a fruit either on the board or on the bar
def drawFruit(app, canvas, x, y, anchor=None):
    if anchor is None:
        # fruit is being placed on board
        size = 1 / 20
        y += 9
    else:
        size = 1 / 10
    fruit = app.scaleImage(app.fruit, size)
    canvas.create_image(x, y, image=ImageTk.PhotoImage(fruit), anchor=anchor)


# draws a counter on the board next to the fruit
def drawFruitCounter(app, canvas):
    board = app.board
    x, y = board.getCenter(board.rows, board.cols - 2, app.margin)
    x -= app.margin
    y += (board.cellSize // 2) + app.margin
    drawFruit(app, canvas, x, y, anchor="w")
    canvas.create_text(
        x,
        y - 20,
        text=f"{app.numFruits} x",
        font="Arial 25 bold",
        fill=app.textColor,
        anchor="e",
    )


# draws pacman
def drawPacman(app, canvas):
    x, y = app.board.getCenter(app.pacmanRow, app.pacmanCol, app.margin)
    r = app.cellSize // 2
    r *= 0.8
    canvas.create_oval(x - r, y - r, x + r, y + r, fill="yellow")
    arcCoord = x - r, y - r, x + r, y + r
    size = 40 if app.pacmanChomp else 90
    if app.pacmanDir == (-1, 0):
        angle = 90 - (size / 2)
    elif app.pacmanDir == (1, 0):
        angle = 270 - (size / 2)
    elif app.pacmanDir == (0, -1):
        angle = 180 - (size / 2)
    elif app.pacmanDir == (0, 1):
        angle = 0 - (size / 2)
    else:
        return
    canvas.create_arc(arcCoord, start=angle, extent=size, fill="black")


# draws ghosts onto the board
def drawGhosts(app, canvas):
    r = app.cellSize // 2
    r *= 0.8
    for ghost in app.ghosts:
        if not ghost.jailed:
            x, y = app.board.getCenter(ghost.row, ghost.col, app.margin)
            color = "purple" if app.ghostEater else ghost.color
            canvas.create_rectangle(x - r, y - r, x + r, y + r, fill=color)


# draws a "you win" message
def drawYouWin(app, canvas):
    winID = canvas.create_text(
        app.width // 2,
        app.height // 2,
        text="You Win!".center(31) + "\nPress 'n' to play again!",
        font="Arial 25 bold",
        fill="white",
    )
    winX0, winY0, winX1, winY1 = canvas.bbox(winID)
    canvas.create_rectangle(
        winX0, winY0, winX1, winY1, fill="black", outline="black", width=10
    )
    canvas.create_text(
        app.width // 2,
        app.height // 2,
        text="You Win!".center(31) + "\nPress 'n' to play again!",
        font="Arial 25 bold",
        fill="white",
    )


# draws a "game over" message
def drawGameOver(app, canvas):
    winID = canvas.create_text(
        app.width // 2,
        app.height // 2,
        text="GAME OVER.".center(28) + "\nPress 'n' to play again!",
        font="Arial 25 bold",
        fill="white",
    )
    winX0, winY0, winX1, winY1 = canvas.bbox(winID)
    canvas.create_rectangle(
        winX0, winY0, winX1, winY1, fill="black", outline="black", width=10
    )
    canvas.create_text(
        app.width // 2,
        app.height // 2,
        text="GAME OVER.".center(28) + "\nPress 'n' to play again!",
        font="Arial 25 bold",
        fill="white",
    )


# draws a small score onto the board when pacman eats a ghost/fruit
def drawSmallScore(app, canvas):
    row, col = app.smallScorePos
    x, y = app.board.getCenter(row, col, app.margin)
    canvas.create_text(x, y, text="100", font="Arial 10", fill="white")


# starting view
def startView(app, canvas):
    canvas.create_text(
        app.width // 2,
        app.height // 4,
        text="Pacman++",
        font="Arial 100 bold",
        fill="yellow",
    )
    usage = (
        "Use WASD or arrow keys to move pacman\n"
        "Press 'h' (help) at any time to return to this menu\n"
        "Press escape to view top scores\n"
        "Press enter to begin the game"
    )
    canvas.create_text(
        app.width // 2,
        app.height // 2,
        text=usage,
        font="Arial 25 bold",
        fill="white",
    )
    canvas.create_text(
        app.width // 2,
        (app.height * 3) // 4,
        text="Good luck!",
        font="Arial 60 bold",
        fill="blue",
    )


# normal view
def normalView(app, canvas):
    drawBar(app, canvas)
    drawBoard(app, canvas)
    drawPacman(app, canvas)
    drawGhosts(app, canvas)
    if app.showSmallScore:
        drawSmallScore(app, canvas)
    if app.win:
        drawYouWin(app, canvas)
    elif app.gameOver:
        drawGameOver(app, canvas)


# highscore view
def showTopScores(app, canvas):
    if app.topScores == ([0] * 9):
        canvas.create_text(
            app.width // 2,
            app.height // 2,
            text="No top scores yet.",
            font="Arial 50 bold",
            fill="white",
        )
        return
    scores = sorted(app.topScores)[::-1]
    height = app.height // 10
    for score in scores[:9]:
        canvas.create_text(
            app.width // 2,
            height,
            text=score,
            font="Arial 50 bold",
            fill="white",
        )
        height += app.height // 10


# built-in function
def redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, fill="black")
    if app.view == 0:
        startView(app, canvas)
    elif app.view == 1:
        normalView(app, canvas)
    elif app.view == 2:
        showTopScores(app, canvas)


if __name__ == "__main__":
    runApp(width=915, height=950)
