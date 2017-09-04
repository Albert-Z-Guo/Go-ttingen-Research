"""@package Dataset
Helper class to store and retrieve histograms from a ROOT file via canonical paths

@author Christian Grefe, Bonn University (christian.grefe@cern.ch)
"""
import logging, os


class HistogramStoreLepHad( object ):
    ## Class to persist and retrieve histograms based on canonical path names
    logger = logging.getLogger( __name__ + '.HistogramStore' )
    
    def __init__( self, fileName ):
        ## Default contructor
        #  @param fileName      the file name of the ROOT file to store the histograms
        from ROOT import TH1
        # ownership is NOT with the TFile ## Currently breaks draw command, don't use!
        #TH1.AddDirectory( False )
        
        self.fileName = fileName
        self.file = None
    
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
        ## close the underlying ROOT file
        if self.file and self.file.IsOpen():
            self.file.Close()
        
    def _open( self ):
        ## open the underlying ROOT file
        #  @return if opening was successful
        if self.file and self.file.IsOpen():
            return True
        from ROOT import TFile
        self.logger.debug( '_open(): opening file at "%s"' % self.fileName )
        self.file = TFile.Open( self.fileName, 'update' )
        if self.file and self.file.IsOpen():
            return True
        self.logger.warning( '_open(): unable to open file at "%s"' % self.fileName )
        return False
        
    def _buildPath( self, channelName, datasetName, systematicName):
        ## helper method to generate canonical path
        #  @param datasetName      the name of the dataset
        #  @param systematicName   the name of the systematic variation
        #  @param var              the variable
        #  @param cut              the cut
        #  @return the path and histogram name (tupel of size 2)
        path = os.path.join( channelName, datasetName )
        histName = systematicName
        #if cut:
        #    histName += '_' + cut.name
        #if prefix:
        #    histName = prefix + '_' + histName
        return path, histName
    
    def getHistogram( self, channelName, datasetName, systematicName, var, cut ):
        ## get a histogram from the store based on how it was created
        #  @param datasetName      the name of the dataset
        #  @param systematicName   the name of the systematic variation
        #  @param var              the variable
        #  @param cut              the cut
        #  @return the histogram
        if not self._open():
            return None
        path, histogramName = self._buildPath( channelName, datasetName, systematicName )
        histPath = os.path.join( path, histogramName )
        h = self.file.Get( histPath )
        if h:
            self.logger.debug( 'getHistogram(): found histogram "%s"' % histPath )
        else:
            self.logger.debug( 'getHistogram(): could not find histogram "%s"' % histPath )
        return h
    
    def putHistogram( self, channelName, datasetName, systematicName, var, cut, histogram ):
        ## update or put a new histogram into store based on how it was created
        #  @param datasetName      the name of the dataset
        #  @param systematicName   the name of the systematic variation
        #  @param var              the variable
        #  @param cut              the cut
        #  @param histogram        the histogram object
        if not self._open():
            return None
        path, histogramName = self._buildPath( channelName, datasetName, systematicName )
        self.logger.debug( 'putHistogram(): storing histogram "%s/%s"' % ( path, histogramName ) )
        self.file.cd()
        from ROOT import TObject, gDirectory
        for directory in path.split( '/' ):
            if not gDirectory.GetDirectory( directory ):
                gDirectory.mkdir( directory )
            gDirectory.cd( directory )
        if 'resopara' in histogramName or 'resoperp' in histogramName:
            if '_low' in histogramName:
                histogramName.replace('_low', '')
            elif '_high' in histogramName:
                return
        histogram.SetTitle( histogramName )
        histogram.Write( histogramName, TObject.kOverwrite )

        
