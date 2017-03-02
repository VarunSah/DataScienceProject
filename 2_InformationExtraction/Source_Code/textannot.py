import logging
import tkinter as tk
import tkinter.filedialog
import os
from os.path import join


logging.basicConfig(level=logging.INFO)


class StatusBar(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.label = tk.Label(self, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.label.pack(fill=tk.X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()


class MainApplication(tk.Frame):

    doc_dir = None # directory containing text documents
    files = [] # list of txt files in directory

    current_file_idx = -1
    current_data = []
    current_changes = False

    def __init__(self, parent, *args, **kwargs):

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("Sam's Amazing Text Annotator")

        # menubar (this should be its own class)
        self.menubar = tk.Menu(self)

        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open...", command=self.open)
        self.filemenu.add_command(label="Exit", command=quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About...", command=self.about)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.parent.config(menu=self.menubar)

        # textbox
        self.textbox = tk.Text(self, bg="#D3D3D3", wrap=tk.WORD)
        self.textbox.tag_config("annotation", background="yellow")

        # buttons
        self.buttonsframe = tk.Frame(self)
        self.next_button = tk.Button(self.buttonsframe, text="Next", command=self.next)
        self.prev_button = tk.Button(self.buttonsframe, text="Prev", command=self.prev)
        self.annot_button = tk.Button(self.buttonsframe, text="Annotate", command=self.annotate)
        self.unannot_button = tk.Button(self.buttonsframe, text="Unannoate", command=self.unannotate)
        self.open_button = tk.Button(self.buttonsframe, text="Open", command=self.open)

        # buttons pack
        self.next_button.pack(side="right")
        self.prev_button.pack(side="right")
        self.annot_button.pack(side="right")
        self.unannot_button.pack(side="right")
        self.open_button.pack(anchor=tk.W)
        
        # status bar
        self.statusbar = StatusBar(self)
        
        # final packing
        self.buttonsframe.pack(anchor=tk.E, fill=tk.X)
        self.textbox.pack(side="top", fill="both", expand=True)
        self.statusbar.pack(fill=tk.X)

        # keyboard shortcuts
        self.textbox.bind("<Key>", lambda e: "break")
        self.textbox.bind("a", self.annotate_keypress)
        
        self.statusbar.set("No directory loaded.")


    def reset(self):

        self.doc_dir = None
        self.files = []
        self.current_file_idx = -1
        self.current_data = []
        self.current_changes = False
        self.clear()


    def about(self):

        about_message="Sam's Amazing Text Annotator\nVersion: 0.1\nAuthor: Sam Gelman"

        top = tk.Toplevel()
        top.title("About")

        msg = tk.Message(top, text=about_message, width=300)
        msg.pack()

        button = tk.Button(top, text="Dismiss", command=top.destroy)
        button.pack()


    def open(self):

        logging.info("opening directory dialog")
        d = tk.filedialog.askdirectory(initialdir=".")

        if d == "":
            logging.info("no directory selected")

        else:
            logging.info("selected directory {}".format(d))
            self.reset()
            self.doc_dir = d
            self.files = sorted([f for f in os.listdir(d) if f.endswith(".txt")])
            if len(self.files) == 0:
                self.statusbar.set("({}/{}) {}".format(self.current_file_idx+1, len(self.files), self.doc_dir))
            else:
                self.next()


    def load_fn(self, fn):

        self.current_data = []
        with open(fn, "r") as f:
            for line in f:
                self.current_data.append(line)

        logging.info("loaded {}".format(fn))


    def load_annots(self, fn):

        with open(fn, "r") as f:
            for line in f:
                line = line.strip()
                positions = line.split(",")
                self.textbox.tag_add("annotation", positions[0], positions[1])
                logging.debug("loaded annotation {}".format(positions))

        logging.info("loaded annotations {}".format(fn))


    def clear(self):

        self.textbox.delete("1.0", tk.END)
        self.statusbar.clear()


    def update(self):

        try:
            self.load_fn(join(self.doc_dir, self.files[self.current_file_idx]))
        except IOError as e:
            print(e)

        self.clear()
        self.current_changes = False
        self.textbox.insert("1.0", "".join(self.current_data))

        try:
            self.load_annots(join(self.doc_dir, self.files[self.current_file_idx] + ".annot"))
        except IOError as e:
            logging.info("no annotations file {}".format(self.files[self.current_file_idx] + ".annot"))

        self.statusbar.set("({}/{}) {}".format(self.current_file_idx+1, len(self.files), self.doc_dir))


    def validate_idx(self, new_idx):

        if (new_idx) < 0 or (new_idx > len(self.files) - 1):
            return False

        return True


    def save(self):

        current_tags = list(map(str,self.textbox.tag_ranges("annotation")))
        with open(join(self.doc_dir, self.files[self.current_file_idx] + ".annot"), "w") as f:    
            for i in range(0, len(current_tags), 2):
                f.write("{},{}\n".format(current_tags[i], current_tags[i+1]))

        logging.info("saved tags {}".format(self.files[self.current_file_idx] + ".annot"))


    def next(self):

        if self.current_file_idx >= 0 and self.current_changes:
            self.save()

        proposed_idx = self.current_file_idx + 1
        if self.validate_idx(proposed_idx):
            self.current_file_idx = proposed_idx
            self.update()
        else:
            logging.info("no more files")


    def prev(self):

        if self.current_file_idx >= 0 and self.current_changes:
            self.save()

        proposed_idx = self.current_file_idx - 1
        if self.validate_idx(proposed_idx):
            self.current_file_idx = proposed_idx
            self.update()
        else:
            logging.info("no previous files")


    def annotate_keypress(self, e):

        self.annotate()
        return "break"


    def annotate(self):

        if self.textbox.tag_ranges("sel"):
            self.textbox.tag_add("annotation", tk.SEL_FIRST, tk.SEL_LAST)
            self.current_changes = True
            logging.info("added annotation")


    def unannotate(self):

        if self.textbox.tag_ranges("sel"):
            self.textbox.tag_remove("annotation", tk.SEL_FIRST, tk.SEL_LAST)
            self.current_changes = True
            logging.info("removed annotation")


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
