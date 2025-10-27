# university_auth.py

import json
import os

# Define the paths to the data files
UNIVERSITY_DATA_FILE = os.path.join(os.path.dirname(__file__), 'university_data.json')
UNIVERSITY_STUDENTS_FILE = os.path.join(os.path.dirname(__file__), 'university_students.json')

# Load the data once when the module is imported
def load_university_data():
    """Load university data from JSON files."""
    try:
        with open(UNIVERSITY_DATA_FILE, 'r') as f:
            university_resources = json.load(f)
        with open(UNIVERSITY_STUDENTS_FILE, 'r') as f:
            university_students = json.load(f)
        return university_resources, university_students
    except FileNotFoundError as e:
        print(f"Error: A university data file was not found. Please create {e.filename}")
        return {}, {}

# Load initial data
UNIVERSITY_RESOURCES, UNIVERSITY_STUDENTS = load_university_data()

def authenticate_student(university_name, student_id, password):
    """
    Authenticates a student against the mock student data.
    
    Args:
        university_name (str): The name of the university.
        student_id (str): The student's ID.
        password (str): The password.
        
    Returns:
        tuple: (success (bool), message (str))
    """
    if university_name not in UNIVERSITY_STUDENTS:
        return False, "University not found."
    
    students = UNIVERSITY_STUDENTS[university_name].get("students", {})
    if student_id not in students:
        return False, "Invalid Student ID."
        
    student_info = students[student_id]
    if student_info['password'] == password:
        return True, "Authentication successful."
    else:
        return False, "Invalid password."

def get_university_resources(university_name):
    """
    Retrieves resources for a given university.
    
    Args:
        university_name (str): The name of the university.
        
    Returns:
        dict: A dictionary of resources. Returns an empty dict if not found.
    """
    # Reload data to get latest changes
    university_resources, _ = load_university_data()
    return university_resources.get(university_name, {})
