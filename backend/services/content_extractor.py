import re
import nltk
import spacy
from collections import Counter
import textstat
from sentence_transformers import SentenceTransformer
import numpy as np

class ContentExtractor:
    def __init__(self):
        self.setup_nltk()
        self.setup_spacy()
        self.setup_embeddings()
    
    def setup_nltk(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')
    
    def setup_spacy(self):
        """Load spaCy model for NLP processing"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If model not found, use basic tokenizer
            self.nlp = None
    
    def setup_embeddings(self):
        """Load sentence transformer for embeddings"""
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except:
            self.embedding_model = None
    
    def clean_text(self, text):
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        return text.strip()
    
    def extract_sentences(self, text):
        """Extract sentences from text"""
        if not text:
            return []
        
        sentences = nltk.sent_tokenize(text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def extract_keywords(self, text, max_keywords=20):
        """Extract keywords using frequency analysis"""
        if not text:
            return []
        
        # Clean text and convert to lowercase
        clean_text = self.clean_text(text.lower())
        
        # Tokenize and remove stopwords
        from nltk.corpus import stopwords
        stop_words = set(stopwords.words('english'))
        
        words = nltk.word_tokenize(clean_text)
        words = [word for word in words if word.isalpha() and len(word) > 2 and word not in stop_words]
        
        # Get word frequencies
        word_freq = Counter(words)
        
        # Extract phrases (bigrams and trigrams)
        bigrams = [' '.join(bg) for bg in nltk.bigrams(words)]
        trigrams = [' '.join(tg) for tg in nltk.trigrams(words)]
        
        phrase_freq = Counter(bigrams + trigrams)
        
        # Combine and rank keywords
        keywords = []
        
        # Add top single words
        for word, freq in word_freq.most_common(max_keywords // 2):
            keywords.append({'term': word, 'frequency': freq, 'type': 'word'})
        
        # Add top phrases
        for phrase, freq in phrase_freq.most_common(max_keywords // 2):
            if freq > 1:  # Only include phrases that appear multiple times
                keywords.append({'term': phrase, 'frequency': freq, 'type': 'phrase'})
        
        return keywords[:max_keywords]
    
    def extract_entities(self, text):
        """Extract named entities using spaCy"""
        if not self.nlp or not text:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            if len(ent.text.strip()) > 2:
                entities.append({
                    'text': ent.text.strip(),
                    'label': ent.label_,
                    'description': spacy.explain(ent.label_)
                })
        
        # Remove duplicates and sort by frequency
        entity_counts = Counter([ent['text'].lower() for ent in entities])
        unique_entities = []
        seen = set()
        
        for ent in entities:
            if ent['text'].lower() not in seen:
                ent['frequency'] = entity_counts[ent['text'].lower()]
                unique_entities.append(ent)
                seen.add(ent['text'].lower())
        
        return sorted(unique_entities, key=lambda x: x['frequency'], reverse=True)
    
    def extract_topics(self, text, num_topics=5):
        """Extract main topics from text using keyword clustering"""
        keywords = self.extract_keywords(text, max_keywords=50)
        
        if not keywords:
            return []
        
        # Simple topic extraction based on keyword co-occurrence
        # This is a simplified approach - could be enhanced with LDA or other topic modeling
        
        # Group keywords by frequency tiers
        high_freq = [kw for kw in keywords if kw['frequency'] >= 5]
        med_freq = [kw for kw in keywords if 2 <= kw['frequency'] < 5]
        
        topics = []
        
        # Create topics from high-frequency terms
        for i, kw in enumerate(high_freq[:num_topics]):
            topics.append({
                'id': i + 1,
                'name': kw['term'].title(),
                'keywords': [kw['term']],
                'strength': kw['frequency'] / max([k['frequency'] for k in keywords])
            })
        
        # Add related medium-frequency terms to topics
        for topic in topics:
            main_term = topic['keywords'][0]
            related = [kw['term'] for kw in med_freq if main_term in kw['term'] or kw['term'] in main_term]
            topic['keywords'].extend(related[:3])
        
        return topics
    
    def calculate_readability(self, text):
        """Calculate readability metrics"""
        if not text:
            return {}
        
        return {
            'flesch_reading_ease': textstat.flesch_reading_ease(text),
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
            'automated_readability_index': textstat.automated_readability_index(text),
            'coleman_liau_index': textstat.coleman_liau_index(text),
            'gunning_fog': textstat.gunning_fog(text),
            'smog_index': textstat.smog_index(text),
            'reading_time_minutes': textstat.reading_time(text, ms_per_char=14.69)
        }
    
    def generate_embeddings(self, text):
        """Generate sentence embeddings for semantic search"""
        if not self.embedding_model or not text:
            return None
        
        try:
            # Split text into chunks for better embeddings
            sentences = self.extract_sentences(text)
            if not sentences:
                return None
            
            # Generate embeddings for sentences
            embeddings = self.embedding_model.encode(sentences)
            
            # Return average embedding for the document
            return np.mean(embeddings, axis=0).tolist()
        except:
            return None
    
    def extract_structure(self, text):
        """Extract document structure (headings, sections)"""
        if not text:
            return {}
        
        lines = text.split('\n')
        structure = {
            'headings': [],
            'sections': [],
            'paragraphs': 0,
            'lists': 0
        }
        
        current_section = None
        paragraph_count = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Detect headings (simple heuristic)
            if (len(line) < 100 and 
                (line.isupper() or 
                 re.match(r'^\d+\.', line) or
                 re.match(r'^[A-Z][^.!?]*$', line))):
                
                structure['headings'].append({
                    'text': line,
                    'line_number': i + 1,
                    'level': self._estimate_heading_level(line)
                })
                
                if current_section:
                    current_section['end_line'] = i
                
                current_section = {
                    'title': line,
                    'start_line': i + 1,
                    'end_line': None
                }
                structure['sections'].append(current_section)
            
            # Count paragraphs
            elif len(line) > 50:
                paragraph_count += 1
            
            # Detect lists
            elif re.match(r'^[\-\*\+]\s', line) or re.match(r'^\d+\.\s', line):
                structure['lists'] += 1
        
        if current_section:
            current_section['end_line'] = len(lines)
        
        structure['paragraphs'] = paragraph_count
        return structure
    
    def _estimate_heading_level(self, text):
        """Estimate heading level based on text characteristics"""
        if text.isupper():
            return 1
        elif re.match(r'^\d+\.', text):
            return 2
        elif len(text) < 50:
            return 3
        else:
            return 4
    
    def process_document_content(self, text, title=None):
        """Complete content processing pipeline"""
        if not text:
            return {}
        
        # Clean the text
        cleaned_text = self.clean_text(text)
        
        # Extract various content features
        result = {
            'cleaned_text': cleaned_text,
            'sentences': self.extract_sentences(cleaned_text),
            'keywords': self.extract_keywords(cleaned_text),
            'entities': self.extract_entities(cleaned_text),
            'topics': self.extract_topics(cleaned_text),
            'readability': self.calculate_readability(cleaned_text),
            'structure': self.extract_structure(text),
            'embeddings': self.generate_embeddings(cleaned_text),
            'statistics': {
                'character_count': len(text),
                'word_count': len(cleaned_text.split()),
                'sentence_count': len(self.extract_sentences(cleaned_text)),
                'paragraph_count': len([p for p in text.split('\n\n') if p.strip()]),
                'unique_words': len(set(cleaned_text.lower().split()))
            }
        }
        
        return result