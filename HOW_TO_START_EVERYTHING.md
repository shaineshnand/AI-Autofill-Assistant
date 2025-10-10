# How to Start Django Server with Training Interface

## 🚀 **Easy Ways to Start Everything**

I've created multiple ways for you to start both the Django server and the training interface together:

### **Method 1: Simple Python Script (Recommended)**

```bash
python start_everything.py
```

This will:
- ✅ Initialize the Universal Document Processing System
- ✅ Start Django server on http://localhost:8000
- ✅ Start training interface on http://localhost:5001
- ✅ Open both interfaces in your browser
- ✅ Show status and allow you to stop everything with Ctrl+C

### **Method 2: Windows Batch File**

```bash
start_all.bat
```

This will:
- ✅ Start both servers in separate windows
- ✅ Open browsers automatically
- ✅ Keep servers running even if you close the script

### **Method 3: Advanced Python Script**

```bash
python start_server_with_training.py
```

This provides more control and monitoring.

### **Method 4: Django Management Command**

```bash
python manage.py runserver
python manage.py start_training --background
```

This starts the training interface as a Django management command.

## 🎯 **Quick Start (Recommended)**

**Just run this one command:**

```bash
python start_everything.py
```

That's it! Everything will start automatically:
- Django server: http://localhost:8000
- Training interface: http://localhost:5001
- Browsers will open automatically

## 📊 **What Each Interface Does**

### **Django Interface (http://localhost:8000)**
- Your main document processing application
- Upload and process documents
- View detected fields
- Generate filled PDFs
- Chat with AI assistant

### **Training Interface (http://localhost:5001)**
- Train the system on new document types
- Upload documents and annotate fields
- Monitor training progress
- Export/import training data
- Create document templates

## 🔧 **Manual Startup (if needed)**

If you prefer to start things manually:

1. **Start Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Start training interface (in another terminal):**
   ```bash
   python ml_training_interface.py
   ```

3. **Open browsers:**
   - Django: http://localhost:8000
   - Training: http://localhost:5001

## 🎓 **How to Train the System**

Once everything is running:

1. **Go to the training interface**: http://localhost:5001

2. **Start a training session:**
   - Enter a session ID (e.g., "my_forms")
   - Enter document type (e.g., "application_form")

3. **Add training samples:**
   - Upload documents
   - Annotate fields manually
   - Add field types and context

4. **Train the model:**
   - Click "Train Model"
   - Monitor accuracy improvements

5. **Test with new documents:**
   - Upload new documents
   - See how well the system detects fields

## 📈 **Training Tips**

### **Quick Training Example:**
```python
# You can also train programmatically
from universal_document_processor import UniversalDocumentProcessor

processor = UniversalDocumentProcessor()

training_data = [
    {
        'text': 'Company Name:',
        'field_type': 'company_name',
        'document_type': 'business_form',
        'context': 'company name',
        'confidence': 1.0
    }
]

results = processor.train_model(training_data)
print(f"Training accuracy: {results['field_type_accuracy']:.2f}")
```

### **Training Data Format:**
```json
{
    "text": "Field label (e.g., 'Name:')",
    "field_type": "Field type (e.g., 'name', 'email', 'phone')",
    "document_type": "Document type (e.g., 'application_form')",
    "context": "Additional context",
    "confidence": 1.0
}
```

## 🛠️ **Troubleshooting**

### **If servers don't start:**
1. Make sure you're in the project root directory
2. Check that `manage.py` exists
3. Check that `ml_training_interface.py` exists
4. Ensure Python is installed and in PATH

### **If ports are busy:**
- Django default port: 8000
- Training interface default port: 5001
- Change ports in the scripts if needed

### **If training doesn't work:**
1. Check that the Universal Document Processor is initialized
2. Verify training data format
3. Check system statistics via API

## 📊 **System Status**

You can check system status at any time:

```bash
python -c "from universal_document_processor import UniversalDocumentProcessor; processor = UniversalDocumentProcessor(); stats = processor.get_system_stats(); print(stats)"
```

## 🎯 **Next Steps**

1. **Start everything**: `python start_everything.py`
2. **Train on your documents**: Use the training interface
3. **Test with real documents**: Upload and process documents
4. **Improve accuracy**: Add more training data
5. **Create templates**: For common document types

## 🏆 **Benefits**

- **One command startup**: Everything starts with one command
- **Integrated training**: Train while using the main application
- **Automatic browser opening**: No manual navigation needed
- **Easy monitoring**: See status of both servers
- **Simple shutdown**: Ctrl+C stops everything

The system is now ready to handle any document type you train it on!

