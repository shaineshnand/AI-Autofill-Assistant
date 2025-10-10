# Simple Usage Guide - Django + Training Interface

## 🚀 **How to Start Everything**

### **Method 1: Start Both Servers**

Open **TWO** command prompt windows:

**Window 1 - Django Server:**
```bash
cd "C:\Users\Shainesh Nand\OneDrive\Documents\GitHub\AI-Autofill-Assistant"
python manage.py runserver
```

**Window 2 - Training Interface:**
```bash
cd "C:\Users\Shainesh Nand\OneDrive\Documents\GitHub\AI-Autofill-Assistant"
python ml_training_interface.py
```

### **Method 2: Use the Batch File (Windows)**

Just double-click: `start_all.bat`

## 🌐 **Access the Interfaces**

Once both are running:

1. **Django Interface**: http://localhost:8000
2. **Training Interface**: http://localhost:5001

## 📋 **Django Interface (http://localhost:8000)**

### **What it does:**
- Upload and process documents
- Detect form fields automatically
- Fill forms with data
- Generate filled PDFs
- Chat with AI assistant

### **How to use:**

1. **Upload a Document:**
   - Click "Choose File" 
   - Select a PDF or image
   - Click "Upload Document"

2. **View Detected Fields:**
   - System automatically detects fields
   - See field types (name, email, phone, etc.)
   - View field positions

3. **Fill the Form:**
   - Click on fields to edit them
   - Type in the data you want
   - Click "Generate Filled PDF"

4. **Download Result:**
   - Download the filled PDF
   - Use the chat to ask questions

## 🎓 **Training Interface (http://localhost:5001)**

### **What it does:**
- Train the system on new document types
- Improve field detection accuracy
- Create custom document templates
- Monitor training progress

### **How to use:**

1. **Start Training Session:**
   - Enter Session ID (e.g., "my_forms")
   - Enter Document Type (e.g., "application_form")
   - Click "Start Session"

2. **Add Training Data:**
   - Upload documents
   - Manually annotate fields
   - Specify field types
   - Add context information

3. **Train the Model:**
   - Click "Train Model"
   - See accuracy improvements
   - Monitor training progress

4. **Test Results:**
   - Upload new documents
   - See how well system detects fields
   - Compare before/after accuracy

## 🎯 **Complete Workflow Example**

### **Step 1: Train the System**

1. Go to http://localhost:5001
2. Start session: ID="job_apps", Type="job_application"
3. Upload job application PDFs
4. Annotate fields:
   - "Applicant Name:" → Field Type: "name"
   - "Email Address:" → Field Type: "email"
   - "Phone Number:" → Field Type: "phone"
   - "Position:" → Field Type: "position"
5. Click "Train Model"
6. See accuracy results

### **Step 2: Use the Trained System**

1. Go to http://localhost:8000
2. Upload a new job application PDF
3. System now better detects:
   - Name fields
   - Email fields
   - Phone fields
   - Position fields
4. Fill in the data
5. Generate filled PDF

### **Step 3: Improve Over Time**

1. Upload more job applications to training interface
2. Annotate fields that were missed
3. Retrain the model
4. System gets better with each training session

## 📊 **Field Types You Can Train**

### **Personal Information:**
- name, email, phone, address, date_of_birth, ssn

### **Business Information:**
- company_name, position, salary, experience_years

### **Medical Information:**
- patient_id, insurance, medications, allergies

### **Legal Information:**
- case_number, court, attorney

### **Education Information:**
- student_id, gpa, major

### **Generic Types:**
- text, checkbox, dropdown, radio

## 🔧 **Quick Training Example**

If you want to train quickly with code:

```python
# Run this in Python
from universal_document_processor import UniversalDocumentProcessor

processor = UniversalDocumentProcessor()

# Training data
training_data = [
    {
        'text': 'Company Name:',
        'field_type': 'company_name',
        'document_type': 'business_form',
        'context': 'company name',
        'confidence': 1.0
    },
    {
        'text': 'Contact Email:',
        'field_type': 'email',
        'document_type': 'business_form',
        'context': 'contact email',
        'confidence': 1.0
    }
]

# Train the model
results = processor.train_model(training_data)
print(f"Training accuracy: {results['field_type_accuracy']:.2f}")
```

## 🎯 **Tips for Best Results**

### **Training Tips:**
1. **Start with 10-20 samples** per document type
2. **Be consistent** with field type names
3. **Include diverse examples** with different layouts
4. **Add descriptive context** for better accuracy
5. **Train regularly** with new examples

### **Usage Tips:**
1. **Upload clear, high-quality documents**
2. **Check detected fields** before filling
3. **Use the chat** to ask questions about fields
4. **Download and verify** filled PDFs
5. **Report issues** back to training interface

## 🚨 **Troubleshooting**

### **If servers don't start:**
- Make sure you're in the correct directory
- Check that Python is installed
- Verify ports 8000 and 5001 are available

### **If training doesn't work:**
- Check that documents are clear and readable
- Verify field annotations are accurate
- Ensure consistent field type naming

### **If field detection is poor:**
- Add more training samples
- Create document templates
- Improve document quality
- Retrain with corrected annotations

## 🏆 **Success Metrics**

You'll know the system is working well when:
- **High field detection accuracy** (80%+)
- **Correct field type classification**
- **Proper field positioning**
- **Good document type recognition**
- **Fast processing times**

## 🎯 **Next Steps**

1. **Start both servers** using the commands above
2. **Train on your document types** using the training interface
3. **Test with real documents** using the Django interface
4. **Improve accuracy** by adding more training data
5. **Create templates** for common document types

The system will get better with each training session!

