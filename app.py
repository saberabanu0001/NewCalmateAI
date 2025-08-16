import os
import re
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Custom modules
from seriousness_detector import get_seriousness_level
from suggestions_manager import get_recovery_suggestions, format_suggestions
from emergency_contacts import get_emergency_info_by_location, format_contacts_for_display
from university_auth import authenticate_student, get_university_resources
from voice_input import recognize_speech_from_audio

# Load environment variables
load_dotenv()

# Set up the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize LangChain and Groq
try:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is not set in the .env file.")
    llm = ChatGroq(model="mixtral-8x7b-32768", groq_api_key=groq_api_key)
except ValueError as e:
    llm = None
    print(f"Error initializing LLM: {e}. AI chat functionality will be disabled.")

# --- LangChain Core Setup ---
prompt_template = PromptTemplate.from_template(
    """
You are a compassionate and empathetic AI named CalmMateAI. Your purpose is to provide emotional support and guidance. Acknowledge the user's feelings and respond with empathy. Avoid giving professional medical advice. Instead, gently guide the user towards seeking professional help if their issues are serious.

User's emotional state (for context): {seriousness_level}
User: {user_input}
CalmMateAI:
"""
)
output_parser = StrOutputParser()
chain = prompt_template | llm | output_parser

@app.route('/')
def index():
    """Renders the initial login page."""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Renders the main dashboard page."""
    user_name = session.get('user_name')
    if not user_name:
        return redirect(url_for('index'))
    return render_template('dashboard.html', user_name=user_name)

@app.route('/login', methods=['POST'])
def login():
    """Handles the user login via name and email."""
    data = request.get_json()
    user_name = data.get('name')
    user_email = data.get('email')

    if user_name and user_email:
        session['user_name'] = user_name
        return jsonify({"success": True, "redirect_url": url_for('dashboard')})
    else:
        return jsonify({"success": False, "message": "Name and email are required."}), 400

@app.route('/chat', methods=['POST'])
def chat():
    """Handles the chat interaction with the AI."""
    user_input = request.json.get('user_input')
    
    if not llm:
        return jsonify({'response': 'AI chat is currently unavailable due to a configuration error.'})

    if not user_input:
        return jsonify({'response': 'Please enter a message.'})

    # Detect seriousness level
    seriousness_level = get_seriousness_level(user_input, chain)
    
    # Generate AI response based on seriousness
    if seriousness_level == 'Emergency':
        ai_response = "This is an emergency. Please contact your local emergency services or a crisis hotline immediately."
    else:
        ai_response = chain.invoke({'seriousness_level': seriousness_level, 'user_input': user_input})
        
    # Get and format suggestions
    suggestions = get_recovery_suggestions(seriousness_level)
    formatted_suggestions = format_suggestions(suggestions)
    
    response_data = {
        "response": ai_response,
        "suggestions": formatted_suggestions,
        "seriousness_level": seriousness_level
    }
    
    return jsonify(response_data)

@app.route('/university_auth', methods=['POST'])
def university_auth():
    """Handles student authentication and resource retrieval."""
    data = request.get_json()
    university = data.get('university_name')
    student_id = data.get('student_id')
    password = data.get('password')

    success, message = authenticate_student(university, student_id, password)
    
    if success:
        resources = get_university_resources(university)
        return jsonify({"success": True, "message": message, "resources": resources})
    else:
        return jsonify({"success": False, "message": message})

@app.route('/emergency_contacts', methods=['POST'])
def emergency_contacts():
    """Retrieves and formats emergency contact information."""
    data = request.get_json()
    country = data.get('country')
    city = data.get('city')
    category = data.get('category')
    
    contacts = get_emergency_info_by_location(country, city, category)
    formatted_contacts = format_contacts_for_display(contacts, f"{city}, {country}")
    
    return jsonify({"contacts": formatted_contacts})

@app.route('/upload_voice', methods=['POST'])
def upload_voice():
    """Handles voice input, saves it, and transcribes it."""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Transcribe the audio file
        transcribed_text = recognize_speech_from_audio(filepath)
        
        # Clean up the file after transcription
        os.remove(filepath)
        
        return jsonify({'transcribed_text': transcribed_text})

if __name__ == '__main__':
    # Get the port from the environment, defaulting to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
