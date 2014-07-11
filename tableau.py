class constraint :
    def __init__(self, index, abbr, describe) :
        self.index = index
        self.abbr = abbr
        self.describe = describe
class data :
    def __init__(self, underline) :
        self.underline = underline
        self.candidates = dict()
        self.winner = None
        
class tableau :
    def __init__(self, fname=None) :
        self.constraints = list()
        self.datum = list()
        #TODO: copier, fromFile, etc.
        if fname :
            self.readFile(fname)
        pass
    def get_constraint(self, index) :
        for c in self.constraints :
            if c.index == index :
                return c
    def get_constraint_indices(self) :
        return [c.index for c in self.constraints]
    def readFile(self, fname) :
        ''' support plain text'''
        f = open(fname) ## may fail and raise IOError
        mat = [line.strip('\r\n').split('\t') for line in f if line.strip() != '']
        
        #: extract constraint info
        self.constraints = [constraint(index=i, abbr=a, describe=d) 
            for i, (d, a) in enumerate(zip(mat[0][3:], mat[1][3:]))]
        
        #: extract data
        onedata = None
        for line in mat[2:] :
            underline = line[0].strip()
            if underline != '' :
                #: new group of data
                if onedata != None :
                    if onedata.winner == None :
                        raise ValueError('no winner form for underline form %s'%(onedata.underline) )
                    self.datum.append(onedata)
                onedata = data(underline)
            if line[1].strip() == '' :
                raise ValueError('empty candidates form when reading underline form %s'%(onedata.underline))
            onedata.candidates[line[1]] = dict((constraint_index, int(degree)) 
                for constraint_index, degree in enumerate(line[3:]) if degree != '')
            if line[2].strip() != '' :
                onedata.winner = line[1]
        if onedata != None :
            if onedata.winner == None :
                raise ValueError('no winner form for underline form %s'%(onedata.underline) )
            self.datum.append(onedata)
        onedata = data(underline)