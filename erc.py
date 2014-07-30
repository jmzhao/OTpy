#import tableau as tb

class Error(Exception) :
    pass

class InvalidValueError(Error) :
    pass
class value(int) :
    def __str__(self) :
        try :
            return ('L', 'e', 'W')[self]
        except IndexError :
            raise InvalidValueError(self)
    __repr__ = __str__
vW = value(2)
ve = value(1)
vL = value(0)
#def value(x) :
#    if x == 0 : return vL
#    if x == 1 : return ve
#    if x == 2 : return vW
#    raise InvalidValueError(x)
class ERC(tuple) :
    def __hash__(self) :
        ans = 0
        for v in self :
            ans *= 3
            ans += v
        return ans
    def cnt_value(self, value) : 
        return sum(1 for v in self if v == value)
    def get_indices(self, value) : 
        return (i for i,x in enumerate(self) if x == value)

## Lombardi’s Swedish, used frequently in (Prince and Brasoveanu 2010)
test_ercs = [
    ERC((ve,ve,vW,vL)),
    ERC((ve,vW,vL,ve)),
    ERC((vW,vL,vW,ve)),
    ERC((ve,ve,vW,vW)),
    ERC((ve,vW,vL,vW)),
    ERC((vW,vL,vW,vL)),
    ERC((vW,vW,vL,ve))
]

#def cmp(value1, value2) :
#    ''' according to the ordering "L<e<W", return -1/0/1 '''
#    return value1 - value2 

def arrow(erc1, erc2) :
    ''' return whether erc1->erc2 '''
    for v1,v2 in zip(erc1, erc2) :
        if v1 > v2 : return False
    return True

def fuse_value(v1, v2) :
    ''' fuse on each value pair, tricky! '''
    ans = v1 * v2
    return value(min(ans, 2))
    
def fuse2(erc1, erc2) :
    ''' fuse 2 ERCs '''
    return ERC(fuse_value(a,b) for a,b in zip(erc1, erc2))

class EmptyERCSetError(Error) :
    pass
def fuse(iterable) :
    ''' input ERCs, return thier fusion 
    raise EmptyERCSetError if fed with empty set (or sth like that)'''
    i = iter(iterable)
    try :
        ans = next(i)
    except StopIteration :
        raise EmptyERCSetError
    while True :
        try : 
            e = next(i)
        except StopIteration :
            break
        ans = fuse2(ans, e)
    return ans
       
def get_ERClist(tab) :
    ''' extract ERCs suitable for calling FRed from a tableau 'tab' '''
    cand_ind = tab.get_constraint_indices()
    def toValue(degree1, degree2) :
        return vW if degree1 > degree2 else ve if degree1 == degree2 else vL
    def toERC(loser_vio_dict, winner_vio_dict) :
        return ERC(toValue(loser_vio_dict.get(i,0), winner_vio_dict.get(i,0)) for i in cand_ind)
    ans = set()
    for data in tab.datum :
        for cand in data.candidates :
            if cand != data.winner :
                ans.add(toERC(data.candidates[cand], data.candidates[data.winner]))
    return ans