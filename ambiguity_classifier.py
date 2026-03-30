"""
Ambiguity Machine Learning Classifier

Trains a classifier to predict ambiguity probability from sentences.
Uses features extracted from the linguistic analysis pipeline.
"""

import os
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
import sys

# Make local modules importable
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from text_preprocessing import TextPreprocessor
from parsing_ambiguity import detect_ambiguity as detect_cfg_ambiguity
from dependency_parser import DependencyParser, AmbiguityAnalyzer
from ambiguity_output import AmbiguityClassifier, OutputFormatter


@dataclass
class TrainingExample:
    """Single training example."""
    sentence: str
    is_ambiguous: bool
    ambiguity_score: float
    features: np.ndarray = None


class FeatureExtractor:
    """Extract numerical features from sentences for ML training."""
    
    def __init__(self):
        """Initialize feature extractor components."""
        self.preprocessor = TextPreprocessor()
        self.dep_parser = DependencyParser()
        self.ambiguity_analyzer = AmbiguityAnalyzer()
        self.classifier = AmbiguityClassifier()
        
    def extract_features(self, sentence: str) -> np.ndarray:
        """
        Extract features from a sentence.
        
        Features (20 total):
        1. Sentence length
        2. Average word length
        3. Number of prepositions
        4. Number of conjunctions
        5. Number of verbs
        6. Number of nouns
        7. Number of pronouns
        8. Lexical diversity (unique words / total words)
        9. POS tag variety (unique tags / total words)
        10. Number of noun phrases
        11. Number of dependency relations
        12. Number of polysemous words
        13. Tree depth (from parse analysis)
        14. Coordination count
        15. Prepositional phrase count
        16. Relative clause count
        17. Verb phrase nesting depth
        18. Number of ambiguity indicators
        19. Sentence complexity (tokens^2 / unique_deps)
        20. Polysemy density (polysemous words / total words)
        
        Returns:
            Feature vector as numpy array
        """
        features = []
        
        try:
            # Preprocess
            tokens = self.preprocessor.tokenize(sentence)
            pos_tags = self.preprocessor.pos_tag(tokens) if tokens else []
            
            # Feature 1: Sentence length
            sentence_length = len(tokens)
            features.append(sentence_length)
            
            # Feature 2: Average word length
            avg_word_length = np.mean([len(word) for word in tokens]) if tokens else 0
            features.append(avg_word_length)
            
            # Features 3-7: POS tag counts
            if pos_tags:
                pos_dict = {}
                for word, tag in pos_tags:
                    pos_dict[tag] = pos_dict.get(tag, 0) + 1
                
                prep_count = pos_dict.get('IN', 0)  # Prepositions
                conj_count = pos_dict.get('CC', 0)  # Conjunctions
                verb_count = sum(pos_dict.get(tag, 0) for tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'])
                noun_count = sum(pos_dict.get(tag, 0) for tag in ['NN', 'NNS', 'NNP', 'NNPS'])
                pron_count = sum(pos_dict.get(tag, 0) for tag in ['PRP', 'PRP$', 'WP', 'WP$'])
            else:
                prep_count = conj_count = verb_count = noun_count = pron_count = 0
            
            features.append(prep_count)      # Feature 3
            features.append(conj_count)      # Feature 4
            features.append(verb_count)      # Feature 5
            features.append(noun_count)      # Feature 6
            features.append(pron_count)      # Feature 7
            
            # Feature 8: Lexical diversity
            unique_words = len(set([w.lower() for w in tokens]))
            lexical_diversity = unique_words / sentence_length if sentence_length > 0 else 0
            features.append(lexical_diversity)
            
            # Feature 9: POS tag variety
            unique_pos = len(set([tag for _, tag in pos_tags])) if pos_tags else 0
            pos_variety = unique_pos / sentence_length if sentence_length > 0 else 0
            features.append(pos_variety)
            
            # Features 10-12: Dependency and semantic features
            try:
                dep_info = self.dep_parser.get_dependencies(sentence)
                noun_phrases = self.dep_parser.get_noun_phrases(sentence)
                dep_count = len(dep_info)
                np_count = len(noun_phrases)
            except:
                dep_count = np_count = 0
            
            features.append(np_count)        # Feature 10: Number of noun phrases
            features.append(dep_count)       # Feature 11: Number of dependencies
            
            # Feature 12: Polysemous word count
            polysemous_words = {
                'bank', 'bark', 'bat', 'bear', 'bow', 'can', 'crane', 'draw', 'lead', 'left',
                'light', 'match', 'mine', 'order', 'plant', 'pound', 'ring', 'saw', 'scale', 'seal',
                'spring', 'tear', 'track', 'wind', 'jam', 'fine', 'bank', 'duck', 'case', 'park'
            }
            polysemy_count = sum(1 for word in tokens if word.lower() in polysemous_words)
            features.append(polysemy_count)
            
            # Features 13-16: Structural features
            # Feature 13: Tree depth approximation (using nesting depth of parens/clauses)
            tree_depth = sentence.count('(') + sentence.count('[')
            features.append(tree_depth)
            
            # Feature 14: Coordination count (and, or, but)
            coord_count = sentence.lower().count(' and ') + sentence.lower().count(' or ') + sentence.lower().count(' but ')
            features.append(coord_count)
            
            # Feature 15: PP count (preposition phrases)
            pp_count = prep_count  # Approximate as number of prepositions
            features.append(pp_count)
            
            # Feature 16: Relative clause count (which, that, who)
            relative_count = (sentence.lower().count(' which ') + 
                            sentence.lower().count(' that ') + 
                            sentence.lower().count(' who '))
            features.append(relative_count)
            
            # Feature 17: Verb phrase nesting (approximated)
            vp_nesting = verb_count - 1 if verb_count > 1 else 0
            features.append(vp_nesting)
            
            # Feature 18: Ambiguity indicators count
            try:
                ambig_info = self.ambiguity_analyzer.analyze_dependency_ambiguity(sentence)
                ambig_indicators = len(ambig_info.get('ambiguity_indicators', []))
            except:
                ambig_indicators = 0
            features.append(ambig_indicators)
            
            # Feature 19: Sentence complexity
            complexity = (sentence_length ** 2 / dep_count) if dep_count > 0 else sentence_length ** 2
            features.append(complexity)
            
            # Feature 20: Polysemy density
            polysemy_density = polysemy_count / sentence_length if sentence_length > 0 else 0
            features.append(polysemy_density)
            
        except Exception as e:
            # Return zero vector if extraction fails
            print(f"Feature extraction error: {e}", file=sys.stderr)
            features = [0.0] * 20
        
        return np.array(features, dtype=np.float32)


class AmbiguityMLClassifier:
    """Machine learning classifier for ambiguity prediction."""
    
    def __init__(self, model_type: str = 'random_forest'):
        """
        Initialize the ML classifier.
        
        Args:
            model_type: 'random_forest' or 'logistic_regression'
        """
        self.model_type = model_type
        self.feature_extractor = FeatureExtractor()
        self.scaler = StandardScaler()
        
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            )
        elif model_type == 'logistic_regression':
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                class_weight='balanced'
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        self.is_trained = False
        self.training_history = {
            'accuracy': None,
            'precision': None,
            'recall': None,
            'f1': None,
            'auc': None,
            'cross_val_scores': None
        }
    
    def train(self, training_data: List[TrainingExample], test_size: float = 0.2, 
              cross_val_folds: int = 5) -> Dict[str, float]:
        """
        Train the classifier on provided data.
        
        Args:
            training_data: List of TrainingExample objects
            test_size: Fraction of data to use for testing
            cross_val_folds: Number of cross-validation folds
            
        Returns:
            Dictionary with performance metrics
        """
        print(f"Training {self.model_type} classifier...")
        
        # Extract features and labels
        X = []
        y = []
        for example in training_data:
            if example.features is None:
                example.features = self.feature_extractor.extract_features(example.sentence)
            X.append(example.features)
            y.append(1 if example.is_ambiguous else 0)
        
        X = np.array(X, dtype=np.float32)
        y = np.array(y, dtype=int)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_pred_proba) if len(np.unique(y_test)) > 1 else 0.5
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, 
                                   cv=cross_val_folds, scoring='f1_weighted')
        
        self.training_history = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1),
            'auc': float(auc),
            'cross_val_scores': cv_scores.tolist(),
            'cross_val_mean': float(cv_scores.mean()),
            'cross_val_std': float(cv_scores.std())
        }
        
        self.is_trained = True
        
        print(f"\nTraining Results:")
        print(f"  Accuracy:  {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  F1 Score:  {f1:.4f}")
        print(f"  AUC:       {auc:.4f}")
        print(f"  CV Mean:   {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        return self.training_history
    
    def predict_proba(self, sentence: str) -> float:
        """
        Predict ambiguity probability for a sentence.
        
        Args:
            sentence: Input sentence
            
        Returns:
            Probability of ambiguity (0.0-1.0)
        """
        if not self.is_trained:
            raise RuntimeError("Classifier must be trained before prediction")
        
        features = self.feature_extractor.extract_features(sentence)
        features_scaled = self.scaler.transform([features])
        proba = self.model.predict_proba(features_scaled)[0, 1]
        
        return float(proba)
    
    def predict(self, sentence: str) -> Tuple[int, float]:
        """
        Predict ambiguity classification and probability.
        
        Args:
            sentence: Input sentence
            
        Returns:
            Tuple of (is_ambiguous: int, probability: float)
        """
        proba = self.predict_proba(sentence)
        is_ambiguous = 1 if proba >= 0.5 else 0
        return is_ambiguous, proba
    
    def predict_batch(self, sentences: List[str]) -> List[Tuple[int, float]]:
        """
        Predict for multiple sentences.
        
        Args:
            sentences: List of sentences
            
        Returns:
            List of (is_ambiguous, probability) tuples
        """
        results = []
        for sentence in sentences:
            results.append(self.predict(sentence))
        return results
    
    def save(self, filepath: str):
        """Save trained model to disk."""
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained classifier")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type,
            'training_history': self.training_history
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load trained model from disk."""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.model_type = model_data['model_type']
        self.training_history = model_data['training_history']
        self.is_trained = True
        
        print(f"Model loaded from {filepath}")
    
    def feature_importance(self) -> List[Tuple[str, float]]:
        """Get feature importance (for Random Forest only)."""
        if self.model_type != 'random_forest':
            raise ValueError("Feature importance only available for Random Forest")
        
        feature_names = [
            'sentence_length', 'avg_word_length', 'prep_count', 'conj_count',
            'verb_count', 'noun_count', 'pron_count', 'lexical_diversity',
            'pos_variety', 'np_count', 'dep_count', 'polysemy_count',
            'tree_depth', 'coord_count', 'pp_count', 'relative_count',
            'vp_nesting', 'ambig_indicators', 'complexity', 'polysemy_density'
        ]
        
        importances = self.model.feature_importances_
        feature_importance_list = sorted(
            zip(feature_names, importances),
            key=lambda x: x[1],
            reverse=True
        )
        
        return feature_importance_list


def create_training_dataset() -> List[TrainingExample]:
    """Create a comprehensive training dataset."""
    training_data = [
        # Clear, unambiguous sentences (0.0-0.2 range)
        TrainingExample("The dog ate the bone.", False, 0.08),
        TrainingExample("She walks to school every day.", False, 0.10),
        TrainingExample("The cat is sleeping on the mat.", False, 0.12),
        TrainingExample("He reads books in the library.", False, 0.09),
        TrainingExample("The sun rises in the east.", False, 0.07),
        TrainingExample("They play football in the park.", False, 0.11),
        TrainingExample("I drink coffee every morning.", False, 0.06),
        TrainingExample("The flower is red.", False, 0.05),
        TrainingExample("She drives a car.", False, 0.08),
        TrainingExample("We go to the beach.", False, 0.10),
        
        # Low ambiguity (0.2-0.4 range)
        TrainingExample("The bank can accept new customers.", True, 0.35),
        TrainingExample("I saw the bird in the window.", True, 0.32),
        TrainingExample("The table has four legs.", True, 0.28),
        TrainingExample("She wore a blue dress.", True, 0.30),
        TrainingExample("The program ran successfully.", True, 0.36),
        TrainingExample("The bat flew at night.", True, 0.38),
        TrainingExample("We can meet tomorrow.", True, 0.33),
        TrainingExample("The line is very long.", True, 0.31),
        TrainingExample("He left the office early.", True, 0.37),
        TrainingExample("The spring weather is nice.", True, 0.34),
        
        # Medium ambiguity (0.4-0.65 range)
        TrainingExample("I saw the man with the binoculars.", True, 0.52),
        TrainingExample("She told me the story yesterday.", True, 0.48),
        TrainingExample("They visited the museum with guides.", True, 0.55),
        TrainingExample("The book was written by the author in the library.", True, 0.58),
        TrainingExample("I watched the movie with my friend.", True, 0.50),
        TrainingExample("He gave the letter to the secretary.", True, 0.46),
        TrainingExample("They saw the film on television.", True, 0.51),
        TrainingExample("She read the article about the politician.", True, 0.49),
        TrainingExample("We discussed the issue in the meeting.", True, 0.54),
        TrainingExample("The teacher explained the problem to the student.", True, 0.47),
        
        # High ambiguity (0.65-1.0 range)
        TrainingExample("I saw the man with the telescope", True, 0.66),
        TrainingExample("I saw the man in the park with the telescope", True, 0.97),
        TrainingExample("The board approved the plan with the executive committee.", True, 0.78),
        TrainingExample("She told the boy the girl left.", True, 0.82),
        TrainingExample("They blamed the senator and the representative.", True, 0.72),
        TrainingExample("The professor told the student the material was difficult.", True, 0.81),
        TrainingExample("I heard the story from the man with the hat and the coat.", True, 0.89),
        TrainingExample("The chicken is ready to eat.", True, 0.75),
        TrainingExample("Walking down the street, the building was on fire.", True, 0.85),
        TrainingExample("The old man and woman sat on the bench.", True, 0.68),
    ]
    
    return training_data


def main():
    """Demo and testing."""
    print("=" * 80)
    print("AMBIGUITY ML CLASSIFIER - TRAINING AND PREDICTION DEMO")
    print("=" * 80)
    
    # Create training dataset
    print("\nCreating training dataset...")
    training_data = create_training_dataset()
    print(f"Training dataset: {len(training_data)} examples")
    
    # Initialize classifier
    print("\nInitializing Random Forest classifier...")
    ml_classifier = AmbiguityMLClassifier(model_type='random_forest')
    
    # Train
    print("\nTraining classifier...")
    metrics = ml_classifier.train(training_data, test_size=0.2)
    
    # Show feature importance
    print("\nTop 10 Most Important Features:")
    for feature_name, importance in ml_classifier.feature_importance()[:10]:
        print(f"  {feature_name:25s}: {importance:.4f}")
    
    # Test predictions
    print("\n" + "=" * 80)
    print("PREDICTIONS ON TEST SENTENCES")
    print("=" * 80)
    
    test_sentences = [
        "The dog ate the bone.",
        "I saw the man with the telescope",
        "The bank can accept new customers.",
        "I saw the man in the park with the telescope",
        "She walked to the store yesterday.",
    ]
    
    for sentence in test_sentences:
        is_ambiguous, proba = ml_classifier.predict(sentence)
        print(f"\nSentence: {sentence}")
        print(f"  Classification: {'AMBIGUOUS' if is_ambiguous else 'CLEAR'}")
        print(f"  Ambiguity Probability: {proba:.4f}")
    
    # Save model
    model_path = str(ROOT / "ambiguity_model.pkl")
    print(f"\nSaving model to {model_path}...")
    ml_classifier.save(model_path)
    
    # Load and test
    print(f"\nLoading model from {model_path}...")
    ml_classifier2 = AmbiguityMLClassifier()
    ml_classifier2.load(model_path)
    
    print("\nVerifying loaded model:")
    test_sent = "I saw the man with the telescope"
    is_ambiguous, proba = ml_classifier2.predict(test_sent)
    print(f"  Test sentence: {test_sent}")
    print(f"  Probability: {proba:.4f}")


if __name__ == '__main__':
    main()
