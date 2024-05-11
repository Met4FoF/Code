#ifndef ADNS3080_HPP
#define ADNS3080_HPP

#include "Met4FoFSensor.h"
#include "spi.h"
#include <math.h>
#include <cstdint> // For standard uint types

namespace Met4FoFSensors {

// Define register addresses and bit fields
namespace ADNS3080RegisterMap {
    const uint8_t Product_ID = 0x00;
    const uint8_t Revision_ID = 0x01;
    const uint8_t Motion = 0x02;
    const uint8_t Delta_X = 0x03;
    const uint8_t Delta_Y = 0x04;
    const uint8_t SQUAL = 0x05;
    const uint8_t Pixel_Sum = 0x06;
    const uint8_t Maximum_Pixel = 0x07;
    const uint8_t Configuration_Bits = 0x0A;
    const uint8_t Extended_Config = 0x0B;
    const uint8_t Data_Out_Lower = 0x0C;
    const uint8_t Data_Out_Upper = 0x0D;
    const uint8_t Shutter_Lower = 0x0E;
    const uint8_t Shutter_Upper = 0x0F;
    const uint8_t Frame_Period_Lower = 0x10;
    const uint8_t Frame_Period_Upper = 0x11;
    const uint8_t Motion_Clear = 0x12;
    const uint8_t Frame_Capture = 0x13;
    const uint8_t SROM_Enable = 0x14;
    const uint8_t Frame_Period_Max_Bound_Lower = 0x19;
    const uint8_t Frame_Period_Max_Bound_Upper = 0x1A;
    const uint8_t Frame_Period_Min_Bound_Lower = 0x1B;
    const uint8_t Frame_Period_Min_Bound_Upper = 0x1C;
    const uint8_t Shutter_Max_Bound_Lower = 0x1D;
    const uint8_t Shutter_Max_Bound_Upper = 0x1E;
    const uint8_t SROM_ID = 0x1F;
    const uint8_t Inverse_Product_ID = 0x3F;

    // Configuration bits with bitfields
    union ConfigurationBits {
        struct {
            uint8_t RES : 1;       // Resolution: 0 = 400 CPI, 1 = 1600 CPI
            uint8_t Sys_Test : 1;  // System Test
            uint8_t LED_Mode : 1;  // LED Shutter Mode: 0 = always on, 1 = on when needed
            uint8_t Reserved : 5;  // Reserved bits, must be zero
        } fields;
        uint8_t value;
    };

    // Motion register bitfields
    union MotionBits {
        struct {
            uint8_t MOT : 1;       // Motion flag (1 = motion occurred)
            uint8_t OVF : 1;       // Overflow flag (1 = overflow occurred)
            uint8_t Reserved : 6;  // Reserved bits
        } fields;
        uint8_t value;
    };

    // Extended configuration bits
    union ExtendedConfigBits {
        struct {
            uint8_t Serial_NPU : 1;    // Disable serial port pull-up current
            uint8_t NAGC : 1;          // Disable AGC
            uint8_t Fixed_FR : 1;      // Fixed frame rate
            uint8_t Reserved : 5;      // Reserved bits
        } fields;
        uint8_t value;
    };

    // SROM Enable
    union SROMEnableBits {
        struct {
            uint8_t SROM_Enable : 1;   // Enable SROM Download
            uint8_t Reserved : 7;      // Reserved bits
        } fields;
        uint8_t value;
    };
}

class ADNS3080 : public Met4FoFSensor {
public:
    ADNS3080(SPI_HandleTypeDef* hspi, GPIO_TypeDef* CS_GPIO_Port, uint16_t CS_Pin, uint32_t baseID);

    void setFrameRate(uint16_t frameRate);
    bool isDataReady();
    void enableLEDShutterMode(bool enable);

    struct SensorData {
        int8_t delta_x;      // X movement
        int8_t delta_y;      // Y movement
        uint8_t squal;       // Surface quality
        uint8_t pixel_sum;   // Pixel sum
        uint8_t max_pixel;   // Maximum pixel value
        uint16_t shutter;    // Shutter value
        uint32_t frame_period; // Frame period
    };

    SensorData readExtendedSensorData();
    // Other existing function declarations...
    int getData(DataMessage *message, uint64_t rawTimeStamp);
    int getDescription(DescriptionMessage *message, DescriptionMessage_DESCRIPTION_TYPE descriptionType);

private:
    SPI_HandleTypeDef* hspi_;
    GPIO_TypeDef* CS_GPIO_Port_;
    uint16_t CS_Pin_;

    void select();
    void deselect();
    void writeRegister(uint8_t reg, uint8_t value);
    uint8_t readRegister(uint8_t reg);
};

} // namespace Met4FoFSensors

#endif // ADNS3080_HPP
