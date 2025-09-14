import os
import csv
import re
import requests
import json
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def clean_text_markdown(text):
    """Basic cleaning to remove markdown symbols and HTML tags"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove markdown headers
    text = re.sub(r'#+\s*', '', text)
    # Remove markdown links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove markdown images
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)
    # Remove markdown bold/italic
    text = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', text)
    # Remove code blocks
    text = re.sub(r'```[^`]*```', '', text)
    text = re.sub(r'`[^`]*`', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def call_groq_api(prompt, model="llama-3.1-8b-instant"):
    """Call Groq API with specified model to refine the problem statement"""
    try:
        # Initialize Groq client
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            print("Error: GROQ_API_KEY not found in environment variables")
            return None
        
        client = Groq(api_key=api_key)
        
        # Make the API call
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that processes LeetCode problem statements. Extract and clean the problem description while preserving all technical content."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=model,
            temperature=0.1,
            max_tokens=2000,
            top_p=0.9
        )
        
        return chat_completion.choices[0].message.content.strip()
            
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return None

def refine_problem_statement(readme_content):
    """Refine the problem statement using Groq API"""
    if not readme_content or readme_content.strip() == "":
        return "No README content available"
    
    # Basic cleaning first
    cleaned_content = clean_text_markdown(readme_content)
    
    if len(cleaned_content.split()) < 10:  # If content is too short
        return cleaned_content
    
    # Create prompt for the model
    prompt = f"""Analyze this LeetCode problem description and extract the complete problem statement in clean, plain text format.

REQUIREMENTS:
1. PRESERVE all technical content exactly: problem description, examples, constraints, and requirements
2. CONVERT all HTML entities to proper characters: &quot; to ", &lt; to <, &gt; to >, etc.
3. REMOVE all markdown formatting: headers (#), bold (**), italics (*), code blocks (```), inline code (`), links, and HTML tags
4. MAINTAIN the original structure: keep examples and constraints clearly separated
5. KEEP all test cases, examples, and constraints intact but remove markdown syntax
6. PRESERVE exact wording and technical details - do not paraphrase or summarize
7. OUTPUT in clean, readable plain text with proper spacing

INPUT CONTENT:
{cleaned_content[:3000]}

Provide the complete problem statement with examples and constraints in clean plain text format:"""
    
    # Call Groq API
    refined_text = call_groq_api(prompt)
    
    if refined_text is None:
        # Fallback to basic cleaning if API fails
        return cleaned_content[:1000]
    
    return refined_text

def process_csv_file(input_csv, output_csv):
    """Process the CSV file and add refined_problem column"""
    if not os.path.exists(input_csv):
        print(f"Error: Input file {input_csv} not found")
        return
    
    rows = []
    
    # Read the input CSV
    try:
        with open(input_csv, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames + ['refined_problem'] if reader.fieldnames else []
            
            for row in reader:
                rows.append(row)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    if not rows:
        print("No data found in CSV file")
        return
    
    # Process each row
    print("Processing README content with Groq API...")
    print("This may take some time depending on the number of entries...")
    
    for i, row in enumerate(rows, 1):
        readme_content = row.get('readme_content', '')
        print(f"Processing entry {i}/{len(rows)}...")
        
        # Refine the problem statement
        refined_problem = refine_problem_statement(readme_content)
        row['refined_problem'] = refined_problem
        
        # Print progress
        print(f"✓ Processed directory: {row.get('directory_name', 'Unknown')}")
        if refined_problem and len(refined_problem) > 0:
            preview = refined_problem[:100] + "..." if len(refined_problem) > 100 else refined_problem
            print(f"   Refined problem: {preview}")
        print()
    
    # Write to output CSV
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = list(rows[0].keys()) if rows else []
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        
        print(f"Successfully processed and saved to {output_csv}")
        print(f"Total entries processed: {len(rows)}")
        
    except Exception as e:
        print(f"Error writing to CSV file: {e}")

def main():
    """Main function to run the script"""
    print("Groq API README Processor")
    print("=" * 40)
    print("Prerequisites:")
    print("1. GROQ_API_KEY must be set in .env file")
    print("2. Install required packages: pip install python-dotenv groq")
    print("3. Input CSV file should have 'readme_content' column")
    print()
    
    # Check if API key is available
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("Error: GROQ_API_KEY not found in environment variables")
        print("Please create a .env file with: GROQ_API_KEY=your_api_key_here")
        print("Get your API key from: https://console.groq.com/keys")
        return
    
    # Get input file path
    input_csv = input("Enter the path to input CSV file: ").strip()
    
    if not input_csv:
        print("No input file provided. Exiting.")
        return
    
    # Set output file path
    output_csv = input("Enter output CSV file name (default: refined_java_readme_data.csv): ").strip()
    if not output_csv:
        output_csv = "refined_java_readme_data.csv"
    
    # Process the CSV file
    process_csv_file(input_csv, output_csv)

if __name__ == "__main__":
    main()