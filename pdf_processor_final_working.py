import streamlit as st
import pandas as pd
import PyPDF2
import re
import os
import zipfile
import time
from pathlib import Path
from io import BytesIO

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, continue without it
    pass

# Environment detection and path setup
def get_base_paths():
    """Get appropriate paths based on environment"""
    if os.path.exists("/var/www/cashback"):
        # VPS/Linux environment
        base_path = Path("/var/www/cashback")
        storage_path = base_path / "storage"
        temp_path = base_path / "temp"
    else:
        # Local/Windows environment
        base_path = Path(".")
        storage_path = base_path / "storage"
        temp_path = base_path / "temp"
    
    # Create directories if they don't exist
    storage_path.mkdir(exist_ok=True)
    temp_path.mkdir(exist_ok=True)
    (storage_path / "generated_pdfs" / "with_email").mkdir(parents=True, exist_ok=True)
    (storage_path / "generated_pdfs" / "without_email").mkdir(parents=True, exist_ok=True)
    
    return base_path, storage_path, temp_path

# Initialize paths
BASE_PATH, STORAGE_PATH, TEMP_PATH = get_base_paths()

# Authentication configuration
AUTHORIZED_EMAILS = [
    "nbeesoo@nicl.mu",
    "skhodabux@nicl.mu", 
    "vikas.khanna@zwennpay.com"
]

def generate_otp():
    """Generate a 6-digit OTP"""
    import random
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    """Send OTP via email using Brevo"""
    try:
        import sib_api_v3_sdk
        from sib_api_v3_sdk.rest import ApiException
        
        # Get API key
        BREVO_API_KEY = os.getenv('BREVO_API_KEY')
        if not BREVO_API_KEY:
            return False, "Brevo API key not configured"
        
        # Setup Brevo client
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = BREVO_API_KEY
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        # Email content
        subject = "NIC Policy Processor - Authentication Code"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center;">
                <h2 style="color: #2c3e50; margin-bottom: 20px;">🔐 Authentication Required</h2>
                <p style="font-size: 16px; margin-bottom: 30px;">Your authentication code for NIC Policy Processor:</p>
                <div style="background: #ffffff; padding: 20px; border-radius: 8px; border: 2px solid #3498db; margin: 20px 0;">
                    <h1 style="color: #3498db; font-size: 36px; margin: 0; letter-spacing: 5px;">{otp}</h1>
                </div>
                <p style="color: #7f8c8d; font-size: 14px; margin-top: 20px;">
                    This code will expire in 10 minutes. Do not share this code with anyone.
                </p>
                <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
                    NIC Life Insurance Mauritius - Secure Access System
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        NIC Policy Processor - Authentication Code
        
        Your authentication code is: {otp}
        
        This code will expire in 10 minutes.
        Do not share this code with anyone.
        
        NIC Life Insurance Mauritius
        """
        
        # Create email
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[sib_api_v3_sdk.SendSmtpEmailTo(email=email)],
            sender=sib_api_v3_sdk.SendSmtpEmailSender(email="CashBack@niclmauritius.site", name="NIC Security"),
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
        # Send email
        api_response = api_instance.send_transac_email(send_smtp_email)
        return True, "OTP sent successfully"
        
    except Exception as e:
        return False, f"Failed to send OTP: {str(e)}"

def show_authentication():
    """Show authentication interface"""
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .auth-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .auth-title {
        color: white;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .auth-subtitle {
        color: rgba(255,255,255,0.9);
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .security-badge {
        background: rgba(255,255,255,0.1);
        border: 2px solid rgba(255,255,255,0.3);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    .otp-display {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 10px;
        letter-spacing: 3px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with company branding
    st.markdown("""
    <div class="auth-container">
        <div class="auth-title">🔐 NIC Policy Processor</div>
        <div class="auth-subtitle">Secure Authentication Portal</div>
        <div style="text-align: center; color: rgba(255,255,255,0.8);">
            <strong>NIC Life Insurance Mauritius</strong><br>
            Authorized Personnel Only
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.otp_sent:
        # Step 1: Email input with enhanced styling
        st.markdown("""
        <div style="background: rgba(0,0,0,0.1); border: 2px solid #4CAF50; 
                    border-radius: 10px; padding: 1rem; margin: 1rem 0;">
            <h3 style="color: #2c3e50; margin: 0; text-align: center;">
                📧 Step 1: Email Verification
            </h3>
            <p style="color: #555; text-align: center; margin: 0.5rem 0;">
                Enter your authorized NIC email address
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create a more visually appealing input
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            email = st.text_input(
                "Email Address",
                placeholder="your.name@nicl.mu",
                help="Only authorized NIC staff can access this system",
                label_visibility="collapsed",
                key="auth_email_input"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🚀 Send Authentication Code", type="primary", use_container_width=True):
                if not email:
                    st.error("❌ Please enter your email address")
                elif email.lower().strip() not in [e.lower() for e in AUTHORIZED_EMAILS]:
                    st.error("❌ Access Denied: Your email address is not authorized to use this system")
                    st.info("📞 Contact IT support if you believe this is an error")
                else:
                # Generate and send OTP
                 otp = generate_otp()
                 success, message = send_otp_email(email, otp)
                
                if success:
                    st.session_state.generated_otp = otp
                    st.session_state.auth_email = email.lower().strip()
                    st.session_state.otp_sent = True
                    st.session_state.otp_timestamp = time.time()
                    
                    # Enhanced success message
                    st.markdown("""
                    <div style="background: linear-gradient(90deg, #4CAF50, #45a049); 
                                color: white; padding: 1rem; border-radius: 10px; 
                                text-align: center; margin: 1rem 0;">
                        <h4 style="margin: 0;">✅ Authentication Code Sent!</h4>
                        <p style="margin: 0.5rem 0;">Check your email for the 6-digit verification code</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    try:
                        st.rerun()
                    except AttributeError:
                        st.experimental_rerun()
                else:
                    st.markdown(f"""
                    <div style="background: linear-gradient(90deg, #f44336, #d32f2f); 
                                color: white; padding: 1rem; border-radius: 10px; 
                                text-align: center; margin: 1rem 0;">
                        <h4 style="margin: 0;">❌ Authentication Failed</h4>
                        <p style="margin: 0.5rem 0;">{message}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    else:
        # Step 2: OTP verification with enhanced styling
        st.markdown("""
        <div style="background: rgba(0,0,0,0.1); border: 2px solid #2196F3; 
                    border-radius: 10px; padding: 1rem; margin: 1rem 0;">
            <h3 style="color: #2c3e50; margin: 0; text-align: center;">
                🔑 Step 2: Enter Authentication Code
            </h3>
            <p style="color: #555; text-align: center; margin: 0.5rem 0;">
                6-digit code sent to: <strong style="color: #2196F3;">{}</strong>
            </p>
        </div>
        """.format(st.session_state.auth_email), unsafe_allow_html=True)
        
        # Check if OTP expired (10 minutes)
        if time.time() - st.session_state.otp_timestamp > 600:
            st.markdown("""
            <div style="background: linear-gradient(90deg, #ff9800, #f57c00); 
                        color: white; padding: 1rem; border-radius: 10px; 
                        text-align: center; margin: 1rem 0;">
                <h4 style="margin: 0;">⏰ Code Expired</h4>
                <p style="margin: 0.5rem 0;">Your authentication code has expired. Please request a new one.</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Request New Code", use_container_width=True, key="request_new_code_expired"):
                    st.session_state.otp_sent = False
                    st.session_state.generated_otp = None
                    try:
                        st.rerun()
                    except AttributeError:
                        st.experimental_rerun()
            return
        
        # Enhanced OTP input section with dynamic timer
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Time remaining display with JavaScript countdown
            time_left = 600 - int(time.time() - st.session_state.otp_timestamp)
            
            # Color changes based on time left
            if time_left > 300:  # More than 5 minutes - green
                timer_color = "#4CAF50"
            elif time_left > 120:  # More than 2 minutes - orange
                timer_color = "#FF9800"
            else:  # Less than 2 minutes - red
                timer_color = "#f44336"
            
            # Simple timer display (no auto-countdown to avoid blocking UI)
            minutes = time_left // 60
            seconds = time_left % 60
            
            st.markdown(f"""
            <div style="background: rgba(0,0,0,0.05); border: 2px solid {timer_color}; 
                        border-radius: 10px; padding: 1rem; text-align: center; margin: 1rem 0;">
                <h4 style="color: {timer_color}; margin: 0;">⏰ Code Expires In</h4>
                <div style="font-size: 2rem; font-weight: bold; color: {timer_color};">
                    {minutes}:{seconds:02d}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # OTP input field
            entered_otp = st.text_input(
                "Authentication Code",
                placeholder="000000",
                max_chars=6,
                help="Enter the 6-digit code from your email",
                label_visibility="collapsed",
                key="otp_input_main"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Verify button
            if st.button("✅ Verify & Access System", type="primary", use_container_width=True, key="verify_otp_main"):
                if not entered_otp:
                    st.markdown("""
                    <div style="background: #f44336; color: white; padding: 0.5rem; 
                                border-radius: 5px; text-align: center; margin: 0.5rem 0;">
                        ❌ Please enter the authentication code
                    </div>
                    """, unsafe_allow_html=True)
                elif entered_otp == st.session_state.generated_otp:
                    st.session_state.authenticated = True
                    st.session_state.auth_timestamp = time.time()
                    
                    st.markdown("""
                    <div style="background: linear-gradient(90deg, #4CAF50, #45a049); 
                                color: white; padding: 1rem; border-radius: 10px; 
                                text-align: center; margin: 1rem 0;">
                        <h3 style="margin: 0;">🎉 Authentication Successful!</h3>
                        <p style="margin: 0.5rem 0;">Welcome to NIC Policy Processor</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                    time.sleep(1)
                    try:
                        st.rerun()
                    except AttributeError:
                        st.experimental_rerun()
                else:
                    st.markdown("""
                    <div style="background: #f44336; color: white; padding: 0.5rem; 
                                border-radius: 5px; text-align: center; margin: 0.5rem 0;">
                        ❌ Invalid code. Please check your email and try again.
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Request new code button
            if st.button("🔄 Send New Code", use_container_width=True, key="send_new_code_first"):
                st.session_state.otp_sent = False
                st.session_state.generated_otp = None
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
            
            # OTP input with custom styling
            entered_otp = st.text_input(
                "Authentication Code",
                placeholder="000000",
                max_chars=6,
                help="Enter the 6-digit code from your email",
                label_visibility="collapsed",
                key="otp_input_expired"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Verify button
            if st.button("✅ Verify & Access System", type="primary", use_container_width=True, key="verify_otp_expired"):
                if not entered_otp:
                    st.markdown("""
                    <div style="background: #f44336; color: white; padding: 0.5rem; 
                                border-radius: 5px; text-align: center; margin: 0.5rem 0;">
                        ❌ Please enter the authentication code
                    </div>
                    """, unsafe_allow_html=True)
                elif entered_otp == st.session_state.generated_otp:
                    st.session_state.authenticated = True
                    st.session_state.auth_timestamp = time.time()
                    
                    st.markdown("""
                    <div style="background: linear-gradient(90deg, #4CAF50, #45a049); 
                                color: white; padding: 1rem; border-radius: 10px; 
                                text-align: center; margin: 1rem 0;">
                        <h3 style="margin: 0;">🎉 Authentication Successful!</h3>
                        <p style="margin: 0.5rem 0;">Welcome to NIC Policy Processor</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                    time.sleep(1)
                    try:
                        st.rerun()
                    except AttributeError:
                        st.experimental_rerun()
                else:
                    st.markdown("""
                    <div style="background: #f44336; color: white; padding: 0.5rem; 
                                border-radius: 5px; text-align: center; margin: 0.5rem 0;">
                        ❌ Invalid code. Please check your email and try again.
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Request new code button
            if st.button("🔄 Send New Code", use_container_width=True, key="send_new_code_second"):
                st.session_state.otp_sent = False
                st.session_state.generated_otp = None
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()

def check_session_timeout():
    """Check if user session has timed out (2 hours)"""
    if st.session_state.authenticated:
        if time.time() - st.session_state.auth_timestamp > 7200:  # 2 hours
            st.session_state.authenticated = False
            st.session_state.auth_email = None
            st.session_state.otp_sent = False
            st.session_state.generated_otp = None
            st.warning("⏰ Session expired. Please authenticate again.")
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()

# Set page config
st.set_page_config(
    page_title="PDF Policy Processor",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'processing_done' not in st.session_state:
    st.session_state.processing_done = False
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'auth_email' not in st.session_state:
    st.session_state.auth_email = None
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False
if 'generated_otp' not in st.session_state:
    st.session_state.generated_otp = None

def process_uploaded_files(pdf_file, excel_file, progress_bar, status_text):
    """Process uploaded PDF and Excel files"""
    
    # Save uploaded files to temp directory
    pdf_path = TEMP_PATH / "temp_uploaded.pdf"
    excel_path = TEMP_PATH / "temp_uploaded.xlsx"
    
    with open(pdf_path, "wb") as f:
        f.write(pdf_file.getvalue())
    
    with open(excel_path, "wb") as f:
        f.write(excel_file.getvalue())
    
    # Read Excel data
    try:
        df = pd.read_excel(excel_path)
        st.success(f"✅ Excel file loaded: {len(df)} policies found")
    except Exception as e:
        st.error(f"❌ Error reading Excel file: {e}")
        return None
    
    # Read PDF and keep file open during processing
    try:
        pdf_file_handle = open(pdf_path, 'rb')
        
        # Handle both old and new PyPDF2 versions
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file_handle)
            total_pages = len(pdf_reader.pages)
        except AttributeError:
            # Older PyPDF2 version
            pdf_reader = PyPDF2.PdfFileReader(pdf_file_handle)
            total_pages = pdf_reader.numPages
        
        st.success(f"✅ PDF file loaded: {total_pages} pages")
    except Exception as e:
        st.error(f"❌ Error reading PDF file: {e}")
        return None
    
    # Create output directories using storage paths
    with_email_dir = STORAGE_PATH / "generated_pdfs" / "with_email"
    without_email_dir = STORAGE_PATH / "generated_pdfs" / "without_email"
    
    with_email_dir.mkdir(parents=True, exist_ok=True)
    without_email_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean old PDF files from previous sessions
    import glob
    for old_file in glob.glob(str(with_email_dir / "*.pdf")):
        os.remove(old_file)
    for old_file in glob.glob(str(without_email_dir / "*.pdf")):
        os.remove(old_file)
    
    st.info("🧹 Cleaned old PDF files from previous sessions")
    
    # First pass: collect all pages for each policy
    policy_pages = {}  # Dictionary to store policy_number -> list of pages
    
    status_text.text("🔍 Scanning PDF for policies...")
    
    try:
        for page_num in range(total_pages):
            progress_bar.progress((page_num + 1) / (total_pages * 2))  # First half of progress
            status_text.text(f"📄 Scanning page {page_num + 1}/{total_pages}")
            
            # Handle both old and new PyPDF2 versions
            try:
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
            except AttributeError:
                # Older PyPDF2 version
                page = pdf_reader.getPage(page_num)
                text = page.extractText()
            
            # Look for policy numbers (both formats: 00407/0054316 and 29031933)
            policy_patterns = [
                r'\b\d{5}/\d{7}\b',  # Format: 00407/0054316
                r'\b\d{8}\b'         # Format: 29031933
            ]
            
            policy_match = None
            for pattern in policy_patterns:
                match = re.search(pattern, text)
                if match:
                    policy_match = match
                    break
            
            if policy_match:
                policy_number = policy_match.group(0)
                if policy_number not in policy_pages:
                    policy_pages[policy_number] = []
                policy_pages[policy_number].append(page_num)
        
        # Second pass: create PDFs for each policy
        policies_found = 0
        for policy_number, pages in policy_pages.items():
            progress_bar.progress(0.5 + (policies_found + 1) / (len(policy_pages) * 2))  # Second half
            status_text.text(f"💾 Creating PDF for policy {policy_number} ({len(pages)} pages)")
            
            save_policy_pdf(pdf_reader, pages, policy_number, df, with_email_dir, without_email_dir)
            policies_found += 1
        
    finally:
        # Close the PDF file
        pdf_file_handle.close()
        
        # Clean up temp PDF file (but keep Excel file for email sending)
        try:
            os.remove(pdf_path)
            # Keep excel_path for email sending - don't delete it
        except:
            pass
    
    # Count results
    policies_with_email = len(list(with_email_dir.glob("*.pdf")))
    policies_without_email = len(list(without_email_dir.glob("*.pdf")))
    
    status_text.text("✅ Processing completed!")
    progress_bar.progress(1.0)
    
    return {
        'total_found': policies_found,
        'with_email': policies_with_email,
        'without_email': policies_without_email
    }

def save_policy_pdf(pdf_reader, page_numbers, policy_number, df, with_email_dir, without_email_dir):
    """Save individual policy as PDF with password protection"""
    
    # Check if policy has email and NIC
    has_email = False
    email = None
    nic_password = None
    
    # Look for policy in Excel (try both formats) - using column names for flexibility
    for _, row in df.iterrows():
        # Get policy number from first column or 'Policy No' column
        if 'Policy No' in df.columns:
            excel_policy = str(row['Policy No']).strip()
        else:
            excel_policy = str(row.iloc[0]).strip()
        
        # Get email from 'Owner 1 Email' column or similar
        excel_email = None
        for email_col in ['Owner 1 Email', 'Email', 'Owner Email', 'email']:
            if email_col in df.columns and pd.notna(row[email_col]):
                excel_email = str(row[email_col]).strip()
                break
        
        # Get NIC from 'NIC' column
        excel_nic = None
        if 'NIC' in df.columns and pd.notna(row['NIC']):
            excel_nic = str(row['NIC']).strip()
        
        # Check if policies match (handle different formats)
        if (excel_policy == policy_number or 
            excel_policy.replace('/', '') == policy_number.replace('/', '') or
            excel_policy.lstrip('0') == policy_number.lstrip('0')):
            
            if excel_email and '@' in excel_email:
                has_email = True
                email = excel_email
            
            if excel_nic:
                nic_password = excel_nic
            
            break
    
    # Create new PDF - handle both old and new PyPDF2 versions
    try:
        from PyPDF2 import PdfWriter
        writer = PdfWriter()
        
        for page_num in page_numbers:
            try:
                if page_num < len(pdf_reader.pages):
                    writer.add_page(pdf_reader.pages[page_num])
            except AttributeError:
                # Older PyPDF2 version
                if page_num < pdf_reader.numPages:
                    writer.addPage(pdf_reader.getPage(page_num))
    except ImportError:
        # Very old PyPDF2 version
        from PyPDF2 import PdfFileWriter
        writer = PdfFileWriter()
        
        for page_num in page_numbers:
            if page_num < pdf_reader.numPages:
                writer.addPage(pdf_reader.getPage(page_num))
    
    # Add password protection ONLY if policy has email (will be sent electronically)
    if has_email and nic_password:
        try:
            # For newer PyPDF2 versions
            writer.encrypt(nic_password)
        except AttributeError:
            try:
                # For older PyPDF2 versions
                writer.encrypt(user_pwd=nic_password, owner_pwd=nic_password)
            except:
                # If encryption fails, continue without password
                st.warning(f"⚠️ Could not encrypt PDF for policy {policy_number}")
    elif has_email and not nic_password:
        st.warning(f"⚠️ Policy {policy_number} has email but no NIC for password protection")
    
    # Save to appropriate folder
    folder = with_email_dir if has_email else without_email_dir
    # Replace invalid filename characters
    safe_policy_number = policy_number.replace('/', '_').replace('\\', '_')
    filename = f"{safe_policy_number}.pdf"
    filepath = Path(folder) / filename
    
    with open(filepath, 'wb') as output_file:
        writer.write(output_file)

def create_download_zip(folder_path, zip_name):
    """Create ZIP file for download"""
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        folder = Path(folder_path)
        for file_path in folder.glob("*.pdf"):
            zip_file.write(file_path, file_path.name)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()



def check_excel_file_exists():
    """Check if Excel file exists for email sending"""
    excel_locations = [
        "Compile CBOpt Nov25.xlsx",  # Legacy filename
        STORAGE_PATH / "uploaded_files" / "latest_excel.xlsx",
        TEMP_PATH / "temp_uploaded.xlsx"
    ]
    
    for location in excel_locations:
        if Path(location).exists():
            return str(location)
    return None

def check_pdf_files_exist():
    """Check if PDF files exist for email sending"""
    pdf_locations = [
        "policies_with_email",  # Legacy folder
        STORAGE_PATH / "generated_pdfs" / "with_email"
    ]
    
    for location in pdf_locations:
        if Path(location).exists():
            pdf_files = list(Path(location).glob("*.pdf"))
            if pdf_files:
                return len(pdf_files)
    return 0

def check_pdf_files_without_email():
    """Check if PDF files exist without email addresses (for printing)"""
    pdf_locations = [
        "policies_without_email",  # Legacy folder
        STORAGE_PATH / "generated_pdfs" / "without_email"
    ]
    
    for location in pdf_locations:
        if Path(location).exists():
            pdf_files = list(Path(location).glob("*.pdf"))
            if pdf_files:
                return len(pdf_files)
    return 0

def send_emails_via_subprocess():
    """Send emails using subprocess to run the existing email script"""
    import subprocess
    import sys
    
    st.subheader("📧 Sending Emails...")
    
    # Create placeholders for real-time updates
    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    metrics_placeholder = st.empty()
    output_placeholder = st.empty()
    
    try:
        # Prepare the command with automated flag
        cmd = [sys.executable, "send_emails_brevo.py", "--automated"]
        
        # Set up environment variables
        env = os.environ.copy()
        env['BREVO_API_KEY'] = os.getenv('BREVO_API_KEY', '')
        
        if not env['BREVO_API_KEY']:
            st.error("❌ BREVO_API_KEY not set. Please set your API key in environment variables.")
            st.code("set BREVO_API_KEY=your-api-key-here")
            return
        
        status_placeholder.info("🚀 Starting email sending process...")
        
        # Start the subprocess with UTF-8 encoding
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=env,
            encoding='utf-8',
            errors='replace'
        )
        
        # Initialize counters and timing
        sent_count = 0
        failed_count = 0
        total_count = 0
        output_lines = []
        failed_emails = []  # Track failed emails with details
        successful_emails = []  # Track successful emails
        start_time = time.time()
        last_email_time = start_time
        
        # Initialize/clear email results in session state for new sending session
        st.session_state.email_results = []
        
        # Read output in real-time
        while True:
            try:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    output_lines.append(line)
            except UnicodeDecodeError as e:
                # Handle encoding errors gracefully
                line = f"⚠️ Encoding error in output: {str(e)}"
                output_lines.append(line)
                continue
                
                # Parse different types of output
                if "✅ Sent to" in line:
                    sent_count += 1
                    last_email_time = time.time()
                    
                    # Extract email and policy info from success message
                    # Format: "✅ Sent to email@domain.com - Policy: 12345"
                    import re
                    match = re.search(r'✅ Sent to (.+?) - Policy: (.+)', line)
                    if match:
                        email, policy = match.groups()
                        email_info = {
                            'email': email.strip(),
                            'policy': policy.strip(),
                            'timestamp': time.strftime("%H:%M:%S")
                        }
                        successful_emails.append(email_info)
                        
                        # Store in session state for CSV
                        st.session_state.email_results.append({
                            'email': email.strip(),
                            'policy': policy.strip(),
                            'status': 'Success',
                            'timestamp': time.strftime("%H:%M:%S"),
                            'details': 'Email sent successfully'
                        })
                    
                    status_placeholder.success(f"📧 Successfully sent email #{sent_count}")
                    
                elif "❌ Failed to send to" in line:
                    failed_count += 1
                    
                    # Extract failure details
                    # Format: "❌ Failed to send to email@domain.com - Policy: 12345"
                    import re
                    match = re.search(r'❌ Failed to send to (.+?) - Policy: (.+)', line)
                    if match:
                        email, policy = match.groups()
                        failed_info = {
                            'email': email.strip(),
                            'policy': policy.strip(),
                            'reason': line.strip(),
                            'timestamp': time.strftime("%H:%M:%S")
                        }
                        failed_emails.append(failed_info)
                        
                        # Store in session state for CSV
                        st.session_state.email_results.append({
                            'email': email.strip(),
                            'policy': policy.strip(),
                            'status': 'Failed',
                            'timestamp': time.strftime("%H:%M:%S"),
                            'details': failed_info['reason']
                        })
                    
                    status_placeholder.error(f"❌ Email failed (Total failures: {failed_count})")
                elif "📊 Loaded" in line and "policies" in line:
                    # Extract total count from "📊 Loaded X policies from Excel"
                    import re
                    match = re.search(r'(\d+) policies', line)
                    if match:
                        total_count = int(match.group(1))
                elif "📁 Found" in line and "PDF files" in line:
                    progress_placeholder.info(line)
                elif "🎉 EMAIL SENDING COMPLETED" in line:
                    status_placeholder.success("🎉 Email sending completed!")
                
                # Update progress bar and metrics
                if total_count > 0:
                    processed = sent_count + failed_count
                    progress = processed / total_count
                    remaining = total_count - processed
                    
                    # Calculate estimated time remaining
                    elapsed_time = time.time() - start_time
                    if processed > 0:
                        avg_time_per_email = elapsed_time / processed
                        eta_seconds = avg_time_per_email * remaining
                        eta_minutes = int(eta_seconds // 60)
                        eta_seconds = int(eta_seconds % 60)
                        eta_text = f" (ETA: {eta_minutes}m {eta_seconds}s)" if remaining > 0 else " (Complete!)"
                    else:
                        eta_text = ""
                    
                    # Enhanced progress bar with detailed info
                    progress_placeholder.progress(
                        progress, 
                        f"📊 Progress: {processed}/{total_count} emails processed ({progress*100:.1f}%){eta_text}"
                    )
                    
                    # Real-time metrics
                    with metrics_placeholder.container():
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("✅ Sent", sent_count, delta=None)
                        with col2:
                            st.metric("❌ Failed", failed_count, delta=None)
                        with col3:
                            st.metric("⏳ Remaining", remaining, delta=None)
                        with col4:
                            success_rate = (sent_count / processed * 100) if processed > 0 else 0
                            st.metric("📈 Success Rate", f"{success_rate:.1f}%", delta=None)
                
                # Show recent output with better formatting
                if output_lines:
                    recent_output = "\n".join(output_lines[-8:])  # Show last 8 lines
                    output_placeholder.text_area("📋 Recent Activity:", recent_output, height=180)
        
        # Wait for process to complete
        return_code = process.wait()
        
        # Load results from file
        results_file = TEMP_PATH / "email_results.json"
        if results_file.exists():
            try:
                import json
                with open(results_file, 'r') as f:
                    file_results = json.load(f)
                
                # Add file results to session state
                st.session_state.email_results.extend(file_results)
                
            except Exception as e:
                pass  # Silently handle file reading errors
        
        # Show final results with enhanced feedback
        total_time = time.time() - start_time
        total_minutes = int(total_time // 60)
        total_seconds = int(total_time % 60)
        
        if return_code == 0:
            st.success(f"🎉 Email sending completed successfully in {total_minutes}m {total_seconds}s!")
            st.balloons()
            
            # Show completion progress bar at 100%
            progress_placeholder.progress(1.0, "✅ All emails processed - 100% Complete!")
        else:
            st.error(f"❌ Email sending failed with return code: {return_code} after {total_minutes}m {total_seconds}s")
        
        # Show comprehensive final summary
        if sent_count > 0 or failed_count > 0:
            st.markdown("---")
            st.subheader("📊 Email Delivery Report")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("✅ Sent", sent_count)
            with col2:
                st.metric("❌ Failed", failed_count)
            with col3:
                success_rate = (sent_count / (sent_count + failed_count) * 100) if (sent_count + failed_count) > 0 else 0
                st.metric("📊 Success Rate", f"{success_rate:.1f}%")
            with col4:
                st.metric("⏱️ Total Time", f"{total_minutes}m {total_seconds}s")
            
            # Detailed reports in tabs
            tab1, tab2, tab3 = st.tabs(["❌ Failed Emails", "✅ Successful Emails", "📋 Summary"])
            
            with tab1:
                if failed_emails:
                    st.error(f"⚠️ {len(failed_emails)} emails failed to send")
                    
                    # Create DataFrame for failed emails
                    failed_df = pd.DataFrame(failed_emails)
                    
                    # Display failed emails table
                    st.dataframe(
                        failed_df,
                        column_config={
                            "email": "📧 Email Address",
                            "policy": "📄 Policy Number", 
                            "reason": "❌ Failure Reason",
                            "timestamp": "⏰ Time"
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # Download failed emails as CSV
                    csv_data = failed_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Failed Emails Report",
                        data=csv_data,
                        file_name=f"failed_emails_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                    # Common failure reasons and solutions
                    st.markdown("### 🔧 Common Issues & Solutions")
                    st.info("""
                    **Common failure reasons:**
                    - **Invalid email format**: Check email addresses in Excel file
                    - **Brevo API limits**: Check your Brevo plan limits
                    - **Network timeout**: Retry sending failed emails
                    - **Sender domain not verified**: Verify domain in Brevo dashboard
                    """)
                    
                else:
                    st.success("🎉 All emails were sent successfully!")
            
            with tab2:
                if successful_emails:
                    st.success(f"✅ {len(successful_emails)} emails sent successfully")
                    
                    # Create DataFrame for successful emails
                    success_df = pd.DataFrame(successful_emails)
                    
                    # Display successful emails table
                    st.dataframe(
                        success_df,
                        column_config={
                            "email": "📧 Email Address",
                            "policy": "📄 Policy Number",
                            "timestamp": "⏰ Time Sent"
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # Download successful emails as CSV
                    csv_data = success_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Successful Emails Report",
                        data=csv_data,
                        file_name=f"successful_emails_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("❌ No emails were sent successfully")
            
            with tab3:
                st.markdown("### 📈 Delivery Statistics")
                
                # Create summary statistics
                total_processed = sent_count + failed_count
                if total_processed > 0:
                    # Success rate chart
                    chart_data = pd.DataFrame({
                        'Status': ['Successful', 'Failed'],
                        'Count': [sent_count, failed_count],
                        'Percentage': [
                            (sent_count / total_processed) * 100,
                            (failed_count / total_processed) * 100
                        ]
                    })
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.bar_chart(chart_data.set_index('Status')['Count'])
                    
                    with col2:
                        st.markdown(f"""
                        **📊 Summary Statistics:**
                        - **Total Processed**: {total_processed} emails
                        - **Success Rate**: {success_rate:.1f}%
                        - **Average Speed**: {total_processed / (total_time / 60):.1f} emails/minute
                        - **Processing Time**: {total_minutes}m {total_seconds}s
                        """)
                
                # Recommendations based on results
                if failed_count > 0:
                    failure_rate = (failed_count / total_processed) * 100
                    if failure_rate > 20:
                        st.warning("⚠️ High failure rate detected. Consider checking email addresses and Brevo account status.")
                    elif failure_rate > 10:
                        st.info("💡 Some emails failed. Review the failed emails report for details.")
                    else:
                        st.success("✅ Low failure rate. Most emails were delivered successfully.")
                else:
                    st.success("🎉 Perfect delivery! All emails were sent successfully.")
            
            
        # Add comprehensive CSV download (moved outside tabs for visibility)
        if sent_count > 0 or failed_count > 0:
            st.markdown("---")
            st.subheader("📥 Download Complete Report")
            
            # Create comprehensive report combining all data
            all_emails_data = []
            
            # Add successful emails
            for email_info in successful_emails:
                all_emails_data.append({
                    'Email': email_info['email'],
                    'Policy_Number': email_info['policy'],
                    'Status': 'Success',
                    'Timestamp': email_info['timestamp'],
                    'Details': 'Email sent successfully'
                })
            
            # Add failed emails
            for email_info in failed_emails:
                all_emails_data.append({
                    'Email': email_info['email'],
                    'Policy_Number': email_info['policy'],
                    'Status': 'Failed',
                    'Timestamp': email_info['timestamp'],
                    'Details': email_info['reason']
                })
            
            if all_emails_data:
                # Create comprehensive DataFrame
                complete_df = pd.DataFrame(all_emails_data)
                
                # Sort by timestamp for chronological order
                complete_df = complete_df.sort_values('Timestamp')
                
                # Add summary information at the top
                summary_data = {
                    'Email': ['SUMMARY', 'SUMMARY', 'SUMMARY', 'SUMMARY'],
                    'Policy_Number': ['', '', '', ''],
                    'Status': ['Total Processed', 'Successful', 'Failed', 'Success Rate'],
                    'Timestamp': [time.strftime('%Y-%m-%d %H:%M:%S'), '', '', ''],
                    'Details': [
                        f'{sent_count + failed_count} emails',
                        f'{sent_count} emails',
                        f'{failed_count} emails',
                        f'{(sent_count / (sent_count + failed_count) * 100) if (sent_count + failed_count) > 0 else 0:.1f}%'
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                final_df = pd.concat([summary_df, complete_df], ignore_index=True)
                
                # Create CSV data
                csv_data = final_df.to_csv(index=False)
                
                # Download button for complete report
                st.download_button(
                    label="📊 Download Complete Email Report (CSV)",
                    data=csv_data,
                    file_name=f"email_delivery_report_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download a comprehensive CSV report with all email delivery details",
                    use_container_width=True
                )
                
                # Show preview of the data
                with st.expander("👀 Preview Complete Report"):
                    st.dataframe(
                        final_df,
                        column_config={
                            "Email": "�  Email Address",
                            "Policy_Number": "📄 Policy Number",
                            "Status": "� Steatus",
                            "Timestamp": "⏰ Time",
                            "Details": "📝 Details"
                        },
                        hide_index=True,
                        use_container_width=True
                    )
        
        # Show complete output in expander
        if output_lines:
            with st.expander("📋 Complete Log"):
                st.text("\n".join(output_lines))
    
    except Exception as e:
        st.error(f"❌ Error running email script: {str(e)}")
        st.exception(e)

def merge_pdfs_for_printing():
    """Merge PDFs without email addresses into a single printable file"""
    st.subheader("🔗 Merging PDFs for Printing...")
    
    # Create placeholders for updates
    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    details_placeholder = st.empty()
    
    try:
        # Find the correct input folder
        input_folders = [
            "policies_without_email",  # Legacy folder
            str(STORAGE_PATH / "generated_pdfs" / "without_email")
        ]
        
        input_folder = None
        for folder in input_folders:
            if os.path.exists(folder):
                pdf_files = list(Path(folder).glob("*.pdf"))
                if pdf_files:
                    input_folder = folder
                    break
        
        if not input_folder:
            st.error("❌ No PDFs without email addresses found")
            return
        
        output_file = str(STORAGE_PATH / "policies_for_printing.pdf")
        
        status_placeholder.info("🔍 Scanning PDF files...")
        
        # Get all PDF files
        pdf_files = list(Path(input_folder).glob("*.pdf"))
        pdf_files.sort()  # Sort for consistent order
        
        if not pdf_files:
            st.error(f"❌ No PDF files found in '{input_folder}' folder")
            return
        
        status_placeholder.success(f"📁 Found {len(pdf_files)} PDF files to merge")
        
        # Delete existing output file if it exists
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
                status_placeholder.info("🗑️ Removed existing merged file")
            except Exception as e:
                st.error(f"⚠️ Could not delete existing file: {e}")
                st.warning("Please close any PDF viewers and try again")
                return
        
        # Initialize progress tracking
        progress_placeholder.progress(0, "Starting PDF merge...")
        
        # Use PyPDF2 PdfMerger (updated from deprecated PdfFileMerger)
        try:
            merger = PyPDF2.PdfMerger()  # New version
        except AttributeError:
            merger = PyPDF2.PdfFileMerger()  # Fallback for older versions
        successful_merges = 0
        failed_files = []
        
        # Merge PDFs with progress updates
        for i, pdf_path in enumerate(pdf_files):
            try:
                # Update progress
                progress = (i + 1) / len(pdf_files)
                progress_placeholder.progress(
                    progress, 
                    f"Processing {i+1}/{len(pdf_files)}: {pdf_path.name}"
                )
                
                # Add PDF to merger
                merger.append(str(pdf_path))
                successful_merges += 1
                
                # Show details every 10 files or for small batches
                if i % 10 == 0 or len(pdf_files) <= 20:
                    details_placeholder.info(f"📄 Added: {pdf_path.name}")
                
            except Exception as e:
                failed_files.append((pdf_path.name, str(e)))
                details_placeholder.warning(f"⚠️ Skipped {pdf_path.name}: {str(e)}")
                continue
        
        if successful_merges == 0:
            st.error("❌ No PDFs could be merged")
            return
        
        # Write the merged PDF
        status_placeholder.info("💾 Writing merged PDF file...")
        progress_placeholder.progress(0.95, "Finalizing merged PDF...")
        
        try:
            with open(output_file, 'wb') as output:
                merger.write(output)
            merger.close()
            
        except Exception as e:
            st.error(f"❌ Error writing output file: {e}")
            st.warning("Make sure no PDF viewer has the file open")
            return
        
        # Get final statistics
        file_size = os.path.getsize(output_file)
        
        # Count pages in final PDF
        try:
            with open(output_file, 'rb') as f:
                reader = PyPDF2.PdfFileReader(f)
                total_pages = reader.numPages
        except:
            total_pages = "Unknown"
        
        # Complete progress
        progress_placeholder.progress(1.0, "✅ PDF merge completed!")
        
        # Show success message
        st.success("🎉 PDF merging completed successfully!")
        st.balloons()
        
        # Display merge statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📄 PDFs Merged", successful_merges)
        with col2:
            st.metric("📊 Total Pages", total_pages)
        with col3:
            st.metric("💾 File Size", f"{file_size / 1024 / 1024:.1f} MB")
        with col4:
            st.metric("❌ Failed", len(failed_files))
        
        # Download button for the merged PDF
        with open(output_file, 'rb') as f:
            pdf_data = f.read()
        
        st.download_button(
            label="📥 Download Merged PDF for Printing",
            data=pdf_data,
            file_name=f"policies_for_printing_{time.strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        # Show merge details
        with st.expander("📋 Merge Details"):
            st.markdown(f"""
            **📊 Merge Summary:**
            - **Input Folder**: {input_folder}
            - **Output File**: {output_file}
            - **Successfully Merged**: {successful_merges} PDFs
            - **Total Pages**: {total_pages}
            - **File Size**: {file_size / 1024 / 1024:.1f} MB
            """)
            
            if failed_files:
                st.markdown("**⚠️ Failed Files:**")
                for filename, error in failed_files:
                    st.text(f"• {filename}: {error}")
            else:
                st.success("✅ All PDFs merged successfully!")
        
        # Instructions for printing
        st.markdown("---")
        st.info("""
        **🖨️ Printing Instructions:**
        1. Download the merged PDF file above
        2. Open it in a PDF viewer (Adobe Reader, etc.)
        3. Print using your preferred printer settings
        4. Consider duplex printing to save paper
        5. Use the merged file for bulk mailing of policies without email addresses
        """)
        
    except Exception as e:
        st.error(f"❌ Error during PDF merging: {str(e)}")
        st.exception(e)

def main():
    # Check authentication first
    check_session_timeout()
    
    if not st.session_state.authenticated:
        show_authentication()
        return
    
    # Enhanced sidebar with user info
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #4CAF50, #45a049); 
                color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <h4 style="margin: 0; text-align: center;">👤 Authenticated User</h4>
        <p style="margin: 0.5rem 0; text-align: center; font-size: 0.9rem;">
            <strong>{}</strong>
        </p>
        <p style="margin: 0; text-align: center; font-size: 0.8rem; opacity: 0.8;">
            Session Active
        </p>
    </div>
    """.format(st.session_state.auth_email), unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Secure Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.auth_email = None
        st.session_state.otp_sent = False
        st.session_state.generated_otp = None
        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()
    
    # Add company branding to sidebar
    st.sidebar.markdown("""
    <div style="text-align: center; margin-top: 2rem; padding: 1rem; 
                background: rgba(0,0,0,0.05); border-radius: 10px;">
        <h5 style="margin: 0; color: #666;">NIC Life Insurance</h5>
        <p style="margin: 0; font-size: 0.8rem; color: #888;">Mauritius</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.title("📄 PDF Policy Processor")
    st.markdown("Extract individual policies from merged PDF and organize by email availability")
    
    # File uploads
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Upload PDF File")
        pdf_file = st.file_uploader("Choose PDF file", type=['pdf'], key="pdf_uploader")
        if pdf_file:
            st.success(f"✅ PDF uploaded: {pdf_file.name}")
    
    with col2:
        st.subheader("📊 Upload Excel File")
        excel_file = st.file_uploader("Choose Excel file", type=['xlsx', 'xls'], key="excel_uploader")
        if excel_file:
            st.success(f"✅ Excel uploaded: {excel_file.name}")
    
    # Processing section
    if pdf_file and excel_file and not st.session_state.processing_done:
        st.markdown("---")
        
        if st.button("🚀 Process Files", type="primary", key="process_btn"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process files
            with st.spinner("Processing files..."):
                results = process_uploaded_files(pdf_file, excel_file, progress_bar, status_text)
                
                # STORE IN SESSION STATE
                st.session_state.results = results
                st.session_state.processing_done = True
                
                # Force rerun to show results
                st.experimental_rerun()
    
    # Results section - ALWAYS show if we have results in session state
    if st.session_state.results:
        results = st.session_state.results
        
        st.success("🎉 Processing completed!")
        
        # Show results
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Total Policies", results['total_found'])
        with col2:
            st.metric("✅ With Email", results['with_email'])
        with col3:
            st.metric("❌ Without Email", results['without_email'])
        
        # Download options
        st.markdown("---")
        st.subheader("📥 Download Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if results['with_email'] > 0:
                zip_data = create_download_zip(str(STORAGE_PATH / "generated_pdfs" / "with_email"), "policies_with_email.zip")
                st.download_button(
                    label="📧 Download Policies WITH Email",
                    data=zip_data,
                    file_name="policies_with_email.zip",
                    mime="application/zip",
                    key="download_with_email"
                )
        
        with col2:
            if results['without_email'] > 0:
                zip_data = create_download_zip(str(STORAGE_PATH / "generated_pdfs" / "without_email"), "policies_without_email.zip")
                st.download_button(
                    label="❓ Download Policies WITHOUT Email",
                    data=zip_data,
                    file_name="policies_without_email.zip",
                    mime="application/zip",
                    key="download_without_email"
                )
        

        

        
        # Reset button
        st.markdown("---")
        if st.button("🔄 Start Over", key="reset_btn"):
            # Clear session state
            st.session_state.results = None
            st.session_state.processing_done = False
            st.experimental_rerun()
    
    elif pdf_file and excel_file:
        st.info("👆 Click 'Process Files' to extract policies")
    else:
        st.info("👆 Please upload both PDF and Excel files to begin processing")
    
    # Email Management Section
    if st.session_state.processing_done and st.session_state.results:
        st.markdown("---")
        st.header("📧 Email Management")
        
        # Check if we have the necessary files for email sending
        excel_file_exists = check_excel_file_exists()
        pdf_files_exist = check_pdf_files_exist()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Email Readiness Check")
            if excel_file_exists:
                st.success("✅ Excel file with email addresses found")
            else:
                st.error("❌ Excel file not found")
            
            if pdf_files_exist:
                st.success(f"✅ {pdf_files_exist} PDF files ready for sending")
            else:
                st.error("❌ No PDF files found")
        
        with col2:
            st.subheader("🚀 Send Emails")
            if excel_file_exists and pdf_files_exist:
                if st.button("📧 Send Emails Now", type="primary", use_container_width=True):
                    send_emails_via_subprocess()
                
                # Add dynamic CSV download for email list with status
                st.markdown("---")
                st.write("📥 **Download Email List**")
                
                # Create email list CSV with dynamic status
                excel_file = check_excel_file_exists()
                if excel_file:
                    try:
                        df = pd.read_excel(excel_file)
                        
                        # Create email list with status tracking
                        email_list = []
                        for _, row in df.iterrows():
                            policy_str = str(row['Policy No'])
                            email = row['Owner 1 Email']
                            title = row.get('Title', '').strip() if pd.notna(row.get('Title', '')) else ''
                            lastname = row.get('LastName', '').strip() if pd.notna(row.get('LastName', '')) else ''
                            
                            if pd.notna(email) and email.strip():
                                greeting = f"{title} {lastname}".strip() if title and lastname else "Valued Client"
                                
                                # Check if email sending results exist in session state
                                status = 'Ready to Send'
                                timestamp = ''
                                details = 'Pending'
                                
                                if 'email_results' in st.session_state:
                                    # Look for this policy in the results
                                    for result in st.session_state.email_results:
                                        if result['policy'] == policy_str and result['email'] == email.strip():
                                            status = result['status']
                                            timestamp = result.get('timestamp', '')
                                            details = result.get('details', '')
                                            break
                                
                                email_list.append({
                                    'Policy_Number': policy_str,
                                    'Email': email.strip(),
                                    'Title': title,
                                    'LastName': lastname,
                                    'Greeting': greeting,
                                    'Status': status,
                                    'Timestamp': timestamp,
                                    'Details': details
                                })
                        
                        if email_list:
                            email_df = pd.DataFrame(email_list)
                            csv_data = email_df.to_csv(index=False)
                            
                            # Count statuses
                            sent_count = len([e for e in email_list if e['Status'] == 'Success'])
                            failed_count = len([e for e in email_list if e['Status'] == 'Failed'])
                            pending_count = len([e for e in email_list if e['Status'] == 'Ready to Send'])
                            
                            st.download_button(
                                label="📊 Download Email Status Report (CSV)",
                                data=csv_data,
                                file_name=f"email_status_report_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                help="Download the complete email status report with delivery results",
                                use_container_width=True
                            )
                            
                            # Show status summary
                            if sent_count > 0 or failed_count > 0:
                                st.caption(f"📊 Status: ✅ {sent_count} sent, ❌ {failed_count} failed, ⏳ {pending_count} pending")
                            else:
                                st.caption(f"📧 {len(email_list)} emails ready to send")
                            

                                
                    except Exception as e:
                        st.error(f"Error creating email list: {e}")
                        
            else:
                st.button("📧 Send Emails Now", disabled=True, use_container_width=True)
                st.caption("⚠️ Upload and process files first")
        
        # PDF Merging Section for Printing
        st.markdown("---")
        st.header("🖨️ PDF Merging for Printing")
        
        # Check if we have PDFs without email addresses
        pdf_without_email_count = check_pdf_files_without_email()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Printing Readiness Check")
            if pdf_without_email_count > 0:
                st.success(f"✅ {pdf_without_email_count} PDFs ready for printing")
                st.info("💡 These are policies without email addresses that need to be printed and mailed manually.")
            else:
                st.info("ℹ️ No PDFs without email addresses found")
        
        with col2:
            st.subheader("🔗 Merge PDFs")
            if pdf_without_email_count > 0:
                if st.button("🖨️ Create Printable PDF", type="secondary", use_container_width=True):
                    merge_pdfs_for_printing()
            else:
                st.button("🖨️ Create Printable PDF", disabled=True, use_container_width=True)
                st.caption("⚠️ No PDFs without email addresses to merge")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>PDF Policy Processor v1.0 | Built with Streamlit</p>
        <p>Complete workflow: Upload → Process → Send Emails</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()