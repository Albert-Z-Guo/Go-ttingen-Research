from plotting.BasicPlot import BasicPlot, alphanumericString
from plotting.Variable import Binning, var_Entries

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
        self.plotDown.topMargin = 0.
        self.plotDown.bottomMargin = 0.
        self.decorators = []
        self.plotDown.decorators = []
    
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
        self.plotUp.normalizeByBinWidth = self.normalizeByBinWidth
        
        # initialize layout
        self.plotUp.canvas.SetPad( 0., 1.-self.upperFraction, 1., 1. )
        self.plotUp.canvas.SetBottomMargin( 0.01 )
        self.plotUp.canvas.SetTopMargin( self.plotDown.canvas.GetTopMargin() / self.upperFraction )
        self.plotUp.canvas.Update()
        self.plotDown.canvas.SetPad( 0., 0., 1., self.lowerFraction )
        self.plotDown.canvas.SetTopMargin( 0.01 )
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
    
    def __mainAction__( self ):
        BasicPlot.__mainAction__( self )
        self.plotDown.__mainAction__()
        self.plotUp.__mainAction__()
    
    def __normalizeObjects__( self ):
        self.plotUp.__normalizeObjects__()
        self.plotDown.__normalizeObjects__()
    
    def __normalizeByBinWidth__( self ):
        self.plotUp.__normalizeByBinWidth__()
        #Commented out since normbybinwidth not necessary for ratioplot down
        #self.plotDown.__normalizeByBinWidth__()
    
    def __fitObjects__( self ):
        self.plotUp.__fitObjects__()
        self.plotDown.__fitObjects__()
    
    def __drawObjects__( self ):
        BasicPlot.__drawObjects__( self )
        self.plotDown.__drawObjects__()
        self.plotUp.__drawObjects__()
   
    def __drawDecorations__(self):
        BasicPlot.__drawDecorations__( self )
        self.plotDown.__drawDecorations__()
        self.plotUp.__drawDecorations__()
    
    def __finalizeAction__( self ):
        self.plotUp.logX = self.logX
        self.plotUp.logY = self.logY
        self.plotUp.logZ = self.logZ
        self.plotDown.__finalizeAction__()
        self.plotUp.__finalizeAction__()
        if self.plotUp.firstDrawnObject and self.plotUp.firstDrawnObject != self.plotUp.previousFirstDrawnObject:
            xAxis = self.plotUp.firstDrawnObject.GetXaxis()
            xAxis.SetTickLength( xAxis.GetTickLength() / self.upperFraction )
            # supress labels by drawing in white
            xAxis.SetLabelColor( 0 )
            xAxis.SetTitleColor( 0 )
            xAxis.Draw()
            yAxis = self.plotUp.firstDrawnObject.GetYaxis()
            #yAxis.SetTickLength( yAxis.GetTickLength() / self.upperFraction )
            yAxis.SetLabelSize( yAxis.GetLabelSize() / self.upperFraction )
            yAxis.SetLabelOffset( yAxis.GetLabelOffset() / self.upperFraction )
            yAxis.SetTitleSize( yAxis.GetTitleSize() / self.upperFraction )
            yAxis.SetTitleOffset( yAxis.GetTitleOffset() * self.upperFraction * 1.1 )
            yAxis.Draw()
        if self.plotDown.firstDrawnObject and self.plotDown.firstDrawnObject != self.plotDown.previousFirstDrawnObject:
            xAxis = self.plotDown.firstDrawnObject.GetXaxis()
            xAxis.SetTickLength( xAxis.GetTickLength() / self.lowerFraction )
            xAxis.SetTitleSize( xAxis.GetTitleSize() / self.lowerFraction )
            xAxis.SetLabelSize( xAxis.GetLabelSize() / self.lowerFraction )
            xAxis.SetLabelOffset( xAxis.GetLabelOffset() / self.lowerFraction )
            xAxis.Draw()
            yAxis = self.plotDown.firstDrawnObject.GetYaxis()
            #yAxis.SetNdivisions( 5 )
            yAxis.CenterTitle( False )
            yAxis.SetTickLength( yAxis.GetTickLength() / self.lowerFraction * self.upperFraction )
            yAxis.SetLabelSize( yAxis.GetLabelSize() / self.lowerFraction * 0.7 )#adapted for envelope plots
            yAxis.SetLabelOffset( yAxis.GetLabelOffset() / self.lowerFraction ) #* 0.5 )
            yAxis.SetTitleSize( yAxis.GetTitleSize() / self.lowerFraction ) # * 0.7 )
            yAxis.SetTitleOffset( yAxis.GetTitleOffset() * self.lowerFraction * 1.1 )
            yAxis.Draw()
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
    
    # create a double plot with ratios by hand
    doubleTest = DoublePlot( 'testDoublePlot', xVar, yVariableDown=yVarDown )
    doubleTest.plotUp.stacked = True
    doubleTest.plotUp.addHistogram( hSum, 'E2' )
    doubleTest.plotUp.addHistogram( h3, 'E0' )
    hSum.Add( doubleTest.plotUp.addHistogram( h1, stacked=True ) )
    hSum.Add( doubleTest.plotUp.addHistogram( h2, stacked=True, copy=True ) )
    hRatio.Add( h3 )
    hRatio.Divide( hSum )
    doubleTest.plotDown.addHistogram( hRatio, 'E0' )
    doubleTest.draw()
    
    raw_input( 'Continue?' )
    
