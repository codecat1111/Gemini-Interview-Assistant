# Gemini Powered Mock Interview Assistant

A web-based tool that helps users prepare and practice for technical interviews using AI-powered feedback.

## Features

- Real-time audio recording and transcription
- AI-powered analysis of interview responses
- Two modes of operation:
  - AI Analysis Only: Get immediate feedback
  - Compare Mode: Practice your answer first, then compare with AI analysis
- Session management with history tracking
- Support for role-specific and job description context

## Prerequisites

- Python 3.8+
- PyTorch and TorchAudio
- Transformers library
- Google Cloud API key for Gemini AI
- Virtual audio cable (VB-CABLE)
- Internet connection for AI services
- Windows OS (for VB-CABLE setup)

## Setup

1. Clone the repository:

```bash
git clone https://github.com/codecat1111/Gemini-Interview-Assistant.git
cd Interview-Assistance
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure virtual audio cable:

   - Install a virtual audio cable software
   - Set audio output to "CABLE Input"

4. Create .env file and add your Gemini API key:

```bash
# Create .env file and add your Gemini API key
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
```

## Usage

1. Start the Gemini analyzer server (in a new terminal):

```bash
python gemini_analyzer.py
```

2. Start the Flask server:

```bash
python main.py
```

3. Open your browser and navigate to `http://localhost:5000`

4. Enter the job role and description

5. Choose your mode:
   - AI Analysis Only: Click "Start Recording" to begin
   - Compare Mode: Enable compare mode, record your answer, then click "Show AI Analysis"

## Features in Detail

### Recording Controls

- Start/Stop Recording button
- New Recording button for multiple attempts
- Reset Session button to clear history

### Analysis Options

- Real-time transcription
- AI-powered feedback
- Compare mode for self-assessment
- Session history tracking

### History Feature

The application maintains a history of interview responses:

- "Start Recording (No History)" - Begins a new recording without considering previous responses
- "New Recording (With History)" - Saves the current analysis to history before starting a new recording
- History is automatically included in AI analysis for context
- Reset Session button clears all history

### Theme Support

- Toggle between dark and light modes
- Theme preference is saved automatically
- Consistent styling across all components
- Accessible color schemes for better readability

## Model Setup

### Loading the Whisper Model

The application uses the Whisper-tiny model for speech transcription. On first run, the model will be automatically downloaded from Hugging Face.

```python
# Initialize Whisper model
processor = AutoProcessor.from_pretrained("openai/whisper-tiny")
model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-tiny")
```

## Virtual Audio Cable Setup and Live Transcription

### 1. Setting Up VB-Audio Virtual Cable

This project utilizes VB-Audio Virtual Cable to capture system audio and process live transcriptions.

#### 1.1 Installation

- Download VB-Audio Virtual Cable from the [official website](https://vb-audio.com/Cable/)
- Extract and install by running `VBCABLE_Setup_x64.exe` (for 64-bit systems)
- Restart your computer to ensure the changes take effect

#### 1.2 Configuring VB-Audio Virtual Cable

1. Open Sound Settings in Windows (Win + I → "Sound")
2. Under Output Devices:
   - Set "CABLE Input (VB-Audio Virtual Cable)" as default output
3. Under Input Devices:
   - Select "CABLE Output (VB-Audio Virtual Cable)" as microphone input
4. (Optional) Use VoiceMeeter Banana for advanced routing if needed

### 2. System Audio Capture Implementation

The application includes built-in functions to detect and record system audio through VB-Audio Virtual Cable.

#### 2.1 Virtual Cable Device Detection

```python
def find_vb_audio_device():
    """Finds VB-Audio Virtual Cable device ID"""
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if "CABLE Output" in device["name"]:
            return i
    return None
```

#### 2.2 Audio Recording System

```python
class SystemAudioRecorder:
    def __init__(self):
        self.sample_rate = 16000
        self.recording = False
        self.audio_data = []

    def start_recording(self):
        device_id = find_vb_audio_device()
        if device_id is None:
            raise RuntimeError("VB-Audio Virtual Cable not found!")

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

    def stop_recording(self):
        self.recording = False
        self.stream.stop()
        self.stream.close()
        audio_data = np.concatenate(self.audio_data, axis=0)
        filename = "recorded_audio.wav"
        sf.write(filename, audio_data, self.sample_rate)
        return filename
```

### Troubleshooting Virtual Audio Cable

1. **No Audio Detected:**

   - Verify "CABLE Input" is set as default playback device
   - Check "CABLE Output" is selected as recording input
   - Ensure system volume is not muted

2. **Device Not Found:**

   - Restart the VB-Audio service
   - Reinstall the drivers if necessary
   - Check Device Manager for any warning icons

3. **Poor Audio Quality:**
   - Verify sample rate settings match (16000 Hz)
   - Check for system CPU usage
   - Close unnecessary audio applications

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Your Name - [@codecat1111](https://github.com/codecat1111)

Project Link: [https://github.com/codecat1111/Gemini-Interview-Assistant](https://github.com/codecat1111/Gemini-Interview-Assistant)
