#!/usr/bin/env python3
"""
Apply VPS-specific fixes to the new code
"""

# Read the file
with open('pdf_processor_final_working.py', 'r') as f:
    content = f.read()

# Apply all the working VPS fixes
fixes = [
    # Fix temp file paths
    ('pdf_path = "temp_uploaded.pdf"', 'pdf_path = "/var/www/cashback/temp/temp_uploaded.pdf"'),
    ('excel_path = "temp_uploaded.xlsx"', 'excel_path = "/var/www/cashback/temp/temp_uploaded.xlsx"'),
    
    # Fix directory paths
    ('os.makedirs("policies_with_email", exist_ok=True)', 'os.makedirs("/var/www/cashback/storage/generated_pdfs/with_email", exist_ok=True)'),
    ('os.makedirs("policies_without_email", exist_ok=True)', 'os.makedirs("/var/www/cashback/storage/generated_pdfs/without_email", exist_ok=True)'),
    
    # Fix folder references
    ('"policies_with_email"', '"/var/www/cashback/storage/generated_pdfs/with_email"'),
    ('"policies_without_email"', '"/var/www/cashback/storage/generated_pdfs/without_email"'),
    
    # Fix glob patterns
    ('glob.glob("policies_with_email/*.pdf")', 'glob.glob("/var/www/cashback/storage/generated_pdfs/with_email/*.pdf")'),
    ('glob.glob("policies_without_email/*.pdf")', 'glob.glob("/var/www/cashback/storage/generated_pdfs/without_email/*.pdf")'),
]

# Apply all fixes
for old, new in fixes:
    content = content.replace(old, new)

# Add Excel preservation if not present
if 'permanent_excel_dir = "/var/www/cashback/storage/uploaded_files"' not in content:
    # Find the Excel writing section and add preservation
    excel_write = 'with open(excel_path, "wb") as f:\n        f.write(excel_file.getvalue())'
    excel_preserve = '''with open(excel_path, "wb") as f:
        f.write(excel_file.getvalue())
    
    # Also save a permanent copy for email sending
    permanent_excel_dir = "/var/www/cashback/storage/uploaded_files"
    os.makedirs(permanent_excel_dir, exist_ok=True)
    permanent_excel_path = os.path.join(permanent_excel_dir, "latest_excel.xlsx")
    
    with open(permanent_excel_path, "wb") as f:
        f.write(excel_file.getvalue())'''
    
    content = content.replace(excel_write, excel_preserve)

# Write back
with open('pdf_processor_final_working.py', 'w') as f:
    f.write(content)

print("✅ Applied all VPS fixes to new code")
