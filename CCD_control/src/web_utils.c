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

#include "lwip/sys.h"
#include "config_apps.h"
#include "mfs_config.h"
#include "webserver.h"
#include "platform_fs.h"
#include "platform_gpio.h"
#include "stdio.h"

void print_http_request(char *buf, int n)
{
	int i;
#ifdef DEBUG_OUTPUT
	xil_printf("print_http_request(%s)\n\r",buf);
#endif

	printf("%s\r\n", buf);
}


void extract_file_name(char *filename, char *req, int rlen, int maxlen)
{
	char *fstart, *fend;
	/* first locate the file name in the request */
	/* requests are of the form GET /path/to/filename HTTP... */

	req += strlen("GET ");

	if (*req == '/')
		req++;

	fstart = req;	/* start marker */

	while (*req != ' ')	/* file name finally ends in a space */
		req++;

	fend = req-1;	/* end marker */

	if (fend < fstart) {
		strcpy(filename, "index.html");
		return;
	}

	/* make sure filename is of reasonable size */
	if (fend - fstart > maxlen) {
		*fend = 0;
		strcpy(filename, "404.html");
		printf("Request filename is too long, length = %d, file = %s (truncated), max = %d\r\n",
				(fend - fstart), fstart, maxlen);
		return;
	}

	/* copy over the filename */
	strncpy(filename, fstart, fend-fstart+1);
	filename[fend-fstart+1] = 0;

	/* if last character is a '/', append index.html */
	if (*fend == '/')
		strcat(filename, "index.html");
}

char *get_file_extension(char *fname)
{
#ifdef DEBUG_OUTPUT
xil_printf("get_file_extension()\n\r");
#endif
	char *fext = fname + strlen(fname) - 1;

	while (fext > fname) {
		if (*fext == '.'){
			return fext + 1;
		}
		fext--;
	}

	return NULL;
}

int generate_http_header(char *buf, char *fext, int fsize)
{
#ifdef DEBUG_OUTPUT
	xil_printf("generate_http_header()\n\r");
#endif
	char lbuf[40];

	strcpy(buf, "HTTP/1.1 200 OK\r\nContent-Type: ");

	if (fext == NULL)
		strcat(buf, "text/html");	/* for unknown types */
	else if (!strncmp(fext, "htm", 3))
		strcat(buf, "text/html");	/* html */
	else if (!strncmp(fext, "jpg", 3))
		strcat(buf, "image/jpeg");
	else if (!strncmp(fext, "gif", 3))
		strcat(buf, "image/gif");
	else if (!strncmp(fext, "json", 4))
		strcat(buf, "application/json");
	else if (!strncmp(fext, "js", 2))
		strcat(buf, "application/javascript");
	else if (!strncmp(fext, "pdf", 2))
		strcat(buf, "application/pdf");
	else if (!strncmp(fext, "css", 2))
		strcat(buf, "text/css");
	else if (!strncmp(fext, "fits", 2))
		strcat(buf, "application/fits");
	else
		strcat(buf, "text/plain");	/* for unknown types */
	strcat(buf, "\r\n");

	sprintf(lbuf, "Content-length: %d", fsize);
	strcat(buf, lbuf);
	strcat(buf, "\r\n");

	strcat(buf, "Connection: close\r\n");
	strcat(buf, "\r\n");

	return strlen(buf)+fsize;
}

static int p_arg_count = 0;

http_arg *palloc_arg()
{
	http_arg *a;
	SYS_ARCH_DECL_PROTECT(lev);
	SYS_ARCH_PROTECT(lev);

	a = malloc(sizeof *a);
	if (!a) {
		print("out of memory, attempted to allocate a http argument structure\r\n");
	} else {
		a->count = p_arg_count++;
		a->fd = -1;
		a->fsize = 0;
	}

	SYS_ARCH_UNPROTECT(lev);

	return a;
}

void pfree_arg(http_arg *arg)
{
	SYS_ARCH_DECL_PROTECT(lev);
	SYS_ARCH_PROTECT(lev);
	free(arg);
	SYS_ARCH_UNPROTECT(lev);
}
