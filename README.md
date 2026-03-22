#  PostureBuddy: Real-Time Posture Detection with Computer Vision

An end-to-end machine learning system that detects and classifies human posture in real time using pose estimation and lightweight classification.

---

##  Motivation

Prolonged poor posture is a widespread issue among students and professionals, often leading to long-term health problems. I built this project to explore how computer vision and machine learning can be used to create a practical, real-time system that encourages better habits.

Beyond the application itself, this project is an exploration of how raw visual data can be transformed into meaningful, actionable insights through a complete ML pipeline.

---

##  System Overview

This project implements a full pipeline:

**Data → Features → Model → Real-Time Inference**

* Capture human pose data from webcam input
* Convert body landmarks into structured numerical features
* Train a machine learning model on labeled posture data
* Perform live posture classification in real time

---

##  Methodology

### Data Collection

* Custom-built data collection pipeline using webcam input
* Pose landmarks extracted using MediaPipe
* Manual labeling system:

  * G → Good posture
  * B → Bad posture
  * N → Neutral posture

### Feature Representation

* Uses body landmark coordinates as feature vectors
* Structures data into CSV format for reproducibility

### Model

* Standardization with `StandardScaler`
* Classification using `KNeighborsClassifier`
* Train/test split for basic evaluation

### Real-Time Inference

* Continuous webcam input
* Real-time pose extraction and classification
* Lightweight pipeline suitable for local execution

---

##  Design Choices

* **KNN over deep learning**: chosen for interpretability and fast iteration on small datasets
* **Landmark-based features**: reduces dimensionality compared to raw images
* **Modular pipeline**: separates data collection, training, and inference

---

##  Evaluation & Limitations

This system demonstrates a working real-time ML application, but also highlights key challenges:

* Performance varies with lighting conditions and camera positioning
* Dataset is relatively small and user-specific
* Temporal information (motion over time) is not yet utilized

---

##  Future Directions

* Incorporate temporal models (e.g., LSTM for posture sequences)
* Expand dataset across multiple users for generalization
* Introduce feedback mechanisms (alerts or scoring system)
* Explore deployment as a lightweight desktop or mobile application

---

##  What This Project Demonstrates

This project reflects an understanding of:

* Building end-to-end machine learning systems
* Translating raw sensor data into structured features
* Making design trade-offs between simplicity and performance
* Deploying models in real-time environments

---

##  Author

Shane Sok
High school student exploring artificial intelligence, with a focus on computer vision and real-world systems.

---

##  Additional Notes

This project was developed independently as part of my interest in applied AI and human-centered technology.

