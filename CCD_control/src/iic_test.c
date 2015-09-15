/**************************************************************
 *  Project          : Mars EDK reference design
 *  File description : I2C Test
 *  File name        : iic_test.c
 *  Author           : Christoph Glattfelder
 **************************************************************
 *  Copyright (c) 2011 by Enclustra GmbH, Switzerland
 *  All rights reserved.
 **************************************************************
 *  Notes:
 *
 **************************************************************
 *  File history:
 *
 *  Version | Date     | Author             | Remarks
 *  -----------------------------------------------------------
 *  1.0	    | 18.03.11 | Ch. Glattfelder    | Created
 *          |          |                    |
 *  ------------------------------------------------------------
 *
 **************************************************************/

#include "xparameters.h"
#include "xiic.h"
#include "xintc.h"
#include "mb_interface.h"
#include "MarsI2C.h"
#include "xutil.h"
#include "stdio.h"


#define IIC_DEVICE_ID               XPAR_IIC_0_DEVICE_ID
#define INTC_DEVICE_ID              XPAR_INTC_0_DEVICE_ID
#define IIC_INTR_ID                 XPAR_INTC_0_IIC_0_VEC_ID

#define SEND_COUNT      8
#define RECEIVE_COUNT   8

extern int Ddr2Size;
extern int FlashSize;

static int SetupInterruptSystem(XIic * IicInstPtr);
void Sleep(int value);

XIntc InterruptController;

static u32 ConvU32(u8* Array){
	u32 Value = (*Array << 24);
	Value += (*(Array+1) << 16);
	Value += (*(Array+2) << 8);
	Value +=  *(Array+3);
	return Value;
}

/*****************************************************************************/
/**
* Main function
*
******************************************************************************/
int iic_test(int ModInfo, int CM, int RTC)
{
	int Status, i;
	int Errors=0;
	u16 ReadData = 0;
	int Temp = 0;
	int Hour, Min, Sec;
	int Year, Month, Day;
	u8 ReadBuffer[4];
	u32 SerialNo;
	u32 ProdNo;
	u32 ModConf;
	u8 MacAddr[6];

	microblaze_enable_icache();
	microblaze_enable_dcache();

	xil_printf("\n\r\n-- Mars I2C Test --\r\n\r\n");


	// Initialize the IIC Instance.
	Status = XIic_Initialize(&IicInstance, IIC_DEVICE_ID);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}

	// Setup the Interrupt System.
	Status = SetupInterruptSystem(&IicInstance);
	if (Status != XST_SUCCESS) {
		xil_printf("Error opening Interrupt-Controller!\n\n");
		return XST_FAILURE;
	}

	// Set the Transmit and Receive handlers
	XIic_SetSendHandler(&IicInstance, &IicInstance,
			    (XIic_Handler) SendHandler);
	XIic_SetRecvHandler(&IicInstance, &IicInstance,
			    (XIic_Handler) ReceiveHandler);
	XIic_SetStatusHandler(&IicInstance, &IicInstance,
				  (XIic_StatusHandler) StatusHandler);

	if(ModInfo){
		Status += EEPROM_init(EEPROM_ADDR);
		if (Status != XST_SUCCESS) {
			xil_printf("Error opening EEPROM!\n\n");
			return XST_FAILURE;
		}
		int Ddr2Size,FlashSize;
		Status = EEPROM_read(0, 4, (u8*)&ReadBuffer);
		SerialNo = ConvU32(ReadBuffer);
		Status += EEPROM_read(4, 4, (u8*)&ReadBuffer);
		ProdNo = ConvU32(ReadBuffer);
		Status += EEPROM_read(8, 4, (u8*)&ReadBuffer);
		ModConf = ConvU32(ReadBuffer);
		Status += EEPROM_read(0x10, 6, (u8*)&MacAddr);
		if (Status != XST_SUCCESS) return XST_FAILURE;
		if ((ProdNo >> 16) == 0x320)
			xil_printf("Module Type: Mars MX1 Rev %d\r\n", ProdNo & 0xff);
		else if ((ProdNo >> 16) == 0x321)
			xil_printf("Module Type: Mars MX2 Rev %d\r\n", ProdNo & 0xff);
		else xil_printf("Unknown Module\r\n");
		xil_printf("SerialNo = 0x%x\r\n", SerialNo);
		//xil_printf("Module Config = 0x%x\r\n", ModConf);
		Ddr2Size = 8*(0x1 << (((ModConf >> 4) & 0xf)-1));
		FlashSize = (0x1 << ((ModConf & 0xf)-1));
		xil_printf("DDR2 memory: %dMB\r\n", Ddr2Size);
		xil_printf("Flash memory: %dMB\r\n", FlashSize);
		xil_printf("MAC0 Addr: %X:%X:%X:%X:%X:%X\r\n", MacAddr[0], MacAddr[1],
				MacAddr[2], MacAddr[3], MacAddr[4], MacAddr[5]);
		if (((ProdNo >> 16) == 0x320) && MacAddr[5] < 0xff){
			xil_printf("MAC1 Addr: %X:%X:%X:%X:%X:%X\r\n", MacAddr[0], MacAddr[1],
					MacAddr[2], MacAddr[3], MacAddr[4], MacAddr[5]+1);
		} else if ((ProdNo >> 16) == 0x320){
			xil_printf("MAC1 Addr: %X:%X:%X:%X:%X:%X\r\n", MacAddr[0], MacAddr[1],
					MacAddr[2], MacAddr[3], MacAddr[4]+1, 0);
		}
		xil_printf("\r\n");
	}

	if (CM){
		// Read and display values from the current monitor
		xil_printf("Current Monitor:\r\n");
		CurrSenseInit(CURRSENS_STARTER);
		Status = CurrSenseWriteConfig(0x019F);
		if (Status != XST_SUCCESS){
			xil_printf("Error accessing current monitor!\r\n");
			Errors++;
		}
		Status = CurrSenseWriteCalib (0xC800);
		if (Status != XST_SUCCESS){
			xil_printf("Error accessing current monitor!\r\n");
			Errors++;
		}

		Status += CurrSenseReadVBus(&ReadData);
		xil_printf("  V-Bus=%d mV\r\n", ReadData);

		Status += CurrSenseReadCurrent(&ReadData);
		xil_printf("  Current=%d mA\r\n", ReadData);

		Status += CurrSenseReadPower(&ReadData);
		xil_printf("  Power=%d mW\r\n\r\n", ReadData);
		if (Status != XST_SUCCESS){
			xil_printf("Error accessing current monitor!\r\n");
			Errors++;
		}
	}

	if (RTC){
		xil_printf("Real time clock:\r\n");
		Status = RTC_init();
		if (Status != XST_SUCCESS){
			xil_printf("Error initializing RTC!\r\n");
			Errors++;
		}
		Status += RTC_setTime(11, 22, 33);
		Status += RTC_setDate(22, 11, 10);
		Status += RTC_readTime((int*)&Hour, (int*)&Min, (int*)&Sec);
		Status += RTC_readDate((int*)&Day, (int*)&Month, (int*)&Year);
		xil_printf("  Time %d:%d:%d\r\n", Hour, Min, Sec);
		xil_printf("  Date %d.%d.%d\r\n", Day, Month, Year);
		if (Hour!=11 || Min !=22 || Sec!=33 || Day!=22 || Month!=11 || Year != 10)
			Errors++;
		Status += RTC_readTime((int*)&Hour, (int*)&Min, (int*)&Sec);
		xil_printf("  Time %d:%d:%d\r\n", Hour, Min, Sec);
		Status += RTC_readTemp((int*)&Temp);
		xil_printf("  Temp %d Celsius\r\n", Temp);
		if (Status != XST_SUCCESS){
			xil_printf("Error accessing RTC!\r\n");
			Errors++;
		}
	}

	xil_printf("\n\r-- Mars I2C Test Complete --\n\r");

	Status = GpioSetLed(0x0);
	if (Status != XST_SUCCESS)
		xil_printf("Error writing to IO device!\r\n");

	if (Errors)
		return XST_FAILURE;
	else
		return XST_SUCCESS;
}



/*****************************************************************************/
/**
* This function setups the interrupt system so interrupts can occur for the
* IIC. The function is application-specific since the actual system may or
* may not have an interrupt controller. The IIC device could be directly
* connected to a processor without an interrupt controller. The user should
* modify this function to fit the application.
*
* @param	IicInstPtr contains a pointer to the instance of the IIC  which
*		is going to be connected to the interrupt controller.
*
* @return	XST_SUCCESS if successful else XST_FAILURE.
*
* @note		None.
*
******************************************************************************/
static int SetupInterruptSystem(XIic * IicInstPtr)
{
	int Status;

	if (InterruptController.IsStarted == XCOMPONENT_IS_STARTED) {
		return XST_SUCCESS;
	}

	/*
	 * Initialize the interrupt controller driver so that it's ready to use.
	 */
	Status = XIntc_Initialize(&InterruptController, INTC_DEVICE_ID);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}

	/*
	 * Connect the device driver handler that will be called when an
	 * interrupt for the device occurs, the handler defined above performs
	 *  the specific interrupt processing for the device.
	 */
	Status = XIntc_Connect(&InterruptController, IIC_INTR_ID,
			       (XInterruptHandler) XIic_InterruptHandler,
			       IicInstPtr);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}

	/*
	 * Start the interrupt controller so interrupts are enabled for all
	 * devices that cause interrupts.
	 */
	Status = XIntc_Start(&InterruptController, XIN_REAL_MODE);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}

	/*
	 * Enable the interrupts for the IIC device.
	 */
	XIntc_Enable(&InterruptController, IIC_INTR_ID);

#ifdef __PPC__
	/*
	 * Initialize the PPC exception table.
	 */
	XExc_Init();

	/*
	 * Register the interrupt controller handler with the exception table.
	 */
	XExc_RegisterHandler(XEXC_ID_NON_CRITICAL_INT,
			     (XExceptionHandler) XIntc_InterruptHandler,
			     &InterruptController);

	/*
	 * Enable non-critical exceptions.
	 */
	XExc_mEnableExceptions(XEXC_NON_CRITICAL);
#endif

#ifdef __MICROBLAZE__
	/*
	 * Enable the Microblaze Interrupts.
	 */
	microblaze_enable_interrupts();
#endif

	return XST_SUCCESS;
}


