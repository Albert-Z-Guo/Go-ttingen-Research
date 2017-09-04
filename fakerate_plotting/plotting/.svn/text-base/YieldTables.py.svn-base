"""@package plotting
Collection of helper methods to generate cutflow tables.

@author Christian Grefe, Bonn University (christian.grefe@cern.ch)
"""

from math import sqrt

class YieldTableFactory:
    ## Factory class to generate yield tables in various formats
    
    def __init__( self ):
        ## Default constructor
        self.unweighted = False
        self.addFractions = True
        self.addErrors = True
        self.luminosity = 1.
        self.cuts = []
        self.datasets = []
        self.yieldsDict = {}
        self.systematicVariation = None
        self.accumulateCuts = True
        self.totalbg = True
        self.otherBkg = True
        self.sortOrder = None
        self.recreate = False
    
    def calculateYields( self, cuts=None, datasets=None, ):
        ## Calculates the yields for all combinations of cuts and datasets.
        #  This method is called automatically when getting a table (if not called before).
        #  In that case, lists of cuts and datasets need to be defined first by setting the member variables 
        #  @param cuts       list of cuts to be include (rows of table)
        #  @param datasets   list of datasets to be included (comlumns of table)
        if cuts:
            self.cuts = cuts
        if datasets: 
            self.datasets = datasets
        for dataset in self.datasets:
            self.yieldsDict[dataset] = dataset.getCutFlowYields( cuts=self.cuts, luminosity=self.luminosity, ignoreWeights=self.unweighted, systematicVariation=self.systematicVariation, accumulateCuts=self.accumulateCuts, systematicsSet=None, recreate=self.recreate )
    
    def getTWikiTable( self ):
        ## Get the yield table in TWiki format
        self.lineStart = '| '
        self.columnSeparator = ' | '
        self.lineEnd = ' |\n'
        self.titleDecoration = '*'
        self.topDecoration = ''
        self.midDecoration = ''
        self.botDecoration = ''
        return self._generateTable()
    
    def getLatexTable( self ):
        ## Get the yield table in latex format
        self.lineStart = ' '
        self.columnSeparator = ' & '
        self.lineEnd = ' \\\\\n'
        self.titleDecoration = ''
        self.topDecoration = '\\toprule\n'
        self.midDecoration = '\\midrule\n'
        self.botDecoration = '\\bottomrule\n'
        result = self._generateTable()
        #format latex table content
        result=result.replace("#tau#tau","$\\tau\\tau$")
        result=result.replace("\\rightarrow\\tau\\tau","$\\rightarrow\\tau\\tau$")
        result=result.replace("#rightarrow"," ")
        result=result.replace("#","\\")
        result=result.replace("\\Delta","$\\Delta$")
        result=result.replace("%","\%")
        result=result=result.replace("_","\_")
        result=result.replace("arrow","arrow ")
        result=result.replace("+-","$\pm$")

        # add the tabular environment
        addColumn= 2 if (self.totalbg and self.otherBkg) else (1 if (self.totalbg or self.otherBkg) else 0)
        begin = '\\footnotesize\\begin{tabular}{ c |' + (len(self.datasets)+addColumn)*' c' + ' }\n'
        end = '\\end{tabular}\n'
        return begin + result + end
    
    def _generateTable( self ):
        ## Helper method doing all the magic
        if not self.yieldsDict:
            self.calculateYields()
        
        if self.sortOrder:
          dssorted=[]
          for sort in self.sortOrder:
            for ds in self.datasets:
              if str(sort)==ds.name:
                dssorted.append(ds)
          print self.datasets
          self.datasets=dssorted
          print dssorted
        
        result = ''
        totalbg= 0
        othersbg=0
        # dictionary to store baseline selection to calculate fractions
        baselineSelection = {}
        # determine column width
        longestCutTitle = 0
        for cut in self.cuts:
            if len(cut.title) > longestCutTitle:
                longestCutTitle = len(cut.title)
        longestDatasetTitle = 0
        for dataset in self.datasets:
            l = len(dataset.title)
            if l > longestDatasetTitle:
                longestDatasetTitle = l
        # table header
        result += self.topDecoration
        result += self.lineStart + '{:{}}'.format( 'Cut', longestCutTitle )
        for dataset in self.datasets:
          result +=  self.columnSeparator + '{deco}{title:{width}}{deco}'.format( title=dataset.titleLatex, width=longestDatasetTitle, deco=self.titleDecoration )
        if self.totalbg: result +=  self.columnSeparator + '{deco}{title:{width}}{deco}'.format( title='TotBG', width=longestDatasetTitle, deco=self.titleDecoration )
        if self.otherBkg: result +=  self.columnSeparator + '{deco}{title:{width}}{deco}'.format( title='OBG', width=longestDatasetTitle, deco=self.titleDecoration )
        result += self.lineEnd + self.midDecoration
        # main body
        for cut in self.cuts:
            totalbg= 0
            totalbg_unc= 0
            othersbg=0
            result += self.lineStart + '{:<{}}'.format( cut.title, longestCutTitle )
            for dataset in self.datasets:
                value, uncertainty = self.yieldsDict[dataset][cut]
                #value = self.yieldsDict[dataset][cut]
                #uncertainty=0
                if not ( dataset.isSignal or dataset.isData ):
                  totalbg+=value
                  totalbg_unc+=uncertainty*uncertainty
                  if not ("Fake" in dataset.name or "Ztt" in dataset.name):
                    othersbg+=value
                if not baselineSelection.has_key(dataset):
                    baselineSelection[dataset] = value
                entry = '{:.1f}'.format( value )
                if self.addErrors:
                    entry += '+-{:.1f}'.format( uncertainty )
                if self.addFractions:
                    entry += ' ({:.3g}%)'.format( 100 * value / float(baselineSelection[dataset]) )
                result += self.columnSeparator + '{:>{}}'.format( entry, longestDatasetTitle + 2*len(self.titleDecoration) )
            if self.totalbg:
              entry = '{:.1f}'.format( totalbg )
              if self.addErrors:
                entry += '+-{:.1f}'.format( sqrt(totalbg_unc) )
              result += self.columnSeparator + '{:>{}}'.format( entry, longestDatasetTitle + 2*len(self.titleDecoration) )
            if self.otherBkg:
              entry = '{:.1f}'.format( othersbg )
              result += self.columnSeparator + '{:>{}}'.format( entry, longestDatasetTitle + 2*len(self.titleDecoration) )
            result += self.lineEnd
        result += self.botDecoration
        return result
    
if __name__ == '__main__':
    from analysis.hadhad.cuts import cutLVeto, cutOS, cutDR, cutMET, cutMETPhiCentrality
    from plotting.Cut import Cut
    from plotting.Dataset import Dataset
    import logging
    
    basePath = '/afs/cern.ch/user/c/cgrefe/eos_cgrefe/xTau-NTuples/hhsm_25.v8/'
    weightExpression = 'weight_total'
    #logging.root.setLevel( logging.DEBUG )

    # define some cuts    
    cutTau0Selection = Cut( 'Tau0Selection', cut='ditau_tau0_pt > 40 && (ditau_tau0_n_tracks==1 || ditau_tau0_n_tracks==3) && abs(ditau_tau0_q)==1 && ditau_tau0_jet_bdt_medium == 1' )
    cutTau1Selection = Cut( 'Tau1Selection', cut='ditau_tau1_pt > 30 && (ditau_tau1_n_tracks==1 || ditau_tau1_n_tracks==3) && abs(ditau_tau1_q)==1 && ditau_tau1_jet_bdt_medium == 1' )
    cutTauSelection = (cutTau0Selection+cutTau1Selection).setNameTitle( 'TauSelection', 'TauSelection' )

    # we have some cuts that are not simply an addition to the previous cut so we need to add all cuts by hand instead for full control    
    cut1 = (cutTauSelection + 'n_taus_medium==2 && ditau_tau0_jet_bdt_tight+ditau_tau1_jet_bdt_tight>0').setNameTitle( '2 medium, >0 tight', '2 medium, >0 tight' )
    cut2 = cut1.AND( cutLVeto, 'leptonVeto', 'Lepton Veto' )
    cut3 = cut2.AND( cutOS, cutOS.name, cutOS.title )
    cut4 = cut3.AND( cutDR, cutDR.name, cutDR.title )
    cut5 = cut4.AND( cutMET, cutMET.name, cutMET.title )
    cut6 = cut5.AND( cutMETPhiCentrality, cutMETPhiCentrality.name, cutMETPhiCentrality.title )
    # cut7 and cut8 are two different categories
    cut7 = (cut6 + 'selection_vbf').setNameTitle( 'categoryVBF', 'VBF Category' )
    cut8 = (cut6 + 'selection_boosted').setNameTitle( 'categoryBoosted', 'Boosted Category' )
    cuts = [ cutTauSelection, cut1, cut2, cut3, cut4, cut5, cut6, cut7, cut8 ]
    
    # define the datasets we are interested in
    datasets = []
    Sh_Wtaunu_lightFilter = Dataset('361348', 'Sh_Wtaunu_Pt0_70_CVetoBVeto', [basePath + '*.361348.*/*.root'], crossSection=21386., kFactor=0.9082, weightExpression=weightExpression )
    Sh_Wtaunu_lightFilter.scaleFactors['filtEff'] = 0.8914
    Sh_Wtaunu_cFilter = Dataset('3613549', 'Sh_Wtaunu_Pt0_70_CFiltBVet', [basePath + '*.361349.*/*.root'], crossSection=21378., kFactor=0.9082, weightExpression=weightExpression )
    Sh_Wtaunu_cFilter.scaleFactors['filtEff'] = 0.0487
    Sh_Wtaunu_bFilter = Dataset('361350', 'Sh_Wtaunu_Pt0_70_BFilter', [basePath + '*.361350.*/*.root'], crossSection=21386., kFactor=0.9082, weightExpression=weightExpression )
    Sh_Wtaunu_bFilter.scaleFactors['filtEff'] = 0.0597
    Sh_Ztautau_lightFilter = Dataset('361420', 'Sh_Ztautau_Pt0_70_CVetoBVeto', [basePath + '*.361420.*/*.root'], crossSection=2196., kFactor=0.9013, weightExpression=weightExpression )
    Sh_Ztautau_lightFilter.scaleFactors['filtEff'] = 0.7781
    Sh_Ztautau_cFilter = Dataset('361421', 'Sh_Ztautau_Pt0_70_CFiltBVet', [basePath + '*.361421.*/*.root'], crossSection=2204.1, kFactor=0.9013, weightExpression=weightExpression )
    Sh_Ztautau_cFilter.scaleFactors['filtEff'] = 0.1423
    Sh_Ztautau_bFilter = Dataset('361422', 'Sh_Ztautaun_Pt0_70_BFilter', [basePath + '*.361422.*/*.root'], crossSection=2204.7, kFactor=0.9013, weightExpression=weightExpression )
    Sh_Ztautau_bFilter.scaleFactors['filtEff'] = 0.0792
    datasets = [Sh_Ztautau_lightFilter, Sh_Ztautau_cFilter, Sh_Ztautau_bFilter, Sh_Wtaunu_lightFilter, Sh_Wtaunu_cFilter, Sh_Wtaunu_bFilter]
    
    # create the factory and set all parameters
    f = YieldTableFactory()
    f.cuts = cuts
    f.datasets = datasets
    f.luminosity = 3200.
    f.accumulateCuts = False   # here we make sure that cuts are not added sucessively, instead we added them by hand before
    print f.getTWikiTable()
    print f.getLatexTable()
    
    
