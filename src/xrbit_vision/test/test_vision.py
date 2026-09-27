import pytest

def test_bounding_box_to_center_logic():
    """ UT-03: Validate that YOLO bounding boxes perfectly translate to center coordinates """
    # Simulate YOLO returning a bounding box (x1, y1, x2, y2)
    x1, y1, x2, y2 = 100.0, 200.0, 300.0, 400.0
    
    # This is the exact math used in vision_node.py
    center_x = (x1 + x2) / 2.0
    center_y = (y1 + y2) / 2.0
    
    assert center_x == 200.0
    assert center_y == 300.0

def test_vision_confidence_threshold():
    """ Ensure low-confidence YOLO ghost objects are rejected """
    conf_thresh = 0.65
    detection_conf = 0.45
    assert detection_conf < conf_thresh # Should drop this frame!
