# 🚀 Ambiguity Detection Web App - Quick Start

Your web application is ready to use! This guide will get you up and running in seconds.

## ⚡ Quick Start (2 minutes)

### Option 1: Simple Command
```bash
python app.py
```

### Option 2: Using the Startup Script
```bash
chmod +x run_webapp.sh
./run_webapp.sh
```

### Option 3: With Custom Port
```bash
python app.py --port 8080
```

Then open your browser to: **http://localhost:5000**

## 📁 What's Included

```
nlp_project/
├── app.py                    # Flask backend (REST API)
├── templates/
│   └── index.html           # Web interface
├── static/
│   ├── style.css            # Styling
│   └── script.js            # Frontend logic
├── requirements.txt         # Python dependencies
├── run_webapp.sh           # Startup script
└── WEBAPP_README.md        # Full documentation
```

## 🎨 Features at a Glance

| Feature | Description |
|---------|-------------|
| **Input Box** | Type or paste any sentence |
| **Analyze Button** | Detect ambiguities with one click |
| **Highlighting** | Color-coded ambiguity visualization |
| **Score Display** | Visual representation of ambiguity level |
| **Details Modal** | Click any highlighted word for explanation |
| **Examples** | Pre-loaded sample sentences |
| **Mobile Ready** | Works on all devices |

## 🎯 How to Use

1. **Open the App**
   - Go to http://localhost:5000

2. **Enter a Sentence**
   - Type in the text area or click "Load Example"
   - Example: "I saw the man with the telescope"

3. **Click Analyze**
   - Wait for analysis (usually < 1 second)

4. **View Results**
   - Red highlights = High ambiguity (severe)
   - Yellow highlights = Medium ambiguity (moderate)
   - Green highlights = Low ambiguity (mild)

5. **Get Details**
   - Click any highlighted word to see explanation
   - Scroll through the ambiguities list below

## 📊 Color Legend

- 🔴 **Red** (High Severity): Score ≥ 0.6 - Definitely ambiguous
- 🟡 **Yellow** (Medium Severity): 0.3 ≤ Score < 0.6 - Somewhat ambiguous
- 🟢 **Green** (Low Severity): Score < 0.3 - Mildly ambiguous

## 🔧 Configuration

Edit `app.py` to enable additional analysis methods:

```python
pipeline = AmbiguityDetectionPipeline(
    remove_stopwords=False,      # Remove common words
    use_dependency_parser=True,  # ✓ Enabled
    use_cfg_parser=True,         # ✓ Enabled
    use_ml_classifier=False,     # Disabled (requires model)
    use_bert=False               # Disabled (requires ~400MB model)
)
```

To enable BERT semantic analysis:
```python
use_bert=True
```
Note: First run will download the BERT model (~400MB)

## 📡 API Endpoints

### Analyze Text
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I saw the man with the telescope"}'
```

**Response:**
```json
{
  "status": "success",
  "text": "I saw the man with the telescope",
  "ambiguous_tokens": [...],
  "overall_score": 0.66,
  "is_ambiguous": true,
  "ambiguity_level": "HIGH"
}
```

### Get Examples
```bash
curl http://localhost:5000/api/examples
```

### Get Stats
```bash
curl http://localhost:5000/api/stats
```

## 🧪 Example Sentences to Try

1. **"I saw the man with the telescope"** - PP attachment ambiguity
2. **"The chicken is ready to eat"** - Syntactic ambiguity
3. **"They are hunting dogs"** - Lexical/syntactic ambiguity
4. **"The old man the boat"** - Complex syntactic structure
5. **"I made her duck"** - Semantic ambiguity
6. **"Can you pass the bill?"** - Lexical ambiguity
7. **"The teacher gave the students the books"** - Syntactic complexity

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Change the port in the command
python app.py --port 8000
```

### Module Not Found
```bash
# Install dependencies
pip install Flask Flask-CORS numpy
```

### CORS Errors
- Ensure Flask-CORS is installed: `pip install Flask-CORS`
- This is pre-configured in app.py

### Slow First Request
- First request initializes the pipeline
- Subsequent requests are much faster
- Consider enabling BERT for better semantic detection (slower but more accurate)

## 📈 Performance

- **Typical Analysis Time**: 200-500ms per sentence
- **With BERT**: 1-3 seconds per sentence
- **Max Sentence Length**: ~1000 characters recommended
- **Concurrent Requests**: Limited only by system resources

## 🔐 Security Notes

- App runs locally (http://localhost)
- No data is sent to external servers
- All processing happens on your machine
- Suitable for sensitive text analysis

## 📚 Ambiguity Types

The system detects:

1. **Lexical Ambiguity** - Words with multiple meanings
   - Example: "bank" (financial vs. river)

2. **Syntactic Ambiguity** - Multiple valid parse trees
   - Example: "I saw the man with the telescope"

3. **Semantic Ambiguity** - Phrase interpretation
   - Example: "I made her duck"

4. **PP Attachment** - Prepositional phrase attachment
   - Example: "I saw the man with the telescope"

## 💡 Tips & Tricks

1. **Batch Analysis**
   - Use the API for multiple sentences
   - Script with Python or your language

2. **Export Results**
   - Right-click highlighted text to copy
   - API returns JSON for integration

3. **Custom Training**
   - Modify `ambiguity_classifier.py` for specific domains
   - Train on domain-specific corpus

4. **Combine Methods**
   - Use multiple detection methods together
   - Higher accuracy with ensemble approach

## 🎓 Learning Resources

- See `ARCHITECTURE_GUIDE.md` for technical details
- Check `BERT_SEMANTIC_GUIDE.md` for BERT configuration
- Review `ML_CLASSIFIER_GUIDE.md` for ML training

## 🤝 Integration

### Python Integration
```python
from ambiguity_pipeline import AmbiguityDetectionPipeline

pipeline = AmbiguityDetectionPipeline()
result, _ = pipeline.process("Your sentence here")
print(f"Ambiguity score: {result.ambiguity_score}")
```

### JavaScript Integration
```javascript
const response = await fetch('/api/analyze', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: 'Your sentence'})
});
const data = await response.json();
```

## ✅ Verification

Test that everything works:

```bash
# 1. Start the app
python app.py

# 2. In another terminal, test the API
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"The chicken is ready to eat"}'

# 3. Visit http://localhost:5000 in your browser
```

## 🎯 Next Steps

1. ✅ Start the app: `python app.py`
2. ✅ Open http://localhost:5000
3. ✅ Try an example sentence
4. ✅ Click on highlighted words for details
5. ✅ Test the examples in the suggestions section

## 📞 Support

For issues or questions:
1. Check the `WEBAPP_README.md` for detailed docs
2. Review error messages in the terminal
3. Ensure Python dependencies are installed
4. Check that port 5000 is available

## 🎉 That's It!

Your ambiguity detection web app is ready to use. Enjoy analyzing text!

---

**Happy analyzing! 🚀**
