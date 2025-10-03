
import re

# Read the current file
with open('pdf_processor_final_working.py', 'r') as f:
    content = f.read()

# Find the section where Excel file is saved
old_pattern = r'(with open\(excel_path, "wb"\) as f:\s+f\.write\(excel_file\.getvalue\(\)\))'

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

# Replace the pattern
content = re.sub(old_pattern, new_code, content)

# Write back to file
with open('pdf_processor_final_working.py', 'w') as f:
    f.write(content)

print("✅ Excel preservation fix applied")
