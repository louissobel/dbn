from PIL import Image, ImageTk
import Tkinter


def draw_window(image):
    master = Tkinter.Tk()

    tkinter_image = ImageTk.PhotoImage(image.resize((202, 202)))
    #tkinter_image = ImageTk.PhotoImage(test_image)

    w = Tkinter.Canvas(master, width=300, height=300, bg='maroon')
    w.pack()

    w.create_image((150,150), image=tkinter_image, anchor='center')
    w.image = tkinter_image

    master.mainloop()

