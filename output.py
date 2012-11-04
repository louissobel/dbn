from PIL import Image, ImageTk
import Tkinter
import ttk


import dbn
import sys
import os
from tokenizer import DBNTokenizer
import parser
import time

from structures import DBNStateWrapper


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
    state_wrapper = DBNStateWrapper(states[0])
    del states[0] # no more reference to state in the caller
    
    master = Tkinter.Tk()
    master.tk_strictMotif()
    
    canvas = Tkinter.Canvas(master, width=302, height=302)
    canvas.grid(row=0, column=0, rowspan=1, sticky='s')
    
    image = state_wrapper.cursor.image._image

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

    def draw_cursor():
        image = state_wrapper.cursor.image._image
        tkinter_image = ImageTk.PhotoImage(image.resize((202, 202)))
        canvas.itemconfigure(canvas_image, image=tkinter_image)
        canvas.image = tkinter_image
        
        # configure the set 'to' to be the length of the canvas
        scale.config(to=len(state_wrapper))
        scale_var.set(state_wrapper.cursor_index)
        
        if not scale.active.get(): # otherwise, not my problem
            scale_label.config(text="%d steps" % len(state_wrapper))
    
    def draw_frame_numbered(n):
        """
        will get the current state, rewind it,
        then walk forward to the nth.
        not elegeant at all.
        REDO THIS (state player wrapper class?)
        """        
        state_wrapper.seek(n)
        draw_cursor()
    
    def draw_text():
        dbn_script = text.get(1.0, Tkinter.END)
        state = dbn.run_script_text(dbn_script)
        state_wrapper.change_state(state)
        draw_cursor()
    
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
        state = state_wrapper.cursor
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
     
    # line highlighting
    highlight_controller = {
        'active' : False,
    }
        
    def highlight_current_line():
        if highlight_controller['active']:
            n = state_wrapper.cursor.line_no
            start_index = "%d.0" % n
            end_index = "%d.end" % n            
            text.tag_add('highlighted', start_index, end_index)
            text.tag_config('highlighted', background="pink")
  
    def clear_line_highlights():
        text.tag_delete('highlighted')       
        
    # timeline scale
    scale_var = Tkinter.IntVar()
    scale_var.set(len(state_wrapper))
    slider_frame = Tkinter.Frame(master)
    scale = Tkinter.Scale(slider_frame, orient=Tkinter.HORIZONTAL, length=200, showvalue=0, var=scale_var, to=len(state_wrapper))

    # scale state stuff
    scale.hover = False
    scale.pressed = False
    scale.active = Tkinter.BooleanVar()
    
    def scale_active_state_changed(*args):
        is_active = bool(scale.active.get())
        clear_line_highlights()
        if is_active:
            scale.focus_set()
            highlight_controller['active'] = True
            highlight_current_line()
            
            # show which step we're at
            scale_label.config(text="step %d" % scale_var.get())
            master.config(cursor='sb_h_double_arrow')
            
            
        else:
            text.focus_set() # just to get to focus away from the scale
            highlight_controller['active'] = False
            # reset the state
            #state_wrapper.fast_forward()
            #draw_cursor()
            
            # set the cursor back. unfortunately
            # named name as state cursor. this is the mouse cursor
            master.config(cursor="")
            
    scale.active.trace_variable('w', scale_active_state_changed)
    
    def scale_entered(event):
        scale.hover = True
        scale.active.set(True)
        
    def scale_leaved(event):
        scale.hover = False
        if not scale.pressed:
            scale.active.set(False)
        
    def scale_mousedown(event):
        scale.pressed = True
    
    def scale_mouseup(event):
        scale.pressed = False
        if not scale.hover:
            scale.active.set(False)
    
    def scale_var_changed(*args):
        frame_number = scale_var.get()
        draw_frame_numbered(frame_number)
        clear_line_highlights()
        highlight_current_line()
        scale_label.config(text="step %d" % frame_number)
    
    scale_var.trace_variable('w', scale_var_changed)
    
    def scale_mouse_deactivate(event):
        clear_line_highlights()
    
    scale.bind("<ButtonRelease-1>", scale_mouseup)
    scale.bind("<ButtonPress-1>", scale_mousedown)
    scale.bind("<Enter>", scale_entered)
    scale.bind("<Leave>", scale_leaved)
    
    scale.grid(column=1, row=0, sticky='e')
    

    step_count = len(state_wrapper)
    scale_label = Tkinter.Label(slider_frame, width=10, text="%d steps" % step_count)
    scale_label.grid(column=0, row=0, sticky='s')
    
    slider_frame.grid(row=1)
    
    
    ##### the state frame
    
    
    
    
    master.mainloop()
    
    