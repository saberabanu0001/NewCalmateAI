# 🌿 CalmMateAI: Your Personal Well-being Companion 🚀

### CalmMateAI is an innovative web application designed to provide a safe and supportive space for users to explore their mental well-being. Built with Flask, this application combines a friendly user interface with the power of artificial intelligence to offer empathetic conversational support, daily well-being tips, and quick access to essential resources.

---

## ✨ Features

- 🤖 **AI-Powered Chat** – Engage in empathetic and supportive conversations with an AI chatbot powered by the Groq API.  
- ⚖️ **Seriousness Detection** – The AI analyzes user input to detect emotional states and provides contextually appropriate responses, including professional help suggestions when needed.  
- 🌱 **Dynamic Well-being Tips** – Fresh daily tips are generated using the Gemini API to inspire self-care and positivity.  
- 🪞 **Reflective Check-in Prompts** – Personalized AI-generated questions encourage mindfulness and self-reflection.  
- 📍 **Emergency Contact Locator** – Quickly access local emergency and mental health resources based on your location.  
- 🎓 **University-Specific Resources** – Securely access well-being support provided by your university.  
- 🎙️ **Voice Input** – Convert speech to text for a hands-free experience.  

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask  
- **AI Integration**: Groq API, Gemini API  
- **Frontend**: HTML5, Tailwind CSS, JavaScript  
- **Data Handling**: JSON  
- **Environment Management**: venv (Python virtual environment)  

---

## 📦 Installation & Setup

### Prerequisites
- **Python 3.8+**
- **pip** (Python package installer)

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/saberabanu0001/NewCalmateAI.git
cd NewCalmateAI
Step 2: Create a Virtual Environment
python3 -m venv venv

Step 3: Activate the Virtual Environment

macOS / Linux

source venv/bin/activate


Windows

venv\Scripts\activate

Step 4: Install Dependencies
pip install -r requirements.txt

Step 5: Configure Environment Variables

Create a .env file in the root directory and add:

FLASK_SECRET_KEY='your_secret_key'
GROQ_API_KEY='your_groq_api_key'
GEMINI_API_KEY='your_gemini_api_key'

Step 6: Run the Application
flask run


Now, open your browser and go to:
👉 http://127.0.0.1:5000/

👩‍💻 Author

Sabera Banu – Initial development and design of CalmMateAI 💡

✨ CalmMateAI is built with love, empathy, and the mission of supporting mental well-being through technology.
