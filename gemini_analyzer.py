import google.generativeai as genai
from dotenv import load_dotenv
import os
from datetime import datetime
from flask import Flask, jsonify, request

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

app = Flask(__name__)


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data or 'text' not in data or 'role' not in data or 'job_description' not in data:
        return jsonify({
            "status": "error",
            "message": "Missing required information"
        })

    text = data['text']
    role = data['role']
    job_description = data['job_description']

    try:
        # Read previous history if exists
        previous_history = ""
        if os.path.exists('history.txt') and os.path.getsize('history.txt') > 0:
            with open('history.txt', 'r', encoding='utf-8') as f:
                previous_history = f.read()

        prompt = f"""You are a {role}.

Job Description:
{job_description}

Previous Interview History:
{previous_history}

Based on the job role and job description, as an interviewee, provide an answer to the following question:
{text}

Points to consider while providing the response:
1) Go straight to the point.
2) Provide counter questions.
3) Divide your output into a set of maybes and for sure's.
4) Please format your response using Markdown.
5) If you think the question is straightforward, provide straightforward points (Increase the forsures and reduce the maybes).
6) If you think the question is quite complex, provide unsure points (Increase the maybes and reduce the forsure's).
7) Add code blocks if only necessary.
8) Add a quick and very brief summary of what question was asked by me and what answer was provided you (the model ) with the title "History"
"""
        response = gemini_model.generate_content(prompt)

        return {
            "status": "success",
            "analysis": response.text
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == '__main__':
    app.run(port=5001)
