#include "xrbit_motion/motion_node.hpp"
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#include <iostream>

MotionNode::MotionNode() : Node("motion_node"), serial_fd_(-1) {
    // Parameters (You can change USB port without recompiling)
    this->declare_parameter<std::string>("serial_port", "/dev/ttyACM0");
    this->declare_parameter<int>("baud_rate", 115200);

    serial_port_ = this->get_parameter("serial_port").as_string();
    baud_rate_ = this->get_parameter("baud_rate").as_int();

    // Connect to STM32 via USB Serial
    if (init_serial()) {
        RCLCPP_INFO(this->get_logger(), "🔌 Connected to STM32 at %s", serial_port_.c_str());
    } else {
        RCLCPP_ERROR(this->get_logger(), "❌ Failed to open serial port %s! Operating in dummy mode.", serial_port_.c_str());
    }

    // Subscribe to commands from the Sorter Brain
    cmd_sub_ = this->create_subscription<xrbit_msgs::msg::SortCommand>(
        "/motion/sort_command", 10,
        std::bind(&MotionNode::sort_command_callback, this, std::placeholders::_1)
    );
    
    RCLCPP_INFO(this->get_logger(), "Motion node ready. Waiting for sort commands...");
}

MotionNode::~MotionNode() {
    if (serial_fd_ != -1) {
        close(serial_fd_);
    }
}

bool MotionNode::init_serial() {
    // Standard POSIX C serial initialization
    serial_fd_ = open(serial_port_.c_str(), O_RDWR | O_NOCTTY | O_NDELAY);
    if (serial_fd_ == -1) return false;

    struct termios options;
    tcgetattr(serial_fd_, &options);
    cfsetispeed(&options, B115200);
    cfsetospeed(&options, B115200);
    
    // 8N1 setup (8 data bits, no parity, 1 stop bit)
    options.c_cflag |= (CLOCAL | CREAD);
    options.c_cflag &= ~PARENB;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;
    
    tcsetattr(serial_fd_, TCSANOW, &options);
    return true;
}

void MotionNode::sort_command_callback(const xrbit_msgs::msg::SortCommand::SharedPtr msg) {
    RCLCPP_INFO(this->get_logger(), "⚙️ EXECUTING: Move Arm %d to Tray %d", msg->arm_id, msg->target_tray);
    send_serial_command(msg->arm_id, msg->target_tray);
}

void MotionNode::send_serial_command(uint8_t arm_id, uint8_t target_tray) {
    /* 
     * 5-Byte Binary Protocol for STM32:
     * Byte 0: 0xAA (Start Byte)
     * Byte 1: Arm ID (1 or 2)
     * Byte 2: Target Tray (1-8)
     * Byte 3: Checksum (Arm ID + Tray)
     * Byte 4: 0x55 (End Byte)
     */
    std::vector<uint8_t> buffer = {0xAA, arm_id, target_tray, 0x00, 0x55};
    buffer[3] = buffer[1] + buffer[2]; // Calculate Checksum

    if (serial_fd_ != -1) {
        write(serial_fd_, buffer.data(), buffer.size());
    } else {
        RCLCPP_WARN(this->get_logger(), "Serial disconnected. Cannot send physical command to STM32.");
    }
}

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<MotionNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
