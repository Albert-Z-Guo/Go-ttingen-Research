'''
Created on Dec 16, 2016

@author: cgrefe
'''
from plotting.Variable import Variable, Binning
from plotting.Cut import Cut
import logging

class CombinedVariable( Variable ):
    ## Class to store a list of variables.
    #  When used to create a histogram, the resulting histogram is the sum of all individual histograms
    logger = logging.getLogger( __name__ + '.CombinedVariable' )

    def __init__( self, name, title=None, unit='', binning=Binning(), defaultCut=Cut(), variables=[] ):
        ## Default constructor
        #  @param name        name
        #  @param title       title used for example in axis lables (default uses name)
        #  @param unit        name of the unit
        #  @param binning     binning object
        #  @param defaultCut  cut that should be applied whenever this variable is plotted
        Variable.__init__( self, name, None, title, unit, binning, defaultCut )
        self.variables = variables
        
    def createHistogramFromTree( self, tree, title='', cut=None, weight=None, drawOption='', style=None ):
        ## Create a histogram from a TTree
        #  Returns the sum of histogram of all contained variables
        #  @ param tree             TTree object used to create the histogram
        #  @ param title            the histogram title
        #  @ param cut              Cut object (optional)
        #  @ param weight           weight expression (optional)
        #  @ param drawOption       draw option used
        #  @ return the generated histogram
        cut = cut if cut else Cut()
        cut += self.defaultCut
        hist = self.createHistogram( title, 'prof' in drawOption )
        if not hist.GetSumw2N():
            hist.Sumw2()
        for variable in self.variables:
            h = variable.createHistogramFromTree( tree, title, cut, weight, drawOption )
            if h:
                hist.Add( h )
        if hist and style:
            style.apply( hist )
        return hist
    
if __name__ == '__main__':
    from plotting.BasicPlot import BasicPlot
    from plotting.AtlasStyle import blackLine, redLine, blueLine
    from ROOT import TFile, TTree, TRandom3
    from array import array
    rndm = TRandom3()
    pT0 = array( 'f', [0] )
    pT1 = array( 'f', [0] )
    t = TTree( 'tree', 'tree' )
    t.Branch( 'tau_0_pt', pT0, 'tau_0_pt/F' )
    t.Branch( 'tau_1_pt', pT1, 'tau_1_pt/F' )
    sumOfWeights = 0.
    for entry in xrange( 10000 ):
        pT0[0] = rndm.Gaus( 60, 15 )
        pT1[0] = rndm.Gaus( 50, 10 )
        t.Fill()
    
    binning = Binning( 50, 0, 100 )
    var_tau_0_pt = Variable( 'tau_0_pt', title='p_{T}(#tau_{0})', unit='GeV', binning=binning )
    var_tau_1_pt = Variable( 'tau_1_pt', title='p_{T}(#tau_{1})', unit='GeV', binning=binning )
    var_tau_pt = CombinedVariable( 'tau_0_pt', 'p_{T}(#tau)', 'GeV', binning, variables=[var_tau_0_pt, var_tau_1_pt] )

    p = BasicPlot( 'Test Plot', var_tau_pt )
    p.addHistogram( var_tau_pt.createHistogramFromTree( t, 'Any Tau', style=blackLine ), 'E0' )
    p.addHistogram( var_tau_0_pt.createHistogramFromTree( t, 'Leading Tau', style=redLine ), 'E0' )
    p.addHistogram( var_tau_1_pt.createHistogramFromTree( t, 'Sub-Leading Tau', style=blueLine ), 'E0' )
    p.draw()
     
    raw_input( 'Continue?' )
    