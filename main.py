import tableau
import cd

def test(fname) :
    t = tableau.tableau(fname)
    print('Stratum\tAbbreviation')
    for c, s in cd.ConstraintsDemotion(t) :
        print(s, c.abbr, sep='\t')