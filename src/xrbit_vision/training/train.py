#!/usr/bin/env python3
import os
from ultralytics import YOLO

def main():
    print("🚀 Starting YOLOv8 Training for XRbit Sorter...")
    
    # 1. Load the base model (Transfer Learning)
    # We start with 'yolov8n.pt' (Nano) because it is the absolute fastest for the Jetson Orin Nano
    model = YOLO('yolov8n.pt') 

    # 2. Get the path to dataset.yaml
    current_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(current_dir, 'dataset', 'dataset.yaml')

    if not os.path.exists(yaml_path):
        print(f"❌ Error: Could not find {yaml_path}")
        return

    # 3. Train the model
    print(f"📂 Using dataset config: {yaml_path}")
    results = model.train(
        data=yaml_path,
        epochs=150,              # Number of times it loops over your data
        imgsz=640,               # Default YOLO resolution
        batch=16,                # Images processed at once (lower to 8 if GPU runs out of memory)
        device=0,                # 0 = Use NVIDIA GPU
        project="xrbit_models",
        name="8_class_custom",   # Output folder name
        save=True,               # Save the best weights
        patience=25              # Early stopping if no improvement for 25 epochs
    )

    print("\n✅ Training Complete!")
    print("Your custom weights are saved at: xrbit_models/8_class_custom/weights/best.pt")
    
    # 4. Export to TensorRT (Uncomment this later when running ON the Jetson!)
    # print("⚙️ Exporting to TensorRT for Jetson optimization...")
    # model.export(format="engine", half=True) # FP16 precision for max speed

if __name__ == '__main__':
    main()
