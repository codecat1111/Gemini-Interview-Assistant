# 🚀 Gemini Powered Mock Interview Assistant

A web-based tool that helps users prepare and practice for technical interviews using AI-powered feedback. 🎯💡

---

## 🌟 Features

✅ **Real-time audio recording & transcription** 🎤📝  
✅ **AI-powered analysis of interview responses** 🤖📊  
✅ **Two modes of operation:**

- 🎯 **AI Analysis Only**: Get immediate feedback 🔥
- 🔄 **Compare Mode**: Practice your answer first, then compare with AI analysis 🆚
  ✅ **Session management with history tracking** 📜📂  
  ✅ **Support for role-specific & job description context** 👨‍💻📄

---

## 🔧 Prerequisites

🛠 **System Requirements:**

- 🐍 Python **3.8+**
- ⚡ **PyTorch & TorchAudio**
- 🤗 **Transformers library**
- 🔑 **Google Cloud API key for Gemini AI**
- 🎧 **Virtual audio cable (VB-CABLE)**
- 🌐 **Internet connection for AI services**
- 💻 **Windows OS (for VB-CABLE setup)**

---

## 🏗️ Setup

### 1️⃣ Clone the Repository

```bash
 git clone https://github.com/codecat1111/Gemini-Interview-Assistant.git
 cd Interview-Assistance
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Virtual Audio Cable 🎧

- Install a **virtual audio cable** software
- Set **audio output** to "CABLE Input"

### 4️⃣ Set Up API Key 🔑

```bash
# Create .env file and add your Gemini API key
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
```

---

## 🚀 Usage

1️⃣ **Start the Gemini Analyzer Server** (in a new terminal):

```bash
python gemini_analyzer.py
```

2️⃣ **Start the Flask Server** 🌐:

```bash
python main.py
```

3️⃣ **Open in Browser**: `http://localhost:5000` 🌍

4️⃣ **Enter job role & description** ✍️

5️⃣ **Choose Your Mode** 🎙️:

- **AI Analysis Only**: Click "Start Recording" 📢
- **Compare Mode**: Record your answer, then click "Show AI Analysis" 🧐

---

## 🔎 Features in Detail

### 🎙️ **Recording Controls**

- **Start/Stop Recording** button ⏺️
- **New Recording** button for multiple attempts 🔄
- **Reset Session** button to clear history 🗑️

### 📊 **Analysis Options**

- **Real-time transcription** 📝
- **AI-powered feedback** 🤖
- **Compare Mode for self-assessment** 🆚
- **Session history tracking** 📂

### 📜 **History Feature**

- 🆕 "Start Recording (No History)" - Begins a new recording without considering previous responses
- 🔄 "New Recording (With History)" - Saves the current analysis to history before starting a new recording
- 📝 **History is automatically included in AI analysis for context**
- 🗑️ **Reset Session button clears all history**

### 🎨 **Theme Support**

- 🌞 **Light Mode** / 🌙 **Dark Mode** toggle
- 🎨 **Theme preference is saved automatically**
- ✅ **Accessible color schemes for better readability**

## Project Demo

https://github.com/codecat1111/Gemini-Interview-Assistant/assets/videos/project-demo.mp4

This video demonstrates:

- Setting up role and job description
- Recording and analyzing responses
- Using AI Analysis Only mode
- Using Compare mode
- Managing interview history
- Theme switching

---

## 🎤 Model Setup

### 🤗 **Loading the Whisper Model**

The application uses the **Whisper-Tiny** model for speech transcription. On first run, the model will be **automatically downloaded** from Hugging Face.

```python
# Initialize Whisper model
processor = AutoProcessor.from_pretrained("openai/whisper-tiny")
model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-tiny")
```

---

## 🎧 Virtual Audio Cable Setup

### 1️⃣ **Setting Up VB-Audio Virtual Cable**

This project uses **VB-Audio Virtual Cable** to capture system audio and process live transcriptions.

#### 🔽 **Installation**

- Download [VB-Audio Virtual Cable](https://vb-audio.com/Cable/)
- Run `VBCABLE_Setup_x64.exe` (for 64-bit systems)
- Restart your computer 🔄

#### 🎚 **Configuration**

1. Open **Sound Settings** (Win + I → "Sound")
2. **Set "CABLE Input (VB-Audio Virtual Cable)" as default output**
3. **Select "CABLE Output (VB-Audio Virtual Cable)" as microphone input**
4. (Optional) Use **VoiceMeeter Banana** for advanced routing 🎛️

---

## 🎤 System Audio Capture Implementation

### 🎧 **Virtual Cable Device Detection**

```python
def find_vb_audio_device():
    """Finds VB-Audio Virtual Cable device ID"""
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if "CABLE Output" in device["name"]:
            return i
    return None
```

### 🎙 **Audio Recording System**

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

---

## 🛠 Troubleshooting Virtual Audio Cable

⚠ **No Audio Detected?**

- ✅ Verify **"CABLE Input"** is set as **default playback device**
- ✅ Check **"CABLE Output"** is selected as **recording input**
- ✅ Ensure **system volume is not muted**

⚠ **Device Not Found?**

- 🔄 Restart the **VB-Audio service**
- 🔄 Reinstall the **drivers**
- 🔍 Check **Device Manager** for warning icons

⚠ **Poor Audio Quality?**

- 🎚 Ensure **sample rate settings match (16000 Hz)**
- 🔍 Check **CPU usage**
- 🚀 Close **unnecessary audio applications**

## Virtual Audio Cable Setup Demo

https://github.com/codecat1111/Gemini-Interview-Assistant/assets/videos/vb-cable-setup.mp4

This video covers:

- Installing VB-Cable
- Configuring Windows audio settings
- Testing the virtual audio setup
- Troubleshooting common issues

---

## 💡 Contributing

1️⃣ **Fork the Repository** 🍴

2️⃣ **Create a Feature Branch** (`git checkout -b feature/AmazingFeature`)

3️⃣ **Commit Your Changes** (`git commit -m 'Add AmazingFeature'`)

4️⃣ **Push to Branch** (`git push origin feature/AmazingFeature`)

5️⃣ **Open a Pull Request** 🚀

---

## ⭐ Found It Helpful? [Star It!](https://github.com/codecat1111/Gemini-Interview-Assistant/stargazers) ⭐

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
