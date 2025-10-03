import pandas as pd
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import base64
import os
from pathlib import Path
import time

def setup_brevo_client(api_key):
    """Setup Brevo API client"""
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key
    return sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

def send_policy_emails():
    """Send emails with PDF attachments using Brevo"""
    
    # CONFIGURATION - UPDATE THESE VALUES
    SENDER_EMAIL = "CashBack@niclmauritius.site"    # Your verified sender email
    SENDER_NAME = "NIC Life Insurance Mauritius"     # Your company name
    REPLY_TO_EMAIL = "customerservice@nicl.mu"            # Reply-to email
    REPLY_TO_NAME = "NIC Life Insurance"             # Reply-to name
    
    # Verify sender email first
    print(f"🔍 Using sender: {SENDER_NAME} <{SENDER_EMAIL}>")
    print(f"📧 Reply-to: {REPLY_TO_NAME} <{REPLY_TO_EMAIL}>")
    print("⚠️  IMPORTANT: Make sure sender domain is verified in your Brevo account!")
    
    # Email template - subject line with dynamic policy number
    SUBJECT_TEMPLATE = "NIC Life Insurance - Cash Back Benefit - Policy {policy_number}"
    # Professional HTML email template with formal content
    EMAIL_TEMPLATE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NIC Life Insurance - Cash Back Benefit</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    
    <!-- Main Content -->
    <div style="background: #ffffff; padding: 30px 20px;
        
        <p style="font-size: 16px; margin-bottom: 20px;">Dear Valued Client,</p>
        
        <p style="font-size: 14px; margin-bottom: 20px;">
            Greetings from NIC.
        </p>
        
        <p style="font-size: 14px; margin-bottom: 20px;">
            We are pleased to inform you that you are entitled to a <strong>Cash Back benefit</strong> under your Life Insurance Policy.
        </p>
        
        <!-- Policy Info Box -->
        <table style="width: 100%; background-color: #f8f9fa; border-left: 4px solid #2c3e50; margin: 20px 0;" cellpadding="15" cellspacing="0">
            <tr>
                <td>
                    <p style="margin: 0; font-size: 16px;"><strong>Policy Number:</strong> <span style="color: #2c3e50; font-weight: bold;">{policy_number}</span></p>
                </td>
            </tr>
        </table>
        
        <p style="font-size: 14px; margin-bottom: 15px;">
            Please find attached the following documents for your reference:
        </p>
        
        <ul style="font-size: 14px; margin-bottom: 20px; padding-left: 20px;">
            <li style="margin-bottom: 8px;">Cash Back Letter</li>
            <li style="margin-bottom: 8px;">Cash Back Form</li>
        </ul>
        
        <!-- Security Notice -->
        <p style="font-size: 14px; margin-bottom: 20px;">
            <strong>Security Information:</strong> For your security, the attached PDF is password-protected. Please use your <strong>National Identity Number</strong> as the password to open the file.
        </p>
        
        <!-- Instructions -->
        <div style="background-color: #e8f4fd; border: 1px solid #bee5eb; padding: 20px; margin: 25px 0;">
            <h3 style="color: #0c5460; margin: 0 0 15px 0; font-size: 16px; font-weight: bold;">Next Steps</h3>
            <p style="margin: 0 0 15px 0; font-size: 14px; color: #0c5460;">
                To proceed, kindly reply directly to this email with the following documents attached:
            </p>
            <ul style="font-size: 14px; color: #0c5460; margin: 0; padding-left: 20px;">
                <li style="margin-bottom: 8px;">The completed and signed Cash Back form (both signatures are required for joint policies).</li>
                <li style="margin-bottom: 8px;">A copy of your ID (copies of both IDs are required for joint policies).</li>
                <li style="margin-bottom: 8px;">The upper part of your bank statement (for joint life policies, a joint bank account is required. If you do not hold one, please visit the nearest NIC branch to complete the Cash Back formalities).</li>
            </ul>
        </div>
        
        <p style="font-size: 14px; margin-bottom: 20px;">
            Should you require any further assistance, our Customer Service team is available on <strong>602 3000</strong>, Monday to Friday, from 08:30 to 16:45.
        </p>
        

        
        <p style="font-size: 14px; margin-bottom: 30px;">
            Kind Regards,<br>
            <strong>NIC - Serving you, Serving the Nation</strong>
        </p>
        
    </div>
    

    
</body>
</html>
"""

    # Plain text version for email clients that don't support HTML
    EMAIL_TEMPLATE_TEXT = """
Dear Valued Client,

Greetings from NIC.

We are pleased to inform you that you are entitled to a CASH BACK BENEFIT under your Life Insurance Policy.

Policy Number: {policy_number}

Please find attached the following documents for your reference:
- Cash Back Letter
- Cash Back Form

For your security, the attached PDF is password-protected. Please use your National Identity number as the password to open the file.

To proceed, kindly reply directly to this email with the following documents attached:
- The completed and signed Cash Back form (both signatures are required for joint policies).
- A copy of your ID (copies of both IDs are required for joint policies).
- The upper part of your bank statement (for joint life policies, a joint bank account is required. If you do not hold one, please visit the nearest NIC branch to complete the Cash Back formalities).

Should you require any further assistance, our Customer Service team is available on 602 3000, Monday to Friday, from 08:30 to 16:45.

Kind Regards,
NIC - Serving you, Serving the Nation

"""
    
    # Get API key from environment variable
    BREVO_API_KEY = os.getenv('BREVO_API_KEY')
    if not BREVO_API_KEY:
        print("❌ Error: BREVO_API_KEY environment variable not set")
        print("Please set your Brevo API key as an environment variable:")
        print("Windows: set BREVO_API_KEY=your-api-key-here")
        print("Linux/Mac: export BREVO_API_KEY=your-api-key-here")
        return
    
    # Setup Brevo client
    try:
        api_instance = setup_brevo_client(BREVO_API_KEY)
        print("✅ Brevo API client initialized successfully")
    except Exception as e:
        print(f"❌ Error setting up Brevo client: {e}")
        return
    
    # Read Excel file to get policy-email mapping
    try:
        # Try multiple Excel file locations
        excel_files = [
            "Compile CBOpt Nov25.xlsx",
            "/var/www/cashback/storage/uploaded_files/latest_excel.xlsx"
        ]
        df = None
        for excel_file in excel_files:
            if os.path.exists(excel_file):
                df = pd.read_excel(excel_file)
                print(f"📊 Using Excel file: {excel_file}")
                break
        if df is None:
            df = pd.read_excel("Compile CBOpt Nov25.xlsx")  # fallback
        print(f"📊 Loaded {len(df)} policies from Excel")
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return
    
    # Check if /var/www/cashback/storage/generated_pdfs/with_email folder exists
    pdf_folder = Path("/var/www/cashback/storage/generated_pdfs/with_email")
    if not pdf_folder.exists():
        print("❌ '/var/www/cashback/storage/generated_pdfs/with_email' folder not found. Run create_complete_analysis.py first.")
        return
    
    # Get list of available PDF files
    pdf_files = list(pdf_folder.glob("*.pdf"))
    print(f"📁 Found {len(pdf_files)} PDF files ready for sending")
    
    # Create policy-email mapping
    policy_email_map = {}
    for _, row in df.iterrows():
        policy_str = str(row['Policy No'])
        email = row['Owner 1 Email']
        if pd.notna(email) and email.strip():  # Check for valid email
            policy_email_map[policy_str] = email
    
    print(f"📧 Found {len(policy_email_map)} valid email addresses")
    
    # Send emails
    sent_count = 0
    failed_count = 0
    failed_policies = []
    
    for pdf_file in pdf_files:
        # Extract policy number from filename
        filename = pdf_file.stem  # filename without extension
        
        # Convert filename back to policy format for lookup
        if '_' in filename and not filename.isdigit():
            # Slash format: 00407_0054316 -> 00407/0054316
            policy_lookup = filename.replace('_', '/', 1)
        else:
            # Numeric format: 29031933 -> 29031933
            policy_lookup = filename
        
        # Find email for this policy
        if policy_lookup not in policy_email_map:
            print(f"⚠️  No email found for policy: {policy_lookup}")
            failed_count += 1
            failed_policies.append(policy_lookup)
            continue
        
        recipient_email = policy_email_map[policy_lookup]
        
        try:
            # Read PDF file and encode to base64
            with open(pdf_file, 'rb') as f:
                pdf_content = f.read()
                pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            
            # Extract customer name (basic extraction from policy number)
            customer_name = "Valued Client"  # Updated to match the formal greeting
            
            # Create dynamic subject line with policy number
            email_subject = SUBJECT_TEMPLATE.format(policy_number=policy_lookup)
            
            # Prepare email content (both HTML and text versions)
            email_content_html = EMAIL_TEMPLATE_HTML.format(
                customer_name=customer_name,
                policy_number=policy_lookup,
                sender_name=SENDER_NAME
            )
            
            email_content_text = EMAIL_TEMPLATE_TEXT.format(
                customer_name=customer_name,
                policy_number=policy_lookup,
                sender_name=SENDER_NAME
            )
            
            # Create email object with professional HTML template
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": recipient_email}],
                sender={"name": SENDER_NAME, "email": SENDER_EMAIL},
                reply_to={"name": REPLY_TO_NAME, "email": REPLY_TO_EMAIL},
                subject=email_subject,
                html_content=email_content_html,
                text_content=email_content_text,
                attachment=[{
                    "content": pdf_base64,
                    "name": f"Policy_{filename}.pdf"
                }]
            )
            
            # Send email
            api_response = api_instance.send_transac_email(send_smtp_email)
            print(f"✅ Sent to {recipient_email} - Policy: {policy_lookup}")
            sent_count += 1
            
            # Rate limiting - Brevo free tier has limits
            time.sleep(0.1)  # Small delay between emails
            
        except ApiException as e:
            # Enhanced error reporting for Brevo API errors
            error_details = str(e)
            if "401" in error_details:
                error_reason = "Invalid API key or authentication failed"
            elif "402" in error_details:
                error_reason = "Insufficient credits or plan limit exceeded"
            elif "400" in error_details:
                error_reason = "Invalid email format or request data"
            elif "403" in error_details:
                error_reason = "Sender domain not verified or forbidden"
            elif "429" in error_details:
                error_reason = "Rate limit exceeded - too many requests"
            elif "500" in error_details:
                error_reason = "Brevo server error - temporary issue"
            else:
                error_reason = f"API Error: {error_details}"
            
            print(f"❌ Failed to send to {recipient_email} - Policy: {policy_lookup}")
            print(f"   Reason: {error_reason}")
            failed_count += 1
            failed_policies.append(policy_lookup)
            
        except Exception as e:
            print(f"❌ Unexpected error for policy {policy_lookup} - Email: {recipient_email}")
            print(f"   Reason: {str(e)}")
            failed_count += 1
            failed_policies.append(policy_lookup)
    
    # Final summary
    print(f"\n🎉 EMAIL SENDING COMPLETED!")
    print(f"📊 SUMMARY:")
    print(f"- Total PDFs processed: {len(pdf_files)}")
    print(f"- Emails sent successfully: {sent_count}")
    print(f"- Failed to send: {failed_count}")
    print(f"- Success rate: {sent_count/(sent_count+failed_count)*100:.1f}%")
    
    if failed_policies:
        print(f"\n⚠️  Failed policies:")
        for policy in failed_policies[:10]:  # Show first 10
            print(f"   - {policy}")
        if len(failed_policies) > 10:
            print(f"   ... and {len(failed_policies)-10} more")
    
    # Create sending report
    report_content = f"""EMAIL SENDING REPORT - BREVO
============================

SUMMARY:
- Total PDFs processed: {len(pdf_files)}
- Emails sent successfully: {sent_count}
- Failed to send: {failed_count}
- Success rate: {sent_count/(sent_count+failed_count)*100:.1f}%

CONFIGURATION USED:
- Sender: {SENDER_NAME} <{SENDER_EMAIL}>
- Subject Template: {SUBJECT_TEMPLATE}
- API: Brevo (Sendinblue)

FAILED POLICIES:
{chr(10).join([f"- {policy}" for policy in failed_policies])}

NEXT STEPS:
- Review failed policies and retry if needed
- Check Brevo dashboard for delivery statistics
- Monitor bounce rates and spam reports
"""
    
    with open("/var/www/cashback/storage/email_sending_report.txt", "w") as f:
        f.write(report_content)
    
    print(f"\n📄 Detailed report saved to: /var/www/cashback/storage/email_sending_report.txt")

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    os.system("pip install sib-api-v3-sdk pandas")

if __name__ == "__main__":
    import sys
    
    # Check if running in automated mode (from web interface)
    automated_mode = len(sys.argv) > 1 and sys.argv[1] == "--automated"
    
    if not automated_mode:
        print("BREVO EMAIL SENDER FOR POLICY DOCUMENTS")
        print("=" * 50)
        print()
        print("⚠️  BEFORE RUNNING:")
        print("1. Get your Brevo API key from: https://app.brevo.com/settings/keys/api")
        print("2. Set BREVO_API_KEY environment variable with your API key")
        print("3. Update SENDER_EMAIL, SENDER_NAME, and REPLY_TO_EMAIL in this script")
        print("4. Make sure your sender email is verified in Brevo")
        print("5. Run 'create_complete_analysis.py' first to generate PDF files")
        print()
        
        choice = input("Do you want to proceed? (y/n): ").lower().strip()
        if choice != 'y':
            print("Email sending cancelled.")
            sys.exit(0)
    
    # Check if required packages are installed
    try:
        import sib_api_v3_sdk
    except ImportError:
        if not automated_mode:
            install_requirements()
        else:
            print("❌ Required package sib_api_v3_sdk not installed")
            sys.exit(1)
    
    # Run the email sending
    try:
        send_policy_emails()
    except Exception as e:
        print(f"❌ Email sending failed: {str(e)}")
        sys.exit(1)