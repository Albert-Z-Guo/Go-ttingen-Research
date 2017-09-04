from plotting.BasicPlot import BasicPlot
from plotting.Variable import Binning, Variable
from plotting.Cut import Cut
import uuid, logging, copy

logger = logging.getLogger( __name__ )
logger = logging.getLogger( 'plotting.TreePlot' )

class CutDefinition:
    ## Container for all parameters to define a histogram based on cuts
    
    def __init__( self, title='', cut=Cut(), weight='', drawOption='', drawLegend=True, style=None, tree=None ):
        ## Default constructor
        #  @param title         title used to define the legend entry
        #  @param cut           Cut object defining the cut
        #  @param weight        the weight expression
        #  @param drawOption    draw option specific to this cut
        #  @param drawLegend    should this histogram be added to the legend?
        #  @param style         the style object associated with this cut
        #  @param tree          the tree associated with this plot
        self.title = title if title else cut.GetName()
        self.cut = cut
        self.weight = weight
        self.drawOption = drawOption
        self.drawLegend = drawLegend
        self.tree = tree
        self.style = style
        
def getValuesFromTree( tree, expression, selection ):
    ## Helper method to get an array of values and weights from a TTree
    #  IMPORTANT: values and weights are associated with the TTree buffer.
    #  They need to be copied in order to be persisted!
    #  @param tree              TTree object used to extract the results
    #  @param expression        string used as variable expression
    #  @param selection         string used as weight and cut expression
    #  @return array of values, array of weights (two return values)
    logger.debug( 'getValuesFromTree(): calling TTree::Draw( "%s", "%s", "%s" )' % (expression, selection, 'goff') )
    tree.Draw( expression, selection, 'goff' )
    entries = tree.GetSelectedRows()
    valueBuffer = tree.GetV1()
    weightBuffer = tree.GetW()
    import numpy
    values = numpy.empty(0)
    weights = numpy.empty(0)
    if entries > 0:
        values = numpy.frombuffer( buffer=valueBuffer, dtype='double', count=entries )
        weights = numpy.frombuffer( buffer=weightBuffer, dtype='double', count=entries )
    return values, weights
            
def createHistogramFromTree( tree, xVar, title='', cut=None, weight=None, drawOption='', style=None ):
    ## Helper method to create a histogram from a TTree and apply a style
    #  @ param tree             TTree object used to create the histogram
    #  @ param xVar             the Variable object defining the xAxis and the draw command
    #  @ param title            the histogram title
    #  @ param cut              Cut object (optional)
    #  @ param weight           weight expression (optional)
    #  @ param drawOption       draw option used
    #  @ param style            Style object which is used
    #  @ return the generated histogram
    myCut = cut
    if not myCut:
        myCut = Cut()
    if xVar.defaultCut:
        myCut = myCut + xVar.defaultCut
    if weight:
        if myCut:
            myCut = weight * myCut
        else:
            myCut = Cut( weight )
    opt = drawOption + 'goff'
    # create an empty histogram
    h = xVar.createHistogram( title, 'prof' in drawOption )
    # no range set, need to determine from values
    if xVar.binning.low is None or xVar.binning.up is None:
        logger.debug( 'createHistogramFromTree(): missing range from binning - determining range automatically.' )
        tree.Draw( '%s >> temp(%d)' % (xVar.command, 1000), myCut.cut, opt )
        hTemp = tree.GetHistogram()
        if hTemp:
            low = max(hTemp.GetXaxis().GetXmin(), hTemp.GetMean()-3*hTemp.GetStdDev()) if xVar.binning.low is None else xVar.binning.low
            up = min(hTemp.GetXaxis().GetXmax(), hTemp.GetMean()+3*hTemp.GetStdDev()) if xVar.binning.up is None else xVar.binning.up
            # reset axis with the new limits
            h.GetXaxis().Set( xVar.binning.nBins, low, up )
        else:
            logger.error( 'createHistogramFromTree(): no histogram created from TTree::Draw( "%s", "%s" )' % (xVar.command, myCut.cut) )
    logger.debug( 'createHistogramFromTree(): calling TTree::Draw( "%s", "%s", "%s" )' % (xVar.command, myCut.cut, drawOption) )
    tree.Draw( '%s >> %s' % (xVar.command, h.GetName()), myCut.cut, opt )
    if not h.GetSumw2N():
        h.Sumw2()
    if style:
        style.apply( h )
    if h:
        logger.debug( 'createHistogramFromTree(): created histogram with %d entries and an integral of %g' % (h.GetEntries(), h.Integral()) )
    else:
        logger.error( 'createHistogramFromTree(): no histogram created from TTree::Draw( "%s", "%s" )' % (xVar.command, myCut.cut) )
    return h

def create2DHistogramFromTree( tree, xVar, yVar, title='', cut=None, weight=None, profile=False ):
    ## Helper method to create a histogram from a TTree and apply a style
    #  @ param tree             TTree object used to create the histogram
    #  @ param xVar             the Variable object defining the xAxis and the draw command
    #  @ param yVar             the Variable object defining the xAxis and the draw command
    #  @ param title            the histogram title
    #  @ param cut              Cut object (optional)
    #  @ param weight           weight expression (optional)
    #  @ param profile          create a profile histogram instead of a 2D histogram
    #  @ return the generated histogram
    from ROOT import TH2D, TProfile
    myCut = cut
    if not myCut:
        myCut = Cut()
    myTitle = title
    if not myTitle:
        myTitle = '%s vs %s' % (yVar.title, xVar.title)
    hName = 'h%s_%s' % ( myTitle.replace(' ', '_').replace('(', '').replace(')',''), uuid.uuid1() )
    myCut += xVar.defaultCut + yVar.defaultCut
    if weight:
        if myCut:
            myCut = weight * myCut
        else:
            myCut = Cut( weight )
    opt = 'goff'
    if profile:
        h = xVar.createHistogram( title, True )
        opt += 'prof'
    else:
        h = TH2D( hName, title, xVar.binning.nBins, xVar.binning.low, xVar.binning.up, yVar.binning.nBins, yVar.binning.low, yVar.binning.up )
        xVar.binning.setupAxis( h.GetXaxis() )
        xVar.applyToAxis( h.GetXaxis() )
        yVar.binning.setupAxis( h.GetYaxis() )
        yVar.applyToAxis( h.GetYaxis() )
    logger.debug( 'create2DHistogramFromTree(): calling TTree::Draw( "%s : %s", "%s" )' % (yVar.command, xVar.command, myCut.cut) )
    tree.Draw( '%s : %s >> %s' % (yVar.command, xVar.command, hName), myCut.cut, opt )
    logger.debug( 'create2DHistogramFromTree(): created histogram with %d entries and an integral of %g' % (h.GetEntries(), h.Integral()) )
    return h

class TreePlot( BasicPlot ):
    ## Class to generate histograms from ROOT trees based on cuts
    
    def __init__( self, title='', xVariable=None, yVariable=None, zVariable=None, tree=None ):
        ## Default constructor
        #  @param title           title of the canvas
        #  @param xVariable       Variable object to define the xAxis and the draw command
        #  @param yVariable       Variable object to define the yAxis
        from AtlasStyle import linesColor
        BasicPlot.__init__( self, title, xVariable, yVariable, zVariable )
        self.cutDefinitions = []
        self.defaultTree = tree
        self.cutStyle = linesColor
    
    def addCut( self, title='', cut=Cut(), weight='', drawOption='', drawLegend=True, style=None, tree=None ):
        ## Adds a new histogram to the list of objects to be drawn
        #  Can be defined via a Cut, a TTree or both
        self.cutDefinitions.append( CutDefinition( title, cut, weight, drawOption, drawLegend, style, tree ) )

    def __initAction__(self):
        ## Method hook to create all desired histograms and add them to the drawn objects
        super( TreePlot, self ).__initAction__()
        from ROOT import TH1D, TProfile
        cutIndex = 0
        for cutDefinition in self.cutDefinitions:
            tree = cutDefinition.tree
            if not tree:
                tree = self.defaultTree
            h = createHistogramFromTree( tree, self.xVariable, cutDefinition.title, cutDefinition.cut, cutDefinition.weight, cutDefinition.drawOption, cutDefinition.style )
            self.addHistogram( h, cutDefinition.drawOption, False )
            if not cutDefinition.style:
                self.cutStyle.apply( h, cutIndex )
            cutIndex += 1

if __name__ == '__main__':
    from ROOT import TTree, TRandom3
    from array import array
    from AtlasStyle import redLine, blueLine, greenLine
    logging.root.setLevel( logging.DEBUG )
    
    # create some dummy tree
    rndm = TRandom3()
    size = array( 'f', [0] )
    energy = array( 'f', [0] )
    t = TTree( 'tree', 'My Tree' )
    t.Branch( 'size', size, 'size/F' )
    t.Branch( 'energy', energy, 'energy/F' )
    for entry in xrange( 10000 ):
        size[0] = rndm.Poisson( 3 )
        energy[0] = rndm.Landau( size[0]*2.5, size[0] )
        t.Fill()
    
    # define a variable object for each branch
    sizeVar = Variable( 'size', title='Cluster Size', binning=Binning(10, 1, 11, range(1,11)) )
    energyVar = Variable( 'energy', title='Hit Energy', unit='MeV', binning=Binning(50, 0, 100) )
    
    # create a plot using the TreePlot class
    treePlotTest = TreePlot( 'TreePlot Test', sizeVar, Variable( 'Entries' ), tree=t )
    treePlotTest.addCut( 'No Cut' )
    treePlotTest.addCut( 'Energy > 15 MeV', 'energy > 15' )
    treePlotTest.draw()

    # create a plot using the BasicPlot class
    testBasicPlot = BasicPlot( 'BasicPlot test', energyVar, Variable( 'Entries' ) )
    testBasicPlot.addHistogram( createHistogramFromTree( t, energyVar, 'Size > 1', Cut( 'size > 1' ), style=redLine ), 'E0' )
    testBasicPlot.addHistogram( createHistogramFromTree( t, energyVar, 'Size > 3', Cut( 'size > 3' ), style=blueLine ), 'E0' )
    testBasicPlot.addHistogram( createHistogramFromTree( t, energyVar, 'Size > 6', Cut( 'size > 6' ), style=greenLine ), 'E0' )
    testBasicPlot.logY = True
    testBasicPlot.draw()
    
    # create correlation plot using the BasicPlot class
    testBasicPlot2D = BasicPlot( 'BasicPlot test 2D', sizeVar, energyVar, Variable( 'Entries' ) )
    testBasicPlot2D.addHistogram( create2DHistogramFromTree( t, sizeVar, energyVar ), 'COLZ' )
    testBasicPlot2D.addHistogram( create2DHistogramFromTree( t, sizeVar, energyVar, profile=True ), 'E0' )
    testBasicPlot2D.logZ = True
    testBasicPlot2D.draw()

    raw_input( 'Continue?' )
