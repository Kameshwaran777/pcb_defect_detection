# AI-Based PCB Defect Detection System

An automated inspection system that detects defects on printed circuit boards (PCBs) using a YOLOv8 object detection model. Users upload a PCB image through a Streamlit web app, and the system highlights the defects, classifies them, and stores the results in an SQLite database.

## Features
- PCB defect detection with YOLOv8
- Simple web interface built with Streamlit
- Detection history stored in SQLite
- Bounding boxes with defect labels and confidence scores

## Tech Stack
Python, YOLOv8 (Ultralytics), OpenCV, Streamlit, SQLite

## How to Run
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `streamlit run app.py`

## Project Info
Semester 5 PBL project, Chennai Institute of Technology.

## Results
![Result 1](result1.png)
![Result 2](result2.png)

