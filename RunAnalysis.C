/*
__________________________________________
  Original code by Grigory.
  Updated code by Prashanth.
  Tweaks by Skipper.
------------------------------------------
*/

// This is needed for calling standalone classes (not needed on RACF)
//#define _VANILLA_ROOT_

// C++ headers
#include <iostream>
#include <sstream>

// ROOT headers
#include "TROOT.h"
#include "TFile.h"
#include "TChain.h"
#include "TTree.h"
#include "TSystem.h"
#include "TH1.h"
#include "TH2.h"
#include "TMath.h"
#include "TString.h"

// PicoDst headers
/*
#include "StRoot/StPicoEvent/StPicoDstReader.h"
#include "StRoot/StPicoEvent/StPicoDst.h"
#include "StRoot/StPicoEvent/StPicoEvent.h"
#include "StRoot/StPicoEvent/StPicoTrack.h"
#include "StRoot/StPicoEvent/StPicoBTofHit.h"
#include "StRoot/StPicoEvent/StPicoBTowHit.h"
#include "StRoot/StPicoEvent/StPicoEmcTrigger.h"
#include "StRoot/StPicoEvent/StPicoBTofPidTraits.h"
#include "StRoot/StPicoEvent/StPicoTrackCovMatrix.h"

// Load libraries (for ROOT_VERSTION_CODE >= 393215)
#if ROOT_VERSION_CODE >= ROOT_VERSION(6,0,0)
R__ADD_LIBRARY_PATH(StRoot/StPicoEvent/)
R__LOAD_LIBRARY(libStPicoDst)
#endif
*/
//_________________
void RunAnalysis(const Char_t *inFile =
  "./data/production_31p2GeV_fixedTarget_2020/ReversedFullField/dev/2020/028/st_physics_adc_21028011_raw.picoDst.root") {

  // try another way to load libraries
  gSystem->Load("StRoot/StPicoEvent/libStPicoDst.so");
  gSystem->Load("StRoot/StEpdUtil/libStEpdUtil.so");

  // Finding the day parameter.
  std::string Queso = inFile;
  std::string Nachos = "Oh no!";
  Queso = Queso.substr( Queso.find_last_of('/')+1 ); // Queso ="st_physics_adc_21028011_raw_6000002.picoDst.root"
  int QuesoNumStart = Queso.length() - 34; // Select 21028011_raw_6000002.picoDst.root from above
  Nachos = Queso.substr(QuesoNumStart + 3,3);
  /*
	if (Queso.substr(15,1) == "2") // '1'
	{
		Nachos = Queso.substr(17,3); // '028'
	}
	else
	{
		Nachos = Queso.substr(13,3); // '38_'
	}
	*/
  std::cout << Nachos << std::endl;
  //int Tacos = stoi(Nachos); // 168
  TString Nachos2 = Nachos;
  TString Queso2 = Queso;
  Int_t Tacos = Nachos2.Atoi();

  std::cout << "Feed me data!" << std::endl;

  cout <<" analysis file "<<inFile<<endl;
  StPicoDstReader* picoReader = new StPicoDstReader(inFile);
  picoReader->Init();

  /// This is a way if you want to spead up IO
  std::cout << "Explicit read status for some branches" << std::endl;
  picoReader->SetStatus("*",0); // what is this status?
  picoReader->SetStatus("Event",1);
  picoReader->SetStatus("Track",1);
  picoReader->SetStatus("EpdHit",1);
  std::cout << "Statuses set. M04r data!" << std::endl;

  std::cout << "Beginning to chew . . ." << std::endl;

  Long64_t events2read = picoReader->chain()->GetEntriesFast(); // Whats will GetEntriesFast return? What's the difference with GetEntries?
  //Long64_t events2read = 10;

  std::cout << "Number of events to read: " << events2read << std::endl;

  /// Histogramming

  /// 1D histograms for ADC distributions
  TH1D *mAdcDists[2][12][31]; // [ew][pp][tt]

  for (int ew=0; ew<2; ew++){
    for (int pp=1; pp<13; pp++){
      for (int tt=1; tt<32; tt++){
    mAdcDists[ew][pp-1][tt-1]  = new TH1D(Form("AdcEW%dPP%dTT%d",ew,pp,tt),
      Form("AdcEW%dPP%dTT%d",ew,pp,tt),4096,0,4096);
      }
    }
  }
  //std::cout<<"test 1" <<std::endl;
  /*
  TH1F *hRefMult = new TH1F("hRefMult","Reference multiplicity;refMult", 500, -0.5, 499.5);
  TH1F *hTransvMomentum = new TH1F("hTransvMomentum",
                                    "Track transverse momentum;p_{T} (GeV/c)", 200, 0., 2.);
  */

  /// Event loop
  for(Long64_t iEvent=0; iEvent<events2read; iEvent++) {

    //std::cout << "Obey your orders, Master! Working on event #["
    //         << (iEvent+1) << "/" << events2read << "]" << std::endl;

    Bool_t readEvent = picoReader->readPicoEvent(iEvent);
    if( !readEvent ) {
      std::cout << "Error on event #" << iEvent << ". No data to chew on. :(" << std::endl;
      break;
    }

    /// Retrieve picoDst
    StPicoDst *dst = picoReader->picoDst();

    /// Retrieve event information
    StPicoEvent *event = dst->event();
    if( !event ) {
      std::cout << "Event #" << iEvent << " does not exist. FEED ME!!" << std::endl;
      break;
    }

    //hRefMult->Fill( event->refMult() );

    if (TMath::Abs(event->primaryVertex().z()) > 40.0 )
    {
     continue;
    }
    if (TMath::Abs( sqrt(pow(event->primaryVertex().x(),2) +
      pow(event->primaryVertex().y(),2))) > 2.0 )
    {
      continue;
    }
    /// Track analysis

    /*Int_t nTracks = dst->numberOfTracks();
    std::cout << "Number of tracks in event: " << nTracks << std::endl;
    /// Loop over tracks (No need for this application. SK)
    for(Int_t iTrk=0; iTrk<nTracks; iTrk++) {

      StPicoTrack *picoTrack = dst->track(iTrk);
      if(!picoTrack) continue;
      //std::cout << "Track #[" << (iTrk+1) << "/" << nTracks << "]"  << std::endl;

      /// Single-track cut example
      if( !picoTrack->isPrimary() ||
	  picoTrack->nHits() < 15 ||
	  TMath::Abs( picoTrack->gMom().pseudoRapidity() ) > 0.5 ) {
	continue;
      } //for(Int_t iTrk=0; iTrk<nTracks; iTrk++)

      hTransvMomentum->Fill( picoTrack->gPt() );
    }*/

    // EPD Hit loop

    TClonesArray *mEpdHits = dst->picoArray(8);
    //cout << mEpdHits->GetEntries()<<endl;
    StPicoEpdHit* epdHit;

    for (int hit=0; hit<mEpdHits->GetEntries(); hit++){
      epdHit = (StPicoEpdHit*)((*mEpdHits)[hit]);
      int ew = (epdHit->id()<0)?0:1;
      int pp = epdHit->position();
      int tt = epdHit->tile();
      double adc = epdHit->adc();
      mAdcDists[ew][pp-1][tt-1]->Fill(adc);
    }


  } //for(Long64_t iEvent=0; iEvent<events2read; iEvent++)

  picoReader->Finish();
  //std::cout<<"test 4" <<std::endl;

  if (Tacos < 100)
  {
    TString pathSave = Form("./Day%d/",Tacos);

    TFile *MyFile = TFile::Open(pathSave+Queso2,"RECREATE"); // "Day168st_mtd_19168038_raw_4000002.picoDst.root"
    MyFile->cd();

    for (int ew=0; ew<2; ew++){
    for (int pp=1; pp<13; pp++){
      for (int tt=1; tt<32; tt++){
    mAdcDists[ew][pp-1][tt-1]->Write();
      }
    }
  }
  //std::cout<<"test 5" <<std::endl;

  MyFile->Close();

  }
  else
  {
    TString pathSave = Form("./Day%d/",Tacos);
    TFile *MyFile = TFile::Open(pathSave+Queso2,"RECREATE");
    MyFile->cd();

    for (int ew=0; ew<2; ew++){
    for (int pp=1; pp<13; pp++){
      for (int tt=1; tt<32; tt++){
    mAdcDists[ew][pp-1][tt-1]->Write();
      }
    }
  }

  MyFile->Close();

  }

  std::cout << "<burp> Ahhhh. All done; thanks!" << std::endl;
}
// This macro make 744 histograms of ADC vs counts
