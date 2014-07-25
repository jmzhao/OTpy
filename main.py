import tkinter as tk
import tkinter.scrolledtext
import tkinter.filedialog
import tkinter.messagebox

import tableau as tb
import cd
import fred

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createMenubar()
        self.createWidgets()
        self.master.title("ot_py")
    
    def createMenubar(self):
        ## menu bar
        self.menubar = tk.Menu(self)
        self.master.config(menu=self.menubar)
        ### File
        self.menuFile = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.menuFile)
        self.menuFile.add_command(label="Open", command=self.z_loadFile)
        ### Run
        self.menuRun = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Run", menu=self.menuRun)
        self.menuRun.add_command(label="Run Constraint Demotion (CD)", command=self.z_cd)
        self.menuRun.add_command(label="Run Fusional Reduction (FRed)", command=self.z_fred)
        ### Help
        self.menuHelp = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.menuHelp)
        self.menuHelp.add_command(label="About", command=self.z_about)
        
    def createWidgets(self):
        '''
        ## "Browse" button to load file
        self.xb_loadFile = tk.Button(self, text="Browse", command=self.z_loadFile)
        self.xb_loadFile.grid(row=0, column=0)    
        
        ## "Constraint Demotion" button to run CD algorithm
        self.xb_cd = tk.Button(self, text="Constraint Demotion", command=self.z_cd)
        self.xb_cd.grid(row=0, column=1)
        
        ## "Fusional Reduction" button to run FRed algorithm
        self.xb_fred = tk.Button(self, text="Fusional Reduction", command=self.z_fred)
        self.xb_fred.grid(row=0, column=1)
        '''
        
        ## scrolled text feild to show input content
        self.xst_input = tk.scrolledtext.ScrolledText(self, width=60, wrap="none")
        self.xst_input.grid(row=1, column=0)
        ## scrolled text feild to show output content
        self.xst_output = tk.scrolledtext.ScrolledText(self, width=60, wrap="none")
        self.xst_output.grid(row=1, column=1)
        
    def say_hi(self):
        self.xst_input.insert(tk.END, "hi there, everyone!\n")
    def z_loadFile(self) :
        ''' action for load file button '''
        fname = tk.filedialog.askopenfile(filetypes=(("Plain text", "*.txt"),
                                                     ("All files", "*.*")))
        f = fname.read()
        self.y_input = str(f)
        if fname :
            self.xst_input.delete(1.0, tk.END)
            self.xst_input.insert(tk.END, f)
    def z_cd(self) :
        ''' actiion for Constraint Demotion button '''
        self.xst_output.delete(1.0, tk.END)
        t = tb.tableau()
        try :
            t.readString(self.y_input)
            self.xst_output.insert(tk.END, cd.toString(cd.ConstraintsDemotion(t)))
        except tb.InputError as e :
            tk.messagebox.showerror(title="INPUT ERROR", message=e)
        except Exception as e :
            tk.messagebox.showerror(title="ERROR", message=e)
            #self.ysv_errmsg.set('ERROR: '+str(e))
    def z_fred(self) :
        ''' actiion for Fusional Reduction button '''
        self.xst_output.delete(1.0, tk.END)
        self.xst_output.insert(tk.END, 'computing...')
        t = tb.tableau()
        try :
            t.readString(self.y_input)
            self.xst_output.delete(1.0, tk.END)
            self.xst_output.insert(tk.END, (fred.FRed(fred.erc.get_ERClist(t))))
        except tb.InputError as e :
            tk.messagebox.showerror(title="INPUT ERROR", message=e)
        except Exception as e :
            tk.messagebox.showerror(title="ERROR", message=e)
    def z_about(self) :
        m = '''ot_py (alpha)
7/26/2014
        '''
        tk.messagebox.showinfo(title="About", message=m)

root = tk.Tk()
app = Application(master=root)
app.mainloop()
