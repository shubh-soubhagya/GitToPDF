import csv
import os
from fpdf import FPDF

# --- Professional PDF Class with Header and Footer ---
class PDF(FPDF):
    """
    Custom PDF class to add a consistent header and footer to each page.
    """
    def header(self):
        # Header is kept minimal to save space
        pass

    def footer(self):
        # Position at 1.0 cm from the bottom
        self.set_y(-10)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_from_csv(csv_file, start_row, end_row, output_pdf):
    """
    Generate a compact, continuously flowing PDF from a CSV file.
    """
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found")
        return False

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            if not (1 <= start_row <= len(rows) and start_row <= end_row <= len(rows)):
                print(f"Error: Invalid row range.")
                return False
            selected_rows = rows[start_row - 1:end_row]
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return False

    # Initialize PDF with smaller margins
    pdf = PDF('P', 'mm', 'A4')
    pdf.set_margins(10, 10, 10) # Left, Top, Right margins (in mm)
    pdf.set_auto_page_break(auto=True, margin=10) # Bottom margin

    # --- Page is added only ONCE at the beginning ---
    pdf.add_page()

    # Define compact styling elements
    LINE_HEIGHT = 4.5 # Reduced line height

    for i, row in enumerate(selected_rows, start=start_row):
        refined_problem = row.get('refined_problem', 'No problem statement available.').strip()
        java_code = row.get('java_code', 'No Java code available.').strip()
        directory_name = row.get('directory_name', f'Row_{i}')

        # --- Problem Title (Compact) ---
        pdf.set_font("Times", 'B', 12) # Reduced from 14
        pdf.cell(0, LINE_HEIGHT * 1.5, txt=f"Problem {i - start_row + 1}: {directory_name}", ln=True)
        pdf.ln(LINE_HEIGHT / 2)

        # --- Problem Statement Section (Compact) ---
        pdf.set_font("Times", 'B', 11) # Reduced from 12
        pdf.cell(0, LINE_HEIGHT, "Problem Statement", ln=True)
        
        pdf.set_font("Times", size=9) # Reduced from 10
        pdf.multi_cell(0, LINE_HEIGHT, txt=refined_problem, align='J')
        pdf.ln(LINE_HEIGHT * 0.5)
        
        # --- Java Code Section (Compact) ---
        pdf.set_font("Times", 'B', 11) # Reduced from 12
        pdf.cell(0, LINE_HEIGHT, "Java Code", ln=True)

        pdf.set_font("Courier", size=8) # Reduced from 9
        pdf.set_fill_color(245, 245, 245) # Very light grey
        
        pdf.multi_cell(0, 4, txt=java_code, border=1, fill=True) # Reduced line height

        # --- ADD A SEPARATOR for continuous flow ---
        # Add a line and space before the next problem, but not after the last one.
        if i < end_row:
            pdf.ln(LINE_HEIGHT)
            pdf.cell(0, 0, '', 'T', 1) # Draw a line using a cell's top border
            pdf.ln(LINE_HEIGHT * 2)

    try:
        pdf.output(output_pdf)
        print(f"✅ PDF successfully generated: {output_pdf}")
        print(f"Content from rows {start_row} to {end_row} included.")
        return True
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False

def get_integer_input(prompt, default_value, min_value=1, max_value=None):
    """Get integer input from the user with validation."""
    while True:
        try:
            value = input(prompt).strip()
            if not value: return default_value
            value = int(value)
            if not (min_value <= value <= (max_value if max_value is not None else value)):
                print(f"Value must be between {min_value} and {max_value}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer.")

def main():
    """Main function to run the script."""
    print("CSV to Compact PDF Generator")
    print("=" * 40)
    
    csv_file = input("Enter the path to the CSV file: ").strip()
    if not csv_file or not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' does not exist. Exiting.")
        return
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            total_rows = sum(1 for row in csv.reader(file)) - 1
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
        
    if total_rows <= 0:
        print("CSV file is empty or contains only a header.")
        return
        
    print(f"Total data rows in CSV: {total_rows}")
    
    start_row = get_integer_input(
        f"Enter start row (1-{total_rows}, default 1): ", 1, 1, total_rows
    )
    
    end_row = get_integer_input(
        f"Enter end row ({start_row}-{total_rows}, default {total_rows}): ", total_rows, start_row, total_rows
    )
    
    default_filename = f"problems_{start_row}_to_{end_row}.pdf"
    output_pdf = input(f"Enter output PDF name (default: {default_filename}): ").strip() or default_filename
    
    print("\nGenerating PDF...")
    generate_pdf_from_csv(csv_file, start_row, end_row, output_pdf)

if __name__ == "__main__":
    main()