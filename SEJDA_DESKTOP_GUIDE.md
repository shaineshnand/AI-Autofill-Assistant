# 🎯 Sejda Desktop Integration Guide

## Complete Workflow for Converting PDFs to Fillable Forms

---

## Step 1: Download & Install Sejda PDF Desktop

1. **Download Sejda Desktop** from: https://www.sejda.com/desktop
2. **Install** the application on your computer
3. **Launch** Sejda PDF Desktop

---

## Step 2: Convert Your PDF to Fillable Form Using Sejda

### Option A: Auto-Detect Form Fields (Recommended)

1. **Open Sejda Desktop**
2. Click **"Forms"** in the left menu
3. Click **"Detect Form Fields"** or **"Add Form Fields"**
4. **Upload your contract PDF** (e.g., your employment contract)
5. Sejda will **automatically detect** blank spaces, dotted lines, and fillable areas
6. **Review** the detected fields:
   - Blue boxes should appear over fillable areas
   - Check if all dotted lines are covered
   - Adjust field positions if needed
7. **Save** the fillable PDF to your computer

### Option B: Manual Field Addition

1. Open your PDF in Sejda Desktop
2. Click **"Forms"** → **"Text Field"**
3. **Click and drag** to create text fields over dotted lines
4. Repeat for all fillable areas
5. **Save** the fillable PDF

---

## Step 3: Upload Fillable PDF to AI Autofill Assistant

1. **Go to** your AI Autofill Assistant: http://127.0.0.1:8000
2. Click the **"Upload Fillable PDF (Sejda)"** button (green button with checkmark icon)
3. **Select** the fillable PDF you created in Sejda Desktop
4. Wait for the upload to complete

---

## Step 4: AI Fill the Fields

1. After upload, you'll see all the detected form fields
2. Click **"AI Fill All Fields"** button
3. The AI will analyze your document and fill all fields automatically
4. **Review** the AI-filled data:
   - Each field will show AI-generated content
   - You can manually edit any field if needed

---

## Step 5: Download the Filled PDF

1. Click **"Generate & Download Filled PDF"**
2. The system will create a PDF with:
   - ✅ All fields filled with AI data
   - ✅ Blue boxes showing fillable areas
   - ✅ Editable form fields (you can still edit it)
3. **Download** and use your filled PDF!

---

## 🎨 Expected Results

### What You'll See:

- **Accurate blue boxes** exactly over dotted lines and blank spaces
- **AI-filled data** in all detected fields
- **Editable PDF** that you can still modify manually
- **No data leakage** - everything processed locally

### Example:

```
Original PDF:
Name: .....................
Date: .....................

After Sejda:
Name: [        BLUE BOX        ]
Date: [        BLUE BOX        ]

After AI Fill:
Name: [    John Smith         ]
Date: [    2025-10-13         ]
```

---

## 🔧 Troubleshooting

### Problem: Sejda didn't detect all fields

**Solution:**
- Use manual field addition in Sejda
- Ensure your PDF has clear dotted lines or blank spaces
- Try adjusting Sejda's detection sensitivity settings

### Problem: Upload failed

**Solution:**
- Make sure you're uploading the **fillable PDF** from Sejda, not the original
- Check file size (max 50MB)
- Ensure PDF is not password-protected

### Problem: AI didn't fill some fields

**Solution:**
- Check if the fields have clear context (labels nearby)
- Manually fill missing fields
- Use the chat feature to ask AI to fill specific fields

---

## 💡 Pro Tips

1. **Save Sejda Templates**: Once you create a fillable version for a document type (e.g., employment contract), save it as a template for reuse

2. **Field Naming**: In Sejda, you can name fields (e.g., "employee_name", "start_date") which helps AI understand what to fill

3. **Batch Processing**: Create fillable templates once, then use them multiple times with different AI data

4. **Quality Check**: Always review AI-filled data before final use

---

## 📋 Quick Reference

| Action | Button/Location |
|--------|----------------|
| Upload fillable PDF | Green "Upload Fillable PDF (Sejda)" button |
| Fill with AI | "AI Fill All Fields" button |
| Download filled PDF | "Generate & Download Filled PDF" button |
| Edit field manually | Click on field input box |

---

## 🎯 Why This Approach Works Best

1. **Sejda Desktop**: Best-in-class field detection (accurate placement)
2. **Our AI**: Best-in-class content generation (smart filling)
3. **Combined**: Perfect placement + Smart content = Ideal solution
4. **No Data Leakage**: All processing happens on your computer

---

## Need Help?

If you encounter any issues:
1. Check the terminal logs for error messages
2. Verify the fillable PDF works in a PDF reader
3. Try re-creating the fillable PDF in Sejda
4. Contact support with screenshots

---

**Ready to get started? Follow the steps above!** 🚀



