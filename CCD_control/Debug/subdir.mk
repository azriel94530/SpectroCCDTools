################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../flashtest.c 

OBJS += \
./flashtest.o 

C_DEPS += \
./flashtest.d 


# Each subdirectory must supply rules for building sources it contributes
%.o: ../%.c
	@echo Building file: $<
	@echo Invoking: MicroBlaze gcc compiler
	mb-gcc -Wall -O0 -g3 -I"C:\project\xps\SDK\SDK_Export\CCD_readout_web\src\lwip140_v1_00_a\src\lwip-1.4.0\src\include" -I"C:\project\xps\SDK\SDK_Export\CCD_readout_web\src\lwip140_v1_00_a\src\contrib\ports\xilinx\include" -c -fmessage-length=0 -I../../ccd_bsp_1/microblaze_0/include -mlittle-endian -mxl-barrel-shift -mxl-pattern-compare -mcpu=v8.20.b -mno-xl-soft-mul -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o"$@" "$<"
	@echo Finished building: $<
	@echo ' '


