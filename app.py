import os
import logging
from flask import Flask, render_template, request, jsonify, send_file

from werkzeug.utils import secure_filename

from DetectApplication import process_video


REPORT_PATH = r'D:\Management\Personal\Reva AI\CP\Fastner detection\New\YoloUI\uploaded_files'
OUTPUT_FOLDER = os.path.join(REPORT_PATH, 'output')
UPLOAD_FOLDER = os.path.join(REPORT_PATH, 'input')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Ensure upload and output folders exist
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Store logs to send to the frontend
log_messages = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global log_messages
    log_messages.clear()  # Clear previous logs

    if 'file' not in request.files:
        message = 'No file part in the request.'
        logger.error(message)
        log_messages.append(f"ERROR: {message}")
        return jsonify({"error": message}), 400

    files = request.files.getlist('file')
    uploaded_files = []

    for file in files:
        if file.filename == '':
            message = 'No file selected for upload.'
            logger.warning(message)
            log_messages.append(f"WARNING: {message}")
            continue

        # Validate file format
        if not file.filename.endswith('.mp4'):
            message = f"Invalid file format: {file.filename}. Only mp4 files are allowed."
            logger.error(message)
            log_messages.append(f"ERROR: {message}")
            continue

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        uploaded_files.append({"filename": filename})

        # Log success message
        logger.info(f"File {filename} uploaded successfully.")
        log_messages.append(f"INFO: File {filename} uploaded successfully.")

    if not uploaded_files:
        message = 'No valid files uploaded.'
        logger.error(message)
        log_messages.append(f"ERROR: {message}")
        return jsonify({"error": message, "logs": log_messages}), 400

    # Process each file (example: adding mock processing logs)
    for uploaded_file in uploaded_files:
        filename = uploaded_file['filename']
        logger.info(f"The file {filename} is processing...")
        log_messages.append(f"INFO: The file {filename} is processing...")

        # Example mock processing
        #total_segments = 10  # Replace with actual logic
        #logger.info(f"The subdiv {filename} has {total_segments} segments.")
        #log_messages.append(f"INFO: The subdiv {filename} has {total_segments} segments.")
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    count, fitness = process_video(video_path)
    
    log_messages.append(f"RailTiePlates Detected: {count}")
    log_messages.append(f"Track Fitness: {fitness}")

  

    return jsonify({"message": "Files successfully uploaded and processed.", "files": uploaded_files, "logs": log_messages, "count": count, "fitness": fitness})

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)