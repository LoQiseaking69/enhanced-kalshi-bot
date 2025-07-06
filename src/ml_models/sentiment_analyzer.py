"""
Advanced Sentiment Analysis for Kalshi Trading Bot

This module provides sophisticated sentiment analysis using multiple approaches:
- Pre-trained transformer models (BERT, RoBERTa)
- Financial-specific sentiment models
- Multi-source sentiment aggregation
- Real-time sentiment scoring
"""

import logging
import re
import pickle
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timezone
import numpy as np
import pandas as pd

# NLP Libraries
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Machine Learning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Deep Learning
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    pipeline, BertTokenizer, BertForSequenceClassification
)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

logger = logging.getLogger(__name__)

class AdvancedSentimentAnalyzer:
    """
    Advanced sentiment analyzer combining multiple approaches for robust
    sentiment analysis of financial and political news.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Financial sentiment keywords
        self.positive_keywords = {
            'financial': ['profit', 'gain', 'growth', 'increase', 'rise', 'bull', 'positive', 'strong', 'good', 'excellent'],
            'political': ['victory', 'win', 'lead', 'ahead', 'support', 'popular', 'favorable', 'success', 'triumph'],
            'general': ['optimistic', 'confident', 'promising', 'bright', 'encouraging', 'upbeat', 'positive']
        }
        
        self.negative_keywords = {
            'financial': ['loss', 'decline', 'fall', 'drop', 'bear', 'negative', 'weak', 'poor', 'terrible'],
            'political': ['defeat', 'lose', 'behind', 'trail', 'scandal', 'controversy', 'unpopular', 'failure'],
            'general': ['pessimistic', 'worried', 'concerning', 'dark', 'discouraging', 'negative', 'bad']
        }
        
        # Initialize models
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize all sentiment analysis models"""
        try:
            # Initialize FinBERT for financial sentiment
            self.finbert_tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
            self.finbert_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
            self.finbert_pipeline = pipeline(
                "sentiment-analysis",
                model=self.finbert_model,
                tokenizer=self.finbert_tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            self.logger.info("FinBERT model loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to load FinBERT model: {e}")
            self.finbert_pipeline = None
            
        try:
            # Initialize RoBERTa for general sentiment
            self.roberta_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
            self.logger.info("RoBERTa model loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to load RoBERTa model: {e}")
            self.roberta_pipeline = None
            
        # Initialize custom model if available
        self.custom_model = None
        self.custom_vectorizer = None
        if self.model_path:
            self._load_custom_model()
            
    def _load_custom_model(self):
        """Load custom trained sentiment model"""
        try:
            with open(f"{self.model_path}/sentiment_model.pkl", 'rb') as f:
                self.custom_model = pickle.load(f)
            with open(f"{self.model_path}/vectorizer.pkl", 'rb') as f:
                self.custom_vectorizer = pickle.load(f)
            self.logger.info("Custom sentiment model loaded successfully")
        except Exception as e:
            self.logger.warning(f"Failed to load custom model: {e}")
            
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words and len(token) > 2
        ]
        
        return ' '.join(tokens)
        
    def keyword_sentiment(self, text: str, category: str = 'general') -> Dict[str, float]:
        """Calculate sentiment based on keyword matching"""
        text_lower = text.lower()
        
        positive_count = sum(
            text_lower.count(keyword)
            for keyword_list in self.positive_keywords.values()
            for keyword in keyword_list
        )
        
        negative_count = sum(
            text_lower.count(keyword)
            for keyword_list in self.negative_keywords.values()
            for keyword in keyword_list
        )
        
        total_count = positive_count + negative_count
        
        if total_count == 0:
            return {'positive': 0.5, 'negative': 0.5, 'confidence': 0.0}
            
        positive_score = positive_count / total_count
        negative_score = negative_count / total_count
        confidence = min(total_count / 10, 1.0)  # Normalize confidence
        
        return {
            'positive': positive_score,
            'negative': negative_score,
            'confidence': confidence
        }
        
    def vader_sentiment(self, text: str) -> Dict[str, float]:
        """Calculate sentiment using VADER"""
        scores = self.vader_analyzer.polarity_scores(text)
        
        return {
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'compound': scores['compound'],
            'confidence': abs(scores['compound'])
        }
        
    def textblob_sentiment(self, text: str) -> Dict[str, float]:
        """Calculate sentiment using TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Convert polarity to positive/negative scores
        if polarity > 0:
            positive = polarity
            negative = 0
        else:
            positive = 0
            negative = abs(polarity)
            
        return {
            'positive': positive,
            'negative': negative,
            'polarity': polarity,
            'subjectivity': subjectivity,
            'confidence': abs(polarity)
        }
        
    def finbert_sentiment(self, text: str) -> Dict[str, float]:
        """Calculate sentiment using FinBERT"""
        if not self.finbert_pipeline:
            return {'positive': 0.5, 'negative': 0.5, 'confidence': 0.0}
            
        try:
            # Truncate text if too long
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]
                
            result = self.finbert_pipeline(text)[0]
            label = result['label'].lower()
            score = result['score']
            
            if label == 'positive':
                return {'positive': score, 'negative': 1-score, 'confidence': score}
            elif label == 'negative':
                return {'positive': 1-score, 'negative': score, 'confidence': score}
            else:  # neutral
                return {'positive': 0.5, 'negative': 0.5, 'confidence': 1-score}
                
        except Exception as e:
            self.logger.error(f"FinBERT sentiment analysis error: {e}")
            return {'positive': 0.5, 'negative': 0.5, 'confidence': 0.0}
            
    def roberta_sentiment(self, text: str) -> Dict[str, float]:
        """Calculate sentiment using RoBERTa"""
        if not self.roberta_pipeline:
            return {'positive': 0.5, 'negative': 0.5, 'confidence': 0.0}
            
        try:
            # Truncate text if too long
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]
                
            result = self.roberta_pipeline(text)[0]
            label = result['label'].lower()
            score = result['score']
            
            if 'positive' in label:
                return {'positive': score, 'negative': 1-score, 'confidence': score}
            elif 'negative' in label:
                return {'positive': 1-score, 'negative': score, 'confidence': score}
            else:  # neutral
                return {'positive': 0.5, 'negative': 0.5, 'confidence': 1-score}
                
        except Exception as e:
            self.logger.error(f"RoBERTa sentiment analysis error: {e}")
            return {'positive': 0.5, 'negative': 0.5, 'confidence': 0.0}
            
    def custom_model_sentiment(self, text: str) -> Dict[str, float]:
        """Calculate sentiment using custom trained model"""
        if not self.custom_model or not self.custom_vectorizer:
            return {'positive': 0.5, 'negative': 0.5, 'confidence': 0.0}
            
        try:
            processed_text = self.preprocess_text(text)
            features = self.custom_vectorizer.transform([processed_text])
            
            # Get prediction probabilities
            probabilities = self.custom_model.predict_proba(features)[0]
            
            # Assuming binary classification (negative=0, positive=1)
            if len(probabilities) == 2:
                negative_score = probabilities[0]
                positive_score = probabilities[1]
            else:
                # Multi-class classification
                negative_score = probabilities[0] if len(probabilities) > 0 else 0.5
                positive_score = probabilities[-1] if len(probabilities) > 1 else 0.5
                
            confidence = max(positive_score, negative_score)
            
            return {
                'positive': positive_score,
                'negative': negative_score,
                'confidence': confidence
            }
            
        except Exception as e:
            self.logger.error(f"Custom model sentiment analysis error: {e}")
            return {'positive': 0.5, 'negative': 0.5, 'confidence': 0.0}
            
    def ensemble_sentiment(self, text: str, weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Calculate ensemble sentiment using multiple models with weighted averaging
        """
        if not weights:
            weights = {
                'keyword': 0.15,
                'vader': 0.15,
                'textblob': 0.15,
                'finbert': 0.25,
                'roberta': 0.20,
                'custom': 0.10
            }
            
        # Get sentiment from all models
        results = {
            'keyword': self.keyword_sentiment(text),
            'vader': self.vader_sentiment(text),
            'textblob': self.textblob_sentiment(text),
            'finbert': self.finbert_sentiment(text),
            'roberta': self.roberta_sentiment(text),
            'custom': self.custom_model_sentiment(text)
        }
        
        # Calculate weighted averages
        weighted_positive = 0
        weighted_negative = 0
        weighted_confidence = 0
        total_weight = 0
        
        for model_name, result in results.items():
            weight = weights.get(model_name, 0)
            if weight > 0 and result.get('confidence', 0) > 0:
                weighted_positive += result['positive'] * weight * result['confidence']
                weighted_negative += result['negative'] * weight * result['confidence']
                weighted_confidence += result['confidence'] * weight
                total_weight += weight * result['confidence']
                
        if total_weight > 0:
            final_positive = weighted_positive / total_weight
            final_negative = weighted_negative / total_weight
            final_confidence = weighted_confidence / sum(weights.values())
        else:
            final_positive = 0.5
            final_negative = 0.5
            final_confidence = 0.0
            
        # Calculate final sentiment score (-1 to 1)
        sentiment_score = final_positive - final_negative
        
        return {
            'sentiment_score': sentiment_score,
            'positive_probability': final_positive,
            'negative_probability': final_negative,
            'confidence': final_confidence,
            'individual_results': results,
            'text_length': len(text),
            'processed_at': datetime.now(timezone.utc).isoformat()
        }
        
    def analyze_batch(self, texts: List[str], weights: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """Analyze sentiment for a batch of texts"""
        results = []
        for text in texts:
            try:
                result = self.ensemble_sentiment(text, weights)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error analyzing text: {e}")
                results.append({
                    'sentiment_score': 0.0,
                    'positive_probability': 0.5,
                    'negative_probability': 0.5,
                    'confidence': 0.0,
                    'error': str(e)
                })
        return results
        
    def analyze_article(self, title: str, content: str, source: str = None) -> Dict[str, Any]:
        """
        Analyze sentiment of a news article considering both title and content
        """
        # Combine title and content with title weighted more heavily
        combined_text = f"{title} {title} {content}"  # Title appears twice for emphasis
        
        # Get ensemble sentiment
        sentiment_result = self.ensemble_sentiment(combined_text)
        
        # Add article-specific metadata
        sentiment_result.update({
            'title': title,
            'source': source,
            'content_length': len(content),
            'title_sentiment': self.ensemble_sentiment(title),
            'content_sentiment': self.ensemble_sentiment(content) if content else None
        })
        
        return sentiment_result
        
    def get_market_sentiment(self, articles: List[Dict[str, Any]], market_keywords: List[str]) -> Dict[str, Any]:
        """
        Calculate overall market sentiment from multiple articles
        """
        relevant_articles = []
        
        # Filter articles by relevance to market keywords
        for article in articles:
            text = f"{article.get('title', '')} {article.get('content', '')}".lower()
            relevance_score = sum(
                text.count(keyword.lower()) for keyword in market_keywords
            ) / len(market_keywords)
            
            if relevance_score > 0:
                article_sentiment = self.analyze_article(
                    article.get('title', ''),
                    article.get('content', ''),
                    article.get('source', '')
                )
                article_sentiment['relevance_score'] = relevance_score
                relevant_articles.append(article_sentiment)
                
        if not relevant_articles:
            return {
                'overall_sentiment': 0.0,
                'confidence': 0.0,
                'article_count': 0,
                'relevant_articles': []
            }
            
        # Calculate weighted average sentiment
        total_weighted_sentiment = 0
        total_weight = 0
        
        for article in relevant_articles:
            weight = article['relevance_score'] * article['confidence']
            total_weighted_sentiment += article['sentiment_score'] * weight
            total_weight += weight
            
        overall_sentiment = total_weighted_sentiment / total_weight if total_weight > 0 else 0.0
        overall_confidence = total_weight / len(relevant_articles)
        
        return {
            'overall_sentiment': overall_sentiment,
            'confidence': min(overall_confidence, 1.0),
            'article_count': len(relevant_articles),
            'relevant_articles': relevant_articles[:10],  # Top 10 most relevant
            'market_keywords': market_keywords,
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    def train_custom_model(self, training_data: List[Tuple[str, int]], test_size: float = 0.2):
        """
        Train a custom sentiment model on domain-specific data
        """
        if len(training_data) < 100:
            self.logger.warning("Insufficient training data for custom model")
            return
            
        # Prepare data
        texts, labels = zip(*training_data)
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            processed_texts, labels, test_size=test_size, random_state=42
        )
        
        # Vectorize text
        self.custom_vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        
        X_train_vec = self.custom_vectorizer.fit_transform(X_train)
        X_test_vec = self.custom_vectorizer.transform(X_test)
        
        # Train model
        self.custom_model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        
        self.custom_model.fit(X_train_vec, y_train)
        
        # Evaluate model
        y_pred = self.custom_model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        
        self.logger.info(f"Custom model trained with accuracy: {accuracy:.3f}")
        
        # Save model
        if self.model_path:
            import os
            os.makedirs(self.model_path, exist_ok=True)
            
            with open(f"{self.model_path}/sentiment_model.pkl", 'wb') as f:
                pickle.dump(self.custom_model, f)
            with open(f"{self.model_path}/vectorizer.pkl", 'wb') as f:
                pickle.dump(self.custom_vectorizer, f)
                
        return {
            'accuracy': accuracy,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'classification_report': classification_report(y_test, y_pred)
        }

# Global sentiment analyzer instance
sentiment_analyzer = AdvancedSentimentAnalyzer()

def analyze_sentiment(text: str, weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Convenience function for sentiment analysis"""
    return sentiment_analyzer.ensemble_sentiment(text, weights)

def analyze_market_sentiment(articles: List[Dict[str, Any]], market_keywords: List[str]) -> Dict[str, Any]:
    """Convenience function for market sentiment analysis"""
    return sentiment_analyzer.get_market_sentiment(articles, market_keywords)

