import pytest
import numpy as np

# Import our Kalman Filter class from the sorter node
from xrbit_sorter.sorter_node import KalmanTrack

def test_kalman_initialization():
    """ Test that an object is initialized with the correct physical parameters """
    track = KalmanTrack(track_id=1, class_id=3, start_x=50.0, start_y=10.0)
    
    assert track.track_id == 1
    assert track.class_id == 3
    
    # Check the State Matrix: [X_pos, Y_pos, X_vel, Y_vel]
    assert track.x[0, 0] == 50.0  # X position
    assert track.x[1, 0] == 10.0  # Y position
    assert track.x[2, 0] == 0.0   # Initial X velocity
    assert track.x[3, 0] == 100.0 # Initial Y velocity MUST be 100mm/s (belt speed)

def test_kalman_predict_blind_zone():
    """ UT-01: Test that the object moves down the belt in memory when the camera is blind """
    track = KalmanTrack(track_id=2, class_id=1, start_x=100.0, start_y=0.0)
    
    # Simulate 1 full second passing while the object is in the camera's Blind Zone
    dt = 1.0
    track.predict(dt)
    
    # Because belt speed is 100mm/s, after 1 sec, the object MUST be at Y = 100.0mm
    assert track.x[0, 0] == 100.0  # X shouldn't change
    assert track.x[1, 0] == 100.0  # 0.0 + (100.0 * 1.0)
    
    # Simulate another 0.5 seconds passing
    track.predict(0.5)
    
    # Object should now be at exactly 150mm
    assert track.x[1, 0] == 150.0  # 100.0 + (100.0 * 0.5)

def test_kalman_update_measurement():
    """ UT-02: Test that a noisy camera measurement is smoothed out by the filter """
    track = KalmanTrack(track_id=3, class_id=4, start_x=50.0, start_y=10.0)
    
    # Predict forward 0.1 seconds (Physics says Y should now be 20.0mm)
    track.predict(0.1)
    assert track.x[1, 0] == 20.0
    
    # The camera takes a picture, but it has sub-pixel noise. 
    # It tells us the object is at Y=22.0 instead of 20.0.
    track.update(meas_x=51.0, meas_y=22.0)
    
    # The Kalman filter shouldn't trust the camera 100%, nor the physics 100%.
    # It should calculate a smoothed value between 20.0 and 22.0.
    assert track.x[1, 0] > 20.0
    assert track.x[1, 0] < 22.0
    
    # It should also slightly adjust the X position
    assert track.x[0, 0] > 50.0
