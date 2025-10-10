# Coordinate Scaling and Multi-Page PDF Fill Fix

## Problem
When filling multi-page PDFs, fields were:
1. ❌ All appearing on the first page only
2. ❌ Appearing in wrong positions (scattered)
3. ❌ Not aligned with the actual form fields

## Root Causes

### Issue 1: Coordinate Scaling Mismatch
During field detection, PDFs are converted to images with **2x scaling** (`Matrix(2.0, 2.0)`):
```python
mat = fitz.Matrix(2.0, 2.0)  # Scale up for better detection
pix = page.get_pixmap(matrix=mat)
```

This means detected field coordinates are **2x larger** than the original PDF dimensions.

When filling the PDF, we were using these **scaled coordinates directly** on the original PDF, causing misalignment.

### Issue 2: Mixed Coordinate Systems
The system uses TWO different coordinate systems:
1. **AcroForm fields**: Coordinates from PDF's native form fields (not scaled)
2. **Visual detection fields**: Coordinates from 2x scaled images (scaled)

The filling code wasn't distinguishing between these two types.

### Issue 3: Page Assignment
Fields detected from different pages weren't being properly grouped and assigned to their respective pages when filling.

## Solution

### 1. Coordinate Scaling Logic
Updated `create_filled_pdf()` to handle both coordinate systems:

```python
# Check field type by ID prefix
is_acroform = field_id.startswith('acroform_')

if is_acroform:
    # AcroForm fields: use coordinates as-is (PDF native)
    x = field['x_position']
    y = field['y_position']
    width = field['width']
    height = field['height']
else:
    # Visual fields: scale back from 2x to 1x
    SCALE_FACTOR = 2.0
    x = field['x_position'] / SCALE_FACTOR
    y = field['y_position'] / SCALE_FACTOR
    width = field['width'] / SCALE_FACTOR
    height = field['height'] / SCALE_FACTOR
```

### 2. Page Grouping
Fields are now grouped by page before filling:

```python
# Group fields by page
fields_by_page = {}
for field in fields:
    page_num = field.get('page', 0)
    if page_num not in fields_by_page:
        fields_by_page[page_num] = []
    fields_by_page[page_num].append(field)

# Process each page separately
for page_num in range(len(doc)):
    page_fields = fields_by_page.get(page_num, [])
    # Fill only fields belonging to this page
```

### 3. Text Positioning
Improved text baseline alignment:

```python
# Calculate font size based on field height
font_size = min(11, height * 0.7)

# Position text baseline at 75% of field height
text_x = x + 2  # Small left padding
text_y = y + height * 0.75  # Baseline position

new_page.insert_text((text_x, text_y), content, fontsize=font_size)
```

### 4. Compatibility Updates
Added `page` alias in `improved_field_detector.py`:

```python
'page_number': field.page_number,
'page': field.page_number,  # Alias for compatibility
```

## Files Modified

1. **documents/views.py**
   - `create_filled_pdf()`: Added coordinate scaling logic
   - Added page grouping and proper field assignment
   - Improved text positioning and font sizing

2. **improved_field_detector.py**
   - `convert_form_fields_to_dict()`: Added `page` alias

## How It Works Now

### Detection Phase (Upload)
1. PDF pages converted to 2x images for better detection
2. Fields detected with 2x coordinates
3. Each field stores:
   - `page_number` / `page`: Which page it's on
   - `x_position`, `y_position`: Coordinates (2x for visual, 1x for AcroForm)
   - `id`: Prefix indicates type (`acroform_` or `rect_field_`, etc.)

### Filling Phase (Download)
1. Fields grouped by page number
2. For each page:
   - Copy original page content
   - Get fields for that page only
   - For each field:
     - Check if AcroForm (use as-is) or visual (scale back)
     - Calculate proper text position
     - Insert text at correct coordinates

## Testing

To verify the fix:

1. **Upload a multi-page PDF** (2-3 pages with form fields)
2. **Fill in fields** on different pages
3. **Download the filled PDF**
4. **Verify**:
   - ✅ All pages are present
   - ✅ Text appears exactly where form fields are
   - ✅ No scattered or misaligned text
   - ✅ Each page shows only its own filled fields

## Debug Output

The system now logs:
```
Processing 3 pages with 12 total fields
Fields by page: [(0, 4), (1, 5), (2, 3)]
Page 0: 4 fields to fill
  Filling field acroform_name_0 (acroform) at (120.0, 150.0) with 'John Doe'
  Filling field rect_field_p0_1 (visual) at (115.5, 225.3) with 'john@email.com'
Page 1: 5 fields to fill
  ...
Page 2: 3 fields to fill
  ...
PDF saved successfully
```

## Date Fixed
October 7, 2025


