#!/usr/bin/env python3

# Read the file
with open('send_emails_brevo.py', 'r') as f:
    lines = f.readlines()

# Find and replace the Excel reading line
new_lines = []
for line in lines:
    if 'df = pd.read_excel("Compile CBOpt Nov25.xlsx")' in line:
        # Get the indentation from the original line
        indent = line[:len(line) - len(line.lstrip())]
        
        # Add the new code with proper indentation
        new_lines.append(f'{indent}# Try multiple Excel file locations\n')
        new_lines.append(f'{indent}excel_files = [\n')
        new_lines.append(f'{indent}    "Compile CBOpt Nov25.xlsx",\n')
        new_lines.append(f'{indent}    "/var/www/cashback/storage/uploaded_files/latest_excel.xlsx"\n')
        new_lines.append(f'{indent}]\n')
        new_lines.append(f'{indent}df = None\n')
        new_lines.append(f'{indent}for excel_file in excel_files:\n')
        new_lines.append(f'{indent}    if os.path.exists(excel_file):\n')
        new_lines.append(f'{indent}        df = pd.read_excel(excel_file)\n')
        new_lines.append(f'{indent}        print(f"📊 Using Excel file: {{excel_file}}")\n')
        new_lines.append(f'{indent}        break\n')
        new_lines.append(f'{indent}if df is None:\n')
        new_lines.append(f'{indent}    df = pd.read_excel("Compile CBOpt Nov25.xlsx")  # fallback\n')
    else:
        new_lines.append(line)

# Write back
with open('send_emails_brevo.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Fixed email script Excel file paths")
