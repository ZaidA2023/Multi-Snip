from PIL import Image, ImageGrab
import pytesseract as tess
import numpy as nm
import tkinter as tk
from tkinter import *
import pyperclip as pc
import pyautogui
import PySimpleGUI as sg
import wn
import string
import json
from revChatGPT.ChatGPT import Chatbot

#Loads in Session token from .json file and activates it
conf = json.load(open("chatgpt.json"))
chatbot = Chatbot(conf)
#Points to OCR program
tess.pytesseract.tesseract_cmd = "C:/Users/zaid2/Tesseract-OCR/tesseract.exe"
en = wn.Wordnet('oewn:2021')
#Initializes global variables
x = False
res = True
userinput=""
type = "no"
#Function to capture highlighted part of screen
#Second half recognizes type of info highlighted and generates an appropriate response
def take_bounded_screenshot(self,x1, y1, x2, y2):
    global type
    image = pyautogui.screenshot(region=(x1, y1, x2, y2))
    text = (tess.image_to_string(image)).strip()
    pc.copy(text)
    print(text)
    synonyms = []
    synonyms.append("")
    definitions = []
    definitions.append("")
    synonyms.clear()
    definitions.clear()
    self.exit_screenshot_mode()  
    try:
        print(eval(text))
        sg.popup(eval(text))
        return
    except SyntaxError:
        print
    except NameError:
        print

    res = any(chr.isdigit() for chr in text)
    if res == False: 
        text = text.translate(str.maketrans('','',string.punctuation))
        x = True
        print(x)
        print(text)
    if len(text.split()) > 1:
        sg.popup("I can only process one word at a time")
    elif((text).isalnum()):
        PopUp()
        print(type)
        if type != "p": 
            try:
                ss = en.synsets(text, pos = type)
            except: IndexError
            for ss in wn.synsets(text):
                definitions.append(ss.definition()) 
                definitions.append("\n")
                synonyms = synonyms + ss.lemmas()
            if definitions: 
                synonyms = list(set(synonyms))
                definitions = list(set(definitions))
                sg.popup("Definitions: "+"\n"+'\n'.join(definitions)+"\n"+"\n"+"Synonyms: " + "\n"+ ', '.join(synonyms))
            else: sg.popup("Sorry, try again")

#Sets fonts for the GUI
LARGE_FONT= ("Verdana", 12)
NORM_FONT= ("Verdana", 10)
SMALL_FONT= ("Verdana", 8)

    
class Application():
    #Function that asks ChatGPT question and gives user response
    def retrieve_input(self):
        global userinput
        input = self.textBox.get("1.0",'end-1c')
        ans = chatbot.ask(input)
        print(ans)
        sg.popup(ans['message'])

    #Initial UI make and tells buttons their jobs
    def __init__(self, master):
        global userinput
        self.snip_surface = None
        self.master = master
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.create_screen_canvas
        root.geometry('200x250+200+200')  #  8675*6745/5     BACK   MAGIC
        root.title('Snip')
        

        self.menu_frame = Frame(master)
        self.menu_frame.pack(fill=BOTH, expand=YES, padx=1, pady=1)

        self.buttonBar = Frame(self.menu_frame, bg="")
        self.buttonBar.pack()

        self.snipButton = Button(self.buttonBar, width=15, height=5, command=self.create_screen_canvas, background="green", text="Click to Snip")
        self.textBox = Text(root, height=2, width =10)
        self.textBox.pack()
        buttonCommit=Button(root, height=1, width=10, text="Search", command=lambda: self.retrieve_input(),)
        buttonCommit.pack()
        self.snipButton.pack()

        self.master_screen = Toplevel(root)
        self.master_screen.withdraw()
        self.master_screen.attributes("-transparent", "maroon3")
        self.picture_frame = Frame(self.master_screen, background="maroon3")
        self.picture_frame.pack(fill=BOTH, expand=YES)
    
    #Creates a transparent screen and hides initial UI
    def create_screen_canvas(self):
        self.master_screen.deiconify()
        root.withdraw()
        self.snip_surface = Canvas(self.picture_frame, cursor="cross", bg="grey11")
        self.snip_surface.pack(fill=BOTH, expand=YES)

        self.snip_surface.bind("<ButtonPress-1>", self.on_button_press)
        self.snip_surface.bind("<B1-Motion>", self.on_snip_drag)
        self.snip_surface.bind("<ButtonRelease-1>", self.on_button_release)

        self.master_screen.attributes('-fullscreen', True)
        self.master_screen.attributes('-alpha', .3)
        self.master_screen.lift()
        self.master_screen.attributes("-topmost", True)

    #Tracks coordinates of mouse and uses math to find the x1,x2,y1,y2 of snipping rectangle
    def on_button_release(self, event):

        if self.start_x <= self.current_x and self.start_y <= self.current_y:
            #right down
            take_bounded_screenshot(self, self.start_x, self.start_y, self.current_x - self.start_x, self.current_y - self.start_y)

        elif self.start_x >= self.current_x and self.start_y <= self.current_y:
            #left down
            take_bounded_screenshot(self, self.current_x, self.start_y, self.start_x - self.current_x, self.current_y - self.start_y)

        elif self.start_x <= self.current_x and self.start_y >= self.current_y:
            #right up
            take_bounded_screenshot(self, self.start_x, self.current_y, self.current_x - self.start_x, self.start_y - self.current_y)

        elif self.start_x >= self.current_x and self.start_y >= self.current_y:
            #left up
            take_bounded_screenshot(self, self.current_x, self.current_y, self.start_x - self.current_x, self.start_y - self.current_y)

        self.exit_screenshot_mode()
        return event

    #Destroys the transparent screen and shows UI
    def exit_screenshot_mode(self):
        self.snip_surface.destroy()
        self.master_screen.withdraw()
        root.deiconify()

    #Saves mouse drag start position
    def on_button_press(self, event):
        self.start_x = self.snip_surface.canvasx(event.x)
        self.start_y = self.snip_surface.canvasy(event.y)
        self.snip_surface.create_rectangle(0, 0, 1, 1, outline='red', width=3, fill="maroon3")

    #Expands rectangle as you drag the mouse
    def on_snip_drag(self, event):
        self.current_x, self.current_y = (event.x, event.y)
        self.snip_surface.coords(1, self.start_x, self.start_y, self.current_x, self.current_y)


def block_focus(window):
    for key in window.key_dict: 
        element = window[key]
        if isinstance(element, sg.Button):
            element.block_focus()

#Customizes part of speech popup, records response, and sends it
def PopUp():
    global type
    def popup_choice(speech):
        print(speech)
        if(speech=="Copy Text"): 
            return "p"
        if(speech=="Noun"):  
            return "n"
        elif(speech=="Verb"):
            return "v"
        elif(speech=="Adverb"):
            return "r"
        elif(speech=="Adjective"):
            return "a"
        elif(speech=="Conjunction"):
            return "c"
        else: return "u"

    items = [
        "Noun", "Verb", "Adjective", " Adverb", "Conjunction", "I don't know", "Copy Text"
    ]
    length = len(items)
    size = (max(map(len, items)), 1)

    sg.theme("DarkBlue3")
    sg.set_options(font=("Courier New", 11))

    column_layout = []
    line = []
    num = 4
    for i, item in enumerate(items):
        line.append(sg.Button(item, size=size, metadata=False))
        if i%num == num-1 or i==length-1:
            column_layout.append(line)
            line = []

    layout = [
        [sg.Text('Choose a part of speech')],
        [sg.Column(column_layout)],
    ]
    window=sg.Window("Word Picker", layout, use_default_focus=False, finalize=True)
    block_focus(window)

    sg.theme("DarkGreen3")
    while True:

        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event in items:
            speech = event
            type = popup_choice(speech)
            break

    window.close()

if __name__ == '__main__':
    root = Tk()
    app = Application(root)
    root.mainloop()