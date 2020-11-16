#include <iostream.h> 
#include <fstream.h> 


void write_epdGain(char* opt="", char* year="19") {
  char fn[256];

  sprintf(fn, "./txt_tables/epdGain.txt.01262019");
  TString storeTime = "2019-01-26 00:00:00"; // storetime is begin time for validity range for WRITING DB

  gROOT->Macro("./loadlib.C");

  // Initiate c sturctue to fill in
  const Int_t MAX_DB_INDEX = 768;
  epdGain_st epdGain;
  for(int i=0; i<MAX_DB_INDEX; i++){
    epdGain.ew[i] = -1;
    epdGain.pp[i] = -1;
    epdGain.tile[i] = -1;

    epdGain.vped[i] = -1;
    epdGain.mip[i] = -1;
    epdGain.qt_pedestals[i] = -1;
    epdGain.dark_current[i] = -1;

    epdGain.qt_pedestals_sigma[i] = -1;
    epdGain.offset[i] = -1;
  }

  // EPD mapping
  //Read EPD mapping from txt file
  FILE *fp = fopen(fn,"r");
  if(fp==NULL) {
    printf("Mapping file does not exist");
  }
  else {
    exit;
  }

  short ew;
  short pp;
  short tile;
  float vped;
  float mip;
  float qt_pedestals;
  float dark_current;
  float qt_pedestals_sigma;
  float offset;
  int n=0;


  char line[2550];
  fgets(line,2550,fp);
  printf("EPD is using mapping as on %s",line);
  while (fgets(line,2550,fp)) {
    if(line[0]=='#') continue;
    sscanf(&line[0],"%hd %hd %hd %f %f %f %f  %f  %f",&ew,&pp,&tile,&vped,&mip,&qt_pedestals,&dark_current,&qt_pedestals_sigma,&offset);


    epdGain.ew[n] = ew;
    epdGain.pp[n] = pp;
    epdGain.tile[n] = tile;

    epdGain.vped[n] = vped; 
    epdGain.mip[n] = mip; 
    epdGain.qt_pedestals[n] = qt_pedestals; 
    epdGain.dark_current[n] = dark_current; 

    epdGain.qt_pedestals_sigma[n] = qt_pedestals_sigma; 
    epdGain.offset[n] = offset; 


    n++;
  }
  fclose(fp);


  // print content of cstructure

  for(int i=0; i<MAX_DB_INDEX; i++){
    printf("%d               %d  %d  %d             %f %f %f %f %f %f \n",i,epdGain.ew[i],epdGain.pp[i],epdGain.tile[i],    epdGain.vped[i] , epdGain.mip[i] , epdGain.qt_pedestals[i] , epdGain.dark_current[i] , epdGain.qt_pedestals_sigma[i] , epdGain.offset[i],  epdGain.qt_pedestals_sigma[i] , epdGain.offset[i]  );
  }
  printf("Found %d entries (should be 768)\n",n);








  // un comment following to fill the DB after testing carfully

  gSystem->Setenv("DB_ACCESS_MODE","write");
  StDbManager* mgr = StDbManager::Instance();
  StDbConfigNode* node = mgr->initConfig("Calibrations_epd");
  StDbTable* dbtable = node->addDbTable("epdGain");
  mgr->setStoreTime(storeTime.Data());    
  dbtable->SetTable((char*)&epdGain, 1);
  dbtable->setFlavor("ofl"); 
  mgr->storeDbTable(dbtable);    
  std::cout << "INFO: table saved to database" << std::endl;

}
