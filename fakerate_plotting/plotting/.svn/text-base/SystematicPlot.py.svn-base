from plotting.BasicPlot import BasicPlot, alphanumericString
from plotting.Variable import Binning, Variable, var_Entries, var_Events
import uuid

class DoublePlot( BasicPlot ):
    
    def __init__( self, title='DoublePlot', xVariable=None, yVariableUp=var_Entries, yVariableDown=None, upperFraction=0.7, lowerFraction=0.3 ):
        BasicPlot.__init__( self, title, xVariable, yVariableUp )
        self.plotUp = BasicPlot( title+'_up', xVariable, yVariableUp )
        self.plotDown = BasicPlot( title+'_down', xVariable, yVariableDown )
        self.plotDown.drawLegend = False
        self.plotDown.showBinWidthY = False
        self.upperFraction = upperFraction
        self.lowerFraction = lowerFraction
        self.legendElements = self.plotUp.legendElements
        self.titles = self.plotUp.titles
        self.plotDown.drawLegend = False
        self.plotDown.drawTitle = False
    
    def __initAction__( self ):
        from ROOT import TCanvas
        ## Method that does all the magic
        if not self.canvas:
            self.canvas = TCanvas( alphanumericString( self.title ), self.title, self.xSize, self.ySize )
        BasicPlot.__initAction__( self )
        self.plotDown.__initAction__()
        self.plotUp.__initAction__()
        
        self.canvas.Divide( 1, 2 )
        self.plotUp.canvas = self.canvas.cd(1)
        self.plotDown.canvas = self.canvas.cd(2)
        self.plotUp.drawLegend = self.drawLegend
        self.plotUp.drawTitle = self.drawTitle
        
        # initialize layout
        self.plotUp.canvas.SetPad( 0., 1.-self.upperFraction, 1., 1. )
        self.plotUp.canvas.SetBottomMargin( 0.03 )
        self.plotUp.canvas.SetTopMargin( self.plotDown.canvas.GetTopMargin() / self.upperFraction )
        self.plotUp.canvas.Update()
        self.plotDown.canvas.SetPad( 0., 0., 1., self.lowerFraction )
        self.plotDown.canvas.SetTopMargin( 0. )
        self.plotDown.canvas.SetBottomMargin( self.plotDown.canvas.GetBottomMargin() / (self.lowerFraction) )
        self.plotDown.canvas.SetGridy( True )
        self.plotDown.canvas.Update()
        self.canvas.Update()
        
        if self.firstTimeDrawn:
            self.plotUp.topMargin = self.topMargin / self.upperFraction
            self.plotUp.bottomMargin = self.bottomMargin / self.bottomMargin
            self.plotUp.legendDecorator.defaultUpperY = 1. - (1 - self.legendDecorator.defaultUpperY) / self.upperFraction
            self.plotUp.legendDecorator.defaultLowerY = self.legendDecorator.defaultLowerY / self.upperFraction
            self.plotUp.legendDecorator.labelTextSize = self.legendDecorator.labelTextSize / self.upperFraction
            self.plotUp.legendDecorator.textSize = self.legendDecorator.textSize / self.upperFraction
            self.plotUp.legendDecorator.lineGap = self.legendDecorator.lineGap / self.upperFraction
            self.plotUp.titleDecorator.defaultUpperY = 1. - (1 - self.titleDecorator.defaultUpperY) / self.upperFraction
            self.plotUp.titleDecorator.defaultLowerY = self.titleDecorator.defaultLowerY / self.upperFraction
            self.plotUp.titleDecorator.textSize = self.titleDecorator.textSize / self.upperFraction
            self.plotUp.titleDecorator.labelTextSize = self.titleDecorator.labelTextSize / self.upperFraction
    
    def __mainAction__(self):
        BasicPlot.__mainAction__(self)
        self.plotDown.__mainAction__()
        self.plotUp.__mainAction__()
    
    def __drawHistograms__(self):
        BasicPlot.__drawHistograms__(self)
        self.plotDown.__drawHistograms__()
        self.plotUp.__drawHistograms__()
    
    def __drawFunctions__(self):
        BasicPlot.__drawFunctions__(self)
        self.plotDown.__drawFunctions__()
        self.plotUp.__drawFunctions__()
    
    def __drawDecorations__(self):
        # No top level decorations
        #BasicPlot.__drawDecorations__(self)
        self.plotDown.__drawDecorations__()
        self.plotUp.__drawDecorations__()
        
    def __drawObjects__(self):
        BasicPlot.__drawObjects__(self)
        self.plotDown.__drawObjects__()
        self.plotUp.__drawObjects__()
    
    def __finalizeAction__( self ):
        self.plotUp.logX = self.logX
        self.plotUp.logY = self.logY
        self.plotUp.logZ = self.logZ
        self.plotDown.__finalizeAction__()
        self.plotUp.__finalizeAction__()
        if self.firstTimeDrawn:
            if self.plotUp.firstDrawnObject:
                xAxis = self.plotUp.firstDrawnObject.GetXaxis()
                xAxis.SetTickLength( xAxis.GetTickLength() / self.upperFraction )
                xAxis.SetLabelOffset( xAxis.GetLabelOffset() * 10. )
                xAxis.Draw()
                yAxis = self.plotUp.firstDrawnObject.GetYaxis()
                yAxis.SetTickLength( yAxis.GetTickLength() / self.upperFraction )
                yAxis.SetLabelSize( yAxis.GetLabelSize() / self.upperFraction )
                yAxis.SetLabelOffset( yAxis.GetLabelOffset() / self.upperFraction )
                yAxis.SetTitleSize( yAxis.GetTitleSize() / self.upperFraction )
                yAxis.SetTitleOffset( yAxis.GetTitleOffset() * self.upperFraction )
                yAxis.Draw()
        if self.plotDown.firstDrawnObject:
                xAxis = self.plotDown.firstDrawnObject.GetXaxis()
                xAxis.SetTickLength( xAxis.GetTickLength() / self.lowerFraction )
                xAxis.SetTitleSize( xAxis.GetTitleSize() / self.lowerFraction )
                xAxis.SetLabelSize( xAxis.GetLabelSize() / self.lowerFraction )
                xAxis.SetLabelOffset( xAxis.GetLabelOffset() / self.lowerFraction )
                xAxis.Draw()
                yAxis = self.plotDown.firstDrawnObject.GetYaxis()
                self.plotDown.firstDrawnObject.SetMinimum(0.9)
                self.plotDown.firstDrawnObject.SetMaximum(1.1)
                yAxis.SetNdivisions( 5 )
                yAxis.CenterTitle( True )
                yAxis.SetTickLength( yAxis.GetTickLength() / self.lowerFraction * 0.5 )
                yAxis.SetLabelSize( yAxis.GetLabelSize() / self.lowerFraction * 0.5 )
                yAxis.SetLabelOffset( yAxis.GetLabelOffset() / self.lowerFraction * 0.5 )
                yAxis.SetTitleSize( yAxis.GetTitleSize() / self.lowerFraction * 0.7 )
                yAxis.SetTitleOffset( yAxis.GetTitleOffset() * self.lowerFraction * 0.8 )
                yAxis.Draw()
        
            #self.stretchAxis( self.plotUp.firstDrawnObject, 1./self.upperFraction, 1.0 )
            #self.stretchAxis( self.plotDown.firstDrawnObject, 1./self.lowerFraction, 0.7 )
        self.plotUp.canvas.Update()
        self.plotDown.canvas.Update()
        self.canvas.Update()
        BasicPlot.__finalizeAction__( self )
        
    def stretchAxis( self, drawnObject, factor, yFactor=1.0 ):
        # get the axis
        xAxis = drawnObject.GetXaxis()
        yAxis = drawnObject.GetYaxis()
      
        for axis in [xAxis, yAxis]:
            axis.SetTickLength( axis.GetTickLength() * factor )
            axis.SetLabelSize( 0.05 * factor )
            axis.SetLabelOffset( axis.GetLabelOffset() * factor )
            if axis == xAxis:
                axis.SetTitleSize( axis.GetTitleSize() * factor )
                # axis.SetLabelOffset( axis.GetLabelOffset() * factor )
                # axis.SetTitleOffset( axis.GetTitleOffset() / factor )
            if axis == yAxis:
                axis.SetTitleSize( axis.GetTitleSize() * factor * yFactor )
                axis.SetTitleOffset( axis.GetTitleOffset() / ( factor * yFactor ) )
                # axis.SetLabelOffset( axis.GetLabelOffset() * factor )

class SystPlot( DoublePlot ):
    
    from AtlasStyle import mcErrorStyle, redLine
    defaultMcErrorStyle = mcErrorStyle
    defaultBaseLineStyle = redLine
    
    def __init__( self, title='DataMcPlot', xVariable=None, yVariableUp=var_Events, yVariableDown=Variable( 'Syst/Nom', binning=Binning(40, 0.6, 1.4) ), upperFraction=0.7, lowerFraction=0.3 ):
        DoublePlot.__init__( self, title, xVariable, yVariableUp, yVariableDown, upperFraction, lowerFraction )
        from ROOT import TF1
        self.dataHist = None
        self.upMcRatioHist = None
        self.nomMcRatioHist = None
        self.downMcRatioHist = None
        self.upMcHist = None
        self.nomMcHist = None
        self.downMcHist = None
        self.dataMcRatioHist = None
        self.baseLine = TF1( '%s_baseLine' % self.title, '1', xVariable.binning.low, xVariable.binning.up )
        self.mcErrorStyle = self.defaultMcErrorStyle
        self.baseLineStyle = self.defaultBaseLineStyle
        self.systlist = []
        
    def addFunction( self, function, drawOption, legendTitle='', copy=True ):
        return self.plotUp.addFunction( function, drawOption, legendTitle, copy )
    
    def addFitFunction( self, obj, function, xMin=None, xMax=None, legendTitle='', copy=True ):
        return self.plotUp.addFitFunction( obj, function, xMin, xMax, legendTitle, copy )
        
    def setDownHistogram( self, histogram ):
        drawOption='HIST'
        copy = True
        stacked = False
        if not histogram:
            return
        self.downMcHist = histogram
        if self.downMcRatioHist:
            del self.downMcRatioHist
        self.downMcRatioHist = histogram.Clone( '%s_downMcRatio_%s' % ( self.title, uuid.uuid1() ) )
        if not self.downMcRatioHist.GetSumw2N():
            self.downMcRatioHist.Sumw2()
        return self.plotUp.addHistogram( histogram, drawOption, stacked, copy )

    def setUpHistogram( self, histogram ):
        drawOption='HIST'
        copy = True
        stacked = False
        if not histogram:
            return
        self.upMcHist = histogram
        if self.upMcRatioHist:
            del self.upMcRatioHist
        self.upMcRatioHist = histogram.Clone( '%s_upMcRatio_%s' % ( self.title, uuid.uuid1() ) )
        if not self.upMcRatioHist.GetSumw2N():
            self.upMcRatioHist.Sumw2()
        return self.plotUp.addHistogram( histogram, drawOption, stacked, copy )
        
    def setNomHistogram( self, histogram ):
        drawOption='HIST'
        copy = True
        stacked = False
        if not histogram:
            return
        self.nomMcHist = histogram
        if self.nomMcRatioHist:
            del self.nomMcRatioHist
        self.nomMcRatioHist = histogram.Clone( '%s_nomMcRatio_%s' % ( self.title, uuid.uuid1() ) )
        if not self.nomMcRatioHist.GetSumw2N():
            self.nomMcRatioHist.Sumw2()
        return self.plotUp.addHistogram( histogram, drawOption, stacked, copy )
        
    def setDataHistogram( self, histogram ):
        if not histogram:
            return
        self.dataHist = histogram
        if self.dataMcRatioHist:
            del self.dataMcRatioHist
        self.dataMcRatioHist = histogram.Clone( '%s_DataMcRatio_%s' % ( self.title, uuid.uuid1() ) )
        if not self.dataMcRatioHist.GetSumw2N():
            self.dataMcRatioHist.Sumw2()
        
    def __mainAction__( self ):
        DoublePlot.__mainAction__( self )
        # make sure that data is always the last histogram drawn
        if self.dataHist in self.plotUp.histograms:
            self.plotUp.histograms.pop( self.plotUp.histograms.index( self.dataHist ) )
        if self.baseLine:
            self.baseLineStyle.apply( self.baseLine )
            self.baseLine.SetLineWidth( 1 )
            self.plotDown.addHistogram( self.baseLine.GetHistogram(), 'L', False, True )
        if self.upMcRatioHist:
            self.plotDown.addHistogram( self.upMcRatioHist, 'HIST', False, False )
        if self.downMcRatioHist:
            self.plotDown.addHistogram( self.downMcRatioHist, 'HIST', False, False )
        # loop over hists to add up to overall 
        if self.upMcHist:
            self.upMcRatioHist.Reset()
            self.upMcRatioHist.Add( self.upMcHist )
            if self.nomMcHist:
                self.upMcRatioHist.Divide( self.nomMcHist )
        if self.downMcHist:
            self.downMcRatioHist.Reset()
            self.downMcRatioHist.Add( self.downMcHist )
            if self.nomMcHist:
                self.downMcRatioHist.Divide( self.nomMcHist )
                
    def __drawDecorations__(self):
        # reverse the order of the legend entries
        self.legendElements.reverse()
        DoublePlot.__drawDecorations__( self )

class DataMcSystPlot( DoublePlot ):
    
    from AtlasStyle import mcErrorStyle, redLine
    defaultMcErrorStyle = mcErrorStyle
    defaultBaseLineStyle = redLine
    
    def __init__( self, title='DataMcPlot', xVariable=None, yVariableUp=var_Events, yVariableDown=Variable( 'Data/MC', binning=Binning(40, 0.6, 1.4) ), upperFraction=0.7, lowerFraction=0.3 ):
        DoublePlot.__init__( self, title, xVariable, yVariableUp, yVariableDown, upperFraction, lowerFraction )
        from ROOT import TF1
        #@param dataHist        Data on main plot (need to change to TAsymErrors?)
        #@param sumMcHist       MC error on main plot
        #@param sumMcRatioHist  MC error on ratio plot
        #@param dataMcRatioHist Data on ratio plot
        self.dataHist = None
        self.sumMcHist = None
        self.sumSystMcHist = None
        self.sumMcRatioHist = None
        self.dataMcRatioHist = None
        self.baseLine = TF1( '%s_baseLine' % self.title, '1', xVariable.binning.low, xVariable.binning.up )
        self.mcErrorStyle = self.defaultMcErrorStyle
        self.baseLineStyle = self.defaultBaseLineStyle
    
    def addHistogram( self, histogram, drawOption='HIST', stacked=True, copy=True ):
        if not self.sumMcHist and histogram:
            self.sumMcHist = histogram.Clone( '%s_SumMc_%s' % ( self.title, uuid.uuid1() ) )
            self.sumMcRatioHist = histogram.Clone( '%s_SumMcRatio_%s' % ( self.title, uuid.uuid1() ) )
            if not self.sumMcRatioHist.GetSumw2N():
                self.sumMcRatioHist.Sumw2()
            self.sumMcHist.SetTitle( 'Stat' )
            self.plotUp.addHistogram( self.sumMcHist, 'E2', False, False )
        return self.plotUp.addHistogram( histogram, drawOption, stacked, copy )
        
    def addFunction( self, function, drawOption, legendTitle='', copy=True ):
        return self.plotUp.addFunction( function, drawOption, legendTitle, copy )
    
    def addFitFunction( self, obj, function, xMin=None, xMax=None, legendTitle='', copy=True ):
        return self.plotUp.addFitFunction( obj, function, xMin, xMax, legendTitle, copy )
        
    def setDataHistogram( self, histogram ):
        if not histogram:
            return
        self.dataHist = histogram
        if self.dataMcRatioHist:
            del self.dataMcRatioHist
        self.dataMcRatioHist = histogram.Clone( '%s_DataMcRatio_%s' % ( self.title, uuid.uuid1() ) )
        if not self.dataMcRatioHist.GetSumw2N():
            self.dataMcRatioHist.Sumw2()
        
    def __mainAction__( self ):
        DoublePlot.__mainAction__( self )
        # make sure that data is always the last histogram drawn
        if self.dataHist in self.plotUp.histograms:
            self.plotUp.histograms.pop( self.plotUp.histograms.index( self.dataHist ) )
        if self.sumMcRatioHist in self.plotDown.histograms:
            self.plotDown.histograms.pop( self.plotDown.histograms.index( self.sumMcRatioHist ) )
        if self.sumMcHist:
            self.sumMcHist.Reset()
            self.sumMcRatioHist.Reset()
            self.mcErrorStyle.apply( self.sumMcHist )
            self.mcErrorStyle.apply( self.sumMcRatioHist )
            self.plotDown.addHistogram( self.sumMcRatioHist, 'E2', False, False )
        if self.baseLine:
            self.baseLineStyle.apply( self.baseLine )
            self.baseLine.SetLineWidth( 1 )
            self.plotDown.addHistogram( self.baseLine.GetHistogram(), 'L', False, True )
        if self.dataHist:
            self.plotUp.addHistogram( self.dataHist, 'E0', False, False )
            self.plotDown.addHistogram( self.dataMcRatioHist, 'E0', False, False )
        for hist in self.plotUp.histograms:
            if hist in [ self.dataHist, self.sumMcHist ] or hist not in self.plotUp.stackedHistograms:
                continue
            if self.sumMcHist:
                self.sumMcHist.Add( hist )
        if self.sumMcHist:
            self.sumMcRatioHist.Reset()
            self.sumMcRatioHist.Add( self.sumMcHist )
            self.sumMcRatioHist.Divide( self.sumMcRatioHist )
        if self.dataHist:
            self.dataMcRatioHist.Reset()
            self.dataMcRatioHist.Add( self.dataHist )
            if self.sumMcHist:
                self.dataMcRatioHist.Divide( self.sumMcHist )
                
    def __drawDecorations__(self):
        # reverse the order of the legend entries
        self.legendElements.reverse()
        DoublePlot.__drawDecorations__( self )
