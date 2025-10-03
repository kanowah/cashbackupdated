#!/usr/bin/env python3
"""
Demo script to create sample PDFs for testing the merge functionality
"""
import os
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_sample_pdfs():
    """Create sample PDF files for testing merge functionality"""
    
    # Create directory for PDFs without email
    output_dir = Path("policies_without_email")
    output_dir.mkdir(exist_ok=True)
    
    print(f"📁 Creating sample PDFs in {output_dir}/")
    
    # Sample policy data
    policies = [
        {"policy": "PRINT001", "name": "John Doe", "amount": "$5,000"},
        {"policy": "PRINT002", "name": "Jane Smith", "amount": "$7,500"},
        {"policy": "PRINT003", "name": "Bob Johnson", "amount": "$3,200"},
        {"policy": "PRINT004", "name": "Alice Brown", "amount": "$9,800"},
        {"policy": "PRINT005", "name": "Charlie Wilson", "amount": "$4,600"},
    ]
    
    for i, policy_data in enumerate(policies, 1):
        filename = f"{policy_data['policy']}.pdf"
        filepath = output_dir / filename
        
        # Create PDF with sample content
        c = canvas.Canvas(str(filepath), pagesize=letter)
        width, height = letter
        
        # Add content to PDF
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "NIC Life Insurance Mauritius")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, "Policy Cash Back Letter")
        
        c.drawString(50, height - 120, f"Policy Number: {policy_data['policy']}")
        c.drawString(50, height - 140, f"Policy Holder: {policy_data['name']}")
        c.drawString(50, height - 160, f"Cash Back Amount: {policy_data['amount']}")
        
        c.drawString(50, height - 200, "Dear Valued Client,")
        c.drawString(50, height - 220, "We are pleased to inform you about your cash back benefit.")
        c.drawString(50, height - 240, "Please find the details above.")
        
        c.drawString(50, height - 280, "This policy requires manual processing as no email")
        c.drawString(50, height - 300, "address was provided.")
        
        c.drawString(50, height - 340, "Kind Regards,")
        c.drawString(50, height - 360, "NIC - Serving you, Serving the Nation")
        
        # Add page number
        c.drawString(width - 100, 30, f"Page {i}")
        
        c.save()
        print(f"✅ Created: {filename}")
    
    print(f"\n🎉 Created {len(policies)} sample PDFs for merge testing!")
    return len(policies)

def cleanup_sample_pdfs():
    """Remove sample PDFs"""
    output_dir = Path("policies_without_email")
    if output_dir.exists():
        pdf_files = list(output_dir.glob("PRINT*.pdf"))
        for pdf_file in pdf_files:
            pdf_file.unlink()
            print(f"🗑️ Removed: {pdf_file.name}")
        print(f"🧹 Cleaned up {len(pdf_files)} sample PDFs")

def main():
    print("🔗 PDF Merge Demo Setup")
    print("=" * 30)
    print()
    
    choice = input("Choose an option:\n1. Create sample PDFs\n2. Cleanup sample PDFs\n3. Both (create then test)\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        create_sample_pdfs()
        print("\n📋 Next steps:")
        print("1. Run: streamlit run pdf_processor_final_working.py")
        print("2. Look for the '🖨️ PDF Merging for Printing' section")
        print("3. Click 'Create Printable PDF' to test the merge functionality")
        
    elif choice == "2":
        cleanup_sample_pdfs()
        
    elif choice == "3":
        create_sample_pdfs()
        print("\n🧪 Testing merge functionality...")
        
        # Import and test the merge function
        try:
            import PyPDF2
            from pathlib import Path
            
            input_folder = "policies_without_email"
            output_file = "test_merged.pdf"
            
            # Get PDF files
            pdf_files = list(Path(input_folder).glob("PRINT*.pdf"))
            print(f"📁 Found {len(pdf_files)} PDFs to merge")
            
            # Merge PDFs
            try:
                merger = PyPDF2.PdfMerger()  # New version
            except AttributeError:
                merger = PyPDF2.PdfFileMerger()  # Fallback for older versions
            for pdf_file in sorted(pdf_files):
                merger.append(str(pdf_file))
                print(f"📄 Added: {pdf_file.name}")
            
            # Write merged file
            with open(output_file, 'wb') as output:
                merger.write(output)
            merger.close()
            
            # Check result
            file_size = os.path.getsize(output_file)
            with open(output_file, 'rb') as f:
                reader = PyPDF2.PdfFileReader(f)
                total_pages = reader.numPages
            
            print(f"\n✅ Merge test successful!")
            print(f"📊 Output: {output_file}")
            print(f"📄 Pages: {total_pages}")
            print(f"💾 Size: {file_size / 1024:.1f} KB")
            
            # Cleanup test file
            os.remove(output_file)
            print(f"🗑️ Cleaned up test file")
            
        except Exception as e:
            print(f"❌ Merge test failed: {e}")
        
        print("\n📋 Now test in Streamlit:")
        print("streamlit run pdf_processor_final_working.py")
        
    else:
        print("Invalid choice. Please run again and select 1, 2, or 3.")

if __name__ == "__main__":
    main()