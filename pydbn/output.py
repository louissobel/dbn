from PIL import Image, ImageTk
import Tkinter
import ttk


import dbn
import sys
import os
from tokenizer import DBNTokenizer
import parser
import time

import dbngui

def animate_state(state, direction):
    master = Tkinter.Tk()

    w = Tkinter.Canvas(master, width=302, height=302)
    w.pack()
    

    w.create_rectangle(49, 49, 252, 252)
    
    
    def draw_state(state, canvas_image):
        image = state.image._image
        tkinter_image = ImageTk.PhotoImage(image.resize((202, 202)))

        if canvas_image is None:    
            canvas_image = w.create_image((151,151), image=tkinter_image, anchor='center', tag='frame')
        else:
            w.itemconfigure(canvas_image, image=tkinter_image)
        w.tkinter_image = tkinter_image
        
        if getattr(state, direction, None) is not None:
            master.after(1, draw_state, getattr(state, direction, None), canvas_image)


    master.after(10, draw_state, state, None)
    master.mainloop()


def draw_window(interpreter):
    TIMEOUT = 10
    master = Tkinter.Tk()

    w = Tkinter.Canvas(master, width=302, height=302)
    w.pack()

    w.create_rectangle(49, 49, 252, 252)
    im = w.create_image((151,151), anchor='center')
    
    def check_draw():
        #racy
        #if image_adapter.new:
        tkinter_image = ImageTk.PhotoImage(interpreter.image._image.resize((202, 202)))

        w.image = tkinter_image
        w.itemconfigure(im, image=tkinter_image)
        master.update_idletasks()
        master.after(TIMEOUT, check_draw)
    
    master.after(0, check_draw)
    master.mainloop()

def output_bmp(interpreter, filename):
    """
    given an interpreter with image at .image,
    save it as bmp
    """
    interpreter.image._image.save(filename, 'bmp')

def print_line_numbers(state):
    """
    will walk the state forward, printing when the line number
    is new
    """
    current = state
    last = -1
    while current is not None:
        if current.line_no != last:
            print current.line_no
            last = current.line_no
        current = current.next

def make_gif(state):
    
    index = 0
    os.mkdir('temp')
    
    filename_template = "temp/im_%06d.gif"
    
    while state.previous:
        state.image._image.save(filename_template % index)
        state = state.previous
        index += 1
        
    """
    convert -delay 3 -loop 1 `ls temp/ | sort -r | perl -pe '$_ = "temp/$_";'` animation.gif"
    """



def full_interface(states, dbn_script):
    ####### STATES IS A ONE_ELEMENT LIST
    state_wrapper = DBNStateWrapper(states[0])
    del states[0] # no more reference to state in the caller
    
    master = Tkinter.Tk()
    
    interface = dbngui.DBNInterface(master, state_wrapper, initial_script=dbn_script)
    
    master.mainloop()
    
    