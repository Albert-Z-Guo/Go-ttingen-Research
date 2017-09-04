#!/usr/bin/env python
# based on atlas-janus/janus/scripts/trunk/getnentriesfromfile.py
import sys,ROOT,math
usage = 'Usage: %s infile treename' % sys.argv[0] 


try:
    infile = sys.argv[1]
except:
    print usage; sys.exit(1)

try:
    treename = sys.argv[2]
except:
    print usage; sys.exit(1)

ROOT.gErrorIgnoreLevel = 60000000000000
print  ' \n number of entries in collection tree in  file ' + infile + ' \n \n'
f = ROOT.TFile(infile)
t = f.Get(treename)

n_xAOD = f.h_metadata.GetBinContent(6)
n_DxAOD = f.h_metadata.GetBinContent(9)
n_tree = 0.0
n_presel = 0.0
n_Z_window = 0.0
n_tau_id_loose = 0.0
n_tau_id_medium = 0.0
n_tau_id_tight = 0.0
n_1p_tau = 0.0
n_1p_tau_id_loose = 0.0
n_1p_tau_id_medium = 0.0
n_1p_tau_id_tight = 0.0
n_3p_tau = 0.0
n_3p_tau_id_loose = 0.0
n_3p_tau_id_medium = 0.0
n_3p_tau_id_tight = 0.0

if (t) :
    n_tree = t.GetEntries()
    for event in t :
	if ((   True
#		) and ( event.HLT_e24_lhmedium_L1EM18VH and event.eleTrigMatch_0_HLT_e24_lhmedium_L1EM18VH	# cut_trigger
		) and ( event.lep_0_iso_wp > 10000 and event.lep_1_iso_wp > 10000				# cut_lep_iso
		) and ( event.lep_0_id_medium and event.lep_1_id_medium						# cut_lep_id_medium
		) and ( event.lep_0_q == -event.lep_1_q								# cut_lep_OS
		) and ( event.tau_0_pt > 20									# cut_tau_pt
		) and ( abs(event.tau_0_eta) < 2.5								# cut_tau_eta
		) and (    ((abs(event.tau_0_phi - event.lep_0_phi) < math.pi)  and math.sqrt(pow(event.tau_0_eta - event.lep_0_eta, 2) + pow(abs(event.tau_0_phi - event.lep_0_phi),           2)) > 0.4)
		        or ((abs(event.tau_0_phi - event.lep_0_phi) >= math.pi) and math.sqrt(pow(event.tau_0_eta - event.lep_0_eta, 2) + pow(abs(event.tau_0_phi - event.lep_0_phi) - math.pi, 2)) > 0.4)	# cut_tau_olr_lep0
		) and (    ((abs(event.tau_0_phi - event.lep_1_phi) < math.pi)  and math.sqrt(pow(event.tau_0_eta - event.lep_1_eta, 2) + pow(abs(event.tau_0_phi - event.lep_1_phi),           2)) > 0.4)
		        or ((abs(event.tau_0_phi - event.lep_1_phi) >= math.pi) and math.sqrt(pow(event.tau_0_eta - event.lep_1_eta, 2) + pow(abs(event.tau_0_phi - event.lep_1_phi) - math.pi, 2)) > 0.4)	# cut_tau_olr_lep1
		) and ( abs(event.tau_0_q) == 1									# cut_tau_q
		) and ( abs(event.tau_0_eta) > 1.52 or abs(event.tau_0_eta) < 1.37				# cut_tau_crack
		) and ( event.tau_0_n_tracks == 1 or event.tau_0_n_tracks == 3					# cut_1or3prong
		)) :
	    n_presel += 1
	    if ( event.dilepton_vis_mass > 86.188 and event.dilepton_vis_mass < 96.188 ) :	# cut_Z_window_5
		n_Z_window += 1
		if ( event.tau_0_jet_bdt_loose ) :	# cut_tau_id_loose
		    n_tau_id_loose += 1
		if ( event.tau_0_jet_bdt_medium ) :	# cut_tau_id_medium
		    n_tau_id_medium += 1
		if ( event.tau_0_jet_bdt_tight ) :	# cut_tau_id_tight
		    n_tau_id_tight += 1
		if ( event.tau_0_n_tracks == 1 ) :
		    n_1p_tau += 1
		    if ( event.tau_0_jet_bdt_loose ) :
			n_1p_tau_id_loose += 1
		    if ( event.tau_0_jet_bdt_medium ) :
			n_1p_tau_id_medium += 1
		    if ( event.tau_0_jet_bdt_tight ) :
			n_1p_tau_id_tight += 1
		if ( event.tau_0_n_tracks == 3 ) :
		    n_3p_tau += 1
		    if ( event.tau_0_jet_bdt_loose ) :
			n_3p_tau_id_loose += 1
		    if ( event.tau_0_jet_bdt_medium ) :
			n_3p_tau_id_medium += 1
		    if ( event.tau_0_jet_bdt_tight ) :
			n_3p_tau_id_tight += 1
else:
    print "no Collection tree \n"

print "xAOD events:\t",		n_xAOD
print "DxAOD events:\t",	n_DxAOD
print "tree:\t\t",		n_tree
print "presel:\t\t",		n_presel
print "Z_Window:\t",		n_Z_window
print "tau_id_loose:\t",	n_tau_id_loose
print "tau_id_medium:\t",	n_tau_id_medium
print "tau_id_tight:\t",	n_tau_id_tight
if (n_1p_tau > 0) :
    print "1p loose FR:\t",	n_1p_tau_id_loose/n_1p_tau
    print "1p medium FR:\t",	n_1p_tau_id_medium/n_1p_tau
    print "1p tight FR:\t",	n_1p_tau_id_tight/n_1p_tau
if (n_3p_tau > 0) :
    print "3p loose FR:\t",	n_3p_tau_id_loose/n_3p_tau
    print "3p medium FR:\t",	n_3p_tau_id_medium/n_3p_tau
    print "3p tight FR:\t",	n_3p_tau_id_tight/n_3p_tau

f.Close()
