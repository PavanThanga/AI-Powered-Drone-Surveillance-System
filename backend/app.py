from flask import Flask, request, jsonify, Response
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import sqlite3
from datetime import datetime
from model import process_video, process_live_frame
import cv2

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
PROCESSED_DIR = os.path.join(BASE_DIR, "static", "processed")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


app.config["UPLOAD_FOLDER"] = UPLOAD_DIR


def insert_record(user, file_name, human, vehicle, weapon):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analysis_records 
        (user, file_name, human, vehicle, weapon, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user,
        file_name,
        human,
        vehicle,
        weapon,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


@app.route('/')
def home():
    return jsonify({"status": "Backend running"})


from flask import request, jsonify

@app.route("/analyze", methods=["POST"])
def analyze():
    if "video" not in request.files:
        return jsonify({"error": "No video file received"}), 400

    file = request.files["video"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # toggles
    human = request.form.get("human") == "true"
    vehicle = request.form.get("vehicle") == "true"
    weapon = request.form.get("weapon") == "true"

    filename = secure_filename(file.filename)
    name, _ = os.path.splitext(filename)

    input_path = os.path.join(UPLOAD_DIR, filename)
    output_name = f"processed_{name}.mp4"
    output_path = os.path.join(PROCESSED_DIR, output_name)

    # save uploaded file
    file.save(input_path)

    # 🔥 ACTUAL VIDEO PROCESSING 
    process_video(
        input_path,
        output_path,
        human=human,
        vehicle=vehicle,
        weapon=weapon
    )
    
    # 🔥 LOG TO DATABASE
    user_name = "admin" # Currently hardcoded in front-end
    try:
        insert_record(user_name, filename, human, vehicle, weapon)
    except Exception as e:
        print(f"Error logging to DB: {e}")

    return jsonify({
        "processed_video": f"/static/processed/{output_name}",
        "summary": {
            "human": human,
            "vehicle": vehicle,
            "weapon": weapon
        }
    })

def generate_original(source):
    if source == "0":
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # webcam (Windows safe)
    elif str(source).startswith("http://") or str(source).startswith("https://"):
        cap = cv2.VideoCapture(source) # generic IP streams
    else:
        cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)  # RTSP
        
    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            frame = cv2.resize(frame, (960, 540))

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()

def generate_processed(source, human=True, vehicle=True, weapon=False):
    if source == "0":
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    elif str(source).startswith("http://") or str(source).startswith("https://"):
        cap = cv2.VideoCapture(source)
    else:
        cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            frame = cv2.resize(frame, (960, 540))

            processed_frame = process_live_frame(
                frame,
                human=human,
                vehicle=vehicle,
                weapon=weapon
            )

            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()

@app.route('/live_original')
def live_original():
    source = request.args.get("source", "0")

    return Response(
        generate_original(source),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/live_processed')
def live_processed():
    source = request.args.get("source", "0")

    human = request.args.get("human") == "true"
    vehicle = request.args.get("vehicle") == "true"
    weapon = request.args.get("weapon") == "true"

    return Response(
        generate_processed(source, human, vehicle, weapon),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )
if __name__ == '__main__':
    app.run(debug=True)
