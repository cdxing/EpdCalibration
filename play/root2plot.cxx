void root2plot(TString file = "Normal.picoDst.result.combined.root") {
   TFile *f1 = TFile::Open(file);
   TString fpdf = ".pdf" ;
   TString fout = file + fpdf;
   TIter keyList(f1->GetListOfKeys());
   TKey *key;
   TCanvas c1;
   c1.SetLogz();
   c1.Print(fout+'[');
   while ((key = (TKey*)keyList())) {
      TClass *cl = gROOT->GetClass(key->GetClassName());
      if (cl->InheritsFrom("TH1")){
      		TH1 *h = (TH1*)key->ReadObj();
      		h->Draw("colz");
      		c1.Print(fout);
      } else  
      if (cl->InheritsFrom("TH2")){
      	TH2 *h = (TH2*)key->ReadObj();
      	h->Draw("colz");
      	c1.Print(fout);
      } else
      if (cl->InheritsFrom("TH3")){
      	TH3 *h = (TH3*)key->ReadObj();
      	h->Draw("colz");
      	c1.Print(fout);
      } else
      if (cl->InheritsFrom("TTree")){
      	TTree *t = (TTree*)key->ReadObj();
      	TObjArray * branchList = t->GetListOfBranches();
      	for(int i = 0; i < branchList->GetEntries() ; i++)
      	  {
      	  	 t->Draw(branchList->At(i)->GetName());
      			 c1.Print(fout);
      	  }
      } else continue;
   }
   c1.Print(fout+']');
}
