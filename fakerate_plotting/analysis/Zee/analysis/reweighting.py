import os, sys, subprocess, ROOT, logging, datetime
from copy import copy
from argparse import ArgumentParser
from ROOT import TH1D, TF1, TH2D, TF2

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
    # greeting and setting up output folder
    scriptName = "reweighting"
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
    if ( 'reweighted' in xmlPath ):
        print "ERROR: xml path already contains the keyword 'reweighted':"
        print xmlPath
        sys.exit(1)
    xmlParser.parse( xmlPath )

    # add HistogramStore to each process
    for process in xmlParser.physicsProcesses:
	for dataset in process.datasets:
	    dataset.histogramStore = xmlParser.histogramStore

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
    variables = [var_dilepton_pt_vect]

    # plotting data/MC comparisons
    print "Start Plotting:"
    for var in variables:
	# summing up histograms from all processes
        h_mc = var.createHistogram( 'MC' )
	h_data = var.createHistogram( 'data' )
        for process in xmlParser.physicsProcesses:
            if process.isData:
                h_tmp = process.getHistogram( var, process.title, luminosity=lumi, cut=selection ); sys.stdout.write('.'); sys.stdout.flush()
		h_data.Add( h_tmp )
	    elif process.name=='Zee' or process.name=='Zmumu' or process.name=='Ztautau':
		# all MC processes with Z will be reweighted simultaneously
                h_tmp = process.getHistogram( var, process.title, luminosity=lumi, cut=selection, weightExpression=weight_expression); sys.stdout.write('.'); sys.stdout.flush()
		h_mc.Add( h_tmp )
	    else:
		# subtract other backgrounds from data
                h_tmp = process.getHistogram( var, process.title, luminosity=lumi, cut=selection, weightExpression=weight_expression); sys.stdout.write('.'); sys.stdout.flush()
		h_data.Add( h_tmp, -1 )
	print "read all histograms for {0}".format(var.name)
	# calculating scale factor data/MC for the given Variable
	h_sf = var.createHistogram( 'SF' )
	h_sf.Divide( h_data, h_mc, 1, 1, 'B' )
	# plotting the scale factor
	bp_sf = BasicPlot( 'SF_'+var.name, var, Variable('Scale Factor') )
	bp_sf.titles.append( '#sqrt{{s}} = 13 TeV, #scale[0.5]{{#int}}Ldt = {0:.2f} fb^{{-1}}, '.format(lumi/1000.) )
	bp_sf.addHistogram( h_sf, 'E', copy=True )
	bp_sf.draw()
	bp_sf.saveAsAll( os.path.join( outFolder, bp_sf.title ) )
	# storing histogram in root file
	from ROOT import TFile, TObject
	filename = outFolder+'/SF_'+var.name+'.root'
	rootfile = TFile.Open( filename, 'update' )
	if rootfile.IsOpen():
	    print "writing in file {}".format( filename )
	    rootfile.cd()
	    histogram = h_sf.Clone( var.name )
	    histogram.SetTitle( var.name )
	    histogram.Write( var.name, TObject.kOverwrite )
	    rootfile.Close()
	else:
	    print "Problem opening file {}".format( filename )
