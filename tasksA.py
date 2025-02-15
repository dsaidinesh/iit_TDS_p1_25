# tasksA.py
# Collection of data processing and manipulation functions for various file formats and operations

# Import required libraries
import sqlite3
import subprocess
from dateutil.parser import parse
from datetime import datetime
import json
from pathlib import Path
import os
import requests
from scipy.spatial.distance import cosine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API token from environment variables
AIPROXY_TOKEN = os.getenv('AIPROXY_TOKEN')

def generate_data(email="22f1000913@ds.study.iitm.ac.in"):
    """
    Generate data by running a Python script from a URL with an email parameter
    Args:
        email (str): Email address to be used for data generation
    Returns:
        str: Output from the script execution
    """
    try:
        process = subprocess.Popen(
            ["uv", "run", "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py", email],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Error: {stderr}")
        return stdout
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error: {e.stderr}")

def format_markdown(prettier_version="prettier@3.4.2", filename="/data/format.md"):
    """
    Format a markdown file using Prettier
    Args:
        prettier_version (str): Version of Prettier to use
        filename (str): Path to the markdown file
    """
    command = [r"C:\Program Files\nodejs\npx.cmd", prettier_version, "--write", filename]
    try:
        subprocess.run(command, check=True)
        print("Prettier executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def count_weekday_dates(filename='/data/dates.txt', targetfile='/data/dates-wednesdays.txt', weekday=2):
    """
    Count occurrences of a specific weekday in a file containing dates
    Args:
        filename (str): Input file containing dates
        targetfile (str): Output file to write the count
        weekday (int): Day of week to count (1=Monday, 7=Sunday)
    """
    input_file = filename
    output_file = targetfile
    weekday_count = 0

    with open(input_file, 'r') as file:
        weekday_count = sum(1 for date in file if parse(date).weekday() == int(weekday)-1)

    with open(output_file, 'w') as file:
        file.write(str(weekday_count))

def sort_contacts(filename="/data/contacts.json", targetfile="/data/contacts-sorted.json"):
    """
    Sort contacts in a JSON file by last name and first name
    Args:
        filename (str): Input JSON file containing contacts
        targetfile (str): Output file for sorted contacts
    """
    with open(filename, 'r') as file:
        contacts = json.load(file)

    sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))

    with open(targetfile, 'w') as file:
        json.dump(sorted_contacts, file, indent=4)

def get_recent_logs(log_dir_path='/data/logs', output_file_path='/data/logs-recent.txt', num_files=10):
    """
    Get first lines from most recent log files
    Args:
        log_dir_path (str): Directory containing log files
        output_file_path (str): Output file to write the first lines
        num_files (int): Number of most recent files to process
    """
    log_dir = Path(log_dir_path)
    output_file = Path(output_file_path)

    log_files = sorted(log_dir.glob('*.log'), key=os.path.getmtime, reverse=True)[:num_files]

    with output_file.open('w') as f_out:
        for log_file in log_files:
            with log_file.open('r') as f_in:
                first_line = f_in.readline().strip()
                f_out.write(f"{first_line}\n")

def create_docs_index(doc_dir_path='/data/docs', output_file_path='/data/docs/index.json'):
    """
    Create an index of markdown documents with their titles
    Args:
        doc_dir_path (str): Directory containing markdown files
        output_file_path (str): Output JSON file for the index
    """
    docs_dir = doc_dir_path
    output_file = output_file_path
    index_data = {}

    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('# '):
                            title = line[2:].strip()
                            relative_path = os.path.relpath(file_path, docs_dir).replace('\\', '/')
                            index_data[relative_path] = title
                            break

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=4)

def extract_email_sender(filename='/data/email.txt', output_file='/data/email-sender.txt'):
    """
    Extract sender's email address from an email file
    Args:
        filename (str): Input email file
        output_file (str): Output file to write the sender's email
    """
    with open(filename, 'r') as file:
        email_content = file.readlines()

    sender_email = "sujay@gmail.com"
    for line in email_content:
        if "From" == line[:4]:
            sender_email = (line.strip().split(" ")[-1]).replace("<", "").replace(">", "")
            break

    with open(output_file, 'w') as file:
        file.write(sender_email)

import base64
def png_to_base64(image_path):
    """
    Convert PNG image to base64 string
    Args:
        image_path (str): Path to the PNG image
    Returns:
        str: Base64 encoded string of the image
    """
    with open(image_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode('utf-8')
    return base64_string

def process_credit_card(filename='/data/credit_card.txt', image_path='/data/credit_card.png'):
    """
    Extract credit card number from an image using AI
    Args:
        filename (str): Output file to write the card number
        image_path (str): Input image containing credit card details
    """
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "There is 8 or more digit number is there in this image, with space after every 4 digit, only extract the those digit number without spaces and return just the number without any other characters"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{png_to_base64(image_path)}"
                        }
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }

    response = requests.post("http://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
                             headers=headers, data=json.dumps(body))
    result = response.json()
    card_number = result['choices'][0]['message']['content'].replace(" ", "")

    with open(filename, 'w') as file:
        file.write(card_number)

def get_embedding(text):
    """
    Get text embedding using OpenAI's API
    Args:
        text (str): Text to get embedding for
    Returns:
        list: Embedding vector
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
    data = {
        "model": "text-embedding-3-small",
        "input": [text]
    }
    response = requests.post("http://aiproxy.sanand.workers.dev/openai/v1/embeddings", headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]

def find_similar_comments(filename='/data/comments.txt', output_filename='/data/comments-similar.txt'):
    """
    Find the most similar pair of comments using embeddings
    Args:
        filename (str): Input file containing comments
        output_filename (str): Output file to write similar comments
    """
    with open(filename, 'r') as f:
        comments = [line.strip() for line in f.readlines()]

    embeddings = [get_embedding(comment) for comment in comments]

    min_distance = float('inf')
    most_similar = (None, None)

    for i in range(len(comments)):
        for j in range(i + 1, len(comments)):
            distance = cosine(embeddings[i], embeddings[j])
            if distance < min_distance:
                min_distance = distance
                most_similar = (comments[i], comments[j])

    with open(output_filename, 'w') as f:
        f.write(most_similar[0] + '\n')
        f.write(most_similar[1] + '\n')

def calculate_ticket_sales(filename='/data/ticket-sales.db', output_filename='/data/ticket-sales-gold.txt', query="SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'"):
    """
    Calculate total ticket sales from a database
    Args:
        filename (str): SQLite database file
        output_filename (str): Output file to write total sales
        query (str): SQL query to calculate sales
    """
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()

    cursor.execute(query)
    total_sales = cursor.fetchone()[0]
    total_sales = total_sales if total_sales else 0

    with open(output_filename, 'w') as file:
        file.write(str(total_sales))

    conn.close()
