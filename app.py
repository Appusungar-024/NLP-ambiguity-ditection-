"""
Web App for Ambiguity Detection and Highlighting
Provides REST API endpoints for detecting and highlighting ambiguous parts of text
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json

# Add project root to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from ambiguity_pipeline import AmbiguityDetectionPipeline

# Initialize Flask app
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
CORS(app)

# Initialize ambiguity detection pipeline
# Using multiple methods for better detection
try:
    pipeline = AmbiguityDetectionPipeline(
        remove_stopwords=False,
        use_dependency_parser=True,
        use_cfg_parser=True,
        use_ml_classifier=False,  # Set to True if model available
        use_bert=False  # Set to True if BERT model should be used
    )
    print("✓ Ambiguity pipeline initialized successfully")
except Exception as e:
    print(f"⚠ Pipeline initialization warning: {e}")
    pipeline = None


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze a sentence for ambiguity
    
    Request JSON:
    {
        "text": "sentence to analyze"
    }
    
    Response JSON:
    {
        "text": "original sentence",
        "ambiguous_tokens": [
            {
                "token": "word",
                "start": 0,
                "end": 4,
                "ambiguity_score": 0.75,
                "type": "lexical|syntactic|semantic",
                "explanation": "explanation of ambiguity"
            }
        ],
        "overall_score": 0.65,
        "status": "success|error"
    }
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({
                'status': 'error',
                'message': 'Empty text provided'
            }), 400
        
        if not pipeline:
            return jsonify({
                'status': 'error',
                'message': 'Pipeline not initialized'
            }), 500
        
        # Run the pipeline using the process method
        result, _ = pipeline.process(text, output_format='json')
        
        # Format the response based on the AmbiguityResult structure
        ambiguous_tokens = []
        
        if result and result.is_ambiguous:
            # Get the ambiguous phrases and types
            phrases = result.ambiguous_phrases if hasattr(result, 'ambiguous_phrases') else []
            amb_types = result.ambiguity_types if hasattr(result, 'ambiguity_types') else []
            explanations = result.explanations if hasattr(result, 'explanations') else []
            
            # Map each phrase to a token entry
            for idx, phrase in enumerate(phrases):
                # Find the phrase in the text
                start_pos = text.find(phrase)
                if start_pos != -1:
                    end_pos = start_pos + len(phrase)
                    
                    # Determine type based on ambiguity types
                    amb_type = amb_types[idx] if idx < len(amb_types) else (amb_types[0] if amb_types else 'syntactic')
                    
                    # Get explanation for this specific phrase
                    explanation = explanations[idx] if idx < len(explanations) else (explanations[0] if explanations else 'Ambiguous phrase detected')
                    
                    token_info = {
                        'token': phrase,
                        'start': start_pos,
                        'end': end_pos,
                        'ambiguity_score': round(result.ambiguity_score, 3),
                        'type': amb_type,
                        'explanation': str(explanation)
                    }
                    ambiguous_tokens.append(token_info)
        
        # Extract suggestions and other details
        suggestions = result.suggestions if hasattr(result, 'suggestions') else []
        
        # Get BERT semantic analysis if available
        bert_analysis = None
        if pipeline.use_bert and pipeline.bert_detector:
            try:
                bert_result = pipeline.get_semantic_ambiguity(text)
                if bert_result:
                    bert_analysis = {
                        'semantic_ambiguity_score': bert_result.get('semantic_ambiguity_score', 0),
                        'is_ambiguous': bert_result.get('is_ambiguous', False),
                        'num_interpretations': bert_result.get('num_interpretations', 0),
                        'semantic_uncertainty': bert_result.get('semantic_uncertainty', 0),
                        'avg_divergence': bert_result.get('avg_divergence', 0),
                        'primary_meaning': bert_result.get('primary_meaning', ''),
                        'alternative_meanings': bert_result.get('alternative_meanings', [])
                    }
            except Exception as e:
                print(f"BERT analysis not available: {e}")
        
        response = {
            'status': 'success',
            'text': text,
            'ambiguous_tokens': ambiguous_tokens,
            'overall_score': round(result.ambiguity_score, 3) if result else 0,
            'num_ambiguities': len(ambiguous_tokens),
            'is_ambiguous': result.is_ambiguous if result else False,
            'ambiguity_level': result.ambiguity_level if result else 'NONE',
            'ambiguity_types': amb_types if amb_types else [],
            'explanations': explanations if explanations else [],
            'suggestions': suggestions if suggestions else [],
            'bert_analysis': bert_analysis
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error in analyze endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Get example sentences with known ambiguities"""
    examples = [
        "I saw the man with the telescope",
        "The chicken is ready to eat",
        "They are hunting dogs",
        "The old man the boat",
        "I made her duck",
        "Can you pass the bill",
        "The teacher gave the students the books"
    ]
    return jsonify({'examples': examples})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about the model"""
    return jsonify({
        'model_status': 'ready',
        'methods_used': [
            'Dependency parsing',
            'Context-free grammar parsing',
            'Token analysis'
        ],
        'ambiguity_types': [
            'Lexical',
            'Syntactic',
            'Semantic'
        ]
    })


if __name__ == '__main__':
    print("Starting Ambiguity Detection Web App...")
    print("Visit http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
