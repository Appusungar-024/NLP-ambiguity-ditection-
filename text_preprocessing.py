"""
Text Preprocessing Pipeline

This module provides a comprehensive preprocessing pipeline including:
- Text cleaning and normalization
- Tokenization
- Stopword removal (optional)
- POS tagging
"""

import re
from typing import List, Tuple, Optional
from pathlib import Path
import sys

# Make local modules importable
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag, download
from nltk.tag import PerceptronTagger

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    download('punkt', quiet=True)
except Exception:
    pass

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    download('averaged_perceptron_tagger', quiet=True)
except Exception:
    pass

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    download('stopwords', quiet=True)
except Exception:
    pass

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    download('wordnet', quiet=True)
except Exception:
    pass


class TextPreprocessor:
    """Comprehensive text preprocessing pipeline."""
    
    def __init__(self, remove_stopwords: bool = False, lowercase: bool = True):
        """
        Initialize the text preprocessor.
        
        Args:
            remove_stopwords: Whether to remove stopwords
            lowercase: Whether to convert text to lowercase
        """
        self.remove_stopwords = remove_stopwords
        self.lowercase = lowercase
        
        # Load stopwords
        try:
            self.stopwords = set(stopwords.words('english'))
        except LookupError:
            download('stopwords', quiet=True)
            self.stopwords = set(stopwords.words('english'))
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Convert to lowercase if enabled
        if self.lowercase:
            text = text.lower()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        try:
            tokens = word_tokenize(text)
        except Exception:
            # Fallback to simple split if word_tokenize fails
            import re
            tokens = re.findall(r"\b\w+\b|[^\w\s]", text)
        return tokens
    
    def remove_stopwords_fn(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords from token list.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Filtered token list
        """
        if not self.remove_stopwords:
            return tokens
        
        filtered = [token for token in tokens if token.lower() not in self.stopwords]
        return filtered
    
    def pos_tag(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """
        Perform Part-of-Speech tagging.
        
        Args:
            tokens: List of tokens
            
        Returns:
            List of (token, POS tag) tuples
        """
        tagged = pos_tag(tokens)
        return tagged
    
    def preprocess(self, text: str, 
                   apply_pos_tagging: bool = True,
                   return_tagged: bool = False) -> Tuple[List[str], Optional[List[Tuple[str, str]]]]:
        """
        Run the full preprocessing pipeline.
        
        Args:
            text: Input text
            apply_pos_tagging: Whether to apply POS tagging
            return_tagged: If True, return tagged tokens; otherwise return tokens only
            
        Returns:
            Tuple of (tokens, tagged_tokens) or just tokens depending on return_tagged
        """
        # Step 1: Clean text
        cleaned = self.clean_text(text)
        
        # Step 2: Tokenize
        tokens = self.tokenize(cleaned)
        
        # Step 3: Remove stopwords
        tokens = self.remove_stopwords_fn(tokens)
        
        # Step 4: POS tagging
        if apply_pos_tagging:
            tagged = self.pos_tag(tokens)
            if return_tagged:
                return tokens, tagged
            else:
                return tokens, None
        
        return tokens, None


def preprocess_batch(texts: List[str], 
                     remove_stopwords: bool = False,
                     apply_pos_tagging: bool = True) -> List[Tuple[List[str], Optional[List[Tuple[str, str]]]]]:
    """
    Preprocess a batch of texts.
    
    Args:
        texts: List of input texts
        remove_stopwords: Whether to remove stopwords
        apply_pos_tagging: Whether to apply POS tagging
        
    Returns:
        List of (tokens, tagged_tokens) tuples
    """
    preprocessor = TextPreprocessor(remove_stopwords=remove_stopwords)
    results = []
    
    for text in texts:
        tokens, tagged = preprocessor.preprocess(text, 
                                                  apply_pos_tagging=apply_pos_tagging,
                                                  return_tagged=True)
        results.append((tokens, tagged))
    
    return results


# Example usage and testing
if __name__ == '__main__':
    preprocessor = TextPreprocessor(remove_stopwords=False)
    
    test_texts = [
        "I saw the man with the telescope in the park",
        "She visited the museum with the interesting exhibits",
        "He gave the book to his friend during class"
    ]
    
    print("=" * 80)
    print("TEXT PREPROCESSING PIPELINE DEMO")
    print("=" * 80)
    
    for text in test_texts:
        print(f"\nOriginal: {text}")
        
        tokens, tagged = preprocessor.preprocess(text, apply_pos_tagging=True, return_tagged=True)
        
        print(f"Tokens: {tokens}")
        print(f"POS Tags: {tagged}")
    
    print("\n" + "=" * 80)
    print("WITH STOPWORD REMOVAL")
    print("=" * 80)
    
    preprocessor_no_stop = TextPreprocessor(remove_stopwords=True)
    
    for text in test_texts:
        print(f"\nOriginal: {text}")
        
        tokens, tagged = preprocessor_no_stop.preprocess(text, apply_pos_tagging=True, return_tagged=True)
        
        print(f"Tokens (no stopwords): {tokens}")
        print(f"POS Tags: {tagged}")
