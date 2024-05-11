/*
 * Met4FOFADNS3080.cpp
 *
 *  Created on: 11.05.2024
 *      Author: seeger01
 */




#include "Met4FoFADNS3080.h"

namespace Met4FoFSensors {

ADNS3080::ADNS3080(SPI_HandleTypeDef* hspi, GPIO_TypeDef* CS_GPIO_Port, uint16_t CS_Pin, uint32_t baseID)
    : Met4FoFSensor(baseID), hspi_(hspi), CS_GPIO_Port_(CS_GPIO_Port), CS_Pin_(CS_Pin) {
    setBaseID(baseID);
}

void ADNS3080::select() {
    HAL_GPIO_WritePin(CS_GPIO_Port_, CS_Pin_, GPIO_PIN_RESET);
}

void ADNS3080::deselect() {
    HAL_GPIO_WritePin(CS_GPIO_Port_, CS_Pin_, GPIO_PIN_SET);
}

void ADNS3080::writeRegister(uint8_t reg, uint8_t value) {
    select();
    uint8_t data[2] = {uint8_t(0x80 | reg), value};
    HAL_SPI_Transmit(hspi_, data, 2, 100);
    deselect();
}

uint8_t ADNS3080::readRegister(uint8_t reg) {
    select();
    uint8_t value;
    HAL_SPI_Transmit(hspi_, &reg, 1, 100);
    HAL_SPI_Receive(hspi_, &value, 1, 100);
    deselect();
    return value;
}

void ADNS3080::setFrameRate(uint16_t frameRate) {
    uint32_t clockFrequency = 24000000; // Assuming a 24 MHz clock frequency
    uint32_t framePeriod = clockFrequency / frameRate;
    uint8_t lowerByte = framePeriod & 0xFF;
    uint8_t upperByte = (framePeriod >> 8) & 0xFF;

    writeRegister(ADNS3080RegisterMap::Frame_Period_Max_Bound_Upper, upperByte);
    writeRegister(ADNS3080RegisterMap::Frame_Period_Max_Bound_Lower, lowerByte);
}

bool ADNS3080::isDataReady() {
    uint8_t motion = readRegister(ADNS3080RegisterMap::Motion);
    return (motion & 0x80) != 0;
}

void ADNS3080::enableLEDShutterMode(bool enable) {
    using namespace ADNS3080RegisterMap;
    ConfigurationBits config;
    config.value = readRegister(Configuration_Bits);
    config.fields.LED_Mode = enable ? 1 : 0;
    writeRegister(Configuration_Bits, config.value);
}

ADNS3080::SensorData ADNS3080::readExtendedSensorData() {
    SensorData data;

    data.delta_x = static_cast<int8_t>(readRegister(ADNS3080RegisterMap::Delta_X));
    data.delta_y = static_cast<int8_t>(readRegister(ADNS3080RegisterMap::Delta_Y));
    data.squal = readRegister(ADNS3080RegisterMap::SQUAL);
    data.pixel_sum = readRegister(ADNS3080RegisterMap::Pixel_Sum);
    data.max_pixel = readRegister(ADNS3080RegisterMap::Maximum_Pixel);
    data.shutter = static_cast<uint16_t>(readRegister(ADNS3080RegisterMap::Shutter_Upper)) << 8 |
                   static_cast<uint16_t>(readRegister(ADNS3080RegisterMap::Shutter_Lower));
    data.frame_period = static_cast<uint32_t>(readRegister(ADNS3080RegisterMap::Frame_Period_Upper)) << 8 |
                        static_cast<uint32_t>(readRegister(ADNS3080RegisterMap::Frame_Period_Lower));

    return data;
}

int ADNS3080::getData(DataMessage *message, uint64_t rawTimeStamp) {
    if (message == nullptr) {
        return -1; // Error if the message pointer is null
    }

    auto data = readExtendedSensorData(); // Assuming this function exists and reads all necessary sensor data

    message->id = _ID;
    message->unix_time = 0xFFFFFFFF; // Placeholder for actual timestamp implementation
    message->unix_time_nsecs = static_cast<uint32_t>(rawTimeStamp & 0xFFFFFFFF);
    message->time_uncertainty = static_cast<uint32_t>((rawTimeStamp >> 32) & 0xFFFFFFFF);
    message->sample_number = _SampleCount++;

    message->Data_01 = static_cast<float>(data.delta_x); // Example conversion to float if necessary
    message->Data_02 = static_cast<float>(data.delta_y);
    message->has_Data_02 = true;

    return 0; // Success
}

int ADNS3080::getDescription(DescriptionMessage *message, DescriptionMessage_DESCRIPTION_TYPE descriptionType) {
    if (message == nullptr) {
        return -1; // Error if the message pointer is null
    }

    strncpy(message->Sensor_name, "ADNS3080 Optical Flow Sensor", sizeof(message->Sensor_name));
    message->id = _ID;
    message->Description_Type = descriptionType;

    switch (descriptionType) {
        case DescriptionMessage_DESCRIPTION_TYPE_PHYSICAL_QUANTITY:
            strncpy(message->str_Data_01, "Optical Flow X", sizeof(message->str_Data_01));
            strncpy(message->str_Data_02, "Optical Flow Y", sizeof(message->str_Data_02));
            break;
        case DescriptionMessage_DESCRIPTION_TYPE_UNIT:
            strncpy(message->str_Data_01, "\\one", sizeof(message->str_Data_01));
            strncpy(message->str_Data_02, "\\one", sizeof(message->str_Data_02));
            break;
        case DescriptionMessage_DESCRIPTION_TYPE_RESOLUTION:
            message->has_f_Data_01 = true;
            message->f_Data_01 = 256; // Assuming pixel resolution is 1:1
            message->has_f_Data_02 = true;
            message->f_Data_02 = 256;
            break;
        case DescriptionMessage_DESCRIPTION_TYPE_MIN_SCALE:
            message->has_f_Data_01 = true;
            message->f_Data_01 = -128; // Minimum scale for X (Add appropriate value)
            message->has_f_Data_02 = true;
            message->f_Data_02 = -128; // Minimum scale for Y (Add appropriate value)
            break;
        case DescriptionMessage_DESCRIPTION_TYPE_MAX_SCALE:
            message->has_f_Data_01 = true;
            message->f_Data_01 = 127; // Maximum scale for X (Add appropriate value)
            message->has_f_Data_02 = true;
            message->f_Data_02 = 127; // Maximum scale for Y (Add appropriate value)
            break;
        case DescriptionMessage_DESCRIPTION_TYPE_HIERARCHY:
            strncpy(message->str_Data_01, "OpticalFlow/0", sizeof(message->str_Data_01));
            strncpy(message->str_Data_02, "OpticalFlow/1", sizeof(message->str_Data_02));
            break;
        default:
            // If an unknown type is passed, handle appropriately
            return -1;
    }

    return 0; // Success
}


} // namespace Met4FoFSensors
