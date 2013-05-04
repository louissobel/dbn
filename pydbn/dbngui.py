import Tkinter

from parser import DBNTokenizer
import parser
import dbn

from PIL import Image, ImageTk

class DBNImageCanvas(Tkinter.Canvas):
    
    def __init__(self, root):
        Tkinter.Canvas.__init__(self, root, width=302, height=302)
        
        self.create_rectangle(49, 49, 252, 252)

        self.canvas_image = self.create_image((151,151), anchor='center')
        self.ghost_image = self.create_image((151, 151), anchor='center')   
        
    def set_image(self, image):
        tkinter_image = ImageTk.PhotoImage(image.resize((202, 202)))
        
        self.itemconfigure(self.canvas_image, image=tkinter_image)
        self._dbn_image = tkinter_image
        
    def set_ghost(self, key, ghost_hash):
        image = ghost_hash.get(key)
        if image is None:
            return None
        else:
            ghost_tkinter_image = ImageTk.BitmapImage(image._image.resize((202, 202)), foreground="red")
            self.itemconfigure(self.ghost_image, image=ghost_tkinter_image)
            self._ghost_image = ghost_tkinter_image
            return True

    def clear_ghost(self):
        if hasattr(self, '_ghost_image'):
            self.itemconfigure(self.ghost_image, image=None)
            del self._ghost_image
        
class DBNTextInput(Tkinter.Text):
    
    def __init__(self, root, initial_script=''):
        Tkinter.Text.__init__(self, root, height=30, width=80, borderwidth=0, selectborderwidth=0, highlightthickness=0)
        
        self.WIDTH=80
        
        self.bind_events()
        self.insert(1.0, initial_script)
        
        self.highlight_active = False
        
        self.highlighted_lines = []
        
        self.tokenizer = DBNTokenizer()
        
    def bind_events(self):
        self.bind("<Tab>", self.insert_tab)

    def insert_tab(self, event):
        # insert 4 spaces
        self.insert(Tkinter.INSERT, " " * 4)
        return "break"
        
    def get_mouse_position(self):
        pointer_x, pointer_y = self.winfo_pointerxy()
        root_x, root_y = self.winfo_rootx(), self.winfo_rooty()
        cx, cy = pointer_x - root_x, pointer_y - root_y
        return cx, cy
    
    def get_contents(self):
        return self.get(1.0, Tkinter.END)
    
    def get_line(self, tkinter_index):
        """
        given an X, Y, gets the line text, or None
        """
        line, column = tkinter_index.split('.')
        end_of_line = self.index("%s.end" % line).split('.')[1]
        if int(column) < int(end_of_line):
            start = "%s.0" % (line)
            end = "%s.end" % (line)
            return self.get(start, end)
        else:
            return None 
  
    def get_ghost_key(self, x, y):
         """
         given an x, y, returns the ghost key there, or None
         """
         tkinter_index = self.index("@%d,%d" % (x, y))

         str_line_no = tkinter_index.split('.')[0]

         line = self.get_line(tkinter_index)
         if line is not None:
             tokens = self.tokenizer.tokenize(line)
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

                 start_bbox = self.bbox(arg_start)
                 start_x, start_y, width, height = start_bbox

                 end_bbox = self.bbox(arg_end)
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
    
    def highlight_line(self, n):
        start_index = "%d.0" % n
        line_end_index = "%d.end" % n
        
        mark_name = "%d.prehighlight_end" % n
        self.mark_set(mark_name, line_end_index)
        self.mark_gravity(mark_name, Tkinter.LEFT)
        
        end_char = int(self.index(line_end_index).split('.')[1])
        leftover = self.WIDTH - end_char
        self.insert(mark_name, " "*leftover)
        
        self.tag_add('highlighted', start_index, line_end_index)
        self.highlighted_lines.append(n)
        
        self.tag_config('highlighted', background="pink")

    def clear_line_highlights(self):
        self.tag_delete('highlighted')
        for n in self.highlighted_lines:
            old_mark = "%d.prehighlight_end" % n
            line_end_index = "%d.end" % n
            self.delete(old_mark, line_end_index)
        self.highlighted_lines = []


class DBNTimeline(Tkinter.Frame):
    
    def __init__(self, root, count):
        Tkinter.Frame.__init__(self, root)
        
        self.value = Tkinter.IntVar()
        self.value.set(count) # initialized to the end
        
        self.scale_hover = False
        self.scale_pressed = False
        self.active = Tkinter.BooleanVar()
        
        self.scale = Tkinter.Scale(self, 
            orient=Tkinter.HORIZONTAL,
            length=200,
            showvalue=0,
            var=self.value,
            to=count
        )
        
        self.scale.grid(column=1, row=0, sticky='e')

        self.label = Tkinter.Label(self, width=10)
        self.set_label_inactive_text(count)
        
        self.label.grid(column=0, row=0, sticky='s')

        self.bind_events()
    
    def set_length(self, length):
        self.scale.config(to=length)
    
    def set_label_inactive_text(self, count):
        text = "%d steps" % count
        self.label.config(text=text)
        
    def set_label_active_text(self, index):
        text = "step %d" % index
        self.label.config(text=text)
      
    def bind_events(self):
        self.scale.bind("<ButtonRelease-1>", self.scale_mouseup)
        self.scale.bind("<ButtonPress-1>", self.scale_mousedown)
        self.scale.bind("<Enter>", self.scale_entered)
        self.scale.bind("<Leave>", self.scale_leaved)
    
    def scale_entered(self, event):
        self.scale_hover = True
        self.active.set(True)

    def scale_leaved(self, event):
        self.scale_hover = False
        if not self.scale_pressed:
            self.active.set(False)

    def scale_mousedown(self, event):
        self.scale_pressed = True

    def scale_mouseup(self, event):
        self.scale_pressed = False
        if not self.scale_hover:
            self.active.set(False)
            
    def focus_set(self):
        self.scale.focus_set()


class ColorDisplayWidget(Tkinter.Canvas):
    
    def __init__(self, root, color=80, width=30, height=30):
        Tkinter.Canvas.__init__(self, root, width=width, height=height)

        self.create_rectangle(3, 3, width+2, height+2)

        self.color = Tkinter.IntVar()
        self.color.trace_variable('w', self.set_color_listener)
        self.color.set(color)
        
    def set_color_listener(self, *args):
        self.set_color(self.color.get())
    
    def set_color(self, color):
        tkinter_color = "gray%d" % color
        self.config(bg=tkinter_color)
        
 
class DBNPenState(Tkinter.Frame):
    
    def __init__(self, root):
        #### the state frame
        Tkinter.Frame.__init__(self, root)
        self.label = Tkinter.Label(self, text="Pen: ")
        self.value_label = Tkinter.Label(self, width=4, text="100")
        self.color_display = ColorDisplayWidget(self)
        
        self.default_background = self.label['background']
        
        self.label.grid(row=0, column=0)
        self.value_label.grid(row=0, column=1)
        self.color_display.grid(row=0, column=2)
        
    def set(self, to):
        self.value_label.config(text=str(to))
        self.color_display.color.set(100 - to)
        
    def highlight(self):
        self.label.config(bg="red")
        print "g"
    
    def clear_highlight(self):
        print "goose"
        self.label.config(background=self.default_background)


class DBNInterface:
    
    def __init__(self, master, state_wrapper, initial_script=''):
        self.master = master
        self.state_wrapper = state_wrapper
        self.initial_script = initial_script
        
        self.add_widgets()
        self.bind_events()
        self.draw_cursor()
        self.text.focus_set()
        
        
    def add_widgets(self):
        self.image_canvas = DBNImageCanvas(self.master)        
        self.image_canvas.grid(row=0, column=0, rowspan=1, sticky='s')
        
        self.textframe = Tkinter.Frame(self.master, bg="black", border=1)
        self.text = DBNTextInput(self.textframe, initial_script=self.initial_script)
        self.text.pack()
        self.textframe.grid(row=0, column=1, padx=20, pady=20, rowspan=2)
        
        self.draw_button = Tkinter.Button(self.master, text="draw", command=self.draw_text)
        self.draw_button.grid(row=2, column=1)
        
        self.timeline = DBNTimeline(self.master, len(self.state_wrapper))
        self.timeline.grid(row=1)
        
        self.pen_color_state = DBNPenState(self.master)
        self.pen_color_state.grid(row=2)
        
    def bind_events(self):
        self.text.bind("<Shift-Return>", self.keyboard_draw_text)
        self.text.bind("<Motion>", self.text_mouse_motion)
        self.text.bind("<Leave>", self.text_mouse_leave)
        
        self.timeline.active.trace_variable('w', self.timeline_active_state_changed)
        self.timeline.value.trace_variable('w', self.timeline_value_changed)

    def draw_cursor(self):
        image = self.state_wrapper.cursor.image._image
        self.image_canvas.set_image(image)
        
        
        self.pen_color_state.set(self.state_wrapper.cursor.pen_color)
    
        # configure the set 'to' to be the length of the canvas
        self.timeline.set_length(len(self.state_wrapper))
        self.timeline.value.set(self.state_wrapper.cursor_index)
    
        if not self.timeline.active.get(): # otherwise, not my problem
            self.timeline.set_label_inactive_text(len(self.state_wrapper))

    def draw_frame_numbered(self, n):
        """
        will get the current state, rewind it,
        then walk forward to the nth.
        not elegeant at all.
        REDO THIS (state player wrapper class?)
        """        
        self.state_wrapper.seek(n)
        self.draw_cursor()

    def draw_text(self):
        dbn_script = self.text.get_contents()
        new_state = dbn.run_script_text(dbn_script)
        self.state_wrapper.change_state(new_state)
        self.draw_cursor()

    def keyboard_draw_text(self, event):
        self.draw_text()
        mouse_position_in_text = self.text.get_mouse_position()
        self.ghost_event(*mouse_position_in_text)
        return "break"
        
    def ghost_event(self, x, y):
        key = self.text.get_ghost_key(x, y)
        self.handle_ghost_key(key)
    
    def handle_ghost_key(self, key):
        if key is None:
            self.image_canvas.clear_ghost()
        else:
            success = self.image_canvas.set_ghost(key, self.state_wrapper.cursor.ghosts._ghost_hash)
            if success is None:
                self.image_canvas.clear_ghost()

    def text_mouse_motion(self, event):
        self.ghost_event(event.x, event.y)
    
    def text_mouse_leave(self, event):
        self.image_canvas.clear_ghost()
        
    def highlight_current_line(self):
        current_line = self.state_wrapper.cursor.line_no
        if self.text.highlight_active:
            self.text.highlight_line(current_line)
          
    def timeline_active_state_changed(self, *args):
        is_active = bool(self.timeline.active.get())
        self.text.clear_line_highlights()
        if is_active:
            self.timeline.focus_set()
            self.text.highlight_active = True
            self.highlight_current_line()

            # show which step we're at
            self.timeline.set_label_active_text(self.timeline.value.get())
            self.master.config(cursor='sb_h_double_arrow')

        else:
            self.text.focus_set() # just to get to focus away from the scale
            self.text.highlight_active = False
            
            # reset the state
            #state_wrapper.fast_forward()
            #draw_cursor()

            # set the cursor back. unfortunately
            # named name as state cursor. this is the mouse cursor
            self.master.config(cursor="")

    def timeline_value_changed(self, *args):
        frame_number = self.timeline.value.get()
        self.draw_frame_numbered(frame_number)
        self.text.clear_line_highlights()
        self.highlight_current_line()
        self.timeline.set_label_active_text(frame_number)
        
        
