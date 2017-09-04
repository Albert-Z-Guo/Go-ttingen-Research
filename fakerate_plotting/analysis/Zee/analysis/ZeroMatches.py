import os, sys, subprocess, ROOT, logging, datetime
from copy import copy
from argparse import ArgumentParser
from ROOT import TH1D, TF1, TH2D, TF2
from ROOT import kBlack, kBlue, kRed, kGreen, kViolet
from ROOT import kFullCircle, kFullSquare, kFullTriangleUp, kFullTriangleDown, kFullStar

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
    # greeting and setting up output folder
    scriptName = "ZeroMatches"
    dateString = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    outFolder = "plots/{}_{}".format(scriptName, dateString)
    print "Welcome, you are running {}.py".format(scriptName)
    print "Output will be stored in the folder {}".format(outFolder)
    if os.path.exists(outFolder):
	print "ERROR: The folder {} already exists!".format(outFolder)
	sys.exit()
    else:
	try:
	    os.makedirs(outFolder)
	except:
	    print "ERROR: Could not create folder {}!".format(outFolder)
	    sys.exit()

    # run in batch mode
    ROOT.gROOT.SetBatch(True)

    xmlParser = XMLParser()
    xmlParser.parse( xmlPath )

    # add HistogramStore to each process
    for process in xmlParser.physicsProcesses:
	for dataset in process.datasets:
	    dataset.histogramStore = xmlParser.histogramStore
    do_plots = True	# false to only fill HistogramStore

    # setting selection criteria
    sel_base = sel_lep & sel_tag & sel_tau

    # Documenting settings
    if do_plots:
	settingsfile = open( outFolder+'/plot-settings.txt', 'w')
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

    selections = [	sel_base & cut_tau0_jetmatch_q,		sel_base & cut_tau0_jetmatch_g,		sel_base & cut_tau0_zeromatch,		]#sel_base & cut_tau0_zero_or_g,		]
    #selections = [	sel_base & cut_tau0_proper_jetmatch_q,	sel_base & cut_tau0_proper_jetmatch_g,	sel_base & cut_tau0_proper_zeromatch,	]#sel_base & cut_tau0_proper_zero_or_g,	]
    #selections = [	sel_base & cut_tau0_TAT_jetmatch_q,	sel_base & cut_tau0_TAT_jetmatch_g,	sel_base & cut_tau0_TAT_zeromatch,	]#sel_base & cut_tau0_TAT_zero_or_g,	]
    sel_names = [	'Quarks',				'Gluons',				'Unmatched',				]#'Zeros and Gluons',			]
    sel_colors = [	kRed,					kBlue,					kViolet,				]#kViolet,				]
    sel_marker = [	kFullTriangleUp,			kFullTriangleDown,			kFullCircle,				]#kFullStar,				]

    variables = [
	    var_dilepton_pt_vect,			#var_n_taus,					var_n_pileup,
	    var_tau0_width,				#var_tau0_bdt,					var_tau0_ntracks,			var_tau0_pt_equal,
	    #var_tau0_match,				var_tau0_proper_pdgId,				var_tau0_TATmatch,
	    #var_tau0_z0,				var_tau0_d0,					var_tau0_z0_sig,			var_tau0_d0_sig,
	    #var_tau0_z0_wide,				var_tau0_d0_wide,				var_tau0_z0_sintheta,
	    #var_tau0_id_centFracCorrected,		var_tau0_id_etOverPtLeadTrkCorrected,		var_tau0_id_innerTrkAvgDistCorrected,	var_tau0_id_ipSigLeadTrkCorrected,
	    #var_tau0_id_SumPtTrkFracCorrected,		var_tau0_id_ptRatioEflowApproxCorrected,	var_tau0_id_mEflowApproxCorrected,	var_tau0_id_ChPiEMEOverCaloEMECorrected,
	    #var_tau0_id_EMPOverTrkSysPCorrected,	var_tau0_id_dRmaxCorrected,			var_tau0_id_trFlightPathSigCorrected,	var_tau0_id_massTrkSysCorrected,
	    ]

    logBool = [
	    False,	#False,	False,
	    False,	#False,	False,	True,	
	    #False,	False,	False,
	    #False,	False,	False,	False,
	    #False,	False,	False,
	    #False,	False,	False,	False,
	    #True,	False,	False,	False,
	    #False,	False,	True,	False,
	    ]

    #sel_p = [		cut_none,	]
    sel_p = [		cut_none,	cut_1prong, 	cut_3prong, 	cut_1or3prong	]
    sel_p_names = [	'',		' 1 Prong', 	' 3 Prong', 	' 1 or 3 Prong'	]
    sel_p_suffix = [	'',		'_1_Prong', 	'_3_Prong', 	'_1_or_3_Prong'	]

    i_var = -1
    for var in variables:
	i_var += 1
	for p in range(len(sel_p)): # Loop over different Prong cuts
	    # Getting selection histograms
	    # ----------------------------
	    h_mc = []
	    # obtain data and mc histograms for different IDs
	    for process in xmlParser.physicsProcesses:
		if process.name=='Zee':
		    for i in range(len(selections)): # Loop over different selections
			tmp_weight = weight_expression
			tmp_weight = weight_expression+'*SF_dilepton_pt_vect'
			h_id    = process.getHistogram( var, sel_names[i], cut=selections[i]+sel_p[p], luminosity=lumi, weight=tmp_weight )
			h_mc.append( h_id )
			sys.stdout.write('.'); sys.stdout.flush()
	    print "\tgot all{0} histograms for {1}".format( sel_p_names[p], var.name )
	    # Plotting
	    # --------
	    if do_plots:
		bp = BasicPlot( var.name+sel_p_suffix[p], var )
		bp.legendDecorator.textSize = 0.045
		bp.showBinWidthY = False
		for i in range(len(selections)): # Loop over different selections
		    h_mc[i].SetLineColor( sel_colors[i] )
		    h_mc[i].SetMarkerColor( sel_colors[i] )
		    h_mc[i].SetMarkerStyle( sel_marker[i] )
		    bp.addHistogram( h_mc[i], 'E', copy=True )
		bp.titles.append( 'Simulation, #sqrt{{s}} = 13 TeV, #scale[0.5]{{#int}}Ldt = {0:.2f} fb^{{-1}}'.format(lumi/1000.) )
		bp.normalizeByBinWidth = False
		bp.normalized = True
		bp.yVariable = Variable( 'Normalized' )
		#bp.yVariable = Variable( 'Events' )
		bp.logY = logBool[i_var]
		bp.draw()
		bp.saveAsAll( os.path.join( outFolder, bp.title ) )
	print "\t\tDone plotting {0}".format( var.name )
    # --------------------
    print 'everything is done!'
