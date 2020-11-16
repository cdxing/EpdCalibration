#include <iostream.h> 
#include <fstream.h> 
#include <float.h>



void write_epdFeeMap(char* opt="", char* year="17") {
  char fn[256];

  sprintf(fn, "./txt_tables/epdFeeMap.txt.05172017");
  TString storeTime = "2017-05-17 00:00:00"; // storetime is begin time for validity range for WRITING DB

  gROOT->Macro("./loadlib.C");

  // Initiate c sturctue to fill in
  const Int_t MAX_DB_INDEX = 768;
  int wire1n=0;
  epdFEEMap_st epdFeeMap;
  for(int i=0; i<MAX_DB_INDEX; i++){
    epdFeeMap.ew[i] = -1;
    epdFeeMap.pp[i] = -1;
    epdFeeMap.tile[i] = -1;

    epdFeeMap.tuff_id[i] = -1;
    epdFeeMap.tuff_group[i] = -1;
    epdFeeMap.tuff_channel[i] = -1;

    epdFeeMap.receiver_board[i] = -1;
    epdFeeMap.receiver_board_channel[i] = -1;
    epdFeeMap.camac_crate_address[i] = -1;
    for(int j=0;j<2;j++){
      epdFeeMap.wire_1_id[wire1n] = 0x0;
      wire1n++;
    }



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
  short tuff_id;
  short tuff_group;
  short tuff_channel;
  short receiver_board;
  short receiver_board_channel;
  short camac_crate_address;
  char wire_1_id[20];
  int n=0;
  wire1n=0;


  char line[2550];
  fgets(line,2550,fp);
  printf("EPD is using mapping as on %s",line);
  while (fgets(line,2550,fp)) {
    if(line[0]=='#') continue;
    sscanf(&line[0],"%hd %hd %hd %hd %hd %hd %hd %hd %hd %s",&ew,&pp,&tile,&tuff_id,&tuff_group,&tuff_channel,&receiver_board,&receiver_board_channel,&camac_crate_address, wire_1_id);

    //cout<<n <<"\t"<<ew<<"\t"<<pp<<"\t"<<tile<<"\t"<<tuff_id<<"\t"<<tuff_group<<"\t"<<tuff_channel<<"\t"<<receiver_board<<"\t"<<receiver_board_channel<<"\t"<<camac_crate_address<<"\t"<<wire_1_id<<endl;

    
    epdFeeMap.ew[n] = ew;
    epdFeeMap.pp[n] = pp;
    epdFeeMap.tile[n] = tile;

    epdFeeMap.tuff_id[n] = tuff_id; 
    epdFeeMap.tuff_group[n] = tuff_group; 
    epdFeeMap.tuff_channel[n] = tuff_channel; 

    epdFeeMap.receiver_board[n] = receiver_board; 
    epdFeeMap.receiver_board_channel[n] = receiver_board_channel; 
    epdFeeMap.camac_crate_address[n] = camac_crate_address; 


    // 1 wire ID

    string s = string(wire_1_id);
    std::string s1 = s.substr(2,8);
    std::string s2 = s.substr(10,8);
    unsigned long u1 = hex2uint( s1 );
    unsigned long u2 = hex2uint( s2 );
    epdFeeMap.wire_1_id[wire1n] = u1;
    wire1n++;
    epdFeeMap.wire_1_id[wire1n] = u2;
    wire1n++;
    
    n++;
  }
  fclose(fp);

  // print content of cstructure
  wire1n=0;
  for(int i=0; i<MAX_DB_INDEX; i++){
    printf("%hd    %hd  %d  %hd     %hd  %hd  %hd    %hd  %hd  %hd  %u %u\n",i,epdFeeMap.ew[i],epdFeeMap.pp[i],epdFeeMap.tile[i],    epdFeeMap.tuff_id[i],epdFeeMap.tuff_group[i],epdFeeMap.tuff_channel[i],   epdFeeMap.receiver_board[i],epdFeeMap.receiver_board_channel[i],epdFeeMap.camac_crate_address[i], epdFeeMap.wire_1_id[wire1n],epdFeeMap.wire_1_id[wire1n+1]);
    wire1n+=2;


  }
  //printf("Found %d entries (should be 744)\n",n);








  // un comment following to fill the DB after testing carfully
  
  
     gSystem->Setenv("DB_ACCESS_MODE","write");
     StDbManager* mgr = StDbManager::Instance();
     StDbConfigNode* node = mgr->initConfig("Geometry_epd");
     StDbTable* dbtable = node->addDbTable("epdFEEMap");
     mgr->setStoreTime(storeTime.Data());    
     dbtable->SetTable((char*)&epdFeeMap, 1);
     dbtable->setFlavor("ofl"); 
     mgr->storeDbTable(dbtable);    
     std::cout << "INFO: table saved to database" << std::endl;





}

unsigned long hex2uint( const std::string& s ) {
  unsigned long d = 0;
  ::sscanf( s.c_str(), "%x", &d );
  return d;
}
