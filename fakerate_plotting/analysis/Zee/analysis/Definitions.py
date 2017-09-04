from plotting.Variable import Binning, Variable, VariableBinning
from plotting.Systematics import Systematics, SystematicsSet, SystematicVariation
#===================#
# Weight Expression #
#===================#
weight_total            = "weight_total"
# acutally used weight expression:
weight_expression       = weight_total

#==========#
# Binnings #
#==========#
bin_pt		= VariableBinning( [20, 25, 30, 40, 60, 120] )
bin_pt_lino	= VariableBinning( [50, 80, 120] )
bin_pt_equal	= Binning( 10, 20, 120 )
bin_pt_fine	= Binning( 24, 0, 120 )

bin_eta		= VariableBinning( [-2.5, -1.52, -1.37, -1.1, -0.05, 0.05, 1.1, 1.37, 1.52, 2.5] )
bin_eta_equal	= Binning( 15, -3, 3 )

bin_phi		= Binning( 11, -3.15, 3.15 )
bin_bdt		= Binning( 20, 0, 1)

#===========#
# Variables #
#===========#
#			  Variable( name,				variable,				x-axis title,					unit,		binning				)
var_run_number		= Variable( 'run_number',			'run_number',				'Run Number',					'',		Binning( 100, 250000, 350000)	)
var_pull		= Variable( 'pull',				'pull',					'Pull',						'',		Binning( 70, -3.5, 3.5)	)

var_weight_mc		= Variable( 'weight_mc',			'weight_mc',				'weight (MC)',					'',		Binning( 500, -2500, 2500)	)
var_weight_pileup	= Variable( 'weight_pileup',			'weight_pileup',			'weight (Pileup)',				'',		Binning( 11, -5, 5)		)
var_weight_total	= Variable( 'weight_total',			'weight_total',				'weight (Total)',				'',		Binning( 500, -2500, 2500)	)
var_weight_ZptSF	= Variable( 'weight_ZptSF',			'SF_dilepton_pt_vect',			'weight (ZptSF)',				'',		Binning( 40, 0, 2)	)

var_n_jets		= Variable( 'n_jets',				'n_jets',				'# jets',					'',		Binning( 13, -0.5, 12.5)	)
var_n_electrons		= Variable( 'n_electrons',			'n_electrons',				'# electrons',					'',		Binning( 13, -0.5, 12.5)	)
var_n_taus		= Variable( 'n_taus',				'n_taus',				'# taus',					'',		Binning( 13, -0.5, 12.5)	)
var_n_taus_l		= Variable( 'n_taus_loose',			'n_taus_loose',				'# loose taus',					'',		Binning( 13, -0.5, 12.5)	)
var_n_taus_m		= Variable( 'n_taus_medium',			'n_taus_medium',			'# medium taus',				'',		Binning( 13, -0.5, 12.5)	)
var_n_taus_t		= Variable( 'n_taus_tight',			'n_taus_tight',				'# tight taus',					'',		Binning( 13, -0.5, 12.5)	)
var_n_jets_taus		= Variable( 'n_jets_taus',			'n_jets+n_taus',			'# jets and taus',				'',		Binning( 13, -0.5, 12.5)	)
var_n_pileup		= Variable( 'n_pileup',				'n_avg_int_cor',			'average interactions per bunch crossing',	'',		Binning( 20, 0, 40)		)
var_n_vx		= Variable( 'n_vertices',			'n_vx',					'number of vertices',				'',		Binning( 25, 0, 25)		)

# Di-Lepton Variables
var_dilepton_vis_mas_fine	= Variable( 'dilepton_vis_mass_fine',	'dilepton_vis_mass',			'M_{ll}',					'GeV',		Binning( 30 ,60.,120.)		)
var_dilepton_vis_mass		= Variable( 'dilepton_vis_mass',	'dilepton_vis_mass',			'M_{ll}',					'GeV',		Binning( 50 ,40.,140.)		)
var_dilepton_pt_vect		= Variable( 'dilepton_pt_vect',		'dilepton_vect_sum_pt',			'p_{T} (ll)',					'GeV',		Binning( 40 ,0.,200.)		)
var_dilepton_pt_scal		= Variable( 'dilepton_pt_scal',		'dilepton_scal_sum_pt',			'scalar p_{T} (ll)',				'GeV',		Binning( 42 ,40.,250.)		)
var_dilepton_dr			= Variable( 'dilepton_dr',		'dilepton_dr',				'#Delta R_{ll}',				'',		Binning( 20 ,0.,4.5)		)
var_dilepton_deta		= Variable( 'dilepton_deta',		'dilepton_deta',			'#Delta #eta_{ll}',				'',		Binning( 20 ,0.,3.)		)
var_dilepton_dphi		= Variable( 'dilepton_dphi',		'dilepton_dphi',			'#Delta #phi_{ll}',				'',		Binning( 20 ,0.,3.14)		)

# Single Lepton Variables
var_lep0_pt		= Variable( 'lep_0_pt',				'lep_0_pt',				'p_{T} #left(lep^{leading}#right)',		'GeV',		bin_pt				)
var_lep0_eta		= Variable( 'lep_0_eta',			'lep_0_eta',				'#eta #left(lep^{leading}#right)',		'',		bin_eta				)
var_lep0_phi		= Variable( 'lep_0_phi',			'lep_0_phi',				'#phi #left(lep^{leading}#right)',		'',		bin_phi				)
var_lep0_pt_fine	= Variable( 'lep_0_pt_fine',			'lep_0_pt',				'p_{T} #left(lep^{leading}#right)',		'GeV',		bin_pt_fine			)
var_lep0_pt_equal	= Variable( 'lep_0_pt_equal',			'lep_0_pt',				'p_{T} #left(lep^{leading}#right)',		'GeV',		bin_pt_equal			)
var_lep0_eta_equal	= Variable( 'lep_0_eta',			'lep_0_eta',				'#eta #left(lep^{leading}#right)',		'',		bin_eta_equal			)

var_lep1_pt		= Variable( 'lep_1_pt',				'lep_1_pt',				'p_{T} #left(lep^{sub-leading}#right)',		'GeV',		bin_pt				)
var_lep1_eta		= Variable( 'lep_1_eta',			'lep_1_eta',				'#eta #left(lep^{sub-leading}#right)',		'',		bin_eta				)
var_lep1_phi		= Variable( 'lep_1_phi',			'lep_1_phi',				'#phi #left(lep^{sub-leading}#right)',		'',		bin_phi				)
var_lep1_pt_fine	= Variable( 'lep_1_pt_fine',			'lep_1_pt',				'p_{T} #left(lep^{sub-leading}#right)',		'GeV',		bin_pt_fine			)
var_lep1_pt_equal	= Variable( 'lep_1_pt_equal',			'lep_1_pt',				'p_{T} #left(lep^{sub-leading}#right)',		'GeV',		bin_pt_equal			)
var_lep1_eta_equal	= Variable( 'lep_1_eta',			'lep_1_eta',				'#eta #left(lep^{sub-leading}#right)',		'',		bin_eta_equal			)

# Tau Variables
var_tau0_pt_lino	= Variable( 'tau_0_pt_lino',			'tau_0_pt',				'p_{T} #left(#tau_{had}^{leading}#right)',			'GeV',		bin_pt_lino			)
var_tau0_pt_one_bin	= Variable( 'tau_0_pt_single_bin',		'tau_0_pt',				'p_{T} #left(#tau_{had}^{leading}#right)',			'GeV',		Binning( 1, 20, 120)		)
var_tau0_pt_two_bins	= Variable( 'tau_0_pt_two_bins',		'tau_0_pt',				'p_{T} #left(#tau_{had}^{leading}#right)',			'GeV',		VariableBinning([20, 30, 120])	)
var_tau0_pt		= Variable( 'tau_0_pt',				'tau_0_pt',				'p_{T} #left(#tau_{had}^{leading}#right)',			'GeV',		bin_pt				)
var_tau0_eta		= Variable( 'tau_0_eta',			'tau_0_eta',				'#eta #left(#tau_{had}^{leading}#right)',			'',		bin_eta				)
var_tau0_phi		= Variable( 'tau_0_phi',			'tau_0_phi',				'#phi #left(#tau_{had}^{leading}#right)',			'',		bin_phi				)
var_tau0_pt_fine	= Variable( 'tau_0_pt_fine',			'tau_0_pt',				'p_{T} #left(#tau_{had}^{leading}#right)',			'GeV',		bin_pt_fine			)
var_tau0_pt_equal	= Variable( 'tau_0_pt_equal',			'tau_0_pt',				'p_{T} #left(#tau_{had}^{leading}#right)',			'GeV',		bin_pt_equal			)
var_tau0_eta_equal	= Variable( 'tau_0_eta_equal',			'tau_0_eta',				'#eta #left(#tau_{had}^{leading}#right)',			'',		bin_eta_equal			)

var_tau0_q_eta		= Variable( 'tau_0_q_eta',			'tau_0_q * tau_0_eta',			'q #cdot #eta #left(#tau_{had}^{leading}#right)',		'',		bin_eta				)
var_tau0_ntracks	= Variable( 'tau_0_n_tracks',			'tau_0_n_tracks',			'# tracks #left(#tau_{had}^{leading}#right)',			'',		Binning( 13, -0.5, 12.5)	)
var_tau0_q		= Variable( 'tau_0_q',				'tau_0_q',				'charge #left(#tau_{had}^{leading}#right)',			'',		Binning( 11, -5.5, 5.5)		)
var_tau0_bdt		= Variable( 'tau_0_bdt',			'tau_0_jet_bdt_score',			'BDT score #left(#tau_{had}^{leading}#right)',			'',		bin_bdt				)
var_tau0_width		= Variable( 'tau_0_width',			'tau_0_jet_width',			'W #left(#tau_{had}^{leading}#right)',			'',		Binning( 30, 0, 0.3)		)

var_tau0_z0		= Variable( 'tau_0_leadTrk_z0',			'tau_0_leadTrk_z0',			'z0 #left(#tau_{had}^{leading}#right)',				'',		Binning( 30, -200, 200)		)
var_tau0_d0		= Variable( 'tau_0_leadTrk_d0',			'tau_0_leadTrk_d0',			'd0 #left(#tau_{had}^{leading}#right)',				'',		Binning( 30, -0.5, 0.5)		)
var_tau0_z0_wide	= Variable( 'tau_0_leadTrk_z0_wide',		'tau_0_leadTrk_z0',			'z0 #left(#tau_{had}^{leading}#right)',				'',		Binning( 30, -1300, 200)	)
var_tau0_d0_wide	= Variable( 'tau_0_leadTrk_d0_wide',		'tau_0_leadTrk_d0',			'd0 #left(#tau_{had}^{leading}#right)',				'',		Binning( 30, -1300, 200)	)
var_tau0_z0_sig		= Variable( 'tau_0_leadTrk_z0_sig',		'tau_0_leadTrk_z0_sig',			'z0_sig #left(#tau_{had}^{leading}#right)',			'',		Binning( 30, -3000, 3000)	)
var_tau0_d0_sig		= Variable( 'tau_0_leadTrk_d0_sig',		'tau_0_leadTrk_d0_sig',			'd0_sig #left(#tau_{had}^{leading}#right)',			'',		Binning( 30, -10, 10)		)
var_tau0_z0_sintheta	= Variable( 'tau_0_leadTrk_z0_sintheta',	'tau_0_leadTrk_z0_sintheta',		'z0 sin(#theta) #left(#tau_{had}^{leading}#right)',		'',		Binning( 30, -200, 200)		)

var_tau0_TATmatch	= Variable( 'tau_0_TAT_matched_pdgId',		'tau_0_TAT_matched_pdgId',		'TAT matched pdgId #left(#tau_{had}^{leading}#right)',		'',		Binning( 61, -30.5, 30.5)	)
var_tau0_match		= Variable( 'tau_0_matched_pdgId',		'tau_0_matched_pdgId',			'Timo matched pdgId #left(#tau_{had}^{leading}#right)',		'',		Binning( 61, -30.5, 30.5)	)
var_tau0_proper_pdgId	= Variable( 'tau_0_proper_pdgId',		'tau_0_matched_proper_pdgId_match',	'properly matched pdgId #left(#tau_{had}^{leading}#right)',	'',		Binning( 61, -30.5, 30.5)	)

var_tau0_id_centFracCorrected		= Variable( 'centFracCorrected',		'tau_0_centFracCorrected',		"f_{cent}",			'',		Binning( 25, 0, 1)		)
var_tau0_id_etOverPtLeadTrkCorrected	= Variable( 'etOverPtLeadTrkCorrected',		'tau_0_etOverPtLeadTrkCorrected',	"f^{-1}_{leadtrack}",		'',		Binning( 25, 0, 5)		)
var_tau0_id_innerTrkAvgDistCorrected	= Variable( 'innerTrkAvgDistCorrected',		'tau_0_innerTrkAvgDistCorrected',	"R^{0.2}_{track}",		'',		Binning( 25, 0, 0.2)		)
var_tau0_id_ipSigLeadTrkCorrected	= Variable( 'ipSigLeadTrkCorrected',		'tau_0_ipSigLeadTrkCorrected',		"#||{S_{Leadtrack}}",		'',		Binning( 25, 0, 5)		)
var_tau0_id_SumPtTrkFracCorrected	= Variable( 'SumPtTrkFracCorrected',		'tau_0_SumPtTrkFracCorrected',		"f^{track}_{iso}",		'',		Binning( 25, 0, 0.5)		)
var_tau0_id_ptRatioEflowApproxCorrected	= Variable( 'ptRatioEflowApproxCorrected',	'tau_0_ptRatioEflowApproxCorrected',	"p_{T}^{EM+track}/p_{T}",	'',		Binning( 25, 0, 1.2)		)
var_tau0_id_mEflowApproxCorrected	= Variable( 'mEflowApproxCorrected',		'tau_0_mEflowApproxCorrected',		"m_{EM+track}",			'MeV',		Binning( 25, 0, 5000)		)
var_tau0_id_ChPiEMEOverCaloEMECorrected	= Variable( 'ChPiEMEOverCaloEMECorrected',	'tau_0_ChPiEMEOverCaloEMECorrected',	"f^{track-HAD}_{EM}",		'',		Binning( 25, -2, 2)		)
var_tau0_id_EMPOverTrkSysPCorrected	= Variable( 'EMPOverTrkSysPCorrected',		'tau_0_EMPOverTrkSysPCorrected',	"f^{EM}_{track}",		'',		Binning( 25, 0, 8)		)
var_tau0_id_dRmaxCorrected		= Variable( 'dRmaxCorrected',			'tau_0_dRmaxCorrected',			"#DeltaR_{Max}",		'',		Binning( 25, 0, 0.22)		)
var_tau0_id_trFlightPathSigCorrected	= Variable( 'trFlightPathSigCorrected',		'tau_0_trFlightPathSigCorrected',	"S^{flight}_{T}",		'',		Binning( 25, -5, 15)		)
var_tau0_id_massTrkSysCorrected		= Variable( 'massTrkSysCorrected',		'tau_0_massTrkSysCorrected',		"m_{track}",			'MeV',		Binning( 25, 0, 4000)		)

#=============#
# Systematics #
#=============#
sys_Tau_INSITU    = Systematics.treeSystematics( 'tau_tes_insitu',      'Tau TES Insitu',
                    upTreeName=     'TAUS_TRUEHADTAU_SME_TES_INSITU_1up',
                    downTreeName=   'TAUS_TRUEHADTAU_SME_TES_INSITU_1down',
                    nominalTreeName='NOMINAL')
sys_Tau_MODEL     = Systematics.treeSystematics( 'tau_tes_model',       'Tau TES Model',
                    upTreeName=     'TAUS_TRUEHADTAU_SME_TES_MODEL_1up',
                    downTreeName=   'TAUS_TRUEHADTAU_SME_TES_MODEL_1down',
                    nominalTreeName='NOMINAL')
sys_Tau_DETECTOR  = Systematics.treeSystematics( 'tau_tes_detector',    'Tau TES Detector',
                    upTreeName=     'TAUS_TRUEHADTAU_SME_TES_DETECTOR_1up',
                    downTreeName=   'TAUS_TRUEHADTAU_SME_TES_DETECTOR_1down',
                    nominalTreeName='NOMINAL')

sys_TES = SystematicsSet()
sys_TES.add( sys_Tau_INSITU   )
sys_TES.add( sys_Tau_MODEL    )
sys_TES.add( sys_Tau_DETECTOR )


sys_EG_RESOLUTION = Systematics.treeSystematics( 'egamma_resolution',   'EGamma Resolution',
                    upTreeName=     'EG_RESOLUTION_ALL_1up',
                    downTreeName=   'EG_RESOLUTION_ALL_1down',
                    nominalTreeName='NOMINAL')
sys_EG_SCALE      = Systematics.treeSystematics( 'egamma_scale',        'EGamma Scale',
                    upTreeName=     'EG_SCALE_ALLCORR_1up',
                    downTreeName=   'EG_SCALE_ALLCORR_1down',
                    nominalTreeName='NOMINAL')

sys_EG  = SystematicsSet()
sys_EG.add( sys_EG_RESOLUTION )
sys_EG.add( sys_EG_SCALE      )


sys_Pu_PRW        = Systematics.weightSystematics('pu_prw',	'Pileup PRW',
                    upWeightExpression=     'pu_PRW_DATASF_1up_pileup_combined_weight',
                    downWeightExpression=   'pu_PRW_DATASF_1down_pileup_combined_weight',
                    nominalWeightExpression='pu_NOMINAL_pileup_combined_weight')

sys_Pu  = SystematicsSet()
sys_Pu.add( sys_Pu_PRW        )


sys_Ele_MEDIUMLLH = Systematics.weightSystematics( 'ele_sf_mediumLLH',	'Ele SF MediumLLH',
                    upWeightExpression=     'lep_0_EL_EFF_ID_TOTAL_1NPCOR_PLUS_UNCOR_1up_EleEffSF_offline_MediumLLH_d0z0_v11',
                    downWeightExpression=   'lep_0_EL_EFF_ID_TOTAL_1NPCOR_PLUS_UNCOR_1down_EleEffSF_offline_MediumLLH_d0z0_v11',
                    nominalWeightExpression='lep_0_NOMINAL_EleEffSF_offline_MediumLLH_d0z0_v11')
sys_Ele_RECOTRK   = Systematics.weightSystematics( 'ele_sf_recotrk',	'Ele SF Reco Track',
                    upWeightExpression=     'lep_0_EL_EFF_Reco_TOTAL_1NPCOR_PLUS_UNCOR_1up_EleEffSF_offline_RecoTrk',
                    downWeightExpression=   'lep_0_EL_EFF_Reco_TOTAL_1NPCOR_PLUS_UNCOR_1down_EleEffSF_offline_RecoTrk',
                    nominalWeightExpression='lep_0_NOMINAL_EleEffSF_offline_RecoTrk')
sys_Ele_ISOLATION = Systematics.weightSystematics( 'ele_sf_iso',	'Ele SF Isolation',
                    upWeightExpression=     'lep_0_EL_EFF_Iso_TOTAL_1NPCOR_PLUS_UNCOR_1up_EleEffSF_Isolation_MediumLLH_d0z0_v11_isolGradient',
                    downWeightExpression=   'lep_0_EL_EFF_Iso_TOTAL_1NPCOR_PLUS_UNCOR_1down_EleEffSF_Isolation_MediumLLH_d0z0_v11_isolGradient',
                    nominalWeightExpression='lep_0_NOMINAL_EleEffSF_Isolation_MediumLLH_d0z0_v11_isolGradient')
sys_Ele_TRIGGER   = Systematics.weightSystematics( 'ele_sf_trigger',	'Ele SF Trigger',
                    upWeightExpression=     'lep_0_EL_EFF_Trigger_TOTAL_1NPCOR_PLUS_UNCOR_1up_EleEffSF_SINGLE_E_2015_e24_lhmedium_L1EM20VH_OR_e60_lhmedium_OR_e120_lhloose_2016_e26_lhtight_nod0_ivarloose_OR_e60_lhmedium_nod0_OR_e140_lhloose_nod0_MediumLLH_d0z0_v11_isolGradient',
                    downWeightExpression=   'lep_0_EL_EFF_Trigger_TOTAL_1NPCOR_PLUS_UNCOR_1down_EleEffSF_SINGLE_E_2015_e24_lhmedium_L1EM20VH_OR_e60_lhmedium_OR_e120_lhloose_2016_e26_lhtight_nod0_ivarloose_OR_e60_lhmedium_nod0_OR_e140_lhloose_nod0_MediumLLH_d0z0_v11_isolGradient',
                    nominalWeightExpression='lep_0_NOMINAL_EleEffSF_SINGLE_E_2015_e24_lhmedium_L1EM20VH_OR_e60_lhmedium_OR_e120_lhloose_2016_e26_lhtight_nod0_ivarloose_OR_e60_lhmedium_nod0_OR_e140_lhloose_nod0_MediumLLH_d0z0_v11_isolGradient')

sys_ELE = SystematicsSet()
sys_ELE.add( sys_Ele_MEDIUMLLH )
sys_ELE.add( sys_Ele_RECOTRK   )
sys_ELE.add( sys_Ele_ISOLATION )
sys_ELE.add( sys_Ele_TRIGGER   )


systSet = SystematicsSet()
systSet |= sys_TES
systSet |= sys_ELE
systSet |= sys_EG
#systSet |= sys_Pu

systVar = SystematicVariation( 'systVar', "All Systematics")
systVar.systematics = systSet
