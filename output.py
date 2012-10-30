from PIL import Image, ImageTk
import Tkinter


import dbn
import sys
import os

import time


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


def draw_window(image, time=False):
    master = Tkinter.Tk()

    tkinter_image = ImageTk.PhotoImage(image.resize((202, 202)))
    #tkinter_image = ImageTk.PhotoImage(test_image)

    w = Tkinter.Canvas(master, width=302, height=302)
    w.pack()

    w.create_rectangle(49, 49, 252, 252)
    w.create_image((151,151), image=tkinter_image, anchor='center')
    w.image = tkinter_image

    if time:
        sys.exit(0)

    master.mainloop()


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
    
    master = Tkinter.Tk()
    
    canvas = Tkinter.Canvas(master, width=302, height=302)
    canvas.grid(row=0, column=0, rowspan=2)
    
    state = states[0]
    
    image = state.image._image

    
    tkinter_image = ImageTk.PhotoImage(image.resize((202, 202)))

    canvas.create_rectangle(49, 49, 252, 252)
    canvas_image = canvas.create_image((151,151), image=tkinter_image, anchor='center')
    canvas.image = tkinter_image
    
    ghost_image = canvas.create_image((151, 151), anchor='center')    
    
    textframe = Tkinter.Frame(master, bg="black", border=1)
    text = Tkinter.Text(textframe, height=30, width=50, borderwidth=0, selectborderwidth=0, highlightthickness=0)
    text.focus_set()

    textframe.grid(row=0, column=1, padx=20, pady=20)
    text.pack()
    
    def insert_tab(event):
        # insert 4 spaces
        text.insert(Tkinter.INSERT, " " * 4)
        return "break"
    text.bind("<Tab>", insert_tab)

    text.insert(1.0, dbn_script)

    def draw_state(state):
        states[0] = state
        image = state.image._image
        tkinter_image = ImageTk.PhotoImage(image.resize((202, 202)))
        canvas.itemconfigure(canvas_image, image=tkinter_image)
        canvas.image = tkinter_image 
        
        print state.ghosts._ghost_hash   
    
    def draw_text():
        dbn_script = text.get(1.0, Tkinter.END)
        state = dbn.run_script_text(dbn_script)
        draw_state(state)
    
    def keyboard_draw_text(event):
        draw_text()
        return "break"
    text.bind("<Shift-Return>", keyboard_draw_text)
    
    b = Tkinter.Button(master, text="draw", command=draw_text)
    b.grid(row=1, column=1)
    
    
    # stuff for testing ghosts
    ghost_input = Tkinter.Entry(master)
    def draw_ghost():
        key = ghost_input.get()
        state = states[0]
        image = state.ghosts._ghost_hash.get(key)._image
        if image is None:
            print "None!"
        else:
            ghost_tkinter_image = ImageTk.BitmapImage(image.resize((202, 202)), foreground="red")
            canvas.itemconfigure(ghost_image, image=ghost_tkinter_image)
            canvas.ghost_image = ghost_tkinter_image
    
    def clear_ghost():
        ghost_input.delete(0, Tkinter.END)
        canvas.itemconfigure(ghost_image, image=None)
        del canvas.ghost_image
    
    ghost_draw = Tkinter.Button(master, text='ghost', command=draw_ghost)
    ghost_clear = Tkinter.Button(master, text='clear', command=clear_ghost)
    
    ghost_input.grid(row=2)
    ghost_draw.grid(row=3)
    ghost_clear.grid(row=4)
    
    
    print state.ghosts._ghost_hash
    
    master.mainloop()
    
    