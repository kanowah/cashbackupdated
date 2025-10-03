import re
import os

# Read the email script
with open('send_emails_brevo.py', 'r') as f:
    content = f.read()

# Find the Excel reading section
old_pattern = r'df = pd\.read_excel\("Compile CBOpt Nov25\.xlsx"\)'

new_code = '''# Try multiple locations for Excel file
    excel_locations = [
        "Compile CBOpt Nov25.xlsx",
        "/var/www/cashback/storage/uploaded_files/latest_excel.xlsx",
        "/var/www/cashback/temp/temp_uploaded.xlsx"
    ]
    
    df = None
    for excel_path in excel_locations:
        try:
            if os.path.exists(excel_path):
                df = pd.read_excel(excel_path)
                print(f"📊 Using Excel file: {excel_path}")
                break
        except Exception as e:
            continue
    
    if df is None:
        raise FileNotFoundError("No Excel file found in any expected location")'''

# Replace the pattern
content = re.sub(old_pattern, new_code, content)

# Write back to file
with open('send_emails_brevo.py', 'w') as f:
    f.write(content)

print("✅ Email script updated to look in multiple locations")
