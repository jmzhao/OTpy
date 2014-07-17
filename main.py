import tkinter as tk
import tkinter.scrolledtext
import tkinter.filedialog
import tkinter.messagebox

import tableau as tb
import cd

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        self.master.title("ot_py")

    def createWidgets(self):
        self.xb_loadFile = tk.Button(self, text="Browse", command=self.z_load_file)
        self.xb_loadFile.grid(row=0, column=0)    
        
        self.xb_cd = tk.Button(self, text="Constraint Demotion", command=self.z_cd)
        self.xb_cd.grid(row=0, column=1)
        
        self.xst_input = tk.scrolledtext.ScrolledText(self, width=60, wrap="none")
        self.xst_input.grid(row=1, column=0)
        self.xst_output = tk.scrolledtext.ScrolledText(self, width=60, wrap="none")
        self.xst_output.grid(row=1, column=1)
        '''
        self.ysv_errmsg = tk.StringVar(self)
        self.xl_errmsg = tk.Label(self, width=120, textvariable=self.ysv_errmsg)
        self.xl_errmsg.grid(row=2, column=0, columnspan=2)
        '''
    def say_hi(self):
        self.xst_input.insert(tk.END, "hi there, everyone!\n")
    def z_load_file(self) :
        fname = tk.filedialog.askopenfile(filetypes=(("Plain text", "*.txt"),
                                                     ("All files", "*.*")))
        f = fname.read()
        self.y_input = str(f)
        if fname :
            self.xst_input.delete(1.0, tk.END)
            self.xst_input.insert(tk.END, f)
    def z_cd(self) :
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

root = tk.Tk()
app = Application(master=root)
app.mainloop()
