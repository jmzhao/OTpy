## An implentation of several algorithms for training Maximum Entropy model,
## including:
## Generalized Iterative Scaling (described in Goodman 2002) 
## Sequential Conditional Generalized Iterative Scaling (as above)
## maximize Log Likelihood using (Nonlinaer) Conjugate Gradient method (Goldwater & Johnson 2003)

import math
import warnings

#import scipy.optimize ## for Conjugate Gradient ## no longer needed
import cg ## my handmade CG

def MaximumEntropy(t, method='CG', **d) :
    ''' Maximum Entropy model
    method = 'GIS'|'SCGIS'|'CG', 'CG' is default.
    
    GIS: Generalized Iterative Scaling,
        (described in Goodman 2002)
    SCGIS: Sequential Conditional Generalized Iterative Scaling, 
        (Goodman 2002)
        //problem _scgis1: may produce mismatching predictions (This is solved. 
        See comments in maxent_scgis.)
    CG: Nonlinear Conjugate Gradient method,
        (Goldwater & Johnson 2003)
        Some critical parameter may need to be adjusted, e.g. sigma0 to achieve convergence.'''
    return {'GIS':maxent_gis,
            'SCGIS':maxent_scgis,
            'CG':maxent_cg, ## under construction
            }.get(method)(t, **d)

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
    slowing_factor_list = tuple(max(max(c.vio[i]
                for c in ins.cand)
            for ins in instance)
        for i in range(len(cons_ind)))
            
    ans = {'ins':instance, 'obs':observed, 'slo':slowing_factor, 
    'ind':cons_ind, 'slolist':slowing_factor_list}
    print(ans)
    return ans
            
def maxent_gis(t, maxiter=10000, needtrim=True, lower_lim=-50, upper_lim=0, 
               callback=None, **unknown_opt) :
    '''Generrized Iterative Scaling'''
    _check_unknown_options(unknown_opt)
    inp = get_maxent_input(t)
    instance = inp['ins']
    observed = inp['obs']
    slowing_factor = inp['slo']
    cons_ind = inp['ind']
    all0 = list(0 for _ in cons_ind)
    cons_n = len(cons_ind)
    if needtrim :
        def trim(w) :
            return max(min(w, upper_lim), lower_lim)
    else :
        def trim(w) : return w
    
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

def maxent_scgis(t, maxiter=10000, needtrim=True, lower_lim=-50, upper_lim=0, 
                 callback=None, **unknown_opt) :
    '''Sequential Conditional Generalized Iterative Scaling'''
    _check_unknown_options(unknown_opt)
    inp = get_maxent_input(t)
    instance = inp['ins']
    observed = inp['obs']
    sf_list = inp['slolist']
    cons_ind = inp['ind']
    all0 = list(0 for _ in cons_ind)
    cons_n = len(cons_ind)
    if needtrim :
        def trim(w) :
            return max(min(w, upper_lim), lower_lim)
    else :
        def trim(w) : 
            return w
    toupper = upper_lim - lower_lim
    tolower = - toupper
    
    w = list(all0)
    z = list(len(ins.cand) for ins in instance)
    s = list(list(0 for c in ins.cand)
        for ins in instance)
    for _ in range(maxiter) :
        for i in range(cons_n) :
            expectedi = sum(ins.freq*sum(c.vio[i]*math.exp(s[j][y])/z[j]
                    for y, c in enumerate(ins.cand) if c.vio[i] != 0)
                for j, ins in enumerate(instance))
            if observed[i] != 0 :
                #print('expectedi:', expectedi)
                di = (math.log(observed[i]/expectedi) / sf_list[i]
                    if expectedi > 0 else toupper)
                wi = trim(w[i]+di)
            else : 
                wi = lower_lim
            if wi != w[i] :
                di = wi - w[i]
                w[i] = wi
                for j, ins in enumerate(instance) :
                    for y, c in enumerate(ins.cand) :
                        if c.vio[i] != 0 :
                            z[j] -= math.exp(s[j][y])
                            s[j][y] += di * c.vio[i] 
                            ## facter $c.vio[i] is not presented in the psuadecode (Figure 2, Goodman 2002)
                            ## After adding this, problem _scgis1 solved.
                            z[j] += math.exp(s[j][y])
            ## Due to the cumulative float point error, the value of $z and $s  
            ## may need to be recalculated by definition after every several 
            ## iterations or when the error will cause an notable harm to con-
            ## vergence. The suitable timing is left to be determined.
        if callback : callback(w)
    return dict(zip(cons_ind, w))

def loglikelihood(t) :
    inp = get_maxent_input(t)
    instance = inp['ins']
    def f(w) :
        ans = 0
        #w = tuple(wi if coi > 0 else 0 for wi, coi in zip(w, co))
        for ins in instance :
            logw = tuple(sum(wi*fi 
                    for wi, fi in zip(w, c.vio) if fi != 0)
                for c in ins.cand)
            #print('logw:', logw)
            logz = math.log(sum(math.exp(x) for x in logw))
            #print('logz:', logz)
            ans += sum(c.freq * logwi 
                for logwi, c in zip(logw, ins.cand) if c.freq != 0)
            ans -= ins.freq * logz
        return ans
    return f
    

def maxent_cg(t, prior=None, trim0=False,
              epsilon=cg.epsilon, tol=1e-9, maxiter=None, 
              linear=cg.linear_secant, linear_tol=1e-5, linear_maxiter=4, sigma0=0.01, approx_hessian=False, 
              callback=None, **unknown_opt) :
    _check_unknown_options(unknown_opt)
#    cnt_examples = 0
#    for d in t.datum :
#        for frequency in d.winners.values() :
#            cnt_examples += frequency
    inp = get_maxent_input(t)
    instance = inp['ins']
    #observed = inp['obs']
    cons_ind = inp['ind']
    #all0 = list(0 for _ in cons_ind)
    #cons_n = len(cons_ind)
    if prior == None : prior = lambda _ : 0
    
    co = list(1 for _ in cons_ind)
    def f(w) :
        ans = 0
        w = tuple(wi if coi > 0 else 0 for wi, coi in zip(w, co))
        for ins in instance :
            logw = tuple(sum(wi*fi 
                    for wi, fi in zip(w, c.vio) if fi != 0)
                for c in ins.cand)
            #print('logw:', logw)
            logz = math.log(sum(math.exp(x) for x in logw))
            #print('logz:', logz)
            ans += sum(c.freq * logwi 
                for logwi, c in zip(logw, ins.cand) if c.freq != 0)
            ans -= ins.freq * logz
        return ans

    w0 = tuple(0 for _ in t.get_constraint_indices())
    
    fcg = lambda w : - f(w) + prior(w)
    cg_opt = {'epsilon':epsilon, 'tol':tol, 'maxiter':maxiter, 
              'linear':linear, 'linear_tol':linear_tol, 'linear_maxiter':linear_maxiter, 
              'sigma0':sigma0, 'approx_hessian':approx_hessian, 
              'callback':callback}
    while True :
        ans = cg.nonlinear_cg(fcg, w0, **cg_opt)
        icons, w = max(enumerate(ans), key=lambda x:x[1])
        if w <= 0 or not trim0 : break
        co[icons] = 0
#    ans = scipy.optimize.fmin_cg(f, w0, callback=callback)#, bounds=list((None, 0) for w in w0))
    print('f(x):', f(ans))
    
    return dict(zip(cons_ind, ans))
    
## extracted from scipy.optimize
class MaxentWarning(UserWarning) :
    pass
def _check_unknown_options(unknown_options):
    if unknown_options:
        msg = ", ".join(map(str, unknown_options.keys()))
        # Stack level 4: this is called from _minimize_*, which is
        # called from another function in Scipy. Level 4 is the first
        # level in user code.
        warnings.warn("Unknown solver options: %s" % msg, MaxentWarning, 4)
