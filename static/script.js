// DOM Elements
const form = document.getElementById('analysisForm');
const textInput = document.getElementById('textInput');
const urlInput = document.getElementById('urlInput');
const textArea = document.getElementById('textArea');
const urlField = document.getElementById('urlField');
const charCount = document.getElementById('charCount');
const analyzeBtn = document.getElementById('analyzeBtn');
const btnText = document.getElementById('btnText');
const btnLoader = document.getElementById('btnLoader');
const results = document.getElementById('results');
const successResults = document.getElementById('successResults');
const errorResults = document.getElementById('errorResults');

// Input type switching
document.querySelectorAll('input[name="inputType"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
        if (e.target.value === 'text') {
            textInput.classList.remove('hidden');
            urlInput.classList.add('hidden');
            urlField.removeAttribute('required');
            textArea.setAttribute('required', '');
        } else {
            textInput.classList.add('hidden');
            urlInput.classList.remove('hidden');
            textArea.removeAttribute('required');
            urlField.setAttribute('required', '');
        }
    });
});

// Character counter
textArea.addEventListener('input', (e) => {
    const count = e.target.value.length;
    charCount.textContent = count;
    
    if (count > 9000) {
        charCount.style.color = '#ef4444';
    } else if (count > 7000) {
        charCount.style.color = '#f59e0b';
    } else {
        charCount.style.color = '#666';
    }
});

// Form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const inputType = document.querySelector('input[name="inputType"]:checked').value;
    const inputValue = inputType === 'text' ? textArea.value.trim() : urlField.value.trim();
    
    if (!inputValue) {
        showError('Please enter some text or a URL to analyze.');
        return;
    }
    
    setLoading(true);
    hideResults();
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: inputType,
                input: inputValue
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess(data);
        } else {
            showError(data.error || 'Analysis failed', data.request_id);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Network error. Please check your connection and try again.');
    } finally {
        setLoading(false);
    }
});

function setLoading(loading) {
    if (loading) {
        btnText.classList.add('hidden');
        btnLoader.classList.remove('hidden');
        analyzeBtn.disabled = true;
    } else {
        btnText.classList.remove('hidden');
        btnLoader.classList.add('hidden');
        analyzeBtn.disabled = false;
    }
}

function hideResults() {
    results.classList.add('hidden');
    successResults.classList.remove('hidden');
    errorResults.classList.add('hidden');
}

function showSuccess(data) {
    // Update prominent sentiment
    const sentimentLabel = document.getElementById('sentimentLabel');
    const confidenceScore = document.getElementById('confidenceScore');
    
    sentimentLabel.textContent = data.prominent_sentiment;
    confidenceScore.textContent = (data.confidence * 100).toFixed(1) + '%';
    
    // Apply sentiment styling
    sentimentLabel.className = 'sentiment-value';
    const sentiment = data.prominent_sentiment.toLowerCase();
    
    if (sentiment.includes('positive')) {
        sentimentLabel.classList.add('sentiment-positive');
    } else if (sentiment.includes('negative')) {
        sentimentLabel.classList.add('sentiment-negative');
    } else {
        sentimentLabel.classList.add('sentiment-neutral');
    }
    
    // Update detailed scores
    const scoresContainer = document.getElementById('scoresContainer');
    scoresContainer.innerHTML = '';
    
    Object.entries(data.scores).forEach(([label, score]) => {
        const scoreItem = document.createElement('div');
        scoreItem.className = 'score-item';
        
        const percentage = (score * 100).toFixed(1);
        
        scoreItem.innerHTML = `
            <div class="score-label">${label}</div>
            <div class="score-bar-container">
                <div class="score-bar">
                    <div class="score-fill" style="width: ${percentage}%"></div>
                </div>
                <div class="score-value">${percentage}%</div>
            </div>
        `;
        
        scoresContainer.appendChild(scoreItem);
    });
    
    // Update metadata
    document.getElementById('numChunks').textContent = data.num_chunks;
    document.getElementById('modelName').textContent = data.model.split('/').pop();
    document.getElementById('requestId').textContent = data.request_id;
    
    // Show results with animation
    results.classList.remove('hidden');
    results.classList.add('fade-in');
    
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showError(message, requestId = '') {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorRequestId').textContent = requestId || 'N/A';
    
    successResults.classList.add('hidden');
    errorResults.classList.remove('hidden');
    results.classList.remove('hidden');
    results.classList.add('fade-in');
    
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Sample data button functionality
function loadSampleText() {
    const samples = [
        "I'm feeling incredibly happy and optimistic about the future. Everything seems to be going well.",
        "I've been struggling with anxiety lately and can't seem to shake this feeling of worry.",
        "Today was an okay day, nothing particularly good or bad happened.",
        "I'm so grateful for all the wonderful people in my life. They bring me so much joy!",
        "I feel completely overwhelmed and don't know how to cope with everything."
    ];
    
    const randomSample = samples[Math.floor(Math.random() * samples.length)];
    textArea.value = randomSample;
    charCount.textContent = randomSample.length;
    
    // Switch to text input if not already
    document.querySelector('input[name="inputType"][value="text"]').checked = true;
    textInput.classList.remove('hidden');
    urlInput.classList.add('hidden');
}

// Add sample button
document.addEventListener('DOMContentLoaded', () => {
    const sampleBtn = document.createElement('button');
    sampleBtn.type = 'button';
    sampleBtn.textContent = '🎲 Try Sample Text';
    sampleBtn.className = 'analyze-btn';
    sampleBtn.style.marginBottom = '15px';
    sampleBtn.style.background = '#6b7280';
    sampleBtn.onclick = loadSampleText;
    
    form.insertBefore(sampleBtn, analyzeBtn);
    
    // Initialize character counter
    charCount.textContent = textArea.value.length;
});
