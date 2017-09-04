import os, sys, subprocess, ROOT, logging
from copy import copy
from argparse import ArgumentParser
from ROOT import TH1D, TF1, TH2D, TF2
from ROOT import kBlack, kBlue, kRed, kGreen, kGray
from ROOT import kFullCircle, kFullSquare, kFullTriangleUp, kFullTriangleDown

from plotting.PlotDecorator import AtlasTitleDecorator
from plotting.AtlasStyle import Style
from plotting.BasicPlot import BasicPlot
from plotting.RatioPlot import DataMcPlot
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

ROOT.gROOT.ProcessLine( "gErrorIgnoreLevel = 3001;")

if __name__ == '__main__':
    # run in batch mode
    ROOT.gROOT.SetBatch(True)

    xmlParser = XMLParser()
    xmlParser.parse( xmlPath )

    # add HistogramStore to each process
    if True:
	for process in xmlParser.physicsProcesses:
	    for dataset in process.datasets:
		dataset.histogramStore = xmlParser.histogramStore

    # setting selection criteria
    sel_base = sel_lep & sel_tag & sel_tau
    #truth_match = cut_none  # applied only to MC FR from Zee sample (propagates to SF)
    truth_match = cut_tau0_jetmatch_q
    
    # make only Fake Rates of MC samples (e.g. when using a truth match)
    only_mc_fakes = True

    # Documenting settings
    settingsfile = open( 'plots/plot-settings.txt', 'w')
    settingsfile.write("\nluminosity:\n{0}\n".format(lumi))
    settingsfile.write("\nweightExpression:\n{0}\n".format(weight_expression))
    settingsfile.write("\nselection:\n{0}\n".format(sel_base))
    settingsfile.write("\nxmlPath:\n{0}\n".format(xmlPath))
    settingsfile.write("\nrunning over the files:\n")
    for process in xmlParser.physicsProcesses:
	settingsfile.write("\nProcess: {0}\n".format(process.name))
	for ds in process.datasets:
	    for fn in ds.fileNames:
		settingsfile.write("File: {0}\n".format(fn))
    settingsfile.close()

    # Different plot settings
    # -----------------------
    sel_colors = [	kBlack,		kRed,				kBlue,				kGreen				]
    sel_marker = [	kFullCircle,	kFullSquare,			kFullTriangleUp,		kFullTriangleDown		]

    sel_p = [		cut_1or3prong,		cut_1prong, 	cut_3prong	]
    sel_p_names = [	' 1 or 3 Prong',	' 1 Prong', 	' 3 Prong'	]
    sel_p_suffix = [	'_1_or_3_Prong',	'_1_Prong', 	'_3_Prong'	]

    variables = [
	var_tau0_bdt				,
	var_tau0_id_centFracCorrected		,
	var_tau0_id_etOverPtLeadTrkCorrected	,
	var_tau0_id_innerTrkAvgDistCorrected	,
	var_tau0_id_ipSigLeadTrkCorrected	,
	var_tau0_id_SumPtTrkFracCorrected	,
	var_tau0_id_dRmaxCorrected		,
	var_tau0_id_trFlightPathSigCorrected	,
	var_tau0_id_massTrkSysCorrected		,
	var_tau0_id_ChPiEMEOverCaloEMECorrected	,
	var_tau0_id_EMPOverTrkSysPCorrected	,
	var_tau0_id_mEflowApproxCorrected	,
	]

    for var in variables:
	for i_p in range(len(sel_p)): # Loop over different Prong cuts
	    # Getting selection histograms
	    # ----------------------------
	    h_jet = var.createHistogram()
	    h_tau = var.createHistogram()
	    # obtain data and mc histograms for different IDs
	    for process in xmlParser.physicsProcesses:
		#tmp_weight = weight_expression
		tmp_weight = weight_expression+'*SF_dilepton_pt_vect'
		if process.name=='Zee':
		    h_jet    = process.getHistogram( var, 'Jet', cut=sel_tau&sel_p[i_p]&cut_tau0_jetmatch, luminosity=lumi, weight=tmp_weight )
		    sys.stdout.write('.'); sys.stdout.flush()
		if process.name=='Ztautau':
		    h_tau    = process.getHistogram( var, 'Tau', cut=sel_tau&sel_p[i_p]&cut_tau0_taumatch, luminosity=lumi, weight=tmp_weight )
		    sys.stdout.write('.'); sys.stdout.flush()
	    sys.stdout.write(' '); sys.stdout.flush()
	    # Styling
	    # --------
	    h_jet.SetLineColor(   sel_colors[0] )
	    h_jet.SetMarkerColor( sel_colors[0] )
	    h_jet.SetMarkerStyle( sel_marker[0] )
	    h_tau.SetLineColor(   sel_colors[1] )
	    h_tau.SetMarkerColor( sel_colors[1] )
	    h_tau.SetMarkerStyle( sel_marker[1] )
	    # Plotting
	    # --------
	    bp = BasicPlot( 'TauID-studies_'+var.name+sel_p_suffix[i_p], var )
	    bp.showBinWidthY = False
	    bp.addHistogram( h_jet, 'E', copy=True )
	    bp.addHistogram( h_tau, 'E', copy=True )
	    bp.titles.append( '#sqrt{{s}} = 13 TeV, #scale[0.5]{{#int}}Ldt = {0:.2f} fb^{{-1}}'.format(lumi/1000.) )
	    bp.yVariable = Variable( 'normalized' )
	    if var.name == 'SumPtTrkFracCorrected':
		bp.logY = True
	    bp.normalized = True
	    bp.draw()
	    bp.saveAsAll( os.path.join( "plots/", bp.title ) )
	print " done with {0}".format(var.name)
    print 'everything is done!'
