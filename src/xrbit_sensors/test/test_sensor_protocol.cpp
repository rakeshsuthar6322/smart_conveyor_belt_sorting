#include <gtest/gtest.h>
#include <cstdint>

struct SensorState {
    bool entry_photo; bool exit_photo; bool arm1_home; bool arm2_home;
};

// Simulating the exact unpacking logic from sensor_node.cpp
SensorState unpack_sensor_byte(uint8_t sensor_bits) {
    SensorState s;
    s.entry_photo = (sensor_bits & 0x01) != 0;
    s.exit_photo  = (sensor_bits & 0x02) != 0;
    s.arm1_home   = (sensor_bits & 0x04) != 0;
    s.arm2_home   = (sensor_bits & 0x08) != 0;
    return s;
}

TEST(SensorProtocolTest, UT05_BitmaskDecoding) {
    // Test 0x09 (Binary: 0000 1001) -> Entry Photo (Bit 0) + Arm 2 Home (Bit 3) are HIGH
    auto state = unpack_sensor_byte(0x09);
    EXPECT_TRUE(state.entry_photo);
    EXPECT_FALSE(state.exit_photo);
    EXPECT_FALSE(state.arm1_home);
    EXPECT_TRUE(state.arm2_home);
}
