# Ambiguity Detection Web App

A modern web application that analyzes sentences and highlights ambiguous parts using NLP techniques.

## 🎯 Features

- **Real-time Analysis**: Enter any sentence and get instant ambiguity detection
- **Visual Highlighting**: Ambiguous parts are highlighted with color-coded severity
- **Detailed Explanations**: Click on highlighted words to see ambiguity analysis
- **Multiple Detection Methods**: Combines dependency parsing, CFG parsing, and semantic analysis
- **Ambiguity Types**: Detects lexical, syntactic, and semantic ambiguities
- **Example Sentences**: Pre-loaded examples to test the system
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices

## 🚀 Quick Start

### Installation

1. Install dependencies:
```bash
pip install Flask Flask-CORS numpy
```

2. Run the web app:
```bash
python app.py
```

3. Open your browser to `http://localhost:5000`

### Using the Docker-like Startup Script

```bash
chmod +x run_webapp.sh
./run_webapp.sh
```

## 📂 Project Structure

```
├── app.py                  # Flask backend API
├── templates/
│   └── index.html         # Main web interface
├── static/
│   ├── style.css          # Styling
│   └── script.js          # Frontend logic
├── requirements.txt       # Python dependencies
└── run_webapp.sh         # Startup script
```

## 🔌 API Endpoints

### POST `/api/analyze`
Analyze text for ambiguities.

**Request:**
```json
{
  "text": "I saw the man with the telescope"
}
```

**Response:**
```json
{
  "status": "success",
  "text": "I saw the man with the telescope",
  "ambiguous_tokens": [
    {
      "token": "saw",
      "start": 2,
      "end": 5,
      "ambiguity_score": 0.65,
      "type": "semantic",
      "explanation": "Could mean 'looked at' or 'past tense of see'"
    }
  ],
  "overall_score": 0.65,
  "num_ambiguities": 1
}
```

### GET `/api/examples`
Get example sentences.

**Response:**
```json
{
  "examples": [
    "I saw the man with the telescope",
    "The chicken is ready to eat",
    "They are hunting dogs"
  ]
}
```

### GET `/api/stats`
Get model statistics.

**Response:**
```json
{
  "model_status": "ready",
  "methods_used": ["Dependency parsing", "CFG parsing", "Token analysis"],
  "ambiguity_types": ["Lexical", "Syntactic", "Semantic"]
}
```

## 🎨 UI Components

### Input Section
- Text area for sentence input
- Analyze button to run detection
- Clear button to reset
- Load Example button for quick testing

### Results Display
- **Highlighted Text**: Color-coded highlighting of ambiguous words
- **Ambiguities List**: Detailed list of detected ambiguities
- **Overall Score**: Visual representation of total ambiguity level

### Highlighting Colors
- 🔴 **Red** (High): Severe ambiguity (score ≥ 0.6)
- 🟡 **Yellow** (Medium): Moderate ambiguity (0.3 ≤ score < 0.6)
- 🟢 **Green** (Low): Mild ambiguity (score < 0.3)

## 🔧 Configuration

The Flask app can be configured by modifying `app.py`:

```python
pipeline = AmbiguityDetectionPipeline(
    remove_stopwords=False,           # Remove common words
    use_dependency_parser=True,       # Enable dependency parsing
    use_cfg_parser=True,              # Enable CFG parsing
    use_ml_classifier=False,          # Enable ML classifier
    use_bert=False                    # Enable BERT semantic analysis
)
```

## 📊 Ambiguity Types

- **Lexical Ambiguity**: A word has multiple meanings (homonymy/polysemy)
- **Syntactic Ambiguity**: Multiple valid parse trees for the sentence
- **Semantic Ambiguity**: Phrase or clause can be interpreted multiple ways

## 💡 Example Sentences

1. "I saw the man with the telescope" - Syntactic ambiguity
2. "The chicken is ready to eat" - Syntactic ambiguity  
3. "They are hunting dogs" - Lexical/syntactic ambiguity
4. "The old man the boat" - Syntactic ambiguity
5. "I made her duck" - Semantic ambiguity
6. "Can you pass the bill" - Lexical ambiguity
7. "The teacher gave the students the books" - Syntactic ambiguity

## 🧠 Technical Details

The web app uses the existing ambiguity detection pipeline which combines:

1. **Dependency Parsing**: Analyzes grammatical relationships between words
2. **Context-Free Grammar (CFG)**: Detects syntactic ambiguities
3. **BERT Semantic Analysis** (optional): Uses transformer embeddings for semantic ambiguity
4. **ML Classification** (optional): ML-based ambiguity scoring

## 🌐 Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Android)

## 📝 Notes

- First request may take longer due to model initialization
- BERT mode requires the model to be downloaded (~400MB)
- Results are cached for repeated sentences

## 🐛 Troubleshooting

**Port already in use:**
```bash
python app.py --port 5001
```

**CORS errors:**
Make sure Flask-CORS is installed: `pip install Flask-CORS`

**Module not found errors:**
Ensure you're running from the project root directory

## 📄 License

Same as the parent NLP project

## 👨‍💻 Development

To extend the app:

1. Add new API endpoints in `app.py`
2. Update frontend in `templates/index.html` and `static/script.js`
3. Modify styles in `static/style.css`
4. Test with different ambiguous sentences
