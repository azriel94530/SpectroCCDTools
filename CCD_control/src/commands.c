/*
 * commands.c
 *
 *  Created on: Oct 1, 2012
 *      Author: TFieger
 */

#include "commands.h"
#include "config_apps.h"
#include "webserver.h"
#include "platform_gpio.h"
#include "globals.h"
#include "mfs_config.h"
#include "xparameters.h"
#include "xspi.h"
#include "string.h"
#include "flashMFS.h"
#include "netif/xadapter.h"


int transfer_data();

int pixels(){
	return resolution;
}
Xuint16 * imageLoc(){
	return imagePointer;
}

char * makeFitsHdr(){
	int fits_hlen;
	int fd;
	char * startFitsDate;
	char * start_NAXIS1;
	char * start_NAXIS2;

	fd = mfs_file_open("fitsheader.txt", MFS_MODE_READ);
	fits_hlen = mfs_file_read(fd, fits_header,0x4000);
	mfs_file_close(fd);
	xil_printf("fits header length %d \n\r",fits_hlen);
	/* get date, columns and rows and write it to fitsheader */
	startFitsDate = strstr(fits_header, "DATE");
	start_NAXIS1 = strstr(fits_header, "NAXIS1");
	start_NAXIS2 = strstr(fits_header, "NAXIS2");

	memcpy(startFitsDate+9,dateAsString,21);
	memcpy(start_NAXIS1+26,columnsAsString,4);
	memcpy(start_NAXIS2+26,rowsAsString,4);
return fits_header;
}

void pollBufferState(struct netif *netif){
//in globals.h	static Xuint32 bufferState = 0;
	Xuint32 bufferState = 0;
	Xuint32 state = 0;
	Xuint32 timeout = 0;
	int i;
	if((reg[0] & (1<<2))==4 ){//readout pending bit set
		reg[0] |= 1<<1; // set trigger bit
		Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[0]);
		state = (Xil_In32(XPAR_CCD_STATE_0_BASEADDR)&8);
		//xil_printf("Triggered %x %x\r\n",reg[0],state);
		while (state == 8){
			state = (Xil_In32(XPAR_CCD_STATE_0_BASEADDR)&8);
			xemacif_input(netif);
			transfer_data();
			timeout++;
			if (timeout == 1000000){
				xil_printf("Timeout during wait for CCD read\r\n");
				return;
			}
			}; //wait for ccd to start reading
		reg[0] &= ~(1<<1); // clear trigger bit
		Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[0]);
		oldbufferState = 0; //beginning of new image, buffer is always empty
	}
	timeout = 0;
	while (reg[0] & (1<<2)){ //readout pending
		bufferState = Xil_In32(XPAR_CCD_STATE_0_BASEADDR)&7;
		timeout++;
		if (timeout == 10000000){
			reg[0] &= ~(1<<2); // clear pending bit
			Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[0]);
			xil_printf("Timeout during wait for CCD read complete %x \r\n " ,reg[0]);
			return;}
		if(  (bufferState&3) != oldbufferState){
			timeout = 0;
			oldbufferState = bufferState&3;
			readBuffer(bufferState);
			if(bufferState > 3){ //image ready bit is set
				reg[0] &= ~(1<<2); // clear pending bit
				Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[0]);
				rowIndex=columnIndex=segmentIndex=0; //reset image location
				for(i=0;i<10;i++){
					xil_printf("data %x %x\r\n", imageData[i],(imageData[i]>>8)+((imageData[i]&0xff)<<8));
				}
			}
		}else{ //if we don't need to move data check for ethernet traffic
			xemacif_input(netif);
			transfer_data();
		}
	}
}
void readBuffer(int bufferState){
	Xuint32 * buffer;

	int i;
	if ( bufferState &1)
		buffer = ( u32 *)XPAR_VIDEO_BRAM_CTRL_S_AXI_BASEADDR;
	else
		buffer = ( u32 *)(XPAR_VIDEO_BRAM_CTRL_S_AXI_BASEADDR +0x2000);
	for(i = 0; segmentIndex < (resolution>>2) && i < 0x800; ++segmentIndex, i+=2 , columnIndex++){
		if (columnIndex == (columns>>1)){
			rowIndex++;
			columnIndex = 0;
		}
		imageData[rowIndex * columns + columnIndex] = buffer[i+1]>>16; //CH4
		imageData[columns * rows-1 - (columns*rowIndex) - columnIndex] = buffer[i+1]&0xffff; //CH1
		imageData[rowIndex * columns + columns - columnIndex -1] = buffer[i] &0xffff; //CH2
		imageData[columns * (rows-1) - (columns*rowIndex)+ columnIndex] =  buffer[i]>>16; // CH3 i+1 used for testing quadrant1
	}
}

void initSpi(){

	XSpi_Initialize(&videoSPI,XPAR_SPI_VIDEO1_DEVICE_ID);
	XSpi_SetOptions(&videoSPI,XSP_MASTER_OPTION  + XSP_MANUAL_SSELECT_OPTION +XSP_CLK_PHASE_1_OPTION);
	XSpi_Start(&videoSPI);
	XSpi_IntrGlobalDisable(&videoSPI);
	XSpi_SetSlaveSelect(&videoSPI,1);

	XSpi_Initialize(&clkSPI,XPAR_SPI_CLK_DEVICE_ID);
	XSpi_SetOptions(&clkSPI,XSP_MASTER_OPTION  + XSP_MANUAL_SSELECT_OPTION +XSP_CLK_PHASE_1_OPTION);
	XSpi_Start(&clkSPI);
	XSpi_IntrGlobalDisable(&clkSPI);
	XSpi_SetSlaveSelect(&clkSPI,1);

	XSpi_Initialize(&flashSPI,XPAR_SPI_FLASH_DEVICE_ID);
	XSpi_SetOptions(&flashSPI,XSP_MASTER_OPTION  + XSP_MANUAL_SSELECT_OPTION );
	XSpi_Start(&flashSPI);
	XSpi_IntrGlobalDisable(&flashSPI);

}
void sendToVideoBoard(int wordcnt){
	int i,j,bytecount;
	bytecount = videoSPIbuffer.send[1] *2 + 2;//number of bytes including wordcount
	for(i = 0; i< bytecount; i+=2){//send until end of buffer
		XSpi_Transfer(&videoSPI,&(videoSPIbuffer.send[i]),&(videoSPIbuffer.receive[i]),2); //send one data word (16bit)
//		for(j = 0; j< 200; ++j); // wait for PIC to empty buffer
	}
	bytecount = wordcnt *2;
	if((bytecount > 0) && (bytecount < SPIBUFFERSIZE)){//return expected number of bytes. Abort if bigger than buffer.
		videoSPIbuffer.send[SPIBUFFERSIZE -2]=0;
		videoSPIbuffer.send[SPIBUFFERSIZE -1]=0;
		videoSPIbuffer.receive[0]=0;
		for(i = 0; i<1000 ; i+=2){//send clk until data is there. Data should be there on the first try.
			XSpi_Transfer(&videoSPI,&(videoSPIbuffer.send[SPIBUFFERSIZE-2]),&(videoSPIbuffer.receive[0]),2); //send one data word (16bit)
			if((videoSPIbuffer.receive[0] == 0xaa)& (videoSPIbuffer.receive[1] == 0xaa))
				break;
		}
		for(i = 0; i<(bytecount) ; i+=2){//send until end of buffer
			XSpi_Transfer(&videoSPI,&(videoSPIbuffer.send[SPIBUFFERSIZE-2]),&(videoSPIbuffer.receive[i]),2); //send one data word (16bit)
//			for(j = 0; j< 200; ++j); // wait for PIC to empty buffer
		}
	}
}

void sendToClkBoard(int wordcnt){
	int i,j,bytecount;
	bytecount = clkSPIbuffer.send[1] *2 + 2;//number of bytes including wordcount
	for(i = 0; i< bytecount; i+=2){//send until end of buffer
		XSpi_Transfer(&clkSPI,&(clkSPIbuffer.send[i]),&(clkSPIbuffer.receive[i]),2); //send one data word (16bit)
//		for(j = 0; j< 200; ++j); // wait for PIC to empty buffer
	}
	bytecount = wordcnt *2;
	if((bytecount > 0) && (bytecount < SPIBUFFERSIZE)){//return expected number of bytes. Abort if bigger than buffer.
		clkSPIbuffer.send[SPIBUFFERSIZE -2]=0;
		clkSPIbuffer.send[SPIBUFFERSIZE -1]=0;
		clkSPIbuffer.receive[0]=0;
		for(i = 0; i<1000 ; i+=2){//send clk until data is there. Data should be there on the first try.
			XSpi_Transfer(&clkSPI,&(clkSPIbuffer.send[SPIBUFFERSIZE-2]),&(clkSPIbuffer.receive[0]),2); //send one data word (16bit)
			if((clkSPIbuffer.receive[0] == 0xaa)& (clkSPIbuffer.receive[1] == 0xaa))
				break;
		}
		for(i = 0; i<(bytecount) ; i+=2){//send until end of buffer
			XSpi_Transfer(&clkSPI,&(clkSPIbuffer.send[SPIBUFFERSIZE-2]),&(clkSPIbuffer.receive[i]),2); //send one data word (16bit)
		}
//		xil_printf("received %d  ",i); //
//		for(i = 0; i<40; ++i)
//			xil_printf("%x  ",videoSPIbuffer.receive[i]); //
	}
}

void cmdClkDacSet(char * buffer, int * len){
	char * dac_base = "dac_41";							//initialize string
	char * erase_set = "erase1";							//initialize string
	char * dac_1;
	int i;
	float storage;
	int channelAddress;
	int dacCode,hvDacCode;

	//extract erase/clear/purge parameters:
	for(i = 0; i < 6; ++i){								// Reads the Values for the  from the web page
		erase_set[5] = (char)(i+49);					// make string of current erase#
		dac_1=strstr(buffer,erase_set);				//get pointer to beginning of "erase_#"
		sscanf(dac_1+7,"%f",&erase_storage[i]);		//convert to float from start address
	}
	//extract desired voltages:
	dac_base[5] = 49; //ascii 1
	dac_1=strstr(buffer,dac_base);					//get pointer to beginning of "dac_41" (HV dac)
	sscanf(dac_1+7,"%f",&storage);					//convert to float from start address
	hvDacCode = (int)( storage /clk_hvbuffgain * 65536);   //for bias voltage
	if(hvDacCode >0xffff)hvDacCode = 0xffff;//trim to 16 bit
	if(hvDacCode <0)hvDacCode = 0;//trim to 16 bit

	//build command buffer for HV DAC
	clkSPIbuffer.send[0] = 0;
	clkSPIbuffer.send[1] = 2;
	clkSPIbuffer.send[2] = HV_CMD_WRITE;
	clkSPIbuffer.send[3] = 0;
	clkSPIbuffer.send[4] = hvDacCode>>8;
	clkSPIbuffer.send[5] = hvDacCode;		// TODO Warum keine truncation warning ?!
	sendToClkBoard(0);
	for(i =0; i< 2000; ++i); //wait for PIC to receive another cmd (todo gpio)

	for(i = 1; i <= 40; ++i){							// Reads the Values for the DAC channels from the web page
		dac_base[4] = (char)(((i-(i%10))/10)+48);		// upper digit
		dac_base[5] = (char)((i%10)+48);				// make string of current dac#
		dac_1=strstr(buffer,dac_base);					//get pointer to beginning of "dac_##"
		sscanf(dac_1+7,"%f",&storage);					//convert to float from start address
		dacCode = (int)( storage /clk_buffergain * 65536/(4*VREF_CLK) + 4*OFFSETVALUE_clk ) ; //gain is always 4.7 for clocks
		dacCode = (int)((dacCode - CVALUE_clk + 32768)* (65536/(MVALUE_clk+1)));
//		xil_printf("%s  %d %x\n\r",dac_base, channelAddress,dacCode);
		if(dacCode >0xffff)dacCode = 0xffff;//trim to 16 bit
		if(dacCode <0)dacCode = 0;//trim to 16 bit
		channelAddress = 7 + i; //start at 8, 0 writes to all groups simultaneous
		clkSPIbuffer.send[(i)*4] = 0;
		clkSPIbuffer.send[(i)*4+1] = DAC_INPUT_WRITE_MODE + channelAddress;
		clkSPIbuffer.send[(i)*4+2] = dacCode>>8;
		clkSPIbuffer.send[(i)*4+3] = dacCode;		// TODO Warum keine truncation warning ?!
	}

	//build command buffer
	clkSPIbuffer.send[0] = 0;
	clkSPIbuffer.send[1] = 81;// 40 voltages @2 words plus cmd word
	clkSPIbuffer.send[2] = DAC_CMD_WRITE;
	clkSPIbuffer.send[3] = 0;
	sendToClkBoard(0);


#ifdef DEBUG_OUTPUT
	xil_printf("cmdDacSet();\n\r");
#endif
	int reply_len;
	char return_delay[] = " ' DACs are Updated ' ";
	reply_len = strlen(return_delay);
	*len = generate_http_header(buffer, "txt", reply_len);
	strcat(buffer, return_delay);
}
void cmdBiasDacSet(char * buffer,int * len){
	Xuint32 chan;
	chan = 0; //init bit mask
	char * dac_base = "dac_00";							//initialize string
	char * dac_1;
	int i;
	unsigned int gain;
	float storage;
	int channelAddress;
	int dacCode;
	//build command buffer
	videoSPIbuffer.send[0] = 0;
	videoSPIbuffer.send[1] = 41; // 20 voltages @2 words plus cmd word
	videoSPIbuffer.send[2] = DAC_CMD_WRITE;
	videoSPIbuffer.send[3] = 0;
//extract desired voltages:
	for(i = 1; i <= 20; ++i){							// Reads the Values for the DAC channels from the web page
		dac_base[4] = (char)(((i-(i%10))/10)+48);
		dac_base[5] = (char)((i%10)+48);				// make string of current dac#
		dac_1=strstr(buffer,dac_base);					//get pointer to beginning of "dac_##"
		sscanf(dac_1+7,"%f",&storage);					//convert to float from start address
		float dac_voltage = ((storage/biasBuffGains[i-1]));//gain array starts at 0
		dacCode = (int)( dac_voltage * 65536/(4*VREF_BIAS) + 4*OFFSETVALUE_bias ) ;
		dacCode = (int)((dacCode - CVALUE_bias + 32768)* (65536/(MVALUE_bias+1)));
		if(dacCode >0xffff)dacCode = 0xffff;//trim to 16 bit
		if(dacCode <0)dacCode = 0;//trim to 16 bit
		channelAddress = 7 + i;
		videoSPIbuffer.send[(i)*4] = 0;
		videoSPIbuffer.send[(i)*4+1] = DAC_INPUT_WRITE_MODE + channelAddress;
		videoSPIbuffer.send[(i)*4+2] = dacCode>>8;
		videoSPIbuffer.send[(i)*4+3] = dacCode;		// TODO Warum keine truncation warning ?!
		xil_printf("cmdDacSet(%d %x %x %d );\n\r",i,dacCode,(dacCode &0xffff),channelAddress);
	}
	sendToVideoBoard(0);

	for(i =0; i< 2000; ++i) //wait for PIC to receive another cmd (TODO gpio)
		dac_1=strstr(buffer,"pga_g");//build command buffer for set gain
						//get pointer to beginning of "pga_g"
	sscanf(dac_1+6,"%u",&gain);					//convert to int from start address
	videoSPIbuffer.send[0] = 0;
	videoSPIbuffer.send[1] = 1; //one word
	videoSPIbuffer.send[2] = PIC_CMD_SET_GAIN;
	videoSPIbuffer.send[3] = gain & 0xFF;
	sendToVideoBoard(0);

#ifdef DEBUG_OUTPUT
	xil_printf("cmdDacSet();\n\r");
#endif
	int reply_len;
	char return_delay[] = " ' DACs are Updated ' ";
	reply_len = strlen(return_delay);
	*len = generate_http_header(buffer, "txt", reply_len);
	strcat(buffer, return_delay);
}
void cmdBiasDacReset(char * buffer, int * len){
#ifdef DEBUG_OUTPUT
	xil_printf("cmdDacReset()\n\r");
#endif
	videoSPIbuffer.index = 0;
	videoSPIbuffer.send[videoSPIbuffer.index++] = 0;
	videoSPIbuffer.send[videoSPIbuffer.index++] = 1;
	videoSPIbuffer.send[videoSPIbuffer.index++] = DAC_CMD_RESET;
	videoSPIbuffer.send[videoSPIbuffer.index++] = 0;
	sendToVideoBoard(0);
}
void cmdBiasDacInit(){
#ifdef DEBUG_OUTPUT
	xil_printf("cmdDacInit();\n\r");
#endif
	videoSPIbuffer.index = 0;
	videoSPIbuffer.send[videoSPIbuffer.index++] = 0;
	videoSPIbuffer.send[videoSPIbuffer.index++] = 6;
	videoSPIbuffer.send[videoSPIbuffer.index++] = DAC_GAIN_WRITE_MODE;
	videoSPIbuffer.send[videoSPIbuffer.index++] = MVALUE_bias>>8;
	videoSPIbuffer.send[videoSPIbuffer.index++] = MVALUE_bias & 0xFF;
	videoSPIbuffer.send[videoSPIbuffer.index++] = DAC_OFFSET_WRITE_MODE;
	videoSPIbuffer.send[videoSPIbuffer.index++] = CVALUE_bias>>8;
	videoSPIbuffer.send[videoSPIbuffer.index++] = CVALUE_bias & 0xFF;
	videoSPIbuffer.send[videoSPIbuffer.index++] = DAC_SPECIAL_FUNCTIONS_MODE + DAC_SF_WRITE_OFS0;
	videoSPIbuffer.send[videoSPIbuffer.index++] = OFFSETVALUE_bias>>8;
	videoSPIbuffer.send[videoSPIbuffer.index++] = OFFSETVALUE_bias & 0xFF;
	videoSPIbuffer.send[videoSPIbuffer.index++] = DAC_SPECIAL_FUNCTIONS_MODE + DAC_SF_WRITE_OFS1;
	videoSPIbuffer.send[videoSPIbuffer.index++] = OFFSETVALUE_bias>>8;
	videoSPIbuffer.send[videoSPIbuffer.index++] = OFFSETVALUE_bias & 0xFF;
	sendToVideoBoard(0);
}

void cmdAdcSet(char * buffer,int * len){
	int adcaddr;
	int regdata;
	char * find;
	find = strstr(buffer,"adcaddr");
	sscanf(find+8,"%x",&adcaddr);	// parse register address
	find = strstr(find,"regdat");
	sscanf(find+7,"%x",&regdata);	// parse register data
	reg[0] |= 1<<9; // set IO reset bit to re-lock SERDES interface
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[0]);

	videoSPIbuffer.index = 0;
	videoSPIbuffer.send[videoSPIbuffer.index++] = 0;
	videoSPIbuffer.send[videoSPIbuffer.index++] = 3;
	videoSPIbuffer.send[videoSPIbuffer.index++] = ADC_CMD_WRITE;
	videoSPIbuffer.send[videoSPIbuffer.index++] = 0;
	videoSPIbuffer.send[videoSPIbuffer.index++] = 0;
	videoSPIbuffer.send[videoSPIbuffer.index++] = adcaddr &0xff;
	videoSPIbuffer.send[videoSPIbuffer.index++] = (regdata >> 8) &0xff;
	videoSPIbuffer.send[videoSPIbuffer.index++] = regdata &0xff;
	sendToVideoBoard(0);
	xil_printf("cmdADC_Set() %d %d ;\n\r", adcaddr, regdata);
	reg[0] &= ~(1<<9); // clear IO reset bit
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[0]);
	int reply_len;
	char reply[] = " ' Adc reconfigured ' ";
	reply_len = strlen(reply);
	*len = generate_http_header(buffer, "txt", reply_len);
	strcat(buffer, reply);
}
void cmdAdcStart(char * buffer, int * len){
	char * startDate;
	int i;
	segmentIndex =columnIndex = rowIndex= 0;

	startDate = strstr(buffer,"mydate");
	for (i = 0; i < 50; i++)
		dateAsString[i]=0;
	strncpy(dateAsString, startDate + 7, 3);
	strncat(dateAsString, "/", 1);
	strncat(dateAsString, startDate + 13, 3);
	strncat(dateAsString, "/", 1);
	strncat(dateAsString, startDate + 19, 2);
	strncat(dateAsString, "/", 1);
	strncat(dateAsString, startDate + 24, 4);
	strncat(dateAsString, "/", 1);
	strncat(dateAsString, startDate + 31, 2);
	strncat(dateAsString, ":", 1);
	strncat(dateAsString, startDate + 36, 2);

	reg[1] = (reg[1] & 0xfc00ffff) | ((readaddr & 0x3ff) <<16); //readout start address
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR+4,reg[1]);
	reg[0] |= (1<<2); //set readout pending bit, but do not write yet. Send web reply first.
	xil_printf("cmdADC_Start() %x %x ;\n\r", reg[10], reg[11]);

#ifdef DEBUG_OUTPUT
	xil_printf("cmdADC_Start() %s %s ;\n\r", rowsAsString, columnsAsString);
#endif

	*len= generate_http_header(buffer,"txt",20);
	strcat(buffer,"\"toggle\" : \"done\",\n\r");// strlen = 20

}
void cmdClkTim(char * buffer, int * len){
	int i;
	unsigned int temp;
	Xuint32 control;
	char * delay_base = "dlya";							//initialize string
	char * dly_1;

	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[0] & 0xfffffff7);	//clear idle bit

	for (i = 0; i < 4; i++)
		rowsAsString[i]= columnsAsString[i]=0;

	//extract desired delay:
	delay_base[3] = 97;
	dly_1=strstr(buffer,delay_base);				//get pointer to beginning of "dlya"
	sscanf(dly_1+5,"%u",&temp);	// parse number of signal samples
	control = (temp <<16 ) & 0xFFFF0000;
	reg[20] = (reg[20]&0xffff) | control; //keep a local copy of register contents
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[20]);

	delay_base[3]++;
	dly_1=strstr(buffer,delay_base);				//get pointer to beginning of "dlyb"
	sscanf(dly_1+5,"%u",&temp);	// parse number of reset samples
	control = (temp <<16 )& 0xFFFF0000;
	reg[21] = (reg[21]&0xffff) | control; //keep a local copy of register contents
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR+4,reg[21]);

	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR+16,0x0000); // BRAM start address = 0

	for(i = 20; i < 30; i++){
		delay_base[3]++;
		dly_1=strstr(buffer,delay_base);				//get pointer to beginning of "dlyc to dlyl"
			sscanf(dly_1+5,"%u",&temp);	// parse delays
			control = (temp & 0xFFFF);	//16 bit
			reg[i] = (reg[i]&0xffff0000) | control; //keep a local copy of register contents
			Xil_Out32(XPAR_CCD_STATE_0_BASEADDR+4*i,reg[i]);
			xil_printf(" delay_data: %x \n\r", reg[i]);
	}

	dly_1 = strstr(buffer,"pixelX");
	sscanf(dly_1 + 7,"%u",&temp);
	columns = temp;
	strncpy(columnsAsString,dly_1+7,4);
	for(i=3; temp < 1000 ;i--,temp *=10){ // fill remaining digits with spaces
		columnsAsString[i]=32;}
	reg[10] = (reg[10]& 0xffff0000) +(((columns >>1) -1)&0xffff);
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR+40,reg[10]);

	dly_1 = strstr(buffer,"pixelY");
	sscanf(dly_1 + 7,"%u",&temp);
	rows = temp;
	strncpy(rowsAsString,dly_1+7,4);
	for(i=3; temp < 1000 ;i--,temp *=10){ // fill remaining digits with spaces
		rowsAsString[i]=32;}
	resolution =  rows * columns;
	reg[11] = (reg[11]& 0xffff0000) +(((rows >>1) -1)&0xffff);
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR+44,reg[11]);

	dly_1 = strstr(buffer,"clrcol");
	sscanf(dly_1 + 7,"%u",&temp);
	reg[12] = (reg[12]& 0xffff0000) +(((temp >>1) -1)&0xffff);
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR+48,reg[12]);

	dly_1 = strstr(buffer,"averaging");	//divide sum of samples for 16 bit transmit, shift by #bits
	sscanf(dly_1 + 10,"%u",&temp);
	control = (temp & 0xf)<<28; //shift no more than 10 bits so only 4 bit needed
	reg[1] = (reg[1] & 0x0fffffff) | control; //keep a local copy of register contents
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR+4,reg[1]);

	dly_1 = strstr(buffer,"digoff");	//offset between digital CDS sums. 16 bit.
	sscanf(dly_1 + 7,"%u",&temp);
	reg[1] = (reg[1]& 0xffff0000) +(temp&0xffff);
	xil_printf(" reg1 %x %d \n\r",reg[1],temp);
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR+4,reg[1]);

	dly_1 = strstr(buffer,"exptim");	//shutter open time
	sscanf(dly_1 + 7,"%u",&temp);
	temp = (temp*(reg[10]& 0xffff))/(((reg[20]& 0xffff0000)>>16) +(reg[20]& 0xffff)+((reg[21]& 0xffff0000)>>16)+(reg[21]& 0xffff)+((reg[22]& 0xffff)*5/3)+(reg[23]& 0xffff)+(reg[24]& 0xffff)); //calc num of pixels
	reg[13] = (reg[13] & 0xffff0000 ) +(temp  & 0xffff);
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR+52,reg[13]);
	Config_BRAM();

	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[0]);		//set idle bit if required

#ifdef DEBUG_OUTPUT
	xil_printf("cmdClkTim();\n\r");
#endif
	*len = generate_http_header(buffer, "txt", 18);
	strcat(buffer,"\"toggle\" : \"OK\",\n\r");// strlen = 18
}
void Config_BRAM(){
	int bram_ad, bram_da, fd;
	char * token_pointer;
	char BRAM_data[4000];
	//xil_printf(" BRAM_con_data: %s \n\r", BRAM_con_data);
	fd = mfs_file_open("timing.txt", MFS_MODE_READ);
	mfs_file_read(fd,BRAM_data,4000);
	token_pointer = strtok(BRAM_data, "x");
	token_pointer = strtok(NULL, "|");
//	xil_printf(" token_pointer: %s \n\r", token_pointer);
	while (token_pointer != NULL) {
		sscanf(token_pointer, "%d", &bram_ad);
		token_pointer = strtok(NULL, "x");
		sscanf(token_pointer, "%x", &bram_da);
		token_pointer = strtok(NULL, "|");
		Xil_Out32(XPAR_WAVEFORM_BRAM_CTRL_S_AXI_BASEADDR + (bram_ad <<2), bram_da); // write data from configuration file via bus to BRAM
//		xil_printf("address: %x data :%x\n\r", XPAR_WAVEFORM_BRAM_CTRL_S_AXI_BASEADDR + bram_ad, bram_da);
	}
	xil_printf(" BRAM config done\n\r");
	mfs_file_close(fd);
}

void cmdBiasPicRead(char * buffer,int * len){
#ifdef  DEBUG_OUTPUT
	xil_printf("cmdPicReadAdc()\n\r");
#endif
	Xuint32 * buffer_BRAM;
	Xuint32 digoff;
	Xuint32 Offset_PGA[4];
	int AdcValue;
	int i;
	char temp[22],data[1000];
	data[0]=temp[0]=0;
	float value;

	videoSPIbuffer.send[0] = 0;
	videoSPIbuffer.send[1] = 1;
	videoSPIbuffer.send[2] = PIC_CMD_READ_ADC;
	videoSPIbuffer.send[3] = 12;
	sendToVideoBoard(12); //read back 12 values
	// Data comes in bytes. Assembling values for the channels
	for(i = 0; i<12; i++){
		AdcValue = (videoSPIbuffer.receive[i*2])&0xff;
		AdcValue += (videoSPIbuffer.receive[i*2+1]<<8)&0x0f00;
		value = biasAdcGains[i]*(float)(AdcValue-biasAdcOffset[i]); //subtract offset in ADC units, scale voltage
		sprintf(temp,"\"ch%d\" : \"%2.2f\",\n\r",adcChannelMapping[i],value);
//		xil_printf("Read %d map %d val %d\n\r",i,adcChannelMapping[i],AdcValue);
		strcat(data,temp);
	}
	buffer_BRAM = ( u32 *)XPAR_VIDEO_BRAM_CTRL_S_AXI_BASEADDR;
	digoff = ((reg[1]&0xffff)<<8)>>((reg[1]>>28)&0xf);
//	xil_printf("digoff %d \n\r",digoff);
//	xil_printf("buffer_BRAM %x\n\r",buffer_BRAM);

	Offset_PGA[0] = (((buffer_BRAM[1]&0xff00) >>8)+((buffer_BRAM[1]&0xff) <<8))-digoff; 		//CH1
	Offset_PGA[2] = (((buffer_BRAM[0]&0xff00) >>8)+((buffer_BRAM[0]&0xff) <<8))-digoff;		//CH3
	Offset_PGA[3] = ((buffer_BRAM[0]>>24)+((buffer_BRAM[0]&0xff0000)>>8))-digoff; 			//CH4
	Offset_PGA[1] = ((buffer_BRAM[1]>>24)+((buffer_BRAM[1]&0xff0000)>>8))-digoff; 			//CH2
	for(i=0; i<4; ++i){
		sprintf(temp,"\"vioff0%d\" : \"%d\",\n\r",i+1,Offset_PGA[i]);
		xil_printf("videooffset PGA%d = %d \n\r",i+1,Offset_PGA[i]);
		strcat(data,temp);
	}
	xil_printf("cmdPicReadAdc()\n\r");
	*len= generate_http_header(buffer,"txt",strlen(data));
	strcat(buffer,data);
}
void cmdClkPicRead(char * buffer,int * len){
#ifdef  DEBUG_OUTPUT
	xil_printf("cmdPicReadAdc()\n\r");
#endif
	int adcval;
	int i;
	char temp[22],data[1000];
	data[0]=temp[0]=0;
	float value;

	clkSPIbuffer.send[0] = 0;
	clkSPIbuffer.send[1] = 1;
	clkSPIbuffer.send[2] = PIC_CMD_READ_ADC;
	clkSPIbuffer.send[3] = 21;
	sendToClkBoard(21); //read back 21 values Data comes in bytes. Assembling values for the channels
	for(i = 0; i<20; i++){
		adcval = (clkSPIbuffer.receive[i*2])&0xff;
		adcval += (clkSPIbuffer.receive[i*2+1]<<8)&0x0f00;
		value = clk_adc_gain *( adcval - clk_adc_offset );
		sprintf(temp,"\"ch%d\" : \"%2.2f\",\n\r",i,value);
		strcat(data,temp);
		//		xil_printf("Read %d hex %x val %d\n\r",i,adcval,value);
	}
	adcval = (clkSPIbuffer.receive[40])&0xff;
	adcval += (clkSPIbuffer.receive[41]<<8)&0x0f00;
	value = clk_hv_adc_gain*(float)(adcval-clk_hv_adc_offset);
	sprintf(temp,"\"ch20\" : \"%3.2f\",\n\r",value);
	strcat(data,temp);
	*len= generate_http_header(buffer,"txt",strlen(data));
	strcat(buffer,data);
}
void cmdPower(char * buffer,int * len){
#ifdef  DEBUG_OUTPUT
	xil_printf("cmdMainPower()\n\r");
#endif
	Xuint32 state;
	xil_printf("cmdMainPower()%d \n\r",buffer[15]);
	if (buffer[15]==49) {//power1 turns on power
		*len= generate_http_header(buffer,"txt",18);
		strcat(buffer,"\"toggle\" : \"On\",\n\r");
		ledRegister = (ledRegister | 0x11); //power is 10 turn on LED1 as well.
		Xil_Out32(XPAR_LEDS_BASEADDR,ledRegister); //turn on main power.
//		if ((ledRegister & 1) ==0){ //power was never on
			xil_printf("first time power on, clear DACs\n\r");
//			ledRegister = 3;
			clkSPIbuffer.send[0] = 0;
			clkSPIbuffer.send[1] = 1; //reset dacs
			clkSPIbuffer.send[2] = DAC_CMD_RESET;
			clkSPIbuffer.send[3] = 0;//fill remainder of 16 bit word
			sendToClkBoard(0);
			videoSPIbuffer.send[0] = 0;
			videoSPIbuffer.send[1] = 1;
			videoSPIbuffer.send[2] = DAC_CMD_RESET;
			videoSPIbuffer.send[3] = 0;
			sendToVideoBoard(0);
//		}

	} else{
		*len= generate_http_header(buffer,"txt",19);
		strcat(buffer,"\"toggle\" : \"Off\",\n\r");
		ledRegister = ledRegister & 0xffee; //power is 10 turn off LED1 as well.
		Xil_Out32(XPAR_LEDS_BASEADDR,ledRegister); //turn off main power.
	}

};void cmdReboot(char * buffer,int * len){
#ifdef  DEBUG_OUTPUT
	xil_printf("cmdReboot()\n\r");
#endif
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,(reg[0] | (3<<8)));		//set reset state machine bit
		*len= generate_http_header(buffer,"txt",22);
		strcat(buffer,"\"toggle\" : \"Reboot\",\n\r");
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,(reg[0]));		//clear reset bit
};
void cmdBiasEna(char * buffer,int * len){
#ifdef  DEBUG_OUTPUT
	xil_printf("cmdPicBiasEna()\n\r");
#endif
	Xuint8 chan;
	Xuint32 chan_2;
	int i;
	chan = 0; //init bit mask
	chan_2 = 0; //init bit mask
	if (!strncmp(buffer + 10, "enableoff", 9)) {
		*len= generate_http_header(buffer,"txt",23);
		strcat(buffer,"\"toggle\" : \"Disable\",\n\r");

	} else{
		char * find;
		char *temp = "enCh0";
		for(i = 1; i<5; i++){
			temp[4]=i+48; //ASCII 0++
			find = strstr(buffer,temp);
			if (find[7]==110)//look for ASSCII 'n' as in on
				chan += 1<<(i-1);
		}
		for(i = 0; i<21; i++){
			temp[4]=i+65; //ASCII A++
			find = strstr(buffer,temp);
			if (find[7]==110)//look for ASSCII 'n' as in on
				chan_2 += 1<<(i);
		}
		*len= generate_http_header(buffer,"txt",22);
		strcat(buffer,"\"toggle\" : \"Enable\",\n\r");
	}
	videoSPIbuffer.send[0] = 0;
	videoSPIbuffer.send[1] = 1;
	videoSPIbuffer.send[2] = PIC_CMD_SET_SEGMENT;
	videoSPIbuffer.send[3] = chan;
	sendToVideoBoard(0);
	xil_printf("cmdPicBiasEna(%x) clk %x)\n\r",chan,chan_2);

	clkSPIbuffer.send[0] = 0;
	clkSPIbuffer.send[1] = 3;
	clkSPIbuffer.send[2] = PIC_CMD_SET_SEGMENT;
	clkSPIbuffer.send[3] = 0;//fill remainder of 16 bit word
	clkSPIbuffer.send[5] = chan_2 & 0xff;//8 bits
	clkSPIbuffer.send[4] = (chan_2 >>8) &3;//2 bits for 10 bits in first word
	clkSPIbuffer.send[7] = (chan_2 >>10) & 0xff;//8 bits
	clkSPIbuffer.send[6] = (chan_2 >>18) &7;//3 bits for 10 bits in second word
	sendToClkBoard(0);
};
void cmdCcd(char * buffer,int * len){
#ifdef  DEBUG_OUTPUT
	xil_printf("cmdPicClkEna()\n\r");
#endif
	unsigned int temp;
	unsigned int Vclk_erase;
	Vclk_erase = (unsigned int)( erase_storage[0] /4.7 * 65536/(4*VREF_CLK) + 4*OFFSETVALUE_clk ) ; //gain is always 4.7 for clocks
	Vclk_erase = (unsigned int)((Vclk_erase - CVALUE_clk + 32768)*65536/(MVALUE_clk+1));
	if(Vclk_erase >0xfffe)Vclk_erase = 0xfffe;		//trim to 16 bit-1 hopefully the DAC does this gracefully

	unsigned int Vsub_erase;
	Vsub_erase = (unsigned int)(erase_storage[1] /179.12 * 65536);   //for HV clock Vmax=96V
	if(Vsub_erase >0xfffe)Vsub_erase = 0xfffe;		//trim to 16 bit-1

	unsigned int slew_erase;
	slew_erase = (unsigned int)(erase_storage[2]);
	if(slew_erase >0xfffe)slew_erase = 0xfffe;		//trim to 16 bit-1

	unsigned int time_erase;
	time_erase = (unsigned int)(erase_storage[3]* 1000);
	if(time_erase >0xfffe)time_erase = 0xfffe;		//trim to 16 bit-1

	unsigned int Vclk_purge;
	Vclk_purge = (unsigned int)(erase_storage[4] /4.7 * 65536/(4*VREF_CLK) + 4*OFFSETVALUE_clk ) ; //gain is always 4.7 for clocks
	Vclk_purge = (unsigned int)((Vclk_purge - CVALUE_clk + 32768)*65536/(MVALUE_clk+1));
	if(Vclk_purge >0xfffe)Vclk_purge = 0xfffe;		//trim to 16 bit-1

	unsigned int time_purge;
	time_purge = (unsigned int)(erase_storage[5]* 1000);
	if(time_purge >0xfffe)time_purge = 0xfffe;		//trim to 16 bit-1


	int j;
	sscanf(buffer + 13, "%d", &j);
	switch (j){
	case 1: //clear CCD
		reg[1] = (reg[1] & 0xfc00ffff) | ((clearaddr & 0x3ff) <<16); //clear start address
		Xil_Out32(XPAR_CCD_STATE_0_BASEADDR+4,reg[1]);
		reg[0] |= 1<<1; // set trigger bit
		Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[0]);
		while ((Xil_In32(XPAR_CCD_STATE_0_BASEADDR)&8) ==8)
			{}; //wait for ccd to leave idle mode
		xil_printf("cmdCCD Clear %x %d\n\r",reg[0],temp);
		reg[0] &= ~(1<<1); // clear trigger bit
		Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[0]);

		*len= generate_http_header(buffer,"txt",21);
		strcat(buffer,"\"toggle\" : \"cleared\",\n\r"); //strlen of "\"toggle\" : \"cleared\",\n\r" = 21
		break;
	case 2: //erase
		*len= generate_http_header(buffer,"txt",20);
		strcat(buffer,"\"toggle\" : \"erased\",\n\r"); //strlen of "\"toggle\" : \"erased\",\n\r" = 20
		xil_printf("cmdCCDerase\n\r");
		clkSPIbuffer.send[0] = 0;
		clkSPIbuffer.send[1] = 5;
		clkSPIbuffer.send[2] = HV_CMD_ERASE;
		clkSPIbuffer.send[3] = 0;//fill remainder of 16 bit word
		clkSPIbuffer.send[4] = Vclk_erase>>8;
		clkSPIbuffer.send[5] = Vclk_erase;
		clkSPIbuffer.send[6] = Vsub_erase>>8;
		clkSPIbuffer.send[7] = Vsub_erase;
		clkSPIbuffer.send[8] = slew_erase>>8;
		clkSPIbuffer.send[9] = slew_erase;
		clkSPIbuffer.send[10] = time_erase>>8;
		clkSPIbuffer.send[11] = time_erase;
		sendToClkBoard(0);
		break;
	case 3: //purge
		*len= generate_http_header(buffer,"txt",20);
		strcat(buffer,"\"toggle\" : \"purged\",\n\r"); //strlen of "\"toggle\" : \"purged\",\n\r" = 20
		xil_printf("cmdCCDpurge\n\r");
		clkSPIbuffer.send[0] = 0;
		clkSPIbuffer.send[1] = 3;
		clkSPIbuffer.send[2] = HV_CMD_PURGE;
		clkSPIbuffer.send[3] = 0;//fill remainder of 16 bit word
		clkSPIbuffer.send[4] = Vclk_purge>>8;
		clkSPIbuffer.send[5] = Vclk_purge;
		clkSPIbuffer.send[6] = time_purge>>8;
		clkSPIbuffer.send[7] = time_purge;
		sendToClkBoard(0);
		break;
	}
};
void cmdIdle(char * buffer,int * len){
#ifdef  DEBUG_OUTPUT
	xil_printf("cmdPicClkEna()\n\r");
#endif
	if (reg[0] & (1<<3)){									//is idle bit set?
		reg[0] &= ~(1<<3);									//clear idle bit
		Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[0]);
		*len= generate_http_header(buffer,"txt",26);
		strcat(buffer,"\"toggle\" : \"Idlemode Off\",\n\r");
		xil_printf("idle off\n\r");
	}else{
		reg[0] |= 1<<3;										//set idle bit
		Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[0]);
		*len= generate_http_header(buffer,"txt",22);
		strcat(buffer,"\"toggle\" : \"Idlemode\",\n\r");
		xil_printf("idle on\n\r");
	}
};
void cmdLiveNoise(char * buffer,int * len){
	Xuint32 avg[4];						//Average of each Channel
	long int sample[4];					//Addition of all values in each row
	Xuint32 * buffer_BRAM;
	Xuint32 timeout = 0;
	Xuint32 tempidle, tempcol;
	int i;
	const Xuint32 ncols = 500;
	unsigned long Noise_Ch[4];					//Noise of each Channel (power of 2)
	char temp[50],data[100];
	data[0]=temp[0]=0;
	for(i=0;i<4;i++){
		sample[i]=0;
		avg[i]= 0;
		Noise_Ch[i]=0;}
	tempidle = Xil_In32(XPAR_CCD_STATE_0_BASEADDR);
	xil_printf("LiveNoise status %x\r\n",tempidle);

	tempcol = reg[10]; //save state of image size
	reg[10] = (reg[10]& 0xffff0000) +(ncols+10); //hardcode to 2068 total cols for noise (discard 10 for each input)
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR+40,reg[10]);

	tempidle = reg[0]; //save state of control register
	reg[1] = (reg[1] & 0xfc00ffff) | ((noiseaddr & 0x3ff) <<16); 	//LiveNoise start address
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR+4,reg[1]);
	reg[0] |= 3<<1; 												//set pending bit and trigger
	reg[0] &= ~(1<<3); 												//clear idle bit
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[0]);
	while ((Xil_In32(XPAR_CCD_STATE_0_BASEADDR)&8)==8){				//wait for ccd to start reading
		timeout++;
		if (timeout == 500000){
			xil_printf("Timeout during wait for LiveNoise reading start\r\n");
			return;
		}
	};
	reg[0] &= ~(1<<1); 												// clear trigger bit
	xil_printf("read noise running\r\n");
	timeout=0;
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[0]);
	while ((Xil_In32(XPAR_CCD_STATE_0_BASEADDR)&8)==0){ 			//wait until readout complete
		if (timeout == 500000){
			xil_printf("Timeout during wait for CCD read LiveNoise\r\n");
			return;
		}
	};
	reg[0] &= ~(1<<2); 												// clear pending bit
	buffer_BRAM = ( u32 *)XPAR_VIDEO_BRAM_CTRL_S_AXI_BASEADDR;
	for(i=20;i<(2*ncols+20);i+=2){
		avg[0]+=((buffer_BRAM[i+1]&0xff00) >>8)+((buffer_BRAM[i+1]&0xff) <<8);			//Ch1
		avg[2]+=((buffer_BRAM[i]&0xff00) >>8)+((buffer_BRAM[i]&0xff) <<8);				//Ch3
		avg[3]+=(buffer_BRAM[i]>>24)+((buffer_BRAM[i]&0xff0000)>>8);						//Ch4
		avg[1]+=(buffer_BRAM[i+1]>>24)+((buffer_BRAM[i+1]&0xff0000)>>8);					//Ch2
	}

	for(i=20;i<(2*ncols+20);i+=2){
		sample[0]=((((buffer_BRAM[i+1]&0xff00) >>8)+((buffer_BRAM[i+1]&0xff) <<8))*ncols)-avg[0];	//Ch1
		sample[2]=((((buffer_BRAM[i]&0xff00) >>8)+((buffer_BRAM[i]&0xff) <<8))*ncols)-avg[2];		//Ch3
		sample[3]=(((buffer_BRAM[i]>>24)+((buffer_BRAM[i]&0xff0000)>>8))*ncols)-avg[3];				//Ch4
		sample[1]=(((buffer_BRAM[i+1]>>24)+((buffer_BRAM[i+1]&0xff0000)>>8))*ncols)-avg[1];			//Ch2
		Noise_Ch[0] += (sample[0]*sample[0])/ncols; 		//Calculation Noise CH1
		Noise_Ch[1] += (sample[1]*sample[1])/ncols; 		//Calculation Noise CH2
		Noise_Ch[2] += (sample[2]*sample[2])/ncols;	 		//Calculation Noise CH3
		Noise_Ch[3] += (sample[3]*sample[3])/ncols; 		//Calculation Noise CH4
	}
	for(i=0; i<4; ++i){
		Noise_Ch[i] = (Noise_Ch[i]*16)/ncols/ncols ;				//Calculate Noise*16 (transmit integers only)
		sprintf(temp,"\"noise0%d\" : \"%d\",\n\r",i+1,Noise_Ch[i]);
		xil_printf("Avg %x Noise Ch %d = %x  sample %d\n\r",(avg[i] >> 7),i+1,(Noise_Ch[i]),sample[i]);
		strcat(data,temp);
	}
	*len= generate_http_header(buffer,"txt",26+strlen(data));
	strcat(buffer,"\"toggle\" : \"Noisemode On\",\n\r");
	strcat(buffer,data);

	reg[10] = tempcol; //restore image size
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR+40,reg[10]);
	reg[0]=tempidle; //restore state of control register
	Xil_Out32(XPAR_CCD_STATE_0_BASEADDR,reg[0]);						//set idle bit if required
}
void cmdsector(char * buffer,int * len){
 // Write MFS to flash
	if(eraseSector(MFS_FLASHADDRESS,MFSBLOCKS)==0)
	   xil_printf("Erase Error!! \n\r");
	xil_printf("Memory Erased \n\r");

	if(flashwrite(MFS_FLASHADDRESS,MFSSIZE,MFS_BASE_ADDRESS+4)==0)
	   xil_printf("Flash Write Error!! \n\r");
	xil_printf("Flash write done \n\r");
	*len = generate_http_header(buffer, "txt", 2);
	strcat(buffer, "OK");
}
int flashwrite(int address, int pagecount, char * flashdata){
	int i,j;
	Xuint8  send_data[260], recv_data[2];

	for(i=0;i<pagecount;i++){
		send_data[0]=WREN; //write enable
		XSpi_SetSlaveSelect(&flashSPI,1);
		XSpi_Transfer(&flashSPI,&(send_data[0]),NULL,1);
		XSpi_SetSlaveSelect(&flashSPI,0);
		for(j=0;j<100;j++){} //wait for flash

		send_data[0]=PP; //page program
		send_data[1]=0xff&(address>>16); //lower 8 bit should be zero
		send_data[2]=0xff&(address>>8); //lower 8 bit should be zero
		send_data[3]=0;
		memcpy(&(send_data[4]),flashdata,256);

		XSpi_SetSlaveSelect(&flashSPI,1);
		XSpi_Transfer(&flashSPI,&(send_data[0]),NULL,260); //send one page
		XSpi_SetSlaveSelect(&flashSPI,0);

		for(j=0;j<100;j++){} //wait for flash
		send_data[0]=RDSR; //read status register
		send_data[1]=0;
		for(j=0;j<1000;j++){
			XSpi_SetSlaveSelect(&flashSPI,1);
			XSpi_Transfer(&flashSPI,&(send_data[0]),&(recv_data[0]),2); //send 4 bytes
			XSpi_SetSlaveSelect(&flashSPI,0);
			if ((recv_data[1]&1)==0)
				break;
		} //wait for flash
		if (j>998){
			xil_printf("Flash write timeout \n\r");
			return 0; //timeout during erase
		}
		address+=256;
		flashdata+=256;
	}
	xil_printf("Flash write done \n\r");
	return 1;
}
int eraseSector(Xuint32 startAddr,Xuint32 num64K){
	Xuint8   send_data[4], recv_data[4];
	int i,j;
	send_data[2]=0;
	send_data[3]=0;
	xil_printf("start Erase %d blocks\n\r",num64K);

	for(i=0;i<num64K;i++){
		send_data[0]=WREN; //write enable
		send_data[1]=0;
		XSpi_SetSlaveSelect(&flashSPI,1);
		XSpi_Transfer(&flashSPI,&(send_data[0]),&(recv_data[0]),1);
		XSpi_SetSlaveSelect(&flashSPI,0);
		for(j=0;j<100;j++){} //wait for flash
		send_data[0]=SE; //erase 64k block
		send_data[1]=0xff&(startAddr>>16); //lower 16 bit should be zero
		XSpi_SetSlaveSelect(&flashSPI,1);
		XSpi_Transfer(&flashSPI,&(send_data[0]),&(recv_data[0]),4); //send 4 bytes
		XSpi_SetSlaveSelect(&flashSPI,0);
		for(j=0;j<100;j++){} //wait for flash
		send_data[0]=RDSR; //read status register
		send_data[1]=0;
		for(j=0;j<100000;j++){
			XSpi_SetSlaveSelect(&flashSPI,1);
			XSpi_Transfer(&flashSPI,&(send_data[0]),&(recv_data[0]),2); //send 4 bytes
			XSpi_SetSlaveSelect(&flashSPI,0);
			if ((recv_data[1]&1)==0)
				break;
		} //wait for flash
		xil_printf("Memory Erased %x\n\r",j);
		if (j>99990){
			xil_printf("timeout at %x\n\r",startAddr);
			return 0;} //timeout during erase
		startAddr+=0x10000;//next 64k block
	}
	return 1;
};
