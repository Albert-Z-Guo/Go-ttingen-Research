"""@package DatasetFactory
Helper class to read and store cross section information

@author Christian Grefe, Bonn University (christian.grefe@cern.ch)
"""

from plotting.Singleton import Singleton
import csv, logging

class CrossSectionDBEntry( object ):
    ## Container class to encapsulate cross section information
    
    def __init__( self, dsid, name=None, crossSection=0., branchingRatio=1., efficiency=1., kFactor=1., uncertainty=0. ):
        ## Constructor, units should be in pb
        #  @param dsid            dataset ID
        #  @param name            name of the dataset
        #  @param crossSection    cross section in pb
        #  @param branchingRatio  branching ratio of this sample
        #  @param efficiency      filter efficiency
        #  @param kFactor         correction factor to cross section
        #  @param uncertainty     relative uncertainty on cross section
        self.dsid = dsid
        self.name = name if name is not None else str(dsid)
        self.crossSection = crossSection
        self.branchingRatio = branchingRatio
        self.efficiency = efficiency
        self.kFactor = kFactor
        self.uncertainty = uncertainty
    
    @property
    def effectiveCrossSection( self ):
        # Calculates the effective cross section in pb taking into account
        # branching ratio, efficiency and higher order corrections
        return self.crossSection * self.branchingRatio * self.efficiency * self.kFactor
    
    def __str__( self ):
        return 'CrossSectionDBEntry(%r): %r, XS=%r pb, BR=%r, eff=%r, kFactor=%r' % ( self.dsid, self.name, self.crossSection, self.branchingRatio, self.efficiency, self.kFactor )
            
    @classmethod
    def fromDict( cls, d ):
        ## Constructor from dictionary
        #  @param d       input dictionary, needs to contain all relevant fields
        entry = cls( int(d['dsid']), d['name'], float(d['crossSection']), efficiency=float(d['efficiency']), kFactor=float(d['kFactor']) )
        if d.has_key( 'branchingRatio' ):
            entry.uncertainty = float( d['branchingRatio'] )
        if d.has_key( 'uncertainty' ):
            entry.uncertainty = float( d['uncertainty'] )
        return entry

@Singleton
class CrossSectionDB( dict ):
    ## Dictionary class handling cross section book keeping
    logger = logging.getLogger( __name__ + '.CrossSectionDB' )
    columnsPMG = ['dsid', 'name', 'crossSection', 'branchingRatio', 'efficiency', 'hoCrossSection', 'kFactor', 'hoSampleCrossSection']
    columnsSUSY = ['dsid', 'name', 'crossSection', 'kFactor', 'efficiency', 'uncertainty']
    

    def __init__( self ):
        ## Constructor
        #  Reads an input text file and add its content to this DB
        #  Uses the CrossSectionDBEntry.fromDict, where columns are assumed to be tab-seperated 
        #  @param fileName      input file name
        pass
    
    @classmethod
    def fromXML( cls, element ):
        ## Constructor from an XML element
        #  <CrossSectionDB>
        #    <File> File1 </File>
        #    <File> File2 </File>
        #  </Dataset>
        #  @param element    the XML element
        #  @return the CrossSectionDB object
        db = CrossSectionDB.get()
        for fileElement in element.findall( 'File' ):
            db.readTextFile( fileElement.text.strip() )
        return db
    
    def add( self, dsid, name, crossSection, branchingRatio=1., efficiency=1., kFactor=1., uncertainty=1. ):
        ## Adds a new entry
        #  @param dsid            dataset ID
        #  @param name            name of the dataset
        #  @param crossSection    cross section
        #  @param branchingRatio  branching ratio of this sample
        #  @param efficiency      filter efficiency
        #  @param kFactor         correction factor to cross section
        #  @param uncertainty     relative uncertainty on cross section
        self[dsid] = CrossSectionDBEntry( dsid, name, crossSection, branchingRatio, efficiency, kFactor, uncertainty )
    
    def readTextFile( self, fileName ):
        ## Read an input text file and add its content to this DB
        #  Uses the CrossSectionDBEntry.fromDict, where columns are assumed to be tab-seperated 
        #  @param fileName      input file name
        self.logger.info( 'readTextFile(): reading cross-sections from %r' % ( fileName ) )
        f = open( fileName, 'r' )
        import string
        # determine the format of the input file
        if 'id/I:name/C:xsec/F:kfac/F:eff/F:relunc/F' in f.readline():
            columnNames = self.columnsSUSY
            self.logger.info( 'readTextFile(): using SUSY XS column scheme' )
        else:
            columnNames = self.columnsPMG
            self.logger.info( 'readTextFile(): using PMG XS column scheme' )
        reader = csv.DictReader( (string.join(row.split(), ' ') for row in f if (not row.startswith( '#' ) and not row.startswith( 'id' ))), columnNames, delimiter=' ' )
        n = 0
        for row in reader:
            if not row['dsid']:
                continue
            try:
                entry = CrossSectionDBEntry.fromDict( row )
            except (ValueError, TypeError):
                self.logger.warning( 'readTextFile(): unable to convert "%s"' % row  )
                continue
            self.logger.debug( 'readTextFile(): found %s' % ( entry ) )
            self[entry.dsid] = entry
            n += 1
        self.logger.info( 'readTextFile(): successfully read %d cross-section entries' % ( n ) )
        
         
if __name__ == "__main__":
    #logging.root.setLevel( logging.DEBUG )
    db = CrossSectionDB.get()
    #db.readTextFile( 'data/SUSY_XS/susy_crosssections_13TeV.txt' )
    db.readTextFile( 'data/PMG_XS/CrossSectionData.txt' )
    
    print db[341001]
    print 'Effective XS for DSID 341001:', db[341001].effectiveCrossSection, 'pb'
    print db[341157]
    print 'Effective XS for DSID 341157:', db[341157].effectiveCrossSection, 'pb'
    