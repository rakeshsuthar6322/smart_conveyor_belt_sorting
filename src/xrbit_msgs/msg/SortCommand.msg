std_msgs/Header header
uint8 arm_id            # 1 or 2 (which arm to move)
uint8 target_tray       # 1 to 4 (for Arm 1) or 5 to 8 (for Arm 2)
float64 intercept_time  # Absolute ROS time when arm should fire to intercept
