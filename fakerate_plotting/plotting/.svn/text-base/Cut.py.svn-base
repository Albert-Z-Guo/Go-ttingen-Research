"""@package Cut
Class to replace TCut with extended functionality

@author Christian Grefe, Bonn University (christian.grefe@cern.ch)
"""
import hashlib

CUTS={}

def findAllOccurrences( expression, char ):
    ## finds all occurances of a given char in the given expression
    return [i for i, ltr in enumerate( expression ) if ltr == char]

def findMatchingParantheses( expression ):
    ## returns a list of tuples with the inidces of the corresponding
    #  open and close parantheses positions.
    result = []
    openParentheses = findAllOccurrences( expression, '(' )
    for i in openParentheses:
        index = i
        counter = 1
        while counter > 0:
            index += 1
            if expression[index] == '(':
                counter += 1
            elif expression[index] == ')':
                counter -= 1
        result.append( (i, index) )
    return result

def removeRedundantParantheses( expression ):
    ## removes all unnecessary parantheses from the given expression
    indicesToRemove = []
    previousParantheses = None
    for parantheses in findMatchingParantheses( expression ):
        # check if the parantheses are just first and last character
        if parantheses[0] == 0 and parantheses[1]+1 == len( expression ):
            indicesToRemove.extend( parantheses )
        # check if the parantheses are nested directly in another set of parantheses
        elif previousParantheses and parantheses[0] == previousParantheses[0]+1 and parantheses[1] == previousParantheses[1]-1:
            indicesToRemove.extend( parantheses )
        previousParantheses = parantheses
    
    # start with highest character and remove indices
    indicesToRemove.sort( reverse=True )
    for index in indicesToRemove:
        expression = expression[:index] + expression[index+1:]
    return expression

class Cut( object ):
    ## Container class for named cuts including titles
    #  Provides intuitive implementation for logical combination of cuts.
    #  Supports implicit conversion from plain strings and TCut objects.
    stringNOT   = 'NOT '
    stringAND   = ' AND '
    stringOR    = ' OR '
    stringTIMES = ' X '
    
    def __init__( self, name='', title=None, cut=None ):
        ## Default constructor
        #  If title and/or cut are empty the name is used respectively
        #  @param name    name of the cut (used for file names etc.: avoid special characters)
        #  @param title   title of the cut (used for legend titles etc.: use TLatex)
        #  @param cut     the actual cut string (see TTree::Draw)
        from ROOT import TCut
        if isinstance( name, TCut ):
            self.name = name.GetName()
            self.title = name.GetName()
            self.cut = name.GetTitle()
        else:
            if name is None:
                name = ''
            elif not isinstance(name, basestring):
                name = str(name)
            self.name = name
            self.title = title if title is not None else name
            self.cut = cut if cut is not None else name
        # register with all cuts
        CUTS[self.name] = self
    
    @classmethod
    def fromTCut( cls, cut ):
        ## Constructor from a ROOT::TCut
        #  The name of the TCut object is used both for name and title.
        #  The title of the TCut object is used as the cut string.
        #  @return the Cut object
        title = cut.GetName()
        return cls( title, title, cut.GetTitle() )
    
    @classmethod
    def fromXML( cls, element ):
        ## Constructor from an XML element
        #  <Cut name="CutName" title=CutTitle> CutString </Cut>
        #  @param element    the XML element
        #  @return the Cut object
        cut = element.text.strip() if element.text else ''
        name = element.attrib['name'] if element.attrib.has_key( 'name' ) else cut
        title = element.attrib['title'] if element.attrib.has_key( 'title' ) else ''
        if CUTS.has_key( name ):
            return CUTS[ name ]
        return cls(name, title, cut)
    
    @property
    def cut( self ):
        ## Get the cut expression
        return self.__cut
    
    @cut.setter
    def cut( self, cut ):
        ## Set the cut expression
        # remove white spaces
        self.__cut = removeRedundantParantheses( cut.replace( ' ', '' ) )

    def __repr__( self ):
        ## simple string representation
        return 'Cut(%s)' % self.name
    
    def __str__( self ):
        ## default string representation
        return '%r: cut="%s", title="%s"' % ( self, self.cut, self.title )
    
    def setNameTitle( self, name='', title='' ):
        ## convenience method for changing name and title
        #  @param name    new name of the cut
        #  @param title   new title of the cut
        #  @return the Cut object
        if name:
            self.name = name
        if title:
            self.title = title
        return self
        
    def getTCut( self ):
        ## Get a corresponding TCut object
        #  @return a corresponding TCut
        from ROOT import TCut
        return TCut( self.title, self.cut )
    
    def getTTreeFormula( self, tree=0 ):
        ## Get a corresponding TTreeFormula object
        from ROOT import TTreeFormula
        import warnings
        warnings.filterwarnings( action='ignore', category=RuntimeWarning, message='creating converter.*' )
        if self.cut:
            return TTreeFormula( self.name, self.cut, tree )
        else:
            return TTreeFormula( self.name, '1', tree )
    
    def withoutCut( self, other ):
        ## Returns this cut without the other cut
        #  @param other    the other cut
        #  @return cut without the other cut
        if not isinstance( other, Cut ):
            other = Cut( other )
        return Cut( '%s_WITHOUT_%s' % (self.name, other.name), '%s WITHOUT %s' % (self.title, other.title), self.cut.replace(other.cut, '1') )
    
    def isSubset( self, other ):
        pass
    
    def isSuperset( self, other ):
        pass


    ##########################################
    #### Operators with implicit renaming ####
    ##########################################

    def NOT( self, name='', title='' ):
        ## logical NOT
        #  @param name    name of the combined cut
        #  @param title   title of the combined cut
        #  @return NOT cut
        return (-self).setNameTitle( name , title )

    def AND( self, other, name='', title='' ):
        ## logical AND
        #  @param cut     the other cut
        #  @param name    name of the combined cut
        #  @param title   title of the combined cut
        #  @return cut AND otherCut
        return (self & other).setNameTitle( name , title )
    
    def OR( self, other, name='', title='' ):
        ## logical OR
        #  @param cut     the other cut
        #  @param name    name of the combined cut
        #  @param title   title of the combined cut
        #  @return cut OR otherCut
        return (self | other).setNameTitle( name , title )
    
    def TIMES( self, other, name='', title='' ):
        ## logical AND (with weights)
        #  @param cut     the other cut
        #  @param name    name of the combined cut
        #  @param title   title of the combined cut
        #  @return cut * otherCut
        return (self*other).setNameTitle( name , title )


    ##################################
    #### Operator implementations ####
    ##################################

    def __eq__( self, other ):
        ## implement == operator
        if not isinstance( other, Cut ):
            other = Cut( other )
        return self.cut == other.cut

    def __hash__( self ):
        ## implement hash function
        return hash( self.cut )
    
    @property
    def md5( self ):
        ## calculate an md5 checksum
        return hashlib.md5( self.cut ).hexdigest()

    def __neg__( self ):
        ## implement -self operator: logical NOT
        if not self.cut:
            return self
        return Cut( 'NOT_%s' % self.name, '%s%s' % (self.stringNOT, self.title), '!(%s)' % self.cut )

    def __and__( self, other ):
        ## implement & operator: logical AND
        if not isinstance( other, Cut ):
            other = Cut( other )
        if not other.cut:
            return self
        if not self.cut:
            return other
        return Cut( '%s_AND_%s' % (self.name, other.name), '%s%s%s' % (self.title, self.stringAND, other.title), '(%s) && (%s)' % (self.cut, other.cut) )
    
    def __or__( self, other ):
        ## implement | operator: logical OR
        if not isinstance( other, Cut ):
            other = Cut( other )
        if not other.cut:
            return self
        if not self.cut:
            return other
        return Cut( '%s_OR_%s' % (self.name, other.name), '%s%s%s' % (self.title, self.stringOR, other.title), '(%s) || (%s)' % (self.cut, other.cut) )
    
    def __mul__( self, other ):
        ## implement * operator: logical AND (with weights)
        if not isinstance( other, Cut ):
            other = Cut( other )
        if not other.cut:
            return self
        if not self.cut:
            return other
        return Cut( '%s_X_%s' % (self.name, other.name), '%s%s%s' % (self.title, self.stringTIMES, other.title), '(%s) * (%s)' % (self.cut, other.cut) )
    
    def __add__( self, other ):
        ## implement + operator: logical AND
        return self & other
    
    def __sub__( self, other ):
        ## implement - operator: logical AND NOT
        return self & -other
    
    
    #########################################
    #### Methods for in-place operations ####
    #########################################
    
    def __iand__( self, other ):
        ## implement cut &= other
        self = self & other
        return self
    
    def __ior__( self, other ):
        ## implement cut |= other
        self = self | other
        return self
    
    def __imul__( self, other ):
        ## implement cut *= other
        self = self * other
        return self
    
    def __iadd__( self, other ):
        ## implement cut += other
        self = self + other
        return self
    
    def __isub__( self, other ):
        ## implement cut -= other
        self = self - other
        return self
    
    
    ###################################
    #### Right-Hand-Side operators ####
    ###################################
    
    def __rand__( self, other ):
        return Cut( other ) & self
    
    def __ror__( self, other ):
        return Cut( other ) | self
    
    def __rmul__( self, other ):
        return Cut( other ) * self
    
    def __radd__( self, other ):
        return Cut( other ) + self
    
    def __rsub__( self, other ):
        return Cut( other ) - self
    
    
if __name__ == '__main__':
    from ROOT import TCut
    c1 = Cut( 'boosted_region', 'Boosted (M_{vis} > 100GeV)', 'ditau_vis_mass > 100.' )
    c2 = Cut( 'rho-rho_decay', '#rho#rho-decay', 'ditau_tau0_decay_mode*ditau_tau1_decay_mode==1' )
    
    print 'Define two cut objects:'
    print '\tc1:\t', c1
    print '\tc2:\t', c2
    print
    print 'Standard logical operations:'
    print '\tNOT c1:\t\t',    -c1
    print '\tc1 AND c2:\t',    c1 & c2
    print '\tc1 OR c2:\t',     c1 | c2
    print '\tc1 TIMES c2:\t',  c1 * c2
    print 
    print 'Logical operations with implicit renaming:'
    print '\tc1 AND c2:\t',      c1.AND( c2, 'signal_region', 'Signal Region' )
    print '\tNOT(c1 AND c2):\t', (c1 & c2).NOT('control_region', 'Control Region')
    print
    print 'Implicit conversion of plain strings and TCut:'
    print '\t"str" AND c1:\t',   '!selection_vbf' + c1
    print '\tc1 OR TCut:\t',     c1 | TCut( 'VBF Region', 'selection_vbf' )
    
    
    print Cut( 'a || b < 70' ) == '(b < 70) || a'
