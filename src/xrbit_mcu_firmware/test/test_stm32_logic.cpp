#include <gtest/gtest.h>
#include <cstdint>

// Simulating the STM32 C Firmware parsing logic
bool process_sort_command(uint8_t* buf, uint32_t len) {
    if (len < 5) return false;
    if (buf[0] != 0xAA || buf[4] != 0x55) return false; // Bad framing
    
    uint8_t arm_id = buf[1];
    uint8_t tray_id = buf[2];
    uint8_t chk = buf[3];
    
    if (chk != (uint8_t)(arm_id + tray_id)) return false; // Checksum failed
    return true; // Valid command!
}

TEST(STM32LogicTest, UT06_AggressiveRejection) {
    // 1. Valid command (Arm 1, Tray 3, Checksum 4)
    uint8_t valid_buf[] = {0xAA, 1, 3, 4, 0x55};
    EXPECT_TRUE(process_sort_command(valid_buf, 5));

    // 2. Electrical Noise / Corrupted Checksum
    uint8_t corrupt_chk[] = {0xAA, 1, 3, 99, 0x55}; 
    EXPECT_FALSE(process_sort_command(corrupt_chk, 5));

    // 3. Bad Framing (Missing Start Byte 0xAA)
    uint8_t bad_framing[] = {0x00, 1, 3, 4, 0x55};
    EXPECT_FALSE(process_sort_command(bad_framing, 5));
}
