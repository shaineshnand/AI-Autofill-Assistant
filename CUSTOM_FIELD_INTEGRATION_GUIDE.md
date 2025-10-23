# Custom Field Editor - Integration Guide

A standalone, easy-to-integrate JavaScript library for creating, editing, and managing custom fields with drag-and-drop functionality.

## 🚀 Quick Start

### 1. Include the Library

```html
<!-- Include the Custom Field Editor library -->
<script src="custom-field-editor.js"></script>
```

### 2. Initialize the Editor

```javascript
const fieldEditor = new CustomFieldEditor({
    targetContainer: document.getElementById('your-container'),
    debug: true,
    onFieldAdded: (fieldId, position) => {
        console.log('Field added:', fieldId, position);
    },
    onFieldMoved: (fieldId, position) => {
        console.log('Field moved:', fieldId, position);
    },
    onFieldDeleted: (fieldId) => {
        console.log('Field deleted:', fieldId);
    },
    onEditModeToggle: (isActive) => {
        console.log('Edit mode:', isActive);
    }
});
```

### 3. Basic Usage

```javascript
// Toggle edit mode
fieldEditor.toggleEditMode();

// Add a field at specific coordinates
const fieldId = fieldEditor.addField(100, 200);

// Remove a field
fieldEditor.removeField(fieldId);

// Remove all fields
fieldEditor.removeAllFields();

// Get all field data
const fields = fieldEditor.getAllFields();
```

## 📚 API Reference

### Constructor Options

```javascript
new CustomFieldEditor({
    targetContainer: document.body,        // Container element
    fieldStyle: { ... },                   // Custom field styling
    dragHandleStyle: { ... },              // Custom drag handle styling
    deleteButtonStyle: { ... },             // Custom delete button styling
    inputStyle: { ... },                   // Custom input field styling
    onFieldAdded: (fieldId, position) => {}, // Field added callback
    onFieldMoved: (fieldId, position) => {}, // Field moved callback
    onFieldDeleted: (fieldId) => {},        // Field deleted callback
    onEditModeToggle: (isActive) => {},     // Edit mode toggle callback
    debug: false                            // Enable debug logging
})
```

### Public Methods

#### `toggleEditMode()`
Toggle edit mode on/off. Returns boolean indicating current state.

```javascript
const isEditMode = fieldEditor.toggleEditMode();
```

#### `addField(x, y, options)`
Add a new field at specified coordinates.

```javascript
const fieldId = fieldEditor.addField(100, 200, {
    placeholder: 'Custom placeholder'
});
```

#### `removeField(fieldId)`
Remove a specific field by ID.

```javascript
const removed = fieldEditor.removeField('custom_field_1234567890');
```

#### `removeAllFields()`
Remove all fields. Returns count of removed fields.

```javascript
const count = fieldEditor.removeAllFields();
```

#### `getAllFields()`
Get all field data as an array.

```javascript
const fields = fieldEditor.getAllFields();
// Returns: [{ id: 'field1', x: 100, y: 200, value: 'text' }, ...]
```

#### `updateFieldValue(fieldId, value)`
Update the value of a specific field.

```javascript
fieldEditor.updateFieldValue('custom_field_1234567890', 'New value');
```

#### `getFieldValue(fieldId)`
Get the value of a specific field.

```javascript
const value = fieldEditor.getFieldValue('custom_field_1234567890');
```

## 🎨 Customization

### Styling Options

You can customize the appearance by passing style objects:

```javascript
const fieldEditor = new CustomFieldEditor({
    targetContainer: document.getElementById('container'),
    fieldStyle: {
        background: 'lightblue',
        border: '3px solid #007bff',
        borderRadius: '8px',
        minWidth: '200px'
    },
    dragHandleStyle: {
        color: '#007bff',
        fontSize: '12px'
    },
    deleteButtonStyle: {
        background: '#ff6b6b',
        borderRadius: '50%'
    },
    inputStyle: {
        fontSize: '14px',
        color: '#333'
    }
});
```

### Callback Functions

Handle events with custom callbacks:

```javascript
const fieldEditor = new CustomFieldEditor({
    targetContainer: document.getElementById('container'),
    onFieldAdded: (fieldId, position) => {
        // Custom logic when field is added
        console.log(`Field ${fieldId} added at (${position.x}, ${position.y})`);
    },
    onFieldMoved: (fieldId, position) => {
        // Custom logic when field is moved
        console.log(`Field ${fieldId} moved to (${position.x}, ${position.y})`);
    },
    onFieldDeleted: (fieldId) => {
        // Custom logic when field is deleted
        console.log(`Field ${fieldId} deleted`);
    },
    onEditModeToggle: (isActive) => {
        // Custom logic when edit mode changes
        console.log(`Edit mode: ${isActive ? 'ON' : 'OFF'}`);
    }
});
```

## 🔧 Integration Examples

### React Integration

```jsx
import React, { useEffect, useRef, useState } from 'react';

const CustomFieldComponent = () => {
    const containerRef = useRef(null);
    const fieldEditorRef = useRef(null);
    const [fields, setFields] = useState([]);

    useEffect(() => {
        if (containerRef.current) {
            fieldEditorRef.current = new CustomFieldEditor({
                targetContainer: containerRef.current,
                onFieldAdded: (fieldId, position) => {
                    setFields(prev => [...prev, { id: fieldId, ...position }]);
                },
                onFieldDeleted: (fieldId) => {
                    setFields(prev => prev.filter(f => f.id !== fieldId));
                }
            });
        }
    }, []);

    const toggleEditMode = () => {
        fieldEditorRef.current?.toggleEditMode();
    };

    return (
        <div>
            <button onClick={toggleEditMode}>Toggle Edit Mode</button>
            <div ref={containerRef} style={{ minHeight: '400px', border: '1px solid #ccc' }} />
        </div>
    );
};
```

### Vue.js Integration

```vue
<template>
    <div>
        <button @click="toggleEditMode">Toggle Edit Mode</button>
        <div ref="container" class="field-container"></div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            fieldEditor: null
        };
    },
    mounted() {
        this.fieldEditor = new CustomFieldEditor({
            targetContainer: this.$refs.container,
            onFieldAdded: (fieldId, position) => {
                this.$emit('field-added', { fieldId, position });
            }
        });
    },
    methods: {
        toggleEditMode() {
            this.fieldEditor.toggleEditMode();
        }
    }
};
</script>
```

### Angular Integration

```typescript
import { Component, ElementRef, ViewChild, AfterViewInit } from '@angular/core';

declare const CustomFieldEditor: any;

@Component({
    selector: 'app-custom-fields',
    template: `
        <button (click)="toggleEditMode()">Toggle Edit Mode</button>
        <div #container class="field-container"></div>
    `
})
export class CustomFieldsComponent implements AfterViewInit {
    @ViewChild('container') container!: ElementRef;
    fieldEditor: any;

    ngAfterViewInit() {
        this.fieldEditor = new CustomFieldEditor({
            targetContainer: this.container.nativeElement,
            onFieldAdded: (fieldId: string, position: any) => {
                console.log('Field added:', fieldId, position);
            }
        });
    }

    toggleEditMode() {
        this.fieldEditor.toggleEditMode();
    }
}
```

## 📦 Data Export/Import

### Export Fields

```javascript
// Get all field data
const fields = fieldEditor.getAllFields();

// Export as JSON
const jsonData = JSON.stringify(fields, null, 2);
console.log(jsonData);

// Save to file
const blob = new Blob([jsonData], { type: 'application/json' });
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'fields.json';
a.click();
```

### Import Fields

```javascript
// Load from JSON
const fields = JSON.parse(jsonData);

// Clear existing fields
fieldEditor.removeAllFields();

// Add imported fields
fields.forEach(field => {
    fieldEditor.addField(field.x, field.y, { placeholder: field.value });
});
```

## 🎯 Advanced Features

### Custom Field Types

Extend the library to support different field types:

```javascript
class ExtendedFieldEditor extends CustomFieldEditor {
    addTextField(x, y, options = {}) {
        return this.addField(x, y, { ...options, type: 'text' });
    }
    
    addNumberField(x, y, options = {}) {
        return this.addField(x, y, { ...options, type: 'number' });
    }
    
    addDateField(x, y, options = {}) {
        return this.addField(x, y, { ...options, type: 'date' });
    }
}
```

### Validation

Add validation to fields:

```javascript
const fieldEditor = new CustomFieldEditor({
    targetContainer: document.getElementById('container'),
    onFieldAdded: (fieldId, position) => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('blur', (e) => {
                // Custom validation logic
                if (e.target.value.length < 3) {
                    e.target.style.border = '2px solid red';
                } else {
                    e.target.style.border = 'none';
                }
            });
        }
    }
});
```

## 🐛 Troubleshooting

### Common Issues

1. **Fields not appearing**: Check that `targetContainer` is properly set
2. **Drag not working**: Ensure edit mode is active
3. **Events not firing**: Check that callbacks are properly defined
4. **Styling issues**: Verify CSS isn't conflicting with field styles

### Debug Mode

Enable debug mode to see detailed logging:

```javascript
const fieldEditor = new CustomFieldEditor({
    targetContainer: document.getElementById('container'),
    debug: true  // Enable console logging
});
```

## 📄 License

This library is provided as-is for integration into your projects. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

To contribute to this library:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For questions or issues:

1. Check the debug console for error messages
2. Verify all required parameters are provided
3. Test with a minimal example
4. Check browser compatibility

---

**Happy coding!** 🎉
