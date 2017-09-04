import os
import sys
import subprocess
import ROOT
import logging
import math
import datetime
from copy import copy
from argparse import ArgumentParser
from ROOT import TH1D, TF1, TH2D, TF2
from ROOT import kBlack, kBlue, kRed, kGreen, kGray, kViolet
from ROOT import kFullCircle, kFullSquare, kFullTriangleUp, kFullTriangleDown
from ROOT import TFile, TObject

from plotting.PlotDecorator import AtlasTitleDecorator
from plotting.AtlasStyle import Style
from plotting.BasicPlot import BasicPlot
from plotting.Colours import *
from plotting.Cut import Cut
from plotting.Dataset import Dataset, PhysicsProcess, readPhysicsProcessesFromFile
from plotting.DataMcRatioPlot import DataMcRatioPlot
from plotting.HistogramStore import HistogramStore
from plotting.XmlParser import XMLParser
from plotting.Variable import Binning, Variable, var_Normalized

# Add 'ATLAS Internal' to all plots
BasicPlot.defaultTitleDecorator = AtlasTitleDecorator('Work In Progress')
BasicPlot.defaultTitleDecorator.textSize = 0.03
BasicPlot.defaultTitleDecorator.lineGap = 0.01
BasicPlot.defaultLegendDecorator.textSize = 0.03

from analysis.Definitions import *
from analysis.Selections import *
from analysis.Datasets import xmlPath, lumi

ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 3001;")


def MCFakeRateHisto(var, processes, name, idName, baseSel, idSel, lumi, weight, systVar=None):
    for process in xmlParser.physicsProcesses:
        tmp_weight = weight
        if process.name == 'Zee' or process.name == 'Zmumu' or process.name == 'Ztautau':
            tmp_weight = weight + '*SF_dilepton_pt_vect'
        if (not process.isData) and (process.name == 'Zee'):
            h_reco = process.getHistogram(var, 'No tau ID ' + name, cut=baseSel, luminosity=lumi, weightExpression=tmp_weight, systematicVariation=systVar)
            sys.stdout.write('.')
            sys.stdout.flush()
            h_id = process.getHistogram(var, idName + name, cut=baseSel & idSel, luminosity=lumi, weightExpression=tmp_weight, systematicVariation=systVar)
            sys.stdout.write('.')
            sys.stdout.flush()

            h_fr = var.createHistogram(idName)
            h_fr.Divide(h_id, h_reco, 1, 1, 'B')

    return h_fr


def DataFakeRateHisto(var, processes, name, idName, baseSel, idSel, lumi, weight, systVar=None):
    h_reco = var.createHistogram('No tau ID ' + name)
    h_id = var.createHistogram(idName + name)
    for process in processes:
        tmp_weight = weight
        if process.isData:
            # Add data
            h_tmp_reco = process.getHistogram(var, 'No tau ID ' + name, cut=baseSel,)
            sys.stdout.write('.')
            sys.stdout.flush()
            h_tmp_id = process.getHistogram(var, idName + name, cut=baseSel & idSel, )
            sys.stdout.write('.')
            sys.stdout.flush()
            h_reco.Add(h_tmp_reco, 1)
            h_id.Add(h_tmp_id, 1)

    h_fr = var.createHistogram(idName)
    h_fr.Divide(h_id, h_reco, 1, 1, 'B')

    return h_fr


def SFHistogram(var, name, h_data, h_mc):
    h_sf = var.createHistogram('SF_' + name)
    h_sf.SetTitle(h_data.GetTitle())
    h_sf.Divide(h_data, h_mc)  # Do NOT use binomial errors for scale factors!

    return h_sf


def BinWiseSystError(h_nom, h_up, h_down, writeToFile=False):
    h_out = h_nom.Clone()
    nBins = h_nom.GetNbinsX()
    for i_bin in range(1, nBins + 1):
        val_nom = h_nom.GetBinContent(i_bin)
        val_up = h_up.GetBinContent(i_bin)
        val_down = h_down.GetBinContent(i_bin)
        delta_up = val_up - val_nom
        delta_down = val_down - val_nom
        delta_sym = (abs(delta_up) + abs(delta_down)) / 2
        stat_nom = h_nom.GetBinError(i_bin)
        if writeToFile:
            out_file.write("Bin: {}\tFake Rate: {:2.2f} %\tSyst: {} %\tstat. uncert.: {:0.6f} %\n".format(i_bin, val_nom * 100, delta_sym * 100, stat_nom * 100))
        h_out.SetBinError(i_bin, delta_sym)
    return h_out


def AddBinWiseSystError(h_syst, h_nom, h_up, h_down):
    h_tmp = BinWiseSystError(h_nom, h_up, h_down)
    nBins = h_nom.GetNbinsX()
    for i_bin in range(1, nBins + 1):
        h_syst.SetBinError(i_bin, math.sqrt(h_syst.GetBinError(i_bin)**2 + h_tmp.GetBinError(i_bin)**2))
    return h_syst


def SetHistStyle(hist, i_style):
    colors = [	kRed,			kViolet,		kBlue			]
    marker = [	kFullSquare,		kFullTriangleUp,	kFullTriangleDown	]
    hist.SetLineColor(colors[i_style])
    hist.SetMarkerColor(colors[i_style])
    hist.SetMarkerStyle(marker[i_style])
    hist.SetMarkerSize(0)


def PlotAndStore(var, filename, lumi, h_1, h_2=None, h_3=None, drawOneLine=False, simulation=False, yLabel="Fake Rate", yLow=0, yHigh=None):
    bp = BasicPlot(filename, var)
    # Add histos
    SetHistStyle(h_1, 0)
    bp.addHistogram(h_1, 'E', copy=True)
    if h_2:
        SetHistStyle(h_2, 1)
        bp.addHistogram(h_2, 'E', copy=True)
    if h_3:
        SetHistStyle(h_3, 2)
        bp.addHistogram(h_3, 'E', copy=True)
    # Draw a line at 1 e.g. for SF plots
    if drawOneLine:
        h_tmp = var.createHistogram('')
        for i_bin in range(h_tmp.GetNbinsX() + 2):
            h_tmp.SetBinContent(i_bin, 1)
            h_tmp.SetBinError(i_bin, 0)
        h_tmp.SetLineColor(kGray)
        bp.addHistogram(h_tmp, 'E')
    # Some further settings
    bp.titles.append(
        '#sqrt{{s}} = 13 TeV, #scale[0.5]{{#int}}Ldt = {0:.2f} fb^{{-1}}'.format(lumi / 1000.))
    bp.legendDecorator.textSize = 0.045
    if simulation:
        bp.titles.append('Simulation')
    bp.showBinWidthY = False
    bp.logY = False
    bp.normalized = False
    bp.normalizeByBinWidth = False
    bp.yVariable = Variable(yLabel)
    bp.yVariable.binning.low = yLow
    bp.yVariable.binning.up = yHigh
    # Plot and store
    bp.draw()
    bp.saveAsAll(os.path.join(outFolder, bp.title))


def StoreTHist(var, filename, histo):
    rootfile = TFile.Open(outFolder + '/' + filename + '.root', 'update')
    if rootfile.IsOpen():
        # print "writing in file {}".format( outFolder+'/'+filename+'.root' )
        rootfile.cd()
        histogram = histo.Clone(var.name)
        histogram.SetTitle(var.name)
        histogram.Write(var.name, TObject.kOverwrite)
        rootfile.Close()
    else:
        print "Problem opening file {}".format(outFolder + '/' + filename + '.root')

if __name__ == '__main__':
    # greeting and setting up output folder
    scriptName = "FakeRates_Syst"
    dateString = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    outFolder = "plots/{}_{}".format(scriptName, dateString)
    print "Welcome, you are running {}.py".format(scriptName)
    print "Output will be stored in the folder {}".format(outFolder)
    if os.path.exists(outFolder):
        print "ERROR: The folder {} already exists!".format(outFolder)
        sys.exit()
    try:
        os.makedirs(outFolder)
    except:
        print "ERROR: Could not create folder {}!".format(outFolder)
        sys.exit()

    # run in batch mode
    ROOT.gROOT.SetBatch(True)

    xmlParser = XMLParser()
    xmlParser.parse(xmlPath)

    # add HistogramStore to each process
    if True:
        for process in xmlParser.physicsProcesses:
            for dataset in process.datasets:
                hist_store = HistogramStore("histogramStore/FakeRates_syst.root")
                dataset.histogramStore = hist_store
                #dataset.histogramStore = xmlParser.histogramStore

    # add Systematics to each dataset
    for process in xmlParser.physicsProcesses:
        if not process.isData:
            for dataset in process.datasets:
                for syst in systSet:
                    dataset.systematicsSet.add(syst)

    # setting selection criteria
    sel_base = sel_lep & sel_tau & sel_tag
    #sel_base = sel_lep & sel_tau & sel_tag & cut_quark_enriched
    #sel_base = sel_lep & sel_tau & sel_tag & cut_gluon_enriched
    sel_noWin = sel_lep & sel_tau
    # applied only to MC FR from Zee sample (propagates to SF)
    truth_match = cut_none
    # truth_match = cut_tau0_jetmatch_q	# use only in combination with process_MC !
    # truth_match = cut_tau0_zero_or_g	# use only in combination with process_MC !

    # only Fake Rates of MC samples (e.g. when using a truth match)
    process_MC = True

    # only fake rates of data
    process_Data = True

    # produce an extra plot for each systematic variation
    plot_each_syst = False

    # Documenting settings
    settingsfile = open(outFolder + '/plot-settings.txt', 'w')
    settingsfile.write("\nluminosity:\n{0}\n".format(lumi))
    settingsfile.write("\nsystSet:\n{0}\n".format(systSet))
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

    out_file = open( outFolder + '/FakeRates_Syst.txt', 'w', 1 )

    # Different plot settings
    # -----------------------
    sel_id = [		cut_tau_id_loose,	cut_tau_id_medium,	cut_tau_id_tight	]
    sel_id_names = [	' Loose ID',		' Medium ID',		' Tight ID'		]
    sel_id_suffix = [	'_loose',		'_medium',		'_tight'		]

    sel_p = [		cut_1prong, 	cut_3prong,	]  # cut_1or3prong,		]
    sel_p_names = [	' 1 Prong', 	' 3 Prong',	]  # ' 1 or 3 Prong',	]
    sel_p_suffix = [	'_1_Prong', 	'_3_Prong',	]  # '_1_or_3_Prong',	]

    # , var_n_pileup, var_tau0_pt_equal, var_tau0_eta_equal, var_tau0_bdt, var_tau0_eta_equal, var_tau0_q_eta, var_tau0_phi, ]
    variables = [var_tau0_pt, var_tau0_eta, var_n_pileup]

    for var in variables:
        print "start getting histos for variable {0}".format(var.name)
        out_file.write("Variable {}\n".format(var.name))
        for i_p in range(len(sel_p)):  # Loop over different Prong cuts
            out_file.write(" {}\n".format(sel_p_names[i_p]))
            print " {}".format(sel_p_names[i_p])
            syst_names = []
            syst_set = []
            for syst in systSet:
                syst_names.append(syst.name)
                syst_set.append(syst)
            syst_names.append('Z_window')

            # Calculating fake rates and scale factors
            h_fr_mc_nom = [None for i_id in range(len(sel_id))]
            h_fr_data_nom = [None for i_id in range(len(sel_id))]
            h_sf_nom = [None for i_id in range(len(sel_id))]
            h_fr_mc_up = [[None for i_id in range(len(sel_id))] for i_sys in range(len(syst_names))]  # access with h_xxx[i_sys][i_id]
            h_fr_data_up = [[None for i_id in range(len(sel_id))] for i_sys in range(len(syst_names))]
            h_sf_up = [[None for i_id in range(len(sel_id))]for i_sys in range(len(syst_names))]
            h_fr_mc_down = [[None for i_id in range(len(sel_id))] for i_sys in range(len(syst_names))]
            h_fr_data_down = [[None for i_id in range(len(sel_id))] for i_sys in range(len(syst_names))]
            h_sf_down = [[None for i_id in range(len(sel_id))] for i_sys in range(len(syst_names))]
            for i_id in range(len(sel_id)):  # Loop over different IDs
                print "   {}".format(sel_id_names[i_id])
                tmp_weight = weight_expression
                base_name = var.name + sel_id_names[i_id] + sel_p_names[i_p]
                # MCFakeRateHisto(var, processes, name, idName, baseSel, idSel, lumi, weight, systVar=None)
                h_fr_mc_nom[i_id] = MCFakeRateHisto(var, xmlParser.physicsProcesses, base_name, sel_id_names[i_id], sel_base & sel_p[i_p] & truth_match, sel_id[i_id], lumi, tmp_weight,)
                h_fr_data_nom[i_id] = DataFakeRateHisto(var, xmlParser.physicsProcesses, base_name, sel_id_names[i_id], sel_base & sel_p[i_p], sel_id[i_id], lumi, tmp_weight,)
                h_sf_nom[i_id] = SFHistogram(var, base_name, h_fr_data_nom[i_id], h_fr_mc_nom[i_id])
                for i_sys in range(len(syst_set)):
                    tmp_name = base_name + syst_set[i_sys].name
                    # only the monte carlo simulation fake rates are plotted
                    if process_MC:
                        h_fr_mc_up[i_sys][i_id] = MCFakeRateHisto(var, xmlParser.physicsProcesses, tmp_name + '_up', sel_id_names[i_id], sel_base & sel_p[i_p] & truth_match, sel_id[i_id], lumi, tmp_weight, syst_set[i_sys].up)
                        h_fr_mc_down[i_sys][i_id] = MCFakeRateHisto(var, xmlParser.physicsProcesses, tmp_name + '_down', sel_id_names[i_id], sel_base & sel_p[i_p] & truth_match, sel_id[i_id], lumi, tmp_weight, syst_set[i_sys].down)
                    # only the data fake rates are plotted
                    if process_Data:
                        h_fr_data_up[i_sys][i_id] = DataFakeRateHisto(var, xmlParser.physicsProcesses, tmp_name + '_up', sel_id_names[i_id], sel_base & sel_p[i_p], sel_id[i_id], lumi, tmp_weight, syst_set[i_sys].up)
                        h_fr_data_down[i_sys][i_id] = DataFakeRateHisto(var, xmlParser.physicsProcesses, tmp_name + '_down', sel_id_names[i_id], sel_base & sel_p[i_p], sel_id[i_id], lumi, tmp_weight, syst_set[i_sys].down)
                    if process_MC and process_Data:
                        h_sf_up[i_sys][i_id] = SFHistogram(var, tmp_name, h_fr_data_up[i_sys][i_id], h_fr_mc_up[i_sys][i_id])
                        h_sf_down[i_sys][i_id] = SFHistogram(var, tmp_name, h_fr_data_down[i_sys][i_id], h_fr_mc_down[i_sys][i_id])

                # Z mass window systematics
                tmp_name = base_name + 'Z_window'
                if process_MC:
                    h_fr_mc_up[len(syst_set)][i_id] = MCFakeRateHisto(var, xmlParser.physicsProcesses, tmp_name + '_up', sel_id_names[i_id], sel_noWin & truth_match & cut_Z_window_up & sel_p[i_p], sel_id[i_id], lumi, tmp_weight,)
                    h_fr_mc_down[len(syst_set)][i_id] = MCFakeRateHisto(var, xmlParser.physicsProcesses, tmp_name + '_down', sel_id_names[i_id], sel_noWin & truth_match & cut_Z_window_down & sel_p[i_p], sel_id[i_id], lumi, tmp_weight,)
                if process_Data:
                    h_fr_data_up[len(syst_set)][i_id] = DataFakeRateHisto(var, xmlParser.physicsProcesses, tmp_name + '_up', sel_id_names[i_id], sel_noWin & cut_Z_window_up & sel_p[i_p], sel_id[i_id], lumi, tmp_weight,)
                    h_fr_data_down[len(syst_set)][i_id] = DataFakeRateHisto(var, xmlParser.physicsProcesses, tmp_name + '_down', sel_id_names[i_id], sel_noWin & cut_Z_window_down & sel_p[i_p], sel_id[i_id], lumi, tmp_weight,)
                if process_MC and process_Data:
                    h_sf_up[len(syst_set)][i_id] = SFHistogram(var, tmp_name, h_fr_data_up[len(syst_set)][i_id],   h_fr_mc_up[len(syst_set)][i_id])
                    h_sf_down[len(syst_set)][i_id] = SFHistogram(var, tmp_name, h_fr_data_down[len(syst_set)][i_id], h_fr_mc_down[len(syst_set)][i_id])
                print ""
            print "    got all histograms, calculating systematics"

            # Calculating systematics on fake rates and scale factors
            if process_MC:
                h_fr_mc_syst = [[None for i_id in range(len(sel_id))] for i_sys in range(len(syst_names))]
                h_fr_mc_syst_all = [h_fr_mc_nom[i_id]for i_id in range(len(sel_id))]
            if process_Data:
                h_fr_data_syst = [[None for i_id in range(len(sel_id))] for i_sys in range(len(syst_names))]
                h_fr_data_syst_all = [h_fr_data_nom[i_id] for i_id in range(len(sel_id))]
            if process_MC and process_Data:
                h_sf_syst = [[None for i_id in range(len(sel_id))] for i_sys in range(len(syst_names))]
                h_sf_syst_all = [h_sf_nom[i_id] for i_id in range(len(sel_id))]

            for i_id in range(len(sel_id)):
                out_file.write("   {}\n".format(sel_id_names[i_id]))
                for i_sys in range(len(syst_names)):
                    out_file.write("    {}\n".format(syst_names[i_sys]))
                    # print syst_names[i_sys]
                    # BinWiseSystError(h_nom, h_up, h_down)
                    if process_MC:
                        h_fr_mc_syst[i_sys][i_id] = BinWiseSystError(h_fr_mc_nom[i_id], h_fr_mc_up[i_sys][i_id], h_fr_mc_down[i_sys][i_id], writeToFile=True)
                    if process_Data:
                        h_fr_data_syst[i_sys][i_id] = BinWiseSystError(h_fr_data_nom[i_id], h_fr_data_up[i_sys][i_id], h_fr_data_down[i_sys][i_id])
                    if process_MC and process_Data:
                        h_sf_syst[i_sys][i_id] = BinWiseSystError(h_sf_nom[i_id], h_sf_up[i_sys][i_id], h_sf_down[i_sys][i_id])
                for i_sys in range(len(syst_names)):
                    # print syst_names[i_sys]
                    # AddBinWiseSystError(h_syst, h_nom, h_up, h_down)
                    if process_MC:
                        h_fr_mc_syst_all[i_id] = AddBinWiseSystError(h_fr_mc_syst_all[i_id], h_fr_mc_nom[i_id], h_fr_mc_up[i_sys][i_id], h_fr_mc_down[i_sys][i_id])
                    if process_MC and process_Data:
                        h_sf_syst_all[i_id] = AddBinWiseSystError(h_sf_syst_all[i_id], h_sf_nom[i_id], h_sf_up[i_sys][i_id], h_sf_down[i_sys][i_id])

            # Plotting the histograms
            base_name = var.name + sel_p_suffix[i_p]
            if process_MC:
                # PlotAndStore(var, filename, lumi, h_1, h_2=None, h_3=None, drawOneLine=False, simulation=False, yLabel="Fake Rate", yLow=0, yHigh=None):
                PlotAndStore(var, base_name + '_MC', lumi, h_fr_mc_syst_all[0], h_fr_mc_syst_all[1], h_fr_mc_syst_all[2], simulation=True,)
            if process_Data:
                PlotAndStore(var, base_name + '_Data', lumi, h_fr_data_syst_all[0], h_fr_data_syst_all[1], h_fr_data_syst_all[2],)
            if process_MC and process_Data:
                PlotAndStore(var, base_name + '_SF', lumi, h_sf_syst_all[0], h_sf_syst_all[1], h_sf_syst_all[2], drawOneLine=True, yLow=0.5, yHigh=2, yLabel="Scale Factor", )
            for i_id in range(len(sel_id)):  # Loop over different IDs
                if process_MC:
                    StoreTHist(var, base_name + '_MC_allSysts' + sel_id_suffix[i_id], h_fr_mc_syst_all[i_id])
                if process_Data:
                    StoreTHist(var, base_name + '_Data_allSysts' + sel_id_suffix[i_id], h_fr_data_syst_all[i_id])
            if plot_each_syst:
                for i_sys in range(len(syst_names)):
                    if process_MC:
                        PlotAndStore(var, base_name + '_MC' + '_' + syst_names[i_sys], lumi, h_fr_mc_syst[i_sys][0], h_fr_mc_syst[i_sys][1], h_fr_mc_syst[i_sys][2], simulation=True,)
                    if process_Data:
                        PlotAndStore(var, base_name + '_Data' + '_' + syst_names[i_sys], lumi, h_fr_data_syst[i_sys][0], h_fr_data_syst[i_sys][1], h_fr_data_syst[i_sys][2],)
                    if process_MC and process_Data:
                        PlotAndStore(var, base_name + '_SF' + '_' + syst_names[i_sys], lumi, h_sf_syst[i_sys][0], h_sf_syst[i_sys][1], h_sf_syst[i_sys][2], drawOneLine=True,  yLow=0.5, yHigh=2, yLabel="Scale Factor", )
    # --------------------
    out_file.close()
    print "\neverything is done!"
