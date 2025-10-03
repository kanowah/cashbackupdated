#!/usr/bin/env python3
"""
Final working PDF merger using PdfMerger (cross-version compatible)
"""

import PyPDF2
import os

def merge_all_pdfs():
    """Merge all PDFs using the robust PdfMerger approach (cross-version compatible)"""
    
    input_folder = "policies_without_email"
    output_file = "policies_for_printing.pdf"
    
    # Check if folder exists
    if not os.path.exists(input_folder):
        print(f"❌ Folder '{input_folder}' not found")
        return False
    
    # Get all PDF files
    pdf_files = []
    for file in os.listdir(input_folder):
        if file.endswith('.pdf'):
            pdf_files.append(os.path.join(input_folder, file))
    
    if not pdf_files:
        print(f"❌ No PDF files found in '{input_folder}' folder")
        return False
    
    # Sort files
    pdf_files.sort()
    
    print(f"📁 Found {len(pdf_files)} PDF files to merge")
    
    # Delete existing output file if it exists
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
            print(f"🗑️  Deleted existing {output_file}")
        except Exception as e:
            print(f"⚠️  Could not delete existing file: {e}")
            print("Please close any PDF viewers and try again")
            return False
    
    try:
        # Use PdfMerger (updated from deprecated PdfFileMerger)
        try:
            merger = PyPDF2.PdfMerger()  # New version
        except AttributeError:
            merger = PyPDF2.PdfFileMerger()  # Fallback for older versions
        
        successful_merges = 0
        
        for i, pdf_path in enumerate(pdf_files):
            # Show progress every 50 files
            if i % 50 == 0 or i == len(pdf_files) - 1:
                print(f"📄 Processing {i+1}/{len(pdf_files)}: {os.path.basename(pdf_path)}")
            
            try:
                # Add entire PDF file to merger
                merger.append(pdf_path)
                successful_merges += 1
                            
            except Exception as e:
                print(f"⚠️  Error processing {os.path.basename(pdf_path)}: {e}")
                continue
        
        if successful_merges == 0:
            print("❌ No PDFs could be merged")
            return False
        
        # Write merged PDF
        print(f"💾 Writing merged PDF with {successful_merges} files...")
        try:
            with open(output_file, 'wb') as output:
                merger.write(output)
            merger.close()
            print(f"✅ Successfully wrote to {output_file}")
        except Exception as e:
            print(f"❌ Error writing output file: {e}")
            print("Make sure no PDF viewer has the file open")
            return False
        
        # Get final statistics
        file_size = os.path.getsize(output_file)
        
        # Count pages in final PDF
        try:
            with open(output_file, 'rb') as f:
                reader = PyPDF2.PdfFileReader(f)
                total_pages = reader.numPages
        except:
            total_pages = "Unknown"
        
        print(f"✅ Successfully merged {successful_merges} PDFs")
        print(f"📊 Total pages: {total_pages}")
        print(f"💾 Output file: {output_file}")
        print(f"📏 File size: {file_size / 1024 / 1024:.1f} MB")
        
        # Test first page to verify content
        try:
            with open(output_file, 'rb') as f:
                reader = PyPDF2.PdfFileReader(f)
                if reader.numPages > 0:
                    page = reader.getPage(0)
                    text = page.extractText()
                    if len(text) > 0:
                        print(f"✅ Content verified: First page has {len(text)} characters")
                    else:
                        print("⚠️  First page appears blank")
        except Exception as e:
            print(f"⚠️  Could not verify content: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during merging: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("FINAL PDF MERGER FOR PRINTING")
    print("=" * 35)
    merge_all_pdfs()