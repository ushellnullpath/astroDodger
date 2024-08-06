'''
Project: astroDodger
By: ushellnullpath
Description:
A vertical scroller game that uses hand gestures for player movements using computer vision. 
Last updated on (D/M/Y): 06/08/2024
'''

from tkinter import *
from PIL import ImageTk, Image
from os.path import join
from game import Game
import webbrowser


# Functions
def start_win_move(event):
    root.x = event.x
    root.y = event.y


def stop_win_move(event):
    root.x = None
    root.y = None


def win_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")


def openlink():
    webbrowser.open(
        "https://github.com/ushellnullpath/astroDodger/blob/main/LICENSE")


def create_button(parent, text, bg_color, fg_color, command, **kwargs):
    """Create and return a styled button."""
    def hover_on(event):
        button['background'] = bg_color
        button['foreground'] = fg_color

    def hover_off(event):
        button['background'] = fg_color
        button['foreground'] = bg_color

    button = Button(
        parent,
        text=text,
        foreground=bg_color,
        background=fg_color,
        activeforeground=fg_color,
        activebackground=bg_color,
        command=command,
        border=0,
        **kwargs
    )
    button.bind("<Enter>", hover_on)
    button.bind("<Leave>", hover_off)
    return button


def start_game():
    """Starts the astroDodger game"""
    root.destroy()
    game = Game()
    game.start()


def enable_start_button():
    """Enable the start buttononly if the Term's consent checkbox is checked."""
    if consent_var.get():
        start_button.config(state=NORMAL)
    else:
        start_button.config(state=DISABLED)


# Main window setup
root = Tk()
root.overrideredirect(True)
root.attributes('-topmost', True)
root.title("astroDodger by ushellnullpath")
root.iconbitmap(join('images', 'favicon1.ico'))

# Window dimensions and position
width_of_win = 300
height_of_win = 490
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coord = ((screen_width/2) - (width_of_win/2))
y_coord = ((screen_height/2) - (height_of_win/2))
root.geometry(('%dx%d+%d+%d') %
              (width_of_win, height_of_win, x_coord, y_coord))
root.configure(background='#1f1e28')

# Binding the mouse events
root.bind("<ButtonPress-1>", start_win_move)
root.bind("<ButtonRelease-1>", stop_win_move)
root.bind("<B1-Motion>", win_move)

# Logo setup
logo = Image.open(join('images', 'logo1.png'))
resized_logo = logo.resize((260, 155))
logo_symbol = ImageTk.PhotoImage(resized_logo)
logo_screen = Label(root, image=logo_symbol,
                    background='#1f1e28').place(x=15, y=25)

# Frame setup
frame1 = LabelFrame(root, text=' HOW  TO  PLAY ', font=(
    'System', 14), foreground='#ffffff', background='#1f1e28', labelanchor='n')
frame1.place(x=25, y=200)

# Message box setup
splash_msg = Message(frame1, text='To play the game, you\'ll need to use your webcam and guide the spaceship with your hand/index finger while avoiding the asteroids. Amp up your defenses by collecting shields to safeguard yourself from these obstacles.',
                     font=('System', 11),
                     foreground='#ffffff',
                     background='#1f1e28',
                     aspect=200,
                     justify=CENTER)
splash_msg.pack()

# Terms consent checkbox setup
consent_var = IntVar()
consent_checkbox = Checkbutton(root, text="I consent to granting the application access to my webcam.",
                               variable=consent_var, onvalue=1, offvalue=0,
                               command=enable_start_button,
                               foreground='#ffffff', background='#1f1e28',
                               activeforeground='#ffffff', activebackground='#1f1e28',
                               selectcolor='#000000',
                               font=('System', 11), wraplength=255, justify=LEFT)
consent_checkbox.place(x=18, y=350)

# Create buttons
start_button = create_button(root, "-  START  GAME  -", "#ffffff",
                             "#000000", start_game, width=17, height=2, font=('System', 14))
start_button.place(x=24, y=400)
start_button.config(state=DISABLED)

exit_button = create_button(root, "❌", "#ffffff", "#000000",
                            root.destroy, width=5, height=2, font=('System', 14))
exit_button.place(x=221, y=400)

terms_bttn = Button(root, text="astroDodger Terms",
                    font=('System', 10, "underline"),
                    fg="#ffffff", bg="#1f1e28",
                    activeforeground="#ffffff", activebackground="#1f1e28",
                    cursor="hand2", bd=0,
                    command=openlink)
terms_bttn.place(relx=0.50, rely=0.96, anchor=CENTER)

root.mainloop()
