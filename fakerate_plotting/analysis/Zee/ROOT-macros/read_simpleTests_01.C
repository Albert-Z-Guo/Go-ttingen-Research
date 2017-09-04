void read_simpleTest_01() {
   TFile* file = new TFile("/afs/desy.de/user/t/tidreyer/plottingCode/trunk/analysis/Zee/root-files/simpleTests_01.root");

   const int N_HISTOS = 3;

   string histo[N_HISTOS]={tau_0_pt_NoCut, tau_0_pt_a_NoCut, tau_0_pt_b_TauPt};

   for (int i = 0; i < N_HISTOS; i++) {
      TH1D* current_histo = (TH1D*) file->GetObjectChecked(histo[i], "TH1D")
      cout																<< endl;
      cout << "INFO:  un-normalized:"													<< endl;
      cout																<< endl;
      cout << "INFO:  Integral:\t\t\t"		<< current_histo->Integral()				<< endl;
      cout << "INFO:  Mean:\t\t\t"		<< current_histo->GetMean()				<< endl;
      cout << "INFO:  RMS:\t\t\t"		<< current_histo->GetRMS()				<< endl;
      cout																<< endl;
      for (int i_bin = 0; i_bin <= 21; i_bin++)
	 cout
	    << "INFO:  Bin "		<< binNo_string(i_bin, current_histo)
	    << "\tfrom "		<< current_histo->GetBinLowEdge(i_bin)
	    << "\tto "			<< current_histo->GetBinLowEdge(i_bin)+current_histo->GetBinWidth(i_bin)
	    << "\thas "			<< current_histo->GetBinContent(i_bin)
	    << "\tEntries"														<< endl;
//      cout																<< endl;
//      cout << "INFO:  normalized:"													<< endl;
//      TH1D* norm_copy = (TH1D*) current_histo->Clone();
//      norm_copy->Scale(1.0/norm_copy->Integral());
//      cout																<< endl;
//      cout << "INFO:  Integral:\t\t\t"		<< norm_copy->Integral()								<< endl;
//      cout << "INFO:  Mean:\t\t\t"		<< norm_copy->GetMean()									<< endl;
//      cout << "INFO:  RMS:\t\t\t"		<< norm_copy->GetRMS()									<< endl;
//      cout																<< endl;
//      for (int i_bin = 0; i_bin <= 21; i_bin++)
//	 cout
//	    << "INFO:  Bin "		<< binNo_string(i_bin, norm_copy)
//	    << "\tfrom "		<< norm_copy->GetBinLowEdge(i_bin)
//	    << "\tto "			<< norm_copy->GetBinLowEdge(i_bin)+norm_copy->GetBinWidth(i_bin)
//	    << "\thas "			<< norm_copy->GetBinContent(i_bin)
//	    << "\tEntries"														<< endl;
//      delete norm_copy;
//      norm_copy = nullptr;
      cout																<< endl;
      cout																<< endl;
   }
}
