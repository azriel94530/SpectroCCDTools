/*
 * Copyright (c) 2007 Xilinx, Inc.  All rights reserved.
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

#ifdef CONFIG_LINKSPEED_AUTODETECT
#undef CONFIG_LINKSPEED_AUTODETECT
#endif
#define CONFIG_LINKSPEED1000
#include <stdio.h>

#include "xaxiethernet.h"
#include "xparameters.h"
#include "config_apps.h"
#include "netif/xadapter.h"
#include "commands.h"

#include "lwip/init.h"
#include "MarsI2C.h"

#include "platform.h"
#include "platform_config.h"
//#include "globals.h"

void print_headers();
int start_applications();
int transfer_data();



void
print_ip(char *msg, struct ip_addr *ip)
{
    print(msg);
    xil_printf("%d.%d.%d.%d\r\n", ip4_addr1(ip), ip4_addr2(ip),
			ip4_addr3(ip), ip4_addr4(ip));
}

void
print_ip_settings(struct ip_addr *ip, struct ip_addr *mask, struct ip_addr *gw)
{
    print_ip("Board IP:       ", ip);
    print_ip("Netmask :       ", mask);
    print_ip("Gateway :       ", gw);
}
static u32 ConvU32(u8* Array){
	u32 Value = (*Array << 24);
	Value += (*(Array+1) << 16);
	Value += (*(Array+2) << 8);
	Value +=  *(Array+3);
	return Value;
}
int main()
{
	struct netif *netif, server_netif;
	struct ip_addr ipaddr, netmask, gw;

	u8 ReadBuffer[4];
	u32 SerialNo;
	u32 ProdNo;
	u32 ModConf;
	u8 mac_ethernet_address[6];
	initSpi();

	if (init_platform() < 0) {
        xil_printf("ERROR initializing platform.\r\n");
        return -1;
    }
	/* now enable interrupts, needed for IIC */
	platform_enable_interrupts();
	//read stuff from EEPROM, such as MAC
	EEPROM_read(0, 4, (u8*)&ReadBuffer);
	SerialNo = ConvU32(ReadBuffer);
	EEPROM_read(4, 4, (u8*)&ReadBuffer);
	ProdNo = ConvU32(ReadBuffer);
	EEPROM_read(8, 4, (u8*)&ReadBuffer);
	ModConf = ConvU32(ReadBuffer);
	EEPROM_read(0x10, 6, (u8*)&mac_ethernet_address);
	Xil_ExceptionDisable();
	/* the mac address of the board. this should be unique per board */
	//unsigned char mac_ethernet_address[] = { 0x00, 0x0a, 0x35, 0x00, 0x01, 0x02 };
    xil_printf("MAC: %x.%x.%x.%x.%x.%x\r\n",mac_ethernet_address[0],mac_ethernet_address[1],mac_ethernet_address[2],mac_ethernet_address[3],mac_ethernet_address[4],mac_ethernet_address[5]);
    xil_printf("Module ser#%x, prod#%x, conf#%x\r\n",SerialNo,ProdNo,ModConf);

	netif = &server_netif;

	/* initliaze IP addresses to be used */
#if (LWIP_DHCP==0)

	/* initliaze IP addresses to be used */
#if 1
	IP4_ADDR(&ipaddr,  169, 254,  207, 10);
	IP4_ADDR(&netmask, 255, 255, 255,  0);
	IP4_ADDR(&gw,      169, 254,  207, 225);
#else
	IP4_ADDR(&ipaddr,  131, 243,  49,120);
	IP4_ADDR(&netmask, 255, 255, 252,  0);
	IP4_ADDR(&gw,      131, 243,  48,  1);
#endif
    print_ip_settings(&ipaddr, &netmask, &gw);
#endif
	lwip_init();

#if (LWIP_DHCP==1)
	ipaddr.addr = 0;
	gw.addr = 0;
	netmask.addr = 0;
#endif

	/* Add network interface to the netif_list, and set it as default */
	if (!xemac_add(netif, &ipaddr, &netmask, &gw, mac_ethernet_address, PLATFORM_EMAC_BASEADDR)) {
		xil_printf("Error adding N/W interface\r\n");
		return -1;
	}
	netif_set_default(netif);

	/* specify that the network if is up */
	netif_set_up(netif);

	/* now enable interrupts */
	platform_enable_interrupts();

#if (LWIP_DHCP==1)
	/* Create a new DHCP client for this interface.
	 * Note: you must call dhcp_fine_tmr() and dhcp_coarse_tmr() at
	 * the predefined regular intervals after starting the client.
	 */
	dhcp_start(netif);
	dhcp_timoutcntr = 24;
	TxPerfConnMonCntr = 0;
	while(((netif->ip_addr.addr) == 0) && (dhcp_timoutcntr > 0)) {
		xemacif_input(netif);
		if (TcpFastTmrFlag) {
			tcp_fasttmr();
			TcpFastTmrFlag = 0;
		}
		if (TcpSlowTmrFlag) {
			tcp_slowtmr();
			TcpSlowTmrFlag = 0;
		}
	}
	if (dhcp_timoutcntr <= 0) {
		if ((netif->ip_addr.addr) == 0) {
			xil_printf("DHCP Timeout\r\n");
			xil_printf("Configuring default IP of 192.168.1.10\r\n");
			IP4_ADDR(&(netif->ip_addr),  192, 168,   1, 10);
			IP4_ADDR(&(netif->netmask), 255, 255, 255,  0);
			IP4_ADDR(&(netif->gw),      192, 168,   1,  1);
		}
	}
	/* receive and process packets */
	print_ip_settings(&(netif->ip_addr), &(netif->netmask), &(netif->gw));
#endif
//	XAxiEthernet_PhyWrite(AxiEthernetInstancePtr, 1, 0xC, 0xF7F7);
//	XAxiEthernet_PhyWrite(AxiEthernetInstancePtr, 1, 0xB, 0x8104);


	/* start the application (web server, rxtest, txtest, etc..) */
	start_applications();
	print_headers();
	cmdBiasDacInit();

	/* receive and process packets */
	while (1) {
//		Xil_Out32(XPAR_LEDS_BASEADDR,Xil_In32(XPAR_CCD_STATE_0_BASEADDR));
//		if (TcpFastTmrFlag) {
//			tcp_fasttmr();
//			TcpFastTmrFlag = 0;
//		}
//		if (TcpSlowTmrFlag) {
//			tcp_slowtmr();
//			TcpSlowTmrFlag = 0;
//		}
		xemacif_input(netif);
		transfer_data();
		pollBufferState(netif);
	}

        /* never reached */
    cleanup_platform();

	return 0;
}
