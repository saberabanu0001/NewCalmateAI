# app.py
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
import requests # Import the requests library

# Custom modules
from seriousness_detector import get_seriousness_level
from suggestions_manager import get_recovery_suggestions, format_suggestions
from emergency_contacts import get_emergency_info_by_location, format_contacts_for_display
from university_auth import authenticate_student, get_university_resources
from voice_input import recognize_speech_from_audio

# Simple user storage (in production, use a proper database)
def get_registered_users():
    """Get list of registered users."""
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_user_name(email):
    """Get user name by email."""
    users = get_registered_users()
    return users.get(email, {}).get('name', 'User')

def save_user(email, name, password):
    """Save new user registration."""
    users = get_registered_users()
    users[email] = {'name': name, 'password': password}  # In production, hash the password
    with open('users.json', 'w') as f:
        json.dump(users, f)

# Load environment variables
load_dotenv()

# Set up the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# --- Routes for HTML pages ---
@app.route('/')
def home():
    """Redirect to login page."""
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    """Render the login page."""
    return render_template('login.html')

@app.route('/login_submit', methods=['POST'])
def login_submit():
    """Handle login form submission."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    users = get_registered_users()
    if email in users and users[email]['password'] == password:
        session['user_email'] = email
        return jsonify({'success': True, 'redirect_url': url_for('dashboard')})
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'})

@app.route('/register')
def register_page():
    """Render the registration page."""
    return render_template('register.html')

@app.route('/register_submit', methods=['POST'])
def register_submit():
    """Handle registration form submission."""
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    users = get_registered_users()
    if email in users:
        return jsonify({'success': False, 'message': 'Email already registered'})
    save_user(email, name, password)
    return jsonify({'success': True, 'message': 'Registration successful!', 'redirect_url': url_for('login_page')})

@app.route('/dashboard')
def dashboard():
    """Render the dashboard page."""
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login_page'))
    user_name = get_user_name(user_email)
    return render_template('dashboard.html', user_name=user_name)

@app.route('/chat')
def chat():
    """Render the chat page."""
    return render_template('chat_page.html')

@app.route('/emergency_contacts')
def emergency_contacts():
    """Render the emergency contacts page."""
    return render_template('emergency_contacts.html')

@app.route('/university_access')
def university_access():
    """Render the university access page."""
    return render_template('university_access.html')

@app.route('/wellbeing_resources')
def wellbeing_resources():
    """Render the wellbeing resources page."""
    return render_template('wellbeing_resources.html')

# --- API Routes ---
@app.route('/api/chat', methods=['POST'])
def chat_api():
    """
    Handles chat messages, determines seriousness, and provides AI response.
    """
    try:
        data = request.get_json()
        user_message = data.get('message')
        history = data.get('history', [])
        
        # --- LLM Integration ---
        # The prompt for the LLM
        prompt = f"""
        You are a kind, empathetic, and professional mental well-being assistant named CalmMateAI. Your goal is to provide supportive and helpful responses to users.

        Here is the user's message: "{user_message}"

        Please provide a response that is supportive and encouraging, based on the user's input.
        """

        # API call to Gemini
        api_key = os.getenv("GEMINI_API_KEY") # You will need to add this to your .env file
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an exception for bad status codes
        
        result = response.json()
        
        ai_response = result['candidates'][0]['content']['parts'][0]['text']

        # Get seriousness level and suggestions using the imported modules
        seriousness_level = get_seriousness_level(user_message, qa_chain_for_llm_check=None)
        suggestions_list = get_recovery_suggestions(seriousness_level)
        formatted_suggestions = format_suggestions(suggestions_list)
        
        return jsonify({
            'ai_response': ai_response,
            'seriousness_level': seriousness_level,
            'suggestions': formatted_suggestions
        })
    except Exception as e:
        print(f"Error processing chat message: {e}")
        return jsonify({'error': 'Failed to get AI response.', 'details': str(e)}), 500

@app.route('/api/contacts', methods=['POST'])
def contacts_api():
    """
    API endpoint to retrieve emergency contact information.
    """
    try:
        data = request.get_json()
        country = data.get('country')
        city = data.get('city')
        category = data.get('category')
        
        # Get the contacts using the imported module
        contacts = get_emergency_info_by_location(country, city, category)
        
        # Format the contacts into a markdown string for display
        formatted_contacts_markdown = format_contacts_for_display(contacts, f"{city}, {country}")
        
        return jsonify({
            'contacts_markdown': formatted_contacts_markdown
        })
    except Exception as e:
        print(f"Error in contacts_api: {e}")
        return jsonify({'error': 'Failed to retrieve contacts.', 'details': str(e)}), 500

@app.route('/api/university_resources', methods=['POST'])
def university_resources_api():
    """
    API endpoint to retrieve university-specific resources.
    """
    try:
        data = request.get_json()
        university_name = data.get('university_name')
        
        resources = get_university_resources(university_name)
        
        if not resources:
            return jsonify({'error': 'University not found or no resources available.'}), 404
            
        return jsonify({'resources': resources})
    except Exception as e:
        print(f"Error in university_resources_api: {e}")
        return jsonify({'error': 'Failed to retrieve university resources.', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
