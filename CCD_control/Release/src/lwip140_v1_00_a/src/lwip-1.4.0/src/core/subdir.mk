################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/def.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/dhcp.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/dns.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/init.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/mem.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/memp.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/netif.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/pbuf.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/raw.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/stats.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/sys.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/tcp.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/tcp_in.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/tcp_out.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/timers.c \
../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/udp.c 

OBJS += \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/def.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/dhcp.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/dns.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/init.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/mem.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/memp.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/netif.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/pbuf.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/raw.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/stats.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/sys.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/tcp.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/tcp_in.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/tcp_out.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/timers.o \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/udp.o 

C_DEPS += \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/def.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/dhcp.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/dns.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/init.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/mem.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/memp.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/netif.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/pbuf.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/raw.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/stats.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/sys.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/tcp.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/tcp_in.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/tcp_out.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/timers.d \
./src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/udp.d 


# Each subdirectory must supply rules for building sources it contributes
src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/%.o: ../src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/%.c
	@echo Building file: $<
	@echo Invoking: MicroBlaze gcc compiler
	mb-gcc -Wall -O3 -c -fmessage-length=0 -I../../ccd_bsp_1/microblaze_0/include -mlittle-endian -mxl-barrel-shift -mxl-pattern-compare -mcpu=v8.20.b -mno-xl-soft-mul -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o"$@" "$<"
	@echo Finished building: $<
	@echo ' '


