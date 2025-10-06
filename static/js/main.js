document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const chatInput = document.getElementById('chatInput');
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
    const documentId = document.getElementById('documentId')?.value;

    // File upload functionality
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', () => fileInput.click());
        
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
            const response = await fetch(`/api/documents/${documentId}/preview/`);
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

    // Fill all fields functionality
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
                    const response = await fetch(`/api/chat/${documentId}/fill-all/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });

                    const data = await response.json();
                    
                    if (data.success) {
                        // Update all field inputs with the filled data
                        data.filled_fields.forEach(field => {
                            const input = document.querySelector(`input[data-field-id="${field.id}"]`);
                            if (input) {
                                input.value = field.content;
                                // Trigger the update
                                updateField(field.id, field.content);
                            }
                        });
                        
                        addMessage(`Successfully filled ${data.filled_fields.length} fields with AI suggestions!`, 'bot');
                    } else {
                        addMessage('Error filling fields: ' + data.error, 'bot');
                    }
                } catch (error) {
                    console.error('Fill all error:', error);
                    addMessage('Error filling fields: ' + error.message, 'bot');
                } finally {
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
                    const response = await fetch(`/api/documents/${documentId}/regenerate/`, {
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

    // Upload file function
    async function uploadFile(file) {
        // Show loading indicator
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            uploadArea.innerHTML = '<i class="fas fa-spinner fa-spin"></i><br>Processing document...';
        }
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
        
        try {
            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Redirect to main page to view the uploaded document
                window.location.href = '/';
            } else {
                alert('Upload failed: ' + (data.error || 'Unknown error'));
                // Reset upload area
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
            // Reset upload area
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
        
        // Add welcome message if chat is empty
        if (chatMessages && chatMessages.children.length === 0) {
            if (documentId) {
                addMessage("Hello! I can see you have a document loaded. I can help you fill out the form fields. Try asking me about the fields or what information you need to provide!", 'bot');
            } else {
                addMessage("Hello! I'm your AI assistant. Upload a document and I can help you fill it out. Ask me anything!", 'bot');
            }
        }
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

    async function generatePDF() {
        if (!documentId) return;

        generatePdfBtn.disabled = true;
        generatePdfBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating PDF...';

        try {
            const response = await fetch(`/api/documents/${documentId}/generate-pdf/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();
            if (data.success) {
                // Download the PDF
                window.open(`/api/documents/download/${documentId}/`, '_blank');
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
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString();
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);
        
        if (chatMessages) {
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } else {
            console.error('chatMessages element not found!');
        }
    }

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
});

