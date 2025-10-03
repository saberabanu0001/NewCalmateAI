# seriousness_detector.py

import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq

# Ensure NLTK data is downloaded
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    print("Downloading NLTK VADER lexicon...")
    nltk.download('vader_lexicon')

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def get_seriousness_level(user_input, qa_chain_for_llm_check):
    """
    Analyzes the user's message to determine a seriousness level.
    Uses keyword matching, sentiment analysis, and a final LLM check.
    
    Args:
        user_input (str): The text message from the user.
        qa_chain_for_llm_check (LLMChain): A pre-initialized LangChain LLMChain object for the LLM check.

    Returns:
        str: The seriousness level ("Low", "Medium", "High", or "Emergency").
    """
    
    # --- Keyword and Pattern Matching (Rule-based) ---
    emergency_keywords = re.compile(
        r'\b(suicide|kill myself|end my life|die|self-harm|harm myself|cutting|overdose|in danger|i need help now)\b',
        re.IGNORECASE
    )
    high_keywords = re.compile(
        r'\b(hopeless|worthless|can\'t go on|give up|no purpose|can\'t take it anymore|lost|alone|trapped|scared|crisis|panic attack|anxious|depressed|depression|extreme pain|severe pain|unbearable pain|debilitating pain)\b',
        re.IGNORECASE
    )
    medium_keywords = re.compile(
        r'\b(stress|stressed|anxious|anxiety|sad|unhappy|tired|overwhelmed|struggling|bad day|tough time|feeling down)\b',
        re.IGNORECASE
    )

    if emergency_keywords.search(user_input):
        return "Emergency"
    if high_keywords.search(user_input):
        return "High"
    
    # --- Sentiment Analysis (Nuance-based) ---
    # We only run this if the keywords didn't trigger a High or Emergency level
    sentiment = analyzer.polarity_scores(user_input)
    compound_score = sentiment['compound']
    
    # If the compound sentiment score is very negative, it might be a medium level
    if compound_score <= -0.5:
        return "Medium"
    
    # --- LLM-based Nuance Check ---
    # For a more nuanced check, we can ask the LLM for its opinion.
    # This is useful for detecting subtle signs not caught by keywords/sentiment alone.
    if compound_score < 0: # Only check if sentiment is slightly negative
        if qa_chain_for_llm_check is not None:
            llm_check_prompt = PromptTemplate.from_template(
                "The user said: '{user_input}'. "
                "Based on this, is their emotional state a 'Low' or 'Medium' level? "
                "Respond with only 'Low' or 'Medium'."
            )

            try:
                # We need a temporary chain to invoke this specific prompt
                llm_check_chain = LLMChain(llm=qa_chain_for_llm_check.llm, prompt=llm_check_prompt)
                llm_response_obj = llm_check_chain.invoke({"user_input": user_input})
                # Handle both old and new LangChain response formats
                if hasattr(llm_response_obj, 'get'):
                    llm_response = llm_response_obj.get('text', '').strip().lower()
                else:
                    llm_response = str(llm_response_obj).strip().lower()

                if "medium" in llm_response:
                    return "Medium"
            except Exception as e:
                print(f"Error during seriousness check LLM invocation: {e}")
                # Fallback to keyword/sentiment if LLM check fails
                if medium_keywords.search(user_input):
                    return "Medium"
        else:
            # If no LLM is available, fall back to rule-based medium detection
            if medium_keywords.search(user_input):
                return "Medium"

    # --- Default Level ---
    # If none of the above conditions are met, default to 'Low'
    return "Low"
