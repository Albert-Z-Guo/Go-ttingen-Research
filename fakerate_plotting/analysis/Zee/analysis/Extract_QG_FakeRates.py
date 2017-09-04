import os, sys, subprocess, ROOT, logging, math
from copy import copy
from argparse import ArgumentParser
from ROOT import TH1D, TF1, TH2D, TF2
from ROOT import kBlack, kBlue, kRed, kGreen, kGray
from ROOT import kFullCircle, kFullSquare, kFullTriangleUp, kFullTriangleDown

from plotting.PlotDecorator import AtlasTitleDecorator
from plotting.AtlasStyle import Style
from plotting.BasicPlot import BasicPlot
from plotting.DataMcRatioPlot import DataMcRatioPlot
from plotting.Dataset import Dataset, PhysicsProcess, HistogramStore, readPhysicsProcessesFromFile
from plotting.XmlParser import XMLParser
from plotting.Cut import Cut
from plotting.Variable import Binning, Variable, var_Normalized
from plotting.Colours import *

# Add 'ATLAS Internal' to all plots
BasicPlot.defaultTitleDecorator = AtlasTitleDecorator( 'Work In Progress' )
BasicPlot.defaultTitleDecorator.textSize = 0.03
BasicPlot.defaultTitleDecorator.lineGap = 0.01
BasicPlot.defaultLegendDecorator.textSize = 0.03

from analysis.Definitions import *
from analysis.Selections import *
from analysis.Datasets import xmlPath, lumi

import csv

ROOT.gROOT.ProcessLine( "gErrorIgnoreLevel = 3001;")

def printForDebug( FR_1, Q_1, FR_2, Q_2, FR_X, name ):
    print "\n{}\n".format(name)
    print "FR_1:\t{}".format(FR_1)
    print "FR_2:\t{}".format(FR_2)
    print "Q_1:\t{}".format(Q_1)
    print "Q_2:\t{}".format(Q_2)
    print ""
    print "FR_X:\t{}".format(FR_X)
    print ""

def compute_fr_Q( FR_1, Q_1, FR_2, Q_2, name ):
    # the denominator does not need to be re-calculated every time
    denom          =  Q_1[0]  - Q_2[0]
    if denom == 0:
	print "warning: quark denominator Q_1 - Q_2 is 0 in {}!\t(Q_1 = {}, Q_2 = {})".format(name, Q_1[0], Q_2[0] )
	return [0, 0.0]
    # calculating the fake rate
    val_FR_Q       = ( (1-Q_2[0]) * FR_1[0] - (1-Q_1[0]) * FR_2[0] ) / denom
    # calculating derivations
    der_FR_Q__FR_1 =                                  ( 1 - Q_2[0] ) / denom
    der_FR_Q__FR_2 =                                  ( Q_1[0] - 1 ) / denom
    der_FR_Q__Q_1  =            ( Q_2[0] - 1 ) * (FR_1[0] - FR_2[0]) / denom**2
    der_FR_Q__Q_2  =            ( Q_1[0] - 1 ) * (FR_1[0] - FR_2[0]) / denom**2
    # using derivations for error propagation
    err_FR_Q_sq    = 0
    err_FR_Q_sq   += ( der_FR_Q__FR_1 * FR_1[1] )**2 + ( der_FR_Q__FR_2 * FR_2[1] )**2
    err_FR_Q_sq   += ( der_FR_Q__Q_1  *  Q_1[1] )**2 + ( der_FR_Q__Q_2  *  Q_2[1] )**2
    err_FR_Q = math.sqrt( err_FR_Q_sq )
    # returning result
    FR_Q = [ val_FR_Q, err_FR_Q ]
    printForDebug( FR_1, Q_1, FR_2, Q_2, FR_Q, name )
    return FR_Q

def compute_fr_G( FR_1, Q_1, FR_2, Q_2, name ):
    # the denominator does not need to be re-calculated every time
    denom          =  Q_2[0]  - Q_1[0]
    if denom == 0:
	print "warning: gluon denominator Q_2 - Q_1 is 0 in {}!\t(Q_1 = {}, Q_2 = {})".format(name, Q_1[0], Q_2[0] )
	return [0, 0.0]
    # calculating the fake rate
    val_FR_G       = ( Q_2[0] * FR_1[0] - Q_1[0] * FR_2[0] ) / denom
    # calculating derivations
    der_FR_G__FR_1 =                                  Q_2[0] / denom
    der_FR_G__FR_2 =                                - Q_1[0] / denom
    der_FR_G__Q_1  =            Q_2[0] * (FR_1[0] - FR_2[0]) / denom**2
    der_FR_G__Q_2  =            Q_1[0] * (FR_1[0] - FR_2[0]) / denom**2
    # using derivations for error propagation
    err_FR_G_sq    = 0
    err_FR_G_sq   += ( der_FR_G__FR_1 * FR_1[1] )**2 + ( der_FR_G__FR_2 * FR_2[1] )**2
    err_FR_G_sq   += ( der_FR_G__Q_1  *  Q_1[1] )**2 + ( der_FR_G__Q_2  *  Q_2[1] )**2
    err_FR_G = math.sqrt( err_FR_G_sq )
    # returning result
    FR_G = [ val_FR_G, err_FR_G ]
    printForDebug( FR_1, Q_1, FR_2, Q_2, FR_G, name )
    return FR_G

def fr_Q_histogram( h_FR_1, h_Q_1, h_FR_2, h_Q_2, name ):
    h_FR_Q = h_FR_1.Clone(name)
    nBins = h_FR_1.GetNbinsX()
    for i_bin in range(1, nBins+1):
	FR_1 = [ h_FR_1.GetBinContent( i_bin ), h_FR_1.GetBinError( i_bin ) ]
	Q_1  = [  h_Q_1.GetBinContent( i_bin ),  h_Q_1.GetBinError( i_bin ) ]
	FR_2 = [ h_FR_2.GetBinContent( i_bin ), h_FR_2.GetBinError( i_bin ) ]
	Q_2  = [  h_Q_2.GetBinContent( i_bin ),  h_Q_2.GetBinError( i_bin ) ]
	bin_name = "{} Bin {}".format(name, i_bin)
	FR_Q = compute_fr_Q( FR_1, Q_1, FR_2, Q_2, bin_name)
	h_FR_Q.SetBinContent( i_bin, FR_Q[0] )
	h_FR_Q.SetBinError(   i_bin, FR_Q[1] )
    return h_FR_Q

def fr_G_histogram( h_FR_1, h_Q_1, h_FR_2, h_Q_2, name ):
    h_FR_G = h_FR_1.Clone(name)
    nBins = h_FR_1.GetNbinsX()
    for i_bin in range(1, nBins+1):
	FR_1 = [ h_FR_1.GetBinContent( i_bin ), h_FR_1.GetBinError( i_bin ) ]
	Q_1  = [  h_Q_1.GetBinContent( i_bin ),  h_Q_1.GetBinError( i_bin ) ]
	FR_2 = [ h_FR_2.GetBinContent( i_bin ), h_FR_2.GetBinError( i_bin ) ]
	Q_2  = [  h_Q_2.GetBinContent( i_bin ),  h_Q_2.GetBinError( i_bin ) ]
	bin_name = "{} Bin {}".format(name, i_bin)
	FR_G = compute_fr_G( FR_1, Q_1, FR_2, Q_2, bin_name)
	h_FR_G.SetBinContent( i_bin, FR_G[0] )
	h_FR_G.SetBinError(   i_bin, FR_G[1] )
    return h_FR_G

def histFromFile( filename, var=None ):
    #print "trying to open {}".format(filename)
    try:
	f_in	= ROOT.TFile( filename, 'READ' )
    except:
	print "failed to open file {}".format( filename )
	sys.exit(2)
    histoname = 'tau_0_pt'
    if var is not None:
	histoname = var.name
    histo = f_in.Get( histoname )
    print "file is {}".format(filename)
    print "type is {}".format(type(histo))
    histo.SetDirectory(0)
    return histo

def getFR_histo( filename ):
    return histFromFile( filename )

def getXRatio_histo( filename, filename_var ):
    #print "getXRatio_histo::INFO nominal file:   {}".format( filename )
    #print "getXRatio_histo::INFO variation file: {}".format( filename_var )
    h_tmp = histFromFile( filename )
    h_syst = histFromFile( filename_var)
    # adding difference between the two histograms as systematic
    nBins = h_tmp.GetNbinsX()
    for i_bin in range(1, nBins+1):
	value     =  h_tmp.GetBinContent( i_bin )
	variation = h_syst.GetBinContent( i_bin )
	diff = abs( value - variation )
	stat_err  = h_tmp.GetBinError( i_bin )
	tot_err = math.sqrt( diff**2 + stat_err**2 )
	h_tmp.SetBinError( i_bin, tot_err )
    return h_tmp

def get_QG_FRs( file_FR_1, file_FR_2, file_Q1, file_Q2, file_Q1_up, file_Q2_up, name ):
    h_FR_1 = getFR_histo( file_FR_1 )
    h_FR_2 = getFR_histo( file_FR_2 )
    h_Q1 = getXRatio_histo( file_Q1_up, file_Q1 )
    h_Q2 = getXRatio_histo( file_Q2_up, file_Q2 )
    h_FR_Q = fr_Q_histogram( h_FR_1, h_Q1, h_FR_2, h_Q2, "FR_Q"+name )
    h_FR_G = fr_G_histogram( h_FR_1, h_Q1, h_FR_2, h_Q2, "FR_G"+name )
    return [ h_FR_Q, h_FR_G ]

def storeHistogram( var, lumi, histo, filename ):
    # Plotting Data
    # ------------------
    bp = BasicPlot( filename, var )
    bp.addHistogram( histo, 'E', copy=True )
    bp.titles.append( "#sqrt{{s}} = 13 TeV, #scale[0.5]{{#int}}Ldt = {0:.2f} fb^{{-1}}".format(lumi/1000.) )
    bp.yVariable = Variable( "Events" )
    bp.normalizeByBinWidth = False
    bp.showBinWidthY = False
    bp.normalized = False
    bp.logY = False
    bp.yVariable.binning.low = 0 # start y-axis at 0
    bp.yVariable.binning.up = 0.5 # start y-axis at 0
    bp.draw()
    bp.saveAsAll( os.path.join( "plots/", bp.title ) )
    # storing histogram in root file
    # ------------------------------
    from ROOT import TFile, TObject
    rootfile = TFile.Open( 'plots/'+filename+'.root', 'update' )
    if rootfile.IsOpen():
	#print "writing in file {}".format( 'plots/'+filename+'.root' )
        rootfile.cd()
        histogram = histo.Clone( 'h_'+var.name )
        histogram.SetTitle( 'h_'+var.name )
        histogram.Write( 'h_'+var.name, TObject.kOverwrite )
	rootfile.Close()
    else:
	print "Problem opening file {}".format( 'plots/'+filename+'.root' )

def storeComparison( h_fr_data, h_fr_mc, name, up_bound=0.5 ):
    h_fr_mc.SetLineColor( kRed )
    h_fr_mc.SetTitle( "MC Fake Rate" )
    h_fr_data.SetTitle( "Data Fake Rate" )
    dataMc = DataMcPlot( name, var_tau0_pt )
    dataMc.setDataHistogram( h_fr_data )
    dataMc.addHistogram( h_fr_mc, copy=False )
    dataMc.plotUp.yVariable.binning.low = 0 # start y-axis at 0
    dataMc.plotUp.yVariable.binning.up = up_bound # start y-axis at 0
    dataMc.draw()
    dataMc.saveAsAll( os.path.join( "plots/", dataMc.title ) )
    return dataMc

if __name__ == '__main__':
    # run in batch mode
    ROOT.gROOT.SetBatch(True)

    path_prefix = "/afs/desy.de/user/z/zuguo/analysis/plots/"
    path_FR_Q_region = path_prefix + "FakeRates_Syst_cut_q_enriched_20170826-111733/"
    path_FR_G_region = path_prefix + "FakeRates_Syst_cut_g_enriched_20170827-103130/"
    path_FR_Q_MC     = path_prefix + "FakeRates_Syst_cut_MC_q_20170826-111734/"
    path_FR_G_MC     = path_prefix + "FakeRates_Syst_cut_MC_g_20170826-111733/"
    #path_TF_1P       = path_prefix + "2016-09-23_TemplateFit_GRID160722_10000Pulls_1Prong/"
    #path_TF_3P       = path_prefix + "2016-09-23_TemplateFit_GRID160722_10000Pulls_3Prong_max60GeV/"
    path_TF_1P       = path_prefix + "TemplateFit_20170823-171320/"
    path_TF_3P       = path_prefix + "TemplateFit_20170823-171320/"

    #path_FR_Q_region = path_prefix + "2016-09-30_FakeRates_Syst_GRID160722_2bins_with_data_quarks/"
    #path_FR_G_region = path_prefix + "2016-09-30_FakeRates_Syst_GRID160722_2bins_with_data_gluons/"
    #path_FR_Q_MC     = path_prefix + "2016-09-30_FakeRates_Syst_GRID160722_2bins_MC_quarks/"
    #path_FR_G_MC     = path_prefix + "2016-09-30_FakeRates_Syst_GRID160722_2bins_MC_gluons/"
    #path_TF_1P       = path_prefix + "2016-10-01_TemplateFit_GRID160722_10000Pulls_2ptBins/"
    #path_TF_3P       = path_prefix + "2016-10-01_TemplateFit_GRID160722_10000Pulls_2ptBins/"

    l_prong	= [ "_1_Prong", "_3_Prong", ]
    l_tf_path	= [ path_TF_1P, path_TF_3P, ]

    l_id	= [ "_loose", "_medium", "_tight", ]
    
    l_up	= [ 0.4, 0.25, 0.3, 0.12, 0.06, 0.02 ]

    tmp = []

    for i_p in range(len(l_prong)):
	for i_id in range(len(l_id)):
	    i_up = i_p * len(l_id) + i_id
	    # read from FakeRates_Syst directories
	    file_FR_1  = path_FR_Q_region + "tau_0_pt" + l_prong[i_p] + "_Data_allSysts" + l_id[i_id] + ".root"
	    file_FR_2  = path_FR_G_region + "tau_0_pt" + l_prong[i_p] + "_Data_allSysts" + l_id[i_id] + ".root"
	    # read from TemplateFit directories
	    file_Q1    = l_tf_path[i_p] + "tau_0_width_quark-enriched_pt-bin_open" + l_prong[i_p] + "_noID_up_PullPlot_q.root"
	    file_Q2    = l_tf_path[i_p] + "tau_0_width_gluon-enriched_pt-bin_open" + l_prong[i_p] + "_noID_up_PullPlot_q.root"
	    file_Q1_up = l_tf_path[i_p] + "tau_0_width_quark-enriched_pt-bin_open" + l_prong[i_p] + "_noID_nominal_PullPlot_q.root"
	    file_Q2_up = l_tf_path[i_p] + "tau_0_width_gluon-enriched_pt-bin_open" + l_prong[i_p] + "_noID_nominal_PullPlot_q.root"

	    QG_FRs_histos = get_QG_FRs( file_FR_1, file_FR_2, file_Q1, file_Q2, file_Q1_up, file_Q2_up, l_prong[i_p]+l_id[i_id] )
            
            # read from FakeRates_Syst directories
	    # produce data mc comparison plots from the histograms
	    file_FR_Q_MC = path_FR_Q_MC + "tau_0_pt" + l_prong[i_p] + "_MC_allSysts" + l_id[i_id] + ".root"
	    file_FR_G_MC = path_FR_G_MC + "tau_0_pt" + l_prong[i_p] + "_MC_allSysts" + l_id[i_id] + ".root"

	    h_FR_Q_MC = getFR_histo( file_FR_Q_MC )
	    h_FR_G_MC = getFR_histo( file_FR_G_MC )

	    tmp.append( storeComparison( QG_FRs_histos[0], h_FR_Q_MC, "Extract_QG_FakeRates" + l_prong[i_p] + l_id[i_id] + "_compare_Q-FR", l_up[i_up] ) )
	    tmp.append( storeComparison( QG_FRs_histos[1], h_FR_G_MC, "Extract_QG_FakeRates" + l_prong[i_p] + l_id[i_id] + "_compare_G-FR", l_up[i_up] ) )
