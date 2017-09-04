"""@package plotting
Classes to handle systematic variations

@author Christian Grefe, Bonn University (christian.grefe@cern.ch)
"""
from plotting.Cut import Cut
import hashlib
from plotting.Tools import wrapMethod

class SystematicVariation( object ):
    ## Container class to hold information on systematic variations.
    #  Handles tree, weight and scale based systematics.
    #  In principle it can be a combination of all three.

    def __init__( self, name, title='' ):
        ## Default constructor
        #  @param name                unique identifier (avoid spaces)
        #  @param title               title used in legends (use TLatex)
        self.name = name
        self.title = title if title else self.name
        self.systematics = None
        
    def __hash__( self ):
        ## only hashes the tree name
        return hash( self.name )
    
    def __eq__( self, other ):
        ## compares only the tree name
        return isinstance( other, SystematicVariation ) and self.name == other.name
    
    @property
    def treeName( self ):
        return None
    
    @property
    def weightExpression( self ):
        return ''
    
    @property
    def scale( self ):
        return 1.0
        
    @property
    def isTreeSystematics( self ):
        ## Check if this is a weight systematics
        return False
    
    @property
    def isWeightSystematics( self ):
        ## Check if this is a weight systematics
        return False
    
    @property
    def isScaleSystematics( self ):
        ## Check if this is a scale systematics
        return False
    
    @property
    def isShapeSystematics( self ):
        ## Check if this is a shape systematics
        return self.isTreeSystematics or self.isWeightSystematics
    
    def __str__( self ):
        return 'SystematicVariation(%r)' % self.name
    
    def __repr__( self ):
        return 'SystematicVariation(%r)' % self.name
    
class ScaleSystematicVariation( SystematicVariation ):
    
    def __init__( self, name, title='', scale=1.0 ):
        ## Default constructor
        #  @param name                unique identifier (avoid spaces)
        #  @param title               title used in legends (use TLatex)
        #  @param weightExpression    weight expression applied for this variation
        SystematicVariation.__init__( self, name, title )
        self.scale = scale
    
    def __hash__( self ):
        ## only hashes the scale factor
        return hash( self.scale )
    
    def __eq__( self, other ):
        ## compares only the scale factor
        return isinstance( other, ScaleSystematicVariation ) and self.scale == other.scale
    
    @property
    def md5( self ):
        ## generates an MD5 hash for this object, only hashes the scale factor
        return hashlib.md5( str( self.scale ) ).hexdigest()
    
    @property
    def scale( self ):
        return self.__scale
    
    @scale.setter
    def scale( self, value ):
        self.__scale = value
        
    @property
    def isScaleSystematics( self ):
        return True
    
class TreeSystematicVariation( SystematicVariation ):
    
    def __init__( self, name, title='', treeName=None ):
        ## Default constructor
        #  @param name                unique identifier (avoid spaces)
        #  @param title               title used in legends (use TLatex)
        #  @param weightExpression    weight expression applied for this variation
        SystematicVariation.__init__( self, name, title )
        self.treeName = treeName
    
    def __hash__( self ):
        ## only hashes the tree name
        return hash( self.treeName )
    
    def __eq__( self, other ):
        ## compares only the tree name
        return isinstance( other, TreeSystematicVariation ) and self.treeName == other.treeName
    
    @property
    def md5( self ):
        ## generates an MD5 hash for this object, only hashes the tree name
        return hashlib.md5( self.treeName ).hexdigest() 
        
    @property
    def treeName( self ):
        return self.__treeName
    
    @treeName.setter
    def treeName( self, value ):
        self.__treeName = value
        
    @property
    def isTreeSystematics( self ):
        return True
    
class WeightSystematicVariation( SystematicVariation ):
    
    def __init__( self, name, title='', weightExpression='' ):
        ## Default constructor
        #  @param name                unique identifier (avoid spaces)
        #  @param title               title used in legends (use TLatex)
        #  @param weightExpression    weight expression applied for this variation
        SystematicVariation.__init__( self, name, title )
        self.weightExpression = weightExpression
    
    def __hash__( self ):
        ## only hashes the weight expression
        return hash( self.weightExpression )
    
    def __eq__( self, other ):
        ## compares only the weight expression
        return isinstance( other, WeightSystematicVariation ) and self.weightExpression == other.weightExpression
    
    @property
    def md5( self ):
        ## generates an MD5 hash for this object, only hashes the weight expression
        return hashlib.md5( self.weightExpression ).hexdigest() 
    
    @property
    def weightExpression( self ):
        return self.__weightExpression
    
    @weightExpression.setter
    def weightExpression( self, value ):
        self.__weightExpression = value
        
    @property
    def isWeightSystematics( self ):
        return True
        
class Systematics( object ):
    ## Container class holding upward and downward fluctions as well as a nominal variation
    
    def __init__( self, name, title='', nominal=None, up=None, down=None):
        ## Default constructor
        #  @param name                unique identifier (avoid spaces)
        #  @param title               title used in legends (use TLatex)
        #  @param nominal             the nominal systematics
        #  @param up                  the upward systematics
        #  @param down                the downward systematics
        self.name = name
        self.title = title if title else self.name
        self.nominal = nominal
        self.up = up
        self.down = down
        self.applyOnlyToRegions = []
        self.applyNotToRegions = []
    
    def __hash__( self ):
        ## hashes the combination of nominal, up and down variations
        return hash( ( hash(self.nominal), hash(self.up), hash(self.down) ) )
    
    def __eq__( self, other ):
        ## compares only the weight expression
        return isinstance( other, Systematics ) and self.nominal == other.nominal and self.up == other.up and self.down == other.down
    
    def appliesToRegion( self, cut ):
        ## check if this Systematics should be applied to the given region
        if cut in self.applyNotToRegions or (self.applyOnlyToRegions and not cut in self.applyOnlyToRegions):
            return False
        return True
    
    @property
    def md5( self ):
        ## generates an MD5 hash for this object
        md5 = hashlib.md5()
        md5.update( self.nominal.md5 )
        md5.update( self.up.md5 )
        md5.update( self.down.md5 )
        return md5.hexdigest()
    
    @property
    def up( self ):
        if self._up:
            return self._up
        return self.nominal
    
    @up.setter
    def up( self, systematicVariation ):
        if systematicVariation:
            systematicVariation.systematics = self
        self._up = systematicVariation
    
    @property
    def down( self ):
        if self._down:
            return self._down
        return self.nominal
    
    @down.setter
    def down( self, systematicVariation ):
        if systematicVariation:
            systematicVariation.systematics = self
        self._down = systematicVariation
        
    @classmethod
    def treeSystematics( cls, name, title='', upTreeName=None, downTreeName=None, nominalTreeName=None ):
        ## Automatically create a full set of tree systematics based on the different tree names
        title = title if title else name
        up = None
        if upTreeName:
            up = TreeSystematicVariation( name + '_high', title + ' (up)', upTreeName )
        down = None
        if downTreeName:
            down = TreeSystematicVariation( name + '_low', title + ' (down)', downTreeName )
        nominal = TreeSystematicVariation( name + '_nominal', title + ' (nominal)', nominalTreeName )
        return cls( name, title, nominal, up, down )
    
    @classmethod
    def weightSystematics( cls, name, title='', upWeightExpression=None, downWeightExpression=None, nominalWeightExpression='1' ):
        ## Automatically create a full set of weight systematics based on the different tree names
        title = title if title else name
        up = None
        if upWeightExpression:
            up = WeightSystematicVariation( name + '_high', title + ' (up)', upWeightExpression )
        down = None
        if downWeightExpression:
            down = WeightSystematicVariation( name + '_low', title + ' (down)', downWeightExpression )
        nominal = WeightSystematicVariation( name + '_nominal', title + ' (nominal)', nominalWeightExpression )
        return cls( name, title, nominal, up, down )
    
    @classmethod
    def scaleSystematics( cls, name, title='', upScale=1.0, downScale=1.0, nominalScale=1.0 ):
        ## Automatically create a full set of weight systematics based on the different tree names
        title = title if title else name
        up = ScaleSystematicVariation( name + '_high', title + ' (up)', upScale )
        down = ScaleSystematicVariation( name + '_low', title + ' (down)', downScale )
        nominal = ScaleSystematicVariation( name + '_nominal', title + ' (nominal)', nominalScale )
        return cls( name, title, nominal, up, down )
    
    def __repr__( self ):
        return 'Systematics(%r)' % self.name
    
    def __str__( self ):
        return '%r: title=%s, nominal=%s up=%s, down=%s' % ( self, self.title, self.nominal, self.up, self.down )
    
    @property
    def isOneSided( self ):
        return self.down == self.nominal or self.up == self.nominal
    
    @property
    def isScaleSystematics( self ):
        ## Check if this is a scale systematics
        return self.nominal.isScaleSystematics or self.up.isScaleSystematics or self.down.isScaleSystematics
    
    @property
    def isShapeSystematics( self ):
        ## Check if this is a shape systematics
        return self.nominal.isShapeSystematics or self.up.isShapeSystematics or self.down.isShapeSystematics
    
    @property
    def isTreeSystematics( self ):
        ## Check if this is a tree systematics
        return self.nominal.isTreeSystematics or self.up.isTreeSystematics or self.down.isTreeSystematics
    
    @property
    def isWeightSystematics( self ):
        ## Check if this is a weight systematics
        return self.nominal.isWeightSystematics or self.up.isWeightSystematics or self.down.isWeightSystematics
    
class SystematicsSet( set ):
    ## List of systematics. Required for proper treatment of total weight.
    
    def __init__( self, iterable=None ):
        # Default constructor (copied from set constructor)
        self._data = {}
        if iterable is not None:
            self._update(iterable)
    
    # override add method
    def add( self, obj ):
        ## Adds an Systematic object to the set
        #  Any other object is ignored
        if isinstance( obj, Systematics ):
            set.add( self, obj )
            
    # overide _update method
    def _update( self, iterable ):
        for obj in iterable:
            self.add( obj )
    
    @property
    def scaleSystematics( self ):
        ## gets a list of all scale systematics in this systematics set
        result = SystematicsSet()
        for systematics in self:
            if systematics.isScaleSystematics:
                result.add( systematics )
        return result
    
    @property
    def shapeSystematics( self ):
        ## gets a list of all shape systematics in this systematics set
        result = SystematicsSet()
        for systematics in self:
            if systematics.isShapeSystematics:
                result.add( systematics )
        return result
    
    @property
    def treeSystematics( self ):
        ## gets a list of all tree systematics in this systematics set
        result = SystematicsSet()
        for systematics in self:
            if systematics.isTreeSystematics:
                result.add( systematics )
        return result
    
    @property
    def weightSystematics( self ):
        ## gets a list of all weight systematics in this systematics set
        result = SystematicsSet()
        for systematics in self:
            if systematics.isWeightSystematics:
                result.add( systematics )
        return result
            
    @property 
    def treeNames( self ):
        ## Gets a list of all tree names connected to any systematics in the list
        treeNames = set()
        for systematics in self:
            for variation in [systematics.nominal, systematics.up, systematics.down]:
                if variation.treeName:
                    treeNames.add( variation.treeName )
        return treeNames
    
    def getNominalVariations( self, systematicVariation=None, cut=Cut() ):
        ## Collect all nominal systematic variations. If a systematicVariation is passed that one is used
        #  to replace the corresponding nominal systematics. The cut is used to check wether the systematics
        #  actually apply to the region of interest
        #  @param systematicVariation     SystematicVariation replacing the corresponding nominal
        #  @param cut                     cut defining the region of interest
        #  @return set of relevant variations
        variationsSet = set()
        for systematics in self:
            if systematics.appliesToRegion( cut ):
                variationsSet.add( systematics.nominal )
        # replace the corresponding nominal variation with the concrete variation
        if systematicVariation:
            systematics = systematicVariation.systematics
            if systematics and systematics.appliesToRegion( cut ):
                variationsSet.discard( systematics.nominal )
                variationsSet.add( systematicVariation )

        return variationsSet
        
    def totalWeight( self, systematicVariation=None, cut=Cut() ):
        ## Calculates the total weight expression of all systematics
        #  All systematics use the nominal value. If a systematicVariation is passed that one is used
        #  to replace the corresponding nominal systematics. The cut is used to check wether the systematics
        #  actually apply to the region of interest
        #  @param systematicVariation     SystematicVariation replacing the corresponding nominal
        #  @param cut                     cut defining the region of interest
        #  @return total weight expression
        weightExpression = Cut( '' )
        for variation in self.getNominalVariations( systematicVariation, cut ):
            weightExpression *= variation.weightExpression
        return weightExpression
    
    def totalScaleFactor( self, systematicVariation=None, cut=Cut() ):
        ## Calculates the total scale factor of all systematics
        #  All systematics use the nominal value. If a systematicVariation is passed that one is used
        #  to replace the corresponding nominal systematics. The cut is used to check wether the systematics
        #  actually apply to the region of interest
        #  @param systematicVariation     SystematicVariation replacing the corresponding nominal
        #  @param cut                     cut defining the region of interest
        #  @return total scale factor
        scaleFactor = 1.
        for variation in self.getNominalVariations( systematicVariation, cut ):
            scaleFactor *= variation.scale
        return scaleFactor
    
# replace inherited methods from set that return a new set with methods that return SystematicsSet instead
for methodName in ['__ror__', 'difference_update', '__isub__', 
    'symmetric_difference', '__rsub__', '__and__', '__rand__',
    'intersection', 'difference', '__iand__', 'union', '__ixor__', 
    'symmetric_difference_update', '__or__', 'copy', '__rxor__',
    'intersection_update', '__xor__', '__ior__', '__sub__',]:
    wrapMethod( SystematicsSet, set, methodName )

nominalSystematics = TreeSystematicVariation( 'nominal', 'Nominal', 'NOMINAL' )    
    
if __name__ == '__main__':
    s = SystematicsSet()
    s.add( Systematics.weightSystematics( 'testWeight1', 'Test Weight 1', 'upWeight1', 'downWeight1', 'nominalWeight' ) )
    s.add( Systematics.weightSystematics( 'testWeight2', 'Test Weight 2', 'upWeight2', 'downWeight2', 'nominalWeight' ) )
    s.add( Systematics.treeSystematics( 'testTree', 'Test Tree', 'upTree', 'downTree', 'nominalTree' ) )
    s.add( Systematics.scaleSystematics( 'testScale1', 'Test Scale 1', 1.31, 0.95, 1.08 ) )
    s.add( Systematics.scaleSystematics( 'testScale2', 'Test Scale 2', 1.13, 0.89, 1.02 ) )
    
    for ss in s:
        variation = ss.up
        print variation, '; totalWeightExpression:', s.totalWeight( variation ).cut, '; totalScaleFactor:', s.totalScaleFactor( variation )
