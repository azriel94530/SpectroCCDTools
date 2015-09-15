/*
 * flashMFS.h
 *
 *  Created on: Jul 3, 2013
 *      Author: karcher
 */

#ifndef FLASHMFS_H_
#define FLASHMFS_H_

XSpi flashSPI;

#define MFS_FLASHADDRESS	0xf90000 //start of MFS in flash memory
#define MFSSIZE				1064 //number of 256 byte pages
#define MFSBLOCKS			5 //number of 64k blocks (rounded)


// SF One-byte Op-Codes for flash access
#define  WREN    0x06  // Write Enable
#define  WRDI    0x04  // Write Disable
#define  RDID    0x9F  // Read Identification
#define  RDSR    0x05  // Read Status Register
#define  WRSR    0x01  // Write Status Register
#define  READ    0x03  // Read Data Bytes
#define  FAST    0x0B  // Read Data Bytes at Higher Speed
#define  PP      0x02  // Page Program
#define  SE      0xD8  // Sector Erase
#define  BE      0xC7  // Bulk Erase
#define  DP      0xB9  // Deep Power-down
#define  RES     0xAB  // Read 8-bit Electronic Signature and/or Release from Deep power-down

#endif /* FLASHMFS_H_ */
