#include <gtest/gtest.h>
#include <vector>
#include <cstdint>

// Simulating the exact payload generator from motion_node.cpp
std::vector<uint8_t> generate_payload(uint8_t arm_id, uint8_t target_tray) {
    std::vector<uint8_t> buffer = {0xAA, arm_id, target_tray, 0x00, 0x55};
    buffer[3] = buffer[1] + buffer[2]; // Checksum
    return buffer;
}

TEST(MotionProtocolTest, UT04_ValidChecksums) {
    // Test Arm 1, Tray 3
    auto buf1 = generate_payload(1, 3);
    EXPECT_EQ(buf1[0], 0xAA);
    EXPECT_EQ(buf1[3], 4); // Checksum: 1 + 3 = 4
    EXPECT_EQ(buf1[4], 0x55);

    // Test Arm 2, Tray 8
    auto buf2 = generate_payload(2, 8);
    EXPECT_EQ(buf2[3], 10); // Checksum: 2 + 8 = 10
}
