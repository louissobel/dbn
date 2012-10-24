from PIL import Image, ImageTk
import Tkinter


import dbn

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


def draw_window(image):
    master = Tkinter.Tk()

    tkinter_image = ImageTk.PhotoImage(image.resize((202, 202)))
    #tkinter_image = ImageTk.PhotoImage(test_image)

    w = Tkinter.Canvas(master, width=302, height=302)
    w.pack()

    w.create_rectangle(49, 49, 252, 252)
    w.create_image((151,151), image=tkinter_image, anchor='center')
    w.image = tkinter_image

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
    
    image = states[0].image._image
    del states[0] # now no more reference to the input state!
    

    
    tkinter_image = ImageTk.PhotoImage(image.resize((202, 202)))

    canvas.create_rectangle(49, 49, 252, 252)
    canvas_image = canvas.create_image((151,151), image=tkinter_image, anchor='center')
    canvas.image = tkinter_image
    
    
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
        image = state.image._image
        tkinter_image = ImageTk.PhotoImage(image.resize((202, 202)))
        canvas.itemconfigure(canvas_image, image=tkinter_image)
        canvas.image = tkinter_image    
    
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
    
    master.mainloop()
    
    