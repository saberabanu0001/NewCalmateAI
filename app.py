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
# --- Helpers ---
def contains_any_word(text: str, keywords: list[str]) -> bool:
    """Return True if any keyword is present as a whole word in text."""
    for kw in keywords:
        pattern = rf"\\b{re.escape(kw.lower())}\\b"
        if re.search(pattern, text):
            return True
    return False

def generate_contextual_response(user_message_lower: str) -> str:
    """Keyword-based compassionate responses when LLM is unavailable."""
    if contains_any_word(user_message_lower, ['anxious', 'anxiety', 'worried', 'nervous']):
        return ("I can hear that you're feeling anxious right now, and that's completely understandable. "
                "Would you like to try a short grounding exercise with me, or talk about what's triggering it?")
    if contains_any_word(user_message_lower, ['sad', 'depressed', 'down', 'lonely']):
        return ("I'm so sorry you're feeling this way. Your feelings are valid. "
                "If you'd like, tell me a bit more about what's been hardest lately.")
    if contains_any_word(user_message_lower, ['stressed', 'stress', 'overwhelmed']):
        return ("Stress can feel heavy. Let's break it down into smaller steps. "
                "What's the one thing we can focus on for the next 15 minutes?")
    if contains_any_word(user_message_lower, ['angry', 'anger', 'frustrated', 'mad', 'irritated']):
        return ("Feeling angry is okay—it's a signal something matters to you. "
                "Try the 4-7-8 breath (inhale 4, hold 7, exhale 8) for 4 rounds, then we can list the top 1-2 triggers together.")
    if contains_any_word(user_message_lower, ['calm', 'calming', 'cope', 'coping', 'relax', 'relaxation', 'strategy', 'strategies']):
        return ("Here are a few calming ideas: 1) 4-7-8 breathing ×4 rounds, 2) a 2-minute cold water splash on wrists, "
                "3) write down the worry and one small next step. Which would you like to try?")
    if contains_any_word(user_message_lower, ['sleep', 'tired', 'insomnia', 'restless']):
        return ("Sleep struggles are tough. A quick tip: dim lights and slow, deep breathing for 2 minutes. "
                "Would you like a short wind-down routine?")
    if contains_any_word(user_message_lower, ['relationship', 'partner', 'boyfriend', 'girlfriend', 'marriage']):
        return ("Relationships can be deeply tender and challenging. "
                "Do you want to unpack what happened, or explore how you'd like to feel in this situation?")
    if (contains_any_word(user_message_lower, ['periods', 'menstrual', 'cramps', 'pms']) and
        not contains_any_word(user_message_lower, ['headache', 'migraine'])):
        return ("I'm so sorry you're experiencing period pain. A heating pad and gentle stretching can help. "
                "If pain is severe or disruptive, consider reaching out to a healthcare provider—there are treatments that help.")
    if (contains_any_word(user_message_lower, ['headache', 'migraine']) and
        not contains_any_word(user_message_lower, ['periods', 'menstrual'])):
        return ("Headaches can be draining. Try resting in a dim room, hydrate, and slow breathing. "
                "If it's severe or persistent, consider checking with a healthcare provider.")
    if contains_any_word(user_message_lower, ['die', 'suicide', 'kill myself', 'end it all', 'want to die']):
        return ("I'm so sorry you're feeling this way. You matter. Please reach out for immediate help: call 988 or "
                "text HOME to 741741. If you can, let someone nearby know how you're feeling right now.")
    # Place greeting last and with whole-word matching to avoid matching 'hi' in 'this'
    if contains_any_word(user_message_lower, ['hi', 'hello', 'hey']):
        return ("Hello! I'm so glad you're here. How are you feeling today? I'm ready to listen and support you.")
    return ("I'm here to listen and support you. I can sense that you're going through something important. "
            "Would you like to share a bit more so we can figure out a next small step together?")

# --- Routes for HTML pages ---
@app.route('/')
def home():
    """Redirect to register page."""
    return redirect(url_for('register_page'))

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
    if not email or not name or not password:
        return jsonify({'success': False, 'message': 'Name, email, and password are required.'}), 400
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
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login_page'))
    user_name = get_user_name(user_email)
    return render_template('chat_page.html', user_name=user_name)

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

@app.route('/logout')
def logout():
    """Logout user and clear session."""
    session.clear()
    return redirect(url_for('register_page'))

# --- API Routes ---
@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple test endpoint to verify API is working."""
    return jsonify({'status': 'API is working', 'message': 'Hello from CalmMateAI API!'})

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """
    Handles chat messages, determines seriousness, and provides AI response.
    """
    try:
        data = request.get_json()
        user_message = data.get('message') or data.get('user_input')
        history = data.get('history', [])
        
        # --- LLM Integration ---
        # The prompt for the LLM
        prompt = f"""
        You are CalmMateAI, a compassionate and empathetic mental well-being assistant. Your role is to provide supportive, personalized, and helpful responses to users who are seeking emotional support.

        User's message: "{user_message}"

        IMPORTANT: If the user mentions any of these specific topics, provide targeted responses:

        - PERIOD PAIN/MENSTRUAL ISSUES: "I'm so sorry you're experiencing period pain. This can be incredibly difficult and debilitating. Have you tried using a heating pad, taking a warm bath, or gentle stretching? If the pain is severe or interfering with your daily activities, please consider reaching out to a healthcare provider - there are treatments that can help. You're not alone in this, and your pain is valid."

        - SUICIDE/CRISIS: "I'm so sorry you're feeling this way, and I want you to know that you're not alone. These feelings are incredibly serious, and I need you to reach out for immediate help. Please call the National Suicide Prevention Lifeline at 988 or 1-800-273-8255 right now, or text HOME to 741741. You matter, and there are people who want to help you through this."

        - ANXIETY: "I can hear that you're feeling anxious right now, and that's completely understandable. Anxiety can feel overwhelming, but remember that these feelings are temporary. Would you like to try some deep breathing exercises together, or would you prefer to talk more about what's causing your anxiety?"

        - SADNESS/DEPRESSION: "I'm so sorry you're feeling sad and lonely. It takes courage to reach out when you're feeling this way. You're not alone in this, and your feelings are completely valid. Have you been able to talk to anyone close to you about how you're feeling?"

        For all other messages, provide a warm, empathetic, and contextual response that:
        1. Acknowledges their specific feelings and situation
        2. Shows genuine understanding and empathy
        3. Offers practical, supportive advice when appropriate
        4. Encourages them to seek professional help if needed
        5. Uses a warm, conversational tone
        6. Avoids generic responses - be specific to their situation

        Keep your response conversational and not too long (2-4 sentences). Be supportive but not overly clinical.
        """

        # Check for API key first
        api_key = os.getenv("GROQ_API_KEY") # Using Groq API key
        
        # Use contextual fallback responses when API key is not configured
        user_message_lower = user_message.lower()
        
        # Treat placeholder keys as not configured
        if (not api_key) or ("your_groq_api_key" in api_key.lower()) or (api_key.lower().startswith("your_")):
            ai_response = generate_contextual_response(user_message_lower)
        else:
            # Use Groq API
            api_url = "https://api.groq.com/openai/v1/chat/completions"
            
            payload = {
                "model": "llama3-70b-8192",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            try:
                            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
                            response.raise_for_status() # Raise an exception for bad status codes
                            result = response.json()
                            ai_response = result['choices'][0]['message']['content']
            except Exception as _e:
                # Fall back to contextual responses if API call fails
                ai_response = generate_contextual_response(user_message_lower)

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
        import traceback
        traceback.print_exc()
        # Return a fallback response instead of an error
        return jsonify({
            'ai_response': "I'm here to listen and support you. While I'm having some technical difficulties right now, please know that your feelings are valid and important. If you're in crisis, please reach out to a mental health professional or call a crisis hotline.",
            'seriousness_level': 'Medium',
            'suggestions': 'Consider talking to a trusted friend, family member, or mental health professional. Practice self-care activities like deep breathing, meditation, or going for a walk.'
        }), 200

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
        if seriousness_level == "Emergency": return jsonify({'error': 'Failed to retrieve contacts.', 'details': str(e)}), 500

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
        if seriousness_level == "Emergency": return jsonify({'error': 'Failed to retrieve university resources.', 'details': str(e)}), 500

if __name__ == '__main__':
    # Get the port from the environment, defaulting to 5001
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
