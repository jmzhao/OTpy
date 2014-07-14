import tkinter as tk
import tkinter.scrolledtext
import tkinter.filedialog

import tableau as tb
import cd

def test(fname) :
    print('-----test for "%s"------'%fname)
    t = tb.tableau(fname)
    print('Stratum\tAbbreviation')
    for c, s in cd.ConstraintsDemotion(t) :
        print(s, c.abbr, sep='\t')

#test('Ilokano.txt')
#test('TinyIllustrativeFile.txt')

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        '''
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")
        '''
        self.xb_loadFile = tk.Button(self, text="Browse", command=self.z_load_file)
        self.xb_loadFile.grid(row=0, column=0)    
        
        self.xb_cd = tk.Button(self, text="Constraint Demotion", command=self.z_cd)
        self.xb_cd.grid(row=0, column=1)
        
        '''
        ########## text-field with slidebars
        self.xt1_sbv = tk.Scrollbar(self, orient=tk.VERTICAL)  # vertical scrollbar
        self.xt1_sbh = tk.Scrollbar(self, orient=tk.HORIZONTAL)  # horizonal scrollbar

        self.xt1 = tk.Text(self, height=15, yscrollcommand=self.xt1_sbv.set,
                                          xscrollcommand=self.xt1_sbh.set, wrap='none')
        ## scroll event
        self.xt1_sbv.config(command=self.xt1.yview)
        self.xt1_sbh.config(command=self.xt1.xview)

        ## layout
        self.xt1_sbv.pack(fill="y", expand=0, side=tk.RIGHT, anchor=tk.N)
        self.xt1_sbh.pack(fill="x", expand=0, side=tk.BOTTOM, anchor=tk.N)
        #self.xt1_t.pack(fill="x", expand=1, side=tk.LEFT)
        self.xt1.pack()

        ## select-all event
        self.xt1.bind("<Control-Key-a>", self.se.selectText)
        self.xt1.bind("<Control-Key-A>", self.selectText)
        ########## text-field with slidebars END
        '''
        self.xst_input = tk.scrolledtext.ScrolledText(self, width=60, wrap="none")
        self.xst_input.grid(row=1, column=0)
        self.xst_output = tk.scrolledtext.ScrolledText(self, width=60, wrap="none")
        self.xst_output.grid(row=1, column=1)
        
        self.ysv_errmsg = tk.StringVar(self)
        self.xl_errmsg = tk.Label(self, width=120, textvariable=self.ysv_errmsg)
        self.xl_errmsg.grid(row=2, column=0, columnspan=2)
        
        #self.xb_quit = tk.Button(self, text="QUIT", fg="red", command=root.destroy)
        #self.xb_quit.grid
        
    def say_hi(self):
        self.xst_input.insert(tk.END, "hi there, everyone!\n")
    def z_load_file(self) :
        fname = tk.filedialog.askopenfile(filetypes=(("Plain text", "*.txt"),
                                                     ("All files", "*.*")))
        f = fname.read()
        self.y_input = str(f)
        #print(f)   
        if fname :
            try :
                #f = open(fname)
                pass
            except Exception as e :
                raise e
            self.xst_input.delete(1.0, tk.END)
            self.xst_input.insert(tk.END, f)
    def z_cd(self) :
        self.xst_output.delete(1.0, tk.END)
        t = tb.tableau()
        t.readString(self.y_input)
        try :
            self.xst_output.insert(tk.END, cd.toString(cd.ConstraintsDemotion(t)))
        except ValueError as e :
            self.ysv_errmsg.set('ERROR: '+str(e))

root = tk.Tk()
app = Application(master=root)
app.mainloop()
