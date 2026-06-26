# MediaPipe-ROS2-PX4-Control
A modular ROS2-based hand gesture drone control system using MediaPipe, MAVSDK, PX4, and Gazebo simulation.
# MediaPipe ROS2 PX4 Control

A modular ROS2-based hand gesture drone control system using **MediaPipe**, **ROS2**, **MAVSDK**, **PX4**, and **Gazebo** simulation.

![Project Preview](p.png)

---

# Project Overview

This project demonstrates a modular robotics architecture where hand gestures are converted into drone flight commands using ROS2.

Unlike monolithic Python applications, each subsystem is separated into independent ROS2 nodes.

The current architecture consists of two nodes:

* **gesture_node** → Detects the user's hand using MediaPipe and publishes gesture commands.
* **px4_control_node** → Subscribes to gesture commands and sends movement commands to PX4 using MAVSDK.

This architecture allows computer vision, decision making and flight control to evolve independently.

---

# System Architecture

```text
                 Webcam
                    │
                    ▼
        MediaPipe Hand Tracking
                    │
                    ▼
             gesture_node.py
                    │
             /gesture_cmd Topic
                    │
                    ▼
          px4_control_node.py
                    │
                 MAVSDK
                    │
                    ▼
                 PX4 SITL
                    │
                    ▼
                  Gazebo
```

---

# Project Structure

```
ros2_ws
│
└── src
    ├── gesture_control
    │   ├── package.xml
    │   ├── setup.py
    │   ├── setup.cfg
    │   ├── resource
    │   └── gesture_control
    │       ├── __init__.py
    │       └── gesture_node.py
    │
    └── px4_control
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource
        └── px4_control
            ├── __init__.py
            └── px4_control_node.py
```

---

# Requirements

## Operating System

* Ubuntu 22.04

## Software

* ROS2 Humble
* PX4 Autopilot
* Gazebo
* Python 3.10

---

# Python Virtual Environments

The project intentionally uses separate Python virtual environments.

## MediaPipe Environment

Responsible only for computer vision.

```bash
python3 -m venv ~/mediapipe_env

source ~/mediapipe_env/bin/activate

pip install --upgrade pip

pip install mediapipe==0.10.14
pip install numpy==1.26.4
pip install opencv-python==4.9.0.80
```

---

## PX4 Environment

Responsible only for drone communication.

```bash
python3 -m venv ~/px4_env

source ~/px4_env/bin/activate

pip install --upgrade pip

pip install mavsdk
pip install pymavlink
```

---

# Building the Workspace

```bash
cd ~/ros2_ws

colcon build --symlink-install

source install/setup.bash
```

---

# Running the Project

## 1) Start PX4 SITL

```bash
cd ~/PX4-Autopilot

make px4_sitl gz_x500
```

---

## 2) Start Gesture Node

```bash
source /opt/ros/humble/setup.bash

source ~/ros2_ws/install/setup.bash

source ~/mediapipe_env/bin/activate

python3 ~/ros2_ws/src/gesture_control/gesture_control/gesture_node.py
```

---

## 3) Monitor ROS Topic

Open another terminal.

```bash
source /opt/ros/humble/setup.bash

source ~/ros2_ws/install/setup.bash

ros2 topic echo /gesture_cmd
```

Example output

```text
data: RIGHT
data: STOP
data: LEFT
data: FORWARD
```

---

## 4) Start PX4 Control Node

```bash
source /opt/ros/humble/setup.bash

source ~/ros2_ws/install/setup.bash

source ~/px4_env/bin/activate

python3 ~/ros2_ws/src/px4_control/px4_control/px4_control_node.py
```

---

# Gesture Mapping

| Finger Position | Command  |
| --------------- | -------- |
| Top             | FORWARD  |
| Bottom          | BACKWARD |
| Left            | LEFT     |
| Right           | RIGHT    |
| Center          | STOP     |

---

## Preview

![Project Preview](p.png)




