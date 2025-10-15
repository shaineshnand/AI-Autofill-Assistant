# Sejda Desktop Workflow Integration

## Overview
This workflow allows you to use Sejda PDF Desktop to create fillable PDFs with accurate field detection, then use our AI to fill those fields automatically.

## Workflow Steps

### Step 1: Convert PDF to Fillable using Sejda Desktop
1. Open **Sejda PDF Desktop**
2. Click **Forms** → **Detect Form Fields** (or similar option)
3. Load your contract PDF
4. Sejda will auto-detect blank spaces and add text fields
5. Review and adjust the detected fields if needed
6. Save the fillable PDF

### Step 2: Upload Fillable PDF to Our System
1. Go to your AI Autofill Assistant web app
2. Upload the fillable PDF that Sejda created
3. Our system will detect the AcroForm fields that Sejda created
4. Click "AI Fill All Fields"
5. Download the filled PDF

## Benefits
- **Accurate field detection** from Sejda Desktop
- **No data leakage** - everything is processed locally
- **AI-powered filling** for all detected fields
- **Best of both worlds** - Sejda's detection + our AI filling

## Alternative: Semi-Automated Approach
We can create a "template library" where:
1. You use Sejda Desktop once per document type
2. Save the fillable template
3. Reuse it for similar documents
4. Our AI fills the fields automatically

## Future Enhancement
If Sejda Desktop has a CLI, we can fully automate this process.



