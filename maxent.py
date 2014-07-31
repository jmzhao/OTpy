## An implentation of Maximum Entropy model (Goldwater and Johnson 2003)
import scipy.optimize
import math

def MaximumEntropy(t, callback=None) :
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