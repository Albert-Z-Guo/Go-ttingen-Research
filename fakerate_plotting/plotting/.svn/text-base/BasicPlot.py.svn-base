"""@package BasicPlot
Wrapper classes to generate beautiful ROOT plots

@author Christian Grefe, Bonn University (christian.grefe@cern.ch)
"""

from plotting.Variable import Variable, var_Entries, VariableBinning
from plotting.PlotDecorator import TitleDecorator, LegendDecorator
from plotting.AtlasStyle import applyAtlasStyle, Style
from plotting.Tools import combineStatsAndSystematics
import os, math, string, uuid, copy

# all characters usable in file names
allowedStringCharacters = string.ascii_letters + string.digits + '_-'

def alphanumericString( s ):
    ## returns a string with all non-alphanumeric characters removed
    #  @param s         input string
    #  @return          pure alpha-numeric string
    return ''.join( ch for ch in s if ch in allowedStringCharacters )

class TextElement:
    ## Container for text attributes used in TLatex
    from ROOT import kBlack
    
    def __init__( self, text, size=0.05, font=42, color=kBlack, italics=False, bold=False, alignment=11, x=0., y=0. ):
        ## Default contructor
        #  @param text      actual text
        #  @param size      text size
        #  @param font      text font
        #  @param color     text color
        #  @param italics   use italics font
        #  @param bold      use bold font
        self.text = text
        self.size = size
        self.font = font
        self.color = color
        self.italics = italics
        self.bold = bold
        self.x = x
        self.y = y
        self.alignment = alignment

    def getText( self ):
        ## returns the TLatex string with all styling attributes
        #  @return          string to be used in TLates
        result = self.text
        if self.font:
            result = '#font[%d]{%s}' % (self.font, result)
        if self.color:
            result = '#color[%d]{%s}' % (self.color, result)
        if self.italics:
            result = '#it{%s}' % result
        if self.italics:
            result = '#bf{%s}' % result
        return result
    
    def getTLatex( self ):
        from ROOT import TLatex
        t = TLatex( self.x, self.y, self.getText() )
        t.SetNDC()
        t.SetTextSize( self.size )
        t.SetTextAlign( self.alignment )
        return t


class LegendElement:
    ## Container for a legend entry
    
    def __init__( self, obj, text, option ):
        ## Default contructor
        #  @param obj       object referenced in the legend entry
        #  @param text      text element used for the legend entry
        #  @param option    draw option: 'l' for line, 'p' for marker, 'f' for filled box
        self.obj = obj
        self.text = text
        self.option = option

    def __str__( self ):
        return 'LegendElement(%r,%r,%r)' % (self.obj, self.text, self.option)

    def getText( self ):
        if isinstance( self.text, TextElement ):
            return self.text.getText()
        return self.text

class BasicPlot( object ):
    ## Generic class holding histograms, functions and graphs.
    #  It takes care of drawing and styling.
    
    applyAtlasStyle()
    defaultTitleDecorator = TitleDecorator()
    defaultLegendDecorator = LegendDecorator()
    
    def __init__( self, title='', xVariable=None, yVariable=var_Entries, zVariable=var_Entries ):
        ## Default constuctor. Check below for options
        #  @param title       title of the canvas
        #  @param xVariable   Variable object defining the x axis
        #  @param yVariable   Variable object defining the y axis
        from ROOT import kGray            
        from ROOT import THStack

        # User options
        self.titleDecorator = copy.copy( self.defaultTitleDecorator )   # object steering how titles are added to the plot
        self.legendDecorator = copy.copy( self.defaultLegendDecorator ) # object steering how legend entries are added to the plot
        self.decorators = [ self.titleDecorator, self.legendDecorator ]
        self.title = title                    # title of the canvas
        self.titles = []                      # titles interpreted by the titleDecorator object
        self.xSize = 800                      # x-dimension of the TCanvas
        self.ySize = 600                      # y-dimension of the TCanvas
        self.stackedOutlineColor = kGray + 2  # color used as line color for filled THStack
        self.normalizeByBinWidth = False      # decide if individual bins should be drawn normalized by their respective bin width
        self.normalized = False               # decide if histograms should be drawn normalized to their integral instead
        self.topMargin = 0.2                  # fraction of the plot thats left blank on top, ie. all histograms, graphs, etc. are below
        self.bottomMargin = 0.05              # fraction of the plot thats left blank on bottom, ie. all histograms, graphs, etc. are above
        self.logX = False                     # decide if the plot should be drawn with logarithmic x-axis
        self.logY = False                     # decide if the plot should be drawn with logarithmic y-axis
        self.logZ = False                     # decide if the plot should be drawn with logarithmic z-axis
        self.showBinWidthY = True             # decide if the y-axis label contains '/ <binWidthX> [<unitX>]' 
        self.combineStatsAndSyst = True       # decide if systematic and statistical errors should be drawn combined or seperately 

        # Internal stuff
        self.canvas = None                    # the actual TCanvas object, created when calling draw()
        self.zColorPalette = None
        self.xVariable = xVariable 
        self.yVariable = yVariable
        self.zVariable = zVariable
        self.histograms2D = []
        self.histograms = []
        self.histogramStack = THStack()
        self.stackedHistograms = []
        self.histogramsByName = {}
        self.optionsDict = {}
        self.textElements = []
        self.legendElements = []
        self.graphs = []
        self.graphsByName = {}
        self.fitFunctions = {}
        self.fitResults = {}
        self.fitOptions = {}
        self.functions = []
        self.functionsByName = {}
        self.systematicsGraphs = {}
        self.combinedSystematicsGraphs = {}
        self.legendTitles = {}
        self.objects = []
        self.decoratorObjects = []
        self.firstDrawnObject = None
        self.previousFirstDrawnObject = None
        self.drawLegend = True
        self.drawTitle = True
        self.minimum = float('inf')
        self.maximum = float('-inf')
        self.firstTimeDrawn = True
    
    def addHistogram( self, histogram, drawOption='HIST', stacked=False, copy=False ):
        ## Adds a histogram to the list of drawn objects
        #  @param histogram    TH1 or TH2 object
        #  @param drawOption   option used to draw the object
        #  @param stacked      set if histogram should be stacked with other stacked histograms
        #  @param copy         make a copy of the histogram instead of using the object itself
        #  @return the histogram object (useful if copy=True to get the copied object)
        if not histogram:
            return
        name = histogram.GetName()
        if copy:
            # generate a copy with a unique name
            histogram = histogram.Clone( '%s_%s' % (name, uuid.uuid1()) )
        self.histogramsByName[ name ] = histogram
        self.optionsDict[ histogram ] = drawOption
        from ROOT import TH2
        if isinstance( histogram, TH2 ):
            self.histograms2D.append( histogram )
        else:
            if stacked:
                self.histogramStack.Add( histogram, drawOption )
                self.stackedHistograms.append( histogram )
            self.histograms.append( histogram )
        self.objects.append( histogram )
        return histogram
    
    def addSystematicsGraph( self, obj, graph, drawOption='2', copy=False ):
        ## Adds a graph containing the systematic errors for the given object (typically a TH1 or TGraph).
        #  The graph needs to have the same number of points/bins as the corresponding object.
        #  If the systematic errors should be drawn seperately, the x/y-values of the graph should match
        #  the corresponding bin centre and bin content / x-y position.
        #  @param obj          TH1 or TGraph object
        #  @param graph        TGraphAsymmErrors containing the systematic errors
        #  @param drawOption   option used to draw the object
        #  @param copy         make a copy of the histogram instead of using the object itself
        #  @return the histogram object (useful if copy=True to get the copied object)
        if not obj or not graph:
            return
        #graph = self.addGraph( graph, drawOption, copy )
        self.systematicsGraphs[ obj ] = graph
        return graph
    
    def addGraph( self, graph, drawOption='P', copy=False ):
        ## Adds a graph to the list of drawn objects
        #  @param graph        TGraph object
        #  @param drawOption   option used to draw the object
        #  @param copy         make a copy of the graph instead of using the object itself
        #  @return the graph object (useful if copy=True to get the copied object)
        if not graph:
            return
        name = graph.GetName()
        if copy:
            graph = graph.Clone( '%s_%s' % (name, uuid.uuid1()) )
        self.graphsByName[ name ] = graph
        self.optionsDict[ graph ] = drawOption
        self.graphs.append( graph )
        self.objects.append( graph )
        return graph
    
    def addFitFunction( self, obj, function, drawOption='', fitOption='QN0', xMin=None, xMax=None, legendTitle='', copy=False ):
        ## Adds a fit function which is linked to the given object. When draw() is called automatically
        #  invokes obj.Fit( function ). Make sure obj is in the list of drawn objects or call obj.Draw()
        #  yourself in order to allow the fit to succeed.
        #  @param obj          object which should be fitted
        #  @param function     TF1 object used in the fit
        #  @param drawOption   option used to draw the object
        #  @param fitOption    option passed to obj.Fit
        #  @param xMin         lower limit of the fit range
        #  @param xMax         upper limit of the fit range
        #  @param legendTitle  title used in the plot legend. If empty no entry willl be made for the fit function
        #  @param copy         make a copy of the fit function instead of using the object itself
        #  @return the graph object (useful if copy=True to get the copied object)
        name = function.GetName()
        if copy:
            function = function.Clone( '%s_%s' % (name, uuid.uuid1()) )
        if not self.fitFunctions.has_key( obj ):
            self.fitFunctions[ obj ] = []
        function = self.addFunction( function, drawOption, legendTitle, copy)
        self.fitFunctions[ obj ].append( function )
        self.fitOptions[ function ] = fitOption
        if function.GetXmin() == 0. and function.GetXmax() == 1.:
            if not xMin:
                xMin = self.xVariable.binning.low
            if not xMax:
                xMax = self.xVariable.binning.up
            function.SetRange( xMin, xMax )
        return function
    
    def addFunction( self, function, drawOption='', legendTitle='', copy=False ):
        ## Adds a function to the list of drawn objects
        #  @param graph        TF1 object
        #  @param drawOption   option used to draw the object
        #  @param legendTitle  title used in the plot legend
        #  @param copy         make a copy of the graph instead of using the object itself
        #  @return the function object (useful if copy=True to get the copied object)
        name = function.GetName()
        if copy:
            function = function.Clone( '%s_%s' % (name, uuid.uuid1()) )
        self.functionsByName[ name ] = function
        self.optionsDict[ function ] = drawOption
        self.legendTitles[ function ] = legendTitle
        self.functions.append( function )
        self.objects.append( function )
        return function
        
    def draw( self ):
        ## Method that does all the magic
        self.__initAction__()
        self.__mainAction__()
        if self.normalizeByBinWidth:
            self.__normalizeByBinWidth__()
        if self.normalized:
            self.__normalizeObjects__()
        self.__fitObjects__()
        self.__drawObjects__()
        self.__drawDecorations__()
        self.__finalizeAction__()
    
    def __normalizeByBinWidth__( self ):
        ## Normalizes all bins in all histograms, i.e. divides their entries by the bin width
        for histogram in self.histograms:
            for iBin in range( 1, histogram.GetNbinsX() + 1 ):
                binWidth = histogram.GetBinWidth( iBin )
                if binWidth > 0.:
                    histogram.SetBinContent( iBin, histogram.GetBinContent( iBin ) / binWidth )
                    histogram.SetBinError( iBin, histogram.GetBinError( iBin ) / binWidth )
        ## Normalise systematics graph like above histograms
        from ROOT import Double
        for graph in self.graphs:
            x, y, ex1, ex2, ey1, ey2 = (Double(0),Double(0),Double(0),Double(0), Double(0), Double(0))
            for iPoint in xrange(graph.GetN()):
                graph.GetPoint(iPoint,x,y)
                ex1=graph.GetErrorXlow(iPoint)
                ex2=graph.GetErrorXhigh(iPoint)
                ey1=graph.GetErrorYlow(iPoint)
                ey2=graph.GetErrorYhigh(iPoint)
            
                width=ex1+ex2
            
                ynew=y/width
                ey1new=ey1/width
                ey2new=ey2/width
                graph.SetPoint(iPoint,x,ynew)
                graph.SetPointError(iPoint,ex1,ex2,ey1new,ey2new)
    
    def __normalizeObjects__( self ):
        ## Normalizes all histograms, i.e. set their integral to 1
        for histogram in self.histograms + self.histograms2D:
            if not histogram.GetSumw2N():
                histogram.Sumw2()
            integral = histogram.Integral()
            if integral > 0. and not integral == 1.:
                histogram.Scale( 1. / integral )
                
    def __fitObjects__( self ):
        ## Fits all objects for which a fit function is defined 
        for obj, fitFunctions in self.fitFunctions.items():
            for function in fitFunctions:
                self.fitResults[ function ] = obj.Fit( function, self.fitOptions[ function ] )
    
    def __drawObjects__( self ):
        ## Draw all objects including histograms, graphs and functions and any other object registered
        self.canvas.cd()
        # first draw the 2D histograms
        for histogram in self.histograms2D:
            self.__drawHistogram2D__( histogram )
        # first draw the histogram stack
        self.__drawHistogramStack__()
        # now loop over objects and draw them
        for obj in self.objects:
            if obj in self.histograms2D:
                continue
            elif obj in self.histograms:
                self.__drawHistogram__( obj )
            elif obj in self.graphs:
                self.__drawGraph__( obj )
            elif obj in self.functions:
                self.__drawFunction__( obj )
            else:
                obj.Draw()
        # redraw axis to ensure tick marks are not covered
        if self.firstDrawnObject:
            self.firstDrawnObject.Draw( 'SAMEAXIS' )
        self.canvas.Update()

    def __drawHistogram2D__( self, hist ):
        ## Takes care of drawing a 2D histogram object.
        #  Also takes care of calculating axis ranges, etc.
        drawOption = self.optionsDict[ hist ]
        if not self.firstDrawnObject:
            self.firstDrawnObject = hist
        else:
            drawOption += 'SAME'
        hist.Draw( drawOption )
        # make room for z color palette if necessary
        if 'Z' in drawOption.upper():
            self.canvas.Update()
            self.canvas.SetRightMargin( 0.17 )
            palette = hist.GetListOfFunctions().FindObject( 'palette' )
            palette.SetX1NDC( 0.835 )
            palette.SetX2NDC( 0.87 )
            palette.SetLabelSize( 0.04 )
            palette.SetLabelOffset( 0.01 )
            palette.SetTitleSize( 0.06 )
            palette.SetTitleOffset( 1.1 )
    
    def __drawHistogramStack__( self ):
        ## Takes care of drawing the histogram stack
        #  Also takes care of calculating axis ranges, etc.
        stack = self.histogramStack
        for hist in self.stackedHistograms:
            # always use filled histograms 
            if not hist.GetFillColor():
                hist.SetFillColor( hist.GetLineColor() )
            if not hist.GetFillStyle():
                hist.SetFillStyle( 1001 )
            if self.stackedOutlineColor:
                hist.SetLineColor( self.stackedOutlineColor )
            hist.SetLineWidth( 1 )
        if self.stackedHistograms:
            # update plot min/max
            if self.minimum > stack.GetMinimum():
                self.minimum = stack.GetMinimum()
            if self.maximum < stack.GetMaximum():
                self.maximum = stack.GetMaximum()
            # actual draw operation
            if self.firstDrawnObject:
                stack.Draw( 'SAME' )
            else:
                self.firstDrawnObject = stack
                self.firstDrawnObject.Draw()
                self.firstDrawnObject.GetYaxis()
    
    def __drawHistogram__( self, hist ):
        ## Takes care of drawing a histogram
        #  Also takes care of calculating axis ranges, etc.
        drawOption = self.optionsDict[ hist ].upper()
        title = hist.GetTitle()
        if title:
            legendOption = 'pl'
            if drawOption in ['HIST']:
                legendOption = 'l'
            if hist in self.stackedHistograms:
                legendOption = 'f'
            if any( x in drawOption for x in ['E2', 'E3', 'E4', 'E5']):
                legendOption = 'f'
            self.legendElements.append( LegendElement( hist, title, legendOption ) )
        # update plotting range
        minBin = hist.GetMinimumBin()
        histMin = hist.GetBinContent(minBin)
        maxBin = hist.GetMaximumBin()
        histMax = hist.GetBinContent(maxBin)
        if 'e' in drawOption.lower():
            histMin -= hist.GetBinErrorLow(minBin)
            histMax += hist.GetBinErrorUp(maxBin)
        if histMin < self.minimum:
            self.minimum = histMin
        if histMax > self.maximum:
            self.maximum = histMax
        # don't draw stacked histograms (done by drawHistogramStack)
        if hist not in self.stackedHistograms:
            # combine statistical and systematic uncertainties (not for stacked histograms)
            if self.combineStatsAndSyst and self.systematicsGraphs.has_key( hist ):
                graph = self.systematicsGraphs[ hist ]
                graph = combineStatsAndSystematics( hist, graph, True )
                graph.SetTitle( '' )
                Style.fromObject( hist ).apply( graph )
                self.combinedSystematicsGraphs = graph
                try:
                    self.optionsDict[ graph ] = drawOption[ drawOption.find( 'E' ) + 1 ]
                except:
                    self.optionsDict[ graph ] = '0'
                drawOption.replace( 'E', '' )
                self.__drawGraph__( graph )
            if self.firstDrawnObject:
                drawOption += 'SAME'
            else:
                self.firstDrawnObject = hist
            hist.Draw( drawOption )
            
    def __drawGraph__( self, graph ):
        ## Takes care of drawing a graph
        #  Also takes care of calculating axis ranges, etc.
        if self.combineStatsAndSyst and graph in self.systematicsGraphs.values():
            return
        drawOption = self.optionsDict[ graph ].upper()
        title = graph.GetTitle()
        if title:
            legendOption = ''
            if any( x in drawOption for x in ['L', '0']):
                legendOption += 'L'
            if any( x in drawOption for x in ['2', '3', '4', '5']):
                legendOption += 'F'
            if any( x in drawOption for x in ['P']):
                legendOption += 'P'
            self.legendElements.append( LegendElement( graph, title, legendOption ) )
        if not self.firstDrawnObject:
            self.firstDrawnObject = self.xVariable.createHistogram()
            self.firstDrawnObject.Draw()
        if graph.GetN() > 0:
            from ROOT import Double
            xMin, xMax, yMin, yMax = (Double(), Double(), Double(), Double())
            graph.ComputeRange( xMin, yMin, xMax, yMax )
            if self.minimum > yMin:
                self.minimum = yMin
            if self.maximum < yMax:
                self.maximum = yMax
            graph.Draw( drawOption )
            
    def __drawFunction__( self, function ):
        ## draws all function objects
        drawOption = self.optionsDict[ function ]
        title = self.legendTitles[ function ]
        if title:
            legendOption = 'L'
            self.legendElements.append( LegendElement( function, title, legendOption ) )
        if self.firstDrawnObject:
            drawOption += 'SAME'
        else:
            self.firstDrawnObject = self.xVariable.createHistogram()
            self.firstDrawnObject.Draw()
        function.Draw( drawOption )
        
    def __drawDecorations__( self ):
        self.canvas.cd()
        for decorator in self.decorators:
            decorator.decorate( self )
        from ROOT import TLatex
        for textElement in self.textElements:
            self.decoratorObjects.append( textElement.getTLatex() )
        for obj in self.decoratorObjects:
            obj.Draw()

    def __initAction__( self ):
        ## initialization hook, takes care of modifying any member variables for later use
        from ROOT import TCanvas
        if not self.canvas:
            self.canvas = TCanvas( alphanumericString( self.title ), self.title, self.xSize, self.ySize )
        self.canvas.Clear()
        
        # reset some values in case it was drawn before
        del self.legendElements[:]
        del self.decoratorObjects[:]
        self.previousFirstDrawnObject = self.firstDrawnObject
        self.firstDrawnObject = None
        self.minimum = float('inf')
        self.maximum = float('-inf')

    def __mainAction__( self ):
        ## main action hook, takes care of automatic creation of drawn objects
        pass
    
    def __finalizeAction__( self ):
        ## finalization hook, takes care setting axis ranges and setting log axes if requested
        # pre-set ranges override automatic range
        
        # treat axis labels
        if self.firstDrawnObject:
            xAxis = self.firstDrawnObject.GetXaxis()
            yAxis = self.firstDrawnObject.GetYaxis()
            try:
                zAxis = self.firstDrawnObject.GetZaxis()
            except:
                zAxis = None
                
            if xAxis:
                # no exponents on x-axis
                xAxis.SetNoExponent( True )
                if self.xVariable:
                    self.xVariable.applyToAxis( xAxis )
            if yAxis:
                if self.yVariable:
                    self.yVariable.applyToAxis( yAxis )
                from ROOT import TH2 
                if xAxis and xAxis.GetNbins() > 1 and self.showBinWidthY and not isinstance( self.firstDrawnObject, TH2 ) and not (isinstance(self.xVariable.binning, VariableBinning) and not self.normalizeByBinWidth):
                    yTitle = yAxis.GetTitle() + ' /'
                    if not self.normalizeByBinWidth:
                        yTitle += ' %.3g' % ((xAxis.GetXmax() - xAxis.GetXmin())/xAxis.GetNbins())
                    if self.xVariable and self.xVariable.unit:
                        yTitle += ' %s' % self.xVariable.unit
                    yAxis.SetTitle( yTitle )
            if zAxis and self.zVariable:
                self.zVariable.applyToAxis( zAxis )
        
        # update the minimum and maximum if it is defined in the variable binning
        if self.yVariable:
            if self.yVariable.binning.low is not None:
                if self.yVariable.binning.low != 0 or not self.logY:
                    self.minimum = self.yVariable.binning.low
                if self.yVariable.binning.up is not None:
                    self.maximum = self.yVariable.binning.up
        
        delta = self.maximum - self.minimum
        if self.logY:
            # make sure the minimum is larger than 0
            if self.minimum <= 0.:
                self.minimum = 0.001 * delta
            # calculate the fraction of the histogram on the pad in log units
            if self.yVariable.binning.up is None and self.maximum > 0.:
                delta = math.log10(self.maximum) - math.log10(self.minimum)
                self.maximum = 10**(math.log10(self.maximum) + delta*self.topMargin)
            # if we have no entries just make up some range for the empty plot
            elif delta == 0.:
                self.minimum = 0.001
                self.maximum = 1.
        else:
            if self.yVariable.binning.low is None and self.minimum != 0.:
                # if minimum is close to 0, set minimum to 0 instead
                if abs(self.minimum) < 0.05*delta or (self.minimum > 0 and self.minimum < delta * self.bottomMargin):
                    self.minimum = -0.
                else:
                    # 0 supressed plot, just leave margin to axis
                    self.minimum -= delta * self.bottomMargin
            self.maximum += delta * self.topMargin
    
        if self.firstDrawnObject:
            from ROOT import TH2
            if isinstance( self.firstDrawnObject, TH2 ):
                # FIXME: no treatment of minimum/maximum for 2D histograms
                pass 
            else:
                self.firstDrawnObject.SetMinimum( self.minimum )
                self.firstDrawnObject.SetMaximum( self.maximum )
                self.firstDrawnObject.GetYaxis().SetRangeUser( self.minimum, self.maximum )
        
        if self.logX:
            self.canvas.SetLogx()
        if self.logY:
            self.canvas.SetLogy()
        if self.logZ:
            self.canvas.SetLogz()
        self.canvas.Update()
        self.firstTimeDrawn = False
            
    def saveAs( self, path='' ):
        ## save the canvas under the given path. If no file ending is given store as PDF
        #  @param path          full path of output file
        fileName, extension = os.path.splitext( path )
        if not extension:
            extension = '.pdf'
        if not fileName:
            fileName = self.title
        #import ROOT
        #oldLevel = ROOT.gErrorIgnoreLevel
        #ROOT.gErrorIgnoreLevel = ROOT.kInfo+1
        self.canvas.SaveAs( fileName + extension )
        #ROOT.gErrorIgnoreLevel = oldLevel
            
    def saveAsAll( self, path='' ):
        ## save the canvas under the given path in all relevant types: EPS, PDF and C-macro
        #  @param path          full path of output file (file ending ignored)
        fileName, extension = os.path.splitext( path )
        self.saveAs( fileName + '.eps' )
        self.saveAs( fileName + '.C' )
        self.saveAs( fileName + '.png' )
        self.saveAs( fileName + '.pdf' )
        self.saveAs( fileName + '.root' )
            
    def saveIn( self, path='' ):
        ## save the canvas under the given path. The file name is created from the plot title
        #  @param path          base path of output file, file name created automatically
        self.saveAs( os.path.join( path, self.title ) )

if __name__ == '__main__':
    from ROOT import kBlack, kBlue, kRed, kGreen
    from ROOT import TH1D, TF1, TH2D, TF2
    from Variable import var_Normalized
    
    h1 = TH1D( 'hTest1', 'First Test', 40, -4, 4 )
    h1.FillRandom( 'gaus', 1000 )
    h1.SetLineColor( kRed )
    
    h2 = TH1D( 'hTest2', 'Second Test', 40, -4, 4 )
    h2.FillRandom( 'gaus', 500 )
    h2.SetLineColor( kBlue )
    
    h3 = TH1D( 'hTest3', 'Data', 40, -4, 4 )
    h3.FillRandom( 'gaus', 1500 )
    h3.SetLineColor( kBlack )
    
    f = TF1( 'fTest', 'gaus', -4, 4 )
    f.SetLineColor( kGreen+2 )
    
    xVar = Variable( 'Invariant Mass', unit='GeV' )
    
    basicTest = BasicPlot( 'basicTest', xVar, var_Normalized )
    h = basicTest.addHistogram( h1, 'HIST', copy=True )
    basicTest.addHistogram( h2, 'E0', copy=True )
    basicTest.addFitFunction( h, f, legendTitle='Fit to First' )
    basicTest.titles.append( 'My title' )
    basicTest.titles.append( 'My second title' )
    basicTest.normalized = True
    basicTest.draw()
    basicTest.saveIn()
        
    stackedTest = BasicPlot( 'stackedTest', xVar )
    stackedTest.addHistogram( h3, 'E' )
    stackedTest.addHistogram( h1, stacked=True )
    stackedTest.addHistogram( h2, stacked=True )
    stackedTest.draw()
    stackedTest.saveIn()
    
    f2 = TF2("f2","sin(x)*sin(y)/(x*y)",0,5,0,5);
    h2D = TH2D( 'hTest2D', 'Test 2D', 40, -1, 1, 40, -1, 1 )
    h2D.FillRandom( "f2", 10000 )
    test2D = BasicPlot( 'Test2D', Variable( 'x' ), Variable( 'y' ) )
    test2D.showBinWidthY = False
    test2D.addHistogram( h2D, 'COLZ', False )
    test2D.draw()
    

    raw_input( 'Continue?' )
