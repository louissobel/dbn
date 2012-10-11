from PIL import Image, ImageTk
import Tkinter

import os

def draw_window(image):
    master = Tkinter.Tk()

    tkinter_image = ImageTk.PhotoImage(image.resize((202, 202)))
    #tkinter_image = ImageTk.PhotoImage(test_image)

    w = Tkinter.Canvas(master, width=300, height=300, bg='maroon')
    w.pack()

    w.create_image((150,150), image=tkinter_image, anchor='center')
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
    