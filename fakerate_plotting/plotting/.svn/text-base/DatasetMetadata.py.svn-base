import re

class DatasetMetadata( object ):
    ## Container class to hold meta data for datasets
    
    def __init__( self, dsid, project, tags ):
        ## Default constructor
        #  @param dsid      dataset ID
        #  @param project   project name, i.e. "mc15_13TeV"
        #  @param tags      list of DatasetTag objects
        self.dsid = int(dsid)
        self.project = project
        # parsing of the project name
        prefix, postfix = project.split( '_' )
        self.year = 2000 + int(prefix[-2:])
        self.isData = 'data' in prefix
        self.isCos = 'cos' == postfix
        self.isComm = 'comm' == postfix
        self.sqrtS = float(postfix[:-3]) if 'eV' in postfix else 0.
        self.tags = tags
        self.derivationType = ''
        self.derivationTag = ''
        self.title = ''
        
    @classmethod
    def fromDatasetName( cls, datasetName ):
        ## Constructor from canonical dataset name
        #  Expects pattern of the form *.mcXX_XXTeV.<title>.<derivation>.<tags>.* for MC
        #  or *.dataXX_XXTeV.<stream>.<derivation>.<tags>.* for data
        #  @param datasetName    dataset name
        s = re.sub('.*data1', 'data1', datasetName )
        s = re.sub('.*mc', 'mc', s )
        result = s.split('.')
        project, dsid, title, derivationType, tagString = result[:5]
        tags = []
        for tagName in tagString.split( '_' ):
            tags.append( DatasetTag(tagName) )
        o = cls(dsid, project, tags)
        o.title = title
        o.derivationType = derivationType
        o.derivationTag=None
        for tag in tagString.split("_"):
          if tag.startswith("p"):
            o.derivationTag=tag
            break
        
        return o
        
    def __str__( self ):
        return 'DatasetMetadata: %d, %s, %s, tags=%s' % ( self.dsid, self.title, self.project, self.tags )
    
    @property
    def canonicalName( self ):
        result = '{}.{:08d}.{}.{}.'.format(self.project, self.dsid, self.title, self.derivationType)
        for tag in self.tags:
            result += tag.name + '_'
        return result.rstrip( '_' )
    
    @property
    def runNumber( self ):
        return self.dsid

class DatasetTag( object ):
    ## Object representing a dataset tag
    
    def __init__( self, name, description='' ):
        self.name = name
        self.description = description
        
    def __hash__( self ):
        ## only hashes the name
        return hash( self.name )
    
    def __eq__( self, other ):
        ## compares only the name
        return self.name == other.name
    
    def __repr__( self ):
        return self.name
    
    def __str__( self ):
        return 'DatasetTag(%s)' % self.name
    
    def inFileName( self, fileName ):
        return self.name in fileName

class Campaign( object ):
    ## Object representing a MC oder data taking campaign defined by a list of valid tags
    
    def __init__( self, name, title, energy, timing, simulationTags=[], hitsMergingTags=[], reconstructionTags=[], mergingTags=[] ):
        self.name = name
        self.title = title
        self.energy = energy
        self.timing = timing
        self.simulationTags = simulationTags
        self.hitsMergingTag = hitsMergingTags
        self.reconstructionTags = reconstructionTags
        self.mergingTags = mergingTags
        
# see https://twiki.cern.ch/twiki/bin/view/AtlasProtected/AtlasProductionGroupMC15a
# see https://twiki.cern.ch/twiki/bin/view/AtlasProtected/AtlasProductionGroupMC15b
# see https://twiki.cern.ch/twiki/bin/view/AtlasProtected/AtlasProductionGroupMC15c

# MC15 simulation tags
s2141 = DatasetTag( 's2141', '19.2.1.6, ATLAS-R2-2015-02-01-00, CalHits, for pre-production single particles' )
s2576 = DatasetTag( 's2576', '19.2.3.3, ATLAS-R2-2015-03-01-00, Frozen Showers and MC12 truth strategy.' )
s2578 = DatasetTag( 's2578', '19.2.3.3, ATLAS-R2-2015-03-01-00 and MC12 truth strategy. Minbias samples only.' )
s2586 = DatasetTag( 's2586', '19.2.3.5, ATLAS-R2-2015-03-01-00 and MC12 truth strategy.' )
s2601 = DatasetTag( 's2601', '19.2.3.6, ATLAS-R2-2015-03-01-00, MC12 truth strategy - low mu configuration only' )
s2650 = DatasetTag( 's2650', '19.2.3.7, ATLAS-R2-2015-03-01-00 and MC12 truth strategy, CalHits/ParticleID, without FS' )
s2608 = DatasetTag( 's2608', '19.2.3.7, ATLAS-R2-2015-03-01-00 and MC12 truth strategy - default' )
s2681 = DatasetTag( 's2681', '19.2.4.5, ATLAS-R2-2015-03-01-00 and MC12 truth strategy' )
s2698 = DatasetTag( 's2698', '19.2.4.9, ATLAS-R2-2015-03-01-00, MC12LLP truth strategy' )
s2697 = DatasetTag( 's2697', '19.2.4.9, ATLAS-R2-2015-03-01-00, LongLived simulator and MC12LLP truth strategy' )
s2694 = DatasetTag( 's2694', '19.2.4.9, ATLAS-R2-2015-03-01-00 and MC12 truth strategy' )
s2726 = DatasetTag( 's2726', '19.2.4.9, ATLAS-R2-2015-03-01-00 and MC15aPlus truth strategy' )
s2802 = DatasetTag( 's2802', 'like s2726, but using QGSP_BERT_VALIDATION instead of FTFP_BERT' )
s2869 = DatasetTag( 's2869', '19.2.4.9, ATLAS-R2-2015-03-01-00, Frozen Showers and MC12 truth strategy (DMG)' )
s2870 = DatasetTag( 's2870', '19.2.4.9, ATLAS-R2-2015-03-15-00, Frozen Showers and MC12 truth strategy) (DMG)' )
s2871 = DatasetTag( 's2871', '19.2.4.9, ATLAS-R2-2015-03-01-19, Frozen Showers and MC12 truth strategy) (DMG)' )
mc15_simulation_tags = [ s2141, s2576, s2578, s2586, s2601, s2650, s2608, s2681, s2698, s2697, s2694, s2726, s2802, s2869, s2870, s2871 ]

# MC15 hits merging tags
s2132 = DatasetTag( 's2132', '19.2.1.2, HITSMerge_tf.py) for Signal' )
s2169 = DatasetTag( 's2169', '19.2.3.5, FilterHit_tf.py) for Minbias' )
s2174 = DatasetTag( 's2174', '19.2.3.5, HITSMerge_tf.py) for Signal' )
s2183 = DatasetTag( 's2183', '19.2.3.7, FilterHit_tf.py) for Signal - default' )
mc15_hits_merging_tags = [ s2132, s2169, s2174, s2183 ]

# MC15a 50ns reconstruction tags
r6630 = DatasetTag( 'r6630', 'ATLAS-R2-2015-03-01-00, tight trigger, 20.1.4.7' )
r6647 = DatasetTag( 'r6647', 'ATLAS-R2-2015-03-01-00, tight trigger, 20.1.4.7, small samples tag (less than 5k)' )
r6767 = DatasetTag( 'r6767', 'ATLAS-R2-2015-03-01-00, tight trigger, 20.1.4.13, MCTruthClassifier fix (like r6630)' )
r6793 = DatasetTag( 'r6793', 'ATLAS-R2-2015-03-01-00, tight trigger, 20.1.4.14 (like r6630)' )
r6802 = DatasetTag( 'r6802', 'ATLAS-R2-2015-03-01-00, tight trigger, small samples tag, 20.1.4.14 (less than 5k)' )
r6828 = DatasetTag( 'r6828', 'ATLAS-R2-2015-03-01-00, tight trigger, small samples tag, 20.1.4.14 (less than 5k)' )
r7050 = DatasetTag( 'r7050', 'ATLAS-R2-2015-03-01-00, tight trigger, 20.1.5.10, without pileup,' )
r6892 = DatasetTag( 'r6892', 'ATLAS-R2-2015-03-01-00, tight trigger, 20.1.5.10, pileup minbias with fixed truth jets (default)' )
mc15a_50ns_reconstruction_tags = [ r6630, r6647, r6767, r6793, r6802, r6828, r7050, r6892 ]

# MC15a 50ns merging tags
r6264 = DatasetTag( 'r6264', 'default' )

# MC15a 25ns reconstruction tags
r6768 = DatasetTag( 'r6768', 'ATLAS-R2-2015-03-01-00, 20.1.4.12, minbias trigger' )
r6765 = DatasetTag( 'r6765', 'ATLAS-R2-2015-03-01-00, 20.1.4.12, tight trigger' )
r6725 = DatasetTag( 'r6725', 'ATLAS-R2-2015-03-01-00, 20.1.4.12, tight trigger (wrong triggerConfig but default is still good)' )
r6771 = DatasetTag( 'r6771', 'ATLAS-R2-2015-03-01-00, 20.1.4.12, tight trigger, saves Calibration Hits' )
r7042 = DatasetTag( 'r7042', 'ATLAS-R2-2015-03-01-00, 20.1.5.10, tight trigger, saving pileup truth' )
r7049 = DatasetTag( 'r7049', 'ATLAS-R2-2015-03-01-00, 20.1.5.10, tight trigger, saves Calibration Hits' )
r7051 = DatasetTag( 'r7051', 'ATLAS-R2-2015-03-01-00, 20.1.5.10, tight trigger, without pileup,' )
r6869 = DatasetTag( 'r6869', 'ATLAS-R2-2015-03-01-00, 20.1.5.10, tight trigger, pileup minbias with fixed truth jets (default)' )
r7509 = DatasetTag( 'r7509', 'ATLAS-R2-2015-03-01-00, 20.1.5.10.1, tight trigger, without pileup' )
mc15a_25ns_reconstruction_tags = [ r6768, r6765, 6725, 6771, r7042, r7049, r7051, r6869, r7509 ]

# MC15 25ns merging tags
r6282 = DatasetTag( 'r6282', 'default' )

# MC15b reconstruction tags
r7267 = DatasetTag( 'r7267', 'ATLAS-R2-2015-03-01-00, 20.1.5.10.1, tight trigger, pileup MB w/ fixed truth jets (same as r6869 except mu profile)' )
r7326 = DatasetTag( 'r7326', 'ATLAS-R2-2015-03-01-00, 20.1.5.10.1, tight trigger, pileup MB w/ fixed truth jets, fix for Frontier DB (default)' )
r7360 = DatasetTag( 'r7360', 'ATLAS-R2-2015-03-01-00, 20.1.5.10.1, tight trigger, pileup MB w/ fixed truth jets, fix for Frontier DB (same as r7326 but for small (1-5k events) samples)' ) 
mc15b_reconstruction_tags = [ r7267, r7326, r7360 ]

# MC15c reconstruction tags
r7725 = DatasetTag( 'r7725', '20.7.5.1, MC15c mu-profile, default' )
r7726 = DatasetTag( 'r7726', '20.7.5.1, MC15b mu-profile, some jobs become very very slow. This issue was fixed in r7773.' )
r7773 = DatasetTag( 'r7773', '20.7.5.1.1, MC15b mu-profile' )
r7728 = DatasetTag( 'r7728', '20.7.5.1, no pileup, DataRunNumber=267599, AODFULL, no slim on track' )
mc15c_reconstruction_tags = [ r7725, r7726, r7728 ]

# MC15c 25ns merging tags
r7676 = DatasetTag( 'r7676', '20.7.5.1, default' )

# MC15 campaigns
mc15a_50ns = Campaign( 'MC15a_50ns', 'MC15a (50ns)', 13, 50, mc15_simulation_tags, mc15_hits_merging_tags, mc15a_50ns_reconstruction_tags, [r6264] )
mc15a_25ns = Campaign( 'MC15a_25ns', 'MC15a (25ns)', 13, 25, mc15_simulation_tags, mc15_hits_merging_tags, mc15a_25ns_reconstruction_tags, [r6282] )
mc15b = Campaign( 'MC15b', 'MC15b', 13, 25, mc15_simulation_tags, mc15_hits_merging_tags, mc15b_reconstruction_tags, [r6282] )
mc15c = Campaign( 'MC15c', 'MC15c', 13, 25, mc15_simulation_tags, mc15_hits_merging_tags, mc15c_reconstruction_tags, [r7676] )

if __name__ == '__main__':
    
    m = DatasetMetadata( 3461713, 'mc15_13TeV', [s2608, s2183, r7326, r6282] )
    print m
    print m.isData
    print m.sqrtS
    print m.year
    
    m = DatasetMetadata.fromDatasetName( 'group.phys-higgs.hhsm_25.data15_13TeV.00280500.physics_Main.D3.f631_m1504_p2524.v10_hist' )
    print m
    print m.isData
    print m.sqrtS
    print m.year
