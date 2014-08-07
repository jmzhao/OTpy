## An implentation of Maximum Entropy model (Goldwater and Johnson 2003)
#import scipy.optimize ## for Conjugate Gradient
import math

def MaximumEntropy(t, method='GIS', callback=None, **d) :
    return {'GIS':maxent_gis,
            #'CG':maxent_cg, ## under construction
            }.get(method)(t, callback=callback, **d)

class __ins_object :
    def __init__(self) :
        self.cand = None
        self.freq = None
    def __str__(self) :
        return '%s%s'%(self.freq, self.cand)
    __repr__ = __str__
class __cand_object :
    def __init__(self) :
        self.vio = None
        self.freq = None
    def __str__(self) :
        return '%s%s'%(self.freq, self.vio)
    __repr__ = __str__
def get_maxent_input(t) :
    cnt_examples = 0
    for d in t.datum :
        for frequency in d.winners.values() :
            cnt_examples += frequency
    '''
    instance = list()
    for d in t.datum :
        ins = object()
        ins.f = tuple(vio_dict for cand, vio_dict in d.candidates.items() )
        ins.freq = dict((i, d.winners[cand]/cnt_examples)
            for i, cand in enumerate(d.candidates) if cand in d.winners)
        ins.tot_freq = sum(ins.freq.values())
        instance.append(ins)
    observed = dict((i_cons, 
                     sum(sum(ins.f[j_cand].get(i_cons, 0)*freq for j_cand, freq in ins.freq.values()) 
                     for ins in instance))
                     for i_cons in t.get_constraint_indices()):
    slow = max(max( for y_cand in ins.f)
            for ins in instance)
    '''
    cons_ind = t.get_constraint_indices()
    instance = list()
    for d in t.datum :
        ins = __ins_object()
        ins.cand = list()
        for cand, vio_dict in d.candidates.items() :
            c = __cand_object()
            c.vio = tuple(vio_dict.get(i, 0) for i in cons_ind)
            c.freq = d.winners.get(cand, 0)  / cnt_examples
            ins.cand.append(c)
        ins.freq = sum(c.freq for c in ins.cand)
        instance.append(ins)
    observed = tuple(sum(sum(c.vio[i]*c.freq
                for c in ins.cand)
            for ins in instance) 
        for i in range(len(cons_ind)))
    slowing_factor = max(max(sum(c.vio)
            for c in ins.cand)
        for ins in instance)
            
    ans = {'ins':instance, 'obs':observed, 'slo':slowing_factor, 
    'ind':cons_ind}
    print(ans)
    return ans
            
def maxent_gis(t, maxiter=1000, lower_lim=-50, upper_lim=0, callback=None) :
    inp = get_maxent_input(t)
    instance = inp['ins']
    observed = inp['obs']
    slowing_factor = inp['slo']
    cons_ind = inp['ind']
    all0 = list(0 for _ in cons_ind)
    cons_n = len(cons_ind)
    def trim(w) :
        return max(min(w, upper_lim), lower_lim)
    
    w = tuple(all0)
    for _ in range(maxiter) :
        expected = all0.copy()
        for ins in instance :
            sj = tuple(sum(wi*fi for wi, fi in zip(w,c.vio) if fi != 0)
                for c in ins.cand)
            z = sum(math.exp(sjy) for sjy in sj)
            for y, c in enumerate(ins.cand) :
                for i, fi in enumerate(c.vio) :
                    if fi != 0 :
                        expected[i] += fi * math.exp(sj[y]) / z * ins.freq
            #expected = tuple(e/z for e in expected)
        
        delta = tuple(math.log(oi/ei)/slowing_factor if oi!=0 else lower_lim
            for oi,ei in zip(observed, expected))        
        w = tuple(trim(wi+di) for wi,di in zip(w,delta))
        if callback : callback(w)
    return dict(zip(cons_ind, w))

def maxent_cg(t, callback=None) :
    sigmaSquared = 1000000
    cnt_examples = 0
    for d in t.datum :
        for frequency in d.winners.values() :
            cnt_examples += frequency
    def f(w) :
        ans = 0
        for d in t.datum :
            logw = dict() ## Sigma_{i=1}^{m}w_i*f_i(y,x) in fomula (1)
            for cand, vio_dict in d.candidates.items() :
                logw[cand] = sum(w[index]*degree for index, degree in vio_dict.items())
            logz = math.log(sum(math.exp(x) for x in logw.values()))
            for win, frequency in d.winners.items() :
                ans += frequency * (logw[win] - logz)
        ans /= cnt_examples
        ans -= sum(wi*wi for wi in w) / (2*sigmaSquared)
        return -ans

    w0 = tuple(0 for _ in t.get_constraint_indices())

    return scipy.optimize.fmin_cg(f, w0, callback=callback)