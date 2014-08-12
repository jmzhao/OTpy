# -*- coding: utf-8 -*-
class constraint :
    def __init__(self, index, abbr, describe) :
        self.index = index
        self.abbr = abbr
        self.describe = describe
class data :
    def __init__(self, underlying) :
        self.underlying = underlying
        self.candidates = dict()
        self._winners = dict()
        self._winner = None
    @property
    def winner(self) :
        return self._winner
    @winner.setter
    def winner(self, value) :
        self._winner = value
        self.winners = {value:1}
    @property
    def winners(self) :
        return self._winners
    @winners.setter
    def winners(self, value) :
        self._winners = value
        self._winner = tuple(value)[0]
    def toHTML(self, rank) :
        ''' @rank is a list of (constraint, rank) pair'''
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
            winner_vio_dict = self.candidates[self.winner]
            distinguished = None
            def check_cand(vio_dict, ind) :
                global distinguished
                if distinguished :
                    return '<td class="grey">%s</td>'
                if vio_dict.get(ind, 0) > winner_vio_dict.get(ind, 0) :
                    distinguished = True
                    return '<td class="grey">!%s</td>'
                return '<td>%s</td>'
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
                        if cand==self.winner else '') 
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
    
        
def subtract(vio_dict1, vio_dict2) :
    ''' get the index of constraints in $vio_dict1 whose degree of violation is bigger 
    than that in $vio_dict2 '''
    ans = dict()
    for i1, d1 in vio_dict1.items() :
        if i1 not in vio_dict2 :
            ans[i1] = d1
        elif d1 > vio_dict2[i1] :
            ans[i1] = d1 - vio_dict2[i1]
    return ans
    
class InputError(Exception) :
    def __init__(self, *args) :
        Exception.__init__(self, *args)
        
class tableau :
    def __init__(self, fname=None, string=None) :
        self.constraints = list()
        self.datum = list()
        #TODO: copier, fromFile, etc.
        if fname :
            self.readFile(fname)
        elif string :
            self.readString(string)
    def get_constraint(self, index) :
        for c in self.constraints :
            if c.index == index :
                return c
    def get_constraint_indices(self) :
        return [c.index for c in self.constraints]
    def readFile(self, fname) :
        ''' construct from plain text file (.txt)'''
        f = open(fname) ## may fail and raise IOError
        self.readLines(f)
    def readString(self, s) :
        ''' construct from plain string '''
        self.readLines(s.split('\n'))
    def readLines(self, s) :
        ''' construct from list of text lines '''
        mat = [line.strip('\r\n').split('\t') for line in s if line.strip() != '']
        self.readMat(mat)
    def readMat(self, mat) :
        ''' construct from table with string elements '''
        ## extract constraint info
        self.constraints = [constraint(index=i, abbr=a, describe=d) 
            for i, (d, a) in enumerate(zip(mat[0][3:], mat[1][3:]))]
        
        ## extract data
        self.datum = list()
        def addToDatum(onedata) :
            ''' put information for one input into the structure '''
            if onedata != None : ## indeed has extracted data
                onedata.winners = onedata.winners ## this is a bit odd, see getter and setter
                if onedata.winner == None : ## has no winner candidate
                    raise InputError('no winner form for underlying form "%s"'%(onedata.underlying) )
                else :
                    winner_vio_dict = onedata.candidates[onedata.winner]
                    for can, vio_dict in onedata.candidates.items() :
                        if ( can != onedata.winner
                        and len(subtract(vio_dict, winner_vio_dict)) == 0 ) :
                            raise InputError('winner candidate "%(win)s is" harmonically bounded by "%(can)s" with underlying form "%(und)s"'
                            %{'win':onedata.winner, 'can':can, 'und':onedata.underlying})
                self.datum.append(onedata)
        onedata = None ## store the data for current underlying form
        for line in mat[2:] : ## data start from 3rd row
            ## underlying form
            underlying = line[0].strip() ## extract underlying form
            if underlying != '' : ## the start of a new group of data
                addToDatum(onedata)
                onedata = data(underlying)
            if line[1].strip() == '' : ## empty candidate
                raise InputError('empty candidates form when reading underlying form "%s"'%(onedata.underlying))
            ## extract information of a candidate
            onedata.candidates[line[1]] = dict((constraint_index, int(degree))
                for constraint_index, degree in enumerate(line[3:]) if degree != '')
            ## winner candidate
            if line[2].strip() != '' : ## if this is a winner
                '''
                if onedata.winner != None : ## already has a winner
                    ## more than one candidate for single underlying form, which is not allowed for now
                    raise InputError('more than one winner when reading underlying form %s'%(onedata.underlying))
                onedata.winner = line[1]
                '''
                onedata.winners.update({line[1]:float(line[2])})
        addToDatum(onedata) ## don't forget to save the last group of data
    def toMat(self) :
        mat = list()
        ind = self.get_constraint_indices()
        ## make the head 
        mat.append(['']*3 + [self.get_constraint(index=i).describe for i in ind])
        mat.append(['']*3 + [self.get_constraint(index=i).abbr for i in ind])
        ## make the body
        for d in self.datum :
            onemat = [ ['', can, ''] + [str(vio_dict.get(i, '')) for i in ind]
                for can, vio_dict in d.candidates.items()]
            onemat[0][0] = d.underlying
            for i in range(len(onemat)) :
                if onemat[i][1] == d.winner :
                    onemat[i][2] = '1'
                    break
            mat.extend(onemat)
        return mat
    def toString(self) :
        return '\n'.join('\t'.join(row) for row in self.toMat())
    def toHTML(self, rank) :
        return '''<link rel="stylesheet" type="text/css" href="tableau.css" />
        '''+'<br>\n'.join(d.toHTML(rank) for d in self.datum)
        