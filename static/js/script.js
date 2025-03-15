const recordButton = document.getElementById("recordButton");
const status = document.getElementById("status");
const transcriptionDiv = document.getElementById("transcription");
const geminiAnalysis = document.getElementById("geminiAnalysis");
const audioPlayer = document.getElementById("audioPlayer");
let isRecording = false;

// Add this at the top of your script.js
const darkModeToggle = document.getElementById('darkModeToggle');

// Check for saved theme preference or default to light
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
darkModeToggle.checked = savedTheme === 'dark';

// Handle theme toggle
darkModeToggle.addEventListener('change', () => {
  if (darkModeToggle.checked) {
    document.documentElement.setAttribute('data-theme', 'dark');
    localStorage.setItem('theme', 'dark');
  } else {
    document.documentElement.setAttribute('data-theme', 'light');
    localStorage.setItem('theme', 'light');
  }
});

// Add mode selection handling
const aiOnlyMode = document.getElementById("aiOnly");
const compareMode = document.getElementById("compare");
const userAnswerSection = document.getElementById("userAnswerSection");

function updateMode() {
userAnswerSection.style.display = compareMode.checked
    ? "block"
    : "none";
geminiAnalysis.style.display = compareMode.checked ? "none" : "block";
compareButton.style.display = "none";
}

aiOnlyMode.addEventListener("change", updateMode);
compareMode.addEventListener("change", updateMode);

// Add this function near the top of your script section
function scrollToAnalysis() {
const analysisColumn = document.querySelector(".analysis-column");
analysisColumn.scrollIntoView({ behavior: "smooth", block: "start" });
window.scrollTo({
    top: 0,
    behavior: "smooth",
});
}

recordButton.addEventListener("click", async () => {
if (!isRecording) {
    const response = await fetch("/start_recording", { method: "POST" });
    const data = await response.json();

    if (data.error) {
    status.textContent = data.error;
    return;
    }

    isRecording = true;
    recordButton.textContent = "Stop Recording";
    recordButton.classList.add("recording");
    status.textContent = "Recording system audio...";
} else {
    // First, stop the recording immediately
    const stopResponse = await fetch("/stop_recording", {
    method: "POST",
    });
    const stopData = await stopResponse.json();

    isRecording = false;
    recordButton.textContent = "Start Recording";
    recordButton.classList.remove("recording");
    status.textContent = "Processing...";

    if (stopData.status === "success") {
    // Then process the audio file
    const processingStatus =
        document.getElementById("processingStatus");
    processingStatus.textContent =
        "Processing audio and getting AI analysis...";

    const processResponse = await fetch("/process_audio", {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
        },
        body: JSON.stringify({
        audio_file: stopData.audio_file,
        role: document.getElementById("roleInput").value,
        job_description:
            document.getElementById("jobDescription").value,
        }),
    });
    const processData = await processResponse.json();

    if (processData.status === "success") {
        transcriptionDiv.textContent = processData.transcription;
        geminiAnalysis.innerHTML = marked.parse(
        processData.gemini_analysis
        );

        if (compareMode.checked) {
        geminiAnalysis.style.display = "none";
        compareButton.style.display = "block";
        processingStatus.textContent =
            "Analysis complete! Type your answer and click Show AI Analysis when ready.";
        } else {
        geminiAnalysis.style.display = "block";
        processingStatus.textContent = "Analysis complete!";
        // Add this line to scroll to analysis when it's shown
        scrollToAnalysis();
        }
    }
    }
    status.textContent = "Ready to record";
}
});

// Update compare button functionality
document.getElementById("compareButton").addEventListener("click", () => {
geminiAnalysis.style.display = "block";
document.getElementById("compareButton").textContent =
    "AI Analysis Shown";
document.getElementById("compareButton").disabled = true;
// Add this line to scroll to analysis when it's revealed
scrollToAnalysis();
});

// Add this JavaScript to your existing script section
document
.getElementById("userAnswer")
.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = this.scrollHeight + "px";
});

const newRecordingBtn = document.getElementById("newRecordingBtn");
const resetSessionBtn = document.getElementById("resetSessionBtn");

newRecordingBtn.addEventListener("click", async () => {
    // Extract and save History section if present
    if (geminiAnalysis.textContent.trim()) {
        const analysisText = geminiAnalysis.textContent;
        let historySection = "";
        
        // Extract History section
        const lines = analysisText.split('\n');
        let capture = false;
        
        for (const line of lines) {
            if (line.includes('History')) {
                capture = true;
                continue;
            } else if (capture && (line.startsWith('#') || line.trim() === '')) {
                break;
            } else if (capture) {
                historySection += line + '\n';
            }
        }

        // Save History if found
        if (historySection.trim()) {
            const saveResponse = await fetch("/save_to_history", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    history: historySection.trim()
                }),
            });
        }
    }

    // Clear current analysis and reset UI
    transcriptionDiv.textContent = "";
    geminiAnalysis.textContent = "";

    // Reset Compare button state
    const compareButton = document.getElementById("compareButton");
    compareButton.textContent = "Show AI Analysis";
    compareButton.disabled = false;

    // Reset processing status
    const processingStatus = document.getElementById("processingStatus");
    if (processingStatus) {
        processingStatus.textContent = "";
    }

    // Automatically trigger the record button click
    recordButton.click();
});

resetSessionBtn.addEventListener("click", async () => {
const response = await fetch("/reset_session", {
    method: "POST",
});

// Clear all fields including role and job description
transcriptionDiv.textContent = "";
geminiAnalysis.textContent = "";
document.getElementById("roleInput").value = "";
document.getElementById("jobDescription").value = "";
const processingStatus = document.getElementById("processingStatus");
if (processingStatus) {
    processingStatus.textContent = "";
}
});