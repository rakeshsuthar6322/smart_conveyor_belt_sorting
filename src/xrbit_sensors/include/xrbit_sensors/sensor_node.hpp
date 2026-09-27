#ifndef XRBIT_SENSOR_NODE_HPP
#define XRBIT_SENSOR_NODE_HPP

#include "rclcpp/rclcpp.hpp"
#include "xrbit_msgs/msg/sensor_state.hpp"
#include <string>

class SensorNode : public rclcpp::Node {
public:
    SensorNode();
    ~SensorNode();

private:
    void read_serial_loop();
    bool init_serial();

    rclcpp::Publisher<xrbit_msgs::msg::SensorState>::SharedPtr sensor_pub_;
    rclcpp::TimerBase::SharedPtr timer_;
    
    std::string serial_port_;
    int baud_rate_;
    int serial_fd_;
};

#endif
