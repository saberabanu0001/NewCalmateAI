# university_auth.py

import json
import os

# Define the paths to the data files
UNIVERSITY_DATA_FILE = os.path.join(os.path.dirname(__file__), 'university_data.json')
UNIVERSITY_STUDENTS_FILE = os.path.join(os.path.dirname(__file__), 'university_students.json')

# Load the data once when the module is imported
try:
    with open(UNIVERSITY_DATA_FILE, 'r') as f:
        UNIVERSITY_RESOURCES = json.load(f)
    with open(UNIVERSITY_STUDENTS_FILE, 'r') as f:
        UNIVERSITY_STUDENTS = json.load(f)
except FileNotFoundError as e:
    print(f"Error: A university data file was not found. Please create {e.filename}")
    UNIVERSITY_RESOURCES = {}
    UNIVERSITY_STUDENTS = {}

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
    return UNIVERSITY_RESOURCES.get(university_name, {})
