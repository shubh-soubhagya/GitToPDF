import csv
import os
from fpdf import FPDF
import textwrap

def generate_pdf_from_csv(csv_file, start_row, end_row, output_pdf):
    """Generate PDF from multiple rows in CSV"""
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found")
        return False
    
    # Read the specified rows from CSV
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            
            if start_row < 1 or start_row > len(rows):
                print(f"Error: Start row {start_row} is out of range. CSV has {len(rows)} rows.")
                return False
            
            if end_row < start_row or end_row > len(rows):
                print(f"Error: End row {end_row} is invalid. Must be between {start_row} and {len(rows)}.")
                return False
            
            selected_rows = rows[start_row - 1:end_row]
            
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return False
    
    # Create PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Process each row
    for i, row in enumerate(selected_rows, start=start_row):
        refined_problem = row.get('refined_problem', '')
        java_code = row.get('java_code', '')
        directory_name = row.get('directory_name', f'Row_{i}')
        
        # Add new page for each problem (including the first one)
        pdf.add_page()
        
        # Set font
        pdf.set_font("Arial", size=11)
        
        # Add title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=f"Problem {i-start_row+1}: {directory_name}", ln=True, align='C')
        pdf.ln(10)
        
        # Add refined problem section
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Problem Statement:", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.ln(5)
        
        # Wrap and add refined problem text
        if refined_problem and refined_problem.strip():
            wrapped_problem = textwrap.fill(refined_problem, width=80)
            pdf.multi_cell(0, 8, txt=wrapped_problem)
        else:
            pdf.cell(200, 10, txt="No problem statement available", ln=True)
        
        pdf.ln(10)
        
        # Add Java code section
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Java Code:", ln=True)
        pdf.set_font("Courier", size=10)  # Use monospace font for code
        pdf.ln(5)
        
        # Add Java code with preserved formatting
        if java_code and java_code.strip():
            # Split Java code into lines and add each line
            for line in java_code.split('\n'):
                # Remove any trailing whitespace but preserve leading spaces for indentation
                clean_line = line.rstrip()
                if clean_line:  # Only add non-empty lines
                    pdf.cell(0, 6, txt=clean_line, ln=True)
                else:
                    pdf.ln(6)  # Add empty line for blank lines in code
        else:
            pdf.set_font("Arial", size=11)
            pdf.cell(200, 10, txt="No Java code available", ln=True)
        
        # Add separator between problems (unless it's the last one)
        if i < end_row:
            pdf.ln(15)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="=" * 80, ln=True, align='C')
            pdf.ln(15)
    
    # Save PDF
    try:
        pdf.output(output_pdf)
        print(f"PDF successfully generated: {output_pdf}")
        print(f"Content from rows {start_row} to {end_row} ({end_row - start_row + 1} problems)")
        return True
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False

def get_integer_input(prompt, default_value, min_value=1, max_value=None):
    """Get integer input with validation"""
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                return default_value
            value = int(value)
            if value < min_value:
                print(f"Value must be at least {min_value}")
                continue
            if max_value is not None and value > max_value:
                print(f"Value must be at most {max_value}")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer")

def main():
    """Main function to run the script"""
    print("CSV to PDF Generator - Multiple Rows")
    print("=" * 50)
    
    # Get CSV file path
    csv_file = input("Enter the path to CSV file: ").strip()
    if not csv_file:
        print("No CSV file provided. Exiting.")
        return
    
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' does not exist")
        return
    
    # Count total rows to set reasonable defaults
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            total_rows = sum(1 for _ in reader)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    if total_rows == 0:
        print("CSV file is empty or cannot be read")
        return
    
    print(f"Total rows in CSV: {total_rows}")
    
    # Get start and end row numbers
    start_row = get_integer_input(
        f"Enter start row number (1-{total_rows}, default 1): ",
        default_value=1,
        min_value=1,
        max_value=total_rows
    )
    
    end_row = get_integer_input(
        f"Enter end row number ({start_row}-{total_rows}, default {total_rows}): ",
        default_value=total_rows,
        min_value=start_row,
        max_value=total_rows
    )
    
    # Get output PDF filename
    output_pdf = input("Enter output PDF file name (default: problems_solutions.pdf): ").strip()
    if not output_pdf:
        output_pdf = "problems_solutions.pdf"
    
    # Generate PDF
    success = generate_pdf_from_csv(csv_file, start_row, end_row, output_pdf)
    
    if success:
        print("\nPDF generation completed successfully!")
        print(f"Generated PDF contains problems from row {start_row} to {end_row}")
    else:
        print("\nPDF generation failed.")

if __name__ == "__main__":
    main()