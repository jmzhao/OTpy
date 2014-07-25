from tableau import subtract

class Error(Exception) :
    pass
class ProcessError(Error) :
    pass
class UnsatisfiableError(ProcessError) :
    def __init__(self, canstraint_list, *args) :
        super().__init__(*args)
        self.unsatisfiable_canstraint_list = canstraint_list
    def __str__(self) :
        return 'no constraint is undominated among %s'%(
                [c.abbr for c in self.unsatisfiable_canstraint_list])
                
def ConstraintsDemotion(t) :
    ''' input tableau t, output ranking stratum for each constraint'''
    def find_dominated() :
        dominated_set = set()
        for data in t.datum :
            winner_constraint = data.candidates[data.winner]
            for s in data.candidates :
                if s != data.winner :
                    s_constraint = data.candidates[s]
                    dominated_constraint = subtract(winner_constraint, s_constraint)
                    #print(winner_constraint, s_constraint, dominated_constraint)
                    ## assert subtract(s_constraint, winner_constraint) not empty
                    ## this is garanteed if there is no harmonically bounded winner
                    dominated_set.update(dominated_constraint)
        return dominated_set
    def discard(dominated_indices, undominated_indices) :
        t.constraints = [t.get_constraint(index=i) for i in dominated_indices]
        #print(t.get_constraint_indices())
        for d in t.datum :
            winner_vio_dict = d.candidates[d.winner]
            for cand, vio_dict in list(d.candidates.items()) :
                if (cand != d.winner
                and len(set(subtract(vio_dict, winner_vio_dict)).intersection(undominated_indices))) > 0 :
                    ## this candidate can be explained by undominated constraints
                    d.candidates.pop(cand)
            assert len(d.candidates) > 0 ## at least the winner should be left
        ## discard the group that only has the winner candidate
        t.datum = [d for d in t.datum if len(d.candidates) > 1]
                
    ans = list()
    stratum_no = 1
    while len(t.constraints) > 0 :
        #print(t.get_constraint_indices())
        dominated_indices = find_dominated()
        #print(dominated_indices)
        undominated_indices = set(t.get_constraint_indices()).difference(dominated_indices)
        #print(undominated_indices)        
        if not len(undominated_indices) > 0 :
            raise UnsatisfiableError([t.get_constraint(index=i) for i in dominated_indices])
        ans.extend((t.get_constraint(index=i), stratum_no) for i in undominated_indices)
        if len(dominated_indices) == 0 : break        
        stratum_no += 1
        discard(dominated_indices, undominated_indices)
        print(t.toString())
    return ans

def toString(ans) :
    lines = [('Stratum\tAbbreviation')]
    for c, s in ans :
        lines.append('\t'.join((str(s), c.abbr)))
    return '\n'.join(lines)