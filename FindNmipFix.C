/* Author: Skipper Kagamaster
 *
 * Update: Rebin
 * Author: Ding Chen
 * Date : Feb 28, 2020
 *
 * Update: Day => Run
 * Author: Ding Chen
 * Date : Nov 20, 2020
 */

#include <fstream>      // std::filebuf

#define nMipsMax 3       // Set the maximum MIPs to consider.
TF1* MipPeak[nMipsMax];
Double_t myfunc(Double_t* x, Double_t* param);  // Fit function used by Minuit.

void FindNmipFix(){

  std::ofstream NmipFile("NmipConstantsFix.txt",ofstream::out);
  // TPaveLabel *title;

  TCanvas *c1 = new TCanvas("c1","ADC",600,600);
  gStyle->SetOptTitle(1);
  c1->SaveAs("ADCspectraFix.pdf[");

  bool runQuit = 0;
  while(runQuit == 0)
  {
    cout << "Enter the run to be refit: ";
    int run;
    cin >> run;

    gStyle->SetOptStat(0);
    gStyle->SetTitleSize(0.1,"t");

    Float_t SingleMipPeakStartingValue,FitRangeLow,FitRangeHigh;
    FitRangeHigh               = 1500.0;  // High edge of range along the x-axis.
    Float_t xlo(0),xhi(16384);

    TF1* func = new TF1("MultiMipFit",myfunc,xlo,xhi,nMipsMax+2);

    // (1) ===================== Define the functions ==============================
    MipPeak[0] = new TF1("1MIP","TMath::Landau(x,[0],[1],1)",xlo,xhi);
    for (Int_t nMIP=2; nMIP<=nMipsMax; nMIP++){
      TF1Convolution* c = new TF1Convolution(MipPeak[nMIP-2],MipPeak[0],xlo,xhi,true);
      MipPeak[nMIP-1] = new TF1(Form("%dMIPs",nMIP),c,xlo,xhi,2*nMIP);
    }

    // (2) ======================= Set up the fit ======================================
    for (Int_t nmip=0; nmip<nMipsMax; nmip++){
      func->SetParName(nmip,Form("%dMIPweight",nmip+1));
    }
    func->SetParName(nMipsMax,"MPV");
    func->SetParName(nMipsMax+1,"WIDbyMPV");
    /// This is the Landau WID/MPV, and should be about 0.15 for the EPD.
    func->SetParameter(nMipsMax+1,0.15);
    // ------------------------------------------------------------------
    func->SetParameter(nMipsMax,SingleMipPeakStartingValue);
    func->SetLineWidth(3);

    TFile* in = new TFile(Form(
              "./Day%d.root",run),"READ");

/// Here's where we fix each tile.
    bool ewQuit = 0;
    while(ewQuit ==0)
    {
      cout << "Which side of STAR? (E=0, W=1)";
      cout << "EW: ";
      int ew;
      cin >> ew;
      TString EWstring[2] = {"East","West"};
      Float_t MaxPlot;

      bool ppQuit = 0;
      while(ppQuit == 0)
      {
        cout << "Which supersector?" << endl << "PP: ";
        int PP;
        cin >> PP;

        bool ttQuit = 0;
        while(ttQuit == 0)
        {
          cout << "Which tile?" << endl << "TT: ";
          int TT;
          cin >> TT;
          // title = new TPaveLabel(.11,.95,.35,.99,Form("Run%dAdcEW%dPP%dTT%d",run,ew,PP,TT),"brndc");
          gStyle->SetOptStat(kFALSE);
          cout << "EW:PP:TT = " << ew << ":" << PP << ":" << TT << endl;
          TH1D* adc = (TH1D*)in->Get(Form("AdcEW%dPP%dTT%d",ew,PP,TT));
        	adc->SetTitle(Form("Run%d %s PP%02d TT%02d",run,EWstring[ew].Data(),PP,TT));
          adc->Draw();
          // title->Draw("same");

          c1->Update();
        	adc->GetXaxis()->SetTitle("ADC");
        	adc->GetXaxis()->SetLabelSize(0.08);
        	adc->GetXaxis()->SetTitleSize(0.08);
        	adc->GetXaxis()->SetTitleOffset(1);
          adc->GetXaxis()->SetRangeUser(30,1500);
          adc->SetMaximum(adc->GetBinContent(adc->GetMaximumBin())/5);
          adc->SetMinimum(0);
          adc->GetXaxis()->SetRangeUser(0,1500);
          int Start;
          int End;
          int yMax;
          int xMax;
          int rMax;
          int endIt;


          bool maxGraph = 0;
          while(maxGraph == 0)
          {
            cout << "Enter a maximum for the graph." << endl;
            cin >> yMax;
            adc->SetMaximum(yMax);
            adc->Draw();
            // title->Draw("same");

            c1->Update();
            std::string maxFin;
            cout << "Look good? (y/n)" << endl;
            cin >> maxFin;
            if (maxFin == "y")
            {
              maxGraph += 1;
            }
          }

          xMax = 0;
          while(xMax == 0)
          {
            cout << "Maximum x value?" << endl;
            cin >> endIt;
            adc->GetXaxis()->SetRangeUser(0,endIt);
            adc->Draw();
            // title->Draw("same");
            c1->Update();
            cout << "Look good? (y/n)" << endl;
            std::string xMaxEnd;
            cin >> xMaxEnd;
            if (xMaxEnd == "y")
            {
              xMax += 1;
            }
          }
          TH1D* temp1 = (TH1D*)(adc->Clone());


          bool fitEnder = 0;
          while(fitEnder == 0)
          {
            bool maxRebin = 0;
            while(maxRebin == 0)
            {
              cout << "Enter a rebin for the graph." << endl;
              cin >> rMax;
              adc->Rebin(rMax);
              adc->GetYaxis()->SetRangeUser(0,rMax*yMax);
              adc->GetXaxis()->SetRangeUser(0,endIt);

              adc->Draw();
              // title->Draw("same");
              c1->Update();
              std::string maxReb;
              cout << "Look good? (y/n)" << endl;
              cin >> maxReb;
              if (maxReb == "y")
              {
                maxRebin += 1;
              }
              else
              {
                adc=(TH1D*)(temp1->Clone());
              }
            }

            cout << "Enter where the fit should start:" << endl;
            cin >> Start;
            cout << "Enter a guess for the first MIP MPV:" << endl;
            cin >> End;
  //-------------------------------------------------------------------------------
            // adc->SetMaximum(adc->GetBinContent(End)*1.7);
            FitRangeLow = Start;
            SingleMipPeakStartingValue=End;
            MaxPlot=SingleMipPeakStartingValue*5;
          	adc->GetXaxis()->SetRangeUser(0,MaxPlot);
            adc->Draw("same");
          	func->SetParameter(nMipsMax+1,0.15);
          	func->SetParameter(nMipsMax,SingleMipPeakStartingValue);
  //-------------------------------------------------------------------------------
            /// This is the fit.

          	int FitStatus = adc->Fit("MultiMipFit","","",FitRangeLow,FitRangeHigh);
            //int FitStatus = 0;
            Float_t nMipFound = func->GetParameter(nMipsMax);
            Float_t nMipError = func->GetParError(nMipsMax);
            cout << "FitStatus= " << FitStatus << endl;
            // adc->GetXaxis()->SetRangeUser(0,SingleMipPeakStartingValue*3);
            // adc->SetMaximum(adc->GetBinContent(nMipFound)*1.7);
            TLine* found = new TLine(nMipFound,0,nMipFound,rMax*yMax/*adc->GetMaximum()*/);
            found->SetLineColor(6);   found->Draw();
            adc->GetYaxis()->SetRangeUser(0,rMax*yMax);

            adc->GetXaxis()->SetRangeUser(0,endIt);

            adc->Draw("same");
            // title->Draw("same");

            c1->Update();
            std::string fam;
            cout << "Is the fit acceptable? (y/n)";
            cin >> fam;
            if (fam == "y")
            {
              fitEnder += 1;
              NmipFile << Form("%d \t%d \t%d \t%d \t%f \t%f",run,ew,PP,TT,nMipFound,nMipError);
              NmipFile << endl;

              /// Display for single MIP fits.
              for (int n=0; n<nMipsMax; n++)
              {
                TH1D* temp = (TH1D*)(adc->Clone());
                temp->Clear();
                for (int ibin=1; ibin<temp->GetXaxis()->GetNbins(); ibin++)
                {
                  temp->SetBinContent(ibin,abs(func->GetParameter(n))*(*MipPeak[n])(temp->GetXaxis()->GetBinCenter(ibin)));
                }
                temp->SetLineWidth(0);
                temp->SetLineColor(1);
                temp->SetFillStyle(1001);
                temp->SetFillColorAlpha(n+1,0.35);
                temp->Draw("hist lf2 same");
                // title->Draw("same");

              }
              c1->Update();
              c1->SaveAs("ADCspectraFix.pdf");
            }
            else
            {
              // adc->SetMaximum(yMax);
              adc->GetYaxis()->SetRangeUser(0,rMax*yMax);

              adc->GetXaxis()->SetRangeUser(0,endIt);
              adc=(TH1D*)(temp1->Clone());

              adc->Draw();
              // title->Draw("same");
              c1->Update();
            }
          }


          cout << "Another tile on this supersector? (y/n)";
          std::string ttFin;
          cin >> ttFin;
          if (ttFin == "n")
          {
            ttQuit += 1;
          }
        }

        cout << "Another supersector on this side? (y/n)";
        std::string ppFin;
        cin >> ppFin;
        if (ppFin == "n")
        {
          ppQuit += 1;
        }
      }
      cout << "Another side of STAR for this run? (y/n)";
      std::string sideFin;
      cin >> sideFin;
      if (sideFin == "n")
      {
        ewQuit += 1;
      }
    }

    cout << "Another run for this energy? (y/n)";
    std::string runFin;
    cin >> runFin;
    if (runFin == "n")
    {
      c1->SaveAs("ADCspectraFix.pdf]");
      runQuit += 1;
      in->Close();
      NmipFile.close();
    }
  }
}



// ------------------------------- here is the fitting function -----------------------------
Double_t myfunc(Double_t* x, Double_t* param){
  // parameters 0...(nMipsMax-1) are the weights of the N-MIP peaks
  // and the last two parameters, index nMipsMax and nMipsMax+1,
  // are single-MIP MPV and WID/MPV, respectively
  Double_t ADC = x[0];
  Double_t SingleMipMPV = abs(param[nMipsMax]);
  Double_t WID = SingleMipMPV*param[nMipsMax+1];
  Double_t fitval=0.0;
  for (Int_t nMip=0; nMip<nMipsMax; nMip++){
    Double_t Weight = abs(param[nMip]);
    for (Int_t imip=0; imip<2*(nMip+1); imip+=2){
      MipPeak[nMip]->SetParameter(imip,SingleMipMPV);
      MipPeak[nMip]->SetParameter(imip+1,WID);
    }
    fitval += Weight*(*MipPeak[nMip])(ADC);
  }
  return fitval;
}
// -------------------------------------------------------------------------------------------
