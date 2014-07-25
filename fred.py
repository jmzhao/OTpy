## An implentation of Fusional Reduction Algorithm (Prince and Brasoveanu 2010)
#import tableau as tb
import erc

class Error(Exception) :
    pass
class ProcessError(Error) :
    pass
class UnsatisfiableError(ProcessError) :
    def __init__(self, erclist, *args) :
        super().__init__(*args)
        self.unsatisfiable_ERClist = erclist
    def __str__(self) :
        return 'fail when processing unsatisfiable ERCs as: %s'%(
            self.unsatisfiable_ERClist)

class __FRedans :
    ''' for the return value of FRed(...) '''
    def __init__(self) :
        self.MIB = set()
        self.SKB = set()
    def update(self, ans) :
        self.MIB.update(ans.MIB)
        self.SKB.update(ans.SKB)
    def add(self, MIBerc, SKBerc) :
        self.MIB.add(MIBerc)
        self.SKB.add(SKBerc)
    def __str__(self) :
        return ('MIB:\n'
        + '\n'.join(str(e) for e in self.MIB)
        + '\nSKB:\n'
        + '\n'.join(str(e) for e in self.SKB)
        )
''' use erc.get_ERClist(t) to get suitable input '''
def FRed(ERClist) :
    ''' Fusional Reduction Algorithm.
    input: list of Elementary Ranking Conditions (ERCs): list(ERC)
    output: Most Infomative Basis (MIB): set(ERC) '''
    ans = __FRedans() ## to store results
    ## calculate the fusion of all ERCs
    try :
        fus = erc.fuse(ERClist)
    except erc.EmptyERCSetError :
        ## the input is an empty set
        return ans ## empty result
    print('fus:', fus)
    ## count the number of W(L) in fus
    cnt_fus_W = fus.cnt_value(erc.vW)
    cnt_fus_L = fus.cnt_value(erc.vL)
    ## check if fus is an L+ (an invalid ERC)
    if cnt_fus_L > 0 and cnt_fus_W == 0 :
        ## announce error and exit
        raise UnsatisfiableError(erclist=ERClist)
        ## if this is the case, there is no need to continue processing
    ## info loss residues are all that cannot be entailed from fus
    total_residue = tuple(e for e in ERClist if not erc.arrow(fus, e))
    print('total_residue', total_residue)
    ## find each residue and do FRed on each of them (recursion)
    if len(total_residue) > 0 :
        for i, v in enumerate(fus) :
            if v == erc.vW : ## this is where "f A[i] = W"
                ## "Res(A,i)"
                residue = list(e for e in total_residue if e[i] == erc.ve)
                if len(residue) == 0 : continue
                print('i =', i, residue)
                ## calc "FNF(Res(A,i))" and union it to ans
                ## residue may be empty, but it doesn't matter
                ans.update(FRed(residue))
        fus_res = erc.fuse(total_residue)
        ## for SKB
        new_fus = erc.ERC(erc.ve if v == erc.vL else fus[i] for i,v in enumerate(fus_res))
    else :
        new_fus = fus
    ## decide whether fus needs to be retained in ans, blend with MIB and SKB
    ## check if fus is an W* (an valid ERC) or "f TR(A) -> f A"
    if new_fus.cnt_value(erc.vL) == 0 :
        ## omit fus from Fusional Normal Form (FNF)
        pass
    else : ## retain it
        ans.add(MIBerc=fus, SKBerc=new_fus)
    return ans
    