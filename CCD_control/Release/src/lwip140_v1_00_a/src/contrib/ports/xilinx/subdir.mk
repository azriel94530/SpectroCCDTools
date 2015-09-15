################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../src/lwip140_v1_00_a/src/contrib/ports/xilinx/sys_arch_raw.c 

OBJS += \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/sys_arch_raw.o 

C_DEPS += \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/sys_arch_raw.d 


# Each subdirectory must supply rules for building sources it contributes
src/lwip140_v1_00_a/src/contrib/ports/xilinx/%.o: ../src/lwip140_v1_00_a/src/contrib/ports/xilinx/%.c
	@echo Building file: $<
	@echo Invoking: MicroBlaze gcc compiler
	mb-gcc -Wall -O3 -c -fmessage-length=0 -I../../ccd_bsp_1/microblaze_0/include -mlittle-endian -mxl-barrel-shift -mxl-pattern-compare -mcpu=v8.20.b -mno-xl-soft-mul -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o"$@" "$<"
	@echo Finished building: $<
	@echo ' '


