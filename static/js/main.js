// Global variables for Sejda workflow
let sejdaWorkflowData = {};
let currentStep = 1;
let useHtmlProcessing = true; // Always use HTML workflow

// Global functions for onclick handlers
window.handleHtmlUpload = function() {
    console.log('handleHtmlUpload called');
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        useHtmlProcessing = true;
        fileInput.click();
    } else {
        console.error('File input not found');
    }
};

window.handleUploadAreaClick = function() {
    console.log('handleUploadAreaClick called');
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        // Don't set useHtmlProcessing here - let user choose workflow
        fileInput.click();
    } else {
        console.error('File input not found');
    }
};

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Sejda workflow functions
function showSejdaModal() {
    document.getElementById('sejdaWorkflowModal').style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent background scroll
    nextStep(1);
}

function closeSejdaModal() {
    document.getElementById('sejdaWorkflowModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

function nextStep(stepNum) {
    // Hide all steps
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });
    
    // Show current step
    const stepElement = document.getElementById(`step${stepNum}`);
    if (stepElement) {
        stepElement.classList.add('active');
        currentStep = stepNum;
        
        // Auto-progress for step 1
        if (stepNum === 1) {
            const progress = document.getElementById('progress1');
            if (progress) {
                progress.style.width = '100%';
                setTimeout(() => nextStep(2), 3000); // Auto-advance after 3 seconds
            }
        }
    }
}

// OLD: Manual Sejda workflow completion (no longer used - now 100% automatic)
/*
async function completeSejdaWorkflow() {
    // This function is no longer needed - Sejda workflow is now fully automatic!
    // Keeping for reference only
}
*/

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing...');
    
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const chatInput = document.getElementById('chatInput');
    
    console.log('Elements found:', {
        uploadArea: !!uploadArea,
        fileInput: !!fileInput,
        documentLoaded: !!document.querySelector('.document-results')
    });
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');
    const generatePdfBtn = document.getElementById('generatePdfBtn');
    const startOverBtn = document.getElementById('startOverBtn');
    const previewBtn = document.getElementById('previewBtn');
    const previewModal = document.getElementById('previewModal');
    const closePreview = document.getElementById('closePreview');
    const closePreviewBtn = document.getElementById('closePreviewBtn');
    const fillAllBtn = document.getElementById('fillAllBtn');
    const regenerateBtn = document.getElementById('regenerateBtn');
    const recreateBtn = document.getElementById('recreateBtn');
    const documentId = document.getElementById('documentId')?.value;

    // File upload functionality
    if (uploadArea && fileInput) {
        // Traditional workflow removed - HTML workflow always enabled
        
    // HTML upload button - triggers HTML-based workflow!
    // HTML workflow is always enabled - no button needed
        
        // Default click behavior (for drag and drop area)
        uploadArea.addEventListener('click', (e) => {
            if (e.target === uploadArea || e.target.classList.contains('upload-icon') || 
                e.target.classList.contains('upload-text') || e.target.classList.contains('upload-subtext')) {
                fileInput.click();
            }
        });
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                
                // Check file size (50MB limit)
                if (file.size > 50 * 1024 * 1024) {
                    alert('File too large. Maximum size is 50MB.');
                    return;
                }
                
                // Check file type
                const allowedExtensions = /\.(pdf|png|jpg|jpeg|gif|bmp|tiff|tif|webp|doc|docx|txt|rtf)$/i;
                if (!allowedExtensions.test(file.name)) {
                    alert('Unsupported file type. Please upload PDF, Word, Text, or Image files.');
                    return;
                }
                
                fileInput.files = files;
                uploadFile(files[0]);
            }
        });
        
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                
                // Check file size (50MB limit)
                if (file.size > 50 * 1024 * 1024) {
                    alert('File too large. Maximum size is 50MB.');
                    fileInput.value = '';
                    return;
                }
                
                // Check file type
                const allowedExtensions = /\.(pdf|png|jpg|jpeg|gif|bmp|tiff|tif|webp|doc|docx|txt|rtf)$/i;
                if (!allowedExtensions.test(file.name)) {
                    alert('Unsupported file type. Please upload PDF, Word, Text, or Image files.');
                    fileInput.value = '';
                    return;
                }
                
                uploadFile(file);
            }
        });
        
    }

    // Start over functionality
    if (startOverBtn) {
        startOverBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to start over? This will clear the current document and allow you to upload a new one.')) {
                // Clear the current document from session and redirect to main page
                fetch('/api/documents/clear-session/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                }).then(() => {
                    // Redirect to main page to show upload area
                    window.location.href = '/';
                }).catch(error => {
                    console.error('Error clearing session:', error);
                    // Still redirect even if clearing session fails
                    window.location.href = '/';
                });
            }
        });
    }

    // Handle AI Fill button for HTML workflow
    const aiFillBtn = document.getElementById('aiFillBtn');
    if (aiFillBtn && documentId) {
        aiFillBtn.addEventListener('click', async () => {
            try {
                aiFillBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> AI is filling...';
                aiFillBtn.disabled = true;

                const response = await fetch(`/ai-fill/${documentId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });

                const data = await response.json();
                
                if (data.success) {
                    // Reload page to show filled form and generate button
                    window.location.reload();
                } else {
                    alert('AI filling failed: ' + (data.error || 'Unknown error'));
                    aiFillBtn.innerHTML = '<i class="fas fa-magic"></i> AI Fill All Fields';
                    aiFillBtn.disabled = false;
                }
            } catch (error) {
                console.error('AI fill error:', error);
                alert('AI filling failed: ' + error.message);
                aiFillBtn.innerHTML = '<i class="fas fa-magic"></i> AI Fill All Fields';
                aiFillBtn.disabled = false;
            }
        });
    }

    // Handle Generate PDF button for HTML workflow
    if (generatePdfBtn && documentId) {
        generatePdfBtn.addEventListener('click', async () => {
            try {
                generatePdfBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating PDF...';
                generatePdfBtn.disabled = true;

                // Capture current field values from editable fields
                const fieldValues = {};
                const editableFields = document.querySelectorAll('.editable-field');
                console.log('Found editable fields in main document:', editableFields.length);
                
                editableFields.forEach(field => {
                    console.log('Field:', field.id, 'Value:', field.value);
                    if (field.id && field.value) {
                        fieldValues[field.id] = field.value;
                    }
                });
                
                // Try to get field values from iframe using postMessage
                const iframe = document.getElementById('htmlFormIframe');
                if (iframe) {
                    console.log('Attempting to get field values from iframe...');
                    
                    // Set up listener for response
                    const messageListener = (event) => {
                        if (event.data.type === 'FIELD_VALUES') {
                            console.log('Received field values from iframe:', event.data.values);
                            Object.assign(fieldValues, event.data.values);
                            window.removeEventListener('message', messageListener);
                        }
                    };
                    
                    window.addEventListener('message', messageListener);
                    
                    // Send message to iframe
                    iframe.contentWindow.postMessage({type: 'GET_FIELD_VALUES'}, '*');
                    
                    // Wait a bit for response
                    await new Promise(resolve => setTimeout(resolve, 100));
                }
                
                console.log('Final captured field values:', fieldValues);

                const response = await fetch(`/generate-pdf/${documentId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        field_values: fieldValues
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    // Download the generated PDF
                    const downloadLink = document.createElement('a');
                    downloadLink.href = data.pdf_url;
                    downloadLink.download = data.pdf_url.split('/').pop();
                    downloadLink.click();
                    
                    // Show success message
                    generatePdfBtn.innerHTML = '<i class="fas fa-check"></i> PDF Generated!';
                    setTimeout(() => {
                        generatePdfBtn.innerHTML = '<i class="fas fa-download"></i> Generate PDF';
                        generatePdfBtn.disabled = false;
                    }, 2000);
                } else {
                    alert('PDF generation failed: ' + (data.error || 'Unknown error'));
                    generatePdfBtn.innerHTML = '<i class="fas fa-download"></i> Generate PDF';
                    generatePdfBtn.disabled = false;
                }
            } catch (error) {
                console.error('PDF generation error:', error);
                alert('PDF generation failed: ' + error.message);
                generatePdfBtn.innerHTML = '<i class="fas fa-download"></i> Generate PDF';
                generatePdfBtn.disabled = false;
            }
        });
    }

    // Document preview functionality
    if (previewBtn) {
        previewBtn.addEventListener('click', () => {
            previewModal.style.display = 'block';
            loadDocumentPreview();
        });
    }

    if (closePreview) {
        closePreview.addEventListener('click', () => {
            previewModal.style.display = 'none';
        });
    }

    if (closePreviewBtn) {
        closePreviewBtn.addEventListener('click', () => {
            previewModal.style.display = 'none';
        });
    }

    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        if (event.target === previewModal) {
            previewModal.style.display = 'none';
        }
    });

    async function loadDocumentPreview() {
        const previewContent = document.getElementById('previewContent');
        
        if (!documentId) {
            previewContent.innerHTML = '<div class="preview-loading">No document loaded</div>';
            return;
        }

        try {
                    const response = await fetch(`/${documentId}/preview/`);
            const data = await response.json();
            
            if (data.success) {
                if (data.preview_type === 'image') {
                    previewContent.innerHTML = `
                        <div class="document-preview">
                            <img src="${data.preview_url}" alt="Document Preview">
                        </div>
                    `;
                } else if (data.preview_type === 'pdf') {
                    previewContent.innerHTML = `
                        <div class="document-preview">
                            <iframe src="${data.preview_url}" type="application/pdf"></iframe>
                        </div>
                    `;
                } else {
                    previewContent.innerHTML = `
                        <div class="document-preview">
                            <h4>Document Content:</h4>
                            <pre style="white-space: pre-wrap; background: #f8f9fa; padding: 20px; border-radius: 8px;">${data.content}</pre>
                        </div>
                    `;
                }
            } else {
                previewContent.innerHTML = '<div class="preview-loading">Error loading preview: ' + data.error + '</div>';
            }
        } catch (error) {
            previewContent.innerHTML = '<div class="preview-loading">Error loading preview: ' + error.message + '</div>';
        }
    }

    // Fill all fields functionality - Updated for HTML workflow
    if (fillAllBtn) {
        fillAllBtn.addEventListener('click', async () => {
            if (!documentId) {
                alert('No document loaded');
                return;
            }

            if (confirm('This will use AI to fill all empty fields with sample data. Continue?')) {
                fillAllBtn.disabled = true;
                fillAllBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Filling fields...';

                try {
                    // Use the new HTML workflow AI fill endpoint
                    const response = await fetch(`/ai-fill/${documentId}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });

                    const data = await response.json();
                    
                    if (data.success) {
                        // Reload page to show filled form and generate button
                        window.location.reload();
                    } else {
                        alert('AI filling failed: ' + (data.error || 'Unknown error'));
                        fillAllBtn.disabled = false;
                        fillAllBtn.innerHTML = '<i class="fas fa-magic"></i> AI Fill All Fields';
                    }
                } catch (error) {
                    console.error('Fill all error:', error);
                    alert('AI filling failed: ' + error.message);
                    fillAllBtn.disabled = false;
                    fillAllBtn.innerHTML = '<i class="fas fa-magic"></i> AI Fill All Fields';
                }
            }
        });
    }

    // Regenerate document functionality
    if (regenerateBtn) {
        regenerateBtn.addEventListener('click', async () => {
            if (!documentId) {
                alert('No document loaded');
                return;
            }

            if (confirm('This will create an exact copy of your original form with all the questions and text preserved, but with your answers filled in. Continue?')) {
                regenerateBtn.disabled = true;
                regenerateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Form with Answers...';

                try {
                    const response = await fetch(`/${documentId}/regenerate/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });

                    const data = await response.json();
                    
                    if (data.success) {
                        addMessage(`✅ Original form with answers created successfully! Download: ${data.output_file}`, 'bot');
                        
                        // Show download link
                        const downloadLink = document.createElement('a');
                        downloadLink.href = data.download_url;
                        downloadLink.download = data.output_file;
                        downloadLink.textContent = 'Download Filled Document';
                        downloadLink.className = 'btn btn-success';
                        downloadLink.style.marginTop = '10px';
                        
                        // Add download link to the page
                        const documentActions = document.querySelector('.document-actions');
                        if (documentActions) {
                            documentActions.appendChild(downloadLink);
                        }
                    } else {
                        addMessage('Error regenerating document: ' + data.error, 'bot');
                    }
                } catch (error) {
                    console.error('Regenerate error:', error);
                    addMessage('Error regenerating document: ' + error.message, 'bot');
                } finally {
                    regenerateBtn.disabled = false;
                    regenerateBtn.innerHTML = '<i class="fas fa-redo"></i> Generate Original Form with Answers';
                }
            }
        });
    }

    // Recreate editable PDF functionality
    if (recreateBtn) {
        recreateBtn.addEventListener('click', async () => {
            if (!documentId) {
                alert('No document loaded');
                return;
            }

            if (confirm('This will extract text from your PDF and create a completely new editable PDF with AI auto-filled data. This recreates the PDF exactly like the original but makes it editable with AI-filled content. Continue?')) {
                recreateBtn.disabled = true;
                recreateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Recreating PDF with AI...';

                try {
                    const response = await fetch(`/${documentId}/recreate-editable/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });

                    const data = await response.json();
                    
                    if (data.success) {
                        addMessage(`🎉 PDF recreated successfully! Document type: ${data.document_type}. Fields detected: ${data.fields_detected}, Fields filled: ${data.fields_filled}`, 'bot');
                        
                        // Show download link
                        const downloadLink = document.createElement('a');
                        downloadLink.href = data.download_url;
                        downloadLink.download = data.output_file;
                        downloadLink.textContent = 'Download Recreated PDF';
                        downloadLink.className = 'btn btn-primary';
                        downloadLink.style.marginTop = '10px';
                        
                        // Add download link to the page
                        const documentActions = document.querySelector('.document-actions');
                        if (documentActions) {
                            documentActions.appendChild(downloadLink);
                        }
                        
                        // Show extracted text preview
                        if (data.extracted_text_preview) {
                            addMessage(`📄 Extracted text preview: ${data.extracted_text_preview}`, 'bot');
                        }
                        
                        // Show filled data
                        if (data.filled_data && Object.keys(data.filled_data).length > 0) {
                            const filledDataText = Object.entries(data.filled_data)
                                .map(([key, value]) => `${key}: ${value}`)
                                .join(', ');
                            addMessage(`🤖 AI-filled data: ${filledDataText}`, 'bot');
                        }
                    } else {
                        addMessage('Error recreating PDF: ' + (data.details || data.error), 'bot');
                    }
                } catch (error) {
                    console.error('Recreate error:', error);
                    addMessage('Error recreating PDF: ' + error.message, 'bot');
                } finally {
                    recreateBtn.disabled = false;
                    recreateBtn.innerHTML = '<i class="fas fa-file-pdf"></i> 🆕 Recreate Editable PDF (AI-Filled)';
                }
            }
        });
    }

    // Upload file function - NOW WITH AUTOMATIC SEJDA WORKFLOW!
    async function uploadFile(file) {
        const isPDF = file.name.toLowerCase().endsWith('.pdf');
        
        // Show loading indicator for HTML workflow
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea && isPDF) {
            // Show HTML workflow processing window
            uploadArea.innerHTML = `
                <div style="max-width: 800px; margin: 0 auto; padding: 30px;">
                    <h2 style="text-align: center; margin-bottom: 30px;">
                        <i class="fas fa-code" style="color: #007bff;"></i> HTML Workflow Processing
                    </h2>
                    
                    <!-- Live Status Box -->
                    <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                                color: white; padding: 30px; border-radius: 15px; 
                                box-shadow: 0 10px 40px rgba(0,0,0,0.2); margin-bottom: 30px;">
                        
                        <div style="font-size: 1.2em; margin-bottom: 20px; text-align: center;">
                            <i class="fas fa-spinner fa-spin"></i> 
                            <span id="statusMessage">Converting PDF to HTML...</span>
                        </div>
                        
                        <!-- Progress Steps -->
                        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px;">
                            <div style="display: flex; flex-direction: column; gap: 15px;">
                                <div id="step1" style="display: flex; align-items: center; gap: 10px;">
                                    <i class="fas fa-spinner fa-spin"></i>
                                    <span>📄 Reading PDF and extracting layout...</span>
                                </div>
                                <div id="step2" style="display: none; align-items: center; gap: 10px;">
                                    <i class="fas fa-spinner fa-spin"></i>
                                    <span>🔍 Detecting form fields...</span>
                                </div>
                                <div id="step3" style="display: none; align-items: center; gap: 10px;">
                                    <i class="fas fa-spinner fa-spin"></i>
                                    <span>🌐 Converting to HTML form...</span>
                                </div>
                                <div id="step4" style="display: none; align-items: center; gap: 10px;">
                                    <i class="fas fa-spinner fa-spin"></i>
                                    <span>✨ Preparing for AI filling...</span>
                                </div>
                            </div>
                        </div>
                        
                        <div style="margin-top: 20px; text-align: center; font-size: 0.9em; opacity: 0.9;">
                            <i class="fas fa-info-circle"></i> 
                            <strong>Tip:</strong> Your PDF will be converted to an HTML form that AI can fill automatically!
                        </div>
                    </div>
                    
                    <!-- What's Happening Section -->
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #007bff;">
                        <h4 style="margin-top: 0;">
                            <i class="fas fa-eye"></i> What's Happening Right Now:
                        </h4>
                        <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                            <li>🔍 Sejda Desktop is analyzing your PDF structure</li>
                            <li>🤖 Our AI is understanding the context of each field</li>
                            <li>✨ Fields are being filled with intelligent data</li>
                            <li>📦 Everything is being saved automatically</li>
                        </ul>
                    </div>
                </div>
            `;
        } else if (uploadArea) {
            uploadArea.innerHTML = '<i class="fas fa-spinner fa-spin"></i><br>Processing document...';
        }
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
        formData.append('use_html_processing', useHtmlProcessing);
        
        try {
            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Check if HTML processing was used
                if (data.html_processed) {
                    console.log("HTML processing completed successfully");
                    // Redirect to document view to show HTML form
                    window.location.reload();
                    return;
                }
                
                // Check if Sejda conversion workflow completed (CHECK THIS FIRST!)
                if (data.pymupdf_converted && data.auto_download) {
                       // PyMuPDF workflow completed! Show success and auto-download
                       console.log('✅ PDF filled automatically! Auto-downloading...');
                       
                       if (uploadArea) {
                           uploadArea.innerHTML = `
                               <div style="text-align: center; padding: 40px;">
                                   <i class="fas fa-check-circle" style="color: #28a745; font-size: 64px; margin-bottom: 20px;"></i>
                                   <h2 style="color: #28a745; margin-bottom: 10px;">🎉 Success!</h2>
                                   <h3 style="margin-bottom: 20px;">PDF Filled Automatically!</h3>
                                   <p style="color: #666; margin-bottom: 30px;">
                                       ✓ AI read your document<br>
                                       ✓ Sejda detected all fields<br>
                                       ✓ AI filled everything<br>
                                       ✓ PDF saved and ready!
                                   </p>
                                   <div style="margin-bottom: 30px;">
                                       <iframe src="${data.pymupdf_fillable_url}" 
                                               style="width: 100%; height: 500px; border: 2px solid #ddd; border-radius: 8px;"
                                               title="Filled PDF Preview"></iframe>
                                   </div>
                                   <div>
                                       <a href="${data.pymupdf_fillable_url}" 
                                          class="btn btn-success btn-large" 
                                          download
                                          style="font-size: 1.2em; padding: 15px 40px; margin-right: 10px;">
                                           <i class="fas fa-download"></i> Download Filled PDF
                                       </a>
                                       <a href="${data.pymupdf_fillable_url}" 
                                          target="_blank"
                                          class="btn btn-primary btn-large" 
                                          style="font-size: 1.2em; padding: 15px 40px;">
                                           <i class="fas fa-external-link-alt"></i> Open in New Tab
                                       </a>
                                   </div>
                               </div>
                           `;
                       }
                       
                       // Auto-download the fillable PDF immediately
                       console.log('Starting auto-download...');
                       const downloadLink = document.createElement('a');
                       downloadLink.href = data.pymupdf_fillable_url;
                       downloadLink.download = 'filled_contract.pdf';
                       document.body.appendChild(downloadLink);
                       downloadLink.click();
                       document.body.removeChild(downloadLink);
                       
                       // Also open in new tab for preview
                       setTimeout(() => {
                           window.open(data.pymupdf_fillable_url, '_blank');
                       }, 1000);
                       
                       return;
                   }
                   
                   // Check if Sejda opened (but user needs to fill manually)
                   if (data.sejda_converted && !data.auto_download) {
                       // Sejda opened - show AI data for user to copy
                       console.log('✅ Sejda opened! Showing AI data...');
                       
                       if (uploadArea) {
                           // Get AI data from the document
                           const aiData = data.document?.fields?.reduce((acc, field) => {
                               if (field.ai_content) {
                                   acc[field.id] = field.ai_content;
                               }
                               return acc;
                           }, {}) || {};
                           
                           let aiDataHtml = '';
                           if (Object.keys(aiData).length > 0) {
                               aiDataHtml = `
                                   <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: left;">
                                       <h4 style="margin-top: 0; color: #007bff;">
                                           <i class="fas fa-robot"></i> AI Generated Data (Copy These Values):
                                       </h4>
                                       <div style="max-height: 300px; overflow-y: auto; font-family: monospace; font-size: 0.9em;">
                                           ${Object.entries(aiData).map(([fieldId, value], index) => 
                                               `<div style="margin-bottom: 8px; padding: 5px; background: white; border-radius: 4px;">
                                                   <strong>${index + 1}.</strong> ${fieldId}: <span style="color: #28a745;">${value}</span>
                                               </div>`
                                           ).join('')}
                                       </div>
                                   </div>
                               `;
                           }
                           
                           uploadArea.innerHTML = `
                               <div style="text-align: center; padding: 40px;">
                                   <i class="fas fa-external-link-alt" style="color: #007bff; font-size: 64px; margin-bottom: 20px;"></i>
                                   <h2 style="color: #007bff; margin-bottom: 10px;">📄 Sejda Desktop Opened!</h2>
                                   <h3 style="margin-bottom: 20px;">Your PDF is ready for filling</h3>
                                   <p style="color: #666; margin-bottom: 30px;">
                                       ✓ PDF opened in Sejda Desktop<br>
                                       ✓ AI analyzed your document<br>
                                       ✓ Ready for you to fill manually<br>
                                       ✓ Copy the data below into Sejda!
                                   </p>
                                   ${aiDataHtml}
                                   <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                                       <h4 style="margin-top: 0; color: #1976d2;">
                                           <i class="fas fa-info-circle"></i> Instructions:
                                       </h4>
                                       <ol style="text-align: left; margin: 0; padding-left: 20px;">
                                           <li>In Sejda Desktop, click <strong>"Forms"</strong> → <strong>"Detect Form Fields"</strong></li>
                                           <li>Copy the AI data from above and paste into each field</li>
                                           <li>Save the PDF with <strong>Ctrl+S</strong></li>
                                           <li>Close Sejda when done</li>
                                       </ol>
                                   </div>
                                   <div>
                                       <button onclick="window.location.href='/'" 
                                               class="btn btn-primary btn-large" 
                                               style="font-size: 1.2em; padding: 15px 40px;">
                                           <i class="fas fa-upload"></i> Upload Another PDF
                                       </button>
                                   </div>
                               </div>
                           `;
                       }
                       
                       return;
                   }
                
                   // Regular upload flow (if Sejda not available)
                if (data.training) {
                    showAutomaticTrainingResults(data.training);
                }
                   
                   if (data?.document?.fillable_pdf) {
                       const fillableUrl = data.document.fillable_pdf;
                       window.open(fillableUrl, '_blank');
                   }
                   
                   // Go back to upload page immediately
                   setTimeout(() => {
                window.location.href = '/';
                   }, 2000);
            } else {
                alert('Upload failed: ' + (data.error || 'Unknown error'));
                if (uploadArea) {
                    uploadArea.innerHTML = `
                        <i class="fas fa-cloud-upload-alt upload-icon"></i>
                        <div class="upload-text">Drop your document here or click to upload</div>
                        <div class="upload-subtext">Supports PDF, Word, Text, Images, and more document formats</div>
                    `;
                }
            }
        } catch (error) {
            console.error('Upload error:', error);
            alert('Upload failed: ' + error.message);
            if (uploadArea) {
                uploadArea.innerHTML = `
                    <i class="fas fa-cloud-upload-alt upload-icon"></i>
                    <div class="upload-text">Drop your document here or click to upload</div>
                    <div class="upload-subtext">Supports PDF, Word, Text, Images, and more document formats</div>
                `;
            }
        }
    }

    // Chat functionality
    if (chatInput && sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Enable chat input (always enabled)
        chatInput.disabled = false;
        sendBtn.disabled = false;
        
        // Add welcome message if chat is empty (handled by template now)
        // Enhanced chat is always ready
        console.log('Chat ready - Ollama status will be checked on first message');
    }

    // Field update functionality
    const fieldInputs = document.querySelectorAll('.field-input');
    fieldInputs.forEach(input => {
        input.addEventListener('blur', () => {
            const fieldId = input.dataset.fieldId;
            const content = input.value;
            updateField(fieldId, content);
        });
    });

    // AI suggestion buttons
    const aiSuggestBtns = document.querySelectorAll('.ai-suggest-btn');
    aiSuggestBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const fieldId = btn.dataset.fieldId;
            getAISuggestion(fieldId);
        });
    });

    // Delete field buttons
    const deleteFieldBtns = document.querySelectorAll('.delete-field-btn');
    deleteFieldBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const fieldId = btn.dataset.fieldId;
            deleteField(fieldId);
        });
    });

    // Bulk delete functionality
    const selectAllBtn = document.getElementById('selectAllBtn');
    const deleteSelectedBtn = document.getElementById('deleteSelectedBtn');
    const selectedCountSpan = document.getElementById('selectedCount');
    const fieldCheckboxes = document.querySelectorAll('.field-checkbox');

    // Update selected count and show/hide delete button
    function updateSelectedCount() {
        const checkedBoxes = document.querySelectorAll('.field-checkbox:checked');
        const count = checkedBoxes.length;
        if (selectedCountSpan) selectedCountSpan.textContent = count;
        if (deleteSelectedBtn) {
            deleteSelectedBtn.style.display = count > 0 ? 'inline-block' : 'none';
        }
        
        // Update Select All button text
        if (selectAllBtn) {
            const allCheckboxes = document.querySelectorAll('.field-checkbox');
            if (count === allCheckboxes.length && count > 0) {
                selectAllBtn.innerHTML = '<i class="fas fa-square"></i> Deselect All';
            } else {
                selectAllBtn.innerHTML = '<i class="fas fa-check-square"></i> Select All';
            }
        }
    }

    // Select/Deselect All button
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            const allCheckboxes = document.querySelectorAll('.field-checkbox');
            const checkedCount = document.querySelectorAll('.field-checkbox:checked').length;
            const shouldCheck = checkedCount !== allCheckboxes.length;
            
            allCheckboxes.forEach(checkbox => {
                checkbox.checked = shouldCheck;
            });
            updateSelectedCount();
        });
    }

    // Checkbox change events
    fieldCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedCount);
    });

    // Delete Selected button
    if (deleteSelectedBtn) {
        deleteSelectedBtn.addEventListener('click', () => {
            deleteSelectedFields();
        });
    }

    // PDF generation
    if (generatePdfBtn && documentId) {
        generatePdfBtn.addEventListener('click', generatePDF);
    }

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessage(message, 'user');
        chatInput.value = '';
        sendBtn.disabled = true;
        
        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message bot typing-indicator';
        typingIndicator.id = 'typingIndicator';
        typingIndicator.innerHTML = `
            <div class="message-content">
                <i class="fas fa-robot"></i> AI is thinking
                <span class="dots">
                    <span>.</span><span>.</span><span>.</span>
                </span>
            </div>
        `;
        if (chatMessages) {
            chatMessages.appendChild(typingIndicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        try {
            let url = documentId ? `/api/chat/${documentId}/` : '/api/chat/general/';
            console.log('Sending message to:', url);
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message })
            });

            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);
            
            // Remove typing indicator
            const typingIndicator = document.getElementById('typingIndicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            if (data.success) {
                addMessage(data.response, 'bot');
                
                // Check if any fields were filled from the conversation
                if (data.filled_fields && data.filled_fields.length > 0) {
                    // Update the UI with filled fields
                    data.filled_fields.forEach(field => {
                        const input = document.querySelector(`input[data-field-id="${field.id}"]`);
                        if (input) {
                            input.value = field.content;
                            // Add visual indication that field was filled by AI
                            input.style.backgroundColor = '#e8f5e8';
                            input.style.borderColor = '#28a745';
                            
                            // Show a notification
                            addMessage(`✅ Filled ${field.type} field: "${field.content}"`, 'bot');
                        }
                    });
                }
            } else {
                addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
        } catch (error) {
            console.error('Chat error:', error);
            
            // Remove typing indicator
            const typingIndicator = document.getElementById('typingIndicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            addMessage('Sorry, I encountered an error. Please try again. Error: ' + error.message, 'bot');
        } finally {
            sendBtn.disabled = false;
        }
    }

    async function updateField(fieldId, content) {
        if (!documentId) return;

        try {
            await fetch(`/api/documents/${documentId}/update-field/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    field_id: fieldId,
                    content: content
                })
            });
        } catch (error) {
            console.error('Failed to update field:', error);
        }
    }

    async function getAISuggestion(fieldId) {
        if (!documentId) return;

        try {
            const response = await fetch(`/api/chat/${documentId}/suggest-content/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    field_id: fieldId,
                    user_input: ''
                })
            });

            const data = await response.json();
            if (data.success) {
                const fieldInput = document.querySelector(`[data-field-id="${fieldId}"]`);
                if (fieldInput) {
                    fieldInput.value = data.suggestion;
                    updateField(fieldId, data.suggestion);
                }
            }
        } catch (error) {
            console.error('Failed to get AI suggestion:', error);
        }
    }

    async function deleteField(fieldId) {
        if (!documentId) return;

        // Confirm deletion
        if (!confirm(`Are you sure you want to delete Field ${fieldId}? This will be permanently removed from the backend.`)) {
            return;
        }

        try {
            // Find the field item container
            const fieldItem = document.querySelector(`.field-item[data-field-id="${fieldId}"]`);
            
            // Add a visual effect to show it's being deleted
            if (fieldItem) {
                fieldItem.style.opacity = '0.5';
                fieldItem.style.transition = 'opacity 0.3s ease';
            }

            // Call backend to delete the field
            console.log(`Deleting field ${fieldId} from document ${documentId}`);
            const response = await fetch(`/api/documents/${documentId}/delete-field/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    field_id: fieldId
                })
            });

            console.log(`Delete response status: ${response.status}`);
            const data = await response.json();
            console.log('Delete response data:', data);
            
            if (data.success) {
                // Remove the field from the UI
                if (fieldItem) {
                    setTimeout(() => {
                        fieldItem.remove();
                    }, 300);
                }

                // Add message to chat
                addMessage(`✅ Field ${fieldId} deleted! ${data.remaining_fields} fields remaining.`, 'bot');
            } else {
                if (fieldItem) fieldItem.style.opacity = '1';
                addMessage(`❌ Failed to delete Field ${fieldId}: ${data.error || JSON.stringify(data)}`, 'bot');
            }

        } catch (error) {
            console.error('Failed to delete field:', error);
            const fieldItem = document.querySelector(`.field-item[data-field-id="${fieldId}"]`);
            if (fieldItem) fieldItem.style.opacity = '1';
            addMessage(`❌ Failed to delete Field ${fieldId}. Please try again.`, 'bot');
        }
    }

    async function deleteSelectedFields() {
        if (!documentId) return;

        const checkedBoxes = document.querySelectorAll('.field-checkbox:checked');
        const fieldIds = Array.from(checkedBoxes).map(cb => cb.dataset.fieldId);
        
        if (fieldIds.length === 0) {
            addMessage('❌ No fields selected for deletion.', 'bot');
            return;
        }

        // Confirm bulk deletion
        if (!confirm(`Are you sure you want to delete ${fieldIds.length} fields? This will be permanently removed from the backend.`)) {
            return;
        }

        addMessage(`🗑️ Deleting ${fieldIds.length} fields...`, 'bot');

        let successCount = 0;
        let failCount = 0;

        // Delete fields one by one
        for (const fieldId of fieldIds) {
            try {
                const fieldItem = document.querySelector(`.field-item[data-field-id="${fieldId}"]`);
                
                if (fieldItem) {
                    fieldItem.style.opacity = '0.5';
                    fieldItem.style.transition = 'opacity 0.3s ease';
                }

                const response = await fetch(`/api/documents/${documentId}/delete-field/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        field_id: fieldId
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    successCount++;
                    if (fieldItem) {
                        setTimeout(() => {
                            fieldItem.remove();
                        }, 300);
                    }
                } else {
                    failCount++;
                    if (fieldItem) fieldItem.style.opacity = '1';
                }

            } catch (error) {
                console.error(`Failed to delete field ${fieldId}:`, error);
                failCount++;
                const fieldItem = document.querySelector(`.field-item[data-field-id="${fieldId}"]`);
                if (fieldItem) fieldItem.style.opacity = '1';
            }
        }

        // Show results
        if (successCount > 0) {
            addMessage(`✅ Successfully deleted ${successCount} field(s)!`, 'bot');
        }
        if (failCount > 0) {
            addMessage(`❌ Failed to delete ${failCount} field(s).`, 'bot');
        }

        // Reset checkboxes and update count
        setTimeout(() => {
            updateSelectedCount();
        }, 500);
    }

    async function generatePDF() {
        if (!documentId) return;

        generatePdfBtn.disabled = true;
        generatePdfBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating PDF...';

        try {
            const response = await fetch(`/generate-pdf/${documentId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();
            if (data.success) {
                // Download the PDF using the URL from the response
                if (data.pdf_url) {
                    const downloadLink = document.createElement('a');
                    downloadLink.href = data.pdf_url;
                    downloadLink.download = data.pdf_url.split('/').pop();
                    downloadLink.click();
                } else {
                    alert('PDF generated but download URL not provided.');
                }
            } else {
                alert('Failed to generate PDF. Please try again.');
            }
        } catch (error) {
            alert('Failed to generate PDF. Please try again.');
        } finally {
            generatePdfBtn.disabled = false;
            generatePdfBtn.innerHTML = '<i class="fas fa-download"></i> Generate & Download PDF';
        }
    }

    function addMessage(content, type) {
        console.log('Adding message:', content, 'type:', type);
        console.log('chatMessages element:', chatMessages);
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        // Add animation
        messageDiv.style.animation = 'fadeIn 0.3s ease-in';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Support HTML content for bot messages (for rich formatting)
        if (type === 'bot') {
            contentDiv.innerHTML = content;
        } else {
            contentDiv.textContent = content;
        }
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);
        
        if (chatMessages) {
            chatMessages.appendChild(messageDiv);
            // Smooth scroll to bottom
            chatMessages.scrollTo({
                top: chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        } else {
            console.error('chatMessages element not found!');
        }
    }
    
    // Add Custom Field functionality
    console.log('🔍 DEBUG: Initializing Add Custom Field functionality...');
    console.log('🔍 DEBUG: Document ready state:', document.readyState);
    
    // Check if we're on the right page
    const isIndexPage = window.location.pathname === '/' || window.location.pathname.includes('index');
    console.log('🔍 DEBUG: Is index page:', isIndexPage);
    
    // Field counter
    let fieldCounter = 0;
    
    // Edit mode state
    let editModeActive = false;
    
    // Drag operation state
    let isDragOperation = false;
    
    // Wait for DOM to be fully loaded
    if (document.readyState === 'loading') {
        console.log('🔍 DEBUG: DOM still loading, waiting...');
        document.addEventListener('DOMContentLoaded', initializeAddCustomField);
    } else {
        console.log('🔍 DEBUG: DOM already loaded, initializing immediately');
        initializeAddCustomField();
    }
    
    function initializeAddCustomField() {
        console.log('🔍 DEBUG: initializeAddCustomField called');
        
        // Check if document is loaded first
        const documentLoaded = document.getElementById('documentLoaded');
        console.log('🔍 DEBUG: documentLoaded element found:', !!documentLoaded);
        
        const addCustomFieldBtn = document.getElementById('addCustomFieldBtn');
        const cancelAddFieldBtn = document.getElementById('cancelAddFieldBtn');
        
        console.log('🔍 DEBUG: addCustomFieldBtn found:', !!addCustomFieldBtn);
        console.log('🔍 DEBUG: cancelAddFieldBtn found:', !!cancelAddFieldBtn);
        
        // Check all elements with "add" in their ID
        const allElements = document.querySelectorAll('[id*="add"]');
        console.log('🔍 DEBUG: All elements with "add" in ID:', Array.from(allElements).map(el => el.id));
        
        // Check if the form header exists
        const formHeader = document.querySelector('.form-header');
        console.log('🔍 DEBUG: form-header found:', !!formHeader);
        if (formHeader) {
            console.log('🔍 DEBUG: form-header HTML:', formHeader.innerHTML);
        }
        
        // Also check if the button is visible
        if (addCustomFieldBtn) {
            console.log('🔍 DEBUG: Button text:', addCustomFieldBtn.textContent);
            console.log('🔍 DEBUG: Button style display:', window.getComputedStyle(addCustomFieldBtn).display);
            console.log('🔍 DEBUG: Button style visibility:', window.getComputedStyle(addCustomFieldBtn).visibility);
            
            // Add a temporary visual indicator to confirm button is found
            addCustomFieldBtn.style.border = '2px solid red';
            setTimeout(() => {
                if (addCustomFieldBtn) {
                    addCustomFieldBtn.style.border = '';
                }
            }, 3000);
        }
        
        if (addCustomFieldBtn) {
            console.log('🔍 DEBUG: Adding click event listener to addCustomFieldBtn');
            addCustomFieldBtn.addEventListener('click', function(e) {
                console.log('🔍 DEBUG: Add Custom Field button clicked!', e);
                e.preventDefault();
                e.stopPropagation();
                enableAddFieldMode();
            });
        } else {
            console.error('❌ DEBUG: addCustomFieldBtn not found! Check if button exists in HTML');
        }
        
        if (cancelAddFieldBtn) {
            console.log('🔍 DEBUG: Adding click event listener to cancelAddFieldBtn');
            cancelAddFieldBtn.addEventListener('click', function(e) {
                console.log('🔍 DEBUG: Cancel Add Field button clicked!', e);
                e.preventDefault();
                e.stopPropagation();
                disableAddFieldMode();
            });
        } else {
            console.log('🔍 DEBUG: cancelAddFieldBtn not found (this is normal if not in add mode)');
        }
        
        // Add event listener for Delete All Fields button
        const deleteAllFieldsBtn = document.getElementById('deleteAllFieldsBtn');
        if (deleteAllFieldsBtn) {
            console.log('🔍 DEBUG: Adding click event listener to deleteAllFieldsBtn');
            deleteAllFieldsBtn.addEventListener('click', function(e) {
                console.log('🔍 DEBUG: Delete All Fields button clicked!', e);
                e.preventDefault();
                e.stopPropagation();
                deleteAllCustomFields();
            });
        } else {
            console.log('🔍 DEBUG: deleteAllFieldsBtn not found');
        }
        
        // Add event listener for Edit Mode button
        const editModeBtn = document.getElementById('editModeBtn');
        if (editModeBtn) {
            console.log('🔍 DEBUG: Adding click event listener to editModeBtn');
            editModeBtn.addEventListener('click', function(e) {
                console.log('🔍 DEBUG: Edit Mode button clicked!', e);
                e.preventDefault();
                e.stopPropagation();
                toggleEditMode();
            });
        } else {
            console.log('🔍 DEBUG: editModeBtn not found');
        }
        
        // Fallback: Check again after a delay in case elements are loaded dynamically
        setTimeout(() => {
            console.log('🔍 DEBUG: Fallback check - looking for button again...');
            const delayedBtn = document.getElementById('addCustomFieldBtn');
            if (delayedBtn && !addCustomFieldBtn) {
                console.log('🔍 DEBUG: Button found in delayed check! Adding event listener...');
                delayedBtn.addEventListener('click', function(e) {
                    console.log('🔍 DEBUG: Add Custom Field button clicked (delayed)!', e);
                    e.preventDefault();
                    e.stopPropagation();
                    enableAddFieldMode();
                });
            }
        }, 2000);
        
        // Watch for dynamic content changes
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // Element node
                            const newBtn = node.id === 'addCustomFieldBtn' ? node : node.querySelector('#addCustomFieldBtn');
                            if (newBtn) {
                                console.log('🔍 DEBUG: Button detected via MutationObserver!', newBtn);
                                newBtn.addEventListener('click', function(e) {
                                    console.log('🔍 DEBUG: Add Custom Field button clicked (observer)!', e);
                                    e.preventDefault();
                                    e.stopPropagation();
                                    enableAddFieldMode();
                                });
                            }
                        }
                    });
                }
            });
        });
        
        // Start observing
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        console.log('🔍 DEBUG: MutationObserver started to watch for button');
        
        // Also add a global function to manually check for the button
        window.checkForAddCustomFieldButton = function() {
            console.log('🔍 DEBUG: Manual check for Add Custom Field button...');
            const btn = document.getElementById('addCustomFieldBtn');
            if (btn) {
                console.log('🔍 DEBUG: Button found in manual check!', btn);
                btn.addEventListener('click', function(e) {
                    console.log('🔍 DEBUG: Add Custom Field button clicked (manual)!', e);
                    e.preventDefault();
                    e.stopPropagation();
                    enableAddFieldMode();
                });
                return true;
            } else {
                console.log('🔍 DEBUG: Button still not found in manual check');
                return false;
            }
        };
        
        console.log('🔍 DEBUG: Manual check function available as window.checkForAddCustomFieldButton()');
    }
    
    function toggleEditMode() {
        console.log('🔍 DEBUG: toggleEditMode called, current state:', editModeActive);
        
        editModeActive = !editModeActive;
        const editModeBtn = document.getElementById('editModeBtn');
        const editModeButtons = document.getElementById('editModeButtons');
        
        if (editModeActive) {
            // Activate edit mode
            console.log('🔍 DEBUG: Activating edit mode');
            editModeBtn.innerHTML = '<i class="fas fa-times-circle"></i> Exit Edit Mode';
            editModeBtn.style.background = 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)';
            
            if (editModeButtons) {
                editModeButtons.style.display = 'flex';
            }
            
            // Show delete buttons on existing fields
            showDeleteButtonsOnFields();
            
            addMessage('✏️ <strong>Edit Mode Activated!</strong><br>You can now add and delete custom fields.', 'bot');
        } else {
            // Deactivate edit mode
            console.log('🔍 DEBUG: Deactivating edit mode');
            editModeBtn.innerHTML = '<i class="fas fa-edit"></i> Edit Mode';
            editModeBtn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
            
            if (editModeButtons) {
                editModeButtons.style.display = 'none';
            }
            
            // Hide delete buttons on existing fields
            hideDeleteButtonsOnFields();
            
            // Exit add field mode if active
            if (document.getElementById('addFieldInstructions').style.display !== 'none') {
                disableAddFieldMode();
            }
            
            addMessage('✅ <strong>Edit Mode Deactivated!</strong><br>Back to normal view mode.', 'bot');
        }
    }
    
    function showDeleteButtonsOnFields() {
        console.log('🔍 DEBUG: Showing delete buttons and enabling drag on existing fields');
        try {
            const iframe = document.getElementById('htmlFormIframe');
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            
            const deleteButtons = iframeDoc.querySelectorAll('[id^="delete_btn_"]');
            deleteButtons.forEach(btn => {
                btn.style.display = 'block';
            });
            
            const dragHandles = iframeDoc.querySelectorAll('[id^="drag_handle_"]');
            dragHandles.forEach(handle => {
                handle.style.cursor = 'move';
                handle.title = 'Drag to move';
            });
        } catch (error) {
            console.error('Error showing delete buttons:', error);
        }
    }
    
    function hideDeleteButtonsOnFields() {
        console.log('🔍 DEBUG: Hiding delete buttons and disabling drag on existing fields');
        try {
            const iframe = document.getElementById('htmlFormIframe');
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            
            const deleteButtons = iframeDoc.querySelectorAll('[id^="delete_btn_"]');
            deleteButtons.forEach(btn => {
                btn.style.display = 'none';
            });
            
            const dragHandles = iframeDoc.querySelectorAll('[id^="drag_handle_"]');
            dragHandles.forEach(handle => {
                handle.style.cursor = 'default';
                handle.title = 'Edit mode required to move';
            });
        } catch (error) {
            console.error('Error hiding delete buttons:', error);
        }
    }
    
    function enableAddFieldMode() {
        console.log('🔍 DEBUG: enableAddFieldMode() called');
        
        // Check if edit mode is active
        if (!editModeActive) {
            console.log('🔍 DEBUG: Edit mode not active, cannot enable add field mode');
            addMessage('⚠️ <strong>Edit Mode Required!</strong><br>Please activate Edit Mode first to add custom fields.', 'bot');
            return;
        }
        
        const instructions = document.getElementById('addFieldInstructions');
        const addFieldBtn = document.getElementById('addCustomFieldBtn');
        const iframe = document.getElementById('htmlFormIframe');
        
        console.log('🔍 DEBUG: instructions element found:', !!instructions);
        console.log('🔍 DEBUG: addFieldBtn element found:', !!addFieldBtn);
        console.log('🔍 DEBUG: iframe element found:', !!iframe);
        
        if (instructions) {
            console.log('🔍 DEBUG: Showing instructions banner');
            instructions.style.display = 'block';
        } else {
            console.error('❌ DEBUG: instructions element not found!');
        }
        
        if (addFieldBtn) {
            console.log('🔍 DEBUG: Updating button to active state');
            addFieldBtn.innerHTML = '<i class="fas fa-times-circle"></i> Exit Mode';
            addFieldBtn.style.background = '#dc3545';
            addFieldBtn.disabled = false;
            addFieldBtn.onclick = function() {
                disableAddFieldMode();
            };
        } else {
            console.error('❌ DEBUG: addFieldBtn element not found!');
        }
        
        if (iframe) {
            console.log('🔍 DEBUG: Updating iframe styling');
            iframe.style.border = '3px solid #667eea';
            iframe.style.cursor = 'crosshair';
            iframe.style.boxShadow = '0 0 20px rgba(102, 126, 234, 0.5)';
            
            // Add click event to iframe content
            try {
                console.log('🔍 DEBUG: Attempting to access iframe content');
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                console.log('🔍 DEBUG: iframeDoc found:', !!iframeDoc);
                if (iframeDoc) {
                    iframeDoc.addEventListener('click', handleIframeClick);
                    console.log('🔍 DEBUG: Click event listener added to iframe');
                }
            } catch(e) {
                console.error('❌ DEBUG: Could not access iframe:', e);
            }
        } else {
            console.error('❌ DEBUG: iframe element not found!');
        }
        
        console.log('🔍 DEBUG: Sending chat message');
        addMessage('✨ <strong>Add Field Mode Activated!</strong><br>Click anywhere in the document to create an editable field at that exact location!', 'bot');
        console.log('🔍 DEBUG: enableAddFieldMode() completed');
    }
    
    function disableAddFieldMode() {
        const instructions = document.getElementById('addFieldInstructions');
        const addFieldBtn = document.getElementById('addCustomFieldBtn');
        const iframe = document.getElementById('htmlFormIframe');
        
        if (instructions) {
            instructions.style.display = 'none';
        }
        
        if (addFieldBtn) {
            addFieldBtn.innerHTML = '<i class="fas fa-plus-circle"></i> Add Custom Field';
            addFieldBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
            addFieldBtn.disabled = false;
        }
        
        if (iframe) {
            iframe.style.border = '2px solid #ddd';
            iframe.style.cursor = 'default';
            iframe.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
            
            // Remove click event from iframe
            try {
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                iframeDoc.removeEventListener('click', handleIframeClick);
            } catch(e) {
                console.error('Could not access iframe:', e);
            }
        }
    }
    
    function handleIframeClick(event) {
        console.log('🔍 DEBUG: handleIframeClick called', event);
        console.log('🔍 DEBUG: Event target:', event.target);
        console.log('🔍 DEBUG: Event type:', event.type);
        console.log('🔍 DEBUG: isDragOperation:', isDragOperation);
        
        // Check if we're in the middle of a drag operation
        if (isDragOperation) {
            console.log('🔍 DEBUG: Drag operation in progress, ignoring click');
            return;
        }
        
        // Check if clicked on an existing custom field or any of its children
        const clickedElement = event.target;
        const isCustomField = clickedElement.closest('[id^="field_container_custom_field_"]');
        const isDragHandle = clickedElement.id && clickedElement.id.startsWith('drag_handle_');
        const isDeleteButton = clickedElement.id && clickedElement.id.startsWith('delete_btn_');
        const isFieldInput = clickedElement.id && clickedElement.id.startsWith('custom_field_');
        
        // Additional check for drag handle clicks specifically
        if (clickedElement.id && clickedElement.id.includes('drag_handle_custom_field_')) {
            console.log('🔍 DEBUG: Clicked on drag handle, ignoring');
            return;
        }
        
        if (isCustomField || isDragHandle || isDeleteButton || isFieldInput) {
            console.log('🔍 DEBUG: Clicked on existing custom field or its components, ignoring');
            console.log('🔍 DEBUG: isCustomField:', isCustomField, 'isDragHandle:', isDragHandle, 'isDeleteButton:', isDeleteButton, 'isFieldInput:', isFieldInput);
            return;
        }
        
        event.preventDefault();
        event.stopPropagation();
        
        // Get the iframe and its position
        const iframe = document.getElementById('htmlFormIframe');
        console.log('🔍 DEBUG: iframe element:', iframe);
        
        if (!iframe) {
            console.error('❌ DEBUG: iframe not found in handleIframeClick!');
            return;
        }
        
        const iframeRect = iframe.getBoundingClientRect();
        
        // Calculate relative position within the iframe
        const relativeX = event.clientX - iframeRect.left;
        const relativeY = event.clientY - iframeRect.top;
        
        console.log('🔍 DEBUG: Click position:', { relativeX, relativeY });
        console.log('🔍 DEBUG: Client position:', { clientX: event.clientX, clientY: event.clientY });
        console.log('🔍 DEBUG: Iframe rect:', iframeRect);
        
        // Check if coordinates are valid
        if (relativeX < 0 || relativeY < 0 || relativeX > iframeRect.width || relativeY > iframeRect.height) {
            console.warn('⚠️ DEBUG: Click coordinates outside iframe bounds!');
            console.log('🔍 DEBUG: Coordinates check:', {
                relativeX, relativeY, 
                iframeWidth: iframeRect.width, 
                iframeHeight: iframeRect.height
            });
        }
        
        // Create field immediately at click position
        createFieldAtPosition(relativeX, relativeY);
    }
    
    function createFieldAtPosition(x, y) {
        fieldCounter++;
        console.log('🔍 DEBUG: createFieldAtPosition called with:', { x, y });
        console.log('🔍 DEBUG: Field attempt #', fieldCounter);
        
        try {
            const iframe = document.getElementById('htmlFormIframe');
            console.log('🔍 DEBUG: iframe found:', !!iframe);
            
            if (!iframe) {
                console.error('❌ DEBUG: iframe not found!');
                addMessage('❌ <strong>Error:</strong> Document iframe not found.', 'bot');
                return;
            }
            
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            console.log('🔍 DEBUG: iframeDoc found:', !!iframeDoc);
            
            if (!iframeDoc) {
                console.error('❌ DEBUG: iframeDoc not found!');
                addMessage('❌ <strong>Error:</strong> Cannot access document content.', 'bot');
                return;
            }
            
            // Create a simple editable field with delete button and drag handle
            const fieldId = `custom_field_${Date.now()}`;
            const fieldHTML = `
                <div id="field_container_${fieldId}" style="position: absolute; left: ${x}px; top: ${y}px; z-index: 1000; background: white; border: 2px solid #667eea; border-radius: 4px; padding: 5px; min-width: 150px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); user-select: none;">
                    <div style="display: flex; align-items: center; gap: 5px;">
                        <div id="drag_handle_${fieldId}" style="font-size: 10px; color: #667eea; cursor: ${editModeActive ? 'move' : 'default'}; flex: 1;" title="${editModeActive ? 'Drag to move' : 'Edit mode required to move'}">📍 (${x}, ${y})</div>
                        <button id="delete_btn_${fieldId}" 
                                style="background: #dc3545; color: white; border: none; border-radius: 3px; padding: 2px 6px; font-size: 10px; cursor: pointer; display: ${editModeActive ? 'block' : 'none'};"
                                title="Delete field">
                            ✕
                        </button>
                    </div>
                    <input type="text" 
                           id="${fieldId}" 
                           placeholder="Click to edit..." 
                           style="border: none; background: transparent; width: 100%; font-size: 12px; outline: none; margin-top: 2px;"
                           onfocus="this.style.background='#f0f8ff';"
                           onblur="this.style.background='transparent';">
                </div>
            `;
            
            // Insert the field
            const tempDiv = iframeDoc.createElement('div');
            tempDiv.innerHTML = fieldHTML;
            const fieldElement = tempDiv.firstElementChild;
            
            console.log('🔍 DEBUG: fieldElement created:', !!fieldElement);
            console.log('🔍 DEBUG: iframeDoc.body found:', !!iframeDoc.body);
            
            // Add to document body for absolute positioning
            if (iframeDoc.body) {
                iframeDoc.body.appendChild(fieldElement);
                console.log('🔍 DEBUG: Field appended to body');
            } else {
                console.error('❌ DEBUG: iframeDoc.body not found!');
                addMessage('❌ <strong>Error:</strong> Cannot find document body.', 'bot');
                return;
            }
            
            // Verify field was added
            const addedField = iframeDoc.getElementById(`field_container_${fieldId}`);
            console.log('🔍 DEBUG: Field verification:', !!addedField);
            
            if (!addedField) {
                console.error('❌ DEBUG: Field was not added successfully!');
                addMessage('❌ <strong>Error:</strong> Field was not added to document.', 'bot');
                return;
            }
            
            // Add event listener to delete button
            const deleteBtn = iframeDoc.getElementById(`delete_btn_${fieldId}`);
            if (deleteBtn) {
                console.log('🔍 DEBUG: Adding delete button event listener');
                deleteBtn.addEventListener('click', function(e) {
                    console.log('🔍 DEBUG: Delete button clicked for field:', fieldId);
                    e.preventDefault();
                    e.stopPropagation();
                    deleteCustomField(fieldId);
                });
            } else {
                console.error('❌ DEBUG: Delete button not found!');
            }
            
            // Add drag functionality
            const dragHandle = iframeDoc.getElementById(`drag_handle_${fieldId}`);
            if (dragHandle) {
                console.log('🔍 DEBUG: Adding drag functionality');
                makeFieldDraggable(fieldElement, dragHandle, fieldId);
            } else {
                console.error('❌ DEBUG: Drag handle not found!');
            }
            
            // Focus the field
            setTimeout(() => {
                const input = iframeDoc.getElementById(fieldId);
                if (input) {
                    input.focus();
                    input.select();
                    console.log('🔍 DEBUG: Field focused successfully');
                } else {
                    console.error('❌ DEBUG: Could not focus field input');
                }
            }, 100);
            
            console.log('🔍 DEBUG: Field created at position:', { x, y });
            console.log('🔍 DEBUG: Field element:', fieldElement);
            console.log('🔍 DEBUG: Field HTML:', fieldHTML);
            
            // Show success message
            addMessage(`✅ <strong>Field #${fieldCounter} Added!</strong><br>Editable field created at position (${x}, ${y}).`, 'bot');
            
        } catch (error) {
            console.error('Error creating field:', error);
            addMessage('❌ <strong>Error:</strong> Could not create field. ' + error.message, 'bot');
        }
    }
    
    function makeFieldDraggable(fieldElement, dragHandle, fieldId) {
        console.log('🔍 DEBUG: makeFieldDraggable called for:', fieldId);
        
        let isDragging = false;
        let startX, startY, initialX, initialY;
        
        dragHandle.addEventListener('mousedown', function(e) {
            // Only allow dragging in edit mode
            if (!editModeActive) {
                console.log('🔍 DEBUG: Drag blocked - edit mode not active');
                return;
            }
            
            console.log('🔍 DEBUG: Drag started for field:', fieldId);
            isDragging = true;
            isDragOperation = true; // Set global drag flag
            
            // Clear drag flag after a timeout as safety measure
            setTimeout(() => {
                if (isDragOperation) {
                    console.log('🔍 DEBUG: Clearing drag flag after timeout');
                    isDragOperation = false;
                }
            }, 1000);
            
            // Get initial positions
            startX = e.clientX;
            startY = e.clientY;
            initialX = parseInt(fieldElement.style.left) || 0;
            initialY = parseInt(fieldElement.style.top) || 0;
            
            // Add dragging styles
            fieldElement.style.cursor = 'grabbing';
            fieldElement.style.zIndex = '2000';
            fieldElement.style.opacity = '0.8';
            fieldElement.style.transform = 'rotate(2deg)';
            
            // Prevent text selection and event bubbling
            e.preventDefault();
            e.stopPropagation();
        });
        
        // Add global mouse move and up listeners to the iframe document
        const iframe = document.getElementById('htmlFormIframe');
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        
        iframeDoc.addEventListener('mousemove', function(e) {
            if (!isDragging) return;
            
            // Calculate new position
            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            const newX = initialX + deltaX;
            const newY = initialY + deltaY;
            
            // Update position
            fieldElement.style.left = newX + 'px';
            fieldElement.style.top = newY + 'px';
            
            // Update coordinates display
            const coordDisplay = dragHandle;
            coordDisplay.textContent = `📍 (${newX}, ${newY})`;
        });
        
        iframeDoc.addEventListener('mouseup', function(e) {
            if (!isDragging) return;
            
            console.log('🔍 DEBUG: Drag ended for field:', fieldId);
            isDragging = false;
            
            // Remove dragging styles
            fieldElement.style.cursor = '';
            fieldElement.style.zIndex = '1000';
            fieldElement.style.opacity = '1';
            fieldElement.style.transform = '';
            
            // Get final position
            const finalX = parseInt(fieldElement.style.left) || 0;
            const finalY = parseInt(fieldElement.style.top) || 0;
            
            console.log('🔍 DEBUG: Field moved to position:', { x: finalX, y: finalY });
            addMessage(`🔄 <strong>Field Moved!</strong><br>Custom field repositioned to (${finalX}, ${finalY}).`, 'bot');
            
            // Clear drag flag after a short delay to prevent click events
            setTimeout(() => {
                isDragOperation = false;
                console.log('🔍 DEBUG: Drag operation flag cleared after delay');
            }, 100);
        });
        
        // Prevent dragging when clicking on input field
        const inputField = iframeDoc.getElementById(fieldId);
        if (inputField) {
            inputField.addEventListener('mousedown', function(e) {
                e.stopPropagation();
            });
        }
        
        // Prevent field container clicks from triggering add field mode
        fieldElement.addEventListener('mousedown', function(e) {
            console.log('🔍 DEBUG: Field container clicked, preventing event bubbling');
            e.stopPropagation();
        });
        
        fieldElement.addEventListener('click', function(e) {
            console.log('🔍 DEBUG: Field container clicked, preventing event bubbling');
            e.stopPropagation();
        });
        
        // Prevent drag handle clicks from triggering add field mode
        dragHandle.addEventListener('click', function(e) {
            console.log('🔍 DEBUG: Drag handle clicked, preventing event bubbling');
            e.preventDefault();
            e.stopPropagation();
        });
        
        dragHandle.addEventListener('mousedown', function(e) {
            console.log('🔍 DEBUG: Drag handle mousedown, preventing event bubbling');
            e.preventDefault();
            e.stopPropagation();
        });
    }
    
    // Delete custom field function
    window.deleteCustomField = function(fieldId) {
        console.log('🔍 DEBUG: deleteCustomField called for:', fieldId);
        
        try {
            const iframe = document.getElementById('htmlFormIframe');
            console.log('🔍 DEBUG: iframe found for delete:', !!iframe);
            
            if (!iframe) {
                console.error('❌ DEBUG: iframe not found for delete!');
                addMessage('❌ <strong>Error:</strong> Document iframe not found.', 'bot');
                return;
            }
            
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            console.log('🔍 DEBUG: iframeDoc found for delete:', !!iframeDoc);
            
            if (!iframeDoc) {
                console.error('❌ DEBUG: iframeDoc not found for delete!');
                addMessage('❌ <strong>Error:</strong> Cannot access document content.', 'bot');
                return;
            }
            
            // Find and remove the field container
            const fieldContainer = iframeDoc.getElementById(`field_container_${fieldId}`);
            console.log('🔍 DEBUG: fieldContainer found:', !!fieldContainer);
            console.log('🔍 DEBUG: Looking for ID:', `field_container_${fieldId}`);
            
            if (fieldContainer) {
                fieldContainer.remove();
                console.log('🔍 DEBUG: Field deleted successfully');
                addMessage(`🗑️ <strong>Field Deleted!</strong><br>Custom field has been removed.`, 'bot');
            } else {
                console.log('🔍 DEBUG: Field container not found');
                console.log('🔍 DEBUG: Available elements with similar IDs:');
                const allElements = iframeDoc.querySelectorAll('[id*="field_container"]');
                allElements.forEach(el => console.log('🔍 DEBUG: Found element:', el.id));
                addMessage('❌ <strong>Error:</strong> Field not found for deletion.', 'bot');
            }
        } catch (error) {
            console.error('Error deleting field:', error);
            addMessage('❌ <strong>Error:</strong> Could not delete field. ' + error.message, 'bot');
        }
    };
    
    // Delete all custom fields function
    window.deleteAllCustomFields = function() {
        console.log('🔍 DEBUG: deleteAllCustomFields called');
        
        if (!confirm('Are you sure you want to delete ALL custom fields? This cannot be undone.')) {
            return;
        }
        
        try {
            const iframe = document.getElementById('htmlFormIframe');
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            
            // Find all custom field containers
            const fieldContainers = iframeDoc.querySelectorAll('[id^="field_container_custom_field_"]');
            console.log('🔍 DEBUG: Found', fieldContainers.length, 'custom fields to delete');
            
            let deletedCount = 0;
            fieldContainers.forEach(container => {
                container.remove();
                deletedCount++;
            });
            
            if (deletedCount > 0) {
                console.log('🔍 DEBUG: Deleted', deletedCount, 'custom fields');
                addMessage(`🗑️ <strong>All Fields Deleted!</strong><br>Removed ${deletedCount} custom field(s).`, 'bot');
            } else {
                addMessage('ℹ️ <strong>No Fields Found</strong><br>No custom fields to delete.', 'bot');
            }
            
        } catch (error) {
            console.error('Error deleting all fields:', error);
            addMessage('❌ <strong>Error:</strong> Could not delete fields. ' + error.message, 'bot');
        }
    };
    

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Training functionality
    const trainBtn = document.getElementById('trainBtn');
    const trainingStatus = document.getElementById('trainingStatus');
    const trainingInfo = document.getElementById('trainingInfo');

    if (trainBtn) {
        trainBtn.addEventListener('click', function() {
            const documentId = document.getElementById('documentId')?.value;
            if (!documentId) {
                alert('No document loaded');
                return;
            }

            trainBtn.disabled = true;
            trainBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Training...';

            fetch(`/${documentId}/train/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showTrainingResults(data.training);
                    addMessage(`Training completed successfully! Added ${data.training.samples_added} samples.`, 'bot');
                } else {
                    alert('Training failed: ' + data.message);
                    addMessage('Training failed: ' + data.message, 'bot');
                }
            })
            .catch(error => {
                console.error('Training error:', error);
                alert('Training failed: ' + error.message);
                addMessage('Training failed: ' + error.message, 'bot');
            })
            .finally(() => {
                trainBtn.disabled = false;
                trainBtn.innerHTML = '<i class="fas fa-graduation-cap"></i> Train System';
            });
        });
    }

    function showTrainingResults(training) {
        if (!trainingStatus || !trainingInfo) return;

        const resultsHtml = `
            <div class="training-result">
                <p><strong>Samples Added:</strong> ${training.samples_added}</p>
                <p><strong>Document Type:</strong> ${training.document_type}</p>
                ${training.field_type_accuracy ? `<p><strong>Field Accuracy:</strong> ${(training.field_type_accuracy * 100).toFixed(1)}%</p>` : ''}
                ${training.document_type_accuracy ? `<p><strong>Document Accuracy:</strong> ${(training.document_type_accuracy * 100).toFixed(1)}%</p>` : ''}
                ${training.training_samples ? `<p><strong>Total Training Samples:</strong> ${training.training_samples}</p>` : ''}
                ${training.note ? `<p><strong>Note:</strong> ${training.note}</p>` : ''}
            </div>
        `;

        trainingInfo.innerHTML = resultsHtml;
        trainingStatus.style.display = 'block';
    }

    function showAutomaticTrainingResults(training) {
        // Show a notification about automatic training
        const message = `🤖 Automatic Training: Added ${training.samples_added} samples for ${training.document_type} documents. The system is getting smarter!`;
        addMessage(message, 'bot');
        
        // You can also show a toast notification or modal here
        console.log('Automatic training completed:', training);
    }

    // Training stats removed - not needed for HTML workflow
});

