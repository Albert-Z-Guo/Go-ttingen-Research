import os, sys, subprocess, ROOT, logging, datetime
from copy import copy
from argparse import ArgumentParser
from ROOT import TH1D, TF1, TH2D, TF2

from plotting.PlotDecorator import AtlasTitleDecorator
from plotting.AtlasStyle import Style
from plotting.BasicPlot import BasicPlot
from plotting.DataMcRatioPlot import DataMcRatioPlot
from plotting.Dataset import Dataset, PhysicsProcess, HistogramStore, readPhysicsProcessesFromFile
from plotting.Systematics import SystematicsSet, Systematics
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
    try:
        if sys.argv[1] == "cut_1prong":
            selection = sel_lep & sel_tag & sel_tau & cut_1prong
            if sys.argv[2] == "cut_tau_id_loose":
                 selection = selection & cut_tau_id_loose
                 scriptName = "dataMC_2015_reweighted_1prong_tau_id_loose"
            elif sys.argv[2] == "cut_tau_id_medium":
                 selection = selection & cut_tau_id_medium
                 scriptName = "dataMC_2015_reweighted_1prong_tau_id_medium"
            elif sys.argv[2] == "cut_tau_id_tight":
                 selection = selection & cut_tau_id_tight
                 scriptName = "dataMC_2015_reweighted_1prong_tau_id_tight"
    except:
        selection = sel_lep & sel_tag & sel_tau
        scriptName = "dataMC_2015_reweighted"

    # greeting and setting up output folder
    dateString = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    outFolder = "plots/{}_{}".format(scriptName, dateString)
    print "Welcome, you are running {}.py".format(scriptName)
    print "Output will be stored in the folder {}".format(outFolder)
    if os.path.exists(outFolder):
        print "ERROR: The folder {} already exists!".format(outFolder)
        sys.exit(1)
    try:
        os.makedirs(outFolder)
    except:
        print "ERROR: Could not create folder {}!".format(outFolder)
        sys.exit(1)

    # setting selection criteria
    selection = sel_lep & sel_tag & sel_tau

    #Dataset.logger.setLevel(10) # 10 = DEBUG
    ROOT.gROOT.SetBatch(True)

    xmlParser = XMLParser()
    xmlParser.parse( xmlPath )

    # add HistogramStore to each process
    if True:
	for process in xmlParser.physicsProcesses:
            for dataset in process.datasets:
                hist_store = HistogramStore("histogramStore/dataMC_2015_reweighted.root")
                dataset.histogramStore = hist_store

    # add Systematics to each dataset
    for process in xmlParser.physicsProcesses:
	if not process.isData:
	    for syst in systSet:
		for dataset in process.datasets:
		    dataset.systematicsSet.add( syst )

    # Documenting settings
    settingsfile = open( outFolder+'/plot-settings.txt', 'w')
    settingsfile.write("\nluminosity:\n{0}\n".format(lumi))
    settingsfile.write("\nweightExpression:\n{0}\n".format(weight_expression))
    settingsfile.write("\nsystSet:\n{0}\n".format(systSet))
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
	    var_n_taus, var_n_pileup, var_n_vx, var_n_jets, var_n_jets_taus,
	    var_dilepton_vis_mass, var_dilepton_pt_vect, var_dilepton_pt_scal, var_dilepton_dr, var_dilepton_deta, var_dilepton_dphi,
	    var_lep0_pt_fine, var_lep0_eta_equal, var_lep0_phi, var_lep1_pt_fine, var_lep1_eta_equal, var_lep1_phi,
	    var_tau0_ntracks, var_tau0_q, var_tau0_pt_fine, var_tau0_eta_equal, var_tau0_phi, var_tau0_match, var_tau0_TATmatch, var_tau0_proper_pdgId,
	    var_weight_ZptSF,
	    var_tau0_pt,
	    ]
    tmp = [] # for a small hack to avoid seg faults when deconstructors are called

    # plotting data/MC comparisons
    print "Start Plotting:"
    for var in variables:
	# getting histograms from all processes
	dataHisto = []
	mcHistos = []
	for process in xmlParser.physicsProcesses:
	    if process.isData:
		h_tmp = process.getHistogram( var, process.title, luminosity=lumi, cut=selection & cut_data_is_2015 ); sys.stdout.write('.'); sys.stdout.flush()
		dataHisto = h_tmp
	    else:
		tmp_weight = weight_expression
	        if process.name=='Zee' or process.name=='Zmumu' or process.name=='Ztautau':
		    tmp_weight = weight_expression+'*SF_dilepton_pt_vect'
		h_tmp = process.getHistogram( var, process.title, luminosity=lumi, cut=selection & cut_mc_is_2015, weightExpression=tmp_weight); sys.stdout.write('.'); sys.stdout.flush()
		mcHistos.append( h_tmp )
	    sys.stdout.write(' '); sys.stdout.flush() # Got all histograms for this process
	# producing a data mc comparison plot from the histograms
	dataMc = DataMcRatioPlot( var.name, var )
	dataMc.setDataHistogram( dataHisto )
	for histo in mcHistos:
	    dataMc.addHistogram( histo, copy=True )
	dataMc.titles.append( '#sqrt{{s}} = 13 TeV, #scale[0.5]{{#int}}Ldt = {0:.2f} fb^{{-1}}'.format(lumi/1000.) )
	dataMc.logY = False
	dataMc.plotUp.legendDecorator.defaultWidth = 0.13
	dataMc.draw()
	dataMc.saveAsAll( os.path.join( outFolder, dataMc.title ) )
	tmp.append(dataMc) # HACK: postpone call of deconstructor to the end of the script to avoid interuption by seg faults
	print "done with plotting of {}".format(var.name)
