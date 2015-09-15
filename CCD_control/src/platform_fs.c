/*
 * Copyright (c) 2008 Xilinx, Inc.  All rights reserved.
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

#include "mfs_config.h"
#include "config_apps.h"
#include "xspi.h"
#include "flashMFS.h"

int platform_init_fs(){
Xuint32 address;
Xuint8 * send_data;
char savemem[4];

#ifdef FLASH_MFS
address = MFS_FLASHADDRESS;
send_data = (Xuint8 *) MFS_BASE_ADDRESS;
savemem[0]=send_data[0];
savemem[1]=send_data[1];
savemem[2]=send_data[2];
savemem[3]=send_data[3];//save contents of memory

send_data[0]=READ; //read
send_data[1]=0xff&(address>>16); //lower 8 bit should be zero
send_data[2]=0xff&(address>>8); //lower 8 bit should be zero
send_data[3]=0;
XSpi_SetSlaveSelect(&flashSPI,1);
XSpi_Transfer(&flashSPI,&(send_data[0]),&(send_data[0]),MFSSIZE*256+4); //send everything plus cmd/addr
XSpi_SetSlaveSelect(&flashSPI,0);

send_data[0]=savemem[0];
send_data[1]=savemem[1];
send_data[2]=savemem[2];
send_data[3]=savemem[3];//save contents of memory
#endif

/* initialize the memory file system (MFS) image pre-loaded into memory */
mfs_init_fs(MFS_NUMBYTES, (char *)(MFS_BASE_ADDRESS+4), MFS_INIT_TYPE);
//	checking of file system exists
#ifdef DEBUG_OUTPUT
	mfs_ls();
#endif

	/* check if we can access index.html */
	if (mfs_exists_file("index.html") == 0) {
		xil_printf("%s: ERROR: unable to locate index.html in MFS\r\n", __FUNCTION__);
		xil_printf("One of your applications requires a Memory File System to be loaded.\r\n");
                xil_printf("Please check if MFS has been loaded, "
				"and it has index.html file in root directory\r\n");
	}

	return 0;
}
