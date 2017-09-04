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
    # greeting and setting up output folder
    scriptName = "Cutflow"
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

    #Dataset.logger.setLevel(10) # 10 = DEBUG
    ROOT.gROOT.SetBatch(True)

    xmlParser = XMLParser()
    xmlParser.parse( xmlPath )

    # add HistogramStore to each process
    if True:
	for process in xmlParser.physicsProcesses:
	    for dataset in process.datasets:
                hist_store = HistogramStore("histogramStore/Cutflow.root")
                dataset.histogramStore = hist_store

    # Documenting settings
    settingsfile = open( outFolder+'/plot-settings.txt', 'w')
    settingsfile.write("\nluminosity:\n{0}\n".format(lumi))
    settingsfile.write("\nweightExpression:\n{0}\n".format(weight_expression))
    settingsfile.write("\nxmlPath:\n{0}\n".format(xmlPath))
    settingsfile.write("\nrunning over the files:\n")
    for process in xmlParser.physicsProcesses:
	settingsfile.write("\nProcess: {0}\n".format(process.name))
	for ds in process.datasets:
	    for fn in ds.fileNames:
		settingsfile.write("File: {0}\n".format(fn))
    settingsfile.close()
    out_file = open( outFolder+'/Cutflow.txt', 'w', 1 ) 
 
    # listing the variables that should be plotted
    variables = [ var_run_number ]
    tmp = [] # for a small hack to avoid seg faults when deconstructors are called
    base_cuts = [ cut_none,
        cut_lep_pt, cut_trigger, cut_lep_iso, cut_lep_id_medium, cut_lep_OS, cut_di_ele, cut_no_muon,
        cut_tau_pt, cut_tau_eta, cut_tau_olr, cut_tau_q, cut_tau_crack, cut_1or3prong,
        cut_Z_window_nominal
        ]
    regions = [cut_none, cut_quark_enriched, cut_gluon_enriched]
    prongs = [cut_none, cut_1prong, cut_3prong]
    pts = [cut_none, cut_tau_pt_20to30, cut_tau_pt_30to120, cut_tau_pt_20to25, cut_tau_pt_25to30, cut_tau_pt_30to40, cut_tau_pt_40to60, cut_tau_pt_60to120]

    # calculating cutflow
    for var in variables:
        out_file.write("====================================================\n".format(var.name))
        out_file.write("Cutflow calculated over the variable {0}\n".format(var.name))
        out_file.write("====================================================\n".format(var.name))

        for process in xmlParser.physicsProcesses:
	    if process.name=='Zee':
                out_file.write("\nCutflow for {0}\n".format(process.name))
                selection = cut_none
                n_last_selection = 100
                for region in regions:
                    for prong in prongs:
                        for pt in pts:
                            cuts = base_cuts
                            cuts.append( region )
                            cuts.append( prong )
                            cuts.append( pt )
                            for new_cut in cuts:
                                selection = selection & new_cut
                                if process.isData:
                                    h_tmp = process.getHistogram( var, process.title, luminosity=lumi, cut=selection ); sys.stdout.write('.'); sys.stdout.flush()
                                else:
                                    tmp_weight = weight_expression
                                    if process.name=='Zee' or process.name=='Zmumu' or process.name=='Ztautau':
                                        tmp_weight = weight_expression+'*SF_dilepton_pt_vect'
                                    h_tmp = process.getHistogram( var, process.title, luminosity=lumi, cut=selection, weightExpression=tmp_weight); sys.stdout.write('.'); sys.stdout.flush()
                                n_events = h_tmp.Integral()
                                if n_last_selection > 0:
                                    percentage = 100 * ( 1 - ( n_events / n_last_selection ) )
                                else:
                                    percentage = 0
                                n_last_selection = n_events
                                out_file.write("{0} left\t({1:.2f}% lost)\tafter application of: {2}\n".format( n_events, percentage, new_cut.name ))
                                sys.stdout.write(' '); sys.stdout.flush() # Got all histograms for this process

        out_file.write("\n\n")
    print "everything is done!"
