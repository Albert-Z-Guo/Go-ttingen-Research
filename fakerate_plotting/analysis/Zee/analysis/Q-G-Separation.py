import os, sys, subprocess, ROOT, logging, math
from copy import copy
from argparse import ArgumentParser
from ROOT import TH1D, TF1, TH2D, TF2
from ROOT import kBlack, kBlue, kRed, kGreen, kViolet, kGray
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

def create_X_Zpt_cuts( x ):
    name_below  = 'dilepton_pt_vect_{}_below'.format( x )
    name_over   = 'dilepton_pt_vect_{}_over'.format( x )
    title_below = 'vect. sum of ee-pt below {}'.format( x )
    title_over  = 'vect. sum of ee-pt over {}'.format( x )
    sel_below   = 'dilepton_vect_sum_pt < {}'.format( x )
    sel_over    = 'dilepton_vect_sum_pt > {}'.format( x )
    cut_below   = Cut( name_below, title_below, sel_below )
    cut_over    = Cut( name_over,  title_over,  sel_over  )
    return [ cut_below, cut_over ]

if __name__ == '__main__':
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

    selections = [	sel_base & cut_tau0_jetmatch_q,		sel_base & cut_tau0_jetmatch_g,		sel_base & cut_tau0_zeromatch,		sel_base & cut_tau0_zero_or_g,		]
    #selections = [	sel_base & cut_tau0_proper_jetmatch_q,	sel_base & cut_tau0_proper_jetmatch_g,	sel_base & cut_tau0_proper_zeromatch,	sel_base & cut_tau0_proper_zero_or_g,	]
    #selections = [	sel_base & cut_tau0_TAT_jetmatch_q,	sel_base & cut_tau0_TAT_jetmatch_g,	sel_base & cut_tau0_TAT_zeromatch,	sel_base & cut_tau0_TAT_zero_or_g,	]

    cut_var = var_dilepton_pt_vect

    l_cuts = [ 20, 25, 30, 35, 40 ]

    variables = [	var_tau0_pt,	var_tau0_pt_two_bins,	cut_var,	]

    sel_p = [		cut_1prong, 	cut_3prong,	cut_1or3prong,		]
    sel_p_name = [	' 1 Prong', 	' 3 Prong',	' 1 or 3 Prong',	]
    sel_p_suffix = [	'_1_Prong', 	'_3_Prong',	'_1_or_3_Prong',	]

    out_file = open( 'plots/Q-G-Separation.txt', 'w' )
    for option in l_cuts: # Loop over different Z pt cuts
	for i_p in range(len(sel_p)): # Loop over different Prong cuts
	    cuts = create_X_Zpt_cuts( option )
	    cut_option_region1 = cuts[0]
	    cut_option_region2 = cuts[1]
	    cut_option_suffix = '_cut_at_{}_GeV'.format( option )
	    cut_option_name = 'll_pt {} GeV'.format( option )
	    # Getting selection histograms
	    # ----------------------------
	    h_quarks_r1 = cut_var.createHistogram( 'Quarks Region 1' )
	    h_quarks_r2 = cut_var.createHistogram( 'Quarks Region 2' )
	    h_gluons_r1 = cut_var.createHistogram( 'Gluons Region 1' )
	    h_gluons_r2 = cut_var.createHistogram( 'Gluons Region 2' )
	    # obtain data and mc histograms for different IDs
	    for process in xmlParser.physicsProcesses:
		if process.name=='Zee':
		    #tmp_weight = weight_expression
		    tmp_weight = weight_expression+'*SF_dilepton_pt_vect'
		    h_quarks_r1 = process.getHistogram( cut_var, cut_option_name, cut=selections[0]+sel_p[i_p]+cut_option_region1, luminosity=lumi, weight=tmp_weight );     sys.stdout.write('.'); sys.stdout.flush()
		    h_quarks_r2 = process.getHistogram( cut_var, cut_option_name, cut=selections[0]+sel_p[i_p]+cut_option_region2, luminosity=lumi, weight=tmp_weight );     sys.stdout.write('.'); sys.stdout.flush()
		    h_gluons_r1 = process.getHistogram( cut_var, cut_option_name, cut=selections[3]+sel_p[i_p]+cut_option_region1, luminosity=lumi, weight=tmp_weight );     sys.stdout.write('.'); sys.stdout.flush()
		    h_gluons_r2 = process.getHistogram( cut_var, cut_option_name, cut=selections[3]+sel_p[i_p]+cut_option_region2, luminosity=lumi, weight=tmp_weight );     sys.stdout.write('.'); sys.stdout.flush()
		    for var in variables:
			# print number of quarks
			h_var_r1 = process.getHistogram( var, "Region 1", cut=selections[0]+sel_p[i_p]+cut_option_region1, luminosity=lumi, weight=tmp_weight );     sys.stdout.write('.'); sys.stdout.flush()
			h_var_r2 = process.getHistogram( var, "Region 2", cut=selections[0]+sel_p[i_p]+cut_option_region2, luminosity=lumi, weight=tmp_weight );     sys.stdout.write('.'); sys.stdout.flush()
			h_var_r1.SetLineColor( kRed )
			h_var_r1.SetMarkerColor( kRed )
			h_var_r2.SetLineColor( kBlue )
			h_var_r2.SetMarkerColor( kBlue )
			bp = BasicPlot( 'Q-G-Separation'+sel_p_suffix[i_p]+'_'+var.name+cut_option_suffix, var )
			bp.yVariable = Variable( "Events with quark match" )
			bp.yVariable.binning.low = 0
			bp.yVariable.binning.up = None
			bp.showBinWidthY = False
			bp.addHistogram( h_var_r1, 'E', copy=True )
			bp.addHistogram( h_var_r2, 'E', copy=True )
			bp.titles.append( '#sqrt{{s}} = 13 TeV, #scale[0.5]{{#int}}Ldt = {0:.2f} fb^{{-1}}, '.format(lumi/1000.) )
			bp.draw()
			bp.saveAsAll( os.path.join( "plots/", bp.title ) )
			# print quark rate
			h_var_tot_r1 = process.getHistogram( var, "Region 1", cut=selections[3]+sel_p[i_p]+cut_option_region1, luminosity=lumi, weight=tmp_weight );     sys.stdout.write('.'); sys.stdout.flush()
			h_var_tot_r2 = process.getHistogram( var, "Region 2", cut=selections[3]+sel_p[i_p]+cut_option_region2, luminosity=lumi, weight=tmp_weight );     sys.stdout.write('.'); sys.stdout.flush()
			h_var_tot_r1.Add( h_var_r1, 1 )
			h_var_tot_r2.Add( h_var_r2, 1 )
			h_var_r1.Divide( h_var_r1, h_var_tot_r1, 1, 1, "B" )
			h_var_r2.Divide( h_var_r2, h_var_tot_r2, 1, 1, "B" )
			h_tmp = var.createHistogram( '' )
			bp_r = BasicPlot( 'Q-G-Separation'+sel_p_suffix[i_p]+'_'+var.name+'_ratio'+cut_option_suffix, var )
			bp_r.yVariable = Variable( "quark fraction" )
			bp_r.yVariable.binning.low = 0
			bp_r.yVariable.binning.up = 1.05
			bp_r.showBinWidthY = False
			bp_r.addHistogram( h_var_r1, 'E', copy=True )
			bp_r.addHistogram( h_var_r2, 'E', copy=True )
			#draw line at one
			for i_bin in range( h_tmp.GetNbinsX() + 2 ):
			    h_tmp.SetBinContent( i_bin, 1 )
			    h_tmp.SetBinError( i_bin, 0 )
			h_tmp.SetLineColor( kGray )
			bp_r.addHistogram( h_tmp, 'E' )
			bp_r.titles.append( '#sqrt{{s}} = 13 TeV, #scale[0.5]{{#int}}Ldt = {0:.2f} fb^{{-1}}, '.format(lumi/1000.) )
			bp_r.draw()
			bp_r.saveAsAll( os.path.join( "plots/", bp_r.title ) )
	    # printing fractions into output file
	    i_quarks_r1 = h_quarks_r1.Integral()
	    i_quarks_r2 = h_quarks_r2.Integral()
	    i_gluons_r1 = h_gluons_r1.Integral()
	    i_gluons_r2 = h_gluons_r2.Integral()

	    sum_r1 = i_quarks_r1+i_gluons_r1
	    sum_r2 = i_quarks_r2+i_gluons_r2

	    out_file.write( "Probing cut option: {}\n".format(cut_option_name+sel_p_name[i_p]) )
	    out_file.write( "---------------------------------\n" )
	    out_file.write( "Region 1:\n" )
	    out_file.write( "Quark Fraction: {:.2f}%\n".format(100*i_quarks_r1/sum_r1) )
	    out_file.write( "Gluon Fraction: {:.2f}%\n".format(100*i_gluons_r1/sum_r1) )
	    out_file.write( "Region 2:\n" )
	    out_file.write( "Quark Fraction: {:.2f}%\n".format(100*i_quarks_r2/sum_r2) )
	    out_file.write( "Gluon Fraction: {:.2f}%\n".format(100*i_gluons_r2/sum_r2) )
	    out_file.write( "Difference:\n" )
	    out_file.write( "In Quark Fraction: {:.2f}\n".format(100*i_quarks_r2/sum_r2 - 100*i_quarks_r1/sum_r1) )
	    out_file.write( "In Gluon Fraction: {:.2f}\n".format(100*i_gluons_r1/sum_r1 - 100*i_gluons_r2/sum_r2) )
	    out_file.write( "Statistics:\n" )
	    out_file.write( "Region 1: {:.1f} ({:.2f}%)\n".format(sum_r1, 100*sum_r1/(sum_r1+sum_r2)) )
	    out_file.write( "Region 2: {:.1f} ({:.2f}%)\n".format(sum_r2, 100*sum_r2/(sum_r1+sum_r2)) )
	    out_file.write( "Figure of Merits:\n" )
	    out_file.write( "G(R1) + Q(R2): {:.1f}\n".format(i_gluons_r1 + i_quarks_r2) )
	    out_file.write( "G(R2) + Q(R1): {:.1f}\n".format(i_gluons_r2 + i_quarks_r1) )
	    figure_of_merit_1 = (i_gluons_r1 + i_quarks_r2) / (i_gluons_r2 + i_quarks_r1)
	    out_file.write( "( G(R1) + Q(R2) )/( G(R2) + Q(R1) ): {:.2f}\n".format( figure_of_merit_1) )
	    figure_of_merit_2 = (i_gluons_r1 + i_quarks_r2) / math.sqrt(sum_r1 + sum_r2)
	    out_file.write( "( G(R1) + Q(R2) )/sqrt( Sum(R1) + Sum(R2) ): {:.2f}\n".format( figure_of_merit_2) )
	    out_file.write( "\n" )

	    print( "\tDone with cut option {}".format(cut_option_name+sel_p_name[i_p]) )
    out_file.close()
