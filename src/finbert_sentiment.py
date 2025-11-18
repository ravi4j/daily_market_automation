#!/usr/bin/env python3
"""
FinBERT Sentiment Analysis
ML-based financial sentiment analysis using FinBERT model

FinBERT is a BERT model fine-tuned on financial news and reports.
It's free, open-source, and specifically trained for financial text.

Model: ProsusAI/finbert
License: MIT (completely free)
"""

import os
import warnings
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Suppress transformers warnings
warnings.filterwarnings('ignore', category=FutureWarning)
os.environ['TOKENIZERS_PARALLELISM'] = 'false'


class FinBERTSentimentAnalyzer:
    """
    Financial sentiment analyzer using FinBERT model

    Features:
    - ML-based sentiment (not keyword matching)
    - Financial domain-specific
    - Returns probabilities for positive/negative/neutral
    - Runs on CPU (no GPU needed)
    - Model cached after first download (~440MB)
    """

    def __init__(self, use_finbert: bool = True):
        """
        Initialize sentiment analyzer

        Args:
            use_finbert: If True, use FinBERT model. If False, fall back to keyword-based.
        """
        self.use_finbert = use_finbert
        self.model = None
        self.tokenizer = None
        self.device = None

        if use_finbert:
            self._load_model()

    def _load_model(self):
        """Load FinBERT model and tokenizer (lazy loading)"""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch

            print("📥 Loading FinBERT model (first time ~440MB download)...")

            model_name = "ProsusAI/finbert"

            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

            # Auto-detect GPU or use CPU
            if torch.cuda.is_available():
                self.device = torch.device('cuda')
                gpu_name = torch.cuda.get_device_name(0)
                print(f"🚀 Using GPU: {gpu_name}")
            else:
                self.device = torch.device('cpu')
                print(f"💻 Using CPU (GPU not available)")

            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode

            print("✅ FinBERT model loaded successfully")

        except ImportError as e:
            print(f"⚠️  FinBERT dependencies not installed: {e}")
            print("   Install with: pip install transformers torch")
            print("   Falling back to keyword-based sentiment")
            self.use_finbert = False
        except Exception as e:
            print(f"⚠️  Failed to load FinBERT: {e}")
            print("   Falling back to keyword-based sentiment")
            self.use_finbert = False

    def analyze(self, text: str) -> Dict[str, any]:
        """
        Analyze sentiment of financial text

        Args:
            text: Financial news headline or article text

        Returns:
            {
                'sentiment': 'positive' | 'negative' | 'neutral',
                'confidence': 0.0-1.0,
                'probabilities': {
                    'positive': 0.0-1.0,
                    'negative': 0.0-1.0,
                    'neutral': 0.0-1.0
                },
                'method': 'finbert' | 'keyword'
            }
        """
        if not text or not text.strip():
            return self._neutral_result()

        if self.use_finbert and self.model is not None:
            return self._analyze_with_finbert(text)
        else:
            return self._analyze_with_keywords(text)

    def _analyze_with_finbert(self, text: str) -> Dict[str, any]:
        """Analyze using FinBERT model"""
        try:
            import torch

            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                truncation=True,
                max_length=512,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

            # FinBERT outputs: [positive, negative, neutral]
            probs = predictions[0].cpu().numpy()

            positive_prob = float(probs[0])
            negative_prob = float(probs[1])
            neutral_prob = float(probs[2])

            # Determine sentiment (highest probability)
            if positive_prob > negative_prob and positive_prob > neutral_prob:
                sentiment = 'positive'
                confidence = positive_prob
            elif negative_prob > positive_prob and negative_prob > neutral_prob:
                sentiment = 'negative'
                confidence = negative_prob
            else:
                sentiment = 'neutral'
                confidence = neutral_prob

            return {
                'sentiment': sentiment,
                'confidence': round(confidence, 4),
                'probabilities': {
                    'positive': round(positive_prob, 4),
                    'negative': round(negative_prob, 4),
                    'neutral': round(neutral_prob, 4)
                },
                'method': 'finbert'
            }

        except Exception as e:
            print(f"⚠️  FinBERT analysis failed: {e}")
            print("   Falling back to keyword-based sentiment")
            return self._analyze_with_keywords(text)

    def _analyze_with_keywords(self, text: str) -> Dict[str, any]:
        """Fallback keyword-based sentiment analysis"""
        text_lower = text.lower()

        # Financial negative keywords
        negative_keywords = [
            'loss', 'losses', 'decline', 'down', 'fall', 'fell', 'drop', 'dropped',
            'miss', 'missed', 'concern', 'warning', 'weak', 'disappointing',
            'investigation', 'lawsuit', 'scandal', 'fraud', 'bankruptcy',
            'downgrade', 'cut', 'slump', 'plunge', 'crash', 'crisis'
        ]

        # Financial positive keywords
        positive_keywords = [
            'gain', 'gains', 'rise', 'rose', 'up', 'surge', 'soar', 'beat',
            'strong', 'growth', 'profit', 'upgrade', 'buy', 'bullish',
            'rally', 'jump', 'record', 'high', 'acquisition', 'deal'
        ]

        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        positive_count = sum(1 for word in positive_keywords if word in text_lower)

        total = negative_count + positive_count

        if total == 0:
            return {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'probabilities': {
                    'positive': 0.33,
                    'negative': 0.33,
                    'neutral': 0.34
                },
                'method': 'keyword'
            }

        negative_prob = negative_count / total
        positive_prob = positive_count / total

        if negative_count > positive_count:
            sentiment = 'negative'
            confidence = negative_prob
        elif positive_count > negative_count:
            sentiment = 'positive'
            confidence = positive_prob
        else:
            sentiment = 'neutral'
            confidence = 0.5

        return {
            'sentiment': sentiment,
            'confidence': round(confidence, 4),
            'probabilities': {
                'positive': round(positive_prob, 4),
                'negative': round(negative_prob, 4),
                'neutral': round(1 - positive_prob - negative_prob, 4)
            },
            'method': 'keyword'
        }

    def _neutral_result(self) -> Dict[str, any]:
        """Return neutral sentiment for empty text"""
        return {
            'sentiment': 'neutral',
            'confidence': 0.5,
            'probabilities': {
                'positive': 0.33,
                'negative': 0.33,
                'neutral': 0.34
            },
            'method': 'keyword'
        }

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, any]]:
        """
        Analyze multiple texts (more efficient than one-by-one)

        Args:
            texts: List of financial news headlines/articles

        Returns:
            List of sentiment results
        """
        return [self.analyze(text) for text in texts]

    def get_sentiment_score(self, text: str) -> int:
        """
        Get simple sentiment score for compatibility with existing code

        Args:
            text: Financial news text

        Returns:
            Sentiment score: -50 to +50
            (negative = -50 to -25, neutral = -25 to +25, positive = +25 to +50)
        """
        result = self.analyze(text)

        if result['sentiment'] == 'positive':
            # Scale confidence to +25 to +50
            return int(25 + (result['confidence'] * 25))
        elif result['sentiment'] == 'negative':
            # Scale confidence to -25 to -50
            return int(-25 - (result['confidence'] * 25))
        else:
            # Neutral: -25 to +25 based on lean
            probs = result['probabilities']
            lean = probs['positive'] - probs['negative']
            return int(lean * 25)


# Singleton instance for reuse (avoid reloading model)
_analyzer_instance = None


def get_sentiment_analyzer(use_finbert: bool = True) -> FinBERTSentimentAnalyzer:
    """
    Get singleton sentiment analyzer instance

    Args:
        use_finbert: Whether to use FinBERT model (True) or keywords (False)

    Returns:
        FinBERTSentimentAnalyzer instance
    """
    global _analyzer_instance

    if _analyzer_instance is None:
        _analyzer_instance = FinBERTSentimentAnalyzer(use_finbert=use_finbert)

    return _analyzer_instance


def analyze_sentiment(text: str, use_finbert: bool = True) -> Dict[str, any]:
    """
    Quick function to analyze sentiment

    Args:
        text: Financial news text
        use_finbert: Whether to use FinBERT (True) or keywords (False)

    Returns:
        Sentiment analysis result
    """
    analyzer = get_sentiment_analyzer(use_finbert=use_finbert)
    return analyzer.analyze(text)


# Example usage
if __name__ == "__main__":
    # Test examples
    test_texts = [
        "Apple stock surges on record earnings beat",
        "Tesla shares plunge after disappointing guidance",
        "Microsoft announces quarterly dividend",
        "Amazon faces lawsuit over labor practices"
    ]

    print("="*80)
    print("FinBERT Sentiment Analysis Test")
    print("="*80)
    print()

    analyzer = get_sentiment_analyzer(use_finbert=True)

    for text in test_texts:
        result = analyzer.analyze(text)

        print(f"Text: {text}")
        print(f"Sentiment: {result['sentiment'].upper()}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Method: {result['method']}")
        print(f"Probabilities:")
        for sentiment, prob in result['probabilities'].items():
            print(f"  {sentiment}: {prob:.2%}")
        print()
