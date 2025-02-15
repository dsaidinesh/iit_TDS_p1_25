# app.py
# Main FastAPI application file that handles API endpoints and function routing
# This file serves as the central hub for all task executions and API interactions

# Dependencies required for the application
# /// script
# dependencies = [
#   "requests",      # For making HTTP requests
#   "fastapi",       # Web framework for building APIs
#   "uvicorn",       # ASGI server implementation
#   "python-dateutil", # For date parsing and manipulation
#   "pandas",        # Data manipulation library
#   "db-sqlite3",    # SQLite database interface
#   "scipy",         # Scientific computing library
#   "pybase64",      # Base64 encoding/decoding
#   "python-dotenv", # Environment variable management
#   "httpx",         # HTTP client with async support
#   "markdown",      # Markdown to HTML conversion
#   "duckdb"         # SQL database management
# ]
# ///

# Import necessary libraries and modules
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from tasksA import *  # Import all functions from tasksA
from tasksB import *  # Import all functions from tasksB
import requests
from dotenv import load_dotenv
import os
import re
import httpx
import json

# Initialize FastAPI application
app = FastAPI()

# Configure CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()

# API endpoint for natural language task processing
@app.get("/ask")
def ask(prompt: str):
    result = get_completions(prompt)
    return result

# Configuration for OpenAI API proxy
openai_api_chat = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
openai_api_key = os.getenv("AIPROXY_TOKEN")

# HTTP headers for API requests
headers = {
    "Authorization": f"Bearer {openai_api_key}",
    "Content-Type": "application/json",
}

# Function definitions for LLM task routing
function_definitions_llm = [
    {
        "name": "generate_data",
        "description": "Run a Python script from a given URL, passing an email as the argument.",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "pattern": r"[\w\.-]+@[\w\.-]+\.\w+"}
            },
            "required": ["filename", "targetfile", "email"]
        }
    },
    {
        "name": "format_markdown",
        "description": "Format a markdown file using a specified version of Prettier.",
        "parameters": {
            "type": "object",
            "properties": {
                "prettier_version": {"type": "string", "pattern": r"prettier@\d+\.\d+\.\d+"},
                "filename": {"type": "string", "pattern": r".*/(.*\.md)"}
            },
            "required": ["prettier_version", "filename"]
        }
    },
    {
        "name": "count_weekday_dates",
        "description": "Count the number of occurrences of a specific weekday in a date file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "pattern": r"/data/.*dates.*\.txt"},
                "targetfile": {"type": "string", "pattern": r"/data/.*/(.*\.txt)"},
                "weekday": {"type": "integer", "pattern": r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"}
            },
            "required": ["filename", "targetfile", "weekday"]
        }
    },
    {
        "name": "sort_contacts",
        "description": "Sort a JSON contacts file and save the sorted version to a target file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.json)",
                },
                "targetfile": {
                    "type": "string",
                    "pattern": r".*/(.*\.json)",
                }
            },
            "required": ["filename", "targetfile"]
        }
    },
    {
        "name": "get_recent_logs",
        "description": "Retrieve the most recent log files from a directory and save their content to an output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "log_dir_path": {
                    "type": "string",
                    "pattern": r".*/logs",
                    "default": "/data/logs"
                },
                "output_file_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/logs-recent.txt"
                },
                "num_files": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 10
                }
            },
            "required": ["log_dir_path", "output_file_path", "num_files"]
        }
    },
    {
        "name": "create_docs_index",
        "description": "Generate an index of documents from a directory and save it as a JSON file.",
        "parameters": {
            "type": "object",
            "properties": {
                "doc_dir_path": {
                    "type": "string",
                    "pattern": r".*/docs",
                    "default": "/data/docs"
                },
                "output_file_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.json)",
                    "default": "/data/docs/index.json"
                }
            },
            "required": ["doc_dir_path", "output_file_path"]
        }
    },
    {
        "name": "extract_email_sender",
        "description": "Extract the sender's email address from a text file and save it to an output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/email.txt"
                },
                "output_file": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/email-sender.txt"
                }
            },
            "required": ["filename", "output_file"]
        }
    },
    {
        "name": "process_credit_card",
        "description": "Generate an image representation of credit card details from a text file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/credit-card.txt"
                },
                "image_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.png)",
                    "default": "/data/credit-card.png"
                }
            },
            "required": ["filename", "image_path"]
        }
    },
    {
        "name": "find_similar_comments",
        "description": "Find similar comments from a text file and save them to an output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/comments.txt"
                },
                "output_filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/comments-similar.txt"
                }
            },
            "required": ["filename", "output_filename"]
        }
    },
    {
        "name": "calculate_ticket_sales",
        "description": "Calculate total ticket sales from a database and save the result to a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.db)",
                    "default": "/data/ticket-sales.db"
                },
                "output_filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "default": "/data/ticket-sales-gold.txt"
                },
                "query": {
                    "type": "string",
                    "default": "SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'"
                }
            },
            "required": ["filename", "output_filename", "query"]
        }
    },
    {
        "name": "validate_data_path",
        "description": "Check if filepath starts with /data",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "pattern": r"^/data/.*"
                }
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "download_url_content",
        "description": "Download content from a URL and save it to the specified path.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "pattern": r"https?://.*",
                    "description": "URL to download content from."
                },
                "save_path": {
                    "type": "string",
                    "pattern": r".*/.*",
                    "description": "Path to save the downloaded content."
                }
            },
            "required": ["url", "save_path"]
        }
    },
    {
        "name": "execute_sql_query",
        "description": "Execute a SQL query on a specified database file and save the result to an output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "db_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.db)",
                    "description": "Path to the SQLite database file."
                },
                "query": {
                    "type": "string",
                    "description": "SQL query to be executed on the database."
                },
                "output_filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.txt)",
                    "description": "Path to the file where the query result will be saved."
                }
            },
            "required": ["db_path", "query", "output_filename"]
        }
    },
    {
        "name": "scrape_web_content",
        "description": "Fetch content from a URL and save it to the specified output file.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "pattern": r"https?://.*",
                    "description": "URL to fetch content from."
                },
                "output_filename": {
                    "type": "string",
                    "pattern": r".*/.*",
                    "description": "Path to the file where the content will be saved."
                }
            },
            "required": ["url", "output_filename"]
        }
    },
    {
        "name": "process_image",
        "description": "Process an image by optionally resizing it and saving the result to an output path.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.(jpg|jpeg|png|gif|bmp))",
                    "description": "Path to the input image file."
                },
                "output_path": {
                    "type": "string",
                    "pattern": r".*/.*",
                    "description": "Path to save the processed image."
                },
                "resize": {
                    "type": "array",
                    "items": {
                        "type": "integer",
                        "minimum": 1
                    },
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "Optional. Resize dimensions as [width, height]."
                }
            },
            "required": ["image_path", "output_path"]
        }
    },
    {
        "name": "convert_markdown_to_html",
        "description": "Convert a Markdown file to HTML and save the result to the specified output path.",
        "parameters": {
            "type": "object",
            "properties": {
                "md_path": {
                    "type": "string",
                    "pattern": r".*/(.*\.md)",
                    "description": "Path to the Markdown file to be converted."
                },
                "output_path": {
                    "type": "string",
                    "pattern": r".*/.*",
                    "description": "Path where the converted file will be saved."
                }
            },
            "required": ["md_path", "output_path"]
        }
    }
]

def get_completions(prompt: str):
    """
    Get function call completions from LLM based on user prompt
    Args:
        prompt (str): User's natural language prompt
    Returns:
        dict: Selected function and its parameters
    """
    with httpx.Client(timeout=20) as client:
        response = client.post(
            f"{openai_api_chat}",
            headers=headers,
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a function classifier that extracts structured parameters from queries."},
                    {"role": "user", "content": prompt}
                ],
                "tools": [
                    {
                        "type": "function",
                        "function": function
                    } for function in function_definitions_llm
                ],
                "tool_choice": "auto"
            },
        )
    return response.json()["choices"][0]["message"]["tool_calls"][0]["function"]

# API endpoint for executing tasks
@app.post("/run")
async def run_task(task: str):
    """
    Execute a specific task based on the provided description
    Args:
        task (str): Task description in natural language
    Returns:
        dict: Execution status and message
    """
    try:
        response = get_completions(task)
        task_code = response['name']
        arguments = response['arguments']

        # Route the task to appropriate function based on task_code
        # TasksA functions
        if "generate_data"== task_code:
            generate_data(**json.loads(arguments))
        if "format_markdown"== task_code:
            format_markdown(**json.loads(arguments))
        if "count_weekday_dates"== task_code:
            count_weekday_dates(**json.loads(arguments))
        if "sort_contacts"== task_code:
            sort_contacts(**json.loads(arguments))
        if "get_recent_logs"== task_code:
            get_recent_logs(**json.loads(arguments))
        if "create_docs_index"== task_code:
            create_docs_index(**json.loads(arguments))
        if "extract_email_sender"== task_code:
            extract_email_sender(**json.loads(arguments))
        if "process_credit_card"== task_code:
            process_credit_card(**json.loads(arguments))
        if "find_similar_comments"== task_code:
            find_similar_comments(**json.loads(arguments))
        if "calculate_ticket_sales"== task_code:
            calculate_ticket_sales(**json.loads(arguments))

        if "validate_data_path"== task_code:
            validate_data_path(**json.loads(arguments))
        if "download_url_content" == task_code:
            download_url_content(**json.loads(arguments))
        if "execute_sql_query" == task_code:
            execute_sql_query(**json.loads(arguments))
        if "scrape_web_content" == task_code:
            scrape_web_content(**json.loads(arguments))
        if "process_image" == task_code:
            process_image(**json.loads(arguments))
        if "convert_markdown_to_html" == task_code:
            convert_markdown_to_html(**json.loads(arguments))
        return {"message": f"{task_code} Task '{task}' executed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# API endpoint for reading file contents
@app.get("/read", response_class=PlainTextResponse)
async def read_file(path: str = Query(..., description="File path to read")):
    """
    Read and return the contents of a file
    Args:
        path (str): Path to the file to be read
    Returns:
        str: Contents of the file
    """
    try:
        with open(path, "r") as file:
            return file.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)