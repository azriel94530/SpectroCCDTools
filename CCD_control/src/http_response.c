/*
 * Copyright (c) 2009 Xilinx, Inc.  All rights reserved.
 *
 * Xilinx, Inc.
 * XILINX IS PROVIDING THIS DESIGN, CODE, OR INFORMATION "AS IS" AS A
 * COURTESY TO YOU.  BY PROVIDING THIS DESIGN, CODE, OR INFORMATION AS
 * ONE POSSIBLE   IMPLEMENTATION OF THIS FEATURE, APPLICATION OR
 * STANDARD, XILINX IS MAKING NO REPRESENTATION THAT THIS IMPLEMENTATION
 * IS FREE FROM ANY CLAIMS OF INFRINGEMENT, AND YOU ARE RESPONSIBLE
 * FOR OBTAINING ANY RIGHTS YOU MAY REQUIRE FOR YOUR IMPLEMENTATION.
 * XILINX EXPRESSLY DISCLAIMS ANY WARRANTY WHATSOEVER WITH RESPECT TO
 * THE ADEQUACY OF THE IMPLEMENTATION, INCLUDING BUT NOT LIMITED TO
 * ANY WARRANTIES OR REPRESENTATIONS THAT THIS IMPLEMENTATION IS FREE
 * FROM CLAIMS OF INFRINGEMENT, IMPLIED WARRANTIES OF MERCHANTABILITY
 * AND FITNESS FOR A PARTICULAR PURPOSE.
 *
 */

#include <string.h>
#include "config_apps.h"
#include "mfs_config.h"
#include "lwip/inet.h"

//#include "globals.h"
#include "commands.h"
#include "webserver.h"

#define ELF_FLASHADDRESS	0x300000 //start of ELF in flash memory from flash boot code!!!

#define maxBRAMlen	30000
extern int BRAM_seq;//also extern in globals.h
extern int BRAMloc;
extern char *webfilename;
extern int file_len;
extern int flash_offset;
extern Xuint16 imageData[5000*5000];

char * BRAM_tim = (char *)imageData;

char *notfound_header =
	"<html> \
	<head> \
		<title>404</title> \
  		<style type=\"text/css\"> \
		div#request {background: #eeeeee} \
		</style> \
	</head> \
	<body> \
	<h1>404 Page Not Found</h1> \
	<div id=\"request\">";

char *notfound_footer =
	"</div> \
	</body> \
	</html>";

/* dynamically generate 404 response:
 *	this inserts the original request string in betwween the notfound_header & footer strings
 */
int do_404(struct tcp_pcb *pcb, char *req, int rlen)
{
	int len, hlen;
	int BUFSIZE = 1024;
	char buf[BUFSIZE];
	err_t err;

	len = strlen(notfound_header) + strlen(notfound_footer) + rlen;
	hlen = generate_http_header(buf, "html", len) - len; //this is sent in multiple parts

	if (tcp_sndbuf(pcb) < hlen) {
		xil_printf("cannot send 404 message, tcp_sndbuf = %d bytes, message length = %d bytes\r\n",
				tcp_sndbuf(pcb), hlen);
		return -1;
	}
	if ((err = tcp_write(pcb, buf, hlen, 1)) != ERR_OK) {
		xil_printf("%s: error (%d) writing 404 http header\r\n", __FUNCTION__, err);
		return -1;
	}
	tcp_write(pcb, notfound_header, strlen(notfound_header), 1);
	tcp_write(pcb, req, rlen, 1);
	tcp_write(pcb, notfound_footer, strlen(notfound_footer), 1);

	return 0;
}
void mcs_flash(){									// Write MCS to flash
	Xuint32 blockcount, bytecount;
	char temp[3];
	char * datastart;
	int data_bytes;
	unsigned int val,i;

	if(flash_offset == -1){							//no update if no bit or elf file
		xil_printf("Error, offset unknown\r\n");
		return;
	}
	xil_printf("parse MCS this takes a while \r\n");
	bytecount = 0;
	datastart = BRAM_tim;
	temp[2]= 0;
	while(1){
		i=0; //make sure i=0 for non-data lines so we properly read next data line
		datastart = strstr(datastart, ":"); 		//find next mcs record start
		if (!strncmp(datastart + 7, "00", 2)){		//record type: data record
			temp[0]= datastart[1];
			temp[1]= datastart[2];
			sscanf(temp,"%x",&data_bytes);			//scan for length of data record
			for(i=0;i<(data_bytes*2);i+=2){
				temp[0]= datastart[i+9];
				temp[1]= datastart[i+10];

				sscanf(temp,"%x",&val);
				BRAM_tim[bytecount]=val;
				bytecount++;
			}
		}else if(!strncmp(datastart + 7, "01", 2)){		//record type: end of file record
			break;
			}
		datastart= datastart+i+1;
	}
	xil_printf("write %d bytes MCS to 0x %x\r\n",bytecount,flash_offset);
	blockcount=(bytecount +0xffff)>>16;
	eraseSector( flash_offset, blockcount);
	xil_printf("write sectors 0x %x\r\n",(bytecount+0xff)>>8);
	flashwrite( flash_offset,(int) (bytecount+0xff)>>8,BRAM_tim);
}
void mfs_bram(char * buffstart,int bufflen){
	mfs_delete_file(webfilename);
	int BRAMfd = mfs_file_open(webfilename, MFS_MODE_CREATE);
	file_len = mfs_file_write (BRAMfd,buffstart,bufflen);
	BRAM_seq = 0;											// if end is found set BRAM_seq to 100 to signal data is complete
	mfs_file_close(BRAMfd);
	xil_printf("@ is_cmd_BRAM 3  %d %d\n\r" ,BRAMloc,file_len);
//	BRAMfd = mfs_file_open(webfilename, MFS_MODE_READ);
//	file_len = mfs_file_lseek(BRAMfd, 0, MFS_SEEK_END);
//	xil_printf("wrote to mfs:  %d\n\r" ,file_len);
//	mfs_file_close(BRAMfd);
}
int do_http_post(struct tcp_pcb *pcb, char *req, int rlen)
{
#ifdef DEBUG_OUTPUT

#endif
	char  notFound[]  = "Command not found!\n\r";
	int len=0;
	char * start_BRAM_file;
	char * start_str;
	char * mcssel;
	int offset;

	if(!strncmp(req+6, "cmd", 3)  ){
		if ( !strncmp(req + 10, "FILExhrBRAM", 11)){
			webfilename= "timing.txt";
			start_str="Content-Type: text/plain";					// search for the start of the relevant data
			offset=28;}
		if ( !strncmp(req + 10, "FILExhrTIME", 11)){
			webfilename= "index.html";
			start_str="Content-Type: text/html";
			offset=27;}
		if ( !strncmp(req + 10, "FILExhrBIAS", 11)){
			webfilename= "clkboard.html";
			start_str="Content-Type: text/html";
			offset=27;}
		if ( !strncmp(req + 10, "FILExhrMCS", 10)){
			webfilename= "CCD_readout.mcs";
			start_str="Content-Type: application/octet-stream";
			offset=42;
			mcssel=strstr(req,"mcsselect");							//get pointer to beginning of "mcsselect"
			if(!strncmp(mcssel+14, "bit", 3))
				flash_offset=0;
			else if(!strncmp(mcssel+14, "elf", 3))
				flash_offset=0x300000;
			else
				flash_offset=-1;
		}
		if ( !strncmp(req + 10, "FILExhr", 7)){
			start_BRAM_file = strstr(req,start_str)+offset; //get pointer to start of file in req buffer
			mcssel =strstr(req, "Content-Length: ");  //temporary pointer to file length in buffer
			sscanf(mcssel + 16,"%u",&file_len);
			mcssel =strstr(mcssel, "--------");  //temporary pointer to separator
			file_len = file_len -(start_BRAM_file-mcssel);
			if (file_len <= ((req+rlen)-start_BRAM_file)){						// if all the data is send in one packet, copy only the data
				BRAM_seq=0 ;
				mcssel= req+rlen -200; //go back 200 char from the end to look for end separator
				mcssel =strstr(mcssel, "--------");  //temporary pointer to separator
				file_len=file_len -((req+rlen)-mcssel)-2;
				if ( !strncmp(req + 10, "FILExhrMCS", 10)){
					memcpy(BRAM_tim,start_BRAM_file,file_len);
					mcs_flash();
				}else
					mfs_bram(start_BRAM_file,file_len);
				len= generate_http_header(req,"txt",4);
				strcat(req,"Read");
				xil_printf("@ is_cmd_BRAM 1\n\r");
			}
			else{
					offset=rlen - (start_BRAM_file - req); //amount of data in this packet
					file_len = file_len-offset;
					memcpy(BRAM_tim,start_BRAM_file,offset);	//copy first part of received file into memory. Write once file is complete.
					BRAMloc = offset;
					BRAM_seq = 4000;															// value how many packets could be received until alert an error
					xil_printf("@ is_cmd_BRAM 2  len %d loc%d req%x start_file%x rlen%d\n\r",file_len,BRAMloc, req, start_BRAM_file, rlen);
					return 0; //do not send reply
			}
		}
		else if (!strncmp(req + 10, "ledxhr", 6)) {
			cmdAdcSet(req,&len);
		}else if (!strncmp(req + 10, "enable", 6)) {
			cmdBiasEna(req,&len);
		}else if (!strncmp(req + 10, "power", 5)){
			cmdPower(req,&len);
		}else if (!strncmp(req + 10, "readclk", 7)){ //read back clk voltages
			cmdClkPicRead(req,&len);
		}else if (!strncmp(req + 10, "reboot", 6)){ //reset state machine for now
			cmdReboot(req,&len);
		}else if (!strncmp(req + 10, "clkdac", 6)){ //update clk voltages
			cmdClkDacSet(req,&len);
		}else if (!strncmp(req + 10, "timing", 6)){ //set delay registers
			cmdClkTim(req,&len);
		}else if(!strncmp(req + 10, "dacxhr", 6)){ // set voltages and PGA gain
			cmdBiasDacSet(req,&len);
		}else if (!strncmp(req + 10, "readxhr", 7)){ //read bias voltages
			cmdBiasPicRead(req,&len);
		}else if(!strncmp(req + 10, "adcxhr", 6)){	//start image acquisition
			cmdAdcStart(req,&len);
		}else if(!strncmp(req + 10, "adcdon", 6)){	//done? just say done
			len= generate_http_header(req,"txt",20);
			strcat(req,"\"toggle\" : \"done\",\n\r");// strlen = 20
		}else if(!strncmp(req + 10, "dacinit", 7)){ // not implemented in web REDUNDANT(done automatically at startup by PIC)
			cmdBiasDacInit();
		}else if(!strncmp(req + 10, "dacreset", 8)){ // not implemented in Web interface Bias DAC reset
			cmdBiasDacReset(req,&len);
		}else if (!strncmp(req + 10, "ccd", 3)){ // clear CCD
			cmdCcd(req,&len);
		}else if (!strncmp(req + 10, "sector", 6)){ // set settings as defaults
			cmdsector(req,&len);
		}else if (!strncmp(req + 10, "idle", 4)){ //start idle mode
			cmdIdle(req,&len);
		}else if (!strncmp(req + 10, "livnoi", 4)){ //start idle mode
			cmdLiveNoise(req,&len);
		}else{ // not found for no cmd or unknown cmd
			len = generate_http_header(req,"txt",strlen(notFound));
			strcat(req,notFound);
		}
	}else{
		len = generate_http_header(req,"txt",strlen(notFound));
		strcat(req,notFound);
#ifdef DEBUG_OUTPUT
       xil_printf("No command received!\n\r");
#endif
	}
	if (tcp_write(pcb, req, len, 1) != ERR_OK) {
		xil_printf("error writing http POST response to socket\n\r");
		xil_printf("http header = %s\r\n", req);
		return -1;
	}else
		tcp_output(pcb);
	return 0;
}

/* respond for a file GET request */
int do_http_get(struct tcp_pcb *pcb, char *req, int rlen)
{
	int BUFSIZE = 1400;
	char filename[MAX_FILENAME];
	unsigned char buf[BUFSIZE];
	int fsize, hlen, n,fits_hlen;
	int fd, sndbuf, pixls;
	char *fext;
	char * fits_header;
	err_t err;

	/* determine file name */
	extract_file_name(filename, req, rlen, MAX_FILENAME);

	/* respond with 404 if not present */
	if (mfs_exists_file(filename) != 1) {
		xil_printf("requested file %s not found, returning 404\r\n", filename);
		do_404(pcb, req, rlen);
		return -1;
	}

	if(!strncmp(filename,"image.fits",10)){
		fits_header = makeFitsHdr();
		fits_hlen = strlen(fits_header);
			/* get a pointer to file extension */
			fext = get_file_extension(filename);
			/* write the http headers */
			pixls = pixels()*2; //number of image bytes
			hlen = generate_http_header(buf, fext, pixls+fits_hlen-2) -(pixls+fits_hlen-2); //need just header length
//			if (tcp_write(pcb, buf, hlen,1) != hlen) {
			if ((err = tcp_write(pcb, buf, hlen, 1)) != ERR_OK) {
				xil_printf("error writing http header to socket\n\r");
				xil_printf(" length %d   %d  http header = %s\n\r",fd,hlen, buf);
				return -1;
			}
			if ((err = tcp_write(pcb, fits_header, fits_hlen-2, 0)) != ERR_OK) {
				xil_printf("error writing fits header to socket\n\r");
				xil_printf("fits header = %s\n\r", fits_header);
				return -1;
			}
//			if ((err = tcp_write(pcb, imageLoc(), pixls, 0)) != ERR_OK) {
//				xil_printf("error start writing fits data to socket \n\r");
//				return -1;
//			}
			fsize = pixls;	//number of pixels that have not been sent out.
			fd = (int)imageLoc(); //contains pointer to image array
			while (fsize) { //there is more pixel data to packk into send buffer
				sndbuf = tcp_sndbuf(pcb);
//        		   xil_printf("writing part %x  %x %d %d\r\n",imageLoc(),fd,sndbuf, fsize);
				if (sndbuf < BUFSIZE) {
					http_arg *a = (http_arg *)pcb->callback_arg;
					a->fd = fd;
					a->fsize = fsize;
					/* not enough space in sndbuf to send anything useful, so send remaining bytes when there is space */
					xil_printf("sending pointers to callback: %x  %d\r\n", fd,fsize);
					return -1;
				}
				n=BUFSIZE;
				if (BUFSIZE > fsize)
					n=fsize;	//read one buffer or the rest.
				if ((err = tcp_write(pcb, (char *) fd, n, 0)) != ERR_OK) {
            		   xil_printf("error writing part %x  %x %d\r\n",err,fd, sndbuf);
            		   return -1;
            	   }
				fd +=n;
				fsize -=n;
			}
			xil_printf("done writing\n\r"); //debug check
		return 0;
		}

	/* respond with correct file */

	/* debug statement on UART */
        xil_printf("http GET: %s\r\n", filename);

	/* get a pointer to file extension */
	fext = get_file_extension(filename);
	fd = mfs_file_open(filename, MFS_MODE_READ);

	/* obtain file size,
	 * note that lseek with offset 0, MFS_SEEK_END does not move file pointer */
	fsize = mfs_file_lseek(fd, 0, MFS_SEEK_END);

	/* write the http headers */
	hlen = generate_http_header(buf, fext, fsize) - fsize; // need just header
	if ((err = tcp_write(pcb, buf, hlen, 1)) != ERR_OK) {
		xil_printf("error (%d) writing http header to socket\r\n", err);
		xil_printf("attempted to write #bytes = %d, tcp_sndbuf = %d\r\n", hlen, tcp_sndbuf(pcb));
		xil_printf("http header = %s\r\n", buf);
		return -1;
	}
	/* now write the file */
	while (fsize) {
		int sndbuf;
		sndbuf = tcp_sndbuf(pcb);
		if (sndbuf < BUFSIZE) {
			/* not enough space in sndbuf, so send remaining bytes when there is space */
			/* this is done by storing the fd in as part of the tcp_arg, so that the sent
			   callback handler knows to send data */
			http_arg *a = (http_arg *)pcb->callback_arg;
			a->fd = fd;
			a->fsize = fsize;
			return -1;
		}

		n = mfs_file_read(fd, buf, BUFSIZE);

		if ((err = tcp_write(pcb, buf, n, 1)) != ERR_OK) {
			xil_printf("error writing file (%s) to socket, remaining unwritten bytes = %d\r\n",
					filename, fsize - n);
			xil_printf("attempted to tcp_write %d bytes, tcp write error = %d\r\n", n, err);
			break;
		}

		fsize -= n;
	}

	mfs_file_close(fd);

	return 0;
}

void dump_payload(char *p, int len)
{
	int i, j;

	for (i = 0; i < len; i+=16) {
		for (j = 0; j < 16; j++)
			xil_printf("%c ", p[i+j]);
		xil_printf("\r\n");
	}
	xil_printf("total len = %d\r\n", len);
}
int do_http_bram(struct tcp_pcb *pcb, char *req, int rlen)
{
	int len=0;
	char * mcssel;
		if (file_len <= rlen){
			BRAM_seq =0 ;
			mcssel= req+rlen -200; //go back 200 char from the end to look for end separator
			mcssel =strstr(mcssel, "--------");  //temporary pointer to separator
			file_len=file_len -((req+rlen)-mcssel)-2;

			memcpy(BRAM_tim + BRAMloc,req,file_len); //copy remaining file
			BRAMloc += file_len;
			xil_printf("@ is_cmd_BRAM 5 len%d  addr %h\n\r",BRAMloc,BRAM_tim);
			if ( !strncmp(webfilename, "CCD_readout.mcs", 15))
				mcs_flash();
			else
				mfs_bram(BRAM_tim,BRAMloc);
			len= generate_http_header(req,"txt",4);
			strcat(req,"Read");
			//no reply unless end of file
			if (tcp_write(pcb, req, len, 1) != ERR_OK) {
				xil_printf("error writing http POST response to socket\n\r");
				xil_printf("http header = %s\r\n", req);
				return -1;
			}else
				tcp_output(pcb);
		}
		else {
			file_len = file_len - rlen;
			memcpy(BRAM_tim + BRAMloc,req,rlen);// copy the whole buffer, for 2nd and later packets
			BRAMloc += rlen;
			BRAM_seq-- ;	// count down max packet load
#ifdef DEBUG_OUTPUT
			xil_printf("@ is_cmd_BRAM 4 len%d\n\r",file_len);
#endif
		}
		return 0;
}

/* generate and write out an appropriate response for the http request */
/* 	this assumes that tcp_sndbuf is high enough to send at least 1 packet */
int generate_response(struct tcp_pcb *pcb, char *http_req, int http_req_len)
{
	char *get_str = "GET";
	char *post_str = "POST";
//	xil_printf("loc port %d remote port %d\r\n",pcb->local_port,pcb->remote_port);
	if (!strncmp(http_req, get_str, strlen(get_str)))
		return do_http_get(pcb, http_req, http_req_len);
	else if (!strncmp(http_req, post_str, strlen(post_str)))
		return do_http_post(pcb, http_req, http_req_len);
	else if  (BRAM_seq >1 ) //if transmitting Bram
		return do_http_bram(pcb, http_req, http_req_len);
	else{
//		xil_printf("request_type != GET|POST %s\r\n",http_req);
		dump_payload(http_req, http_req_len);
		return do_404(pcb, http_req, http_req_len);
	}
}
