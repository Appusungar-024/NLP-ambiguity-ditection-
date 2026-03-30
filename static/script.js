// Ambiguity Detection Web App - JavaScript

const API_BASE = '/api';

// DOM Elements
const inputText = document.getElementById('input-text');
const analyzeBtn = document.getElementById('analyze-btn');
const clearBtn = document.getElementById('clear-btn');
const exampleBtn = document.getElementById('example-btn');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('results-section');
const errorSection = document.getElementById('error-section');
const highlightedText = document.getElementById('highlighted-text');
const ambiguitiesList = document.getElementById('ambiguities-list');
const noAmbiguities = document.getElementById('no-ambiguities');
const scoreFill = document.getElementById('score-fill');
const scoreValue = document.getElementById('score-value');
const scoreDescription = document.getElementById('score-description');
const errorMessage = document.getElementById('error-message');
const examplesGrid = document.getElementById('examples-grid');
const infoModal = document.getElementById('info-modal');
const modalTitle = document.getElementById('modal-title');
const modalBody = document.getElementById('modal-body');
const modalClose = document.querySelector('.modal-close');

// Event Listeners
analyzeBtn.addEventListener('click', analyzeText);
clearBtn.addEventListener('click', clearAll);
exampleBtn.addEventListener('click', loadRandomExample);
inputText.addEventListener('keypress', (e) => {
    if (e.ctrlKey && e.key === 'Enter') analyzeText();
});
modalClose.addEventListener('click', closeModal);
infoModal.addEventListener('click', (e) => {
    if (e.target === infoModal) closeModal();
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadExamples();
});

/**
 * Analyze the input text for ambiguities
 */
async function analyzeText() {
    const text = inputText.value.trim();

    if (!text) {
        showError('Please enter a sentence to analyze');
        return;
    }

    showLoading(true);
    hideError();
    resultsSection.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'error') {
            showError(data.message);
        } else {
            displayResults(data);
        }
    } catch (error) {
        console.error('Analysis error:', error);
        showError(`Error analyzing text: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

/**
 * Display analysis results
 */
function displayResults(data) {
    const { text, ambiguous_tokens, overall_score, ambiguity_types, explanations, suggestions, bert_analysis } = data;

    // Display highlighted text
    displayHighlightedText(text, ambiguous_tokens);

    // Display ambiguity types
    displayAmbiguityTypes(ambiguity_types);

    // Display ambiguities list
    displayAmbiguitiesList(ambiguous_tokens);

    // Display explanations
    displayExplanations(explanations);

    // Display suggestions
    displaySuggestions(suggestions);

    // Display BERT analysis
    if (bert_analysis) {
        displayBertAnalysis(bert_analysis);
    }

    // Display overall score
    displayScore(overall_score);

    // Show results section
    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Display text with highlighted ambiguous parts
 */
function displayHighlightedText(text, ambiguities) {
    if (!ambiguities || ambiguities.length === 0) {
        highlightedText.innerHTML = `<p>${escapeHtml(text)}</p>`;
        noAmbiguities.classList.remove('hidden');
        ambiguitiesList.classList.add('hidden');
        return;
    }

    noAmbiguities.classList.add('hidden');
    ambiguitiesList.classList.remove('hidden');

    // Sort ambiguities by start position (descending) to avoid index shifts
    const sorted = [...ambiguities].sort((a, b) => b.start - a.start);

    let html = text;
    sorted.forEach((amb) => {
        const token = text.substring(amb.start, amb.end);
        const severity = getAmbiguitySeverity(amb.ambiguity_score);
        const highlighted = `<span class="highlight ${severity}" data-token="${token}" data-score="${amb.ambiguity_score}" data-type="${amb.ambiguity_type}" data-explanation="${escapeHtml(amb.explanation)}">${token}</span>`;
        html = html.substring(0, amb.start) + highlighted + html.substring(amb.end);
    });

    highlightedText.innerHTML = html;

    // Add click handlers to highlights
    document.querySelectorAll('.highlight').forEach((span) => {
        span.addEventListener('click', (e) => {
            e.stopPropagation();
            showAmbiguityDetail(span);
        });
    });
}

/**
 * Display list of ambiguities
 */
function displayAmbiguitiesList(ambiguities) {
    if (!ambiguities || ambiguities.length === 0) {
        ambiguitiesList.innerHTML = '';
        return;
    }

    ambiguitiesList.innerHTML = ambiguities
        .map((amb, idx) => {
            const severity = getAmbiguitySeverity(amb.ambiguity_score);
            return `
                <div class="ambiguity-item ${severity}" onclick="scrollToHighlight('${amb.token}')">
                    <div class="ambiguity-header">
                        <div>
                            <span class="ambiguity-word">"${amb.token}"</span>
                            <span class="ambiguity-type">${capitalize(amb.type)}</span>
                        </div>
                        <div class="ambiguity-score">${amb.ambiguity_score.toFixed(2)}</div>
                    </div>
                    <div class="ambiguity-description">${amb.explanation}</div>
                </div>
            `;
        })
        .join('');
}

/**
 * Display overall ambiguity score
 */
function displayScore(score) {
    const percentage = (score * 100).toFixed(1);
    scoreFill.style.width = `${percentage}%`;
    scoreValue.textContent = score.toFixed(2);

    if (score === 0) {
        scoreDescription.textContent = 'No ambiguities detected - text is clear!';
    } else if (score < 0.3) {
        scoreDescription.textContent = 'Low ambiguity - mostly clear with minor issues';
    } else if (score < 0.6) {
        scoreDescription.textContent = 'Moderate ambiguity - some unclear parts';
    } else if (score < 0.8) {
        scoreDescription.textContent = 'High ambiguity - significant unclear parts';
    } else {
        scoreDescription.textContent = 'Very high ambiguity - severely unclear';
    }
}

/**
 * Display ambiguity types
 */
function displayAmbiguityTypes(types) {
    const typesList = document.getElementById('ambiguity-types-list');
    const typesCard = document.getElementById('types-card');
    
    if (!types || types.length === 0) {
        typesCard.classList.add('hidden');
        return;
    }
    
    typesCard.classList.remove('hidden');
    typesList.innerHTML = types
        .map((type) => `<span class="type-tag">${capitalize(type)}</span>`)
        .join('');
}

/**
 * Display detailed explanations
 */
function displayExplanations(explanations) {
    const explanationsList = document.getElementById('explanations-list');
    const explanationsCard = document.getElementById('explanations-card');
    
    if (!explanations || explanations.length === 0) {
        explanationsCard.classList.add('hidden');
        return;
    }
    
    explanationsCard.classList.remove('hidden');
    explanationsList.innerHTML = explanations
        .map((explanation, idx) => `
            <div class="explanation-item">
                <div class="explanation-label">📌 Point ${idx + 1}:</div>
                <div class="explanation-text">${escapeHtml(explanation)}</div>
            </div>
        `)
        .join('');
}

/**
 * Display suggestions
 */
function displaySuggestions(suggestions) {
    const suggestionsList = document.getElementById('suggestions-list');
    const suggestionsCard = document.getElementById('suggestions-card');
    
    if (!suggestions || suggestions.length === 0) {
        suggestionsCard.classList.add('hidden');
        return;
    }
    
    suggestionsCard.classList.remove('hidden');
    suggestionsList.innerHTML = suggestions
        .map((suggestion, idx) => `
            <div class="suggestion-item">
                <span class="suggestion-number">💡 ${idx + 1}.</span>
                <span class="suggestion-text">${escapeHtml(suggestion)}</span>
            </div>
        `)
        .join('');
}

/**
 * Display BERT semantic analysis
 */
function displayBertAnalysis(bertData) {
    const bertCard = document.getElementById('bert-card');
    const bertAnalysis = document.getElementById('bert-analysis');
    
    if (!bertData) {
        bertCard.classList.add('hidden');
        return;
    }
    
    bertCard.classList.remove('hidden');
    
    const semanticScore = bertData.semantic_ambiguity_score || 0;
    const numInterpretations = bertData.num_interpretations || 0;
    const avgDivergence = bertData.avg_divergence || 0;
    const primaryMeaning = bertData.primary_meaning || 'N/A';
    const alternativeMeanings = bertData.alternative_meanings || [];
    
    let html = `
        <div class="bert-metric">
            <div class="bert-metric-label">Semantic Ambiguity Score</div>
            <div class="bert-metric-value">${semanticScore.toFixed(3)}</div>
            <div class="bert-metric-unit">out of 1.000</div>
        </div>
        
        <div class="bert-metric">
            <div class="bert-metric-label">Number of Interpretations</div>
            <div class="bert-metric-value">${numInterpretations}</div>
            <div class="bert-metric-unit">distinct meanings</div>
        </div>
        
        <div class="bert-metric">
            <div class="bert-metric-label">Average Divergence</div>
            <div class="bert-metric-value">${avgDivergence.toFixed(3)}</div>
            <div class="bert-metric-unit">semantic distance</div>
        </div>
    `;
    
    // Add meanings section if we have them
    if (primaryMeaning || alternativeMeanings.length > 0) {
        html += `
            <div class="bert-meanings">
                <div class="bert-meanings-title">🧠 Semantic Interpretations:</div>
                <div class="bert-meaning-item">
                    <div class="bert-meaning-label">🎯 Primary Meaning:</div>
                    <div class="bert-meaning-text">${escapeHtml(primaryMeaning || 'N/A')}</div>
                </div>
        `;
        
        if (alternativeMeanings && alternativeMeanings.length > 0) {
            alternativeMeanings.forEach((meaning, idx) => {
                html += `
                    <div class="bert-meaning-item">
                        <div class="bert-meaning-label">🔄 Alternative ${idx + 1}:</div>
                        <div class="bert-meaning-text">${escapeHtml(meaning || 'N/A')}</div>
                    </div>
                `;
            });
        }
        
        html += `</div>`;
    }
    
    bertAnalysis.innerHTML = html;
}

/**
 * Get ambiguity severity level
 */
function getAmbiguitySeverity(score) {
    if (score >= 0.6) return 'high';
    if (score >= 0.3) return 'medium';
    return 'low';
}

/**
 * Show ambiguity details in modal
 */
function showAmbiguityDetail(element) {
    const token = element.dataset.token;
    const score = element.dataset.score;
    const type = element.dataset.type;
    const explanation = element.dataset.explanation;

    modalTitle.textContent = `Ambiguity Details: "${token}"`;
    modalBody.innerHTML = `
        <div class="mb-15">
            <strong>Word:</strong> <em>"${token}"</em>
        </div>
        <div class="mb-15">
            <strong>Type:</strong> ${capitalize(type)}
        </div>
        <div class="mb-15">
            <strong>Ambiguity Score:</strong> ${score} / 1.0
        </div>
        <div>
            <strong>Explanation:</strong><br>
            ${explanation}
        </div>
    `;

    infoModal.classList.remove('hidden');
}

/**
 * Close the info modal
 */
function closeModal() {
    infoModal.classList.add('hidden');
}

/**
 * Load and display examples
 */
async function loadExamples() {
    try {
        const response = await fetch(`${API_BASE}/examples`);
        const data = await response.json();
        
        examplesGrid.innerHTML = data.examples
            .map((example) => `
                <button class="example-btn" onclick="setExample('${escapeHtml(example)}')">
                    ${escapeHtml(example)}
                </button>
            `)
            .join('');
    } catch (error) {
        console.error('Error loading examples:', error);
    }
}

/**
 * Load a random example
 */
async function loadRandomExample() {
    try {
        const response = await fetch(`${API_BASE}/examples`);
        const data = await response.json();
        const randomExample = data.examples[Math.floor(Math.random() * data.examples.length)];
        setExample(randomExample);
    } catch (error) {
        console.error('Error loading example:', error);
    }
}

/**
 * Set example in input and analyze
 */
function setExample(example) {
    inputText.value = example;
    inputText.focus();
    setTimeout(analyzeText, 100);
}

/**
 * Scroll to and highlight a specific token
 */
function scrollToHighlight(token) {
    const highlights = document.querySelectorAll('.highlight');
    for (let highlight of highlights) {
        if (highlight.textContent === token) {
            highlight.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            highlight.style.animation = 'none';
            setTimeout(() => {
                highlight.style.animation = 'pulse 0.5s ease-in-out';
            }, 10);
            break;
        }
    }
}

/**
 * Clear all inputs and results
 */
function clearAll() {
    inputText.value = '';
    resultsSection.classList.add('hidden');
    hideError();
    inputText.focus();
}

/**
 * Show loading state
 */
function showLoading(show) {
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorSection.classList.remove('hidden');
    errorSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Hide error message
 */
function hideError() {
    errorSection.classList.add('hidden');
}

/**
 * Utility: Escape HTML special characters
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, (m) => map[m]);
}

/**
 * Utility: Capitalize string
 */
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Add pulse animation
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
`;
document.head.appendChild(style);
