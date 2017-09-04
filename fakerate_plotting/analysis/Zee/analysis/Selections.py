from plotting.Cut import Cut

#======#
# Cuts #
#======#
cut_none		= Cut( 'NoCut',			'No Cut',				'1' )
cut_even		= Cut( 'Even',			'Even Events',				'event_number % 2 == 0'	)
cut_odd			= Cut( 'Odd',			'Odd Events',				'event_number % 2 == 1'	)

#----------------
# lepton criteria
#----------------
cut_lep_id_loose	= Cut( 'lepId_loose',		'Lepton ID loose',			'lep_0_id_loose && lep_1_id_loose' )
cut_lep_id_lm_mix	= Cut( 'lepId_lm_mix',		'Lepton ID 1 med & 1 loose',		'(lep_0_id_loose && lep_1_id_medium) || (lep_0_id_medium && lep_1_id_loose)' )
cut_lep_id_medium	= Cut( 'lepId_medium',		'Lepton ID medium',			'lep_0_id_medium && lep_1_id_medium' )
cut_lep_id_tight	= Cut( 'lepId_tight',		'Lepton ID tight',			'lep_0_id_tight && lep_1_id_tight' )

# Z-mass: 91.1876(21) GeV [pdg2015]
# Z-width: 2.4952(23) GeV [pdg2015]
cut_Z_window_4		= Cut( 'ZMassWindow_4',		'm_{Z} #pm ~4 GeV',			'dilepton_vis_mass > 87.188 && dilepton_vis_mass < 95.188' )
cut_Z_window_5		= Cut( 'ZMassWindow_5',		'm_{Z} #pm ~5 GeV',			'dilepton_vis_mass > 86.188 && dilepton_vis_mass < 96.188' )
cut_Z_window_8		= Cut( 'ZMassWindow_8',		'm_{Z} #pm ~8 GeV',			'dilepton_vis_mass > 83.188 && dilepton_vis_mass < 99.188' )
cut_Z_window_10		= Cut( 'ZMassWindow_10',	'm_{Z} #pm ~10 GeV',			'dilepton_vis_mass > 81.188 && dilepton_vis_mass < 101.188' )
cut_Z_window_nominal	= cut_Z_window_5
cut_Z_window_down	= cut_Z_window_4
cut_Z_window_up		= cut_Z_window_8

cut_lep_OS		= Cut( 'lepton_OS',		'OS for leptons',			'lep_0_q * lep_1_q < 0'	)
cut_di_ele		= Cut( 'dielectron',		'dielectron event',			'lep_0 == 2 && lep_1 == 2' )
cut_no_muon		= Cut( 'no_muon', 		'no muon in the event', 		'n_muons == 0')

# 2015 triggers
cut_trigger_low_2015_mc = Cut( 'trigger_low_mc', 'Trigger', 'HLT_e24_lhmedium_L1EM18VH  && eleTrigMatch_0_HLT_e24_lhmedium_L1EM18VH && lep_0_pt < 65.' )
cut_trigger_low_2015_data = Cut( 'trigger_low_mc', 'Trigger', 'HLT_e24_lhmedium_L1EM20VH  && eleTrigMatch_0_HLT_e24_lhmedium_L1EM20VH && lep_0_pt < 65.' )

cut_trigger_mid_2015	= Cut( 'trigger_mid', 'Trigger', 'HLT_e60_lhmedium && eleTrigMatch_0_HLT_e60_lhmedium && lep_0_pt < 135.' )
cut_trigger_high_2015	= Cut( 'trigger_high', 'Trigger', 'HLT_e120_lhloose && eleTrigMatch_0_HLT_e120_lhloose' )

# 2016 triggers
cut_trigger_low_2016 	= Cut( 'trigger_low_2016', 'Trigger', 'HLT_e26_lhtight_nod0_ivarloose && eleTrigMatch_0_HLT_e26_lhtight_nod0_ivarloose  && lep_0_pt < 65. ' )
cut_trigger_mid_2016 	= Cut( 'trigger_mid_2016', 'Trigger', 'HLT_e60_lhmedium_nod0 && eleTrigMatch_0_HLT_e60_lhmedium_nod0  && lep_0_pt < 135.' )
cut_trigger_high_2016 	= Cut( 'trigger_high_2016', 'Trigger', 'HLT_e140_lhloose_nod0 && eleTrigMatch_0_HLT_e140_lhloose_nod0')

# NOMINAL_pileup_random_run_number < 290000
cut_trigger_2015_mc	= cut_trigger_low_2015_mc | cut_trigger_mid_2015 | cut_trigger_high_2015
cut_trigger_2015_data	= cut_trigger_low_2015_data | cut_trigger_mid_2015 | cut_trigger_high_2015

# NOMINAL_pileup_random_run_number > 290000
cut_trigger_2016_mc 	= cut_trigger_low_2016 | cut_trigger_mid_2016 | cut_trigger_high_2016
cut_trigger_2016_data 	= cut_trigger_low_2016 | cut_trigger_mid_2016 | cut_trigger_high_2016

cut_mc_is_2015		= Cut( 'cut_mc_is_2015', 'Select 2015 Events Only', 'NOMINAL_pileup_random_run_number < 290000')
cut_mc_is_2016 		= Cut( 'cut_mc_is_2016', 'Select 2016 Events Only', 'NOMINAL_pileup_random_run_number > 290000')
cut_data_is_2015 	= Cut( 'cut_data_is_2015', 'Select 2015 Events Only', 'run_number < 290000')
cut_data_is_2016 	= Cut( 'cut_data_is_2016', 'Select 2016 Events Only', 'run_number > 290000')

# mc/data triggers
cut_is_mc               = Cut( 'trigger_is_mc',  'Trigger', ' (run_number == 222525 || run_number == 222526)' )
cut_is_data             = Cut( 'trigger_is_data', 'Trigger', ' (run_number != 222525 || run_number != 222526)' )

cut_trigger_mc 		= (cut_mc_is_2015 & cut_trigger_2015_mc) | (cut_mc_is_2016 & cut_trigger_2016_mc) 
cut_trigger_data 	= (cut_data_is_2015 & cut_trigger_2015_data) | (cut_data_is_2015 & cut_trigger_2016_data) 
#cut_trigger		= (cut_is_mc & cut_trigger_mc) | (cut_is_data & cut_trigger_data)

cut_trigger             = Cut( 'trigger', 'Trigger', 'Alt$( ( NOMINAL_pileup_random_run_number < 290000 && ( ( lep_0_pt<65. && HLT_e24_lhmedium_L1EM20VH && eleTrigMatch_0_HLT_e24_lhmedium_L1EM20VH )  || ( lep_0_pt<135 && eleTrigMatch_0_HLT_e60_lhmedium && HLT_e60_lhmedium ) || (eleTrigMatch_0_HLT_e120_lhloose && HLT_e120_lhloose ) ) ) || ( NOMINAL_pileup_random_run_number > 290000 && ( ( lep_0_pt<65. && HLT_e26_lhtight_nod0_ivarloose && eleTrigMatch_0_HLT_e26_lhtight_nod0_ivarloose ) || ( lep_0_pt<135 && eleTrigMatch_0_HLT_e60_lhmedium_nod0 && HLT_e60_lhmedium_nod0 ) || (eleTrigMatch_0_HLT_e140_lhloose_nod0 && HLT_e140_lhloose_nod0 ) ) ) , ( run_number < 290000 && ( ( lep_0_pt<65. && HLT_e24_lhmedium_L1EM20VH && eleTrigMatch_0_HLT_e24_lhmedium_L1EM20VH )  || ( lep_0_pt<135 && eleTrigMatch_0_HLT_e60_lhmedium && HLT_e60_lhmedium ) || (eleTrigMatch_0_HLT_e120_lhloose && HLT_e120_lhloose ) ) ) || ( run_number > 290000 && ( ( lep_0_pt<65. && HLT_e26_lhtight_nod0_ivarloose && eleTrigMatch_0_HLT_e26_lhtight_nod0_ivarloose ) || ( lep_0_pt<135 && eleTrigMatch_0_HLT_e60_lhmedium_nod0 && HLT_e60_lhmedium_nod0 ) || (eleTrigMatch_0_HLT_e140_lhloose_nod0 && HLT_e140_lhloose_nod0 ) ) ) )' )

#cut_trigger		= cut_trigger_low_mc | cut_trigger_low_data | cut_trigger_mid | cut_trigger_high
#cut_lep_iso		= Cut( 'lepton_iso'		'Lepton Isolation',			'lep_0_iso_wp > 10000 && lep_1_iso_wp > 10000')
cut_lep_iso             = Cut( 'lepton_iso',            'Lepton Isolation',                     'lep_0_iso_Gradient && lep_1_iso_Gradient' )
cut_lep_pt		= Cut( 'lep_pt',		'Lepton pt',				'lep_0_pt > 26 && lep_1_pt > 20' )

#-------------
# tau criteria
#-------------
cut_tau_pt_20to30	= Cut( 'TauPt_20to30',		'Tau pt 20 to 30',			'20 < tau_0_pt && tau_0_pt < 30' )
cut_tau_pt_30to120	= Cut( 'TauPt_30to120',		'Tau pt 30 to 120',			'30 < tau_0_pt && tau_0_pt < 120' )
cut_tau_pt_20to25	= Cut( 'TauPt_20to25',		'Tau pt 20 to 25',			'20 < tau_0_pt && tau_0_pt < 25' )
cut_tau_pt_25to30	= Cut( 'TauPt_25to30',		'Tau pt 25 to 30',			'25 < tau_0_pt && tau_0_pt < 30' )
cut_tau_pt_30to40	= Cut( 'TauPt_30to40',		'Tau pt 30 to 40',			'30 < tau_0_pt && tau_0_pt < 40' )
cut_tau_pt_40to60	= Cut( 'TauPt_40to60',		'Tau pt 40 to 60',			'40 < tau_0_pt && tau_0_pt < 60' )
cut_tau_pt_60to120	= Cut( 'TauPt_60to120',		'Tau pt 60 to 120',			'60 < tau_0_pt && tau_0_pt < 120' )

cut_tau_id_loose	= Cut( 'tauId_loose',		'Tau ID loose',				'tau_0_jet_bdt_loose' )
cut_tau_id_medium	= Cut( 'tauId_medium',		'Tau ID medium',			'tau_0_jet_bdt_medium' )
cut_tau_id_tight	= Cut( 'tauId_tight',		'Tau ID tight',				'tau_0_jet_bdt_tight' )

cut_tau_olr_lep0	= Cut( 'TauOLR_lep0',		'Tau Overlap Removal (Lepton 0)',	'((abs(tau_0_phi - lep_0_phi) < pi) && sqrt(pow(tau_0_eta - lep_0_eta, 2) + pow(abs(tau_0_phi - lep_0_phi), 2)) > 0.4) || ((abs(tau_0_phi - lep_0_phi) >= pi) && sqrt(pow(tau_0_eta - lep_0_eta, 2) + pow(abs(abs(tau_0_phi - lep_0_phi) - 2*pi), 2)) > 0.4)'	)
cut_tau_olr_lep1	= Cut( 'TauOLR_lep1',		'Tau Overlap Removal (Lepton 1)',	'((abs(tau_0_phi - lep_1_phi) < pi) && sqrt(pow(tau_0_eta - lep_1_eta, 2) + pow(abs(tau_0_phi - lep_1_phi), 2)) > 0.4) || ((abs(tau_0_phi - lep_1_phi) >= pi) && sqrt(pow(tau_0_eta - lep_1_eta, 2) + pow(abs(abs(tau_0_phi - lep_1_phi) - 2*pi), 2)) > 0.4)'	)
cut_tau_olr_lep2	= Cut( 'TauOLR_lep2',		'Tau Overlap Removal (Lepton 2)',	'((abs(tau_0_phi - lep_2_phi) < pi) && sqrt(pow(tau_0_eta - lep_2_eta, 2) + pow(abs(tau_0_phi - lep_2_phi), 2)) > 0.4) || ((abs(tau_0_phi - lep_2_phi) >= pi) && sqrt(pow(tau_0_eta - lep_2_eta, 2) + pow(abs(abs(tau_0_phi - lep_2_phi) - 2*pi), 2)) > 0.4)'	)
cut_tau_olr		= cut_tau_olr_lep0 & cut_tau_olr_lep1

cut_tau_q		= Cut( 'tau_q',			'Tau Charge',				'abs(tau_0_q) == 1' )
cut_tau_q_pos		= Cut( 'tau_q_pos',		'pos. Tau Charge',			'tau_0_q > 0' )
cut_tau_q_neg		= Cut( 'tau_q_neg',		'neg. Tau Charge',			'tau_0_q < 0' )

cut_posProng		= Cut( 'PosProng',		'positive Prong',			'tau_0_n_tracks > 0' )
cut_1prong		= Cut( '1Prong',		'1 Prong',				'tau_0_n_tracks == 1' )
cut_3prong		= Cut( '3Prong',		'3 Prong',				'tau_0_n_tracks == 3' )
cut_1or3prong		= Cut( '1or3Prong',		'1or3 Prong',				'tau_0_n_tracks == 1 || tau_0_n_tracks == 3' )

cut_tau_pt		= Cut( 'TauPt',			'Tau pt',				'tau_0_pt > 20' )
cut_tau_eta		= Cut( 'TauEta',		'Tau eta',				'abs(tau_0_eta) < 2.5' )
cut_tau_crack		= Cut( 'TauCrack',		'Tau crack region',			'abs(tau_0_eta) > 1.52 || abs(tau_0_eta) < 1.37' )

cut_tau0_taumatch		= Cut( 'tau_match_true',		'Tau truth matching',			'abs(tau_0_matched_pdgId) == 15' )
cut_tau0_jetmatch_g		= Cut( 'tau_match_jet_g',		'Gluon-Jet truth matching',		'abs(tau_0_matched_pdgId) == 21' )
cut_tau0_jetmatch_q		= Cut( 'tau_match_jet_q',		'Quark-Jet truth matching',		'abs(tau_0_matched_pdgId) > 0 &&  abs(tau_0_matched_pdgId) <=4' )
cut_tau0_jetmatch		= Cut( 'tau_match_jet',			'Jet truth matching',			'(abs(tau_0_matched_pdgId) > 0 &&  abs(tau_0_matched_pdgId) <=4) || abs(tau_0_matched_pdgId) == 21' )
cut_tau0_zeromatch		= Cut( 'tau_match_zero',		'Zero truth matching',			'tau_0_matched_pdgId == 0' )
cut_tau0_zero_or_g		= Cut( 'tau_match_zero_or_g',		'Zero or Gluon truth matching',		'tau_0_matched_pdgId == 0 || tau_0_matched_pdgId == 21' )

cut_tau0_proper_zeromatch	= Cut( 'proper_tau_match_zero',		'proper Zero truth matching',		'tau_0_matched_proper_pdgId_match == 0'	)
cut_tau0_proper_nozeromatch	= Cut( 'proper_tau_match_nozero',	'proper Non Zero truth matching',	'tau_0_matched_proper_pdgId_match != 0'	)
cut_tau0_proper_noelematch	= Cut( 'proper_tau_match_noele',	'proper Non Ele truth matching',	'abs(tau_0_matched_proper_pdgId_match) != 11' )
cut_tau0_proper_jetmatch_g	= Cut( 'proper_tau_match_jet_g',	'proper Gluon-Jet truth matching',	'abs(tau_0_matched_proper_pdgId_match) == 21' )
cut_tau0_proper_jetmatch_q	= Cut( 'proper_tau_match_jet_q',	'proper Quark-Jet truth matching',	'tau_0_matched_proper_pdgId_match > 0 &&  tau_0_matched_proper_pdgId_match <=4'	)
cut_tau0_proper_jetmatch	= Cut( 'proper_tau_match_jet',		'proper Jet truth matching',		'(tau_0_matched_proper_pdgId_match > 0 &&  tau_0_matched_proper_pdgId_match <=4) || abs(tau_0_matched_proper_pdgId_match) == 21' )
cut_tau0_proper_zero_or_g	= Cut( 'proper_tau_match_zero_or_g',	'proper Zero or Gluon truth matching',	'tau_0_matched_proper_pdgId_match == 21 || tau_0_matched_proper_pdgId_match == 0' )

cut_tau0_TAT_zeromatch		= Cut( 'TAT_tau_match_zero',		'TAT Zero truth matching',		'tau_0_TAT_matched_pdgId == -1' )
cut_tau0_TAT_nozeromatch	= Cut( 'TAT_tau_match_nozero',		'TAT Non Zero truth matching',		'tau_0_TAT_matched_pdgId != 0' )
cut_tau0_TAT_noelematch		= Cut( 'TAT_tau_match_noele',		'TAT Non Ele truth matching',		'abs(tau_0_TAT_matched_pdgId) != 11' )
cut_tau0_TAT_jetmatch_g		= Cut( 'TAT_tau_match_jet_g',		'TAT Gluon-Jet truth matching',		'abs(tau_0_TAT_matched_pdgId) == 21' )
cut_tau0_TAT_jetmatch_q		= Cut( 'TAT_tau_match_jet_q',		'TAT Quark-Jet truth matching',		'tau_0_TAT_matched_pdgId > 0 &&  tau_0_TAT_matched_pdgId <=4' )
cut_tau0_TAT_jetmatch		= Cut( 'TAT_tau_match_jet',		'TAT Jet truth matching',		'(tau_0_TAT_matched_pdgId > 0 &&  tau_0_TAT_matched_pdgId <=4) || abs(tau_0_TAT_matched_pdgId) == 21' )
cut_tau0_TAT_zero_or_g		= Cut( 'TAT_tau_match_zero_or_g',	'TAT Zero or Gluon truth matching',	'tau_0_TAT_matched_pdgId == 21 || tau_0_TAT_matched_pdgId == -1' )

#---------------
# other criteria
#---------------
cut_dilepton_pt_vect	= Cut( 'dilepton_pt_vect',	'vect. sum of ee-pt',			'dilepton_vect_sum_pt > 15' )
cut_quark_enriched	= Cut( 'quark_enriched',	'quark enriched region',		'dilepton_vect_sum_pt > 25' )
cut_gluon_enriched	= Cut( 'gluon_enriched',	'gluon enriched region',		'dilepton_vect_sum_pt < 25' )

#---------------------------
# combine cuts to selections
#---------------------------
sel_lep		= cut_lep_pt & cut_trigger & cut_lep_iso & cut_lep_id_medium & cut_lep_OS & cut_di_ele & cut_no_muon
sel_tau		= cut_tau_pt & cut_tau_eta & cut_tau_olr & cut_tau_q & cut_tau_crack & cut_1or3prong
sel_tau_allP	= cut_tau_pt & cut_tau_eta & cut_tau_olr & cut_tau_q & cut_tau_crack
sel_tag		= cut_Z_window_nominal

sel_comb_allP	= sel_lep & sel_tau_allP
sel_comb	= sel_lep & sel_tau & sel_tag
sel_1p		= sel_comb & cut_1prong
sel_3p		= sel_comb & cut_3prong
