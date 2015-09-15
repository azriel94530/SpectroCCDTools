################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/autoip.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/icmp.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/igmp.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/inet.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/inet_chksum.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/ip.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/ip_addr.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/ip_frag.c 

OBJS += \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/autoip.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/icmp.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/igmp.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/inet.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/inet_chksum.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/ip.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/ip_addr.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/ip_frag.o 

C_DEPS += \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/autoip.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/icmp.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/igmp.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/inet.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/inet_chksum.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/ip.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/ip_addr.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/ip_frag.d 


# Each subdirectory must supply rules for building sources it contributes
src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/%.o: ../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/%.c
	@echo Building file: $<
	@echo Invoking: MicroBlaze gcc compiler
	mb-gcc -Wall -O0 -g3 -I"U:\PC_boards\CCD_READOUT\Firmware_C\CCD_control\src\lwip140_v1_00_a\src\lwip-1.4.0\src\include" -I"U:\PC_boards\CCD_READOUT\Firmware_C\CCD_control\src\lwip140_v1_00_a\src\contrib\ports\xilinx\include" -c -fmessage-length=0 -I../../ccd_bsp_1/microblaze_0/include -mlittle-endian -mxl-barrel-shift -mxl-pattern-compare -mcpu=v8.20.b -mno-xl-soft-mul -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o"$@" "$<"
	@echo Finished building: $<
	@echo ' '


