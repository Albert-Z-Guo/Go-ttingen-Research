// ROOT macro to compute the invariant mass of the two leading leptons
// in an n-tuple and store the result as a new TBranch
#include <dirent.h>

void computeInvariantMass(string fileName) {
   TFile *file = new TFile(fileName.c_str(), "update");
   TTree *tree = (TTree*) file->Get("NOMINAL");

   double lep_m_01, lep_m_02, lep_m_12;
   TBranch *b_dilepton_vis_mass = tree->Branch("dilepton_vis_mass", &lep_m_01, "dilepton_vis_mass/D");
   TBranch *b_lep_m_01 = tree->Branch("lep_m_01", &lep_m_01, "lep_m_01/D");
   TBranch *b_lep_m_02 = tree->Branch("lep_m_02", &lep_m_02, "lep_m_02/D");
   TBranch *b_lep_m_12 = tree->Branch("lep_m_12", &lep_m_12, "lep_m_12/D");

   double lep_0_pt, lep_0_eta, lep_0_phi, lep_0_m;
   tree->SetBranchAddress("lep_0_pt", &lep_0_pt);
   tree->SetBranchAddress("lep_0_eta", &lep_0_eta);
   tree->SetBranchAddress("lep_0_phi", &lep_0_phi);
   tree->SetBranchAddress("lep_0_m", &lep_0_m);
   double lep_1_pt, lep_1_eta, lep_1_phi, lep_1_m;
   tree->SetBranchAddress("lep_1_pt", &lep_1_pt);
   tree->SetBranchAddress("lep_1_eta", &lep_1_eta);
   tree->SetBranchAddress("lep_1_phi", &lep_1_phi);
   tree->SetBranchAddress("lep_1_m", &lep_1_m);
   double lep_2_pt, lep_2_eta, lep_2_phi, lep_2_m;
   tree->SetBranchAddress("lep_2_pt", &lep_2_pt);
   tree->SetBranchAddress("lep_2_eta", &lep_2_eta);
   tree->SetBranchAddress("lep_2_phi", &lep_2_phi);
   tree->SetBranchAddress("lep_2_m", &lep_2_m);

   Long64_t nentries = tree->GetEntries();
   for (Long64_t i=0; i < nentries; i++) {
      tree->GetEntry(i);

      TLorentzVector p0, p1, p2;
      p0.SetPtEtaPhiM(lep_0_pt, lep_0_eta, lep_0_phi, lep_0_m);
      p1.SetPtEtaPhiM(lep_1_pt, lep_1_eta, lep_1_phi, lep_1_m);
      p2.SetPtEtaPhiM(lep_2_pt, lep_2_eta, lep_2_phi, lep_2_m);

      TLorentzVector m01, m02, m12;
      m01 = p0 + p1;	lep_m_01 = m01.M();
      m02 = p0 + p2;	lep_m_02 = m02.M();
      m12 = p1 + p2;	lep_m_12 = m12.M();

      b_dilepton_vis_mass->Fill();
      b_lep_m_01->Fill();
      b_lep_m_02->Fill();
      b_lep_m_12->Fill();
   }

   tree->Write();
   delete file;
}

void recursive_apply_to_folders(string base, string file) {
    if (file == "." || file == "..")
	return;
    path = base + "/" + file;

    if (path.length() >= 5 && path.substr(path.length()-5, 5) == ".root") {
	// check, if the file fits one of the exeptions
	vector<string> exeptions = {"mc15_13TeV", "00276982", "00277061", "00277064", "00279255", "00279258", "00279260"};
	for (unsigned i = 0; i < exeptions.size(); i++) {
	    string exeption = exeptions.at(i);
	    if (path.find(exeption) != string::npos) {
		cout << "skipping file: " << path << endl;
		cout << "...because its name containes: " << exeption << endl;
		return;
	    }
	}
	// run on the file
	cout << "now running on: " << path << endl;
	computeInvariantMass(path);
    } else {
	// if its a directory, run recursively
	DIR *dir;
	struct dirent *ent;
	if ((dir = opendir(path.c_str())) != NULL) {
	    while ((ent = readdir (dir)) != NULL) {
		recursive_apply_to_folders( path, ent->d_name);
	    }
	    closedir (dir);
	}
    }
}

void apply_to_all_Files() {
    string sonas = "/nfs/dust/atlas/user/tidreyer/ntuple";
    //string folder = "GRID_160205";
    string folder = "output-20160413-Zmumucheck-TAUP1-common_lephad_eVeto_test-3_root";
    recursive_apply_to_folders( sonas, folder);
}
