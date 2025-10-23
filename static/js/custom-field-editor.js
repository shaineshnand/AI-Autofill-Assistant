/**
 * Custom Field Editor - Standalone Library
 * Easy to integrate custom field creation, editing, and management
 * 
 * Usage:
 * 1. Include this script in your HTML
 * 2. Initialize with: new CustomFieldEditor(options)
 * 3. Use the API methods to control the editor
 */

class CustomFieldEditor {
    constructor(options = {}) {
        // Default configuration
        this.config = {
            // Target container (iframe, div, etc.)
            targetContainer: options.targetContainer || document.body,
            
            // Field styling
            fieldStyle: {
                position: 'absolute',
                background: 'white',
                border: '2px solid #667eea',
                borderRadius: '4px',
                padding: '5px',
                minWidth: '150px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
                zIndex: 1000,
                userSelect: 'none'
            },
            
            // Drag handle styling
            dragHandleStyle: {
                fontSize: '10px',
                color: '#667eea',
                cursor: 'move',
                flex: 1
            },
            
            // Delete button styling
            deleteButtonStyle: {
                background: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '3px',
                padding: '2px 6px',
                fontSize: '10px',
                cursor: 'pointer'
            },
            
            // Input field styling
            inputStyle: {
                border: 'none',
                background: 'transparent',
                width: '100%',
                fontSize: '12px',
                outline: 'none',
                marginTop: '2px'
            },
            
            // Callbacks
            onFieldAdded: options.onFieldAdded || (() => {}),
            onFieldMoved: options.onFieldMoved || (() => {}),
            onFieldDeleted: options.onFieldDeleted || (() => {}),
            onEditModeToggle: options.onEditModeToggle || (() => {}),
            
            // Debug mode
            debug: options.debug || false
        };
        
        // State management
        this.editModeActive = false;
        this.isDragOperation = false;
        this.fieldCounter = 0;
        this.fields = new Map(); // Store field references
        
        // Initialize
        this.init();
    }
    
    init() {
        this.log('CustomFieldEditor initialized');
        this.setupEventListeners();
    }
    
    log(message, ...args) {
        if (this.config.debug) {
            console.log(`[CustomFieldEditor] ${message}`, ...args);
        }
    }
    
    // Public API Methods
    
    /**
     * Toggle edit mode on/off
     */
    toggleEditMode() {
        this.editModeActive = !this.editModeActive;
        this.log('Edit mode toggled:', this.editModeActive);
        
        // Update field visibility
        this.updateFieldVisibility();
        
        // Trigger callback
        this.config.onEditModeToggle(this.editModeActive);
        
        return this.editModeActive;
    }
    
    /**
     * Add a new field at specified coordinates
     */
    addField(x, y, options = {}) {
        if (!this.editModeActive) {
            this.log('Cannot add field: edit mode not active');
            return null;
        }
        
        const fieldId = `custom_field_${Date.now()}_${this.fieldCounter++}`;
        const field = this.createFieldElement(fieldId, x, y, options);
        
        // Add to container
        this.config.targetContainer.appendChild(field);
        
        // Store field reference
        this.fields.set(fieldId, {
            element: field,
            id: fieldId,
            x: x,
            y: y
        });
        
        this.log('Field added:', fieldId, { x, y });
        this.config.onFieldAdded(fieldId, { x, y });
        
        return fieldId;
    }
    
    /**
     * Remove a field by ID
     */
    removeField(fieldId) {
        const field = this.fields.get(fieldId);
        if (field) {
            field.element.remove();
            this.fields.delete(fieldId);
            this.log('Field removed:', fieldId);
            this.config.onFieldDeleted(fieldId);
            return true;
        }
        return false;
    }
    
    /**
     * Remove all fields
     */
    removeAllFields() {
        const fieldIds = Array.from(this.fields.keys());
        fieldIds.forEach(id => this.removeField(id));
        this.log('All fields removed');
        return fieldIds.length;
    }
    
    /**
     * Get all field data
     */
    getAllFields() {
        const fields = [];
        this.fields.forEach((field, id) => {
            fields.push({
                id: id,
                x: field.x,
                y: field.y,
                value: field.element.querySelector('input').value
            });
        });
        return fields;
    }
    
    /**
     * Update field value
     */
    updateFieldValue(fieldId, value) {
        const field = this.fields.get(fieldId);
        if (field) {
            const input = field.element.querySelector('input');
            if (input) {
                input.value = value;
                return true;
            }
        }
        return false;
    }
    
    /**
     * Get field value
     */
    getFieldValue(fieldId) {
        const field = this.fields.get(fieldId);
        if (field) {
            const input = field.element.querySelector('input');
            return input ? input.value : null;
        }
        return null;
    }
    
    // Private Methods
    
    createFieldElement(fieldId, x, y, options = {}) {
        const container = document.createElement('div');
        container.id = `field_container_${fieldId}`;
        
        // Apply container styles
        Object.assign(container.style, this.config.fieldStyle, {
            left: `${x}px`,
            top: `${y}px`
        });
        
        // Create drag handle
        const dragHandle = document.createElement('div');
        dragHandle.id = `drag_handle_${fieldId}`;
        dragHandle.textContent = `📍 (${x}, ${y})`;
        dragHandle.title = this.editModeActive ? 'Drag to move' : 'Edit mode required to move';
        Object.assign(dragHandle.style, this.config.dragHandleStyle);
        
        // Create delete button
        const deleteButton = document.createElement('button');
        deleteButton.id = `delete_btn_${fieldId}`;
        deleteButton.innerHTML = '✕';
        deleteButton.title = 'Delete field';
        deleteButton.style.display = this.editModeActive ? 'block' : 'none';
        Object.assign(deleteButton.style, this.config.deleteButtonStyle);
        
        // Create input field
        const input = document.createElement('input');
        input.type = 'text';
        input.id = fieldId;
        input.placeholder = options.placeholder || 'Click to edit...';
        Object.assign(input.style, this.config.inputStyle);
        
        // Add event listeners
        this.setupFieldEventListeners(container, dragHandle, deleteButton, input, fieldId);
        
        // Assemble field
        const header = document.createElement('div');
        header.style.display = 'flex';
        header.style.alignItems = 'center';
        header.style.gap = '5px';
        header.appendChild(dragHandle);
        header.appendChild(deleteButton);
        
        container.appendChild(header);
        container.appendChild(input);
        
        return container;
    }
    
    setupFieldEventListeners(container, dragHandle, deleteButton, input, fieldId) {
        // Delete button
        deleteButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.removeField(fieldId);
        });
        
        // Drag functionality
        this.setupDragFunctionality(container, dragHandle, fieldId);
        
        // Input field events
        input.addEventListener('mousedown', (e) => {
            e.stopPropagation();
        });
        
        // Container events
        container.addEventListener('mousedown', (e) => {
            e.stopPropagation();
        });
        
        container.addEventListener('click', (e) => {
            e.stopPropagation();
        });
        
        // Drag handle events
        dragHandle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
        
        dragHandle.addEventListener('mousedown', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    }
    
    setupDragFunctionality(container, dragHandle, fieldId) {
        let isDragging = false;
        let startX, startY, initialX, initialY;
        
        dragHandle.addEventListener('mousedown', (e) => {
            if (!this.editModeActive) return;
            
            isDragging = true;
            this.isDragOperation = true;
            
            startX = e.clientX;
            startY = e.clientY;
            initialX = parseInt(container.style.left) || 0;
            initialY = parseInt(container.style.top) || 0;
            
            // Visual feedback
            container.style.cursor = 'grabbing';
            container.style.zIndex = '2000';
            container.style.opacity = '0.8';
            container.style.transform = 'rotate(2deg)';
            
            e.preventDefault();
            e.stopPropagation();
        });
        
        // Global mouse events
        const handleMouseMove = (e) => {
            if (!isDragging) return;
            
            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            const newX = initialX + deltaX;
            const newY = initialY + deltaY;
            
            container.style.left = `${newX}px`;
            container.style.top = `${newY}px`;
            dragHandle.textContent = `📍 (${newX}, ${newY})`;
        };
        
        const handleMouseUp = (e) => {
            if (!isDragging) return;
            
            isDragging = false;
            
            // Remove visual feedback
            container.style.cursor = '';
            container.style.zIndex = '1000';
            container.style.opacity = '1';
            container.style.transform = '';
            
            // Update field data
            const finalX = parseInt(container.style.left) || 0;
            const finalY = parseInt(container.style.top) || 0;
            
            const field = this.fields.get(fieldId);
            if (field) {
                field.x = finalX;
                field.y = finalY;
            }
            
            this.log('Field moved:', fieldId, { x: finalX, y: finalY });
            this.config.onFieldMoved(fieldId, { x: finalX, y: finalY });
            
            // Clear drag flag after delay
            setTimeout(() => {
                this.isDragOperation = false;
            }, 100);
        };
        
        // Add global listeners
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
        
        // Clean up listeners when field is removed
        const originalRemove = this.removeField.bind(this);
        this.removeField = (id) => {
            if (id === fieldId) {
                document.removeEventListener('mousemove', handleMouseMove);
                document.removeEventListener('mouseup', handleMouseUp);
            }
            return originalRemove(id);
        };
    }
    
    updateFieldVisibility() {
        this.fields.forEach((field, fieldId) => {
            const deleteButton = field.element.querySelector(`#delete_btn_${fieldId}`);
            const dragHandle = field.element.querySelector(`#drag_handle_${fieldId}`);
            
            if (deleteButton) {
                deleteButton.style.display = this.editModeActive ? 'block' : 'none';
            }
            
            if (dragHandle) {
                dragHandle.style.cursor = this.editModeActive ? 'move' : 'default';
                dragHandle.title = this.editModeActive ? 'Drag to move' : 'Edit mode required to move';
            }
        });
    }
    
    setupEventListeners() {
        // Override this method in subclasses or add custom event listeners
        this.log('Event listeners setup complete');
    }
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CustomFieldEditor;
} else if (typeof define === 'function' && define.amd) {
    define([], function() {
        return CustomFieldEditor;
    });
} else {
    window.CustomFieldEditor = CustomFieldEditor;
}
