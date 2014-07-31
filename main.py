import tkinter as tk
import tkinter.scrolledtext
import tkinter.filedialog
import tkinter.messagebox
import os
import threading as th

import tableau as tb
import cd
import fred
import maxent

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
        self.menuRun.add_command(label="Run Constraint Demotion (CD)", command=self.z_cd, state=tk.DISABLED)
        self.menuRun.add_command(label="Run Fusional Reduction (FRed)", command=self.z_fred, state=tk.DISABLED)
        self.menuRun.add_command(label="Run Maximum Entropy (MaxEnt)", command=self.z_maxent, state=tk.DISABLED)
        #self.menuRun.add_separator()
        #self.menuRun.add_command(label="Abort Running", command=self.z_abort, state=tk.DISABLED)
        ### Show
        self.menuShow = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Show", menu=self.menuShow)
        self.menuShow.add_command(label="Show Hasse Diagram", command=self.z_hasse, state=tk.DISABLED)
        ### Help
        self.menuHelp = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.menuHelp)
        self.menuHelp.add_command(label="About", command=self.z_about)
        
    def createWidgets(self):
        ## scrolled text feild to show input content
        self.xst_input = tk.scrolledtext.ScrolledText(self, width=60, wrap="none")
        self.xst_input.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        ## scrolled text feild to show output content
        self.xst_output = tk.scrolledtext.ScrolledText(self, width=60, wrap="none")
        self.xst_output.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
    
    @property  
    def y_output(self) :
        return self._y_output['value']
    @y_output.setter
    def y_output(self, value_dict) :
        del self.y_output
        self._y_output = value_dict
        toString = value_dict.get('toString', lambda x: x)
        self.xst_output.insert(tk.END, toString(self.y_output))
        if value_dict.get('caller') == self.z_fred :
            self.menuShow.entryconfigure(0, state=tk.NORMAL)
    @y_output.deleter
    def y_output(self) :
        if hasattr(self, '_y_output') : del self._y_output
        self.xst_output.delete(1.0, tk.END)
        self.menuShow.entryconfigure(0, state=tk.DISABLED)
    @property
    def y_input(self) :
        return self._y_input
    @y_input.setter
    def y_input(self, value) :
        del self.y_input
        self._y_input = value
        self.xst_input.insert(tk.END, value)
        for k in range(3) :
            self.menuRun.entryconfig(k, state=tk.NORMAL)
    @y_input.deleter
    def y_input(self) :
        if hasattr(self, '_y_input') : del self._y_input
        for k in range(3) :
            self.menuRun.entryconfig(k, state=tk.DISABLED)
        self.xst_input.delete(1.0, tk.END)
    @property
    def y_running(self) :
        return self._y_running
    @y_running.setter
    def y_running(self, v) :
        self._y_running = v
        self.menuRun.entryconfig(4, state=tk.NORMAL)
    @y_running.deleter
    def y_running(self) :
        del self._y_running
        self.menuRun.entryconfig(4, state=tk.DISABLED)
        
        
    def z_loadFile(self) :
        ''' action for load file button '''
        fname = tk.filedialog.askopenfile(filetypes=(("Plain text", "*.txt"),
                                                     ("All files", "*.*")))
        if fname :
            f = fname.read()
            self.y_input = str(f)
            del self.y_output
    def z_cd(self) :
        ''' actiion for Constraint Demotion button '''
        del self.y_output
        t = tb.tableau()
        try :
            t.readString(self.y_input)
            self.y_output = {'caller':self.z_cd, 'value':cd.ConstraintsDemotion(t), 'toString':cd.toString}
        except tb.InputError as e :
            tk.messagebox.showerror(title="INPUT ERROR", message=e)
        except Exception as e :
            tk.messagebox.showerror(title="ERROR", message=e)
            #self.ysv_errmsg.set('ERROR: '+str(e))
    def z_fred(self) :
        ''' actiion for Fusional Reduction button '''
        self.y_output = {'value':'computing...'}
        t = tb.tableau()
        try :
            t.readString(self.y_input)
            self.y_tab = t
            def task() :
                self.y_output = {'caller':self.z_fred, 'value':fred.FRed(fred.erc.get_ERClist(t))}
            self.y_running = th.Thread(target=task)
            self.y_running.start()
        except tb.InputError as e :
            tk.messagebox.showerror(title="INPUT ERROR", message=e)
        except Exception as e :
            tk.messagebox.showerror(title="ERROR", message=e)
    def z_maxent(self) :
        ''' actiion for Maximum Entropy button '''
        cnt = [0]
#        def rep(w) :
#            cnt[0] += 1
#            self.xst_output.delete(1.0, tk.END)
#            self.xst_output.insert(tk.END, 'Iteration count: %d\n'%(cnt[0]))
        t = tb.tableau()
        try :
            def task() :
                t.readString(self.y_input)
                ans = maxent.MaximumEntropy(t, callback=print)
                def toString(a) :
                    return '\n'.join('%s\t%s'%x for x in sorted(
                        ((t.get_constraint(index=i).abbr, w) for i, w in enumerate(a)), 
                        key=(lambda a:a[1])))
                self.y_output = {'caller':self.z_maxent, 'value':ans, 'toString':toString}
            self.y_running = th.Thread(target=task)
            self.y_running.start()
        except tb.InputError as e :
            tk.messagebox.showerror(title="INPUT ERROR", message=e)
        except Exception as e :
            tk.messagebox.showerror(title="ERROR", message=e)
    def z_abort(self) :
        del self.y_running
    def z_hasse(self) :
        fred.hasse.hasse(self.y_tab, self.y_output.SKB).write('hasse.png', format='png')
        os.system('hasse.png')
    def z_about(self) :
        m = '''ot_py (alpha)
7/31/2014
        '''
        tk.messagebox.showinfo(title="About", message=m)

root = tk.Tk()
app = Application(master=root)
app.mainloop()
