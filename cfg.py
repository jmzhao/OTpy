import configparser as cp

import cg

cfgtype = {
    'DEFAULT': {
    },
    'HTML': {
        'precision': 'int',
    },
    'GIS': {
        'maxiter': 'int', 
        'needtrim': 'boolean', 
        'lower_lim': 'int', 
        'upper_lim': 'int',
    },
    'SCGIS': {
        'maxiter': 'int', 
        'needtrim': 'boolean', 
        'lower_lim': 'int', 
        'upper_lim': 'int',
    },
    'CG': {
        'prior': 'eval',
        'trim0': 'boolean',
        'epsilon': 'float',
        'tol': 'float',
        'maxiter': 'eval',
        'linear': 'eval',
        'linear_tol': 'float',
        'linear_maxiter': 'int',
        'sigma0': 'float',
    },
}

class MyConfigParser(cp.ConfigParser) :
    def smartget(self, sec, opt, typecode) :
        if typecode == 'eval' :
            return eval(self.get(sec, opt))
        else :
            return getattr(self, 'get'+typecode)(sec, opt)

def get_config_as_dict(fcfg) :
    cfg = MyConfigParser()
    cfg.read(fcfg)
    ans = dict()
    for s in cfg :
        ans[s] = dict((o, cfg.smartget(s, o, cfgtype[s].get(o,''))) for o in cfg[s])
    return ans
