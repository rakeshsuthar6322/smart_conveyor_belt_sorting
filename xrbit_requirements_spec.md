# XRbit-SORT-8C: Requirements Specification Document

This document outlines the User, System, Functional, and Integration requirements for the XRbit-SORT-8C automated conveyor sorting project. It serves as the baseline for the engineering team (CV, Electronics, CAD, Software, and Robotics).

---

## 1. User Requirements (UR)
*These define what the end-user (the operator or business) needs the system to accomplish.*

*   **UR-01 (Sorting Capability):** The system must automatically sort passing objects into 8 distinct categories, dropping them into 8 separate trolleys/bins.
*   **UR-02 (Payload):** The system must reliably sort objects weighing up to a maximum of 250 grams.
*   **UR-03 (Environment):** The system must be capable of operating outdoors, resisting dust, dirt, and moisture.
*   **UR-04 (Maintainability):** The system must use standard industrial-grade hardware (preferably German engineering standards) to ensure high reliability and easy part replacement.
*   **UR-05 (Safety):** The system must include a robust, operator-accessible emergency stop mechanism that immediately halts all moving parts without relying on software.
*   **UR-06 (Adaptability):** The user must be able to retrain the AI vision system on custom objects without needing to rewrite the core software logic.

---

## 2. System Requirements (SR)
*These define the overarching physical, electrical, and performance parameters of the machine.*

*   **SR-01 (Conveyor Dimensions):** The main conveyor belt shall have a precise width of 200 mm.
*   **SR-02 (Conveyor Speed):** The conveyor belt must operate at a constant, regulated speed of 100 mm/s.
*   **SR-03 (Vision Geometry):** The camera shall be mounted exactly 450 mm above the belt, providing a Field of View (FOV) of 220 mm x 160 mm.
*   **SR-04 (IP Rating):** All external field devices (motors, sensors, camera, buttons, enclosure) must carry a minimum ingress protection rating of IP65, up to IP69K.
*   **SR-05 (Power Infrastructure):** The system shall be powered by a centralized 24V DC / 10A industrial power supply (e.g., PULS), stepped down only internally for specific microelectronics.
*   **SR-06 (Compute Hardware):** AI inference shall be performed on an NVIDIA Jetson Orin Nano 8GB, while real-time hardware I/O shall be handled by an STM32F407VET6 MCU.

---

## 3. Functional Requirements (FR)
*These define the specific behaviors and step-by-step actions the system must perform during operation.*

*   **FR-01 (Entry/Exit Detection):** Photoelectric sensors (SICK W12-2) shall detect the presence of an object at the beginning of the belt to start the process, and at the end of the belt to verify if an object was missed.
*   **FR-02 (Idle Shutdown):** If the entry photoelectric sensor detects no incoming objects for a predefined timeout period, the system shall halt the conveyor belt to save power.
*   **FR-03 (Object Recognition):** The vision system must capture images and execute a YOLOv8 object detection model at a minimum of 30 frames per second (FPS) to classify objects and determine their X/Y coordinates.
*   **FR-04 (Blind-Zone Tracking):** Because objects exit the camera's FOV before reaching the sorting arms, the software must utilize a state estimator (Kalman Filter) to virtually track the object's position down the belt based on the 100mm/s speed.
*   **FR-05 (Actuation Arm 1):** The system shall actuate Sorting Arm 1 using a NEMA 17 stepper motor to sweep objects classified as Classes 1, 2, 3, or 4 sideways into their respective bins.
*   **FR-06 (Actuation Arm 2):** The system shall actuate Sorting Arm 2 to sweep objects classified as Classes 5, 6, 7, or 8 sideways into their respective bins.
*   **FR-07 (Home Verification):** Inductive proximity sensors (ifm IGS232) shall detect the metal presence of the sorting arms to verify they have successfully returned to their home (zero) positions after a sort.

---

## 4. Integration Requirements (IR)
*These define how the different hardware and software subsystems interface and communicate with each other.*

*   **IR-01 (Software Architecture):** The high-level software stack shall be built on ROS 2 (Robot Operating System), utilizing a distributed node architecture with distinct packages for Vision, Sorting logic, Motion, and Sensors.
*   **IR-02 (PC-to-MCU Communication):** The NVIDIA Jetson and STM32F407 shall communicate via USB OTG (Virtual COM Port) using a strict, low-latency, 5-byte binary protocol (Start Byte, ID, Target, Checksum, End Byte) at 115200 baud.
*   **IR-03 (Vision Networking):** The Basler ace 2 camera shall interface with the Jetson compute module via Gigabit Ethernet, utilizing Power over Ethernet (PoE IEEE 802.3af) to combine data and power into a single Cat6 cable.
*   **IR-04 (Signal Conditioning):** All 24V digital signals from industrial field sensors (SICK, ifm) must pass through TTC surge protectors and 24V-to-TTL optocouplers (e.g., Phoenix Contact) before interfacing with the 3.3V STM32 GPIO pins.
*   **IR-05 (Motor Driver Interface):** The STM32 shall drive the three Trinamic TMC2209 motor drivers via highly precise hardware timer interrupts (STEP/DIR pins) and configure them dynamically via a shared USART half-duplex UART bus.
*   **IR-06 (Safety Interlock):** The E-Stop button shall be hardwired directly to a safety relay (Siemens 3SK1) that physically cuts the 24V power to the motor drivers, while simultaneously providing an auxiliary 3.3V digital feedback signal to the STM32.

## 5. Unit Test Requirements (UT)
*These define the testing of individual software and hardware components in complete isolation.*

*   **UT-01 (Kalman Filter Predict):** The `xrbit_sorter` tracking algorithm must be tested with simulated time deltas (`dt`) to ensure objects propagate precisely at 100mm/s without camera updates (testing the Blind Zone).
*   **UT-02 (Kalman Filter Update):** The tracking algorithm must be tested with simulated YOLO bounding boxes to verify the Hungarian matching algorithm correctly associates objects and prevents ID switching when multiple objects are on the belt.
*   **UT-03 (Vision Inference):** The `xrbit_vision` node must be tested against a static dataset of 100 known images to verify it consistently outputs correct `TrackedObjectArray` messages at >= 30 FPS on the Jetson Orin Nano.
*   **UT-04 (Motion Protocol Generation):** The `xrbit_motion` C++ node must be unit-tested using a mock serial port to verify it correctly constructs the 5-byte payload (`[0xAA, ArmID, TrayID, Checksum, 0x55]`) and computes the checksum accurately for all 8 tray scenarios.
*   **UT-05 (Sensor Bit Unpacking):** The `xrbit_sensors` C++ node must be tested with mock binary payloads (e.g., `0xBB 0x05 0x05 0x55`) to verify it accurately decodes the bitmask into the `SensorState` boolean values.
*   **UT-06 (STM32 Logic):** The STM32 C firmware must have its checksum validation function unit-tested (Software-in-the-Loop) to ensure corrupted serial packets are aggressively rejected without triggering the motors.

## 6. Integration Test Requirements (IT)
*These define the testing of interactions between multiple nodes, subsystems, and physical hardware.*

*   **IT-01 (Vision-to-Sorter Pipeline):** A ROS 2 `bag` file containing pre-recorded tracking data shall be played back. The system must verify that the `xrbit_sorter` correctly receives the topics and fires the `/motion/sort_command` at the correct, deterministic timestamps.
*   **IT-02 (Jetson-to-STM32 Comms - HIL):** (Hardware-In-the-Loop) The Jetson shall send 1,000 automated sort commands to the STM32 via USB `/dev/ttyACM0`. A logic analyzer connected to the STM32 STEP/DIR pins must verify 100% command execution with zero dropped packets.
*   **IT-03 (Sensor-to-Jetson Comms - HIL):** A physical 24V signal shall be toggled at the STM32 optocoupler input (simulating the SICK sensor). The system must verify that the `xrbit_sensors` node publishes the state change to the ROS 2 network within 20 milliseconds.
*   **IT-04 (Full AI-to-Hardware Chain):** A physical object (e.g., Class 3) shall be placed in front of the active camera. The system must verify the complete end-to-end chain: YOLO detection -> Kalman Tracking -> ROS 2 Command -> STM32 USB parsing -> NEMA 17 Stepper motor rotation.
*   **IT-05 (Safety Interlock Integration):** While the conveyor is running, the physical E-Stop button shall be pressed. The system must verify that (1) 24V power to the TMC2209 motor drivers is physically severed by the safety relay, and (2) the STM32 relays the halted state back to the Jetson master planner.

## 7. System Test Requirements (ST)
*These define the black-box testing of the fully assembled machine to verify it meets the overarching business, performance, and environmental requirements.*

*   **ST-01 (Sorting Accuracy):** A mixed batch of 800 objects (100 of each of the 8 classes) shall be fed into the system. The machine must recognize, track, and sort them into the correct physical trays with a minimum end-to-end accuracy of 98%.
*   **ST-02 (Payload Stress Test):** Objects weighing exactly 250 grams (the maximum specified payload) shall be placed on the belt. The system must verify that the NEMA 17 stepper motors can cleanly deflect the heavy objects without stalling, slipping, or losing step synchronization.
*   **ST-03 (Continuous Throughput):** The machine shall be operated continuously for 8 hours at the nominal belt speed of 100 mm/s. The Jetson ROS 2 software must not exhibit any memory leaks, and the STM32 must not drop any USB connections.
*   **ST-04 (Thermal Validation):** During the 8-hour continuous test, the internal temperature of the main electronics enclosure must remain below 55°C, proving that the specified fan and filter cooling configuration is sufficient for the Jetson Orin Nano and TMC2209 drivers.
*   **ST-05 (Power Failure Recovery):** While the system is actively sorting, the main 24V power supply shall be unexpectedly disconnected. Upon restoring power, the Jetson must automatically boot the Docker containers, the STM32 must re-home the sorting arms using the ifm sensors, and the entire system must be fully operational within 60 seconds with absolutely zero human intervention.
