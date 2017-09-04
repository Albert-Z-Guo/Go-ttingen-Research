"""@package Dataset
Helper class to store and retrieve histograms from a ROOT file via canonical paths

@author Christian Grefe, Bonn University (christian.grefe@cern.ch)
"""
import logging, os
from plotting.HistogramStore import HistogramStore

class WorkspaceInputHistogramStore( HistogramStore ):
    ## Class to persist and retrieve histograms based on canonical path names
    #  The expected structure matches those used for the WorkspaceBuilder:
    #  One file per variable with the internal structure "CutName/DatasetName/SystematicVariationHistogram"
    logger = logging.getLogger( __name__ + '.WorkspaceInputHistogramStore' )
    
    def __init__( self ):
        ## Default contructor        
        HistogramStore.__init__( self, None )
        self._fileDict = {}
    
    @classmethod
    def fromXML( cls, element ):
        ## Constructor from an XML element
        #  <MultiFileHistogramStore> </MultiFileHistogramStore>
        #  @param element    the XML element
        #  @return the HistogramStore object
        return cls( element.text.strip() )
    
    def __repr__( self ):
        return 'MultiFileHistogramStore'
    
    def setFile( self, var, fileName ):
        self._fileDict[ var ] = fileName
        
    def _open( self, dataset, systematicVariation, var, cut, mode='read' ):
        ## open the underlying ROOT file depending on the histogram
        #  @param dataset              Dataset object
        #  @param systematicVariation  SystematicVariation object
        #  @param var                  Variable object
        #  @param cut                  Cut object
        #  @return if opening was successful
        if self._fileDict.has_key( var ):
            return self._openFile( self._fileDict[ var ], mode )
        else:
            self.logger.warning( '_open(): no file defined for "%s"' % var )
            return False
        
    def _buildPath( self, dataset, systematicVariation, var, cut ):
        ## helper method to generate canonical path
        #  @param dataset              Dataset object
        #  @param systematicVariation  SystematicVariation object
        #  @param var                  Variable object
        #  @param cut                  Cut object
        #  @return the path and histogram name (tupel of size 2)
        path = os.path.join( cut.name, dataset.name )
        histName = systematicVariation.name
        return path, histName
    
    def _buildPathToSystematics( self, dataset, var, cut ):
        ## helper method to generate canonical path to directory containing systematic variations
        #  @param dataset              Dataset object
        #  @param var                  Variable object
        #  @param cut                  Cut object
        #  @return the path
        path = os.path.join( cut.name, dataset.name )
        return path

def testMultiFileHistogramStore():
    from plotting.Cut import Cut
    from plotting.Dataset import Dataset
    from plotting.Variable import Binning, Variable
    from plotting.Systematics import nominalSystematics as s
    # create some required objects
    v = Variable( 'tau_pt', title='p_{T}^{#tau}', unit='GeV', binning=Binning( 20, -3, 3 ) )
    histogramTitle = 'TestHistogram'
    h = v.createHistogram( 'TestHistogram' )
    h.FillRandom( 'gaus', 1000 )
    c = Cut( 'signal_region', cut = '|tau_eta| < 2.5' )
    d = Dataset( 'test_dataset' )
    # create a histogram store
    storeFileName = 'testMultiFileHistogramStore.root'
    store = WorkspaceInputHistogramStore()
    store.setFile( v, storeFileName )
    # store a histogram
    store.putHistogram( d, s, v, c, h )
    # close the store
    store.close()    
    # retrieve a histogram (automatically opens the file again)
    h = store.getHistogram( d, s, v, c )
    # clean up
    store.close()
    os.remove( storeFileName )
    # check if everything worked and the histograms are actually the same
    return h.GetTitle() == histogramTitle

if __name__ == '__main__':
    print testMultiFileHistogramStore()
        