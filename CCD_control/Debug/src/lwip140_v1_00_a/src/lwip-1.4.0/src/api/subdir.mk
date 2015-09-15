################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/api_lib.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/api_msg.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/err.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/netbuf.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/netdb.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/netifapi.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/sockets.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/tcpip.c 

OBJS += \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/api_lib.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/api_msg.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/err.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/netbuf.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/netdb.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/netifapi.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/sockets.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/tcpip.o 

C_DEPS += \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/api_lib.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/api_msg.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/err.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/netbuf.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/netdb.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/netifapi.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/sockets.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/tcpip.d 


# Each subdirectory must supply rules for building sources it contributes
src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/%.o: ../src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/%.c
	@echo Building file: $<
	@echo Invoking: MicroBlaze gcc compiler
	mb-gcc -Wall -O0 -g3 -I"U:\PC_boards\CCD_READOUT\Firmware_C\CCD_control\src\lwip140_v1_00_a\src\lwip-1.4.0\src\include" -I"U:\PC_boards\CCD_READOUT\Firmware_C\CCD_control\src\lwip140_v1_00_a\src\contrib\ports\xilinx\include" -c -fmessage-length=0 -I../../ccd_bsp_1/microblaze_0/include -mlittle-endian -mxl-barrel-shift -mxl-pattern-compare -mcpu=v8.20.b -mno-xl-soft-mul -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o"$@" "$<"
	@echo Finished building: $<
	@echo ' '


