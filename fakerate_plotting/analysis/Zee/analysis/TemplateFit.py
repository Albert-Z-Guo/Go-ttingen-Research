import os, sys, subprocess, ROOT, logging, datetime
from copy import copy
from argparse import ArgumentParser
from ROOT import TH1D, TF1, TH2D, TF2
from ROOT import kBlack, kBlue, kRed, kGreen, kGray
from ROOT import kFullCircle, kFullSquare, kFullTriangleUp, kFullTriangleDown
from ROOT import TFile, TObject, TObjArray, TFractionFitter

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

def TemplateFit( filename, data, mc_q, mc_g, w_q=None, w_g=None, pull_widths=[1,1], doPlots=True ):
    n_mc = 2

    # Define MC samples
    mc = TObjArray(n_mc)
    mc.Add( mc_q )
    mc.Add( mc_g )

    # Names
    mc_type = []
    mc_type.append( 'Quarks' )
    mc_type.append( 'Gluons' )

    # Perform Fit
    fit = TFractionFitter( data, mc, "q" )
    if w_q and w_g:
	fit.SetWeight( 0, w_q )
	fit.SetWeight( 1, w_g )
    fit.Constrain( 0, 0.0, 1.0 ) #quarks
    fit.Constrain( 1, 0.0, 1.0 ) #gluons
    fit.Fit()

    # Printing results
    val_q = ROOT.Double()
    err_q = ROOT.Double()
    val_g = ROOT.Double()
    err_g = ROOT.Double()
    fit.GetResult( 0, val_q, err_q )
    fit.GetResult( 1, val_g, err_g )
    err_q = err_q * pull_widths[0] # correcting the error for the width of the pull plot
    err_g = err_g * pull_widths[1] # correcting the error for the width of the pull plot
    for i in range(n_mc):
	val = ROOT.Double()
	err = ROOT.Double()
	fit.GetResult( i, val, err )
	out_file.write( "fit result {}: {}, {}\n".format( mc_type[i], val, err ))
    out_file.write( "X2 = {}\n".format( fit.GetChisquare() ))
    out_file.write( "NDF = {}\n".format( fit.GetNDF() ))
    red_chi = fit.GetChisquare()/fit.GetNDF()
    out_file.write( "red. X2 = {}\n".format( red_chi ))
    out_file.write( "\n" )

    if doPlots:
	print "storing plot as {}".format( filename )
	# Preparing Histograms
	h_fit = fit.GetPlot()
	h_q = fit.GetMCPrediction( 0 )
	h_g = fit.GetMCPrediction( 1 )
	h_fit.SetTitle( "Fit" )
	h_q.SetTitle( "Quarks" )
	h_g.SetTitle( "Gluons" )
	h_fit.SetLineColor( kGreen )
	h_q.SetLineColor( kRed )
	h_g.SetLineColor( kBlue )
	h_q.SetMarkerColor( kRed )
	h_g.SetMarkerColor( kBlue )

	# Scaling to the fit result
	int_fit = h_fit.Integral()
	int_q = h_q.Integral()
	int_g = h_g.Integral()
	h_q.Sumw2()
	h_g.Sumw2()
	h_q.Scale( val_q * int_fit / int_q )
	h_g.Scale( val_g * int_fit / int_g )

	# Checking fit vs. templates
	h_check = h_fit.Clone('Fit - Templates Check')
	h_check.Add( h_q, -1 )
	h_check.Add( h_g, -1 )
	check_maxBin = h_check.GetMaximumBin()
	out_file.write( "Maximal bin of fit minus templates divided by content of that bin in fit: {} / {}\n\n".format( h_fit.GetBinContent(check_maxBin), h_check.GetBinContent(check_maxBin) ) )

	# Plotting results
	bp = BasicPlot( filename, var_tau0_width )
	bp.addHistogram( h_q, 'E', copy=True )
	bp.addHistogram( h_g, 'E', copy=True )
	bp.addHistogram( h_fit, 'HIST', copy=True )
	bp.addHistogram( data, 'E', copy=True )
	bp.titles.append( 'Quarks: {:.3} #pm {:.2}, Gluons: {:.3} #pm {:.2}'.format( val_q, err_q, val_g, err_g ) )
	bp.titles.append( '#sqrt{{s}} = 13 TeV, #scale[0.5]{{#int}}Ldt = {0:.2f} fb^{{-1}}'.format(lumi/1000.) )
	bp.titles.append( '#chi^{{2}}/ndf: {:.3}'.format( red_chi ) )
	bp.yVariable = Variable( "Events" )
	bp.legendDecorator.textSize = 0.045
	bp.normalizeByBinWidth = False
	bp.showBinWidthY = False
	bp.normalized = False
	bp.logY = False
	bp.yVariable.binning.low = 0 # start y-axis at 0
	bp.draw()
	bp.saveAsAll( os.path.join( outFolder, bp.title ) )

    return fit

def PullPlot(filename, h_data, h_quarks, h_gluons, w_quarks=None, w_gluons=None, pull_widths=[1,1]):
    # Creating a pull-plot
    # --------------------
    ratio_q = []
    error_q = []
    ratio_g = []
    error_g = []
    n_runs = 10000
    # getting fit results for toy experiments
    for i in range(1, n_runs+1):
	if i ==1: print "    starting loop"
	h_tmp = var.createHistogram( str(i) )
	h_tmp.FillRandom( h_data )
	filename_tmp = filename+'_'+str(i)
	out_file.write( str(i)+":\n")

	fit = TemplateFit( filename, h_tmp, h_quarks, h_gluons, w_quarks, w_gluons, pull_widths, doPlots=False )

	val_q = ROOT.Double()
	err_q = ROOT.Double()
	val_g = ROOT.Double()
	err_g = ROOT.Double()
	fit.GetResult( 0, val_q, err_q )
	fit.GetResult( 1, val_g, err_g )
	del fit
	err_q = err_q * pull_widths[0] # correcting the error for the width of the pull plot
	err_g = err_g * pull_widths[1] # correcting the error for the width of the pull plot

	ratio_q.append( val_q )
	error_q.append( err_q )
	ratio_g.append( val_g )
	error_g.append( err_g )
	
	if i%(n_runs/10) == 0 or i ==1 or i == n_runs:
	    print "    {}\tQ: {} +- {}\tG: {} +- {}".format( i, val_q, err_q, val_g, err_g )

    # creating pull histogram for quarks
    h_pull = var_pull.createHistogram()
    ratio_q_mean = sum(ratio_q)/len(ratio_q)
    for i in range(n_runs):
	tmp = (ratio_q[i] - ratio_q_mean)/error_q[i]
	h_pull.Fill(tmp)

    fit_result		= h_pull.Fit('gaus', 'QS')
    f_gaus		= h_pull.GetFunction('gaus')
    v_q_mu		= fit_result.Parameter(1)
    v_q_mu_err		= fit_result.ParError(1)
    v_q_sigma		= fit_result.Parameter(2)
    v_q_sigma_err	= fit_result.ParError(2)
    chi = fit_result.Chi2()
    ndf = fit_result.Ndf()
    #red_chi = chi / ndf

    filename_tmp = filename+'_PullPlot_q'
    bp = BasicPlot( filename_tmp, var_pull )
    bp.titles.append( 'Fit Results: #mu = {:05.3f}#pm{:05.3f}, #sigma = {:05.3f}#pm{:05.3f}'.format( v_q_mu, v_q_mu_err, v_q_sigma, v_q_sigma_err ) )
    bp.titles.append( '#chi^{{2}}/ndf: {:.3}/{}'.format( chi, ndf ) )
    bp.addHistogram( h_pull, 'E', copy=True )
    bp.yVariable = Variable( "Events" )
    bp.normalizeByBinWidth = False
    bp.showBinWidthY = False
    bp.normalized = False
    bp.logY = False
    bp.yVariable.binning.low = 0 # start y-axis at 0
    bp.draw()
    bp.saveAsAll( os.path.join( outFolder, bp.title ) )

    del h_pull
    del bp

    # creating pull histogram for gluons
    h_pull = var_pull.createHistogram()
    ratio_g_mean = sum(ratio_g)/len(ratio_g)
    for i in range(n_runs):
	tmp = (ratio_g[i] - ratio_g_mean)/error_g[i]
	h_pull.Fill(tmp)

    fit_result		= h_pull.Fit('gaus', 'QS')
    f_gaus		= h_pull.GetFunction('gaus')
    v_g_mu		= fit_result.Parameter(1)
    v_g_mu_err		= fit_result.ParError(1)
    v_g_sigma		= fit_result.Parameter(2)
    v_g_sigma_err	= fit_result.ParError(2)
    chi = fit_result.Chi2()
    ndf = fit_result.Ndf()
    #red_chi = chi / ndf

    filename_tmp = filename+'_PullPlot_g'
    bp = BasicPlot( filename_tmp, var_pull )
    bp.titles.append( 'Fit Results: #mu = {:05.3f}#pm{:05.3f}, #sigma = {:05.3f}#pm{:05.3f}'.format( v_g_mu, v_g_mu_err, v_g_sigma, v_g_sigma_err ) )
    bp.titles.append( '#chi^{{2}}/ndf: {:.3}/{}'.format( chi, ndf ) )
    bp.addHistogram( h_pull, 'E', copy=True )
    bp.yVariable = Variable( "Events" )
    bp.normalizeByBinWidth = False
    bp.showBinWidthY = False
    bp.normalized = False
    bp.logY = False
    bp.yVariable.binning.low = 0 # start y-axis at 0
    bp.draw()
    bp.saveAsAll( os.path.join( outFolder, bp.title ) )

    return [ v_q_sigma, v_g_sigma ]

def storeHistogram( var, lumi, cut, histo, filename ):
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
    bp.draw()
    bp.saveAsAll( os.path.join( outFolder, bp.title ) )
    # storing histogram in root file
    # ------------------------------
    from ROOT import TFile, TObject
    rootfile = TFile.Open( outFolder+'/'+filename+'.root', 'update' )
    if rootfile.IsOpen():
	print "writing in file {}".format( outFolder+'/'+filename+'.root' )
        rootfile.cd()
        histogram = histo.Clone( 'h_'+var.name )
        histogram.SetTitle( 'h_'+var.name )
        histogram.Write( 'h_'+var.name, TObject.kOverwrite )
	rootfile.Close()
    else:
	print "Problem opening file {}".format( outFolder+'/'+filename+'.root' )

def storeTHist( var, filename, histo):
    rootfile = TFile.Open( outFolder+'/'+filename+'.root', 'update' )
    if rootfile.IsOpen():
	#print "writing in file {}".format( outFolder+'/'+filename+'.root' )
	rootfile.cd()
	histogram = histo.Clone( var.name )
	histogram.SetTitle( var.name )
	histogram.Write( var.name, TObject.kOverwrite )
	rootfile.Close()
    else:
	print "Problem opening file {}".format( outFolder+'/'+filename+'.root' )

def unweight( histo ):
    weights = histo.Clone( histo.GetName()+'_weights' )
    nBins = histo.GetNbinsX()
    for i_bin in range( 1, nBins+1):
	before = histo.GetBinContent( i_bin )
	after = histo.GetBinError( i_bin ) ** 2
	histo.SetBinContent( i_bin, after )
	if(after != 0):
	    weights.SetBinContent( i_bin, before/after )
	else:
	    weights.SetBinContent( i_bin, 1 )
    return weights

if __name__ == '__main__':
    # greeting and setting up output folder
    scriptName = "TemplateFit"
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
    if True:
	for process in xmlParser.physicsProcesses:
	    for dataset in process.datasets:
                hist_store = HistogramStore("histogramStore/TemplateFit.root")
                dataset.histogramStore = hist_store

    # setting selection criteria
    sel_base = sel_lep & sel_tag & sel_tau

    # Documenting settings
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

    # Different plot settings
    # -----------------------
    path = '/afs/desy.de/user/t/tidreyer/plots/plotdirs/2016-07-27_Templates_GRID160524_P1_new_structure'

    hist_var = var_tau0_pt
    #hist_var = var_tau0_pt_two_bins
    variables = [	var_tau0_width	]

    sel_p = [		cut_1prong, 	cut_3prong,	]#cut_1or3prong,	 	]
    sel_p_names = [	' 1 Prong', 	' 3 Prong',	]#' 1 or 3 Prong', 	]
    sel_p_suffix = [	'_1_Prong', 	'_3_Prong',	]#'_1_or_3_Prong', 	]

    sel_region = [		cut_none, 		cut_gluon_enriched, 	cut_quark_enriched, 	]
    sel_region_names = [	' full region',		' gluon region', 	' quark region', 	]
    sel_region_suffix = [	'_full-region',		'_gluon-enriched', 	'_quark-enriched', 	]
    
    sel_bin = [		cut_none, 		cut_tau_pt_20to25, 	cut_tau_pt_25to30, 	cut_tau_pt_30to40, 	cut_tau_pt_40to60, 	cut_tau_pt_60to120, 	]
    sel_bin_names = [	' pt-bin open',		' pt-bin 20-25', 	' pt-bin 25-30', 	' pt-bin 30-40', 	' pt-bin 40-60', 	' pt-bin 60-120', 	]
    sel_bin_suffix = [	'_pt-bin_open', 	'_pt-bin_20-25', 	'_pt-bin_25-30', 	'_pt-bin_30-40', 	'_pt-bin_40-60', 	'_pt-bin_60-120', 	]
    sel_bin_index = [	0,			1,			2,			3,			4,			5,			]

    #sel_tm = [		cut_tau0_jetmatch_q,	cut_tau0_jetmatch_g, 	cut_tau0_zeromatch,	]
    sel_tm = [		cut_tau0_TAT_jetmatch_q,	cut_tau0_TAT_jetmatch_g, 	cut_tau0_TAT_zeromatch,	]
    sel_tm_names = [	' Quarks',		' Gluons',		' Unmatched',		]
    sel_tm_suffix = [	'_Quarks',		'_Gluons',		'_Unmatched',		]

    sel_id = [		cut_none, 	]#cut_tau_id_loose,	cut_tau_id_medium,	cut_tau_id_tight,	]
    sel_id_names = [	' no ID',	]#' Loose',		' Medium',		' Tight',		]
    sel_id_suffix = [	'_noID',	]#'_loose',		'_medium',		'_tight',		]

    sel_testA = cut_even
    sel_testB = cut_odd
    #sel_testA = cut_gluon_enriched
    #sel_testB = cut_quark_enriched

    out_file = open( outFolder+'/TemplateFit_results.txt', 'w' )

    doTest = False
    onlyFillHistoStore = False
    doUnweighting = False

    n_loops = len(variables) * len(sel_p) * len(sel_region) * len(sel_id) * len(sel_bin)
    i_loops = 0
    for var in variables:
	print "start working on variable {0}".format(var.name)
	for i_p in range(len(sel_p)): # Loop over different Prong cuts
	    for i_region in range(len(sel_region)): # Loop over different enriched regions
		for i_id in range(len(sel_id)): # Loop over different tau IDs
		    h_binned_q_ratio    = hist_var.createHistogram('q_ratio')
		    h_binned_g_ratio    = hist_var.createHistogram('g_ratio')
		    h_binned_q_ratio_up = hist_var.createHistogram('q_ratio_up')
		    h_binned_g_ratio_up = hist_var.createHistogram('g_ratio_up')
		    for i_bin in range(len(sel_bin)): # Loop over different tau pt bins
			i_loops += 1
			print "\nstarting loop {}/{}".format(i_loops,n_loops)
			cut_loop	= sel_base	& sel_region[i_region]		& sel_bin[i_bin]	& sel_p[i_p]		& sel_id[i_id]
			name_loop	= var.name	+ sel_region_names[i_region]	+ sel_bin_names[i_bin]	+ sel_p_names[i_p]	+ sel_id_names[i_id]
			filename_loop	= var.name	+ sel_region_suffix[i_region]	+ sel_bin_suffix[i_bin]	+ sel_p_suffix[i_p]	+ sel_id_suffix[i_id]
			# -------------------------------------
			# Getting templates and data histograms
			# -------------------------------------
			h_testA_quarks, h_testB_quarks = None, None
			h_testA_gluons, h_testB_gluons = None, None
			h_testA_zeros , h_testB_zeros  = None, None
			h_data   = None
			h_quarks = None
			h_gluons = None
			h_zeros  = None

			for process in xmlParser.physicsProcesses:
			    if process.isData:
				cut_tmp		= cut_loop
				filename_tmp	= filename_loop+"_data"
				name_tmp	= name_loop+" Data"
				h_data	= process.getHistogram( var, name_tmp, cut=cut_tmp, luminosity=lumi);	sys.stdout.write('.'); sys.stdout.flush()
				#if not doTest and not onlyFillHistoStore:
				#    storeHistogram( var, lumi, cut_tmp, h_data, filename_tmp )
			    elif process.name=='Zee':
				# Loop over different truth matches for MC histograms
				cut_tmp		= cut_loop
				filename_tmp	= filename_loop
				name_tmp	= name_loop
				tmp_weight	= weight_expression+'*SF_dilepton_pt_vect'
				if doTest:
				    h_testA_quarks	= process.getHistogram( var, name_tmp+sel_tm_names[0], cut=cut_tmp&sel_testA&sel_tm[0], luminosity=lumi, weightExpression=tmp_weight );	sys.stdout.write('.'); sys.stdout.flush()
				    h_testA_gluons	= process.getHistogram( var, name_tmp+sel_tm_names[1], cut=cut_tmp&sel_testA&sel_tm[1], luminosity=lumi, weightExpression=tmp_weight );	sys.stdout.write('.'); sys.stdout.flush()
				    h_testA_zeros	= process.getHistogram( var, name_tmp+sel_tm_names[2], cut=cut_tmp&sel_testA&sel_tm[2], luminosity=lumi, weightExpression=tmp_weight );	sys.stdout.write('.'); sys.stdout.flush()
				    h_testB_quarks	= process.getHistogram( var, name_tmp+sel_tm_names[0], cut=cut_tmp&sel_testB&sel_tm[0], luminosity=lumi, weightExpression=tmp_weight );	sys.stdout.write('.'); sys.stdout.flush()
				    h_testB_gluons	= process.getHistogram( var, name_tmp+sel_tm_names[1], cut=cut_tmp&sel_testB&sel_tm[1], luminosity=lumi, weightExpression=tmp_weight );	sys.stdout.write('.'); sys.stdout.flush()
				    h_testB_zeros	= process.getHistogram( var, name_tmp+sel_tm_names[2], cut=cut_tmp&sel_testB&sel_tm[2], luminosity=lumi, weightExpression=tmp_weight );	sys.stdout.write('.'); sys.stdout.flush()
				else:
				    h_quarks	= process.getHistogram( var, name_tmp+sel_tm_names[0], cut=cut_tmp&sel_tm[0], luminosity=lumi, weightExpression=tmp_weight );	sys.stdout.write('.'); sys.stdout.flush()
				    h_gluons	= process.getHistogram( var, name_tmp+sel_tm_names[1], cut=cut_tmp&sel_tm[1], luminosity=lumi, weightExpression=tmp_weight );	sys.stdout.write('.'); sys.stdout.flush()
				    h_zeros	= process.getHistogram( var, name_tmp+sel_tm_names[2], cut=cut_tmp&sel_tm[2], luminosity=lumi, weightExpression=tmp_weight );	sys.stdout.write('.'); sys.stdout.flush()
				#    if not onlyFillHistoStore:
				#	storeHistogram( var, lumi, cut_tmp, h_quarks, filename_tmp+sel_tm_suffix[0] )
				#	storeHistogram( var, lumi, cut_tmp, h_gluons, filename_tmp+sel_tm_suffix[1] )
				#	storeHistogram( var, lumi, cut_tmp, h_zeros,  filename_tmp+sel_tm_suffix[2] )
			print "\tgot all templates for {}".format( name_loop )

			# For Validation:
			if doTest:
			    h_data.Add( h_testA_quarks, h_testA_gluons, 1, 1 )
			    h_data.Add( h_testA_zeros, 1 )
			    h_quarks = h_testB_quarks
			    h_gluons = h_testB_gluons
			    h_zeros  = h_testB_zeros

			h_data.Sumw2()
			h_quarks.Sumw2()
			h_gluons.Sumw2()
			h_zeros.Sumw2()

			h_gluons_up = var.createHistogram("gluons_up")
			h_gluons_up.Add(   h_gluons, h_zeros, 1,  1 )

			h_data.SetTitle( "Data" )
			h_quarks.SetTitle( "Quarks")
			h_gluons.SetTitle( "Gluons")
			h_gluons_up.SetTitle( "Gluons + Unmatched" )

			# Printing number of events
			out_file.write( "Using{} and{} in region {} and tau-pt bin {} for variable {}\n".format( sel_p_names[i_p], sel_id_names[i_id], sel_region_names[i_region], sel_bin_index[i_bin], var.name ))
			out_file.write( "-------------------------------\n" )
			out_file.write( "Data events = {}\n".format( h_data.Integral() ))
			out_file.write( "Quarks events (MC) = {}\n".format( h_quarks.Integral() ))
			out_file.write( "Gluons events (MC) = {}\n".format( h_gluons.Integral() ))
			out_file.write( "Unmatched events (MC) = {}\n".format( h_zeros.Integral() ))
			out_file.write( "Gluons and Unmatched events (MC) = {}\n".format( h_gluons_up.Integral() ))
			out_file.write( "\n" )
			sum_mc    = h_quarks.Integral() + h_gluons.Integral()
			sum_mc_up = h_quarks.Integral() + h_gluons_up.Integral()
			if sum_mc != 0 and sum_mc_up != 0:
			    out_file.write( "Quarks fraction (MC) = {}\n".format( h_quarks.Integral() / sum_mc ))
			    out_file.write( "Gluons fraction (MC) = {}\n".format( h_gluons.Integral() / sum_mc ))
			    out_file.write( "Quarks fraction (MC_up) = {}\n".format( h_quarks.Integral() / sum_mc_up ))
			    out_file.write( "Gluons fraction (MC_up) = {}\n".format( h_gluons_up.Integral() / sum_mc_up ))
			    out_file.write( "\n" )

			w_quarks = None
			w_gluons = None
			w_gluons_up = None
			
			if doUnweighting:
			    print "Doing unweighting"
			    w_quarks = unweight( h_quarks )
			    w_gluons = unweight( h_gluons )
			    w_gluons_up = unweight( h_gluons_up )
			print "Data Integral: {}".format(h_data.Integral())
			print "Quarks Integral: {}".format(h_quarks.Integral())
			print "Gluons Integral: {}".format(h_gluons.Integral())
			print "Gluons up Integral: {}".format(h_gluons_up.Integral())

			# ---------------------------
			# Performing the template fit
			# ---------------------------
			if not onlyFillHistoStore:
			    pull_widths = [1,1]
			    print "Producing nominal pull plot:"
			    pull_widths = PullPlot(filename_loop+'_nominal',           h_data, h_quarks, h_gluons, w_quarks, w_gluons)
			    #print "Producing nominal pull plot (pull corrected):"
			    #PullPlot(              filename_loop+'_nominal_corrected', h_data, h_quarks, h_gluons, w_quarks, w_gluons, pull_widths)
			    print "Performing nominal fit:"
			    out_file.write( "Nominal:\n")
			    fit = TemplateFit( filename_loop+'_nominal', h_data, h_quarks, h_gluons, w_quarks, w_gluons, pull_widths)
			    if sel_bin_index[i_bin] > 0:
				val_q = ROOT.Double()
				err_q = ROOT.Double()
				val_g = ROOT.Double()
				err_g = ROOT.Double()
				fit.GetResult( 0, val_q, err_q )
				fit.GetResult( 1, val_g, err_g )
				err_q = err_q * pull_widths[0] # correcting the error for the width of the pull plot
				err_g = err_g * pull_widths[1] # correcting the error for the width of the pull plot
				h_binned_q_ratio.SetBinContent( sel_bin_index[i_bin], val_q )
				h_binned_g_ratio.SetBinContent( sel_bin_index[i_bin], val_g )
				h_binned_q_ratio.SetBinError(   sel_bin_index[i_bin], err_q )
				h_binned_g_ratio.SetBinError(   sel_bin_index[i_bin], err_g )
			    pull_widths = [1,1]
			    print "Producing up pull plot:"
			    pull_widths = PullPlot(filename_loop+'_up',           h_data, h_quarks, h_gluons_up, w_quarks, w_gluons_up)
			    #print "Producing up pull plot (pull corrected):"
			    #PullPlot(              filename_loop+'_up_corrected', h_data, h_quarks, h_gluons_up, w_quarks, w_gluons_up, pull_widths)
			    print "Performing up fit:"
			    out_file.write( "Up:\n")
			    fit = TemplateFit( filename_loop+'_up', h_data, h_quarks, h_gluons_up, w_quarks, w_gluons_up, pull_widths)
			    if sel_bin_index[i_bin] > 0:
				val_q = ROOT.Double()
				err_q = ROOT.Double()
				val_g = ROOT.Double()
				err_g = ROOT.Double()
				fit.GetResult( 0, val_q, err_q )
				fit.GetResult( 1, val_g, err_g )
				err_q = err_q * pull_widths[0] # correcting the error for the width of the pull plot
				err_g = err_g * pull_widths[1] # correcting the error for the width of the pull plot
				h_binned_q_ratio_up.SetBinContent( sel_bin_index[i_bin], val_q )
				h_binned_g_ratio_up.SetBinContent( sel_bin_index[i_bin], val_g )
				h_binned_q_ratio_up.SetBinError(   sel_bin_index[i_bin], err_q )
				h_binned_g_ratio_up.SetBinError(   sel_bin_index[i_bin], err_g )
			# ---------------
			# End of i_bin loop
		    filename = var.name + sel_region_suffix[i_region] + '_binned_histogram' + sel_p_suffix[i_p] + sel_id_suffix[i_id]
		    storeTHist( hist_var, filename+'_q',    h_binned_q_ratio)
		    storeTHist( hist_var, filename+'_g',    h_binned_g_ratio)
		    storeTHist( hist_var, filename+'_q_up', h_binned_q_ratio_up)
		    storeTHist( hist_var, filename+'_g_up', h_binned_g_ratio_up)
		    print "finished storing binned histograms for this loop"
		    # ----------------
		    # End of i_id loop
		# ---------------
		# End of i_region loop
	    # ---------------
	    # End of i_p loop
	# ---------------
	# End of var loop
    print "everything is done!"
    out_file.close()
