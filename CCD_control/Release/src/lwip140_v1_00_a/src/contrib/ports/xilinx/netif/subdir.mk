################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xadapter.c \
../src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xaxiemacif.c \
../src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xaxiemacif_dma.c \
../src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xaxiemacif_hw.c \
../src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xaxiemacif_physpeed.c \
../src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xpqueue.c \
../src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xtopology_g.c 

OBJS += \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xadapter.o \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xaxiemacif.o \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xaxiemacif_dma.o \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xaxiemacif_hw.o \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xaxiemacif_physpeed.o \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xpqueue.o \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xtopology_g.o 

C_DEPS += \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xadapter.d \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xaxiemacif.d \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xaxiemacif_dma.d \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xaxiemacif_hw.d \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xaxiemacif_physpeed.d \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xpqueue.d \
./src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/xtopology_g.d 


# Each subdirectory must supply rules for building sources it contributes
src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/%.o: ../src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/%.c
	@echo Building file: $<
	@echo Invoking: MicroBlaze gcc compiler
	mb-gcc -Wall -O3 -c -fmessage-length=0 -I../../ccd_bsp_1/microblaze_0/include -mlittle-endian -mxl-barrel-shift -mxl-pattern-compare -mcpu=v8.20.b -mno-xl-soft-mul -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o"$@" "$<"
	@echo Finished building: $<
	@echo ' '


