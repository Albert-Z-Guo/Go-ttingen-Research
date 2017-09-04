void fractionElectrons(TH1* histo, string name);

void countMatchPDGID() {
   TFile *file = new TFile("/afs/desy.de/user/t/tidreyer/plottingCode/trunk/analysis/Zee/root-files/SelectionPlots.root");
   TDirectory *Zee;
   file->GetObject("Zee", Zee);
   Zee->cd();

   TH1 *no_cut, *sel, *loose, *medium, *tight;
   Zee->GetObject("matched_pdgId_tau_0_NoCut", no_cut);
   Zee->GetObject("matched_pdgId_tau_0_lepId_medium_AND_ZMassWindow_5_AND_lepton_OS_AND_TauPt_AND_TauEta_AND_TauOLR_lep0_AND_TauOLR_lep1_AND_TauCrack_AND_PosProng", sel);
   Zee->GetObject("matched_pdgId_tau_0_lepId_medium_AND_ZMassWindow_5_AND_lepton_OS_AND_TauPt_AND_TauEta_AND_TauOLR_lep0_AND_TauOLR_lep1_AND_TauCrack_AND_PosProng_AND_tauId_loose", loose);
   Zee->GetObject("matched_pdgId_tau_0_lepId_medium_AND_ZMassWindow_5_AND_lepton_OS_AND_TauPt_AND_TauEta_AND_TauOLR_lep0_AND_TauOLR_lep1_AND_TauCrack_AND_PosProng_AND_tauId_medium", medium);
   Zee->GetObject("matched_pdgId_tau_0_lepId_medium_AND_ZMassWindow_5_AND_lepton_OS_AND_TauPt_AND_TauEta_AND_TauOLR_lep0_AND_TauOLR_lep1_AND_TauCrack_AND_PosProng_AND_tauId_tight", tight);

   // no cut
   fractionElectrons( no_cut,	"no cut");
   fractionElectrons( sel,	"selection");
   fractionElectrons( loose,	"selection + loose");
   fractionElectrons( medium,	"selection + medium");
   fractionElectrons( tight,	"selection + tight");

   delete file;

   return;
}

void fractionElectrons(TH1* histo, string name) {
   int bin_neg11	= histo->FindBin(-11);
   int bin_neg6		= histo->FindBin(-6);
   int bin_neg1		= histo->FindBin(-1);
   int bin_zero		= histo->FindBin(0);
   int bin_pos1		= histo->FindBin(1);
   int bin_pos6		= histo->FindBin(6);
   int bin_pos11	= histo->FindBin(11);
   int bin_pos21	= histo->FindBin(21);

   double integral	= histo->Integral();
   double electrons	= histo->GetBinContent(bin_neg11) + histo->GetBinContent(bin_pos11);
   double quarks	= histo->Integral(bin_neg6, bin_neg1) + histo->Integral(bin_pos1, bin_pos6);
   double gluons	= histo->GetBinContent(bin_pos21);
   double zero		= histo->GetBinContent(bin_zero);

   cout << name << endl;
   cout << "----------------------------------------" << endl;
   cout << "Percentage jets:\t"		<< 100*(quarks+gluons)/integral		<< endl;
   cout << "Percentage electrons:\t"	<< 100*electrons/integral		<< endl;
   cout << "Percentage zeros:\t"	<< 100*zero/integral			<< endl;
   cout << "Percentage rest:\t"		<< 100*(1 - (electrons+quarks+gluons+zero)/integral)		<< endl;
   cout << endl;
   cout << "Fraction ele/jets:\t"	<< electrons/(quarks+gluons)		<< endl;
   cout << "Fraction quark/gluon:\t"	<< quarks/gluons			<< endl;
   cout << endl;
   cout << endl;

   return;
}
