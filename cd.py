#import tableau

def ConstraintsDemotion(t) :
    ''' input tableau t, output ranking stratum for each constraint'''
    def subtract(cons_row1, cons_row2) :
        ans = dict()
        for i1, d1 in cons_row1.items() :
            if i1 not in cons_row2 :
                ans[i1] = d1
            elif d1 > cons_row2[i1] :
                ans[i1] = d1 - cons_row2
        return ans
    def find_loser() :
        loser_set = set()
        for data in t.datum :
            winner_constraint = data.candidates[data.winner]
            for s in data.candidates :
                if s != data.winner :
                    s_constraint = data.candidates[s]
                    loser_constraint = subtract(winner_constraint, s_constraint)
                    #print(winner_constraint, s_constraint, loser_constraint)
                    #: assert subtract(s_constraint, winner_constraint) not empty
                    loser_set.update(loser_constraint)
        return loser_set
    def discard(loser_indices, non_loser_indices) :
        t.constraints = [t.get_constraint(index=i) for i in loser_indices]
        #print(t.get_constraint_indices())
        for d in t.datum :
            for cand, cons in list(d.candidates.items()) :
                if len(set(cons).intersection(non_loser_indices)) > 0 :
                    d.candidates.pop(cand)
            assert len(d.candidates) > 0
        t.datum = [d for d in t.datum if len(d.candidates) == 1] #: only winner left
                
    ans = list()
    stratum_no = 1
    while len(t.constraints) > 0 :
        #print(t.get_constraint_indices())
        loser_indices = find_loser()
        #print(loser_indices)
        non_loser_indices = set(t.get_constraint_indices()).difference(loser_indices)
        #print(non_loser_indices)        
        if not len(non_loser_indices) > 0 :
            raise ValueError('no constraint is never-losing among %s'%(
                [t.get_constraint(index=i).abbr for i in loser_indices]))
        ans.extend((t.get_constraint(index=i), stratum_no) for i in non_loser_indices)
        if len(loser_indices) == 0 : break        
        stratum_no += 1
        discard(loser_indices, non_loser_indices)
    return ans

def toString(ans) :
    lines = [('Stratum\tAbbreviation')]
    for c, s in ans :
        lines.append('\t'.join((str(s), c.abbr)))
    return '\n'.join(lines)