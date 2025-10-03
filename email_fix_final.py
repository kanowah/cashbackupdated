#!/usr/bin/env python3
import os

# Read the original file
with open('send_emails_brevo.py', 'r') as f:
    lines = f.readlines()

# Find the line with pd.read_excel and replace it
new_lines = []
for line in lines:
    if 'df = pd.read_excel("Compile CBOpt Nov25.xlsx")' in line:
        # Get the indentation from the original line
        indent = line[:len(line) - len(line.lstrip())]
        
        # Add the new code block with proper indentation
        new_lines.append(f'{indent}# Try multiple locations for Excel file\n')
        new_lines.append(f'{indent}excel_locations = [\n')
        new_lines.append(f'{indent}    "Compile CBOpt Nov25.xlsx",\n')
        new_lines.append(f'{indent}    "/var/www/cashback/storage/uploaded_files/latest_excel.xlsx",\n')
        new_lines.append(f'{indent}    "/var/www/cashback/temp/temp_uploaded.xlsx"\n')
        new_lines.append(f'{indent}]\n')
        new_lines.append(f'{indent}\n')
        new_lines.append(f'{indent}df = None\n')
        new_lines.append(f'{indent}for excel_path in excel_locations:\n')
        new_lines.append(f'{indent}    try:\n')
        new_lines.append(f'{indent}        if os.path.exists(excel_path):\n')
        new_lines.append(f'{indent}            df = pd.read_excel(excel_path)\n')
        new_lines.append(f'{indent}            print(f"📊 Using Excel file: {{excel_path}}")\n')
        new_lines.append(f'{indent}            break\n')
        new_lines.append(f'{indent}    except Exception as e:\n')
        new_lines.append(f'{indent}        continue\n')
        new_lines.append(f'{indent}\n')
        new_lines.append(f'{indent}if df is None:\n')
        new_lines.append(f'{indent}    raise FileNotFoundError("No Excel file found in any expected location")\n')
    else:
        new_lines.append(line)

# Write the modified file
with open('send_emails_brevo.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Email script fixed successfully")
print("📧 Script will now look for Excel files in multiple locations")
