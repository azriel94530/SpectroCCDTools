/*
 * commands.h
 *
 *  Created on: Oct 1, 2012
 *      Author: TFieger
 */

#ifndef COMMANDS_H_
#define COMMANDS_H_
#include "xbasic_types.h"
#include "lwip/netif.h"

//checks the status of the buffer and calls readbuffer automatically if data is available
void pollBufferState(struct netif *netif);
//reads the buffer given by bufferstate
void readBuffer(int bufferState);
void Config_BRAM();

void initSpi();
//sends the current spi output buffer (struct defined in globals.h) if mode != 0 it keeps sending 0 until it
//gets ENDOFTRANSMISSION from the client
void sendToVideoBoard(int mode);
void sendToClkBoard(int mode);

int pixels();
Xuint16 * imageLoc();
char * makeFitsHdr();

void cmdClkDacSet(char * buffer, int * len);
void cmdBiasDacSet(char * buffer,int * len);
void cmdBiasDacReset(char * buffer, int * len);
void cmdBiasDacInit();

void cmdClkDacInit();
void cmdAdcStart();
void cmdAdcSet(char * buffer,int * len);
void cmdClkPicRead(char * buffer,int * len);
void cmdClkTim(char * buffer,int * len);

void cmdBiasPicRead(char * buffer,int * len);
void cmdBiasEna(char * buffer,int * len);
void cmdPower(char * buffer,int * len);
void cmdReboot(char * buffer,int * len);
void cmdCcd(char * buffer,int * len);
void cmdIdle(char * buffer,int * len);
void cmdLiveNoise(char * buffer,int * len);
void cmdsector(char * buffer,int * len);

int flashwrite(int address, int pagecount, char * flashdata);
int eraseSector(Xuint32 startAddr,Xuint32 num64K);

#endif /* COMMANDS_H_ */
