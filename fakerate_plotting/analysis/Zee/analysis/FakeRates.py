import os, sys, subprocess, ROOT, logging
from copy import copy
from argparse import ArgumentParser
from ROOT import TH1D, TF1, TH2D, TF2
from ROOT import kBlack, kBlue, kRed, kGreen, kGray, kViolet
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

ROOT.gROOT.ProcessLine( "gErrorIgnoreLevel = 3001;")

if __name__ == '__main__':
    # run in batch mode
    ROOT.gROOT.SetBatch(True)

    xmlParser = XMLParser()
    xmlParser.parse( xmlPath )

    # add HistogramStore to each process
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
    sel_id = [		sel_base,	sel_base&cut_tau_id_loose,	sel_base&cut_tau_id_medium,	sel_base&cut_tau_id_tight	]
    sel_id_names = [	'No tau ID',	'Loose ID',			'Medium ID',			'Tight ID'			]
    sel_colors = [	kBlack,		kRed,				kViolet,			kBlue				]
    sel_marker = [	kFullCircle,	kFullSquare,			kFullTriangleUp,		kFullTriangleDown		]

    sel_p = [		cut_1or3prong,		cut_1prong, 	cut_3prong	]
    sel_p_names = [	' 1 or 3 Prong',	' 1 Prong', 	' 3 Prong'	]
    sel_p_suffix = [	'_1_or_3_Prong',	'_1_Prong', 	'_3_Prong'	]

    if not only_mc_fakes:
	name_set = [	'_data',	'_mc'		]
	name_type = [	'_Sel',		'_FR',		'_SF'		]
	id_range = [	4,		3,		3		]
	normByWidth = [	True,		False,		False		]
	logScale = [	True,		False,		False		]
	yLabel = [	'Events',	'Fake Rate',	'Scale Factor'	]
    else:
	name_set = [	'_mc'		]
	name_type = [	'_Sel',		'_FR'		]
	id_range = [	4,		3		]
	normByWidth = [	True,		False		]
	logScale = [	True,		False		]
	yLabel = [	'Events',	'Fake Rate'	]

    variables = [var_tau0_pt, var_tau0_eta	]#, var_tau0_eta_equal, var_tau0_q_eta, var_tau0_phi, var_n_pileup, var_tau0_bdt]

    for var in variables:
	print "start getting histos for variable {0}".format(var.name)
	for p in range(len(sel_p)): # Loop over different Prong cuts
	    # Getting selection histograms
	    # ----------------------------
	    h_mc = []
	    h_data = []
	    # obtain data and mc histograms for different IDs
	    for process in xmlParser.physicsProcesses:
		for i in range(len(sel_id)): # Loop over different IDs
		    if process.name=='Zee':
			#tmp_weight = weight_expression
			tmp_weight = weight_expression+'*SF_dilepton_pt_vect'
			h_id    = process.getHistogram( var, sel_id_names[i]+sel_p_names[p], cut=sel_id[i]&sel_p[p]&truth_match, luminosity=lumi, weightExpression=tmp_weight )
			h_mc.append( h_id )
			sys.stdout.write('.'); sys.stdout.flush()
		    if not only_mc_fakes and process.isData:
			h_id    = process.getHistogram( var, sel_id_names[i]+sel_p_names[p], cut=sel_id[i]&sel_p[p], luminosity=lumi )
			h_data.append( h_id )
			sys.stdout.write('.'); sys.stdout.flush()
	    # subtract background from data histograms for different IDs
	    if not only_mc_fakes:
		for process in xmlParser.physicsProcesses:
		    if not process.isData and not process.name=='Zee':
			for i in range(len(sel_id)): # Loop over different IDs
			    tmp_weight = weight_expression
			    if process.name=='Zee' or process.name=='Zmumu' or process.name=='Ztautau':
				#tmp_weight = weight_expression
				tmp_weight = weight_expression+'*SF_dilepton_pt_vect'
			    h_bkg    = process.getHistogram( var, sel_id_names[i]+sel_p_names[p], cut=sel_id[i]&sel_p[p], luminosity=lumi, weightExpression=tmp_weight )
			    h_data[i].Add( h_bkg, -1 )
			    sys.stdout.write('.'); sys.stdout.flush()
	    print "\tgot all{0} histograms for {1}".format( sel_p_names[p], var.name )
	    # Fake Rate and Scale Factor calculation
	    # --------------------------------------
	    h_mc_fr = []
	    h_data_fr = []
	    h_sf = []
	    for i in range(1,len(sel_id)): # mc FRs: Loop over different IDs
		h_tmp = var.createHistogram( sel_id_names[i] )
		h_tmp.Divide( h_mc[i], h_mc[0], 1, 1, 'B' )
		h_mc_fr.append( h_tmp )
	    if not only_mc_fakes:
		for i in range(1,len(sel_id)): # data FRs: Loop over different IDs
		    h_tmp = var.createHistogram( sel_id_names[i] )
		    h_tmp.Divide( h_data[i], h_data[0], 1, 1, 'B' )
		    h_data_fr.append( h_tmp )
	    if not only_mc_fakes:
		for i in range(len(sel_id)-1): # SFs: Loop over FRs for different IDs
		    h_tmp = var.createHistogram( sel_id_names[i+1] )
		    h_tmp.Divide( h_data_fr[i], h_mc_fr[i]) # Do NOT use binomial errors for scale factors!
		    h_sf.append( h_tmp )
	    if not only_mc_fakes:
		histo_set = [	h_data,		h_mc,		h_data_fr,	h_mc_fr,	h_sf	]
	    else:
		histo_set = [	h_mc,		h_mc_fr		]
	    # Plotting Fake Rates and Scale Factors
	    # -------------------------------------
	    for i_type in range(len(name_type)): # Selection, FR or SF plot?
		if name_type[i_type] == '_SF':
		    n_sets = 1
		else:
		    n_sets = len(name_set)
		for i_set in range(n_sets): # data or mc plot ?
		    if i_type == 2: # SF plots have a different naming convention
			bp = BasicPlot( 'FakeRate_'+var.name+name_type[i_type]+sel_p_suffix[p], var )
		    else:
			bp = BasicPlot( 'FakeRate_'+var.name+name_type[i_type]+sel_p_suffix[p]+name_set[i_set], var )
		    bp.showBinWidthY = False
		    if name_type[i_type] == '_SF': # Draw a line at 1 for SF plots
			h_tmp = var.createHistogram( '' )
			for i_bin in range( h_tmp.GetNbinsX() + 2 ):
			    h_tmp.SetBinContent( i_bin, 1 )
			    h_tmp.SetBinError( i_bin, 0 )
			h_tmp.SetLineColor( kGray )
			bp.addHistogram( h_tmp, 'E' )
		    for i in range(id_range[i_type]): # Loop over different IDs
			histo_set[len(name_set)*i_type+i_set][i].SetLineColor( sel_colors[i] )
			histo_set[len(name_set)*i_type+i_set][i].SetMarkerColor( sel_colors[i] )
			histo_set[len(name_set)*i_type+i_set][i].SetMarkerStyle( sel_marker[i] )
			bp.addHistogram( histo_set[len(name_set)*i_type+i_set][i], 'E', copy=True )
		    bp.titles.append( '#sqrt{{s}} = 13 TeV, #scale[0.5]{{#int}}Ldt = {0:.2f} fb^{{-1}}'.format(lumi/1000.) )
		    bp.legendDecorator.textSize = 0.045
		    bp.normalizeByBinWidth = normByWidth[i_type]
		    bp.yVariable = Variable( yLabel[i_type] )
		    bp.logY = logScale[i_type]
		    bp.normalized = False
		    if i_type == 1 or i_type == 2: # For FR and SF plots start y-axis at 0
			bp.yVariable.binning.low = 0
		    bp.draw()
		    bp.saveAsAll( os.path.join( "plots/", bp.title ) )
    # --------------------
    print 'everything is done!'
