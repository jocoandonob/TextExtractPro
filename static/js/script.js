document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    const imagePreview = document.getElementById('image-preview');
    const resultContainer = document.getElementById('result-container');
    const processingSpinner = document.querySelector('.processing-spinner');
    const ocrText = document.getElementById('ocr-text');
    const errorAlert = document.getElementById('error-alert');
    const errorMessage = document.getElementById('error-message');
    const fileNameDisplay = document.getElementById('file-name');
    const fileSizeDisplay = document.getElementById('file-size');
    const processingTimeDisplay = document.getElementById('processing-time');
    const copyButton = document.getElementById('copy-button');
    const cleanTextButton = document.getElementById('clean-text-button');
    const preprocessingTypeSelect = document.getElementById('preprocessing-type');
    const languageSelect = document.getElementById('ocr-language');
    const preprocessingInfo = document.getElementById('preprocessing-info');
    const autoDetectButton = document.getElementById('auto-detect-language');
    const autoDetectCheckbox = document.getElementById('auto-detect-checkbox');
    const visitorCount = document.getElementById('visitor-count');
    const conversionCount = document.getElementById('conversion-count');
    const conversionRate = document.getElementById('conversion-rate');

    // Supported file types
    const supportedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff'];

    // Function to handle file selection
    function handleFileSelect(file) {
        // Validate file existence and type
        if (!file) {
            showError('No file selected. Please choose an image file.');
            return;
        }
        
        if (!supportedTypes.includes(file.type)) {
            showError('Unsupported file type. Please upload a JPG, PNG, GIF, BMP, or TIFF image.');
            return;
        }

        // Create a new DataTransfer object and add the file
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;
        
        // Reset UI and hide any previous errors
        hideError();
        
        // Show file preview
        const reader = new FileReader();
        reader.onload = function(e) {
            if (imagePreview) {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
            }
        };
        reader.onerror = function() {
            showError('Error reading file. Please try another image.');
        };
        reader.readAsDataURL(file);
        
        // Upload the file for OCR processing
        uploadFile(file);
    }

    // Function to upload the file and process OCR
    function uploadFile(file) {
        if (!file) {
            showError('No file selected for upload.');
            return;
        }
        
        // Create form data for upload
        const formData = new FormData();
        formData.append('file', file);
        
        // Get selected preprocessing type (with fallback to default)
        const preprocessType = preprocessingTypeSelect ? preprocessingTypeSelect.value : 'default';
        formData.append('preprocess_type', preprocessType);
        formData.append('auto_detect_language', 'false');
        
        // Get selected language (with fallback to English)
        const language = languageSelect ? languageSelect.value : 'eng';
        formData.append('language', language);
        
        // Show loading state
        if (processingSpinner) processingSpinner.style.display = 'block';
        if (resultContainer) resultContainer.style.display = 'none';
        
        console.log(`Uploading file: ${file.name}, size: ${formatFileSize(file.size)}, type: ${preprocessType}, language: ${language}`);
        
        // Send request to server
        fetch('/upload/', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                // Try to get error details from response
                return response.json()
                    .then(data => {
                        throw new Error(data.detail || `Server error: ${response.status}`);
                    })
                    .catch(e => {
                        // If we can't parse JSON, use status text
                        throw new Error(`Error processing image (${response.status}: ${response.statusText})`);
                    });
            }
            return response.json();
        })
        .then(data => {
            console.log('OCR processing successful', data);
            
            // Check if we have valid data
            if (!data) {
                throw new Error('No data received from server');
            }
            
            // Display the results
            if (ocrText) {
                const extractedText = data.text || 'No text was detected in the image.';
                
                // Apply highlighting to the extracted text
                ocrText.innerHTML = highlightText(extractedText);
                
                // Log text length for debugging
                console.log(`Extracted ${extractedText.length} characters of text`);
            }
            
            // Update file information
            if (fileNameDisplay) fileNameDisplay.textContent = data.filename || file.name;
            if (fileSizeDisplay) fileSizeDisplay.textContent = formatFileSize(data.size || file.size);
            if (processingTimeDisplay) processingTimeDisplay.textContent = `${data.processing_time || '?'} seconds`;
            
            // Update preprocessing and language info
            let infoText = `Preprocessing: ${data.preprocessing_type || preprocessType}`;
            if (data.language) {
                infoText += ` | Language: ${data.language}`;
            }
            if (preprocessingInfo) preprocessingInfo.textContent = infoText;
            
            // Show result container
            if (resultContainer) resultContainer.style.display = 'block';
        })
        .catch(error => {
            console.error('OCR processing error:', error);
            showError(error.message || 'Unknown error occurred during processing');
        })
        .finally(() => {
            // Hide loading spinner
            if (processingSpinner) processingSpinner.style.display = 'none';
        });
    }

    // Function to show error message
    function showError(message) {
        errorMessage.textContent = message;
        errorAlert.style.display = 'block';
    }

    // Function to hide error message
    function hideError() {
        errorAlert.style.display = 'none';
    }
    
    // Function to highlight the extracted text
    function highlightText(text) {
        if (!text) return '';
        
        // Create highlighted content by wrapping text in spans
        const lines = text.split('\n');
        const highlightedLines = lines.map(line => {
            if (line.trim() === '') return line;
            
            // Add highlight class to each line
            return `<span class="highlight-text">${line}</span>`;
        });
        
        return highlightedLines.join('\n');
    }
    
    // Function to clean up the extracted text
    function cleanText() {
        const currentText = ocrText.textContent || '';
        if (!currentText.trim()) {
            showError('No text to clean');
            return;
        }
        
        // Show loading state
        cleanTextButton.disabled = true;
        cleanTextButton.innerHTML = '<i class="bi bi-hourglass-split"></i> Cleaning...';
        
        // Create form data
        const formData = new FormData();
        formData.append('text', currentText);
        formData.append('fix_layout', 'true');
        
        // Send request to clean text API
        fetch('/api/clean-text/', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Update the text with cleaned and highlighted version
                ocrText.innerHTML = highlightText(data.cleaned_text);
                console.log('Text cleaned successfully');
            } else {
                throw new Error(data.error || 'Unknown error cleaning text');
            }
        })
        .catch(error => {
            console.error('Error cleaning text:', error);
            showError(error.message || 'Failed to clean text');
        })
        .finally(() => {
            // Reset button state
            cleanTextButton.disabled = false;
            cleanTextButton.innerHTML = '<i class="bi bi-magic"></i> Clean Text';
        });
    }

    // Function to format file size
    function formatFileSize(bytes) {
        if (bytes < 1024) {
            return bytes + ' bytes';
        } else if (bytes < 1048576) {
            return (bytes / 1024).toFixed(2) + ' KB';
        } else {
            return (bytes / 1048576).toFixed(2) + ' MB';
        }
    }

    // Function to detect language from an image
    function detectLanguage(file) {
        if (!file) {
            showError('No file selected for language detection.');
            return;
        }
        
        // Show loading state on the detect button
        autoDetectButton.disabled = true;
        autoDetectButton.innerHTML = '<i class="bi bi-hourglass-split"></i>';
        
        // Create form data for upload
        const formData = new FormData();
        formData.append('file', file);
        
        // Send request to language detection API
        fetch('/api/detect-language/', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Update the language dropdown with detected language
                languageSelect.value = data.language;
                console.log(`Language detected: ${data.language}`);
                
                // Show success feedback
                autoDetectButton.classList.remove('btn-outline-secondary');
                autoDetectButton.classList.add('btn-success');
                autoDetectButton.innerHTML = '<i class="bi bi-check"></i>';
                
                setTimeout(() => {
                    autoDetectButton.classList.remove('btn-success');
                    autoDetectButton.classList.add('btn-outline-secondary');
                    autoDetectButton.innerHTML = '<i class="bi bi-magic"></i>';
                }, 2000);
            } else {
                throw new Error(data.error || 'Failed to detect language');
            }
        })
        .catch(error => {
            console.error('Error detecting language:', error);
            autoDetectButton.classList.remove('btn-outline-secondary');
            autoDetectButton.classList.add('btn-danger');
            autoDetectButton.innerHTML = '<i class="bi bi-x"></i>';
            
            setTimeout(() => {
                autoDetectButton.classList.remove('btn-danger');
                autoDetectButton.classList.add('btn-outline-secondary');
                autoDetectButton.innerHTML = '<i class="bi bi-magic"></i>';
            }, 2000);
        })
        .finally(() => {
            // Reset button state
            autoDetectButton.disabled = false;
        });
    }
    
    // Function to update the statistics from API
    function refreshStatistics() {
        fetch('/api/statistics/')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.statistics) {
                    const stats = data.statistics;
                    if (visitorCount) visitorCount.textContent = stats.visitor_count || 0;
                    if (conversionCount) conversionCount.textContent = stats.conversion_count || 0;
                    if (conversionRate) conversionRate.textContent = `${stats.conversion_rate || 0}%`;
                }
            })
            .catch(error => {
                console.error('Error fetching statistics:', error);
            });
    }

    // Event listeners
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (fileInput.files.length > 0) {
            handleFileSelect(fileInput.files[0]);
        }
    });

    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            // Don't process on change anymore, just preview the image
            const reader = new FileReader();
            reader.onload = function(e) {
                if (imagePreview) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                }
            };
            reader.readAsDataURL(this.files[0]);
            
            // Enable auto-detect button if we have an image
            if (autoDetectButton) {
                autoDetectButton.disabled = false;
            }
        }
    });

    // Drag and drop functionality
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', function() {
        this.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('drag-over');
        
        if (e.dataTransfer.files.length > 0) {
            // Just preview the image, don't process it yet
            const file = e.dataTransfer.files[0];
            const reader = new FileReader();
            reader.onload = function(e) {
                if (imagePreview) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                }
            };
            reader.readAsDataURL(file);
            
            // Set the file input value
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            
            // Enable auto-detect button
            if (autoDetectButton) {
                autoDetectButton.disabled = false;
            }
        }
    });

    dropZone.addEventListener('click', function() {
        fileInput.click();
    });
    
    // Auto-detect button click handler
    if (autoDetectButton) {
        autoDetectButton.addEventListener('click', function(e) {
            e.preventDefault();
            if (fileInput.files.length > 0) {
                detectLanguage(fileInput.files[0]);
            } else {
                showError('Please select an image file first.');
            }
        });
    }
    
    // Auto-detect checkbox change handler
    if (autoDetectCheckbox) {
        autoDetectCheckbox.addEventListener('change', function() {
            if (this.checked) {
                // Disable the language select when auto-detect is enabled
                if (languageSelect) languageSelect.disabled = true;
            } else {
                // Enable the language select when auto-detect is disabled
                if (languageSelect) languageSelect.disabled = false;
            }
        });
    }

    // Copy text button
    copyButton.addEventListener('click', function() {
        const textToCopy = ocrText.textContent;
        
        navigator.clipboard.writeText(textToCopy).then(function() {
            // Change button text temporarily
            const originalText = copyButton.innerHTML;
            copyButton.innerHTML = '<i class="bi bi-check"></i> Copied!';
            
            setTimeout(function() {
                copyButton.innerHTML = originalText;
            }, 2000);
        }).catch(function(err) {
            console.error('Could not copy text: ', err);
        });
    });
    
    // Clean text button
    cleanTextButton.addEventListener('click', function() {
        cleanText();
    });

    // Fetch preprocessing types from API
    fetch('/api/preprocessing-types/')
        .then(response => response.json())
        .then(data => {
            // Populate preprocessing type select
            preprocessingTypeSelect.innerHTML = '';
            data.preprocessing_types.forEach(type => {
                const option = document.createElement('option');
                option.value = type.id;
                option.textContent = type.name;
                preprocessingTypeSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching preprocessing types:', error);
        });
        
    // Fetch available languages from API
    fetch('/api/languages/')
        .then(response => response.json())
        .then(data => {
            // Populate language select
            languageSelect.innerHTML = '';
            data.languages.forEach(lang => {
                const option = document.createElement('option');
                option.value = lang.id;
                option.textContent = lang.name;
                languageSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching languages:', error);
        });
        
    // Initial statistics load
    refreshStatistics();
    
    // Refresh statistics every 2 minutes
    setInterval(refreshStatistics, 120000);
});
