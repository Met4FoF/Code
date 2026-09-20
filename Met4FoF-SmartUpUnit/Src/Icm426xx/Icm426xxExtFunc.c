/*
 * Icm426xxExtFunc.c
 *
 *  Created on: Jul 9, 2024
 *      Author: seeger01
 */

#include "Icm426xx/Icm426xxExtFunc.h"


/** @brief Hook for low-level high res system sleep() function to be implemented by upper layer
 *  ~100us resolution is sufficient
 *  @param[in] us number of us the calling thread should sleep
 */
void inv_icm426xx_sleep_us(uint32_t us) {
    if (us >= 1000) {
        // Delay for whole milliseconds using vTaskDelay
        TickType_t ticks = us / 1000 / portTICK_PERIOD_MS;
        if (ticks > 0) {
            vTaskDelay(ticks);
        }
    }

    // Calculate the remaining microseconds
    uint32_t remainder_us = us % 1000;

    // Use a busy wait loop for sub-millisecond delay
    uint32_t start_tick = HAL_GetTick();
    while ((HAL_GetTick() - start_tick) < (remainder_us / 1000.0f));
}

/** @brief Hook for low-level high res system get_time() function to be implemented by upper layer
 *  Timer should be on 64bit with a 1 us resolution
 *  @return The current time in us
 */
uint64_t inv_icm426xx_get_time_us(void) {
    // Get the current tick count
    TickType_t ticks = xTaskGetTickCount();

    // Convert ticks to microseconds
    // configTICK_RATE_HZ is the FreeRTOS tick rate in Hz
    uint64_t time_us = (uint64_t)ticks * 1000000 / configTICK_RATE_HZ;

    return time_us;
}
