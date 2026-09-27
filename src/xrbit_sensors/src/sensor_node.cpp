#include "xrbit_sensors/sensor_node.hpp"
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#include <iostream>

SensorNode::SensorNode() : Node("sensor_node"), serial_fd_(-1) {
    this->declare_parameter<std::string>("serial_port", "/dev/ttyACM0");
    this->declare_parameter<int>("baud_rate", 115200);

    serial_port_ = this->get_parameter("serial_port").as_string();
    baud_rate_ = this->get_parameter("baud_rate").as_int();

    sensor_pub_ = this->create_publisher<xrbit_msgs::msg::SensorState>("/sensors/state", 10);

    if (init_serial()) {
        RCLCPP_INFO(this->get_logger(), "📡 Connected to STM32 Sensors at %s", serial_port_.c_str());
        // Run the read loop at ~100Hz (10ms)
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(10),
            std::bind(&SensorNode::read_serial_loop, this)
        );
    } else {
        RCLCPP_ERROR(this->get_logger(), "❌ Failed to open serial port for sensors!");
    }
}

SensorNode::~SensorNode() {
    if (serial_fd_ != -1) close(serial_fd_);
}

bool SensorNode::init_serial() {
    // Open as Read-Only (Motion node handles writing)
    serial_fd_ = open(serial_port_.c_str(), O_RDONLY | O_NOCTTY | O_NDELAY);
    if (serial_fd_ == -1) return false;

    struct termios options;
    tcgetattr(serial_fd_, &options);
    cfsetispeed(&options, B115200);
    cfsetospeed(&options, B115200);
    
    options.c_cflag |= (CLOCAL | CREAD);
    options.c_cflag &= ~PARENB;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;
    
    tcsetattr(serial_fd_, TCSANOW, &options);
    return true;
}

void SensorNode::read_serial_loop() {
    if (serial_fd_ == -1) return;

    uint8_t buffer[4];
    int bytes_read = read(serial_fd_, buffer, sizeof(buffer));

    // Look for our 4-byte Sensor Protocol: [0xBB, SensorBits, Checksum, 0x55]
    if (bytes_read >= 4 && buffer[0] == 0xBB && buffer[3] == 0x55) {
        
        uint8_t sensor_bits = buffer[1];
        uint8_t chk = buffer[2];
        
        if (chk == sensor_bits) { // Simple checksum
            auto msg = xrbit_msgs::msg::SensorState();
            msg.header.stamp = this->get_clock()->now();
            
            // Unpack the bits (Bit 0-3)
            msg.entry_photo_sick = (sensor_bits & 0x01) != 0;
            msg.exit_photo_sick  = (sensor_bits & 0x02) != 0;
            msg.arm1_home_ifm    = (sensor_bits & 0x04) != 0;
            msg.arm2_home_ifm    = (sensor_bits & 0x08) != 0;

            sensor_pub_->publish(msg);
        }
    }
}

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<SensorNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
