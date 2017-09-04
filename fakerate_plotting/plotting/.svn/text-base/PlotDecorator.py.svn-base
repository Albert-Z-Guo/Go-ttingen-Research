"""@package PlotDecorator
Classes for decorating plots with titles, legends and other elements

@author Christian Grefe, Bonn University (christian.grefe@cern.ch)
"""

class DecoratorPosition():
    
    def __init__( self, name ):
        self.name = name
        
    def __repr__( self ):
        return 'DecoratorPosition(%r)' % self.name
        
leftTop = DecoratorPosition( 'LeftTop' )
leftCenter = DecoratorPosition( 'LeftCenter' )
leftBottom = DecoratorPosition( 'LeftBottom' )

rightTop = DecoratorPosition( 'RightTop' )
rightCenter = DecoratorPosition( 'RightCenter' )
rightBottom = DecoratorPosition( 'RightBottom' )
    

class PlotDecorator( object ):
    ## Class that takes care of placing legends and additional text on a plot

    def __init__( self, position=leftTop ):
        ## Default constructor
        #  @param position         string to identify where to position the text items (lt, rt, lb, rb) 
        self.position = position
        self.currentX = 0.
        self.currentY = 0.
        self.defaultWidth = 0.2
        self.defaultHeight = 0.2
        self.defaultUpperY = 0.93
        self.defaultLowerY = 0.2

    def decorate( self, plot ):
        ## Does nothing, see derived classes
        pass

    def __calculateSize__( self, plot ):
        print 'Calling base calculate size'
        ## Method hook to calculate width and height of the placed objects
        self.height = self.defaultHeight
        self.width = self.defaultWidth

    def __resetBasePosition__( self ):
        ## Method hook to reset the current positions to the original positions
        if self.position == leftTop:
            self.currentX = 0.2
            self.currentY = self.defaultUpperY
        elif self.position == rightTop:
            self.currentX = 0.9 - self.width
            self.currentY = self.defaultUpperY
        elif self.position == leftCenter:
            self.currentX = 0.2
            self.currentY = 0.58 + 0.5*self.height
        elif self.position == rightCenter:
            self.currentX = 0.9 - self.width
            self.currentY = 0.58 + 0.5*self.height
        elif self.position == leftBottom:
            self.currentX = 0.2
            self.currentY = self.defaultLowerY + self.height
        elif self.position == rightBottom:
            self.currentX = 0.9 - self.width
            self.currentY = self.defaultLowerY + self.height
        else:
            print 'ERROR: Unknown DecoratorPosition'
            self.currentX = 0.0
            self.currentY = 0.0


class LegendDecorator( PlotDecorator ):
    ## Class to place legend entries to a plot

    def __init__( self, position=rightTop ):
        ## Default constructor
        #  @param position         string to identify where to position the text items (lt, rt, lb, rb) 
        PlotDecorator.__init__( self, position )
        self.labelText = ''
        self.labelTextSize = 0.05
        self.labelTextFont = 42
        self.textSize = 0.04
        self.textFont = 42
        self.lineGap = 0.0
        self.columns = 1
        self.maxEntriesPerColumn = 6
        self.objectWidth = 0.03
    
    def decorate( self, plot ):
        PlotDecorator.decorate( self, plot )
        ## Does all the magic
        #  Reads the legendElements attribute from the plot object
        #  @ param plot          the plot object to decorate
                
        self.__calculateSize__( plot )
        self.__resetBasePosition__()
        
        import ROOT
        if self.labelText:
            self.currentY -= self.labelTextSize + self.lineGap
            t = ROOT.TLatex( self.currentX, self.currentY, self.labelText )
            t.SetNDC()
            if self.labelTextSize:
                t.SetTextSize( self.labelTextSize )
            if self.labelTextFont:
                t.SetTextFont( self.labelTextFont )
            plot.decoratorObjects.append( t )
        
        currentColumn = 0
        currentColumnEntries = 0
        maxColumnEntries = self.columns*[0]
        for legendElement in plot.legendElements:
            maxColumnEntries[ currentColumn ] += 1
            currentColumn += 1
            if currentColumn >= self.columns:
                currentColumn = 0
        
        basePositionY = self.currentY
        currentColumn = 0
        for legendElement in plot.legendElements:
            self.currentY -= self.textSize + self.lineGap
            if 'f' in legendElement.option.lower():
                o = ROOT.TPave( self.currentX, self.currentY, self.currentX + self.objectWidth, self.currentY + 0.7*self.textSize, 1, 'NDC' )
                o.SetFillColor( legendElement.obj.GetFillColor() )
                o.SetLineColor( legendElement.obj.GetLineColor() )
                o.SetLineWidth( legendElement.obj.GetLineWidth() )
                o.SetFillStyle( legendElement.obj.GetFillStyle() )
                plot.decoratorObjects.append( o )
            if 'l' in legendElement.option.lower():
                o = ROOT.TLine( self.currentX, self.currentY + 0.3*self.textSize, self.currentX + self.objectWidth, self.currentY + 0.3*self.textSize )
                o.SetLineColor( legendElement.obj.GetLineColor() )
                o.SetLineStyle( legendElement.obj.GetLineStyle() )
                o.SetLineWidth( legendElement.obj.GetLineWidth() )
                o.SetBit( ROOT.TLine.kLineNDC )
                plot.decoratorObjects.append( o )
            if 'p' in legendElement.option.lower():
                o = ROOT.TMarker( self.currentX + 0.5*self.objectWidth, self.currentY + 0.3*self.textSize, legendElement.obj.GetMarkerStyle() )
                o.SetMarkerSize( legendElement.obj.GetMarkerSize() )
                o.SetMarkerColor( legendElement.obj.GetMarkerColor() )
                o.SetNDC( True )
                plot.decoratorObjects.append( o )
            t = ROOT.TLatex( self.currentX + self.objectWidth + 0.15*self.textSize, self.currentY, legendElement.getText() )
            t.SetNDC()
            if self.labelTextSize:
                t.SetTextSize( self.textSize )
            if self.labelTextFont:
                t.SetTextFont( self.textFont )
            plot.decoratorObjects.append( t )
            currentColumnEntries += 1
            if currentColumnEntries >= maxColumnEntries[ currentColumn ]:
                currentColumn += 1
                currentColumnEntries = 0
                self.currentX += self.defaultWidth
                self.currentY = basePositionY
    
    def __calculateSize__( self, plot ):
        ## Method hook to calculate width and height of the placed objects
        if len(plot.legendElements) > self.maxEntriesPerColumn:
            self.columns = len(plot.legendElements) / int( self.maxEntriesPerColumn )
            if len(plot.legendElements) % int( self.maxEntriesPerColumn ) > 0:
                self.columns += 1     
        nLines = len( plot.legendElements )
        self.height = nLines * self.textSize + (nLines - 1) * self.lineGap
        if self.labelText:
            self.height += self.labelTextSize + self.lineGap
        self.width = self.defaultWidth * self.columns


class TitleDecorator( PlotDecorator ):
    ## Class that takes care of placing title text(s) onto a plot
    
    def __init__( self, position=leftTop ):
        PlotDecorator.__init__( self, position )
        self.labelText = ''
        self.labelTextSize = 0.05
        self.labelTextFont = 42
        self.textSize = 0.04
        self.textFont = 42
        self.lineGap = 0.0

    def decorate( self, plot ):
        PlotDecorator.decorate( self, plot )
        ## Does all the magic
        #  Reads the titles attribute from the plot object
        #  @ param plot          the plot object to decorate
        self.__calculateSize__( plot )
        self.__resetBasePosition__()
        import ROOT
        if self.labelText:
            self.currentY -= self.labelTextSize + self.lineGap
            t = ROOT.TLatex( self.currentX, self.currentY, self.labelText )
            t.SetNDC()
            if self.labelTextSize:
                t.SetTextSize( self.labelTextSize )
            if self.labelTextFont:
                t.SetTextFont( self.labelTextFont )
            plot.decoratorObjects.append( t )
        for title in plot.titles:
            self.currentY -= self.textSize + self.lineGap
            t = ROOT.TLatex( self.currentX, self.currentY, title )
            t.SetNDC()
            if self.textSize:
                t.SetTextSize( self.textSize )
            if self.textFont:
                t.SetTextFont( self.textFont )
            plot.decoratorObjects.append( t )

    def __calculateSize__( self, plot ):
        ## Method hook to calculate width and height of the placed objects
        nLines = len( plot.titles )
        self.height = nLines * self.textSize + (nLines - 1) * self.lineGap
        if self.labelText:
            self.height += self.labelTextSize + self.lineGap
        self.width = self.defaultWidth


class AtlasTitleDecorator( TitleDecorator ):
    ## Special version of the TitleDecorator that also adds 'ATLAS' on the plot

    def __init__( self, plotType='Preliminary', position=leftTop ):
        ## Default constructor
        #  @param plotType         string that is appended to 'ATLAS' in a slightly smaller font
        #  @param position         string to identify where to position the text items (lt, rt, lb, rb) 
        TitleDecorator.__init__( self, position )
        self.plotType = plotType
        self.labelText = '#it{#bf{ATLAS}}  %s' % self.plotType
        self.labelTextSize = 0.05
        self.labelTextFont = 42
