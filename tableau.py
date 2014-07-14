class constraint :
    def __init__(self, index, abbr, describe) :
        self.index = index
        self.abbr = abbr
        self.describe = describe
class data :
    def __init__(self, underlying) :
        self.underlying = underlying
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
        self.readLines(f)
    def readString(self, s) :
        self.readLines(s.split('\n'))
    def readLines(self, s) :
        mat = [line.strip('\r\n').split('\t') for line in s if line.strip() != '']
        self.readMat(mat)
    def readMat(self, mat) :
        #: extract constraint info
        self.constraints = [constraint(index=i, abbr=a, describe=d) 
            for i, (d, a) in enumerate(zip(mat[0][3:], mat[1][3:]))]
        
        #: extract data
        def addToDatum(onedata) :
            if onedata != None :
                if onedata.winner == None :
                    raise ValueError('no winner form for underlying form %s'%(onedata.underlying) )
                self.datum.append(onedata)
        onedata = None
        for line in mat[2:] :
            underlying = line[0].strip()
            if underlying != '' :
                addToDatum(onedata)
                #: new group of data
                onedata = data(underlying)
            if line[1].strip() == '' :
                raise ValueError('empty candidates form when reading underlying form %s'%(onedata.underlying))
            onedata.candidates[line[1]] = dict((constraint_index, int(degree)) 
                for constraint_index, degree in enumerate(line[3:]) if degree != '')
            if line[2].strip() != '' :
                if onedata.winner != None :
                    raise ValueError('more than one winner when reading underlying form %s'%(onedata.underlying))
                onedata.winner = line[1]
        addToDatum(onedata)