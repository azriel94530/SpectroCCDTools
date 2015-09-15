################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-include ../makefile.init

RM := rm -rf

# All of the sources participating in the build are defined here
-include sources.mk
-include subdir.mk
-include src/subdir.mk
-include src/lwip140_v1_00_a/src/obj/subdir.mk
-include src/lwip140_v1_00_a/src/lwip-1.4.0/src/netif/subdir.mk
-include src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/subdir.mk
-include src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/snmp/subdir.mk
-include src/lwip140_v1_00_a/src/lwip-1.4.0/src/core/ipv4/subdir.mk
-include src/lwip140_v1_00_a/src/lwip-1.4.0/src/api/subdir.mk
-include src/lwip140_v1_00_a/src/contrib/ports/xilinx/subdir.mk
-include src/lwip140_v1_00_a/src/contrib/ports/xilinx/netif/subdir.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
ifneq ($(strip $(S_UPPER_DEPS)),)
-include $(S_UPPER_DEPS)
endif
endif

-include ../makefile.defs

# Add inputs and outputs from these tool invocations to the build variables 
ELFSIZE += \
CCD_readout_web.elf.size \

ELFCHECK += \
CCD_readout_web.elf.elfcheck \


# All Target
all: CCD_readout_web.elf secondary-outputs

# Tool invocations
CCD_readout_web.elf: $(OBJS) ../src/lscript.ld $(USER_OBJS)
	@echo Building target: $@
	@echo Invoking: MicroBlaze gcc linker
	mb-gcc -Wl,-T -Wl,../src/lscript.ld -L../../ccd_bsp_1/microblaze_0/lib -mlittle-endian -mxl-barrel-shift -mxl-pattern-compare -mcpu=v8.20.b -mno-xl-soft-mul -o"CCD_readout_web.elf" $(OBJS) $(USER_OBJS) $(LIBS)
	@echo Finished building target: $@
	@echo ' '

CCD_readout_web.elf.size: CCD_readout_web.elf
	@echo Invoking: MicroBlaze Print Size
	mb-size CCD_readout_web.elf  |tee "CCD_readout_web.elf.size"
	@echo Finished building: $@
	@echo ' '

CCD_readout_web.elf.elfcheck: CCD_readout_web.elf
	@echo Invoking: Xilinx ELF Check
	elfcheck CCD_readout_web.elf -hw ../../xps_hw_platform/system.xml -pe microblaze_0  |tee "CCD_readout_web.elf.elfcheck"
	@echo Finished building: $@
	@echo ' '

# Other Targets
clean:
	-$(RM) $(OBJS)$(C_DEPS)$(EXECUTABLES)$(ELFSIZE)$(ELFCHECK)$(S_UPPER_DEPS) CCD_readout_web.elf
	-@echo ' '

secondary-outputs: $(ELFSIZE) $(ELFCHECK)

.PHONY: all clean dependents
.SECONDARY:

-include ../makefile.targets
