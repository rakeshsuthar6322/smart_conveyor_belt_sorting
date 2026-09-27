#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from xrbit_msgs.msg import TrackedObjectArray, SortCommand
import numpy as np
import time
from scipy.optimize import linear_sum_assignment

class KalmanTrack:
    def __init__(self, track_id, class_id, start_x, start_y):
        self.track_id = track_id
        self.class_id = class_id
        
        # State vector: [X_pos, Y_pos, X_vel, Y_vel] (in millimeters)
        # We initialize Y_vel to 100 mm/s based on your belt specs
        self.x = np.array([[start_x], [start_y], [0.0], [100.0]]) 
        
        # Covariance Matrix (Uncertainty)
        self.P = np.eye(4) * 10.0
        
        # Measurement Matrix (We only get X and Y from the camera, not velocity)
        self.H = np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0]])
                           
        # Measurement Noise (Camera jitter)
        self.R = np.eye(2) * 5.0
        
        self.last_update_time = time.time()
        self.missed_frames = 0
        
    def predict(self, dt):
        """ Runs when object is blind (out of frame) or between frames """
        # State Transition Matrix (Physics model)
        # x_new = x_old + vx * dt
        # y_new = y_old + vy * dt
        F = np.array([[1, 0, dt, 0],
                      [0, 1, 0, dt],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]])
                      
        # Process Noise (Allows velocity to fluctuate slightly)
        Q = np.eye(4) * 0.1
        
        # Predict State
        self.x = np.dot(F, self.x)
        # Predict Uncertainty
        self.P = np.dot(np.dot(F, self.P), F.T) + Q
        
    def update(self, meas_x, meas_y):
        """ Runs when we get a new camera frame showing this object """
        z = np.array([[meas_x], [meas_y]])
        
        # Difference between measurement and prediction (Innovation)
        y = z - np.dot(self.H, self.x)
        
        # Innovation Covariance
        S = np.dot(np.dot(self.H, self.P), self.H.T) + self.R
        
        # Kalman Gain (How much do we trust the camera vs our physics model?)
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        
        # Update State
        self.x = self.x + np.dot(K, y)
        
        # Update Uncertainty
        I = np.eye(4)
        self.P = np.dot((I - np.dot(K, self.H)), self.P)
        
        self.missed_frames = 0
        self.last_update_time = time.time()


class SorterNode(Node):
    def __init__(self):
        super().__init__('sorter_node')
        
        # Physical Parameters (in millimeters)
        self.declare_parameter('pixels_to_mm_ratio', 0.114) # 220mm / 1920px
        self.declare_parameter('arm1_y_pos', 450.0) # mm from camera start
        self.declare_parameter('arm2_y_pos', 750.0) # mm from camera start
        
        self.px_to_mm = self.get_parameter('pixels_to_mm_ratio').value
        self.arm1_y = self.get_parameter('arm1_y_pos').value
        self.arm2_y = self.get_parameter('arm2_y_pos').value
        
        self.tracks = []
        self.next_track_id = 0
        self.last_time = time.time()
        
        # Subscriptions & Publishers
        self.sub = self.create_subscription(TrackedObjectArray, '/vision/tracked_objects', self.vision_callback, 10)
        self.cmd_pub = self.create_publisher(SortCommand, '/motion/sort_command', 10)
        
        # High-frequency control loop (50 Hz) for predicting Blind Zone movement
        self.timer = self.create_timer(0.02, self.tracking_loop)
        
        self.get_logger().info("Sorter Brain & Kalman Filter initialized.")

    def vision_callback(self, msg):
        """ Matches YOLO camera detections to existing Kalman tracks using Hungarian Algorithm """
        current_time = time.time()
        
        meas_x = [obj.center_x * self.px_to_mm for obj in msg.objects]
        meas_y = [obj.center_y * self.px_to_mm for obj in msg.objects]
        classes = [obj.class_id for obj in msg.objects]
        
        if len(self.tracks) == 0:
            # First objects ever seen
            for i in range(len(meas_x)):
                self.tracks.append(KalmanTrack(self.next_track_id, classes[i], meas_x[i], meas_y[i]))
                self.next_track_id += 1
            return

        # Build distance matrix between existing tracks and new camera measurements
        if len(meas_x) > 0:
            cost_matrix = np.zeros((len(self.tracks), len(meas_x)))
            for i, trk in enumerate(self.tracks):
                for j in range(len(meas_x)):
                    # Distance formula
                    dist = np.hypot(trk.x[0,0] - meas_x[j], trk.x[1,0] - meas_y[j])
                    cost_matrix[i, j] = dist
            
            # Scipy Linear Sum Assignment (Hungarian Algorithm)
            row_ind, col_ind = linear_sum_assignment(cost_matrix)
            
            unassigned_measurements = set(range(len(meas_x)))
            
            for r, c in zip(row_ind, col_ind):
                if cost_matrix[r, c] < 50.0: # 50mm matching threshold
                    self.tracks[r].update(meas_x[c], meas_y[c])
                    unassigned_measurements.remove(c)
                else:
                    self.tracks[r].missed_frames += 1
                    
            # Create new tracks for unassigned measurements
            for c in unassigned_measurements:
                self.tracks.append(KalmanTrack(self.next_track_id, classes[c], meas_x[c], meas_y[c]))
                self.next_track_id += 1

    def tracking_loop(self):
        """ This runs at 50Hz even when the camera sees nothing (Blind Zone propagation) """
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        active_tracks = []
        for trk in self.tracks:
            # 1. PREDICT: Push the object down the belt in memory
            trk.predict(dt)
            
            # If camera hasn't seen it in a while, it's in the BLIND ZONE.
            # But the Kalman predict step keeps updating its position accurately!
            
            # 2. CHECK INTERCEPT: Has it reached an arm?
            # Arm 1 handles classes 1-4
            if trk.class_id <= 4:
                if trk.x[1,0] >= self.arm1_y:
                    self.fire_arm(1, trk.class_id)
                    continue # Remove track, we sorted it
                    
            # Arm 2 handles classes 5-8
            elif trk.class_id >= 5:
                if trk.x[1,0] >= self.arm2_y:
                    self.fire_arm(2, trk.class_id)
                    continue # Remove track, we sorted it
                    
            # If it fell off the end of the belt without being sorted
            if trk.x[1,0] > self.arm2_y + 200:
                self.get_logger().warn(f"Object {trk.track_id} missed and fell off belt.")
                continue 
                
            active_tracks.append(trk)
            
        self.tracks = active_tracks
        
    def fire_arm(self, arm_id, class_id):
        cmd = SortCommand()
        cmd.arm_id = arm_id
        cmd.target_tray = class_id # e.g. class 3 goes to tray 3
        
        self.get_logger().info(f"🟢 FIRE COMMAND: Arm {arm_id} to deflect Class {class_id} into Tray {class_id}!")
        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = SorterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
