import tkinter as tk
import tkinter.scrolledtext
import tkinter.filedialog
import tkinter.messagebox
import os
import threading as th
import time ## ctime
import queue
import webbrowser as wbb

## open a folder in window cross-platformly
import subprocess
import sys
if sys.platform == 'darwin':
    def openFolder(path):
        subprocess.check_call(['open', '--', path])
elif sys.platform == 'linux2':
    def openFolder(path):
        subprocess.check_call(['gnome-open', '--', path])
elif sys.platform == 'win32':
    def openFolder(path):
        subprocess.check_call(['explorer', path])
        
import tableau as tb
import cd
import fred
import maxent
import cfg

def timing(func, *arg, **dic) :
    t0 = time.clock()
    ans = func(*arg, **dic)
    t1 = time.clock()
    return ans, t1-t0

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.y_info = {
            'libname':  'ot_py',
            'appname':  "OTpy",
            'version':  '0.3.1',
            'build':    '140828',
            'author':   'jmzhao',
            'github':   'https://github.com/jmzhao/ot_py'
        }
        self.y_datainfo = {}
        
        self.pack()
        self.createMenubar()
        self.createWidgets()
        self.master.title(self.y_info['appname'])
        print('working directory:', os.getcwd())
        self.checkFiles()
    
    def createMenubar(self):
        ## menu bar
        self.menubar = tk.Menu(self)
        self.master.config(menu=self.menubar)
        ### File
        self.menuFile = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.menuFile)
        self.menuFile.add_command(label="Open", command=self.z_loadFile)
        self.menuFile.add_separator()
        self.menuFile.add_command(label="Config", command=self.z_config)
        ### Run
        self.menuRun = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Run", menu=self.menuRun)
        self.menuRun.add_command(label="Run Constraint Demotion (CD)", command=self.z_cd, state=tk.DISABLED)
        self.menuRun.add_command(label="Run Fusional Reduction (FRed)", command=self.z_fred, state=tk.DISABLED)
#        self.menuRun.add_command(label="Run Maximum Entropy (MaxEnt)", command=self.z_maxent, state=tk.DISABLED)
        self.menuRunMaxent = tk.Menu(self.menuRun, tearoff=0)
        self.menuRun.add_cascade(label="Run Maximum Entropy (MaxEnt)", menu=self.menuRunMaxent, state=tk.DISABLED)
        self.menuRunMaxent.add_command(label="Using Generalized Iterative Scaling (GIS)", 
                                       command=(lambda : self.z_maxent('GIS')))
        self.menuRunMaxent.add_command(label="Using Sequential Conditional Generalized Iterative Scaling (SCGIS)", 
                                       command=(lambda : self.z_maxent('SCGIS')))
        self.menuRunMaxent.add_command(label="Using Nonlinear Conjugate Gradient method (CG)", 
                                       command=(lambda : self.z_maxent('CG')))
        self.menuRun.add_separator()
        self.menuRun.add_command(label="Abort Running", command=self.z_abort, state=tk.DISABLED)
        ### Show
        self.menuShow = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Show", menu=self.menuShow)
        self.menuShow.add_command(label="Show Hasse Diagram", command=self.z_hasse, state=tk.DISABLED)
        self.menuShow.add_command(label="Show Tableau", command=self.z_tableau, state=tk.DISABLED)
        self.menuShow.add_separator()
        self.menuShow.add_command(label="Show Resouce Folder", command=self.z_folder, state=tk.NORMAL)
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
    
    def checkFiles(self) :
        self.f_cwd = os.getcwd()
        self.f_res_folder = 'res'
        self.f_fcfg = self.getResouceFileName('config.ini')
    def getResouceFileName(self, *args) :
        return os.path.join(self.f_cwd, self.f_res_folder, *args)
    
    @property  
    def y_output(self) :
        return self._y_output['value']
    @y_output.setter
    def y_output(self, value_dict) :
        del self.y_output
        if type(value_dict) is not dict : value_dict = {'value':value_dict}
        self._y_output = value_dict
        toString = value_dict.get('toString', lambda x: x)
        self.xst_output.insert(tk.END, toString(self.y_output))
        if value_dict.get('caller') == self.z_fred :
            self.menuShow.entryconfigure(0, state=tk.NORMAL)
        if value_dict.get('caller') in (self.z_cd, self.z_maxent) :
            self.menuShow.entryconfigure(1, state=tk.NORMAL)
    @y_output.deleter
    def y_output(self) :
        if hasattr(self, '_y_output') : del self._y_output
        self.xst_output.delete(1.0, tk.END)
        self.menuShow.entryconfigure(0, state=tk.DISABLED)
        self.menuShow.entryconfigure(1, state=tk.DISABLED)
        
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
        #self.menuShow.entryconfigure(1, state=tk.NORMAL)
    @y_input.deleter
    def y_input(self) :
        if hasattr(self, '_y_input') : del self._y_input
        for k in range(3) :
            self.menuRun.entryconfig(k, state=tk.DISABLED)
        self.menuShow.entryconfigure(1, state=tk.DISABLED)
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
#    @property
#    def y_error(self) :
#        return self._y_error
#    @y_error.setter
#    def y_error(self, e) :
#        self._y_error = e
#        tk.messagebox.showerror(title="ERROR", message=e)        
        
    def z_loadFile(self) :
        ''' action for load file button '''
        fpath = tk.filedialog.askopenfilename(
            filetypes=(("Plain text", "*.txt"),
                       ("All files", "*.*")))
        fdir, fname = os.path.split(fpath)
        fnamebase, fnameext = os.path.splitext(fname)
        self.y_datainfo.update({
            'inputpath':    fpath,
            'inputdir':     fdir,
            'inputname':    fname,
            'inputnamebase': fnamebase,
            'inputnameext': fnameext,
        })
        resdir = self.getResouceFileName(fnamebase)
        if not os.path.exists(resdir) :
            os.makedirs(resdir)
        try :
            f = open(fpath)
        except Exception as e :
            tk.messagebox.showerror(title="INPUT ERROR", message=e)
            return 
        f = f.read()
        self.y_input = str(f)
        del self.y_output
    def z_config(self) :
        ''' open config file '''
        fname = '"%s"'%self.f_fcfg
        th.Thread(target=os.system, args=(fname,)).start()
#        os.system(fname)
    def z_cd(self) :
        ''' actiion for Constraint Demotion button '''
        del self.y_output
        t = tb.tableau()
        try :
            t.readString(self.y_input)
            ans, tim = timing(cd.ConstraintsDemotion, t)
            self.y_output = {'caller':self.z_cd, 'value':ans, 'time':tim, 'toString':cd.toString}
        except tb.InputError as e :
            tk.messagebox.showerror(title="INPUT ERROR", message=e)
        except Exception as e :
            tk.messagebox.showerror(title="ERROR", message=e)
            #self.ysv_errmsg.set('ERROR: '+str(e))
    def init_queue(self) :
        self.queue_output = queue.Queue()
        self.queue_error = queue.Queue()
    def put_queue(self, d) :
        if isinstance(d, Exception) :
            self.queue_error.put(d)
        else :
            self.queue_output.put(d)
    def process_queue(self) :
        try :
            while True :
                try :
                    e = self.queue_output.get(0)
                    self.y_output = e
                except queue.Empty :
                    break
            e = self.queue_error.get(0)
            tk.messagebox.showerror(title="ERROR", message=e)      
        except queue.Empty :
            self.master.after(50, self.process_queue)
            
    def z_fred(self) :
        ''' actiion for Fusional Reduction button '''
        self.y_output = {'value':'computing...'}
        t = tb.tableau()
        self.init_queue()
        try :
            t.readString(self.y_input)
            self.y_tab = t
            def task() :
                try :
                    ans, tim = timing(fred.FRed, fred.erc.get_ERClist(t))
                    self.put_queue({'caller':self.z_fred,  'value':ans, 'time':tim,})
                except Exception as e :
                    self.put_queue(e)
            self.y_running = th.Thread(target=task)
            self.y_running.start()
            self.process_queue()
        except tb.InputError as e :
            tk.messagebox.showerror(title="INPUT ERROR", message=e)
        except Exception as e :
            tk.messagebox.showerror(title="ERROR", message=e)
    def z_maxent(self, method) :
        ''' actiion for Maximum Entropy button '''
        t = tb.tableau()
        try :
            t.readString(self.y_input)
            dcfg = cfg.get_config_as_dict(self.f_fcfg)
        except tb.InputError as e :
            tk.messagebox.showerror(title="INPUT ERROR", message=e)
        except Exception as e :
            tk.messagebox.showerror(title="ERROR", message=e)
        self.init_queue()
        cnt = [0]
        repgap = max(1, int((100 if method=='CG' else 2000 ) / len(t.constraints)))
        self.z_abort = False
        def rep(w) :
            cnt[0] += 1
            if cnt[0] % repgap == 0 :
                self.put_queue('Iteration count: %d\n'%(cnt[0]))
            if self.z_abort : 
                self.put_queue('Aborted.')
                raise KeyboardInterrupt
        try :
            self.queue = queue.Queue()
            def task() :
                try :
                    ans, tim = timing(maxent.MaximumEntropy, t, 
                                    method=method, callback=rep, **dcfg[method])
                    def toString(a) :
                        s = sorted(
                            ((t.get_constraint(index=i).abbr, -w) for i, w in a.items()), 
                            key=(lambda a:a[1]), reverse=True)
                        return '\n'.join(('%'+str(max(len(abbr) for abbr, _ in s))+'s\t%s')%x for x in s)
                    self.put_queue({
                        'caller':self.z_maxent, 'value':ans, 'time':tim,
                        'toString':toString, 'method':method})
                except Exception as e :
                    self.put_queue(e)
            self.y_running = th.Thread(target=task)
            self.y_running.start()
            self.process_queue()
        except Exception as e :
            tk.messagebox.showerror(title="ERROR", message=e)
    def z_abort(self) :
        self.z_abort = True
    def z_HTMLheader(self) :
        caller = self._y_output['caller'].__name__[2:]
        method = self._y_output.get('method')
        return ('''<h1>%(appname)s</h1>
        <p>ver%(version)s build%(build)s</p>'''%self.y_info
        +'<ul>'
        +'<li>Input file: %(inputpath)s</li>'%self.y_datainfo
        +'<li>Algorithm: %s</li>'%(caller + (' using %s'%method if caller=='maxent' else ''))
        +'<li>Running time: %(time)fs</li>'%(self._y_output)        
        +'<li>Page generated at: %s</li>'%time.ctime()
        +'</ul>')
    def z_hasse(self) :
        fname = self.getResouceFileName(self.y_datainfo['inputnamebase'], 'hasse.png')
        fred.hasse.hasse(self.y_tab, self.y_output.SKB).write(fname, format='png')
        fhtml = self.getResouceFileName(self.y_datainfo['inputnamebase'], 'hasse.html')        
        f = open(fhtml, 'w')
        f.write(self.z_HTMLheader())
        f.write('<h2>Hasse Diagram</h2>'
            +'<img src="./hasse.png" />')
        f.close()
#        th.Thread(target=os.system, args=(fname,)).start()
        wbb.open_new_tab(fhtml)
    def z_tableau(self) :
        caller = self._y_output['caller'].__name__[2:]
        method = self._y_output.get('method')
        aff = caller+'_'+method if method else caller
        print('in z_tableau: aff="%s"'%(aff))
        fhtml = self.getResouceFileName(self.y_datainfo['inputnamebase'], 'tableau_%s.html'%(aff))
        f = open(fhtml, 'w')
        f.write(self.z_HTMLheader())
        f.write('<link rel="stylesheet" type="text/css" href="../tableau.css" />')
        f.write(tb.tableau(string=self.y_input).toHTML(**{caller:self.y_output}))
        f.close()
#        th.Thread(target=os.system, args=(fhtml,)).start()
        wbb.open_new_tab(fhtml)
    def z_folder(self) :
        openFolder(self.getResouceFileName())
    def z_about(self) :
        m = '''
%(appname)s (ver%(version)s build%(build)s)
GitHub: %(github)s'''%(self.y_info)
        tk.messagebox.showinfo(title="About", message=m)

root = tk.Tk()
app = Application(master=root)
app.mainloop()
