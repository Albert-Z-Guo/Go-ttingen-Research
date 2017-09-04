"""@package Dataset
Helper class to store and retrieve histograms from a ROOT file via canonical paths

@author Christian Grefe, Bonn University (christian.grefe@cern.ch)
"""
import logging, os, uuid

class HistogramStore( object ):
    ## Class to persist and retrieve histograms based on canonical path names
    logger = logging.getLogger( __name__ + '.HistogramStore' )
    
    def __init__( self, fileName ):
        ## Default contructor
        #  @param fileName      the file name of the ROOT file to store the histograms
        #from ROOT import TH1
        # ownership is NOT with the TFile ## Currently breaks draw command, don't use!
        #TH1.AddDirectory( False )
        
        self.fileName = fileName
        self.useHash = False       # use hash values instead of names of objects
        
        self._openFiles = {}       # book keeping for opened files
        self._file = None          # currently used file
    
    @classmethod
    def fromXML( cls, element ):
        ## Constructor from an XML element
        #  <HistogramStore> FileName </HistogramStore>
        #  @param element    the XML element
        #  @return the HistogramStore object
        return cls( element.text.strip() )
    
    def __repr__( self ):
        return 'HistogramStore'
    
    def __str__( self ):
        return '%r(%s)' % (self, self.fileName)
    
    def close( self ):
        ## close the underlying ROOT files
        for fileName, f in self._openFiles.items():
            if f and f.IsOpen():
                f.Close()
            if self._file is f:
                self._file = None
            
    def _openFile( self, fileName, mode ):
        ## open the underlying ROOT file
        if self._file and self._file.IsOpen() and self._file.GetName() == fileName:
            if self._file.ReOpen( mode ) > -1:
                return True
            else:
                return False
        if self._openFiles.has_key( fileName ):
            self._file = self._openFiles[ fileName ]
            if self._file and self._file.IsOpen():
                return True
        from ROOT import TFile
        self._file = TFile.Open( fileName, mode )
        if self._file and self._file.IsOpen():
            self._openFiles[ fileName ] = self._file
            self.logger.debug( '_open(): opened file at "%s"' % fileName )
            return True
        self.logger.debug( '_open(): unable to open file at "%s"' % fileName )
        return False
        
    def _open( self, dataset, systematicVariation, var, cut, mode='read' ):
        ## open the underlying ROOT file depending on the histogram
        #  @param dataset              Dataset object
        #  @param systematicVariation  SystematicVariation object
        #  @param var                  Variable object
        #  @param cut                  Cut object
        #  @return if opening was successful
        return self._openFile( self.fileName, mode )
        
    def _buildPath( self, dataset, systematicVariation, var, cut ):
        ## helper method to generate canonical path
        #  @param dataset              Dataset object
        #  @param systematicVariation  SystematicVariation object
        #  @param var                  Variable object
        #  @param cut                  Cut object
        #  @return the path and histogram name (tupel of size 2)
        if self.useHash:
            path = os.path.join( var.md5, cut.md5, dataset.md5 )
            histName = str( hash( systematicVariation ) )
        else:
            path = os.path.join( var.name, cut.name, dataset.name )
            histName = systematicVariation.name
        return path, histName
    
    def _buildPathToSystematics( self, dataset, var, cut ):
        ## helper method to generate canonical path to directory containing systematic variations
        #  @param dataset              Dataset object
        #  @param var                  Variable object
        #  @param cut                  Cut object
        #  @return the path
        if self.useHash:
            path = os.path.join( var.md5, cut.md5, dataset.md5 )
        else:
            path = os.path.join( var.name, cut.name, dataset.name )
        return path
    
    def getSystematicVariationNames( self, dataset, var, cut ):
        ## determines the list of available SystematicVariation names for given dataset, variable and cut
        #  @param dataset              Dataset object
        #  @param var                  Variable object
        #  @param cut                  Cut object
        #  @return the list of systematic variation names
        result = set()
        if self._open( dataset, None, var, cut ):
            directory = self._file.Get( self._buildPathToSystematics( dataset, var, cut ) )
            for key in directory.GetListOfKeys():
                result.add( key.GetName() )
        return result
    
    def getHistogram( self, dataset, systematicVariation, var, cut ):
        ## get a histogram from the store based on how it was created
        #  @param dataset              Dataset object
        #  @param systematicVariation  SystematicVariation object
        #  @param var                  Variable object
        #  @param cut                  Cut object
        #  @return the histogram
        if not self._open( dataset, systematicVariation, var, cut ):
            return None
        path, histogramName = self._buildPath( dataset, systematicVariation, var, cut )
        histPath = os.path.join( path, histogramName )
        h = self._file.Get( histPath )
        if h:
            h = h.Clone( histogramName + '_%s' % uuid.uuid1() )
            h.SetDirectory( 0 )
            self.logger.debug( 'getHistogram(): found histogram "%s"' % histPath )
        else:
            self.logger.debug( 'getHistogram(): could not find histogram "%s"' % histPath )
        return h
    
    def putHistogram( self, dataset, systematicVariation, var, cut, histogram ):
        ## update or put a new histogram into store based on how it was created
        #  @param dataset              Dataset object
        #  @param systematicVariation  SystematicVariation object
        #  @param var                  Variable object
        #  @param cut                  Cut object
        #  @param histogram            ROOT::TH1 object
        #if not self._open( dataset, systematicVariation, var, cut ):
        #    return None
        if not self._open( dataset, systematicVariation, var, cut, 'update' ):
            self.logger.warning( 'putHistogram(): unable to store histogram, file not open' )
            return None
        path, histogramName = self._buildPath( dataset, systematicVariation, var, cut )
        self.logger.debug( 'putHistogram(): storing histogram "%s/%s"' % ( path, histogramName ) )
        self._file.cd()
        from ROOT import TObject, gDirectory
        for directory in path.split( '/' ):
            if not gDirectory.GetDirectory( directory ):
                gDirectory.mkdir( directory )
            gDirectory.cd( directory )
        histogram = histogram.Clone( histogramName )
        histogram.Write( histogramName, TObject.kOverwrite )

def testHistogramStore():
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
    storeFileName = 'testHistogramStore.root'
    store = HistogramStore( storeFileName )
    # store objects by hash value instead of names
    store.useHash = True
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
    testHistogramStore()
        
