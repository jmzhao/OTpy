import tableau as tb
import maxent
import math

class Error(Exception) : pass
class UnimplementedError(Error) :
    def __init__(self, m) :
        self.m = m
    def __str__(self) :
        return 'calling unimplemented toHTML() method with "%s"'%(self.m)

class dataMixin :#(tb.data) :
    def toHTML_cd(self, rank) :
        ''' convert to html presentation for the results of Constraint Demotion
        @rank is a list of (constraint, rank) pair'''
        stratum = dict()
        for cons, r in rank :
            stratum.setdefault(r, list()).append(cons)
        s = sorted(stratum.items())
        def head() :
            return ('<tr>'
            '<th class="row-title">' 
            '<table class="input-form">'
            '<td>Input:</td>''<td>/'+self.underlying+'/</td>'
            '</table>'
            '</th>'
            +''.join((''.join('<th>'+cons.abbr+'</th>'
                    for cons in cons_list)
                    + '<th class="stratum-separation"></th>')
                for _, cons_list in s)+
            '</tr>')
        def body() :
            def winner_vio_dict_get(ind, v) :
                return max(self.candidates[winner].get(ind, v) 
                    for winner in self.winners)
            distinguished = None
            def check_cand(vio_dict, ind) :
                global distinguished
                if distinguished :
                    return '<td class="in-stratum grey">%s</td>'
                if vio_dict.get(ind, 0) > winner_vio_dict_get(ind, 0) :
                    distinguished = True
                    return '<td class="in-stratum grey">!%s</td>'
                return '<td class="in-stratum">%s</td>'
            def check_cand_init() :
                global distinguished
                distinguished = False
                return ''
            return '\n'.join('<tr>%s</tr>'%(
            '<td class="row-title">%s</td>'%(
                '<table class="candidates">%s</table>'%(
                    '<td>%s.</td>'%(chr(ord('a')+icand)) 
                    + '<td>%s</td>'%(
                        ('&#9758;'#('Ö'.encode("ascii", errors='replace')).decode("ISO-8859-1")#) 
                        if cand in self.winners else '') 
                        + cand)))
            + check_cand_init()
            + ''.join((
                    ''.join(check_cand(vio_dict, cons.index)%(
                            (lambda x : '*'*x if x < 5 else x)(
                                vio_dict.get(cons.index, 0)))
                            for cons in cons_list)
                    + '<td class="stratum-separation"></td>')
                    for _, cons_list in s))
            for icand, (cand, vio_dict) in enumerate(self.candidates.items()))
                
        return '<table class="tableau">' + head() + body() + '</table>'
    
    def toHTML_maxent(self, w_dict, precision=4) :
        ''' convert to html presentation for the results of Maximum Entropy
        @w_dict is a dict of (constraint, negtive weight)'''
        s = sorted(w_dict.items(), key=lambda x: x[1])
        eps = 10 ** (-precision)
        def neg(x) :
            return -x if abs(x) > eps else 0
        def head() :
            return ('<tr>'
            '<th class="row-title">' 
            '<table class="input-form">'
            '<td>Input:</td>''<td>/%s/</td>'%(self.underlying) +
            '</table>'
            '</th>'
            + ''.join('<th>%s</th>'%(x) for x in ('Harmony','Predicted', 'Observed'))
            + ''.join('<th>%s</th>'%(cons.abbr) for cons, w in s) 
            +
            '</tr>'
            '<tr>'
            + '<td></td>'*4
            + ''.join('<td>%%.%df</td>'%(precision)%(neg(w)) 
                for cons, w in s)
            +
            '</tr>')
        def body() :
            h = tuple( sum(vio_dict.get(cons.index, 0)*nw 
                    for cons, nw in w_dict.items())
                for cand, vio_dict in self.candidates.items())
            z = sum(math.exp(hi) for hi in h)
            ob = tuple(self.winners.get(cand, 0) for cand in self.candidates)
            zob = sum(ob)
            return '\n'.join('<tr>%s</tr>'%(
            '<td class="row-title">%s</td>'%(
                '<table class="candidates">%s</table>'%(
                    '<td>%s.</td>'%(chr(ord('a')+icand)) 
                    + '<td>%s</td>'%(cand)))
            + '<td>%%.%df</td>'%(precision)%(neg(h[icand])) ## Harmony
            + '<td>%%.%df</td>'%(precision)%(math.exp(h[icand])/z) ## Predicted
            + '<td>%%.%df</td>'%(precision)%(ob[icand]/zob) ## Observed
            + ''.join('<td>%s</td>'%((lambda x : '*'*x if x < 5 else x)(
                            vio_dict.get(cons.index, 0)))
                    for cons, w in s))
            for icand, (cand, vio_dict) in enumerate(self.candidates.items()))
        return '<table class="tableau">' + head() + body() + '</table>'
    

class tableauMixin :#(tb.tableau) :
    def toHTML(self, **dic) :
        for m in ('cd', 'maxent') :
            if m in dic :
                ans = dic.pop(m)
                inp = getattr(self, '_prep_'+m)(ans)
                return ('''<h2>Tableax</h2>                
                '''
                +('<p>Log Likelihood: %f</p>'%(
                    maxent.loglikelihood(self)(tuple(ans[i] for i in self.get_constraint_indices()))
                    ) if m == 'maxent' else '')
                +'<br>\n'.join(getattr(d, 'toHTML_'+m)(inp, **dic) 
                    for d in self.datum))
        raise UnimplementedError(dic)
    def _prep_cd(self, cd) :
        return cd
    def _prep_maxent(self, maxent) :
        return dict((self.get_constraint(index=icons), w) 
            for icons, w in maxent.items())