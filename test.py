import tableau as tb
import cd

t = tb.tableau()

def test(fname) :
    print('-----test for "%s"------'%fname)
    try :
        t.readFile(fname)
        print(cd.toString(cd.ConstraintsDemotion(t)))
    except tb.InputError as e :
        print('Error when reading file:', e)
    except ValueError as e :
        print('Error when processing:', e)

test('''.\InputFiles\Ilokano.txt''')
#test('''.\InputFiles\contradiction.txt''')
test('''.\InputFiles\HarmonicallyBounded.txt''')
test('''.\InputFiles\Hebrew.txt''')