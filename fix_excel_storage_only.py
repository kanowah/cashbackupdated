#!/usr/bin/env python3

# Read the file
with open('pdf_processor_final_working.py', 'r') as f:
    content = f.read()

# Remove the problematic line that writes to main directory
old_code = '''# Create a copy with the expected filename for email script
    expected_excel_path = "/var/www/cashback/Compile CBOpt Nov25.xlsx"
    with open(expected_excel_path, "wb") as f:
        f.write(excel_file.getvalue())'''

# Replace with empty string (remove this section)
content = content.replace(old_code, '')

# Write back
with open('pdf_processor_final_working.py', 'w') as f:
    f.write(content)

print("✅ Removed problematic Excel copy to main directory")
