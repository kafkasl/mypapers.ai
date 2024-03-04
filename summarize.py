#!/usr/bin/env python3
import sys

import openai

import os
from dotenv import load_dotenv
import openai

# Load environment variables from a .env file
load_dotenv()

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from a .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')  # defaults to os.environ.get("OPENAI_API_KEY")
)

def summarize_text(text):
    if not client.api_key:
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable in a .env file.")

    # System prompt with clear instructions for summarization
    system_prompt = "Please summarize the following research paper:"

    # Combining the system prompt with the user's text to form the full prompt
    full_prompt = f"{system_prompt}\n\n{text}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ]
    )
    summary = response.choices[0].message['content'].strip()
    return summary

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: summarize file.txt")
        sys.exit(1)

    txt_file_path = sys.argv[1]
    with open(txt_file_path, 'r') as txt_file:
        input_text = txt_file.read()


    summary = summarize_text(input_text)
    summary_file_path = txt_file_path.rsplit('.', 1)[0] + '_summary.txt'

    with open(summary_file_path, 'w') as summary_file:
        summary_file.write(summary)

    print(summary)  # Also print the summary to stdout
