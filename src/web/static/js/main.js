// Main JavaScript for Virtual Camera Server

// Upload video form handler
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const fileInput = document.getElementById('video-file');
            const statusDiv = document.getElementById('upload-status');
            
            if (!fileInput.files[0]) {
                statusDiv.innerHTML = '<div class="flash flash-error">Please select a file</div>';
                return;
            }
            
            formData.append('file', fileInput.files[0]);
            statusDiv.innerHTML = '<div class="flash flash-info">Uploading...</div>';
            
            try {
                const response = await fetch('/api/upload-video', {
                    method: 'POST',
                    body: formData
                });
                
                // Check if response is JSON
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    const text = await response.text();
                    statusDiv.innerHTML = `<div class="flash flash-error">Server error: ${response.status} ${response.statusText}</div>`;
                    console.error('Non-JSON response:', text);
                    return;
                }
                
                const data = await response.json();
                
                if (data.success) {
                    statusDiv.innerHTML = '<div class="flash flash-success">Video uploaded successfully!</div>';
                    fileInput.value = '';
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                } else {
                    statusDiv.innerHTML = `<div class="flash flash-error">Error: ${data.error}</div>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="flash flash-error">Upload failed: ${error.message}</div>`;
                console.error('Upload error:', error);
            }
        });
    }
    
    // Create camera form handler
    const createCameraForm = document.getElementById('create-camera-form');
    if (createCameraForm) {
        createCameraForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(createCameraForm);
            const data = {
                name: formData.get('name'),
                video_ids: Array.from(formData.getAll('video_ids')),
                auth_enabled: formData.get('auth_enabled') === 'on',
                auth_username: formData.get('auth_username') || null,
                auth_password: formData.get('auth_password') || null
            };
            
            try {
                const response = await fetch('/api/create-camera', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Camera created successfully!');
                    location.reload();
                } else {
                    alert(`Error: ${result.error}`);
                }
            } catch (error) {
                alert(`Failed to create camera: ${error.message}`);
            }
        });
    }
});

// Start camera
async function startCamera(cameraId) {
    try {
        const response = await fetch(`/api/start-camera/${cameraId}`, {
            method: 'POST'
        });
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            alert(`Server error: ${response.status} ${response.statusText}`);
            console.error('Non-JSON response:', text);
            return;
        }
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Failed to start camera: ${error.message}`);
        console.error('Start camera error:', error);
    }
}

// Scan for missing videos
async function scanVideos() {
    if (!confirm('This will scan the videos directory and add any videos that are not in the library. Continue?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/scan-videos', {
            method: 'POST'
        });
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            alert(`Server error: ${response.status} ${response.statusText}`);
            console.error('Non-JSON response:', text);
            return;
        }
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Failed to scan videos: ${error.message}`);
        console.error('Scan videos error:', error);
    }
}

// Stop camera
async function stopCamera(cameraId) {
    try {
        const response = await fetch(`/api/stop-camera/${cameraId}`, {
            method: 'POST'
        });
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            alert(`Server error: ${response.status} ${response.statusText}`);
            console.error('Non-JSON response:', text);
            return;
        }
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Failed to stop camera: ${error.message}`);
        console.error('Stop camera error:', error);
    }
}

