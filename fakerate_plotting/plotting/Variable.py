"""@package Variable
Helper classes to store variables and related quantities

@author Christian Grefe, Bonn University (christian.grefe@cern.ch)
"""

from plotting.Cut import Cut
from array import array
import uuid, logging, hashlib
from plotting.Tools import blindHistogram

# dictionary of all registered variables, allows look-up by name
VARIABLES = {}

def addParantheses( s, checkFor ):
    ## helper method to check if any of the given characters is present
    #  @param s            the string to check
    #  @param checkFor     list of strings to check for
    #  @return the string surrounded by parantheses if true, otherwise leave it unchanged 
    if any(x in s for x in checkFor):
        return '(%s)' % s
    else:
        return s

class Interval( object ):
    ## Container for lower and upper limits
    
    def __init__( self, low, up ):
        ## Default contructor
        #  @param low       lower limit
        #  @param up        upper limit
        self.low = low
        self.up = up
    
    def applyToAxis( self, axis ):
        ## Apply the interval range to the given axis
        #  @param axis     axis which has attributes updated
        pass
        
    def __repr__( self ):
        return 'Interval(low=%r, up=%r)' % ( self.low, self.up )
    
    def __eq__( self, other ):
        return isinstance( other, Interval ) and self.low == other.low and self.up == other.up

    def __hash__( self ):
        return hash( ( self.low, self.up ) )
    
    @property
    def md5( self ):
        md5 = hashlib.md5()
        md5.update( str(self.low) )
        md5.update( str(self.up) )
        return md5.hexdigest()

class Binning( Interval ):
    ## Container for a binning with lower and upper limits
    logger = logging.getLogger( __name__ + '.Binning' )
    
    def __init__( self, nBins=40, low=None, up=None, binLabels=None ):
        ## Default contructor
        #  @param nBins      number of bins
        #  @param low        lower edge of the lowest bin
        #  @param up         upper edge of the highest bin
        #  @param binLabels  the list of labels for the bins, should match the number of bins
        Interval.__init__( self, low, up )
        self.nBins = nBins
        if binLabels and len(binLabels) != nBins:
            self.logger.warning( 'Number of bin labels (%s) does not match number of bins (%d)' % (binLabels, nBins) )
        self.binLabels = binLabels
        self.drawUnderflowBin = False
        self.drawOverflowBin = False
        self.nDivisions = 510
    
    def setupAxis( self, axis ):
        ## Set the binning of the given axis
        #  @param axis     axis which has attributes updated
        low = self.low if self.low is not None else 0.
        up = self.up if self.up is not None else 0.
        axis.Set( self.nBins, low, up )
    
    def applyToAxis( self, axis ):
        ## Apply attributes to the given axis
        #  @param axis     axis which has attributes updated
        Interval.applyToAxis( self, axis )
        axis.SetNdivisions( self.nDivisions )
        if axis and self.binLabels:
            index = 1
            for label in self.binLabels:
                axis.SetBinLabel( index, str(label) )
                index += 1
    
    def __repr__( self ):
        return 'Binning(nBins=%r, low=%r, up=%r)' % ( self.nBins, self.low, self.up )
    
    def __eq__( self, other ):
        return isinstance( other, Binning ) and self.nBins == other.nBins and Interval.__eq__( self, other )
    
    def __hash__( self ):
        return hash( ( self.nBins, Interval.__hash__( self ) ) )
    
    @property
    def md5( self ):
        md5 = hashlib.md5()
        md5.update( str(self.nBins) )
        md5.update( str(self.low) )
        md5.update( str(self.up) )
        return md5.hexdigest()
    
    @property
    def bins( self ):
        ## Get the array of bin boundaries
        import numpy
        return numpy.linspace( self.low, self.up , self.nBins+1 )
    
class VariableBinning( Binning ):
    ## Container for variable binning
    logger = logging.getLogger( __name__ + '.VariableBinning' )
    
    def __init__( self, bins=[], binLabels=[] ):
        ## Default contructor
        #  @param bins       numbers defining the bin boundaries, nBins = lenght-1
        #  @param binLabels  the list of labels for the bins, should match the number of bins
        Binning.__init__( self )
        self.bins = bins
        self.binLabels = binLabels
    
    def setupAxis( self, axis ):
        ## Set the binning of the given axis
        #  @param axis     axis which has attributes updated
        axis.Set( self.nBins, self.bins )
    
    def applyToAxis( self, axis ):
        ## Apply attributes to the given axis
        #  @param axis     axis which has attributes updated
        Binning.applyToAxis( self, axis )
    
    def __repr__( self ):
        return 'VariableBinning(nBins=%r, low=%r, up=%r)' % ( self.nBins, self.low, self.up )
    
    def __eq__( self, other ):
        return isinstance( other, VariableBinning ) and set( self.bins ) == set( other.bins )
    
    def __hash__( self ):
        return hash( tuple( self.bins ) )
    
    @property
    def md5( self ):
        return hashlib.md5( str( tuple( self.bins ) ) ).hexdigest()
    
    @property
    def bins( self ):
        ## Get the array of bin boundaries
        return self.__bins
    
    @bins.setter
    def bins( self, bins ):
        ## Set the array of bin boundaries
        if not bins:
            self.logger.error( 'Trying to set an empty list of bins' )
            return
        bins.sort()
        self.__bins = array( 'd', bins )
        self.nBins = len(self.__bins)-1
        self.low = self.__bins[0]
        self.up = self.__bins[-1]
    
        
class Variable( object ):
    ## Container for attributes of a variable
    logger = logging.getLogger( __name__ + '.Variable' )
    
    def __init__( self, name, command=None, title=None, unit='', binning=Binning(), defaultCut=Cut() ):
        ## Default contructor
        #  @param name        the name, also used for draw command and title if not specified
        #  @param command     command used in TTree::Draw (default uses name)
        #  @param title       title used for example in axis lables (default uses name)
        #  @param unit        name of the unit
        #  @param binning     binning object
        #  @param defaultCut  cut that should be applied whenever this variable is plotted
        self.name = name
        self.command = command if command is not None else name
        self.title = title if title is not None else name
        self.unit = unit
        self.binning = binning
        self.defaultCut = defaultCut
        self.matchedVariable = None
        self.periodicity = None
        self.isBlinded = True
        self._blindingScheme = {}
    
    @classmethod
    def fromXML( cls, element ):
        ## Constructor from an XML element
        #  <Variable name="VariableName" command="DrawCommand" title="AxisTitle" unit="Unit" nBins="nBins" low="min" up="max">
        #    <Cut>DefaultCut</Cut>
        #  </Variable>
        #  @param element    the XML element
        #  @return the Variable object
        attributes = element.attrib
        name = attributes[ 'name' ]
        variable = cls( name )
        if attributes.has_key( 'command' ):
            variable.treeName = attributes['command']
        if attributes.has_key( 'title' ):
            variable.title = attributes['title']
        if attributes.has_key( 'unit' ):
            variable.unit = attributes['unit']
        if attributes.has_key( 'nBins' ):
            variable.binning.nBins = int(attributes['nBins'])
        if attributes.has_key( 'low' ):
            variable.binning.low = float(attributes['low'])
        if attributes.has_key( 'up' ):
            variable.binning.up = float(attributes['up'])
        for cutElement in element.findall( 'Cut' ):
            variable.defaultCut += Cut.fromXML( cutElement )
        return variable
    
    def __repr__( self ):
        return 'Variable(%r)' % (self.name )
    
    def __str__( self ):
        result = self.name
        if not self.name == self.command:
            result += ' (%s)' % self.command
        return result + ': %s, %s' % (self.axisLabel, self.binning)
    
    def __eq__( self, other ):
        return isinstance( other, Variable ) and self.command == other.command and self.binning == other.binning and self.defaultCut == other.defaultCut
    
    def __hash__( self ):
        return hash( ( self.command, hash( self.binning ), hash( self.defaultCut ) ) )
    
    @property
    def md5( self ):
        md5 = hashlib.md5()
        md5.update( self.command )
        md5.update( str( self.binning.md5 ) )
        md5.update( self.defaultCut.cut )
        return md5.hexdigest()
    
    @property
    def name( self ):
        ## Get the name of the variable
        return self.__name
    
    @name.setter
    def name( self, name ):
        ## Set the name of bin variable
        # remove the old reference
        if hasattr( self, '__name' ) and VARIABLES.has_key( self.__name ):
            del VARIABLES[self.__name]
        self.__name = name
        # register variable
        if not VARIABLES.has_key( self.__name ):
            VARIABLES[self.__name] = self
    
    @property
    def deltaVar( self ):
        ## Get the variable corresponding to "self - matched", if the matchedVariable is available
        #  @return the deltaVar
        if not self.matchedVariable:
            self.logger.error( 'deltaVar(): no matched variable available for %r' % self )
            return
        deltaVar = self - self.matchedVariable
        deltaVar.name = 'delta_' + self.name
        return deltaVar
    
    @property
    def deltaRelativeVar( self ):
        ## Get the variable corresponding to "(this - matched) / matched", if the matchedVariable is available
        #  @return the deltaVar
        if not self.matchedVariable:
            self.logger.error( 'deltaRelativeVar(): no matched variable available for %r' % self )
            return
        deltaVar = (self - self.matchedVariable) / self.matchedVariable
        deltaVar.name = 'delta-relative_' + self.name
        return deltaVar
    
    @property
    def rooFitVar( self ):
        ## Get the corresponding RooRealVar used in RooFit
        #  @return the RooRealVar
        if not self.__rooFitVar:
            from ROOT import RooRealVar
            self.__rooFitVar = RooRealVar( self.name, self.title, self.low, self.up, self.unit )
            self.__rooFitVar.setBins( self.nBins )
        return self.__rooFitVar
    
    @property
    def axisLabel( self ):
        ## Get the full axis label including unit
        #  @return title with unit
        label = self.title
        if self.unit:
            label += ' [%s]' % self.unit
        return label
    
    def applyToAxis( self, axis ):
        ## Apply attributes to the given axis
        #  @param axis     axis which has attributes updated
        self.binning.applyToAxis( axis )
        axis.SetTitle( self.axisLabel )
        
    def blindRegion( self, cut, low, high ):
        ## Adds a blinded region for this variable defined by a cut, a minimum and a maximum
        #  @param cut      cut defining the region in which the blinding is applied
        #  @param low      lower edge of the blinded region
        #  @param high     upper edge of the blinded region
        self._blindingScheme[ cut ] = ( low, high )
        
    def applyBlinding( self, cut, histogram ):
        ## Applies the blinding scheme defined for this variable to the given histogram
        #  Only modifies the histogram if isBlinded is set to True
        #  This can not be done automatically in createHistogram since it should only apply to data
        #  @param cut          cut defining the region contained in the histogram
        #  @param histogram    TH1 object to be blinded
        #  @return the blinded histogram
        if self.isBlinded and self._blindingScheme.has_key( cut ):
            low, high = self._blindingScheme[ cut ]
            histogram = blindHistogram( histogram, low, high )
        return histogram
        
    def createHistogram( self, title=None, profile=False ):
        ## Create an empty histogram for this variable with the given title
        #  @param title      the title of the new histogram
        #  @param profile    set if the histogram should be a TProfile instead
        #  @return the new histogram 
        title = title if title is not None else self.title
        name = 'h%s_%s' % ( self.name.replace(' ', '').replace('(', '').replace(')',''), uuid.uuid1() )
        from ROOT import TH1D, TProfile
        if profile:
            h = TProfile( name, title, self.binning.nBins, 0., 1. )
        else:
            h = TH1D( name, title, self.binning.nBins, 0., 1. )
        self.binning.setupAxis( h.GetXaxis() )
        self.applyToAxis( h.GetXaxis() )
        return h
    
    def createHistogramFromTree( self, tree, title='', cut=None, weight=None, drawOption='', style=None ):
        ## Create a histogram of this variable from a TTree
        #  @ param tree             TTree object used to create the histogram
        #  @ param title            the histogram title
        #  @ param cut              Cut object (optional)
        #  @ param weight           weight expression (optional)
        #  @ param drawOption       draw option used
        #  @ return the generated histogram
        cut = cut if cut else Cut()
        cut += self.defaultCut
        if weight:
            cut *= weight
        opt = drawOption + 'goff'
        # create an empty histogram
        h = self.createHistogram( title, 'prof' in drawOption )
        # no range set, need to determine from values
        if self.binning.low is None or self.binning.up is None:
            self.logger.debug( 'createHistogramFromTree(): missing range from binning - determining range automatically.' )
            tree.Draw( '%s >> temp(%d)' % ( self.command, 1000 ), cut.cut, opt )
            hTemp = tree.GetHistogram()
            if hTemp:
                low = max(hTemp.GetXaxis().GetXmin(), hTemp.GetMean()-3*hTemp.GetStdDev()) if self.binning.low is None else self.binning.low
                up = min(hTemp.GetXaxis().GetXmax(), hTemp.GetMean()+3*hTemp.GetStdDev()) if self.binning.up is None else self.binning.up
                # reset axis with the new limits
                h.GetXaxis().Set( self.binning.nBins, low, up )
            else:
                self.logger.error( 'createHistogramFromTree(): no histogram created from TTree::Draw( "%s", "%s" )' % (self.command, cut.cut) )
        self.logger.debug( 'createHistogramFromTree(): calling TTree::Draw( "%s", "%s", "%s" )' % (self.command, cut.cut, drawOption) )
        tree.Draw( '%s >> %s' % (self.command, h.GetName()), cut.cut, opt )
        if not h.GetSumw2N():
            h.Sumw2()
        if h:
            self.logger.debug( 'createHistogramFromTree(): created histogram with %d entries and an integral of %g' % (h.GetEntries(), h.Integral()) )
        else:
            self.logger.error( 'createHistogramFromTree(): no histogram created from TTree::Draw( "%s", "%s" )' % (self.command, cut.cut) )
        if h and style:
            style.apply( h )
        return h
    
    ##################################
    #### Operator implementations ####
    ##################################
    
    def __neg__( self ):
        ## implement -self operator
        command = '-' + addParantheses( self.command, '+-' )
        title = '-' +  addParantheses( self.title, '+-' )
        return Variable( 'inv_'+self.name, command, title, self.unit, self.binning, self.defaultCut )
    
    def __add__( self, other ):
        ## implement + operator
        command = '%s+%s' % (addParantheses( self.command, '*/' ), addParantheses( other.command, '*/' ) )
        title = '%s + %s' % (addParantheses( self.title, '*/' ), addParantheses( other.title, '*/' ) )
        if self.unit is not other.unit:
            self.logger.warning( '__add__(): combining variables %r and %r with different units.' % (self, other) )
        return Variable( '%s_PLUS_%s' % (self.name, other.name), command, title, self.unit, self.binning, self.defaultCut+other.defaultCut )
    
    def __sub__( self, other ):
        ## implement - operator
        command = '%s-%s' % (addParantheses( self.command, '*/' ), addParantheses( other.command, '*/' ) )
        title = '%s - %s' % (addParantheses( self.title, '*/' ), addParantheses( other.title, '*/' ) )
        if self.unit is not other.unit:
            self.logger.warning( '__add__(): combining variables %r and %r with different units.' % (self, other) )
        return Variable( '%s_MINUS_%s' % (self.name, other.name), command, title, self.unit, self.binning, self.defaultCut+other.defaultCut )
    
    def __mul__( self, other ):
        ## implement * operator:
        command = '%s*%s' % (addParantheses( self.command, '+-' ), addParantheses( other.command, '+-' ) )
        title = '%s * %s' % (addParantheses( self.title, '+-' ), addParantheses( other.title, '+-' ) )
        if self.unit == other.unit:
            unit = self.unit + '^{2}'
        else:
            unit = self.unit+other.unit
        return Variable( '%s_TIMES_%s' % (self.name, other.name), command, title, unit, self.binning, self.defaultCut+other.defaultCut )
    
    def __div__( self, other ):
        ## implement / operator:
        command = '%s/%s' % (addParantheses( self.command, '+-' ), addParantheses( other.command, '+-' ) )
        title = '%s / %s' % (addParantheses( self.title, '+-' ), addParantheses( other.title, '+-' ) )
        if self.unit == other.unit:
            unit = ''
        else:
            unit = self.unit+other.unit+'^{-1}'
        return Variable( '%s_DIV_%s' % (self.name, other.name), command, title, unit, self.binning, self.defaultCut+other.defaultCut )


def createCutFlowVariable( name='cutflow', cuts=[] ):
    ## Helper method to create a cutflow variable from a list of cuts
    #  @param name    name of the variable
    #  @param cuts    the list of cuts that define the x-axis
    #  @return the variable 
    binLables = []
    for cut in cuts:
        binLables.append( cut.title )
    binning = Binning( len(cuts), 0, len(cuts) )
    binning.binLabels = binLables
    return Variable( name, '', '', '', binning )


# some standard variable definitions for axis labels, lower limit 0, upper limit free
var_AU         = Variable( 'A.U.', binning=Binning(40, low=0) )
var_Events     = Variable( 'Events', binning=Binning(40, low=0.5) )
var_Entries    = Variable( 'Entries', binning=Binning(40, low=0.5) )
var_Normalized = Variable( 'Normalized Entries', binning=Binning(40, low=0) )
var_Yield      = Variable( 'yield', '0', '', '', Binning(1, 0, 1, ['']) )

if __name__ == '__main__':
    # define an interval
    testInterval = Interval( -10., 15. )
    print testInterval
    
    # define a binning
    testBinning = Binning( 25, 0, 25. )
    print testBinning
    print testBinning.bins
    
    # define a binning with custom bin labels
    testBinningWithLabels = Binning( 5, 0, 5, ['1p0n', '1p1n', '1pXn', '3p0n', '3pXn'] )
    print testBinningWithLabels
    
    # define a binning with variable bin widths
    testVariableBinning = VariableBinning( [0,0.3,1,3,4,7] )
    print testVariableBinning
    
    # define some variables
    tauEnergy = Variable( 'tau_energy', 'tau_energy', 'E(#tau)', 'GeV', testBinning )
    tauPt     = Variable( 'tau_pt', 'tau_pt', 'p_{T}(#tau)', 'GeV', testBinning )
    print tauEnergy
    print tauPt
    
    # combine variables, note the treatment of the unit
    print tauEnergy - tauPt
    print tauEnergy * tauPt
    print tauEnergy / tauPt
    
    # define a matched variable and get standard resolution observables
    tauPt.matchedVariable = Variable( 'tau_matched_pt', 'tau_matched_pt', 'p^{true}_{T}(#tau)', 'GeV', testBinning )
    print tauPt.deltaVar
    print tauPt.deltaRelativeVar
    
    # example plot
    from BasicPlot import BasicPlot
    # create an empty histogram from the variable object
    h = tauEnergy.createHistogram()
    import ROOT
    r = ROOT.TRandom3()
    for x in xrange(10000):
        h.Fill( r.Gaus( 2, 5 ) )
    p = BasicPlot( 'testVariableBinning' )
    p.addHistogram( h )
    p.draw()
    
    raw_input( 'Continue?' )
