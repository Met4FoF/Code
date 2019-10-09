################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Middlewares/Third_Party/FatFs/src/diskio.c \
../Middlewares/Third_Party/FatFs/src/ff.c \
../Middlewares/Third_Party/FatFs/src/ff_gen_drv.c 

OBJS += \
./Middlewares/Third_Party/FatFs/src/diskio.o \
./Middlewares/Third_Party/FatFs/src/ff.o \
./Middlewares/Third_Party/FatFs/src/ff_gen_drv.o 

C_DEPS += \
./Middlewares/Third_Party/FatFs/src/diskio.d \
./Middlewares/Third_Party/FatFs/src/ff.d \
./Middlewares/Third_Party/FatFs/src/ff_gen_drv.d 


# Each subdirectory must supply rules for building sources it contributes
Middlewares/Third_Party/FatFs/src/%.o: ../Middlewares/Third_Party/FatFs/src/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: MCU GCC Compiler'
	@echo $(PWD)
	arm-none-eabi-gcc -mcpu=cortex-m7 -mthumb -mfloat-abi=hard -mfpu=fpv5-d16 '-D__weak=__attribute__((weak))' '-D__packed=__attribute__((__packed__))' -DUSE_HAL_DRIVER -DSTM32F767xx -I"../protobuff_deps" -I"../Middlewares/Third_Party/LwIP/src/include" -I"../Middlewares/Third_Party/LwIP/system" -I"../Drivers/STM32F7xx_HAL_Driver/Inc" -I"../Drivers/STM32F7xx_HAL_Driver/Inc/Legacy" -I"../Middlewares/Third_Party/FatFs/src" -I"../Middlewares/Third_Party/FreeRTOS/Source/include" -I"../Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS" -I"../Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM7/r0p1" -I"../Middlewares/Third_Party/LwIP/src/include/netif/ppp" -I"../Drivers/CMSIS/Device/ST/STM32F7xx/Include" -I"../Middlewares/Third_Party/LwIP/src/include/lwip" -I"../Middlewares/Third_Party/LwIP/src/include/lwip/apps" -I"../Middlewares/Third_Party/LwIP/src/include/lwip/priv" -I"../Middlewares/Third_Party/LwIP/src/include/lwip/prot" -I"../Middlewares/Third_Party/LwIP/src/include/netif" -I"../Middlewares/Third_Party/LwIP/src/include/posix" -I"../Middlewares/Third_Party/LwIP/src/include/posix/sys" -I"../Middlewares/Third_Party/LwIP/system/arch" -I"../Drivers/CMSIS/Include" -I"../Inc"  -Og -g3 -Wall -fmessage-length=0 -ffunction-sections -c -fmessage-length=0 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


