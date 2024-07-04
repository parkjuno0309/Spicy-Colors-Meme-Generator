from cmu_112_graphics import *
from PIL import ImageTk, Image
from classes import Tournament
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import random, string, re, requests, urllib

# gets images based on user search query input before game
def getImages(app):
    header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
    keyword = "".join(app.input)
    app.x = f"{keyword} meme"
    url = "https://imgur.com/search/score?q=%s"%(app.x)
    response = requests.get(url, headers = header)
    soup = BeautifulSoup(response.text, 'html.parser')
    app.images = re.findall('i[.]imgur[.]com/[0-9a-zA-z]{8}.jpg', str(soup))
    # exception for insufficient results
    """ if len(app.images) < app.size:
        app.noGood = True
        app.message = "Not Enough Image Results" """

# adds images to the tournament pool list
def addImages(app):
    for i in range(app.size):
        app.round.pool.append(app.images[i])

def appStarted(app):
    # ui parameters
    app.margin = app.height / (13 / 1.6)
    app.size = 8
    app.boardSize = app.height - 2 * app.margin
    app.boardMargin = app.boardSize / 15
    app.imgSize = 0.9 * app.boardSize
    app.alphabet = string.ascii_lowercase
    app.input = []
    
    # app states
    app.started = False
    app.selected = None
    app.gameOver = False
    app.selection = None
    app.message = "Type any keyword and press enter for not so spicy memes (try to keep it simple :))"

# creates new round of meme tournaments
def createRound(app):
    if app.started:
        # round pool parameters
        app.round = Tournament(app.size)
        getImages(app)
        addImages(app)
        random.shuffle(app.round.pool)
        app.round.createTwo(app.round.teamNum)

# key presses for input as well as restart command with 'r'
def keyPressed(app, event):
    # pre-game
    if not app.started:
        if event.key in app.alphabet:
            index = app.alphabet.find(event.key)
            app.input.append(app.alphabet[index])
            print(app.input)
        if event.key == "Space":
            app.input.append(" ")
            print(app.input)
        if event.key == "Backspace":
            app.input.pop()
            print(app.input)
        if event.key == "Enter":
            app.x = app.input
            app.started = True
            createRound(app)
    # in game
    else: 
        if event.key == "r":
            appStarted(app)

# mouse press detection on images
def mousePressed(app, event):
    if app.started:
        if not app.gameOver:
            # user selects left image
            bounds = getBounds(app)
            if (bounds['left'][0] < event.x < bounds['left'][2] and 
                bounds['left'][1] < event.y < bounds['left'][3]):
                app.selected = 'left'
                app.round.voteWinner(0)
                if len(app.round.winners) < app.round.size // 2:
                    app.round.nextTeam()
                    app.selection = None
            # user selects right image
            elif (bounds['right'][0] < event.x < bounds['right'][2] and 
                bounds['right'][1] < event.y < bounds['right'][3]):
                app.round.voteWinner(1)
                app.selected = 'right'
                if len(app.round.winners) < app.round.size // 2:
                    app.round.nextTeam()
                    app.selection = None
            if app.round.isLastStage():
                app.gameOver = True
                app.round.champion = app.round.winners.pop()
            elif len(app.round.winners) == app.round.size // 2:
                app.round.nextStage()

def redrawAll(app, canvas):
    drawBackground(app, canvas)
    if app.started:
        drawWinner(app, canvas)
        if not app.gameOver:
            drawTitle(app, canvas)
            drawStage(app, canvas)
            drawImageBoard(app, canvas)
            drawImages(app, canvas)
    else: drawSplash(app, canvas)

# draws title
def drawTitle(app, canvas):
    canvas.create_text(app.width // 2, app.margin // 4, text="Pick Your Spiciest Meme",
                            font="Arial 45 bold", fill= 'black')

# draws pre-game splash screen with input
def drawSplash(app, canvas):
    text = "".join(app.input)
    canvas.create_rectangle(app.width / 2 - 200, app.height / 2 - 30, 
                        app.width / 2 + 200, app.height / 2 + 30, 
                        fill = 'black')
    canvas.create_text(app.width / 2, app.height / 2, text = f"{text}",
                        font="Arial 30 bold", fill= 'white')
    canvas.create_text(app.width / 2, app.height / 2 - 100, text = app.message,
                        font="Arial 30 bold", fill= 'white')

# draws stage and round numbers
def drawStage(app, canvas):
    round = 2 ** (app.round.stages - app.round.stage + 1)
    canvas.create_text(app.width // 2, 3 * app.margin // 4, 
            text=f"Round of {round} Match {app.round.teamNum + 1}",
            font="Arial 45 bold", fill= 'black')

# draws black board behind image
def drawImageBoard(app, canvas):
    size = app.boardSize
    canvas.create_rectangle(app.margin, app.margin, app.margin + size, 
                            app.margin + size, fill = 'black')
    canvas.create_rectangle(app.width - app.margin - size, app.margin, 
                            app.width - app.margin, app.margin + size, 
                            fill = 'black')

# returns bounds of left and right images
def getBounds(app):
    size = app.imgSize
    bounds = {
    'left': [app.margin + app.boardMargin, app.margin + app.boardMargin, 
                            app.margin + app.boardMargin + size, 
                            app.margin + app.boardMargin + size],
    'right': [app.width - app.margin - app.boardMargin - size,
                            app.margin + app.boardMargin,
                            app.width - app.margin - app.boardMargin, 
                            app.margin + app.boardMargin + size]
            }
    return bounds

# draws winner when tournament round is over
def drawWinner(app, canvas):
    if app.gameOver:
        size = int(app.imgSize)
        link = f'http://{app.round.champion}'
        img = Image.open(requests.get(link, stream=True).raw)
        img = img.resize((size, size))
        # message
        canvas.create_text(app.width / 2, app. margin / 2, 
                            text = f"The spiciest {app.x} is...", 
                            font = "Arial 45 bold", fill = 'black')
        # image black board
        canvas.create_rectangle(app.width / 2 - app.boardSize / 2,
                                app.height / 2 - app.boardSize / 2,
                                app.width / 2 + app.boardSize / 2,
                                app.height / 2 + app.boardSize / 2, 
                                fill = 'black')
        # image
        canvas.create_image(app.width / 2, app.height / 2,
                        image = ImageTk.PhotoImage(img))

# draws images using links and image conversion from PIL to Tk
def drawImages(app, canvas):
    size = int(app.imgSize)
    link1 = f'http://{app.round.versus[0]}'
    link2 = f'http://{app.round.versus[1]}'
    img1 = Image.open(requests.get(link1, stream=True).raw)
    img2 = Image.open(requests.get(link2, stream=True).raw)
    img1, img2 = img1.resize((size, size)), img2.resize((size, size))
    canvas.create_image(app.margin + app.boardMargin + size / 2,
                        app.margin + app.boardMargin + size / 2,
                        image = ImageTk.PhotoImage(img1))
    canvas.create_image(app.width - app.margin - app.boardMargin - size / 2, 
                        app.margin + app.boardMargin + size / 2,
                        image = ImageTk.PhotoImage(img2))

# draws the amazing Kosbie background (created by: Ariel Kwak)
def drawBackground(app, canvas):
    background = Image.open("/Users/junopark/Documents/GitHub/Spicy-Colors-Meme-Generator/spicy colors/background.jpg")
    background = background.resize((app.width, app.height))
    canvas.create_image(app.width / 2, app.height / 2,
                        image = ImageTk.PhotoImage(background))

runApp(width=1280, height=720)