#include "runday.h"

void th1to2() 
{
  //TFile* in[nrun];
 // for(int iday = 0; iday< nrun; iday++)
 // {
 // 	in[iday]	= new TFile(Form(
 //           //"../data/Day%d.root",runs[iday]),"READ");
 //           "../runs/%d.picoDst.root",runs[iday]),"READ");
 // }
  //std::cout << "test 0 " << std::endl;
  TFile* out = new TFile(Form("data2d%dto%d.root",runs[0],runs[nrun-1]),"RECREATE");
  //std::cout << "test 0.1 " << std::endl;
    /// 2D histograms for ADC distributions
    //TH2F *th2[2][12][31]; // [ew][pp][tt]
    TH3I *th3; // [ew][pp][tt]
    int nNumber = 10;
    th3  = new TH3I(Form("RunAdcTile"),
        Form("RunAdcTile;Tile ;ADC value;Run "),744,0.5,744.5,800,0,800,nNumber,0.5,0.5+nNumber);
        //Form("RunAdcTile;Tile #;ADC value;Run #"),744,0.5,744.5,4096,0,4096,nrun,0.5,0.5+nrun);

    /*for (int ew=0; ew<2; ew++){
  	std::cout << "ew " << ew << std::endl;
      for (int pp=1; pp<13; pp++){
  		std::cout << "pp " << pp << std::endl;
        for (int tt=1; tt<32; tt++){
  			std::cout << "tt " << tt << std::endl;
      th2[ew][pp-1][tt-1]  = new TH2F(Form("AdcEW%dPP%dTT%d",ew,pp,tt),
        Form("AdcEW%dPP%dTT%d;runs;ADC value",ew,pp,tt),nrun,0.5,0.5+nrun,4096,0,4096);
        }
      }
    }*/
  //std::cout << "test 1 " << std::endl;
  //for (int iday = 0 ;iday < nrun ; iday++)
  	TFile* in;
  for (int iday = 0 ;iday < 10; iday++)
  { // iday
  	in	= new TFile(Form(
            //"../data/Day%d.root",runs[iday]),"READ");
            "../runs/%d.picoDst.root",runs[iday]),"READ");
	std::cout << iday <<" runing run: " << runs[iday] << std::endl;
	std::string sday = std::to_string(runs[iday]);
	char const *pchar = sday.c_str();  //use char const* as target type
	int itt = 1;
  	for (int ew=0; ew<2; ew++){// ew // only East side need to be calibrated for FXT
  	  for (int PP=1; PP<13; PP++)
	  { // pp
  	    int iPad=0;
  	      for (int TT=1; TT<32; TT++)
	      { // TT
  		//std::cout << "test 1.1 " << std::endl;
		//th2[ew][PP-1][TT-1]->GetXaxis() ->SetBinLabel(iday+1, pchar);
		th3->GetZaxis() ->SetBinLabel(iday+1, pchar);
		th3->GetXaxis() ->SetBinLabel(itt, Form("AdcEW%dPP%dTT%d",ew,PP,TT));
  	      	//TH1D* adc = (TH1D*)in[iday]->Get(Form("AdcEW%dPP%dTT%d",ew,PP,TT)); // h1 for each tiles
  	      	TH1D* adc = (TH1D*)in->Get(Form("AdcEW%dPP%dTT%d",ew,PP,TT)); // h1 for each tiles
  		//std::cout << "test 1.2 " << std::endl;
		for(int iadc = 0; iadc < 1000 ; iadc ++)
		{ // iadc
		//	std::cout << "itt: " << itt << std::endl;
		//	std::cout << "iday +1: " << iday + 1 << std::endl;
		//	std::cout << "iadc +1: " << iadc + 1 << std::endl;
			//if((Double_t)adc->GetBinContent(iadc+1) != 0)std::cout << "ivalue +1: " << (Double_t)adc->GetBinContent(iadc+1) << std::endl;
  		//	std::cout << "test 1.3 " << std::endl;
		  //th2[ew][PP-1][TT-1] ->Fill(iday+1,iadc+1,(Double_t)adc->GetBinContent(iadc+1));
		  	//th3 ->Fill(itt,iadc+1,iday+1,(Float_t)adc->GetBinContent(iadc+1));
			Int_t value = (Int_t)adc->GetBinContent(iadc+1);
			//Float_t value = (Float_t)adc->GetBinContent(iadc+1);
		  	th3 ->SetBinContent(itt,iadc+1,iday+1,value);
  			//std::cout << "test 1.4 " << std::endl;
		} // iadc ++
		itt++;
		//std::cout << "itt: " << itt << std::endl;
  	      } // TT end
  	   } // pp end
  	} // ew end
  	in->Close();
  } // iday end
  //std::cout << "test 2 " << std::endl;
 // for(int iday = 0; iday< nrun; iday++)
 // {
 // 	in[iday]->Close();
 // }
  out->cd();	
  th3->Write();
  //out->Write();
  out->Close();

}



