import os
import csv
import argparse
from pathlib import Path

def read_file_content(file_path):
    """Read the content of a file with proper error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {e}"
    except Exception as e:
        return f"Error reading file: {e}"

def scan_directory(base_dir):
    """Scan the base directory for subdirectories containing .java and README.md files"""
    data = []
    base_path = Path(base_dir)
    
    if not base_path.exists() or not base_path.is_dir():
        print(f"Error: {base_dir} is not a valid directory")
        return data
    
    # Iterate through all subdirectories
    for subdir in base_path.iterdir():
        if subdir.is_dir():
            dir_name = subdir.name
            readme_content = ""
            java_code = ""
            
            # Look for README.md files
            readme_files = list(subdir.glob('README.md')) + list(subdir.glob('readme.md')) + list(subdir.glob('Readme.md'))
            
            if readme_files:
                # Take the first README file found
                readme_content = read_file_content(readme_files[0])
            
            # Look for .java files
            java_files = list(subdir.glob('*.java'))
            java_contents = []
            
            for java_file in java_files:
                content = read_file_content(java_file)
                java_contents.append(f"--- File: {java_file.name} ---\n{content}\n")
            
            java_code = "\n".join(java_contents)
            
            data.append({
                'directory_name': dir_name,
                'readme_content': readme_content,
                'java_code': java_code
            })
    
    return data

def save_to_csv(data, output_file):
    """Save the collected data to a CSV file"""
    if not data:
        print("No data to save")
        return
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['directory_name', 'readme_content', 'java_code']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        
        print(f"Data successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving CSV file: {e}")

def main():
    """Main function to run the script"""
    print("Java and README File Scanner")
    print("=" * 40)
    
    # Get input directory path
    base_dir = input("Enter the path to directoryA: ").strip()
    
    if not base_dir:
        print("No directory path provided. Exiting.")
        return
    
    # Scan the directory
    print(f"Scanning directory: {base_dir}")
    data = scan_directory(base_dir)
    
    if not data:
        print("No subdirectories with Java/README files found.")
        return
    
    print(f"Found {len(data)} subdirectories with files")
    
    # Save to CSV
    output_file = "java_readme_data.csv"
    save_to_csv(data, output_file)
    
    # Display summary
    print("\nSummary:")
    print(f"Total directories processed: {len(data)}")
    
    directories_with_readme = sum(1 for item in data if item['readme_content'].strip())
    directories_with_java = sum(1 for item in data if item['java_code'].strip())
    
    print(f"Directories with README: {directories_with_readme}")
    print(f"Directories with Java code: {directories_with_java}")

if __name__ == "__main__":
    main()