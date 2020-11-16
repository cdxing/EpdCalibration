#include <iostream.h> 
#include <fstream.h> 


void write_epdQTMap(char* opt="", char* year="18", char* input="epdmap.txt") {
  char fn[256];

  sprintf(fn, "./txt_tables/epdQTMap.txt.05222019");
  TString storeTime = "2019-05-22 12:00:00"; // storetime is begin time for validity range for WRITING DB

  gROOT->Macro("./loadlib.C");


  /* Print size of structures
     cout<<"Size of EPDmap structure = "<<sizeof(epdQTMap_st)<<endl;
     cout<<"Size of EPDStatus structure = "<<sizeof(epdStatus_st)<<endl;
     cout<<"Size of EPDGain structure = "<<sizeof(epdGain_st)<<endl;
     cout<<"Size of EPD FEE structure = "<<sizeof(epdFEEMap_st)<<endl;
     */

  // Initiate c sturctue to fill in
  const Int_t MAX_DB_INDEX = 768;
  epdQTMap_st epdQTMap;
  for(int i=0; i<MAX_DB_INDEX; i++){
    epdQTMap.ew[i] = -1;
    epdQTMap.pp[i] = -1;
    epdQTMap.tile[i] = -1;

    epdQTMap.qt_crate_adc[i] = -1;
    epdQTMap.qt_board_adc[i] = -1;
    epdQTMap.qt_channel_adc[i] = -1;

    epdQTMap.qt_crate_tac[i] = -1;
    epdQTMap.qt_board_tac[i] = -1;
    epdQTMap.qt_channel_tac[i] = -1;
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
  short qt_crate_adc;
  short qt_board_adc;
  short qt_channel_adc;
  short qt_crate_tac;
  short qt_board_tac;
  short qt_channel_tac;
  int n=0;


  char line[2550];
  fgets(line,2550,fp);
  printf("EPD is using mapping as on %s",line);
  while (fgets(line,2550,fp)) {
    if(line[0]=='#') continue;
    sscanf(&line[0],"%hd %hd %hd %hd %hd %hd %hd %hd %hd %hd %hd %s",&ew,&pp,&tile,&qt_crate_adc,&qt_board_adc,&qt_channel_adc,&qt_crate_tac,&qt_board_tac,&qt_channel_tac);

    //cout<<n <<"\t"<<ew<<"\t"<<pp<<"\t"<<tile<<"\t"<<qt_crate_adc<<"\t"<<qt_board_adc<<"\t"<<qt_channel_adc<<"\t"<<qt_crate_tac<<"\t"<<qt_board_tac<<"\t"<<qt_channel_tac<<endl;

    epdQTMap.ew[n] = ew;
    epdQTMap.pp[n] = pp;
    epdQTMap.tile[n] = tile;

    epdQTMap.qt_crate_adc[n] = qt_crate_adc; 
    epdQTMap.qt_board_adc[n] = qt_board_adc; 
    epdQTMap.qt_channel_adc[n] = qt_channel_adc; 

    epdQTMap.qt_crate_tac[n] = qt_crate_tac; 
    epdQTMap.qt_board_tac[n] = qt_board_tac; 
    epdQTMap.qt_channel_tac[n] = qt_channel_tac; 

    n++;
  }
  fclose(fp);


  // print content of cstructure
  for(int i=0; i<MAX_DB_INDEX; i++){
    printf("%d               %d  %d  %d             %d  %d  %d          %d  %d  %d \n",i,epdQTMap.ew[i],epdQTMap.pp[i],epdQTMap.tile[i],    epdQTMap.qt_crate_adc[i],epdQTMap.qt_board_adc[i],epdQTMap.qt_channel_adc[i],   epdQTMap.qt_crate_tac[i],epdQTMap.qt_board_tac[i],epdQTMap.qt_channel_tac[i]);
  }
  printf("Found %d entries (should be 768)\n",n);








  // un comment following to fill the DB after testing carfully

  gSystem->Setenv("DB_ACCESS_MODE","write");
  StDbManager* mgr = StDbManager::Instance();
  StDbConfigNode* node = mgr->initConfig("Geometry_epd");
  StDbTable* dbtable = node->addDbTable("epdQTMap");
  mgr->setStoreTime(storeTime.Data());    
  dbtable->SetTable((char*)&epdQTMap, 1);
  dbtable->setFlavor("ofl"); 
  mgr->storeDbTable(dbtable);    
  std::cout << "INFO: table saved to database" << std::endl;




}
