from plotting.BasicPlot import BasicPlot, alphanumericString, TextElement
from plotting.Variable import Binning, Variable, var_Entries, var_Events
from plotting.Tools import histToGraph, combineStatsAndSystematics, addGraphs, divideGraphs, resetGraph,\
    divideHistograms
import uuid
from copy import copy

class DataMcPlot( BasicPlot ):
    
    from AtlasStyle import Style
    from ROOT import kRed, kSpring, kGray, TColor
    defaultStatErrorTitle = 'Stat. Uncertainty'
    defaultSystErrorTitle = 'Syst. Uncertainty'
    defaultCombinedErrorTitle = 'Stat #oplus Syst'
    #defaultStatErrorStyle = mcErrorStyle
    defaultStatErrorStyle = Style( TColor.GetColorTransparent( kSpring, 0.3 ), lineWidth=0, fillStyle=1000, markerStyle=0 )
    defaultSystErrorStyle = Style( kGray+3, lineWidth=0, fillStyle=3354, markerStyle=0 )
    defaultCombinedErrorStyle = Style( kGray+3, lineWidth=0, fillStyle=3354, markerStyle=0 )
    
    def __init__( self, title='DataMcPlot', xVariable=None, yVariable=var_Events ):
        BasicPlot.__init__( self, title, xVariable, yVariable )
        
        ## settings from default settings 
        self.statErrorStyle = copy( self.defaultStatErrorStyle )
        self.systErrorStyle = copy( self.defaultSystErrorStyle )
        self.combinedErrorStyle = copy( self.defaultCombinedErrorStyle )
        self.statErrorTitle = copy( self.defaultStatErrorTitle )
        self.systErrorTitle = copy( self.defaultSystErrorTitle )
        self.combinedErrorTitle = copy( self.defaultCombinedErrorTitle )
        
        self._dataGraph = None
        self._mcCombinedErrorGraph = None
        self._mcSystGraph = None
        self._mcSumHist = None
        
        # flags to decide which errors bars are shown
        self.drawStatError = False
        self.drawSystError = False
        self.drawCombinedError = True
    
    def addHistogram( self, histogram, drawOption='HIST', stacked=True, copy=False ):
        if not self._mcSumHist:
            self._mcSumHist = histogram.Clone( '%s_McSumHist_%s' % ( self.title, uuid.uuid1() ) )
            BasicPlot.addHistogram( self, self._mcSumHist, 'E2' )
            if not self._mcSumHist.GetSumw2N():
                self._mcSumHist.Sumw2()
        return BasicPlot.addHistogram( self, histogram, drawOption, stacked, copy )
    
    def setMCSystematicsGraph( self, graph ):
        if not graph:
            return
        self._mcSystGraph = self.addGraph( graph, '2', True )
        self._mcCombinedErrorGraph = self.addGraph( graph, '2', True )
    
    def setDataHistogram( self, histogram, copy=False ):
        ## Sets the data histogram
        #  internally this is handled as TGraphAsymmErrors with proper Poisson errors
        if not histogram:
            return
        # convert to TGraphAsymmErrors to store correct Poisson errors
        self._dataGraph = BasicPlot.addGraph( self, histToGraph( histogram, '%s_DataGraph_%s' % ( self.title, uuid.uuid1() ), poissonErrors=True ), 'P0' )
            
    def __initAction__( self ):
        BasicPlot.__initAction__( self )
        # remove the histograms / graphs with special roles to add them in correct order
        # note: the stacked histogram order is defined by the order in which they were added
        for obj in [ self._dataGraph, self._mcSumHist, self._mcSystGraph, self._mcCombinedErrorGraph ]:
            if obj in self.objects:
                self.objects.pop( self.objects.index( obj ) )
        if self.drawStatError and self._mcSumHist:
            self.statErrorStyle.apply( self._mcSumHist )
            self._mcSumHist.SetTitle( self.statErrorTitle )
            self.objects.insert( 0, self._mcSumHist )
        if self.drawSystError and self._mcSystGraph:    
            self.systErrorStyle.apply( self._mcSystGraph )
            self._mcSystGraph.SetTitle( self.systErrorTitle )
            self.objects.insert( 0, self._mcSystGraph )
        if self.drawCombinedError and self._mcCombinedErrorGraph:
            self.combinedErrorStyle.apply( self._mcCombinedErrorGraph )
            self._mcCombinedErrorGraph.SetTitle( self.combinedErrorTitle )
            self.objects.insert( 0, self._mcCombinedErrorGraph )
            resetGraph( self._mcCombinedErrorGraph )
        if self._mcSumHist:
            self._mcSumHist.Reset()
        if self._dataGraph:
            self.objects.append( self._dataGraph )
    
    def __mainAction__( self ):
        BasicPlot.__mainAction__( self )
        if self._mcSumHist:
            for hist in self.stackedHistograms:
                self._mcSumHist.Add( hist )
        if self._mcSystGraph and self._mcCombinedErrorGraph:
            addGraphs( self._mcCombinedErrorGraph, self._mcSystGraph )
        if self._mcSumHist and self._mcCombinedErrorGraph:
            combineStatsAndSystematics( self._mcSumHist, self._mcCombinedErrorGraph )

    def __drawDecorations__(self):
        # reverse the order of the legend entries
        self.legendElements.reverse()
        BasicPlot.__drawDecorations__( self )
                
if __name__ == '__main__':
    from ROOT import TH1D, TF1, kBlack, kRed, kBlue, kGreen
    from AtlasStyle import mcErrorStyle, blackLine
    from Variable import Variable
    from PlotDecorator import AtlasTitleDecorator
    
    h1 = TH1D( 'hTest1', 'First Test', 20, -4, 4 )
    h1.FillRandom( 'gaus', 1000 )
    h1.SetLineColor( kRed )
    
    h2 = TH1D( 'hTest2', 'Second Test', 20, -4, 4 )
    h2.FillRandom( 'gaus', 500 )
    h2.SetLineColor( kBlue )   # if no fill color is defined, the line color is used to fill stacked histograms
    
    h3 = TH1D( 'hTest3', 'Data', 20, -4, 4 )
    h3.FillRandom( 'gaus', 1500 )
    h3.SetLineColor( kBlack )
    
    hSum = TH1D( 'hSum', 'Stat', 20, -4, 4 )
    mcErrorStyle.apply( hSum )
    
    hRatio = TH1D( 'hRatio', 'Ratio', 20, -4, 4 )
    hRatio.Sumw2()
    
    xVar = Variable( 'Invariant Mass', unit='GeV', binning=Binning( 20, -4, 4 ) )
    yVarDown = Variable ( 'Ratio', binning=Binning(low=0.5, up=1.5) )
    
    # Add the ATLAS label to each plot
    BasicPlot.defaultTitleDecorator = AtlasTitleDecorator( 'work in progress' )
    
    # use the DataMc class to create the double plot with ratio
    # create a +30% -20% systematics for the first background only
    sys = histToGraph( h1, 'hSyst', False )
    for i in xrange( sys.GetN() ):
        from ROOT import Double
        x, y = (Double(), Double())
        sys.GetPoint( i, x, y )
        sys.SetPointEYlow( i, 0.2*y )
        sys.SetPointEYhigh( i, 0.3*y )
    # now add the nominal value for the second background
    addGraphs( sys, histToGraph( h2, '', False ) )
    
    dataMcTest = DataMcPlot( 'testDataMcPlot', xVar )
    dataMcTest.drawStatError = False
    dataMcTest.drawCombinedError = True
    dataMcTest.addHistogram( h1 )
    dataMcTest.setMCSystematicsGraph( sys )
    dataMcTest.addHistogram( h2, stacked=False )
    dataMcTest.setDataHistogram( h3 )
    dataMcTest.addHistogram( h2, copy=True )
    dataMcTest.draw()
    dataMcTest.saveIn('')
     
    # accessing the sumMC and data histograms from the DataMcPlot ( only after calling draw() )    
    from ROOT import TFile
    f = TFile.Open( 'test.root', 'RECREATE' )
    #blackLine.apply( dataMcTest._mcSumHist ) 
    dataMcTest._mcSumHist.Write( 'SumMC' )
    dataMcTest._dataGraph.Write( 'Data' )
    f.Close()
    
    raw_input( 'Continue?' )
    
