/*
 * globals.h
 *
 *  Created on: Oct 1, 2012
 *      Author: TFieger
 */

#ifndef GLOBALS_H_
#define GLOBALS_H_
#include "xspi.h"
#include "xparameters.h"

#define BRAM_BUFFER
#define clearaddr 96
#define readaddr 32
#define noiseaddr 128

#define SPIBUFFERSIZE 256

#define STARTOFTRANSMISION          0xAAAA
#define ENDOFTRANSMISSION           0xFFFF

#define DAC_CMD_RESET               0x01
#define DAC_CMD_WRITE               0x02
#define DAC_CMD_CLR                 0x03
#define DAC_CMD_UPDATE              0x04


#define DAC_INPUT_WRITE_MODE        0xC0		//0b11<<6
#define DAC_OFFSET_WRITE_MODE       0x80 		//0b10<<6
#define DAC_GAIN_WRITE_MODE         0x04		//0b01<<6
#define DAC_SPECIAL_FUNCTIONS_MODE  0x00		//0b00<<6

#define DAC_SF_WRITE_OFS0			0x02
#define DAC_SF_WRITE_OFS1			0x03

#define PIC_CMD_READ_ADC            0x10
#define PIC_CMD_SET_SEGMENT         0x11
#define PIC_CMD_SET_GAIN            0x12

#define ADC_CMD_WRITE               0x20
#define HV_CMD_WRITE               0x20
#define HV_CMD_ERASE               0x21
#define HV_CMD_PURGE               0x22

float erase_storage[6];

XSpi videoSPI,clkSPI;

typedef struct {
	Xuint8 receive[SPIBUFFERSIZE];
	Xuint8  send[SPIBUFFERSIZE];
	Xuint16 index;}SPIbuffer;
SPIbuffer videoSPIbuffer,clkSPIbuffer;

int rowIndex=0,columnIndex=0,segmentIndex=0;

Xuint16 imageData[5000*5000];
Xuint16 * imagePointer = imageData;
Xuint32 resolution;
Xuint32 rows;
Xuint32 columns;
Xuint32 oldbufferState = 0;
Xuint32 ledRegister = 0;
Xuint32 reg[32];

unsigned int file_len;
int BRAM_seq; //current number of bram file packages received.
int BRAMloc;
long flash_offset = -1;
//char * BRAM_tim = (char *)imageData; //also extern in http_response
char * webfilename ="clkboard.html"; //also extern in http_response

char fits_header[0x4000];

char rowsAsString[4]; // MAX 9999 pixel each side
char columnsAsString[4];
char dateAsString[50];

//DAC settings
#define OFFSETVALUE_bias	8192
#define MVALUE_bias			0xfffe
#define CVALUE_bias			32768
#define OFFSETVALUE_clk		8192
#define MVALUE_clk			0xfffe
#define CVALUE_clk			32768
#define VREF_BIAS			2.5
#define VREF_CLK			1.2
#define clk_buffergain		4.77
#define clk_hvbuffgain		190.22

const float clk_adc_gain 	=	0.0064;
const int clk_adc_offset  	=	1866;
//const float clk_adc_gain 	=	0.006;
//const int clk_adc_offset  	=	2144;
const float clk_hv_adc_gain = 	0.0465;
const int clk_hv_adc_offset = 	0;
// pic adc: Vr 1-4, Vdd 1-4, Vog 1-4 ,Vdrain1-4
const float biasAdcGains[] = { 0.0103,0.0103,0.0103,0.0103,  0.01484,0.01484,0.01484,0.01484,  0.00526,0.00526,0.00526,0.00526,  0.01484,0.01484,0.01484,0.01484};
const int biasAdcOffset[] = {1918,1918,1918,1918,   1959,1959,1959,1959,  1790,1790,1790,1790,   1918,1918,1918,1918};
//const float biasAdcGains[] = { 0.00585,0.00585,0.00585,0.00585,  0.00806,0.00806,0.00806,0.00806,  0.00423,0.00423,0.00423,0.00423,  0.00806,0.00806,0.00806,0.00806};
//const int biasAdcOffset[] = {0,0,0,0,   0,0,0,0,  1691,1691,1691,1691,   0,0,0,0}; //offset makes readback value smaller
const int adcChannelMapping[16] = {9,10,11,12, 17,18,19,20, 13,14,15,16, 21,22,23,24};
// 1-4 PGA offset 5-8 comv offset 9-12 Vr 13,14,19,20 Vog 15-18 VDD
const float biasBuffGains[] = { 1.0,1.0,1.0,1.0,  1.0,1.0,1.0,1.0,  4.0,4.0,4.0,4.0,  2.0,2.0,2.0,2.0, 6.0,6.0,6.0,6.0,   6.0,6.0,6.0,6.0 };


#endif /* GLOBALS_H_ */
