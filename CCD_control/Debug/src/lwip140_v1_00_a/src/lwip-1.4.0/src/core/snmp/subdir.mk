################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/asn1_dec.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/asn1_enc.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/mib2.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/mib_structs.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/msg_in.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/msg_out.c 

OBJS += \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/asn1_dec.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/asn1_enc.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/mib2.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/mib_structs.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/msg_in.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/msg_out.o 

C_DEPS += \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/asn1_dec.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/asn1_enc.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/mib2.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/mib_structs.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/msg_in.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/msg_out.d 


# Each subdirectory must supply rules for building sources it contributes
src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/%.o: ../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/%.c
	@echo Building file: $<
	@echo Invoking: MicroBlaze gcc compiler
	mb-gcc -Wall -O0 -g3 -I"U:\PC_boards\CCD_READOUT\Firmware_C\CCD_control\src\lwip140_v1_00_a\src\lwip-1.4.0\src\include" -I"U:\PC_boards\CCD_READOUT\Firmware_C\CCD_control\src\lwip140_v1_00_a\src\contrib\ports\xilinx\include" -c -fmessage-length=0 -I../../ccd_bsp_1/microblaze_0/include -mlittle-endian -mxl-barrel-shift -mxl-pattern-compare -mcpu=v8.20.b -mno-xl-soft-mul -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o"$@" "$<"
	@echo Finished building: $<
	@echo ' '


