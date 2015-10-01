################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../src/MarsI2C.c \
../src/commands.c \
../src/dispatch.c \
../src/echo.c \
../src/http_response.c \
../src/main.c \
../src/platform.c \
../src/platform_fs.c \
../src/platform_gpio.c \
../src/prot_malloc.c \
../src/rxperf.c \
../src/tftpserver.c \
../src/tftputils.c \
../src/txperf.c \
../src/urxperf.c \
../src/utxperf.c \
../src/web_utils.c \
../src/webserver.c 

LD_SRCS += \
../src/lscript.ld 

OBJS += \
./src/MarsI2C.o \
./src/commands.o \
./src/dispatch.o \
./src/echo.o \
./src/http_response.o \
./src/main.o \
./src/platform.o \
./src/platform_fs.o \
./src/platform_gpio.o \
./src/prot_malloc.o \
./src/rxperf.o \
./src/tftpserver.o \
./src/tftputils.o \
./src/txperf.o \
./src/urxperf.o \
./src/utxperf.o \
./src/web_utils.o \
./src/webserver.o 

C_DEPS += \
./src/MarsI2C.d \
./src/commands.d \
./src/dispatch.d \
./src/echo.d \
./src/http_response.d \
./src/main.d \
./src/platform.d \
./src/platform_fs.d \
./src/platform_gpio.d \
./src/prot_malloc.d \
./src/rxperf.d \
./src/tftpserver.d \
./src/tftputils.d \
./src/txperf.d \
./src/urxperf.d \
./src/utxperf.d \
./src/web_utils.d \
./src/webserver.d 


# Each subdirectory must supply rules for building sources it contributes
src/%.o: ../src/%.c
	@echo Building file: $<
	@echo Invoking: MicroBlaze gcc compiler
	mb-gcc -Wall -O0 -g3 -I"U:\PC_boards\CCD_READOUT\Firmware_C\CCD_control\src\lwip140_v1_00_a\src\lwip-1.4.0\src\include" -I"U:\PC_boards\CCD_READOUT\Firmware_C\CCD_control\src\lwip140_v1_00_a\src\contrib\ports\xilinx\include" -c -fmessage-length=0 -I../../ccd_bsp_1/microblaze_0/include -mlittle-endian -mxl-barrel-shift -mxl-pattern-compare -mcpu=v8.20.b -mno-xl-soft-mul -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o"$@" "$<"
	@echo Finished building: $<
	@echo ' '

