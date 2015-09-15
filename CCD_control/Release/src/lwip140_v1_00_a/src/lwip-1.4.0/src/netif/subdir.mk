################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/netif/etharp.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/netif/ethernetif.c 

OBJS += \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/netif/etharp.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/netif/ethernetif.o 

C_DEPS += \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/netif/etharp.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/netif/ethernetif.d 


# Each subdirectory must supply rules for building sources it contributes
src/lwip140_v1_00_a/src/lwip-1.4.0/src/netif/%.o: ../src/lwip140_v1_00_a/src/lwip-1.4.0/src/netif/%.c
	@echo Building file: $<
	@echo Invoking: MicroBlaze gcc compiler
	mb-gcc -Wall -O3 -c -fmessage-length=0 -I../../ccd_bsp_1/microblaze_0/include -mlittle-endian -mxl-barrel-shift -mxl-pattern-compare -mcpu=v8.20.b -mno-xl-soft-mul -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o"$@" "$<"
	@echo Finished building: $<
	@echo ' '


