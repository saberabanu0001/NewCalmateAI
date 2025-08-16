# emergency_contacts.py

import json
import os

# Define the path to the data file
DATA_FILE = os.path.join(os.path.dirname(__file__), 'emergency_data.json')

# Load the data once when the module is imported
try:
    with open(DATA_FILE, 'r') as f:
        EMERGENCY_DATA = json.load(f)
except FileNotFoundError:
    print(f"Error: The data file '{DATA_FILE}' was not found.")
    EMERGENCY_DATA = {}

def get_available_countries():
    """Returns a list of all countries available in the data."""
    return sorted(list(EMERGENCY_DATA.keys()))

def get_cities_for_country(country_name):
    """Returns a list of cities for a given country."""
    if country_name in EMERGENCY_DATA:
        return sorted(list(EMERGENCY_DATA[country_name].keys()))
    return []

def get_emergency_info_by_location(country, city, category):
    """
    Retrieves emergency contact information for a specific country, city, and category.
    
    Args:
        country (str): The country name.
        city (str): The city name.
        category (str): The category ("helplines" or "doctors").
        
    Returns:
        list: A list of dictionaries containing contact info. Returns an empty list if not found.
    """
    country_data = EMERGENCY_DATA.get(country, {})
    city_data = country_data.get(city, {})
    return city_data.get(category, [])

def format_contacts_for_display(contacts, location):
    """
    Formats a list of contact dictionaries into a Markdown string for display.
    
    Args:
        contacts (list): A list of contact dictionaries.
        location (str): A string representing the location (e.g., "Seoul, South Korea").
        
    Returns:
        str: A Markdown-formatted string.
    """
    if not contacts:
        return f"No information found for {location}."
    
    formatted_text = f"### Emergency Contacts for {location}\n\n"
    for contact in contacts:
        name = contact.get('name', 'N/A')
        number = contact.get('number', 'N/A')
        url = contact.get('url', None)
        
        formatted_text += f"**{name}**\n"
        if number != 'N/A':
            formatted_text += f"- Phone: `{number}`\n"
        if url:
            formatted_text += f"- Website: <{url}>\n"
        formatted_text += "\n"
        
    return formatted_text

# You'll also need the emergency_data.json file.
# We'll create a sample version for you.
