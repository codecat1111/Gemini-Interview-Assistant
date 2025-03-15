import torch
import torchaudio
import sounddevice as sd
import soundfile as sf
import numpy as np
from flask import Flask, render_template, jsonify, request
import os
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
from datetime import datetime
import requests

# Initialize Flask app
app = Flask(__name__)

# Create templates directory and static directory if they don't exist
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# Step 1: Load WhisperProcessor (AutoProcessor) and Model
processor = AutoProcessor.from_pretrained("openai/whisper-tiny")
model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-tiny")


class AudioRecorder:
    def __init__(self):
        self.sample_rate = 16000
        self.recording = False
        self.audio_data = []

    def find_vb_audio_device(self):
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if "CABLE Output" in device["name"]:
                return i
        return None

    def start_recording(self):
        device_id = self.find_vb_audio_device()
        if device_id is None:
            return {"error": "VB-Audio Virtual Cable not found! Check installation."}

        try:
            self.recording = True
            self.audio_data = []

            def audio_callback(indata, frames, time, status):
                if self.recording:
                    self.audio_data.append(indata.copy())

            self.stream = sd.InputStream(
                device=device_id,
                channels=1,
                samplerate=self.sample_rate,
                callback=audio_callback
            )
            self.stream.start()
            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)}

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.stream.stop()
            self.stream.close()

            if self.audio_data:
                audio_data = np.concatenate(self.audio_data, axis=0)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"static/recording_{timestamp}.wav"
                sf.write(filename, audio_data, self.sample_rate)
                return filename
        return None


recorder = AudioRecorder()


# Move model to GPU for faster inference
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)


def transcribe_audio(audio_path):
    """Transcribes a long audio file using Whisper-Tiny with chunking."""
    waveform, sample_rate = torchaudio.load(audio_path)

    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(
            orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform)

    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)

    waveform = waveform.numpy().flatten()  # Convert to 1D array

    # Convert audio to chunks to bypass rate limits for whisper-tiny model
    chunk_length = 25 * 16000  # 25 seconds * 16000 samples/sec
    stride = 10 * 16000  # 10-second overlap for better continuity

    full_transcription = []

    # Process chunks with proper padding
    for i in range(0, len(waveform), chunk_length - stride):
        end_idx = min(i + chunk_length, len(waveform))
        chunk = waveform[i:end_idx]

        # Pad last chunk if needed
        if len(chunk) < chunk_length:
            chunk = np.pad(chunk, (0, chunk_length - len(chunk)), 'constant')

        # Process chunk
        inputs = processor(
            chunk,
            sampling_rate=16000,
            return_tensors="pt",
            language="en",
            return_attention_mask=True
        ).to(device)

        with torch.no_grad():
            output_tokens = model.generate(
                inputs.input_features,
                attention_mask=inputs.attention_mask,
                max_length=1024,
                min_length=1  # Ensure some output is generated
            )

        chunk_transcription = processor.batch_decode(
            output_tokens, skip_special_tokens=True)[0].strip()

        # Only add non-empty transcriptions
        if chunk_transcription:
            full_transcription.append(chunk_transcription)

    # Join with space and clean up any double spaces
    return ' '.join(full_transcription).replace('  ', ' ')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start_recording', methods=['POST'])
def start_recording():
    result = recorder.start_recording()
    return jsonify(result)


@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    audio_file = recorder.stop_recording()
    return jsonify({
        "status": "success",
        "audio_file": audio_file
    })


@app.route('/process_audio', methods=['POST'])
def process_audio():
    data = request.json
    audio_file = data.get('audio_file')
    role = data.get('role', '')
    job_description = data.get('job_description', '')

    if audio_file:
        try:
            transcription = transcribe_audio(audio_file)

            # Process with Gemini
            try:
                gemini_response = requests.post(
                    'http://localhost:5001/analyze',
                    json={
                        'text': transcription,
                        'role': role,
                        'job_description': job_description
                    }
                )
                gemini_analysis = gemini_response.json().get('analysis', 'Analysis failed')
            except requests.RequestException:
                gemini_analysis = "Unable to connect to Gemini service"

            # Delete the audio file after processing
            try:
                os.remove(audio_file)
            except OSError as e:
                print(f"Error deleting audio file: {e}")

            # Read history if it exists
            history = ""
            if os.path.exists('history.txt') and os.path.getsize('history.txt') > 0:
                with open('history.txt', 'r', encoding='utf-8') as f:
                    history = f.read()

            # Add history context to your AI prompt
            prompt = f"""Previous interview history:\n{history}\n
            Current transcription:\n{transcription}\n
            Role: {role}\n
            Job Description: {job_description}\n
            Please analyze the answer..."""

            return jsonify({
                "status": "success",
                "transcription": transcription,
                "gemini_analysis": gemini_analysis
            })
        except Exception as e:
            # Try to clean up the file even if processing failed
            try:
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            except OSError:
                pass
            return jsonify({
                "status": "error",
                "message": str(e)
            })

    return jsonify({"status": "error"})


@app.route('/save_to_history', methods=['POST'])
def save_to_history():
    data = request.json
    if 'history' not in data:
        return jsonify({"status": "error", "message": "No history provided"})

    history_file = 'history.txt'
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(history_file, 'a', encoding='utf-8') as f:
            f.write(f"\n[{timestamp}]\n")
            f.write(data['history'])
            f.write("\n" + "-"*50 + "\n")
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/reset_session', methods=['POST'])
def reset_session():
    history_file = 'history.txt'
    try:
        # Create empty history file or clear existing one
        open(history_file, 'w').close()
        return jsonify({"status": "success", "message": "Session reset successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    app.run(debug=True)
