# AI-Powered Drone Surveillance System

An intelligent real-time surveillance system built using Flask, YOLOv8, OpenCV, HTML, CSS, and JavaScript for detecting humans and vehicles from drone footage and live video streams. The system provides both existing footage analysis and live transmission monitoring through a futuristic web-based dashboard.

---

## 🚀 Features

- User Authentication Interface
- Upload and Analyze Recorded Videos/Images
- Real-Time Live Stream Analysis
- AI-Based Human & Vehicle Detection using YOLOv8
- Toggle Detection Models Dynamically
- Processed Video Output with Bounding Boxes
- Detection Summary Panel
- RTSP/Webcam Stream Support
- SQLite Database Integration
- Responsive Futuristic UI

---

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask
- Flask-CORS

### AI / Computer Vision
- YOLOv8
- OpenCV
- Ultralytics

### Database
- SQLite

---

## 📂 Project Structure

```bash
AI-Powered-Drone-Surveillance/
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
│
├── backend/
│   ├── app.py
│   ├── model.py
│   ├── database.db
│   ├── uploads/
│   ├── static/
│   │   └── processed/
│   └── best.pt
│
├── README.md
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/AI-Powered-Drone-Surveillance.git
cd AI-Powered-Drone-Surveillance
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

#### Windows
```bash
venv\Scripts\activate
```

#### Linux/Mac
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install flask flask-cors ultralytics opencv-python
```

---

## ▶️ Run the Backend Server

```bash
cd backend
python app.py
```

Backend will start at:

```bash
http://127.0.0.1:5000
```

---

## 🌐 Run the Frontend

Open `frontend/index.html` in your browser.

---

## 🧠 AI Detection Models

The system currently supports:

- Human Detection
- Vehicle Detection
- Weapon Detection (Future Enhancement)

YOLOv8 Nano model is used for fast real-time inference.

---

## 📡 Live Surveillance

The system supports:

- Webcam Input (`0`)
- RTSP Camera Streams
- Real-Time AI Frame Processing

---

## 🖥️ User Interface

The dashboard provides two modes:

1. Existing Footage Analysis
2. Live Transmission Monitoring

Features include:
- Detection model toggles
- Upload section
- AI processed feed
- Original footage preview
- Detection summary panel

---

## 📊 Detection Workflow

1. Upload video or connect live stream
2. Select detection models
3. Send media to Flask backend
4. YOLOv8 processes frames
5. Bounding boxes are drawn
6. Processed output is displayed in browser

---

## 🗄️ Database

SQLite database is used to store:
- User activity
- File details
- Detection preferences
- Analysis records

---

## 👨‍💻 Author

**Venkata Pavan Thanga**  

---

## 📜 License

This project is developed for academic and research purposes.
