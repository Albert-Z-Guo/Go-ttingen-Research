'''
Created on Dec 9, 2016

@author: cgrefe
'''
from plotting.Systematics import SystematicsSet
from plotting.Tools import histToGraph
import math

def calculateSystematicsGraph( datasets, xVar, title=None, cut=None, weightExpression=None, luminosity=1., recreate=False, includeOverflowBins=False, forceBinning=False ):
    # # Creates a graph similar to getHistogram. The errors are determined from the combined systematic uncertainties.
    #  Loops over all systematics and determines the respective uncertainties. Uncertainties are combined in quadrature.
    #  @param datasets             list of datasets to consider
    #  @param xVar                 Variable object that defines the variable expresseion used in draw and the binning
    #  @param title                defines the histogram title
    #  @param cut                  Cut object that defines the applied cut
    #  @param weightExpression     weight expression (overrides the default weight expression)
    #  @param luminosity           global scale factor, i.e. integrated luminosity, not applied for data
    #  @param recreate             force recreation of the histogram (don't read it from a possible histogram file)
    #  @param includeOverflowBins  decide if the entries of the overflow bins should be added to the first and last bins, respectively
    #  @return graph
    from ROOT import TGraphAsymmErrors
    # get the total nominal histogram
    nominalHist = None
    systematicsSet = SystematicsSet()
    for dataset in datasets:
        systematicsSet |= dataset.combinedSystematicsSet
        h = dataset.getHistogram( xVar, title, cut, weightExpression, luminosity=luminosity, recreate=recreate, includeOverflowBins=includeOverflowBins, forceBinning=forceBinning )
        if nominalHist:
            nominalHist.Add( h )
        else:
            nominalHist = h
        
    # convert nominal histogram to a graph
    graph = histToGraph( nominalHist, '%s_syst' % nominalHist.GetName(), False )
            
    for systematics in systematicsSet:
        # TODO: instead of simply summing up in quadrature we could include correlation terms (at least within each bin)
        upHist = None
        downHist = None
        # collect all up and down histograms for all datasets
        for dataset in datasets:
            upH = dataset.getHistogram( xVar, title, cut, weightExpression, luminosity=luminosity, recreate=recreate, systematicVariation=systematics.up, includeOverflowBins=includeOverflowBins, forceBinning=forceBinning )
            downH = dataset.getHistogram( xVar, title, cut, weightExpression, luminosity=luminosity, recreate=recreate, systematicVariation=systematics.down, includeOverflowBins=includeOverflowBins, forceBinning=forceBinning )
            if upH:
                if upHist:
                    upHist.Add( upH )
                else:
                    upHist = upH
            if downH:
                if downHist:
                    downHist.Add( downH )
                else:
                    downHist = downH
        for i in xrange( nominalHist.GetNbinsX() ):
            upVal = upHist.GetBinContent( i + 1 )
            downVal = downHist.GetBinContent( i + 1 )
            nominalVal = nominalHist.GetBinContent( i + 1 )
            deltaUp = upVal - nominalVal
            deltaDown = downVal - nominalVal
            # check which value is the down fluctuation
            if deltaDown > deltaUp:
                deltaDown, deltaUp = deltaUp, deltaDown
            # add uncertainty in quadrature to previous uncertainties
            graph.SetPointEYlow( i, math.sqrt( graph.GetErrorYlow( i ) ** 2 + deltaDown ** 2 ) )
            graph.SetPointEYhigh( i, math.sqrt( graph.GetErrorYhigh( i ) ** 2 + deltaUp ** 2 ) )
    return graph

def testSystematicsCalculator():
    from plotting.AtlasStyle import Style
    from plotting.Cut import Cut
    from plotting.Dataset import Dataset
    from plotting.DataMcRatioPlot import DataMcRatioPlot
    from plotting.DoublePlot import DoublePlot
    from plotting.HistogramStore import HistogramStore
    from plotting.Systematics import Systematics
    from plotting.Tools import divideGraphs
    from plotting.Variable import Binning, Variable
    from ROOT import TF1, kViolet, kCyan, kBlack, kDashed
    
    cut = Cut()
    luminosity = 36.2
    
    f_zpeak = TF1('z-peak', 'TMath::Voigt((1./[0])*x-91.2, [1], 2.5)')
    f_zpeak.SetParNames( 'TES', 'TER' )
    f_zpeak.SetParameter( 'TES', 1.0 )
    f_zpeak.SetParameter( 'TER', 10. )
    
    f_cont = TF1('continuum', '[0]*1./x')
    f_cont.SetParNames( 'TES' )
    f_cont.SetParameter( 'TES', 1.0 )
    f_zpeak.SetParameter( 'TER', 10. )
    
    var = Variable( 'dimuon_mass', title='#it{m_{#tau#tau}}', unit='GeV', binning=Binning(20, 50., 150.) )
    
    store = HistogramStore( 'testHistogramStore.root' )
    z_jets = Dataset( 'z_jets', '#it{Z}+jets', style=Style( kCyan ), crossSection=0.0004 )
    continuum = Dataset( 'continuum', 'Others', style=Style( kViolet ), crossSection=0.002 )
    sysLumi = Systematics.scaleSystematics( 'sysLumi', 'Lumi', 1.031, 0.968, 1.0 )
    sysTES = Systematics.treeSystematics( 'sysTES', 'TES', 'tes_up', 'tes_down' )
    sysTER = Systematics.treeSystematics( 'sysTER', 'TER', 'ter_up', 'ter_down' )
    
    mcStat = 500000
    datasets = [continuum,z_jets]
    functions = { z_jets : f_zpeak, continuum : f_cont }
    for dataset in datasets:
        dataset.addSystematics( sysTES )
        dataset.addSystematics( sysLumi )
        h = var.createHistogram( dataset.title )
        f = functions[ dataset ]
        h.FillRandom( f.GetName(), mcStat )
        store.putHistogram( dataset, dataset.nominalSystematics, var, cut, h )
        h.Reset()
        f.SetParameter( 'TES', 1.02 )
        h.FillRandom( f.GetName(), mcStat )
        store.putHistogram( dataset, sysTES.up, var, cut, h )
        h.Reset()
        f.SetParameter( 'TES', 0.98 )
        h.FillRandom( f.GetName(), mcStat )
        store.putHistogram( dataset, sysTES.down, var, cut, h )
        f.SetParameter( 'TES', 1.0 )
    
    z_jets.addSystematics( sysTER )
    h.Reset()
    f_zpeak.SetParameter( 'TER', 13 )
    h.FillRandom( f_zpeak.GetName(), mcStat )
    store.putHistogram( z_jets, sysTER.up, var, cut, h )
    h.Reset()
    f.SetParameter( 'TER', 7 )
    h.FillRandom( f_zpeak.GetName(), mcStat )
    store.putHistogram( z_jets, sysTER.down, var, cut, h )
        
    p = DataMcRatioPlot( 'testPlot', var )
    for dataset in datasets:
        dataset.histogramStore = store
        p.addHistogram( dataset.getHistogram( var, cut=cut, luminosity=luminosity ) )
    systGraph = calculateSystematicsGraph( datasets, var, luminosity=luminosity )
    systGraph.SetTitle( 'Combined Systematics' )
    p.defaultCombinedErrorStyle.apply( systGraph )
    p.setMCSystematicsGraph( systGraph )
    p.draw()
    p.saveAs( 'test.pdf' )
    
    p1 = DoublePlot( 'testPlot1', var, yVariableDown=Variable( 'Ratio', binning=Binning(low=0.8, up=1.2) ) )
    p1.plotDown.yVariable.binning.nDivisions = 205
    nominalHist = None
    systematicsSet = SystematicsSet()
    for dataset in datasets:
        systematicsSet |= dataset.combinedSystematicsSet
        h = dataset.getHistogram( var, cut=cut, luminosity=luminosity )
        if nominalHist:
            nominalHist.Add( h )
        else:
            nominalHist = h
    nominalHist.SetLineColor( kBlack )
    nominalHist.SetTitle( 'Nominal' )
    p1.plotUp.addGraph( systGraph, '2' )
    p1.plotUp.addHistogram( nominalHist )
    rSystGraph = systGraph.Clone()
    rSystGraph.SetTitle()
    p1.plotDown.addGraph( rSystGraph, '2' )
    divideGraphs( rSystGraph, nominalHist )
    lineColor = 1
    for systematics in systematicsSet:
        lineColor += 1
        upHist = None
        downHist = None
        # collect all up and down histograms for all datasets
        for dataset in datasets:
            upH = dataset.getHistogram( var, cut=cut, luminosity=luminosity, systematicVariation=systematics.up )
            downH = dataset.getHistogram( var, cut=cut, luminosity=luminosity, systematicVariation=systematics.down )
            downH.SetLineColor( lineColor )
            downH.SetLineStyle( kDashed )
            if upH:
                if upHist:
                    upHist.Add( upH )
                else:
                    upHist = upH
            if downH:
                if downHist:
                    downHist.Add( downH )
                else:
                    downHist = downH
        upHist.SetLineColor( lineColor )
        upHist.SetTitle( systematics.title )
        downHist.SetLineColor( lineColor )
        downHist.SetLineStyle( kDashed )
        downHist.SetTitle( '' )
        rUpHist = upHist.Clone()
        rUpHist.Divide( nominalHist )
        rUpHist.SetTitle( '' )
        rDownHist = downHist.Clone()
        rDownHist.Divide( nominalHist )
        rDownHist.SetTitle( '' )
        p1.plotUp.addHistogram( upHist )
        p1.plotUp.addHistogram( downHist )
        p1.plotDown.addHistogram( rUpHist )
        p1.plotDown.addHistogram( rDownHist )
    p1.draw()
    
    raw_input()

if __name__ == '__main__':
    testSystematicsCalculator()
