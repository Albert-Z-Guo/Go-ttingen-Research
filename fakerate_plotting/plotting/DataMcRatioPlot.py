from plotting.BasicPlot import BasicPlot, LegendElement
from plotting.DoublePlot import DoublePlot
from plotting.Variable import Binning, Variable, var_Events
from plotting.Tools import histToGraph, combineStatsAndSystematics, addGraphs, divideGraphs, resetGraph,\
    divideHistograms, createOutOfRangeArrows
import uuid
from copy import copy

var_dataMc = Variable( 'Data / Model', binning=Binning(low=0.7, up=1.3) )
var_dataMc.binning.nDivisions = 205

class DataMcRatioPlot( DoublePlot ):
    
    from AtlasStyle import Style
    from ROOT import kRed, kSpring, kGray, TColor
    defaultStatErrorTitle = 'Stat. Uncertainty'
    defaultSystErrorTitle = 'Syst. Uncertainty'
    defaultCombinedErrorTitle = 'Stat #oplus Syst'
    defaultStatErrorStyle = Style( TColor.GetColorTransparent( kSpring, 0.3 ), lineWidth=0, fillStyle=1000, markerStyle=0 )
    defaultSystErrorStyle = Style( kGray+3, lineWidth=0, fillStyle=3354, markerStyle=0 )
    defaultCombinedErrorStyle = Style( kGray+3, lineWidth=0, fillStyle=3354, markerStyle=0 )
    defaultBaseLineStyle = Style( kRed, lineWidth=2, markerStyle=0 )
    
    def __init__( self, title='DataMcPlot', xVariable=None, yVariableUp=var_Events, yVariableDown=var_dataMc, upperFraction=0.7, lowerFraction=0.3 ):
        DoublePlot.__init__( self, title, xVariable, yVariableUp, yVariableDown, upperFraction, lowerFraction )
        from ROOT import TF1
        
        ## settings from default settings 
        self.baseLineStyle = copy( self.defaultBaseLineStyle )
        self.statErrorStyle = copy( self.defaultStatErrorStyle )
        self.systErrorStyle = copy( self.defaultSystErrorStyle )
        self.combinedErrorStyle = copy( self.defaultCombinedErrorStyle )
        self.statErrorTitle = copy( self.defaultStatErrorTitle )
        self.systErrorTitle = copy( self.defaultSystErrorTitle )
        self.combinedErrorTitle = copy( self.defaultCombinedErrorTitle )
        
        self._dataGraph = None
        self._dataMcRatioGraph = None
        self._mcCombinedErrorGraph = None
        self._mcCombinedErrorRatioGraph = None
        self._mcSystGraph = None
        self._mcSystRatioGraph = None
        self._mcSumHist = None
        self._mcSumRatioHist = None
        self._baseLine = TF1( '%s_baseLine' % self.title, '1', xVariable.binning.low, xVariable.binning.up )
        self.plotDown.addFunction( self._baseLine )
        
        # flags to decide which errors bars are shown
        self.drawStatErrorDown = True
        self.drawStatErrorUp = False
        self.drawSystErrorDown = False
        self.drawSystErrorUp = False
        self.drawCombinedErrorUp = True
        self.drawCombinedErrorDown = True
        self.drawOutOfRangeArrows = False
    
    def addHistogram( self, histogram, drawOption='HIST', stacked=True, copy=False ):
        if not self._mcSumHist:
            self._mcSumHist = histogram.Clone( '%s_McSumHist_%s' % ( self.title, uuid.uuid1() ) )
            self._mcSumRatioHist = histogram.Clone( '%s_McSumRatioHist_%s' % ( self.title, uuid.uuid1() ) )
            self.plotUp.addHistogram( self._mcSumHist, 'E2' )
            self.plotDown.addHistogram( self._mcSumRatioHist, 'E2', stacked=False )
            if not self._mcSumHist.GetSumw2N():
                self._mcSumHist.Sumw2()
                self._mcSumRatioHist.Sumw2()
        return self.plotUp.addHistogram( histogram, drawOption, stacked, copy )
    
    def addGraph( self, graph, drawOption='P', copy=False ):
        return self.plotUp.addGraph( graph, drawOption, copy )
    
    def addFunction( self, function, drawOption, legendTitle='', copy=False ):
        return self.plotUp.addFunction( function, drawOption, legendTitle, copy )
    
    def addFitFunction( self, obj, function, drawOption='', fitOption='QN0', xMin=None, xMax=None, legendTitle='', copy=False ):
        return self.plotUp.addFitFunction( obj, function, xMin, xMax, legendTitle, copy )
    
    def setMCSystematicsGraph( self, graph ):
        if not graph:
            return
        self._mcSystGraph = self.addGraph( graph.Clone( '%s_McSystGraph_%s' % ( self.title, uuid.uuid1() ) ), '2' )
        self._mcSystRatioGraph = self.plotDown.addGraph( graph.Clone( '%s_McSystRatioGraph_%s' % ( self.title, uuid.uuid1() ) ), '2' )
        self._mcCombinedErrorGraph = self.addGraph( graph.Clone( '%s_McCombinedErrorGraph_%s' % ( self.title, uuid.uuid1() ) ), '2' )
        self._mcCombinedErrorRatioGraph = self.plotDown.addGraph( graph.Clone( '%s_McCombinedErrorRatioGraph_%s' % ( self.title, uuid.uuid1() ) ), '2' )
        
    def setDataHistogram( self, histogram, copy=False ):
        ## Sets the data histogram
        #  internally this is handled as TGraphAsymmErrors with proper Poisson errors
        if not histogram:
            return
        # convert to TGraphAsymmErrors to store correct Poisson errors
        self._dataGraph = self.plotUp.addGraph( histToGraph( histogram, '%s_DataGraph_%s' % ( self.title, uuid.uuid1() ), poissonErrors=True ), 'P0' )
        self._dataMcRatioGraph = self._dataGraph.Clone( '%s_DataMcRatioGraph_%s' % ( self.title, uuid.uuid1() ) )
        self.plotDown.addGraph( self._dataMcRatioGraph, 'P0' )
            
    def __initAction__( self ):
        DoublePlot.__initAction__( self )
        # remove the histograms / graphs with special roles to add them in correct order
        # note: the stacked histogram order is defined by the order in which they were added
        for obj in [ self._dataGraph, self._mcSumHist, self._mcSystGraph, self._mcCombinedErrorGraph ]:
            if obj in self.plotUp.objects:
                self.plotUp.objects.pop( self.plotUp.objects.index( obj ) )
        for obj in [ self._dataMcRatioGraph, self._mcSumRatioHist, self._mcSystRatioGraph, self._mcCombinedErrorRatioGraph ]: 
            if obj in self.plotDown.objects:
                self.plotDown.objects.pop( self.plotDown.objects.index( obj ) )
        self.baseLineStyle.apply( self._baseLine )
        for obj in [ self._mcSumHist, self._mcSumRatioHist ]:
            if obj: 
                self.statErrorStyle.apply( obj )
                obj.SetTitle( self.statErrorTitle )
        for obj in [ self._mcSystGraph, self._mcSystRatioGraph ]:
            if obj:
                self.systErrorStyle.apply( obj )
                obj.SetTitle( self.systErrorTitle )
        for obj in [ self._mcCombinedErrorGraph, self._mcCombinedErrorRatioGraph ]:
            if obj:
                self.combinedErrorStyle.apply( obj )
                obj.SetTitle( self.combinedErrorTitle )
        if self.drawStatErrorUp and self._mcSumHist:
            self.plotUp.objects.insert( 0, self._mcSumHist )
        if self.drawStatErrorDown and self._mcSumRatioHist:
            self.plotDown.objects.insert( 0, self._mcSumRatioHist )
            self._mcSumRatioHist.Reset()
        if self.drawSystErrorUp and self._mcSystGraph:
            self.plotUp.objects.insert( 0, self._mcSystGraph )
        if self.drawSystErrorDown and self._mcSystRatioGraph:
            self.plotDown.objects.insert( 0, self._mcSystRatioGraph )
            resetGraph( self._mcSystRatioGraph )
        if self.drawCombinedErrorUp and self._mcCombinedErrorGraph:
            self.plotUp.objects.insert( 0, self._mcCombinedErrorGraph )
            resetGraph( self._mcCombinedErrorGraph )
        if self.drawCombinedErrorDown and self._mcCombinedErrorRatioGraph:
            self.plotDown.objects.insert( 0, self._mcCombinedErrorRatioGraph )
            resetGraph( self._mcCombinedErrorRatioGraph )
        if self._mcSumHist:
            self._mcSumHist.Reset()
        if self._dataGraph:
            resetGraph( self._dataMcRatioGraph )
            addGraphs( self._dataMcRatioGraph, self._dataGraph, poissonErrors=True )
            self.plotUp.objects.append( self._dataGraph )
            self.plotDown.objects.append( self._dataMcRatioGraph )
    
    def __mainAction__( self ):
        if self._mcSumHist:
            for hist in self.stackedHistograms:
                self._mcSumHist.Add( hist )
        if self._mcSystGraph and self._mcCombinedErrorGraph:
            addGraphs( self._mcCombinedErrorGraph, self._mcSystGraph )
        if self._mcSumHist and self._mcCombinedErrorGraph:
            combineStatsAndSystematics( self._mcSumHist, self._mcCombinedErrorGraph )

        DoublePlot.__mainAction__( self )
        if self._mcSumHist:
            for hist in self.plotUp.stackedHistograms:
                self._mcSumHist.Add( hist )
            self._mcSumRatioHist.Add( self._mcSumHist )
            divideHistograms( self._mcSumRatioHist, self._mcSumHist )
        if self._mcSystGraph and self._mcCombinedErrorGraph:    
            addGraphs( self._mcCombinedErrorGraph, self._mcSystGraph )
            addGraphs( self._mcSystRatioGraph, self._mcSystGraph )
            divideGraphs( self._mcSystRatioGraph, self._mcSystGraph )
        if self._mcSumHist and self._mcCombinedErrorGraph:
            combineStatsAndSystematics( self._mcSumHist, self._mcCombinedErrorGraph )            
            addGraphs( self._mcCombinedErrorRatioGraph, self._mcCombinedErrorGraph )
            divideGraphs( self._mcCombinedErrorRatioGraph, self._mcCombinedErrorGraph )
        if self._dataMcRatioGraph and self._mcSumHist:
            divideGraphs( self._dataMcRatioGraph, self._mcSumHist )
            if self.drawOutOfRangeArrows:
                for obj in createOutOfRangeArrows( self._dataMcRatioGraph, self.plotDown.yVariable.binning.low, self.plotDown.yVariable.binning.up ):
                    self.plotDown.decoratorObjects.append( obj )

    def __drawDecorations__(self):
        # reverse the order of the legend entries
        self.legendElements.reverse()
        if not self.drawStatErrorUp and self.drawStatErrorDown:
            self.legendElements.append( LegendElement( self._mcSumHist, self.statErrorTitle, 'f' ) )
        if not self.drawSystErrorUp and self.drawSystErrorDown:
            self.legendElements.append( LegendElement( self._mcSystGraph, self.systErrorTitle, 'f' ) )
        if not self.drawCombinedErrorUp and self.drawCombinedErrorDown:
            self.legendElements.append( LegendElement( self._mcCombinedErrorGraph, self.combinedErrorTitle, 'f' ) )
        self.plotDown.canvas.cd()
        DoublePlot.__drawDecorations__( self )
        
                
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
    yVarDown = Variable ( 'Data / Model', binning=Binning(low=0.5, up=1.5) )
    
    # Add the ATLAS label to each plot
    BasicPlot.defaultTitleDecorator = AtlasTitleDecorator( 'work in progress' )
    
    # use the DataMc class to create the double plot with ratio
    # create a +30% -20% systematics for the first background only
    sys = histToGraph( h1, 'hSyst', False )
    for i in xrange( sys.GetN() ):
        from ROOT import Double
        x, y = (Double(), Double())
        sys.GetPoint( i, x, y )
        sys.SetPointEYlow( i, 0.1*y )
        sys.SetPointEYhigh( i, 0.15*y )
    # now add the nominal value for the second background
    addGraphs( sys, histToGraph( h2, '', False ) )
    
    dataMcTest = DataMcRatioPlot( 'testDataMcPlot', xVar )
    dataMcTest.drawOutOfRangeArrows = True
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
    
