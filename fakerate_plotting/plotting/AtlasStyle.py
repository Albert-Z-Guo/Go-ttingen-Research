"""@package AtlasStyle
Classes to generate ROOT plots according to ATLAS style

@author Christian Grefe, Bonn University (christian.grefe@cern.ch)
"""

from array import array
import os
import copy

## parse the ROOT macro only once
appliedAtlasStyle = False

def loadRootMacro( path ):
    ## Helper method to execute a ROOT C macro
    if os.path.exists( path ) and os.path.isfile( path ):
        import ROOT
        ROOT.gROOT.LoadMacro( path )
    else:
        print 'Unable to load macro %s' % path

def setPalette( name='palette', ncontours=999 ):
    """Set a color palette from a given RGB list
    stops, red, green and blue should all be lists of the same length
    see set_decent_colors for an example"""
    from ROOT import TColor, gStyle

    if name == "gray" or name == "grayscale":
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [1.00, 0.84, 0.61, 0.34, 0.00]
        green = [1.00, 0.84, 0.61, 0.34, 0.00]
        blue  = [1.00, 0.84, 0.61, 0.34, 0.00]
    # elif name == "whatever":
        # (define more palettes)
    else:
        # default palette, looks cool
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [0.00, 0.00, 0.87, 1.00, 0.51]
        green = [0.00, 0.81, 1.00, 0.20, 0.00]
        blue  = [0.51, 1.00, 0.12, 0.00, 0.00]

    s = array( 'd', stops )
    r = array( 'd', red )
    g = array( 'd', green )
    b = array( 'd', blue )

    npoints = len(s)
    TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
    gStyle.SetNumberContours(ncontours)
    
def applyAtlasStyle( path=os.environ.get('ATLAS_STYLE_MACRO') ):
    ## Helper method to load the ATLAS style ROOT C macro
    global appliedAtlasStyle
    if appliedAtlasStyle:
        return
    loadRootMacro( path )
    appliedAtlasStyle = True
    import plotting.Colours
    import ROOT
    ROOT.SetAtlasStyle()
    setPalette()
    ROOT.TGaxis.SetMaxDigits( 4 )


# Load the ATLAS style
applyAtlasStyle()



        
class Style:
    ## Simple container for style definitions
    
    def __init__( self, color=1, lineColor=None, lineStyle=0, lineWidth=3, markerColor=None, markerStyle=20, markerSize=1.2, fillColor=None, fillStyle=0 ):
        ## Default costructor
        #  @param color         the color 
        #  @param lineStyle     the line style (see TAttLine)
        #  @param markerStyle   the marker type (see TAttMarker)
        #  @param fillStyle     the fill style (see TAttFill)
        markerColor = markerColor if markerColor is not None else color
        lineColor = lineColor if lineColor is not None else color
        fillColor = fillColor if fillColor is not None else color
        self.lineColor = lineColor
        self.lineStyle = lineStyle
        self.lineWidth = lineWidth
        self.fillColor = fillColor
        self.fillStyle = fillStyle
        self.markerColor = markerColor
        self.markerStyle = markerStyle
        self.markerSize = markerSize
        
    @classmethod
    def fromXML( cls, element ):
        ## Constructor from an XML element
        #  <Style color="" lineColor="" lineStyle="" lineWidth="" markerColor="" markerStyle="" markerSize="" fillColor="" fillStyle=""/>
        #  @param element    the XML element
        #  @return the Cut object
        attributes = element.attrib
        color = int(attributes['color']) if attributes.has_key( 'color' ) else 1
        style = cls( color )
        if attributes.has_key( 'lineColor' ):
            style.lineColor = int(attributes['lineColor'])
        if attributes.has_key( 'lineStyle' ):
            style.lineStyle = int(attributes['lineStyle'])
        if attributes.has_key( 'lineWidth' ):
            style.lineWidth = int(attributes['lineWidth'])
        if attributes.has_key( 'markerColor' ):
            style.markerColor = int(attributes['markerColor'])
        if attributes.has_key( 'markerStyle' ):
            style.markerStyle = int(attributes['markerStyle'])
        if attributes.has_key( 'markerSize' ):
            style.markerSize = float(attributes['markerSize'])
        if attributes.has_key( 'fillColor' ):
            style.fillColor = int(attributes['fillColor'])
        if attributes.has_key( 'fillStyle' ):
            style.fillStyle = int(attributes['fillStyle'])
        return style

    @classmethod
    def fromObject( cls, obj ):
        style = cls()
        style.lineColor = obj.GetLineColor()
        style.lineWidth = obj.GetLineWidth()
        style.fillColor = obj.GetFillColor()
        style.fillStyle = obj.GetFillStyle()
        style.markerColor = obj.GetMarkerColor()
        style.markerStyle = obj.GetMarkerStyle()
        style.markerSize = obj.GetMarkerSize()
        return style
    
    def __repr__( self ):
        return 'Style'
    
    def __str__( self ):
        return 'Style: lCol=%d, lSty=%d, lWid=%d, mCol=%d, mSty=%d, mSiz=%g, fCol=%d, fSty=%d' % (self.lineColor, self.lineStyle, self.lineWidth, self.markerColor, self.markerStyle, self.markerSize, self.fillColor, self.fillStyle)
    
    def apply( self, obj ):
        ## Applies all attributes to the given object
        #  @param obj       the object to modify
        try:
            obj.SetLineColor( self.lineColor )
            obj.SetLineStyle( self.lineStyle )
            obj.SetLineWidth( self.lineWidth )
        except AttributeError:
            pass
        try:
            obj.SetFillColor( self.fillColor )
            obj.SetFillStyle( self.fillStyle )
        except AttributeError:
            pass
        try:
            obj.SetMarkerColor( self.markerColor )
            obj.SetMarkerStyle( self.markerStyle )
            obj.SetMarkerSize( self.markerSize )
        except AttributeError:
            pass
        
class FilledStyle( Style ):
    ## Simple container for style definitions
    
    def __init__( self, color=1, lineStyle=0, markerStyle=0, fillStyle=1001 ):
        ## Default costructor
        #  @param color         the color 
        #  @param lineStyle     the line style (see TAttLine)
        #  @param markerStyle   the marker type (see TAttMarker)
        #  @param fillStyle     the fill style (see TAttFill)
        Style.__init__( self, color, lineStyle, markerStyle, fillStyle )
        from ROOT import kBlack
        self.lineColor = kBlack
        self.lineWidth = 2

class DrawStyles:
    ## Container for defining sequence of styles
    #  Used to map a set of styles to a unique index
    
    def __init__( self, colorStyles=None, lineStyles=None, markerStyles=None, fillStyles=None ):
        ## Default constructor
        #  @param colorStyles       the ColorStyles object
        #  @param lineStyles         the LineStyles object
        #  @param markerStyles       the MarkerStyles object
        #  @param fillStyles        the FillStyles object
        self.colorStyles = colorStyles
        self.lineStyles = lineStyles
        self.markerStyles = markerStyles
        self.fillStyles = fillStyles
    
    def apply( self, obj, index ):
        ## Apply the relevant styles according to the given index
        #  @param obj           the object to modify
        #  @param index         the index to indentify the unique style
        if self.colorStyles:
            self.colorStyles.apply( obj, index )
        if self.lineStyles:
            self.lineStyles.apply( obj, index )
        if self.markerStyles:
            self.markerStyles.apply( obj, index )
        if self.fillStyles:
            self.fillStyles.apply( obj, index )

class ColorStyles:
    ## Container for defining sequence of color styles
    #  Used to map a set of styles to a unique index
    
    from ROOT import kBlack, kRed, kBlue, kGreen
    def __init__( self, colors=[kBlack, kRed, kBlue, kGreen] ):
        # Default constructor
        #  @param colors            list of ROOT color indices
        self.colors = colors
        self.line = True
        self.fill = True
        self.marker = True
    
    def apply( self, obj, index ):
        ## Apply the relevant styles according to the given index
        #  @param obj           the object to modify
        #  @param index         the index to indentify the unique style
        color = self.colors[ int(index) % len(self.colors) ]
        if self.line:
            obj.SetLineColor( color )
        if self.fill:
            obj.SetFillColor( color )
        if self.marker:
            obj.SetMarkerColor( color )

class LineStyles:
    ## Container for defining sequence of line styles
    #  Used to map a set of styles to a unique index
    
    from ROOT import kSolid, kDashed, kDotted, kDashDotted
    def __init__( self, styles=[kSolid, kDashed, kDotted, kDashDotted], width=None ):
        ## Default cosntructor
        #  @param colors            list of ROOT line style indices (see TAttLine)
        self.styles = styles
        self.width = width
    
    def apply( self, obj, index ):
        ## Apply the relevant styles according to the given index
        #  @param obj           the object to modify
        #  @param index         the index to indentify the unique style
        style = self.styles[ int(index) % len(self.styles) ]
        obj.SetLineStyle( style )
        if self.width:
            obj.SetLineWidth = width

class MarkerStyles:
    ## Container for defining sequence of marker styles
    #  Used to map a set of styles to a unique index
    
    from ROOT import kFullCircle, kFullSquare, kFullTriangleUp, kFullTriangleDown
    def __init__( self, styles=[kFullCircle, kFullSquare, kFullTriangleUp, kFullTriangleDown], size=None ):
        ## Default constructor
        #  @param colors            list of ROOT marker style indices (see TAttMarker)        
        self.styles = styles
        self.size = size
    
    def apply( self, obj, index ):
        ## Apply the relevant styles according to the given index
        #  @param obj           the object to modify
        #  @param index         the index to indentify the unique style
        style = self.styles[ int(index) % len(self.styles) ]
        obj.SetMarkerStyle( style )
        if self.size:
            obj.SetMarkerSize( self.size )

class FillStyles:
    ## Container for defining sequence of fill styles
    #  Used to map a set of styles to a unique index
    
    def __init__( self, styles=[3003, 3004, 3005] ):
        ## Default constructor
        #  @param colors            list of ROOT fill style indices (see TAttFill)
        self.styles = styles
    
    def apply( self, obj, index ):
        ## Apply the relevant styles according to the given index
        #  @param obj           the object to modify
        #  @param index         the index to indentify the unique style
        style = self.styles[ int(index) % len(self.styles) ]
        obj.SetFillStyle( style )

def dashedLineStyle( style ):
    from ROOT import kDashed
    newStyle = copy.copy( style )
    newStyle.lineStyle = kDashed
    return newStyle

def openMarkerStyle( style ):
    from ROOT import kDashed
    newStyle = copy.copy( style )
    if newStyle.markerStyle in [20,21,22]:
        newStyle.markerStyle += 4
    return newStyle

#######################
# some default styles #
#######################
import ROOT
linesBW = DrawStyles( ColorStyles([ROOT.kBlack]), LineStyles(), MarkerStyles([0],0.), FillStyles([0]) )
linesColor = DrawStyles( ColorStyles(), LineStyles([ROOT.kSolid]), MarkerStyles([0],0.), FillStyles([0]) )

mcErrorStyle = Style( 1031, lineColor=0, lineWidth=0, markerStyle=0, fillStyle=3144 )
mcErrorStyle.lineColor = 0
mcErrorStyle.lineWidth = 0
blackLine = Style( color=ROOT.kBlack, markerStyle=20 )
redLine = Style( color=ROOT.kRed, markerStyle=20 )
orangeLine = Style( color=ROOT.kOrange+1, markerStyle=20 )
blueLine = Style( color=ROOT.kBlue, markerStyle=20 )
greenLine = Style( color=ROOT.kGreen+1, markerStyle=20 )

lines = [ blackLine, redLine, blueLine, greenLine, orangeLine ]
lineColors = [ ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kGreen+1, ROOT.kOrange+1 ]

