"""@package DatasetFactory
Helper class to generate Datasets

@author Christian Grefe, Bonn University (christian.grefe@cern.ch)
"""

from plotting.CrossSectionDB import CrossSectionDB
from plotting.Dataset import Dataset
from plotting.DatasetMetadata import DatasetMetadata
from plotting.Tools import string2bool
from plotting.Cut import Cut
import logging, os, re

class DatasetFactory( object ):
    logger = logging.getLogger( __name__ + '.DatasetFactory' )

    def __init__( self ):
        pass
    
    @classmethod
    def datasetsFromXML( cls, element ):
        ## Constructor from an XML element
        #  <Datasets basepath="" treeName="" isData="" isSignal="" weightExpression="">
        #    <Style color="5"/>
        #    <DSIDS> 1234, 4321, 3412 </DSIDS>
        #    <AddCuts>
        #      <Cut> Cut1 </Cut>
        #      <Cut> Cut2 </Cut>
        #    </AddCuts>
        #    <IgnoreCuts>
        #      <Cut> Cut3 </Cut>
        #      <Cut> Cut4 </Cut>
        #    </IgnoreCuts>
        #  </Dataset>
        #  @param element    the XML element
        #  @return a list of Dataset objects
        attributes = element.attrib
        
        datasets = []
        treeName = None
        isData = False
        isSignal = False
        isBSMSignal = False
        weighExpression = None
        if attributes.has_key( 'basePath' ):
            basePath = attributes['basePath']
        else:
            cls.logger.warning( 'datasetsFromXML(): Datasets XML element is missing "basePath" attribute. No datasets created.' )
            return datasets
        if attributes.has_key( 'treeName' ):
            treeName = attributes['treeName']
        if attributes.has_key( 'isData' ):
            isData = string2bool(attributes['isData'])
        if attributes.has_key( 'isSignal' ):
            isSignal = string2bool(attributes['isSignal'])
        if attributes.has_key( 'isBSMSignal' ):
            isBSMSignal = string2bool(attributes['isBSMSignal'])
        if attributes.has_key( 'weightExpression' ):
            weightExpression = attributes['weightExpression']
        style = Style.fromXML( element.find( 'Style' ) ) if element.find( 'Style' ) is not None else None
        addCuts = []
        ignoreCuts = []
        if element.find( 'AddCuts' ):
            for cutElement in element.find( 'AddCuts' ).findall( 'Cut' ):
                addCuts.append( Cut.fromXML( cutElement ) )
        if element.find( 'IgnoreCuts' ):
            for cutElement in element.find( 'IgnoreCuts' ).findall( 'Cut' ):
                ignoreCuts.append( Cut.fromXML( cutElement ) )
        if element.find( 'DSIDS' ) is not None:
            dsids = element.text.split(',')
            for dsid in dsids:
                dataset = cls.datasetFromDSID( basePath, int(dsid), dsid.strip(), treeName  , style, weightExpression )
                dataset.isData = isData
                dataset.isSignal = isSignal
                dataset.isBSMSignal = isBSMSignal
                dataset.addCuts += addCuts
                dataset.ignoreCuts += ignoreCuts 
        else:
            cls.logger.warning( 'datasetsFromXML(): Datasets XML element is missing "DSIDS" element. No datasets created.' )
            return datasets
        return datasets
    
    @classmethod
    def datasetsFromPattern( cls, basePath, pattern, title='', treeName='NOMINAL', style=None, weightExpression=None ):
        import ROOT
        directory = ROOT.gSystem.OpenDirectory( basePath )
        entry = True
        datasets = []
        p = re.compile( pattern )
        while entry:
            entry = ROOT.gSystem.GetDirEntry( directory )
            if p.match( entry ):
                metadata = DatasetMetadata.fromDatasetName( entry )
                if metadata:
                    fileNames = [os.path.join( basePath, entry, '*.root' )]
                    dataset = Dataset( str(metadata.dsid), title, fileNames, treeName, style )
                    dataset.isData = metadata.isData
                    dataset.metadata = metadata
                    if metadata.isData:
                        dataset.isData = True
                    else:
                        dataset.dsid = metadata.dsid
                    datasets.append( dataset )
                else:
                    cls.logger.warning( 'datasetFromPattern(): unable to find metadata for "%s"' % entry )
        ROOT.gSystem.FreeDirectory( directory )
        return datasets
        
    @classmethod
    def datasetFromDSID( cls, basePath, dsid, title='', treeName='NOMINAL', style=None, weightExpression=None ):
        import ROOT
        directory = ROOT.gSystem.OpenDirectory( basePath )
        entry = True
        name = str(dsid)
        dataset = None
        while entry:
            entry = ROOT.gSystem.GetDirEntry( directory )
            if name in entry:
                fileNames = [os.path.join( basePath, entry, '*.root*' )]
                dataset = Dataset( name, title, fileNames, treeName, style, weightExpression )
                dataset.metadata = DatasetMetadata.fromDatasetName( entry )
                if dataset.metadata:
                    dataset.isData = dataset.metadata.isData
                break
        ROOT.gSystem.FreeDirectory( directory )
        if dataset:
            if not dataset.isData:
              dataset.dsid = dsid
            else:
              pass
        else:
            cls.logger.warning( 'datasetFromDSID(): unable to find dataset for "%d" in "%s"' % (dsid,basePath) )
        return dataset

            
if __name__ == '__main__':
    from ROOT import kRed, kCyan
    from plotting.Dataset import PhysicsProcess
    from plotting.AtlasStyle import Style
    
    #logging.root.setLevel( logging.DEBUG )
    
    db = CrossSectionDB.get()
    db.readTextFile( 'plotting/files/susy_crosssections_13TeV.txt' )
    
    basePath = '/eos/atlas/user/c/cgrefe/xTau-NTuples/hh.v14_skimmed/mc15'
    
    print 'Building signal process:'
    signal = PhysicsProcess( 'signal', 'Signal', style=Style( kRed+1 ) )
    for dsid in [ 341124, 341157 ]:
        d = DatasetFactory.datasetFromDSID( basePath, dsid )
        d.isSignal = True
        print d
        print d.metadata
        signal.datasets.append( d )
    print signal
    
    print 'Building ztautau process:'
    ztautau = PhysicsProcess( 'ztautau', 'Z#rightarrow#tau#tau', style=Style( kCyan+1 ) )
    for dsid in range(361510, 361515) + range(361638, 361643):
        d = DatasetFactory.datasetFromDSID( basePath, dsid )
        d.isSignal = True
        print d
        print d.metadata
        ztautau.datasets.append( d )
    print ztautau
