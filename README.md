CalmMateAI: Your Personal Well-being Companion
🚀 Project Overview
CalmMateAI is an innovative web application designed to provide a safe and supportive space for users to explore their mental well-being. Built with Flask, this application combines a friendly user interface with the power of artificial intelligence to offer empathetic conversational support, daily well-being tips, and easy access to essential resources.

The project's core is an AI-powered chatbot that uses the Groq API to engage in empathetic conversations, detect the seriousness of user input, and provide tailored suggestions for self-care. It also integrates the Gemini API to offer dynamic, AI-generated daily tips and reflective check-in prompts, making each interaction fresh and personalized.

✨ Key Features
AI-Powered Chat: Engage in empathetic and supportive conversations with a chatbot powered by a large language model.

Seriousness Detection: The AI analyzes user input to determine the emotional state and provides contextually appropriate responses, including suggestions for seeking professional help in serious situations.

Dynamic Well-being Tips: A daily tip is generated on the dashboard using the Gemini API to offer a new dose of inspiration and self-care advice each day.

Reflective Check-in Prompts: Get a personalized, AI-generated question to help you reflect on your feelings and practice mindfulness.

Emergency Contact Locator: Easily find local emergency and mental health support resources based on your location.

University-Specific Resources: Access dedicated well-being resources from your university through a secure authentication process.

Voice Input: Transcribe spoken messages into text for a hands-free conversational experience.

🛠️ Technology Stack
Backend: Python 3, Flask

AI Integration: Groq API, Gemini API

Frontend: HTML5, Tailwind CSS, JavaScript

Data Handling: JSON for structured data storage

Environment Management: venv (Python virtual environment)

📦 Installation and Setup
Follow these steps to get a local copy of the project up and running.

Prerequisites
Python 3.8+ installed on your system.

pip (Python package installer).

Step-by-Step Guide
Clone the Repository:

git clone https://github.com/saberabanu0001/NewCalmateAI.git
cd NewCalmateAI

Create a Virtual Environment:

python3 -m venv venv

Activate the Virtual Environment:

On macOS / Linux:

source venv/bin/activate

On Windows:

venv\Scripts\activate

Install Dependencies:

pip install -r requirements.txt

Configure Environment Variables:

Create a file named .env in the root directory of the project.

Add your API keys to this file:

FLASK_SECRET_KEY='your_secret_key'
GROQ_API_KEY='your_groq_api_key'

Replace 'your_secret_key' and 'your_groq_api_key' with your actual keys.

Run the Flask Application:

flask run

The application will now be running on http://127.0.0.1:5000/.

🧑‍💻 Author
Saberabanu - Initial work and development of the CalmMateAI web application.

