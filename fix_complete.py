#!/usr/bin/env python3
import re

# Read the file
with open('pdf_processor_final_working.py', 'r') as f:
    content = f.read()

# Fix 1: Update temp file paths to use absolute paths
content = content.replace(
    'pdf_path = "temp_uploaded.pdf"',
    'pdf_path = "/var/www/cashback/temp/temp_uploaded.pdf"'
)

content = content.replace(
    'excel_path = "temp_uploaded.xlsx"',
    'excel_path = "/var/www/cashback/temp/temp_uploaded.xlsx"'
)

# Fix 2: Update directory creation paths
content = content.replace(
    'os.makedirs("policies_with_email", exist_ok=True)',
    'os.makedirs("/var/www/cashback/storage/generated_pdfs/with_email", exist_ok=True)'
)

content = content.replace(
    'os.makedirs("policies_without_email", exist_ok=True)',
    'os.makedirs("/var/www/cashback/storage/generated_pdfs/without_email", exist_ok=True)'
)

# Fix 3: Update folder references
content = content.replace(
    '"policies_with_email"',
    '"/var/www/cashback/storage/generated_pdfs/with_email"'
)

content = content.replace(
    '"policies_without_email"',
    '"/var/www/cashback/storage/generated_pdfs/without_email"'
)

# Fix 4: Add Excel preservation
old_excel_code = '''with open(excel_path, "wb") as f:
        f.write(excel_file.getvalue())'''

new_excel_code = '''with open(excel_path, "wb") as f:
        f.write(excel_file.getvalue())
    
    # Also save a permanent copy for email sending
    permanent_excel_dir = "/var/www/cashback/storage/uploaded_files"
    os.makedirs(permanent_excel_dir, exist_ok=True)
    permanent_excel_path = os.path.join(permanent_excel_dir, "latest_excel.xlsx")
    
    with open(permanent_excel_path, "wb") as f:
        f.write(excel_file.getvalue())
    
    # Create a copy with the expected filename for email script
    expected_excel_path = "/var/www/cashback/Compile CBOpt Nov25.xlsx"
    with open(expected_excel_path, "wb") as f:
        f.write(excel_file.getvalue())'''

content = content.replace(old_excel_code, new_excel_code)

# Write back
with open('pdf_processor_final_working.py', 'w') as f:
    f.write(content)

print("✅ Complete fix applied - file paths and Excel preservation")
