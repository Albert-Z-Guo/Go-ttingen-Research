from xml.etree.ElementTree import ElementTree
from plotting.Cut import Cut
from plotting.Dataset import HistogramStore, Dataset, PhysicsProcess
from plotting.Systematics import SystematicsSet, Systematics
from plotting.CrossSectionDB import CrossSectionDB
import logging

class XMLParser( ElementTree ):
    logger = logging.getLogger( __name__ + '.XMLParser' )
    
    def __init__( self ):
        ## Default constructor
        ElementTree( self )
        self.cuts = []
        self.variables = []
        self.datasets = []
        self.physicsProcesses = []
        self.systematicsSet = SystematicsSet()
        self.histogramStore = None
        self.crossSectionDB = None
    
    def parse( self, fileName ):
        ## Read all known elements from an input XML
        #  @param fileName       input XML
        self.logger.debug( 'parse(): reading "%s"' % fileName )
        tree = ElementTree.parse( self, fileName )
        
        # read the CrossSectionDB elements
        for element in tree.findall('CrossSectionDB'):
            self.crossSectionDB = CrossSectionDB.fromXML( element )
        
        # read the HistogramStore elements
        for element in tree.findall('HistogramStore'):
            self.histogramStore = HistogramStore.fromXML( element )
        
        # read all Cut elements
        for element in tree.findall('Cut'):
            self.cuts.append( Cut.fromXML( element ) )
            
        # read all Dataset elements
        for element in tree.findall('Dataset'):
            self.datasets.append( Dataset.fromXML( element ) )
            
        # read all PhysicsProcess elements
        for element in tree.findall('PhysicsProcess'):
            self.physicsProcesses.append( PhysicsProcess.fromXML( element ) )
        
        # read all Systematics elements
        for element in tree.findall('Systematics'):
            self.systematicsSet.add( Systematics.fromXML( element ) )
            
if __name__ == '__main__':
    p = XMLParser()
    p.parse( 'xTauPlots/xTauDatasets.xml' )