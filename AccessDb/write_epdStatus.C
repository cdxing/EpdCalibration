#include <iostream.h> 
#include <fstream.h> 


void write_epdStatus(char* opt="", char* year="19") {
  char fn[256];

  sprintf(fn, "./txt_tables/epdStatus.txt.01262019");
  TString storeTime = "2019-01-26 00:00:00"; // storetime is begin time for validity range for WRITING DB

  gROOT->Macro("./loadlib.C");

  // Initiate c sturctue to fill in
  const Int_t MAX_DB_INDEX = 768;
  epdStatus_st epdStatus;
  for(int i=0; i<MAX_DB_INDEX; i++){
    epdStatus.ew[i] = -1;
    epdStatus.pp[i] = -1;
    epdStatus.tile[i] = -1;

    epdStatus.status[i] = -1;
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
  short status;
  int n=0;


  char line[2550];
  fgets(line,2550,fp);
  printf("EPD is using mapping as on %s",line);
  while (fgets(line,2550,fp)) {
    if(line[0]=='#') continue;
    sscanf(&line[0],"%hd %hd %hd %hd",&ew,&pp,&tile,&status);

    //cout<<n <<"\t"<<ew<<"\t"<<pp<<"\t"<<tile<<"\t"<<status<<endl;

    epdStatus.ew[n] = ew;
    epdStatus.pp[n] = pp ;
    epdStatus.tile[n] = tile ;

    epdStatus.status[n] = status; 

    n++;
  }
  fclose(fp);


  // print content of cstructure

  for(int i=0; i<MAX_DB_INDEX; i++){
    printf("%d               %d  %d  %d             %d   \n",i,epdStatus.ew[i],epdStatus.pp[i],epdStatus.tile[i],    epdStatus.status[i]);
  }
  printf("Found %d entries (should be 768)\n",n);








  // un comment following to fill the DB after testing carfully
/*
  gSystem->Setenv("DB_ACCESS_MODE","write");
  StDbManager* mgr = StDbManager::Instance();
  StDbConfigNode* node = mgr->initConfig("Calibrations_epd");
  StDbTable* dbtable = node->addDbTable("epdStatus");
  mgr->setStoreTime(storeTime.Data());    
  dbtable->SetTable((char*)&epdStatus, 1);
  dbtable->setFlavor("ofl"); 
  mgr->storeDbTable(dbtable);    
  std::cout << "INFO: table saved to database" << std::endl;
*/
}
