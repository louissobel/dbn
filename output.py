from PIL import Image, ImageTk
import Tkinter

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
    