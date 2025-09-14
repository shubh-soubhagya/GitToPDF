import os
import csv
import re
import requests
import json
from pathlib import Path

def clean_text_markdown(text):
    """Basic cleaning to remove markdown symbols and HTML tags"""
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

def call_ollama_gemma(prompt, model="gemma2:2b", host="http://localhost:11434"):
    """Call Ollama API with Gemma2 model to refine the problem statement"""
    try:
        # Prepare the payload
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9
            }
        }
        
        # Make the API call
        response = requests.post(
            f"{host}/api/generate",
            json=payload,
            timeout=120  # 2 minute timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()
        else:
            print(f"Ollama API error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def refine_problem_statement(readme_content):
    """Refine the problem statement using Ollama Gemma2 model"""
    if not readme_content or readme_content.strip() == "":
        return "No README content available"
    
    # Basic cleaning first
    cleaned_content = clean_text_markdown(readme_content)
    
    if len(cleaned_content.split()) < 10:  # If content is too short
        return cleaned_content
    
    # Create prompt for the model
    # prompt = f""" This is a leatcode problem. 
    # Please analyze this README content and extract the core problem statement in clear, concise text. 
    # Also do include the examples given in clear format with any constraints. 
    # Just remove the HTML tags and Markdown characters. Remove any markdown formatting like `` or ** or others.

    # README Content:
    # {cleaned_content[:2000]}  # Limit content to avoid token limits

    # Please provide only the refined content without markdown formatting removing all special charcaters denoting markdown"""

    prompt = f"""Analyze this LeetCode problem description and extract the complete problem statement in clean, plain text format.

    REQUIREMENTS:
    1. PRESERVE all technical content: problem description, examples, constraints, and requirements
    2. REMOVE all markdown formatting: headers (#), bold (**), italics (*), code blocks (```), inline code (`), links, and HTML tags
    3. MAINTAIN the original structure: keep examples and constraints clearly separated
    4. USE clean formatting: use plain text with clear section separators
    5. KEEP all test cases and examples intact but remove markdown syntax around them

    INPUT CONTENT:
    {cleaned_content[:2000]}

    OUTPUT FORMAT:
    Problem Description: [clear description of the problem]
    Examples: [formatted examples without markdown]
    Constraints: [list of constraints]
    Requirements: [what the solution must accomplish]

    Provide only the cleaned problem statement without any additional commentary or analysis:"""
    
    # Call Ollama
    refined_text = call_ollama_gemma(prompt)
    
    if refined_text is None:
        # Fallback to basic cleaning if Ollama fails
        return cleaned_content[:500]  # Limit length
    
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
    print("Processing README content with Ollama Gemma2 model...")
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
    print("Ollama Gemma2 README Processor")
    print("=" * 50)
    print("Prerequisites:")
    print("1. Ollama must be installed and running")
    print("2. Gemma2:2b model must be downloaded: run 'ollama pull gemma2:2b'")
    print("3. Input CSV file should have 'readme_content' column")
    print()
    
    # Get input file path
    input_csv = input("Enter the path to input CSV file: ").strip()
    
    if not input_csv:
        print("No input file provided. Exiting.")
        return
    
    # Set output file path
    output_csv = input("Enter output CSV file name (default: refined_java_readme_data.csv): ").strip()
    if not output_csv:
        output_csv = "refined_java_readme_data.csv"
    
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("Warning: Ollama may not be running on localhost:11434")
            print("Please ensure Ollama is installed and running")
    except:
        print("Warning: Cannot connect to Ollama. Please ensure it's running on localhost:11434")
        print("You can install Ollama from: https://ollama.com/")
        continue_anyway = input("Continue anyway? (y/n): ").strip().lower()
        if continue_anyway != 'y':
            return
    
    # Process the CSV file
    process_csv_file(input_csv, output_csv)

if __name__ == "__main__":
    main()