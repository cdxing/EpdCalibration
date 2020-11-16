#include <iostream.h> 
#include <fstream.h> 


void write_epdStatus2() {
  gROOT->Macro("./loadlib.C");
  char fn[256];
  sprintf(fn, "./Badruns.txt");

  // EPD Status txt file
  FILE *fp = fopen(fn,"r");
  if(fp==NULL) {
    printf("Mapping file does not exist");
    return;
  }

  const Int_t MAX_DB_INDEX = 768;
  char line[2550];
  while (fgets(line,2550,fp)) {
    if(line[0]=='#') continue;
    int year,month,day,hour,min,sec, status, n=0;
    sscanf(&line[0],"%d-%d-%d %d:%d:%d %d",&year,&month,&day,&hour,&min,&sec,&status);

    TString storeTime;
    storeTime.Form("%i-%02i-%02i %02i:%02i:%02i",year,month,day,hour,min,sec);

    cout<<"\n\n"<<
      "Working on Timestamp = "<< storeTime<<"\n"
      <<endl;

    epdStatus_st epdStatus;
    for(int ew=0;ew<2;ew++){
      for(int pp=0; pp<12; pp++){
	for(int tt=0; tt<32; tt++){

	  epdStatus.ew[n] = ew;
	  epdStatus.pp[n] = pp;
	  epdStatus.tile[n] = tt;
	  epdStatus.status[n] = status;
	  n++;
	}
      }
    }

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


    memset(&epdStatus, -1, sizeof(epdStatus));

  }
  fclose(fp);
  return;
}
