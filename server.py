from flask import Flask, render_template, request, jsonify, send_file
from speech_toolkit import record_audio, transcribe_audio, compare_texts, generate_suggestions
import pyttsx3
import os
import tempfile

app = Flask(__name__)
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/record", methods=["POST"])
def record():
    message = record_audio()
    return jsonify({"message": message})

@app.route("/home")
def main():
    return render_template("home.html")

@app.route("/articles")
def articles():
    return render_template("articles.html")


# tts
@app.route('/tts')
def index():
    return render_template('tts.html')

@app.route('/convert', methods=['POST'])
def convert_text_to_audio():
    text = request.form['text']
    volume = float(request.form['volume'])

    # Initialize the TTS engine
    engine = pyttsx3.init()
    engine.setProperty('volume', volume)
    engine.setProperty('rate', 150)

    # Save speech to a temporary WAV file
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    temp_audio.close()  # Close the file so pyttsx3 can write to it
    engine.save_to_file(text, temp_audio.name)
    engine.runAndWait()

    # Send the file to the frontend
    response = send_file(temp_audio.name, mimetype='audio/wav', as_attachment=False)

    # Clean up temporary file after sending
    @response.call_on_close
    def cleanup_tempfile():
        if os.path.exists(temp_audio.name):
            os.remove(temp_audio.name)

    return response

@app.route("/transcript")
def trans():
    return render_template("index.html")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    transcription_result = transcribe_audio()
    return jsonify({"transcription": transcription_result})

@app.route("/compare", methods=["POST"])
def compare():
    reference_text = request.form.get("reference_text")
    transcription_result = request.form.get("transcription_result")
    if not reference_text or not transcription_result:
        return jsonify({"error": "Both reference text and transcription are required!"}), 400

    accuracy, differences = compare_texts(reference_text, transcription_result)
    return jsonify({"accuracy": accuracy, "differences": differences})

@app.route("/suggestions", methods=["POST"])
def suggestions():
    reference_text = request.form.get("reference_text")
    transcription_result = request.form.get("transcription_result")
    differences = request.form.get("differences")
    if not reference_text or not transcription_result or not differences:
        return jsonify({"error": "All fields are required!"}), 400

    suggestions = generate_suggestions(reference_text, transcription_result, differences)
    return jsonify({"suggestions": suggestions})

if __name__ == "__main__":
    app.run(debug=True)
