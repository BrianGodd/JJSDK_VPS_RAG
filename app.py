from flask import Flask, request, send_file, jsonify, send_from_directory
import os
import time
import main as pipeline
import json

UPLOAD_FOLDER = "uploads"
AUDIO_FILENAME = "input.wav"
OUTPUT_FILENAME = "output.mp3"
RESULT_FILENAME = "result.txt"
INPUT_TEXT_FILENAME = "input.txt"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/process", methods=["POST"])
def process_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    if 'param' not in request.form or 'text' not in request.form:
        return jsonify({"error": "Missing param or text field"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # 儲存音訊
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], AUDIO_FILENAME)
    file.save(input_path)

    # 解析整數與文字參數
    try:
        param = int(request.form['param'])
    except ValueError:
        return jsonify({"error": "param must be an integer"}), 400
    
    try:
        param_x = round(float(request.form['param_x']), 1)  # 保留一位小數
        param_z = round(float(request.form['param_z']), 1)
        param_rot = round(float(request.form['param_rot']), 1)
        print(param_x, param_z, param_rot)
    except ValueError:
        return jsonify({"error": "One of param_x/z/rot is not a valid float"}), 400

    input_text = request.form['text']
    data = json.loads(input_text)
    # 取出 text 欄位
    text = data['text']
    with open(INPUT_TEXT_FILENAME, "w", encoding="utf-8") as f:
        f.write(text)

    try:
        # 呼叫 pipeline.main(param)
        pipeline.main(kind = param, pos_x = param_x, pos_z = param_z, direction = param_rot)

        # 讀取 result.txt
        with open(RESULT_FILENAME, "r", encoding="utf-8") as f:
            result_text = f.read()

        return jsonify({
            "message": result_text,
            "audio_url": f"/download/{OUTPUT_FILENAME}"
        })

    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
        return jsonify({"error": str(e)}), 500

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(".", filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
