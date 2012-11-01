from PIL import Image, ImageTk
import Tkinter
import ttk


import dbn
import sys
import os
from tokenizer import DBNTokenizer
import parser
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
    master.tk_strictMotif()
    
    canvas = Tkinter.Canvas(master, width=302, height=302)
    canvas.grid(row=0, column=0, rowspan=1, sticky='s')
    
    image = states[0].image._image

    
    tkinter_image = ImageTk.PhotoImage(image.resize((202, 202)))

    canvas.create_rectangle(49, 49, 252, 252)
    canvas_image = canvas.create_image((151,151), image=tkinter_image, anchor='center')
    canvas.image = tkinter_image
    
    ghost_image = canvas.create_image((151, 151), anchor='center')    
    
    textframe = Tkinter.Frame(master, bg="black", border=1)
    text = Tkinter.Text(textframe, height=30, width=50, borderwidth=0, selectborderwidth=0, highlightthickness=0)
    text.focus_set()

    textframe.grid(row=0, column=1, padx=20, pady=20, rowspan=2)
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
    
    def draw_frame_numbered(n):
        """
        will get the current state, rewind it,
        then walk forward to the nth.
        not elegeant at all.
        REDO THIS (state player wrapper class?)
        """
        state = states[0]
        first_state = state
        while first_state.previous is not None:
            first_state = first_state.previous
        
        out_state = first_state
        for i in range(1,n):
            out_state = out_state.next
            # will raise Attriubte Error if counting is off
        draw_state(out_state)
        
    
    def draw_text():
        dbn_script = text.get(1.0, Tkinter.END)
        state = dbn.run_script_text(dbn_script)
        draw_state(state)
    
    def keyboard_draw_text(event):
        draw_text()
        pointer_x, pointer_y = text.winfo_pointerxy()
        root_x, root_y = text.winfo_rootx(), text.winfo_rooty()
        cx, cy = pointer_x - root_x, pointer_y - root_y
        ghost_event(cx, cy)
        return "break"
    text.bind("<Shift-Return>", keyboard_draw_text)
    
    
    ### stuff for drawing ghosts
    tokenizer = DBNTokenizer()
    def get_line(tkinter_index):
        """
        given an X, Y, gets the line text, or None
        """
        line, column = tkinter_index.split('.')
        end_of_line = text.index("%s.end" % line).split('.')[1]
        if int(column) < int(end_of_line):
            start = "%s.0" % (line)
            end = "%s.end" % (line)
            return text.get(start, end)
        else:
            return None
        
    def get_ghost_key(x, y):
        """
        given an x, y, returns the ghost key there, or None
        """
        tkinter_index = text.index("@%d,%d" % (x, y))
        
        str_line_no = tkinter_index.split('.')[0]
        
        line = get_line(tkinter_index)
        if line is not None:
            tokens = tokenizer.tokenize(line)
            args = parser.parse_ghost_line(tokens)
            if args is None:
                return None
            
            # we have to manually get bounding box for args
            bounding_boxes = []
            for index, arg in enumerate(args):
                _, str_start_char = arg.start_location().split('.')
                _, str_end_char = arg.end_location().split('.')

                arg_start = "%s.%s" % (str_line_no, str_start_char)
                arg_end = "%s.%s" % (str_line_no, str_end_char)

                start_bbox = text.bbox(arg_start)
                start_x, start_y, width, height = start_bbox

                end_bbox = text.bbox(arg_end)
                end_x, end_y, _, _ = end_bbox
                
                arg_bbox = (start_x, start_y, (end_x - start_x), height)
                bounding_boxes.append(arg_bbox)
            
            int_arg_index = None
            for index, arg_bbox in enumerate(bounding_boxes):
                start_x, start_y, width, height = arg_bbox
                if start_x <= x < start_x + width:
                    int_arg_index = index
                    break
            if int_arg_index is not None:
                return "l%sa%d" % (str_line_no, int_arg_index)
            else:
                return None
        else:
           return None
      
    def ghost_event(x, y):
        key = get_ghost_key(x, y)
        if key is None:
            clear_ghost()
        else:
            success = set_ghost(key)
            if success is None:
                clear_ghost()
    
    def text_mouse_motion(event):
        ghost_event(event.x, event.y)
        
    def text_mouse_leave(event):
        clear_ghost()
        
    text.bind("<Motion>", text_mouse_motion)
    text.bind("<Leave>", text_mouse_leave)
    
    
    
    b = Tkinter.Button(master, text="draw", command=draw_text)
    b.grid(row=2, column=1)
    
    
    # stuff for testing ghosts
    def set_ghost(key):
        state = states[0]
        image = state.ghosts._ghost_hash.get(key)
        if image is None:
            return None
        else:
            ghost_tkinter_image = ImageTk.BitmapImage(image._image.resize((202, 202)), foreground="red")
            canvas.itemconfigure(ghost_image, image=ghost_tkinter_image)
            canvas.ghost_image = ghost_tkinter_image
            return True
    
    def clear_ghost():
        if hasattr(canvas, 'ghost_image'):
            canvas.itemconfigure(ghost_image, image=None)
            del canvas.ghost_image
            
    
    # timeline scale
    scale_var = Tkinter.IntVar()
    scale_var.set(7)
    slider_frame = Tkinter.Frame(master)
    scale = Tkinter.Scale(slider_frame, orient=Tkinter.HORIZONTAL, showvalue=0, var=scale_var)
    scale.active = False
    
    def scale_var_changed(*args):
        frame_number = scale_var.get()
        draw_frame_numbered(frame_number)
    
    scale_var.trace_variable('w', scale_var_changed)
    
    scale.grid(column=1, row=0)
    

    
    label = Tkinter.Label(slider_frame, text="hi")
    label.grid(column=0, row=0, sticky='s')
    
    slider_frame.grid(row=1)
    
    master.mainloop()
    
    