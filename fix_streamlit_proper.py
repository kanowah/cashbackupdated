#!/usr/bin/env python3

# Read the file
with open('pdf_processor_final_working.py', 'r') as f:
    content = f.read()

# Find and replace the Excel file writing section
old_code = '''with open(excel_path, "wb") as f:
        f.write(excel_file.getvalue())'''

new_code = '''with open(excel_path, "wb") as f:
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

# Replace the code
content = content.replace(old_code, new_code)

# Write back
with open('pdf_processor_final_working.py', 'w') as f:
    f.write(content)

print("✅ Streamlit app fixed properly")
