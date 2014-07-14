import tableau as tb
import cd

def test(fname) :
    print('-----test for "%s"------'%fname)
    t = tb.tableau(fname)
    try :
        print(cd.toString(cd.ConstraintsDemotion(t)))
    except ValueError as e :
        print(e)

test('Ilokano.txt')
test('TinyIllustrativeFile.txt')
test('contradiction.txt')