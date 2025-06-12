document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const dropArea = document.getElementById('dropArea');
    const fileInput = document.getElementById('fileInput');
    const processingContainer = document.getElementById('processingContainer');
    const resultsContainer = document.getElementById('resultsContainer');
    const fileName = document.getElementById('fileName');
    const stageUpload = document.getElementById('stageUpload');
    const stageTranscript = document.getElementById('stageTranscript');
    const stageClustering = document.getElementById('stageClustering');
    const stageSummarizing = document.getElementById('stageSummarizing');
    const transcriptText = document.getElementById('transcriptText');
    const clustersList = document.getElementById('clustersList');
    const summariesList = document.getElementById('summariesList');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Event Listeners
    dropArea.addEventListener('dragover', handleDragOver);
    dropArea.addEventListener('dragleave', handleDragLeave);
    dropArea.addEventListener('drop', handleDrop);
    dropArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);
        });
    });
    
    // Functions
    function handleDragOver(e) {
        e.preventDefault();
        dropArea.classList.add('dragging');
    }
    
    function handleDragLeave(e) {
        e.preventDefault();
        dropArea.classList.remove('dragging');
    }
    
    function handleDrop(e) {
        e.preventDefault();
        dropArea.classList.remove('dragging');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            processFile(files[0]);
        }
    }
    
    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            processFile(file);
        }
    }
    
    function processFile(file) {
        // Check if file is audio
        if (!file.type.startsWith('audio/')) {
            alert('Please upload an audio file (MP3 or WAV)');
            return;
        }
        
        // Show processing container
        dropArea.classList.add('hidden');
        processingContainer.classList.remove('hidden');
        fileName.textContent = `Processing: ${file.name}`;
        
        // Start processing workflow
        transcribeAudio(file)
            .then(transcript => {
                updateStage('stageTranscript', 'completed');
                updateStage('stageClustering', 'active');
                return createClusters(transcript);
            })
            .then(clusters => {
                updateStage('stageClustering', 'completed');
                updateStage('stageSummarizing', 'active');
                return summarizeClusters(clusters);
            })
            .then(summaries => {
                updateStage('stageSummarizing', 'completed');
                showResults();
            })
            .catch(error => {
                console.error('Error in processing workflow:', error);
                alert('An error occurred during processing. Please try again.');
            });
    }
    
    async function transcribeAudio(file) {
        // Create FormData to send the file
        const formData = new FormData();
        formData.append('audio', file);
        
        try {
            // Simulate a loading delay (remove in production)
            await simulateDelay(2000);
            
            // Send the audio file to the backend for transcription
            const response = await fetch('/transcribe', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            const transcript = data.transcript;
            
            // Display transcript in the UI
            transcriptText.innerHTML = `<p>${transcript}</p>`;
            
            return transcript;
        } catch (error) {
            console.error('Error transcribing audio:', error);
            throw error;
        }
    }
    
    async function createClusters(transcript) {
        try {
            // Simulate a loading delay (remove in production)
            await simulateDelay(2000);
            
            // Create a text file from the transcript
            const textBlob = new Blob([transcript], { type: 'text/plain' });
            const textFile = new File([textBlob], 'transcript.txt', { type: 'text/plain' });
            
            // Create FormData to send the file
            const formData = new FormData();
            formData.append('file', textFile);
            
            // Send the transcript to the backend for clustering
            const response = await fetch('/cluster', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const clusters = await response.json();
            
            // Display clusters in the UI
            clustersList.innerHTML = '';
            clusters.forEach((cluster, index) => {
                const clusterElement = document.createElement('div');
                clusterElement.className = 'cluster-item';
                clusterElement.innerHTML = `
                    <h4>Cluster ${index + 1}</h4>
                    <p>${cluster}</p>
                `;
                clustersList.appendChild(clusterElement);
            });
            
            return clusters;
        } catch (error) {
            console.error('Error creating clusters:', error);
            throw error;
        }
    }
    
    async function summarizeClusters(clusters) {
        try {
            // Simulate a loading delay (remove in production)
            await simulateDelay(2000);
            
            // Send the clusters to the backend for summarization
            const response = await fetch('/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(clusters)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            const summaries = data.summaries;
            
            // Display summaries in the UI
            summariesList.innerHTML = '';
            summaries.forEach((summary, index) => {
                const summaryElement = document.createElement('div');
                summaryElement.className = 'summary-item';
                
                // Extract title if format is "Title: Content"
                let title = `Summary ${index + 1}`;
                let content = summary;
                
                const titleMatch = summary.match(/^(.*?):\s*([\s\S]*)$/);
                if (titleMatch) {
                    title = titleMatch[1];
                    content = titleMatch[2];
                }
                
                summaryElement.innerHTML = `
                    <h3>${title}</h3>
                    <p>${content}</p>
                `;
                summariesList.appendChild(summaryElement);
            });
            
            return summaries;
        } catch (error) {
            console.error('Error summarizing clusters:', error);
            throw error;
        }
    }
    
    function updateStage(stageId, status) {
        const stage = document.getElementById(stageId);
        const spinner = stage.querySelector('.spinner');
        
        if (status === 'active') {
            stage.classList.add('active');
            stage.classList.remove('completed');
            if (spinner) spinner.classList.remove('hidden');
        } else if (status === 'completed') {
            stage.classList.remove('active');
            stage.classList.add('completed');
            if (spinner) spinner.classList.add('hidden');
        }
    }
    
    function showResults() {
        // Add a slight delay to complete the animation effect
        setTimeout(() => {
            processingContainer.classList.add('hidden');
            resultsContainer.classList.remove('hidden');
        }, 500);
    }
    
    function switchTab(tabName) {
        // Update tab buttons
        tabButtons.forEach(button => {
            if (button.dataset.tab === tabName) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
        
        // Update tab contents
        tabContents.forEach(content => {
            if (content.id === `${tabName}-content`) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
    }
    
    // Helper function to simulate delay (for demo purposes)
    function simulateDelay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
});
