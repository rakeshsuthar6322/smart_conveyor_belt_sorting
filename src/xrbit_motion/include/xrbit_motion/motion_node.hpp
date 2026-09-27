#ifndef XRBIT_MOTION_NODE_HPP
#define XRBIT_MOTION_NODE_HPP

#include "rclcpp/rclcpp.hpp"
#include "xrbit_msgs/msg/sort_command.hpp"
#include <string>
#include <vector>

class MotionNode : public rclcpp::Node {
public:
    MotionNode();
    ~MotionNode();

private:
    void sort_command_callback(const xrbit_msgs::msg::SortCommand::SharedPtr msg);
    bool init_serial();
    void send_serial_command(uint8_t arm_id, uint8_t target_tray);

    rclcpp::Subscription<xrbit_msgs::msg::SortCommand>::SharedPtr cmd_sub_;
    std::string serial_port_;
    int baud_rate_;
    int serial_fd_;
};

#endif // XRBIT_MOTION_NODE_HPP
