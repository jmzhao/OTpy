# -*- coding: utf-8 -*-
import os.path

import tableau as tb
import cd
import fred
import maxent

t = tb.tableau()

def test(fname) :
    print('-----test for "%s"------'%fname)
    try :
        t.readFile(fname)
        print('read file done:')
        print(t.get_constraint_indices())
        print(*(cand.abbr for cand in t.constraints))
        #print(*(d.candidates for d in t.datum))
        ## MaxEnt
#        print(*sorted((w, t.get_constraint(index=i).abbr) 
#                    for i, w in (maxent.MaximumEntropy(t)).items()),
#            sep='\n')
#        ## FRed
#        ercs = fred.erc.get_ERClist(t)
#        print('ERCs:', *ercs, sep='\n')
#        fredans = fred.FRed(ercs)
#        print(fredans)
#        ### Hasse Diagram
#        root, ext = os.path.splitext(fname)
#        fred.hasse.hasse(t, fredans.SKB).write(root+'.png', format='png')
        ## CD (last because it will modify the tableau)
        rank_stratum = cd.ConstraintsDemotion(t)
        print(cd.toString(rank_stratum))
        fhtml='tableau.html'
        print(tb.tableau(fname).toHTML(rank=rank_stratum), 
              file=open(fhtml,'w'))#, errors='replace', encoding="ISO-8859-1"))
        os.system(fhtml)
    except tb.InputError as e :
        print('Error when reading file:', e)
    except (cd.UnsatisfiableError, fred.UnsatisfiableError) as e :
        print('Error when processing:', e)

#test('''.\InputFiles\Ilokano.txt''')
#test('''.\InputFiles\contradiction.txt''')
#test('''.\InputFiles\HarmonicallyBounded.txt''')
test('''.\InputFiles\Hebrew.txt''')