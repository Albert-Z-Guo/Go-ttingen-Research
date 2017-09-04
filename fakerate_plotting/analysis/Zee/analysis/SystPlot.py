import os, sys, subprocess, ROOT, logging
from copy import copy
from argparse import ArgumentParser
from ROOT import TH1D, TF1, TH2D, TF2
from ROOT import kBlack, kBlue, kRed, kGreen, kGray, kViolet

from plotting.PlotDecorator import AtlasTitleDecorator
from plotting.AtlasStyle import Style
from plotting.BasicPlot import BasicPlot
from plotting.RatioPlot import DataMcPlot
from plotting.Dataset import Dataset, PhysicsProcess, HistogramStore, readPhysicsProcessesFromFile
from plotting.Systematics import SystematicsSet, Systematics
from plotting.SystematicPlot import SystPlot
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
    # setting selection criteria
    selection = sel_lep & sel_tau & sel_tag
    sel_noWin = sel_lep & sel_tau

    #PhysicsProcess.logger.setLevel(10) # 10 = DEBUG
    ROOT.gROOT.SetBatch(True)

    xmlParser = XMLParser()
    xmlParser.parse( xmlPath )

    # add HistogramStore to each process
    if True:
	for process in xmlParser.physicsProcesses:
	    for dataset in process.datasets:
		dataset.histogramStore = xmlParser.histogramStore

    # add Systematics to each dataset
    weight_expression = "weight_total" # Don't apply SFs if systematics for SFs are used
    for process in xmlParser.physicsProcesses:
	if not process.isData:
	    for dataset in process.datasets:
		for syst in systSet:
		    dataset.systematicsSet.add( syst )

    # Documenting settings
    settingsfile = open( 'plots/plot-settings.txt', 'w')
    settingsfile.write("\nluminosity:\n{0}\n".format(lumi))
    settingsfile.write("\nweightExpression:\n{0}\n".format(weight_expression))
    settingsfile.write("\nselection:\n{0}\n".format(selection))
    settingsfile.write("\nxmlPath:\n{0}\n".format(xmlPath))
    settingsfile.write("\nrunning over the files:\n")
    for process in xmlParser.physicsProcesses:
	settingsfile.write("\nProcess: {0}\n".format(process.name))
	for ds in process.datasets:
	    for fn in ds.fileNames:
		settingsfile.write("File: {0}\n".format(fn))
    settingsfile.close()
    
    # listing the variables that should be plotted
    variables = [
	    #var_tau0_pt_one_bin,
	    var_tau0_pt,
	    #var_tau0_eta,
	    #var_tau0_eta_equal,
	    #var_tau0_q_eta,
	    #var_tau0_phi,
	    #var_n_pileup,
	    #var_tau0_bdt
	    ]
    tmp = [] # used for a small hack to avoid seg faults when deconstructors are called

    #sel_p = [		cut_1or3prong,		]
    sel_p = [		cut_1or3prong,		cut_1prong, 		cut_3prong	]
    sel_p_names = [	' 1 or 3 Prong',	' 1 Prong', 		' 3 Prong'	]
    sel_p_suffix = [	'_1_or_3_Prong',	'_1_Prong', 		'_3_Prong'	]

    out_file = open( 'plots/SystPlot_results.txt', 'w' )
    
    # plotting data/MC comparisons
    print "Start Plotting:"
    for var in variables:
	print "start getting histos for variable {0}".format(var.name)
	out_file.write( "Variable {}\n".format(var.name) )
	for i_p in range(len(sel_p)): # Loop over different Prong cuts
	    print "\nstart getting histos for {0}".format(sel_p_names[i_p])
	    out_file.write( "   {}\n".format(sel_p_names[i_p]) )
	    syst_names = []
	    syst_set = []
	    for syst in systSet:
		syst_names.append( syst.name )
		syst_set.append( syst )
	    syst_names.append( 'Z_window' )
	    for i_sys in range(len(syst_names)):
		out_file.write( "        {}\t".format(syst_names[i_sys]) )
		# getting histograms from all processes
		h_data = var.createHistogram( "Data" )
		h_mc_nom = var.createHistogram( "MC" )
		h_mc_up = var.createHistogram( "MC up" )
		h_mc_down = var.createHistogram( "MC down" )
		for process in xmlParser.physicsProcesses:
		    tmp_weight = weight_expression
		    if process.name=='Zee' or process.name=='Zmumu' or process.name=='Ztautau':
		        tmp_weight = weight_expression+'*SF_dilepton_pt_vect'
		    if process.isData:
			h_tmp = process.getHistogram(		var, process.title,         cut=selection&sel_p[i_p], luminosity=lumi ); sys.stdout.write('.'); sys.stdout.flush()
			h_data.Add( h_tmp, 1 )
		    elif process.name == 'Zee':
			if not syst_names[i_sys] == 'Z_window':
			    h_mc_nom = process.getHistogram(	var, process.title,         cut=selection&sel_p[i_p], weight=tmp_weight, luminosity=lumi, systematicVariation=None                    ); sys.stdout.write('.'); sys.stdout.flush()
			    h_mc_up = process.getHistogram(	var, process.title+"_up",   cut=selection&sel_p[i_p], weight=tmp_weight, luminosity=lumi, systematicVariation=syst_set[i_sys].up      ); sys.stdout.write('.'); sys.stdout.flush()
			    h_mc_down = process.getHistogram(	var, process.title+"_down", cut=selection&sel_p[i_p], weight=tmp_weight, luminosity=lumi, systematicVariation=syst_set[i_sys].down    ); sys.stdout.write('.'); sys.stdout.flush()
			else:
			    sel_tmp = sel_lep & sel_tau
			    # Z mass window systematics
			    h_mc_nom = process.getHistogram(	var, process.title,         cut=sel_noWin&sel_p[i_p]&cut_Z_window_nominal,	weight=tmp_weight, luminosity=lumi, systematicVariation=None	); sys.stdout.write('.'); sys.stdout.flush()
			    h_mc_up = process.getHistogram(	var, process.title+"_up",   cut=sel_noWin&sel_p[i_p]&cut_Z_window_up,		weight=tmp_weight, luminosity=lumi, systematicVariation=None	); sys.stdout.write('.'); sys.stdout.flush()
			    h_mc_down = process.getHistogram(	var, process.title+"_down", cut=sel_noWin&sel_p[i_p]&cut_Z_window_down,		weight=tmp_weight, luminosity=lumi, systematicVariation=None	); sys.stdout.write('.'); sys.stdout.flush()
		    else:
			h_tmp = process.getHistogram(		var, process.title,         cut=selection&sel_p[i_p], weight=tmp_weight, luminosity=lumi, systematicVariation=None ); sys.stdout.write('.'); sys.stdout.flush()
			h_data.Add( h_tmp, -1 )
		    sys.stdout.write(' '); sys.stdout.flush() # Got all histograms for this process
		# print syst-var to file
		nBins = h_mc_nom.GetNbinsX()
		for i_bin in range(nBins):
		    val_nom  = h_mc_nom.GetBinContent(  i_bin+1 )
		    val_up   = h_mc_up.GetBinContent(   i_bin+1 )
		    val_down = h_mc_down.GetBinContent( i_bin+1 )
		    delta_up   = val_up - val_nom 
		    delta_down = val_down - val_nom
		    delta_sym  = (abs(delta_up) + abs(delta_down)) / 2
		    out_file.write( "Bin {}\tNominal {}\t Delta up {}\tDelta down {}\tDelta symmetric {}\t%: {}\n".format(i_bin+1, val_nom, delta_up, delta_down, delta_sym, 100*delta_sym/val_nom) )
		# producing a data mc comparison plot from the histograms
		dataMc = SystPlot( "SystPlot_"+var.name+sel_p_suffix[i_p]+"_"+syst_names[i_sys], var )
		h_mc_nom.SetLineColor(kRed)
		h_mc_up.SetLineColor(kBlue)
		h_mc_down.SetLineColor(kViolet)
		dataMc.setDataHistogram( h_data )
		dataMc.setDownHistogram( h_mc_down )
		dataMc.setUpHistogram( h_mc_up )
		dataMc.setNomHistogram( h_mc_nom )
		dataMc.titles.append( '#sqrt{{s}} = 13 TeV, #scale[0.5]{{#int}}Ldt = {0:.2f} fb^{{-1}}, '.format(lumi/1000.) )
		dataMc.logY = False
		dataMc.plotUp.legendDecorator.defaultWidth = 0.13
		dataMc.draw()
		dataMc.saveAsAll( os.path.join( "plots/", dataMc.title ) )
		tmp.append(dataMc) # HACK: postpone call of deconstructor to the end of the script to avoid interuption by seg faults
		print "done with plotting of {} for systematic {}".format(var.name, syst_names[i_sys])
    out_file.close()
