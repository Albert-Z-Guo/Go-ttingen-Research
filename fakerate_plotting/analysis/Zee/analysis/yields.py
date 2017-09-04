import os, sys, subprocess, ROOT, logging, math
from copy import copy
from argparse import ArgumentParser
from ROOT import TH1D, TF1, TH2D, TF2

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
    # setting selection criteria
    sel_base = sel_lep & sel_tag & sel_tau

    #Dataset.logger.setLevel(10) # 10 = DEBUG
    ROOT.gROOT.SetBatch(True)

    xmlParser = XMLParser()
    xmlParser.parse( xmlPath )

    # add HistogramStore to each process
    if True:
	for process in xmlParser.physicsProcesses:
	    for dataset in process.datasets:
		dataset.histogramStore = xmlParser.histogramStore

    # Documenting settings
    settingsfile = open( 'plots/plot-settings.txt', 'w')
    settingsfile.write("\nluminosity:\n{0}\n".format(lumi))
    settingsfile.write("\nweightExpression:\n{0}\n".format(weight_expression))
    settingsfile.write("\nbase selection:\n{0}\n".format(sel_base))
    settingsfile.write("\nxmlPath:\n{0}\n".format(xmlPath))
    settingsfile.write("\nrunning over the files:\n")
    for process in xmlParser.physicsProcesses:
	settingsfile.write("\nProcess: {0}\n".format(process.name))
	for ds in process.datasets:
	    for fn in ds.fileNames:
		settingsfile.write("File: {0}\n".format(fn))
    settingsfile.close()

    selections = [
	    None,
	    cut_none,
	    cut_even,
	    cut_odd,
	    cut_tau_id_loose,
	    cut_tau_id_medium,
	    cut_tau_id_tight,
	    ]

    lumi_weighted = [
	    True,
	    False
	    ]

    # printing yields from dataset
    yieldsfile = open( 'plots/yields.txt', 'w')
    for weighted in lumi_weighted:
	if weighted:
	    print "Weighted Yields\n----------------\n"
	    yieldsfile.write( "Weighted Yields\n----------------\n\n" )
	else:
	    print "Unweighted Yields\n------------------\n"
	    yieldsfile.write( "Unweighted Yields\n------------------\n\n" )
	for sel_add in selections:
	    if sel_add == None:
		selection = cut_none
		print "Without Selection:"
		yieldsfile.write( "Without Selection \n" )
	    else:
		selection = sel_base & sel_add
		print "Additional Selection: {}".format( sel_add.name )
		yieldsfile.write( "Additional Selection: {} \n".format( sel_add.name ) )
	    print "Yields (value, uncertainty):"
	    yieldsfile.write( "Yields (value, uncertainty):\n" )
	    mc_sum = 0
	    mc_err = 0
	    for process in xmlParser.physicsProcesses:
		if process.isData:
		    # for data calculate yields without weight
		    tmp_yield = process.getYield( luminosity=lumi, cut=selection )
		    out_string = "{0}:\t\t{1}".format( process.name, tmp_yield )
		    print out_string
		    yieldsfile.write( out_string+'\n' )
		else:
		    # for mc calculate yields with weight
		    tmp_weight = weight_expression
		    if process.name=='Zee' or process.name=='Zmumu' or process.name=='Ztautau':
			tmp_weight = weight_expression+'*SF_dilepton_pt_vect'
		    tmp_yield = process.getYield( luminosity=lumi, cut=selection, weightExpression=tmp_weight, ignoreWeights=(not weighted) )
		    mc_sum += tmp_yield[0]
		    mc_err = math.sqrt( mc_err**2 + tmp_yield[1]**2 )
		    out_string = "{0}:\t\t{1}".format( process.name, tmp_yield )
		    print out_string
		    yieldsfile.write( out_string+'\n' )
	    out_string = "MC sum: {} +- {}\n".format( mc_sum, mc_err )
	    print out_string
	    yieldsfile.write( out_string+'\n' )
    yieldsfile.close()
