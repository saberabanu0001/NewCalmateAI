# suggestions_manager.py

import textwrap

# Dictionary of suggestions based on seriousness level
SUGGESTIONS = {
    "Low": [
        "Take a short walk or stretch.",
        "Practice a few minutes of deep breathing.",
        "Try a 5-minute meditation.",
        "Listen to some calming music.",
        "Connect with a friend or family member."
    ],
    "Medium": [
        "Jot down your thoughts in a journal.",
        "Distract yourself with a hobby you enjoy.",
        "Limit social media and news consumption.",
        "Remember to stay hydrated and eat well.",
        "Consider scheduling a time to talk with a professional."
    ],
    "High": [
        "Reach out to a trusted friend or family member immediately.",
        "Contact a local crisis hotline or helpline.",
        "Consider visiting an emergency room or walk-in clinic if you feel unsafe.",
        "Focus on one thing in your immediate surroundings to ground yourself.",
        "Remember this feeling will pass. You are not alone."
    ],
    "Emergency": [
        "Call your local emergency services immediately.",
        "Go to the nearest emergency room.",
        "Reach out to a crisis hotline or text line right now."
    ]
}

def get_recovery_suggestions(seriousness_level):
    """
    Retrieves a list of suggestions for a given seriousness level.
    
    Args:
        seriousness_level (str): The seriousness level ("Low", "Medium", "High", "Emergency").
        
    Returns:
        list: A list of string suggestions.
    """
    return SUGGESTIONS.get(seriousness_level, [])

def format_suggestions(suggestions_list):
    """
    Formats a list of suggestions into a Markdown string.
    
    Args:
        suggestions_list (list): A list of strings.
        
    Returns:
        str: A Markdown-formatted string with a header and bullet points.
    """
    if not suggestions_list:
        return "No specific suggestions at this time. Just breathe."
    
    formatted_text = "**What to do right now:**\n\n"
    for item in suggestions_list:
        formatted_text += f"- {item}\n"
        
    return formatted_text

# Example of use:
if __name__ == "__main__":
    low_suggestions = get_recovery_suggestions("Low")
    print(format_suggestions(low_suggestions))
    
    medium_suggestions = get_recovery_suggestions("Medium")
    print(format_suggestions(medium_suggestions))
