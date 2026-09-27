#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from xrbit_msgs.msg import TrackedObject, TrackedObjectArray
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')
        
        # --- Parameters ---
        # These allow you to change the model and camera without editing the code!
        self.declare_parameter('model_path', 'yolov8n.pt') 
        self.declare_parameter('camera_source', 0)         
        self.declare_parameter('conf_thresh', 0.60)
        
        model_path = self.get_parameter('model_path').get_parameter_value().string_value
        camera_source = self.get_parameter('camera_source').get_parameter_value().integer_value
        self.conf_thresh = self.get_parameter('conf_thresh').get_parameter_value().double_value

        # --- Publishers ---
        # This publishes our custom message to the Sorter logic
        self.obj_pub = self.create_publisher(TrackedObjectArray, '/vision/tracked_objects', 10)
        # This publishes a debug video feed so you can see the bounding boxes in RViz
        self.img_pub = self.create_publisher(Image, '/vision/debug_frame', 10)
        
        # --- Initialize YOLO ---
        self.get_logger().info(f"Loading YOLO model from: {model_path}")
        self.model = YOLO(model_path)
        
        # --- Initialize Camera ---
        self.get_logger().info(f"Opening camera source: {camera_source}")
        self.cap = cv2.VideoCapture(camera_source)
        if not self.cap.isOpened():
            self.get_logger().error("Could not open camera! Check connection.")
            
        self.bridge = CvBridge()
        
        # Run vision loop at ~30 FPS
        self.timer = self.create_timer(1.0 / 30.0, self.timer_callback)
        
    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            return
            
        # 1. Run YOLO Inference
        results = self.model(frame, verbose=False)[0]
        
        # 2. Prepare our custom ROS2 Message Array
        msg_array = TrackedObjectArray()
        msg_array.header.stamp = self.get_clock().now().to_msg()
        msg_array.header.frame_id = "camera_optical_frame"
        
        # 3. Parse YOLO boxes
        for box in results.boxes:
            conf = float(box.conf[0])
            if conf < self.conf_thresh:
                continue
                
            cls_id = int(box.cls[0])
            
            # Calculate the center (X, Y) of the object on the conveyor belt
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            center_x = (x1 + x2) / 2.0
            center_y = (y1 + y2) / 2.0
            
            # Populate our custom message
            obj_msg = TrackedObject()
            obj_msg.class_id = cls_id
            obj_msg.center_x = float(center_x)
            obj_msg.center_y = float(center_y)
            obj_msg.confidence = conf
            
            msg_array.objects.append(obj_msg)
            
            # Draw on the frame for debugging
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f"Class:{cls_id} {conf:.2f}", (int(x1), int(y1)-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 4. Publish the data to the rest of the robot
        self.obj_pub.publish(msg_array)
        
        # Publish the debug image (with bounding boxes drawn on it)
        img_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        self.img_pub.publish(img_msg)

    def destroy_node(self):
        if self.cap:
            self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = VisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
