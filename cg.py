import math

def dot(v1, v2) :
    return sum(x1*x2 for x1,x2 in zip(v1,v2))
    
epsilon = math.sqrt(7/3 - 4/3 - 1)

def linear_newton(fprime, fhess_p, x, d, newton_tol, newton_maxiter) :
    delta_d = dot(d, d)
    print('d:', d)
    alpha = 1 / newton_tol
    for __ in range(newton_maxiter) :
        alpha_old = alpha
        alpha = - dot(fprime(x), d) / dot(d, fhess_p(x, d))
        if abs(alpha / alpha_old) > 1 :
            break
        print('alpha:', alpha)
        x = tuple(xi + alpha * di for xi, di in zip(x, d))
        if alpha*alpha*delta_d < newton_tol :
            break
    return alpha, x

def linear_secant(fprime, x, d, tol, maxiter, sigma0) :
    delta_d = dot(d, d)
    print('d:', d)
    alpha = -sigma0
    ita_prev = dot(d, fprime(tuple(xi+sigma0*di for xi,di in zip(x,d))))
    for __ in range(maxiter) :
        ita = dot(d, fprime(x))
        rat = ita / (ita_prev - ita)
        if __ > 0 and abs(rat) > 1 : break
        alpha *= rat
        print('alpha:', alpha)
        x = tuple(xi + alpha * di for xi, di in zip(x, d))
        if alpha*alpha*delta_d < tol :
            break
    return alpha, x
    
def nonlinear_cg(f, x0, fprime=None, epsilon=epsilon, tol=1e-9, maxiter=None, 
                 linear=linear_secant, linear_tol=1e-5, linear_maxiter=4, 
                     sigma0=0.1, 
                     approx_hessian=False,
                 callback=None) :
    """
    Minimize a function using a nonlinear conjugate gradient algorithm
    with Secant and PR. 
    NR: Newton-Rahson, PR: Polak-Ribiere, FR: Fletcher-Reeves.
    """
    nx = len(x0)
    if maxiter == None : 
        maxiter = 200 * nx
    if fprime == None :
        def fprime(x) :
            x = list(x)
            xeps = tuple(xi * epsilon if xi!=0 else epsilon for xi in x)
            f0 = f(x)
            ans = list()
            for i in range(nx) :
                old = x[i]
                x[i] += xeps[i]
                ans.append((f(x)-f0)/xeps[i])
                x[i] = old
#            print('fprime:', ans)
            return ans
    ## define fhess_p(d) for $ f''(x) \dot d
    if approx_hessian :
        def fhess_p(x, d) :
            pass
    else :
        def fhess_p(x, d) :
            x = list(x)
            esqr = epsilon * epsilon
            xeps = tuple(xi * epsilon if xi!=0 else epsilon for xi in x)
            ans = list()
            f0 = f(x)
            fp = list()
            for i in range(nx) :
                oldxi = x[i]
                x[i] += xeps[i]
                fp.append(f(x))
                ansi = 0
                for j in range(i) :
                    oldxj = x[j]
                    x[j] += xeps[j]
                    t1 = (f(x) - fp[i])
                    t2 = (- fp[j] + f0)
                    ansi += (t1 + t2) * d[j]
                    x[j] = oldxj
                ansi *= 2
                x[i] = oldxi + 2*xeps[i]
                t1 = (f(x) - fp[i])
                t2 = (-fp[i] + f0)
                ansi += (t1 + t2) * d[i]
                ans.append(ansi)
                x[i] = oldxi
            ans = tuple(x / (esqr) for x in ans)
#            print('fhess_p:', ans)
            return ans
    
    k = 0
    x = x0
    r = tuple(-xi for xi in fprime(x))
    d = r
    delta_old = 0
    delta_new = dot(r, r)
    delta_0 = delta_new
    for _ in range(maxiter) :
        print('iter:', _)
        print('delta_new:', delta_new , tol * delta_0)
        if delta_new < tol :#* delta_0 :
#        print('abs:', abs(delta_new - delta_old))
#        if abs(delta_new - delta_old) < tol :
            break
        if linear == linear_secant :
            alpha, x = linear_secant(fprime, x, d, linear_tol, linear_maxiter, sigma0)
        else :
            alpha, x = linear_newton(fprime, fhess_p, x, d, linear_tol, linear_maxiter)
        #x = tuple(min(0,xi) for xi in x)
        r_old = r
        r = tuple(-xi for xi in fprime(x))
        delta_old = delta_new
        delta_mid = dot(r, r_old)
        delta_new = dot(r, r)
        beta = max(0, (delta_new - delta_mid) / delta_old)
        d = tuple(ri + beta * di for ri, di in zip(r, d))
#        k += 1
#        if k == nx or beta <= 0 :#dot(r, d) <= 0 :
#            d = r
#            k = 0
        if callback : callback(x)
    
    return x
    """
    Parameters
    ----------
    f : callable, ``f(x, *args)``
        Objective function to be minimized.  Here `x` must be a 1-D array of
        the variables that are to be changed in the search for a minimum, and
        `args` are the other (fixed) parameters of `f`.
    x0 : tuple
        A user-supplied initial estimate of `xopt`, the optimal value of `x`.
        It must be a 1-D array of values.
    fprime : callable, ``fprime(x, *args)``, optional
        A function that returns the gradient of `f` at `x`. Here `x` and `args`
        are as described above for `f`. The returned value must be a 1-D array.
        Defaults to None, in which case the gradient is approximated
        numerically (see `epsilon`, below).
    args : tuple, optional
        Parameter values passed to `f` and `fprime`. Must be supplied whenever
        additional fixed parameters are needed to completely specify the
        functions `f` and `fprime`.
    gtol : float, optional
        Stop when the norm of the gradient is less than `gtol`.
    norm : float, optional
        Order to use for the norm of the gradient
        (``-np.Inf`` is min, ``np.Inf`` is max).
    epsilon : float or ndarray, optional
        Step size(s) to use when `fprime` is approximated numerically. Can be a
        scalar or a 1-D array.  Defaults to ``sqrt(eps)``, with eps the
        floating point machine precision.  Usually ``sqrt(eps)`` is about
        1.5e-8.
    maxiter : int, optional
        Maximum number of iterations to perform. Default is ``200 * len(x0)``.
    full_output : bool, optional
        If True, return `fopt`, `func_calls`, `grad_calls`, and `warnflag` in
        addition to `xopt`.  See the Returns section below for additional
        information on optional return values.
    disp : bool, optional
        If True, return a convergence message, followed by `xopt`.
    retall : bool, optional
        If True, add to the returned values the results of each iteration.
    callback : callable, optional
        An optional user-supplied function, called after each iteration.
        Called as ``callback(xk)``, where ``xk`` is the current value of `x0`.

    Returns
    -------
    xopt : ndarray
        Parameters which minimize f, i.e. ``f(xopt) == fopt``.
    fopt : float, optional
        Minimum value found, f(xopt).  Only returned if `full_output` is True.
    func_calls : int, optional
        The number of function_calls made.  Only returned if `full_output`
        is True.
    grad_calls : int, optional
        The number of gradient calls made. Only returned if `full_output` is
        True.
    warnflag : int, optional
        Integer value with warning status, only returned if `full_output` is
        True.

        0 : Success.

        1 : The maximum number of iterations was exceeded.

        2 : Gradient and/or function calls were not changing.  May indicate
            that precision was lost, i.e., the routine did not converge.

    allvecs : list of ndarray, optional
        List of arrays, containing the results at each iteration.
        Only returned if `retall` is True.

    References
    ----------
    .. [1] Jonathan Richard Shewchuk, "An Introduction to the Conjugate Gradient Method Without the Agonizing Pain", 1994.
    """
    
if __name__ == '__main__' :
    def f(w) :
        x, y = w
        return (#(x-1)**2 + (y-2)**2
            (1-x)**2 + 100 * (y - x*x)**2
        )
    nonlinear_cg(f, (0,0), callback=print)
