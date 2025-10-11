# emergency_contacts.py

import json
import os
import re

# Define the path to the data file
DATA_FILE = os.path.join(os.path.dirname(__file__), 'emergency_data.json')

# Load the data once when the module is imported
try:
    with open(DATA_FILE, 'r') as f:
        EMERGENCY_DATA = json.load(f)
except FileNotFoundError:
    print(f"Error: The data file '{DATA_FILE}' was not found.")
    EMERGENCY_DATA = {}
except json.JSONDecodeError as e:
    print(f"Error parsing JSON data: {e}")
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
    Supports fuzzy matching for country and city names.
    
    Args:
        country (str): The country name.
        city (str): The city name.
        category (str): The category ("helplines", "doctors", "domestic_violence", "substance_abuse").
        
    Returns:
        list: A list of dictionaries containing contact info. Returns an empty list if not found.
    """
    if not country or not city or not category:
        return []
    
    # Normalize inputs
    country = country.strip().title()
    city = city.strip().title()
    category = category.strip().lower()
    
    # Direct lookup first
    country_data = EMERGENCY_DATA.get(country, {})
    if country_data:
        city_data = country_data.get(city, {})
        if city_data and category in city_data:
            return city_data[category]
    
    # Fuzzy matching for country
    for available_country in EMERGENCY_DATA.keys():
        if (country.lower() in available_country.lower() or 
            available_country.lower() in country.lower()):
            country_data = EMERGENCY_DATA[available_country]
            # Fuzzy matching for city
            for available_city in country_data.keys():
                if (city.lower() in available_city.lower() or 
                    available_city.lower() in city.lower()):
                    city_data = country_data[available_city]
                    if category in city_data:
                        return city_data[category]
    
    return []

def search_emergency_contacts(query, category=None):
    """
    Search for emergency contacts across all locations using a query string.
    
    Args:
        query (str): Search query (can be country, city, or organization name).
        category (str, optional): Filter by specific category.
        
    Returns:
        list: A list of dictionaries containing contact info with location context.
    """
    if not query:
        return []
    
    query = query.strip().lower()
    results = []
    
    for country, cities in EMERGENCY_DATA.items():
        for city, categories in cities.items():
            for cat, contacts in categories.items():
                if category and cat != category:
                    continue
                    
                for contact in contacts:
                    # Search in contact name, number, or location
                    searchable_text = f"{contact.get('name', '')} {contact.get('number', '')} {country} {city}".lower()
                    if query in searchable_text:
                        contact_with_location = contact.copy()
                        contact_with_location['location'] = f"{city}, {country}"
                        contact_with_location['category'] = cat
                        results.append(contact_with_location)
    
    return results

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
        return f"❌ No emergency contacts found for {location}.\n\n💡 Try searching for a nearby major city or check the global crisis hotlines below."
    
    # Group contacts by category
    categories = {}
    for contact in contacts:
        cat = contact.get('category', 'helplines')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(contact)
    
    formatted_text = f"## 🆘 Emergency Contacts for {location}\n\n"
    
    # Category icons and names
    category_info = {
        'helplines': ('📞', 'Crisis Hotlines'),
        'doctors': ('🏥', 'Mental Health Professionals'),
        'domestic_violence': ('🛡️', 'Domestic Violence Support'),
        'substance_abuse': ('💊', 'Substance Abuse Support')
    }
    
    for cat, contact_list in categories.items():
        icon, display_name = category_info.get(cat, ('📋', cat.replace('_', ' ').title()))
        formatted_text += f"### {icon} {display_name}\n\n"
        
        for contact in contact_list:
            name = contact.get('name', 'N/A')
            number = contact.get('number', 'N/A')
            url = contact.get('url', None)
            location_info = contact.get('location', '')
            
            formatted_text += f"**{name}**"
            if location_info and location_info != location:
                formatted_text += f" *({location_info})*"
            formatted_text += "\n"
            
            if number != 'N/A':
                # Make phone numbers clickable
                if number.startswith(('+', '1-', '0')):
                    formatted_text += f"- 📞 **Phone:** `{number}`\n"
                else:
                    formatted_text += f"- 📞 **Phone:** `{number}`\n"
            
            if url:
                formatted_text += f"- 🌐 **Website:** [{url}]({url})\n"
            
            formatted_text += "\n"
    
    # Add global crisis resources
    formatted_text += "---\n\n"
    formatted_text += "## 🌍 Global Crisis Resources\n\n"
    formatted_text += "**International Association for Suicide Prevention:** [iasp.info](https://www.iasp.info/resources/Crisis_Centres/)\n\n"
    formatted_text += "**Befrienders Worldwide:** [befrienders.org](https://www.befrienders.org/)\n\n"
    
    return formatted_text

# You'll also need the emergency_data.json file.
# We'll create a sample version for you.
