# NIC Policy Processor - Complete Technical Documentation

## 📋 Project Overview

### **Purpose**
The NIC Policy Processor is a web-based application designed to automate the distribution of insurance policy documents via email. It processes merged PDF files containing multiple policies, extracts individual policies, and sends personalized emails with password-protected attachments.

### **Core Functionality**
1. **PDF Processing** - Split merged PDFs into individual policy documents
2. **Email Distribution** - Send personalized emails with policy attachments
3. **Authentication System** - Secure access with OTP and backup password
4. **Reporting** - Comprehensive delivery tracking and CSV exports
5. **PDF Merging** - Combine policies without emails for printing

### **Target Users**
- NIC Life Insurance Mauritius staff
- Authorized personnel handling policy distribution
- IT administrators managing the system

## 🏗️ System Architecture

### **Technology Stack**
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.8+
- **Email Service**: Brevo API (formerly Sendinblue)
- **PDF Processing**: PyPDF2 library
- **Data Processing**: Pandas for Excel handling
- **Authentication**: Custom OTP system with email verification
- **Deployment**: DigitalOcean VPS with PM2 process management

### **File Structure**
```
/var/www/cashback/
├── pdf_processor_final_working.py    # Main Streamlit application
├── send_emails_brevo.py             # Email sending engine
├── production_config.py             # Production environment settings
├── deploy_production.sh             # Automated deployment script
├── .env                            # Environment variables (API keys)
├── venv/                           # Python virtual environment
├── storage/                        # Application data storage
│   ├── generated_pdfs/
│   │   ├── with_email/            # Policies with email addresses
│   │   └── without_email/         # Policies for manual distribution
│   ├── uploaded_files/            # User uploaded files
│   └── email_results.json         # Email delivery results
├── temp/                          # Temporary processing files
├── backups/                       # Automated backups
└── logs/                          # Application logs
```

## 🔐 Authentication System

### **Security Model**
- **Two-factor authentication** with email verification
- **Authorized email whitelist** (only 3 specific email addresses)
- **Dual authentication methods** (OTP + backup password)
- **Session management** with 2-hour timeout

### **Authorized Users**
```python
AUTHORIZED_EMAILS = [
    "nbeesoo@nicl.mu",
    "skhodabux@nicl.mu", 
    "vikas.khanna@zwennpay.com"
]
BACKUP_PASSWORD = "NICL@2025"
```

### **Authentication Flow**
1. **Email Validation** - Check if email is in authorized list
2. **Method Selection** - Choose OTP or backup password
3. **OTP Method**: Generate 6-digit code → Send via Brevo → Verify input
4. **Password Method**: Validate against backup password
5. **Session Creation** - 2-hour authenticated session
6. **Auto-logout** - Session timeout and manual logout options
## 📄 PDF Processing Engine

### **Input Requirements**
- **PDF File**: Merged document containing multiple policies (typically 50-500 pages)
- **Excel File**: Policy database with columns:
  - `Policy No` - Policy numbers (format: 12345 or 00407/0054316)
  - `Owner 1 Email` - Customer email addresses
  - `NIC` - National Identity numbers (used for PDF passwords)
  - `Title` - Customer titles (Mr., Mrs., Dr., etc.)
  - `LastName` - Customer surnames

### **Processing Algorithm**
1. **PDF Analysis** - Scan each page for policy numbers using regex patterns
2. **Policy Extraction** - Group pages by policy number
3. **Email Matching** - Cross-reference with Excel data
4. **Password Protection** - Encrypt PDFs using NIC numbers
5. **File Organization** - Sort into "with_email" and "without_email" folders

### **Regex Patterns for Policy Detection**
```python
# Primary patterns for policy number detection
patterns = [
    r'Policy No[:\s]*([0-9/]+)',
    r'Policy Number[:\s]*([0-9/]+)', 
    r'Policy[:\s]*([0-9/]+)',
    r'\b(\d{5}/\d{7})\b',  # Format: 00407/0054316
    r'\b(\d{8})\b'         # Format: 29025259
]
```

### **Password Protection Logic**
- **With Email + NIC**: PDF encrypted with NIC number
- **With Email, No NIC**: PDF unencrypted, warning displayed
- **Without Email**: PDF unencrypted for printing

## 📧 Email Distribution System

### **Brevo API Integration**
```python
# Email configuration
SENDER_EMAIL = "CashBack@niclmauritius.site"
SENDER_NAME = "NIC Life Insurance Mauritius"
REPLY_TO_EMAIL = "customerservice@nicl.mu"
REPLY_TO_NAME = "NIC Life Insurance"
```

### **Email Personalization**
- **Greeting Logic**:
  - Title + LastName: "Dear Dr. Smith"
  - LastName only: "Dear Mr./Ms. Johnson"
  - Fallback: "Dear Valued Client"

### **Email Template Structure**
- **Subject**: "NIC Life Insurance - Cash Back Benefit - Policy {policy_number}"
- **HTML Version**: Professional styled email with company branding
- **Text Version**: Plain text fallback for basic email clients
- **Attachments**: Password-protected PDF with policy documents

### **Rate Limiting & Performance**
- **Batch Processing**: 25 emails per batch (configurable)
- **Rate Limiting**: 1 email per second (Brevo free tier compliance)
- **Progress Tracking**: Real-time progress bars with ETA calculations
- **Error Handling**: Comprehensive retry logic and failure reporting