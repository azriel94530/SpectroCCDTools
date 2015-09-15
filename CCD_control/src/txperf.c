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

#include <stdio.h>
#include <string.h>

#include "lwip/err.h"
#include "lwip/tcp.h"

static struct tcp_pcb *connected_pcb = NULL;

#define SEND_BUFSIZE (1400)
static char send_buf[SEND_BUFSIZE];

static unsigned txperf_client_connected = 0;

int
transfer_txperf_data()
{
	int copy = 1;
	err_t err;
	struct tcp_pcb *tpcb = connected_pcb;

	if (!connected_pcb)
		return ERR_OK;

	while (tcp_sndbuf(tpcb) > SEND_BUFSIZE) {
		err = tcp_write(tpcb, send_buf, SEND_BUFSIZE, copy);
		if (err != ERR_OK) {
			xil_printf("txperf: Error on tcp_write: %d\r\n", err);
                        connected_pcb = NULL;
			return -1;
		}
		tcp_output(tpcb);
	}

	return 0;
}

static err_t
txperf_sent_callback(void *arg, struct tcp_pcb *tpcb, u16_t len)
{
	return ERR_OK;
}

static err_t
txperf_connected_callback(void *arg, struct tcp_pcb *tpcb, err_t err)
{
	xil_printf("txperf: Connected to iperf server\r\n");
        txperf_client_connected = 1;

	/* store state */
	connected_pcb = tpcb;

	/* set callback values & functions */
	tcp_arg(tpcb, NULL);
	tcp_sent(tpcb, txperf_sent_callback);

	/* initiate data transfer */
	return ERR_OK;
}

int
start_txperf_application()
{
	struct tcp_pcb *pcb;
	struct ip_addr ipaddr;
	err_t err;
	u16_t port;
	int i;

	/* create new TCP PCB structure */
	pcb = tcp_new();
	if (!pcb) {
		xil_printf("txperf: Error creating PCB. Out of Memory\r\n");
		return -1;
	}

	/* connect to iperf server */
#if 0
	IP4_ADDR(&ipaddr,  192, 168,   0,  2);		/* iperf server address */
#else
	IP4_ADDR(&ipaddr,  131, 243,  51, 95);		/* iperf server address */
#endif
	port = 5001;					/* iperf default port */
	err = tcp_connect(pcb, &ipaddr, port, txperf_connected_callback);
        txperf_client_connected = 0;

	if (err != ERR_OK) {
		xil_printf("txperf: tcp_connect returned error: %d\r\n", err);
		return err;
	}

	/* initialize data buffer being sent */
	for (i = 0; i < SEND_BUFSIZE; i++)
		send_buf[i] = (i % 10) + '0';

	return 0;
}

void
print_txperf_app_header()
{
        xil_printf("%20s %6s %s\r\n", "txperf client",
                        "N/A",
                        "$ iperf -s -i 5 -t 100 (on host with IP 192.168.1.100)");
}
