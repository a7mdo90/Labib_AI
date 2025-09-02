# log_reader.py

import csv

LOG_FILE = "student_logs.csv"

def get_user_history(phone_number, limit=5):
    """Return the most recent N questions/answers by a given phone number."""
    rows = []
    try:
        with open(LOG_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 6 and phone_number in row[5]:
                    rows.append(row)
        return rows[-limit:]  # return last N entries
    except FileNotFoundError:
        return []

def find_similar_questions(keyword, limit=5):
    """Return questions that include a given keyword."""
    matches = []
    try:
        with open(LOG_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4 and keyword in row[3]:
                    matches.append((row[3], row[4]))  # (question, answer)
        return matches[-limit:]
    except FileNotFoundError:
        return []
