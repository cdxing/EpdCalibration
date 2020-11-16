
#include <iostream.h>
#include <fstream.h>

void read_epdStatus(){

  // base libraries
  gSystem->Load("St_base");
  gSystem->Load("StChain");
  gSystem->Load("StUtilities");
  gSystem->Load("StIOMaker");
  gSystem->Load("StarClassLibrary");

  // db-related libraries
  gSystem->Load("St_Tables");
  gSystem->Load("StDbLib");
  gSystem->Load("StDbBroker");
  gSystem->Load("St_db_Maker");

  St_db_Maker *dbMk=new St_db_Maker("db", "MySQL:StarDb", "$STAR/StarDb");
  dbMk->SetDebug();
  dbMk->SetDateTime(20190201,0); // event or run start time, set to your liking
  dbMk->SetFlavor("ofl");

  dbMk->Init();
  dbMk->Make();

  TDataSet *DB = 0;
  DB = dbMk->GetDataBase("Calibrations/epd/epdStatus");
  if (!DB) {
    std::cout << "ERROR: no table found in db, or malformed local db config" << std::endl;
  }

  St_epdStatus *dataset = 0;
  dataset = (St_epdStatus*) DB->Find("epdStatus");
  Int_t rows = dataset->GetNRows();
  if (rows > 1) {
    std::cout << "I>>>>>>NFO: found INDEXED table with " << rows << " rows" << std::endl;
  }

  if (dataset) {
    TDatime val[2];
    dbMk->GetValidity((TTable*)dataset,val);
    std::cout << "Dataset validity range: [ " << val[0].GetDate() << "." << val[0].GetTime() << " - " 
      << val[1].GetDate() << "." << val[1].GetTime() << "  "
      << std::endl;

    epdStatus_st *table = dataset->GetTable();
    for (Int_t i = 0; i < 768; i++) {
      std::cout << i << "\t"<< table->ew[i]<<"\t"<< table->pp[i]<<"\t"<< table->tile[i]<<"\t"<< table->status[i]<<std::endl;

    }
  } else {
    std::cout << "ERROR: dataset does not contain requested table" << std::endl;
  }

}

