# voice_input.py

import os
import speech_recognition as sr
from pydub import AudioSegment

def recognize_speech_from_audio(audio_file_path):
    """
    Transcribes speech from an audio file using Google Web Speech API.
    
    Args:
        audio_file_path (str): The file path to the audio file.
    
    Returns:
        str: The transcribed text, or an error message.
    """
    r = sr.Recognizer()
    
    try:
        # Convert audio file to a format compatible with SpeechRecognition (e.g., WAV)
        # This is important for handling various input formats like .mp3, .ogg, etc.
        audio = AudioSegment.from_file(audio_file_path)
        wav_audio_path = "temp_audio.wav"
        audio.export(wav_audio_path, format="wav")

        with sr.AudioFile(wav_audio_path) as source:
            audio_data = r.record(source)  # Read the entire audio file
            
            # Use Google's Speech Recognition API
            text = r.recognize_google(audio_data, language="en-US")
            
            # Clean up the temporary file
            os.remove(wav_audio_path)
            
            return text
            
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"
    except Exception as e:
        return f"An error occurred during speech recognition: {e}"

# Note: The Flask app would need to save the uploaded audio file to a temporary location
# before calling this function with the path to that temporary file.
