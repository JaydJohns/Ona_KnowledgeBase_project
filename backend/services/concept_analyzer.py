import re
import numpy as np
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from backend.models.document import Concept, ConceptRelation, Document, db, document_concepts
import spacy

class ConceptAnalyzer:
    def __init__(self):
        self.setup_nlp()
        self.hci_concepts = self.load_hci_concepts()
        self.concept_patterns = self.create_concept_patterns()
    
    def setup_nlp(self):
        """Setup NLP pipeline"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = None
    
    def load_hci_concepts(self):
        """Load predefined HCI concepts and terminology"""
        return {
            'interaction_design': [
                'user interface', 'ui', 'user experience', 'ux', 'interaction design',
                'interface design', 'usability', 'accessibility', 'user-centered design',
                'human-centered design', 'design thinking', 'wireframe', 'prototype',
                'mockup', 'user flow', 'information architecture', 'navigation'
            ],
            'usability': [
                'usability testing', 'user testing', 'heuristic evaluation', 'cognitive walkthrough',
                'task analysis', 'user study', 'usability metrics', 'effectiveness',
                'efficiency', 'satisfaction', 'learnability', 'memorability', 'error prevention'
            ],
            'cognitive_psychology': [
                'cognitive load', 'mental model', 'working memory', 'attention',
                'perception', 'cognition', 'cognitive science', 'human factors',
                'cognitive ergonomics', 'information processing', 'decision making'
            ],
            'input_methods': [
                'mouse', 'keyboard', 'touchscreen', 'gesture', 'voice input',
                'eye tracking', 'brain-computer interface', 'haptic feedback',
                'multimodal interaction', 'natural user interface', 'tangible interface'
            ],
            'evaluation_methods': [
                'user evaluation', 'empirical study', 'controlled experiment',
                'field study', 'ethnography', 'survey', 'interview', 'focus group',
                'observation', 'think-aloud protocol', 'a/b testing'
            ],
            'design_principles': [
                'affordance', 'feedback', 'visibility', 'consistency', 'constraint',
                'mapping', 'conceptual model', 'gulf of execution', 'gulf of evaluation',
                'norman door', 'fitts law', 'hicks law', 'gestalt principles'
            ],
            'accessibility': [
                'web accessibility', 'wcag', 'screen reader', 'assistive technology',
                'universal design', 'inclusive design', 'disability', 'barrier-free',
                'alt text', 'keyboard navigation', 'color contrast'
            ],
            'mobile_computing': [
                'mobile interface', 'responsive design', 'touch interaction',
                'mobile usability', 'context-aware computing', 'location-based',
                'augmented reality', 'virtual reality', 'mixed reality'
            ],
            'social_computing': [
                'social media', 'collaborative system', 'computer-mediated communication',
                'online community', 'social network', 'crowdsourcing',
                'social presence', 'computer-supported cooperative work', 'cscw'
            ],
            'visualization': [
                'information visualization', 'data visualization', 'visual analytics',
                'scientific visualization', 'dashboard', 'chart', 'graph',
                'interactive visualization', 'visual encoding', 'visual perception'
            ]
        }
    
    def create_concept_patterns(self):
        """Create regex patterns for concept detection"""
        patterns = {}
        for category, concepts in self.hci_concepts.items():
            category_patterns = []
            for concept in concepts:
                # Create pattern that matches the concept with word boundaries
                pattern = r'\b' + re.escape(concept.lower()) + r'\b'
                category_patterns.append(pattern)
            patterns[category] = '|'.join(category_patterns)
        return patterns
    
    def extract_concepts_from_text(self, text, document_id=None):
        """Extract concepts from text using multiple methods"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_concepts = []
        
        # 1. Pattern-based concept extraction
        for category, pattern in self.concept_patterns.items():
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                concept_text = match.group()
                context = self._extract_context(text, match.start(), match.end())
                
                found_concepts.append({
                    'name': concept_text,
                    'category': category,
                    'context': context,
                    'position': match.start(),
                    'confidence': 0.9  # High confidence for pattern matches
                })
        
        # 2. NLP-based concept extraction
        if self.nlp:
            nlp_concepts = self._extract_nlp_concepts(text)
            found_concepts.extend(nlp_concepts)
        
        # 3. Statistical concept extraction
        statistical_concepts = self._extract_statistical_concepts(text)
        found_concepts.extend(statistical_concepts)
        
        # Remove duplicates and rank by confidence
        unique_concepts = self._deduplicate_concepts(found_concepts)
        
        return sorted(unique_concepts, key=lambda x: x['confidence'], reverse=True)
    
    def _extract_context(self, text, start, end, window=100):
        """Extract context around a concept mention"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
    
    def _extract_nlp_concepts(self, text):
        """Extract concepts using NLP techniques"""
        concepts = []
        doc = self.nlp(text)
        
        # Extract noun phrases as potential concepts
        for chunk in doc.noun_chunks:
            if len(chunk.text.strip()) > 3 and len(chunk.text.split()) <= 4:
                concepts.append({
                    'name': chunk.text.lower().strip(),
                    'category': 'extracted',
                    'context': self._extract_context(text, chunk.start_char, chunk.end_char),
                    'position': chunk.start_char,
                    'confidence': 0.6
                })
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'PRODUCT', 'EVENT'] and len(ent.text.strip()) > 2:
                concepts.append({
                    'name': ent.text.lower().strip(),
                    'category': f'entity_{ent.label_.lower()}',
                    'context': self._extract_context(text, ent.start_char, ent.end_char),
                    'position': ent.start_char,
                    'confidence': 0.7
                })
        
        return concepts
    
    def _extract_statistical_concepts(self, text):
        """Extract concepts using statistical methods"""
        concepts = []
        
        # Use TF-IDF to find important terms
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        if len(sentences) < 2:
            return concepts
        
        try:
            vectorizer = TfidfVectorizer(
                max_features=50,
                ngram_range=(1, 3),
                stop_words='english',
                min_df=1,
                max_df=0.8
            )
            
            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get average TF-IDF scores
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Extract top scoring terms as concepts
            for i, score in enumerate(mean_scores):
                if score > 0.1:  # Threshold for significance
                    term = feature_names[i]
                    if len(term) > 3 and not term.isdigit():
                        concepts.append({
                            'name': term,
                            'category': 'statistical',
                            'context': '',
                            'position': 0,
                            'confidence': min(score * 2, 0.8)  # Scale confidence
                        })
        
        except Exception:
            pass  # Skip if TF-IDF fails
        
        return concepts
    
    def _deduplicate_concepts(self, concepts):
        """Remove duplicate concepts and merge similar ones"""
        unique_concepts = {}
        
        for concept in concepts:
            name = concept['name'].strip().lower()
            
            # Skip very short or common terms
            if len(name) < 3 or name in ['the', 'and', 'for', 'with', 'this', 'that']:
                continue
            
            if name in unique_concepts:
                # Keep the one with higher confidence
                if concept['confidence'] > unique_concepts[name]['confidence']:
                    unique_concepts[name] = concept
            else:
                unique_concepts[name] = concept
        
        return list(unique_concepts.values())
    
    def save_concepts_to_db(self, concepts, document_id):
        """Save extracted concepts to database"""
        saved_concepts = []
        
        for concept_data in concepts:
            # Check if concept already exists
            concept = Concept.query.filter_by(name=concept_data['name']).first()
            
            if not concept:
                # Create new concept
                concept = Concept(
                    name=concept_data['name'],
                    category=concept_data['category'],
                    description=concept_data.get('context', '')[:500]  # Limit description length
                )
                db.session.add(concept)
                db.session.flush()  # Get the ID
            else:
                # Update frequency
                concept.frequency += 1
            
            # Link concept to document
            existing_link = db.session.query(document_concepts).filter_by(
                document_id=document_id,
                concept_id=concept.id
            ).first()
            
            if not existing_link:
                # Create new document-concept relationship
                stmt = document_concepts.insert().values(
                    document_id=document_id,
                    concept_id=concept.id,
                    relevance_score=concept_data['confidence'],
                    context=concept_data.get('context', '')[:1000]
                )
                db.session.execute(stmt)
            
            saved_concepts.append(concept)
        
        db.session.commit()
        return saved_concepts
    
    def find_concept_relations(self, concept_id, similarity_threshold=0.3):
        """Find related concepts using various similarity measures"""
        concept = Concept.query.get(concept_id)
        if not concept:
            return []
        
        # Get all other concepts
        other_concepts = Concept.query.filter(Concept.id != concept_id).all()
        relations = []
        
        for other_concept in other_concepts:
            similarity = self._calculate_concept_similarity(concept, other_concept)
            
            if similarity > similarity_threshold:
                relation_type = self._determine_relation_type(concept, other_concept, similarity)
                
                # Check if relation already exists
                existing = ConceptRelation.query.filter(
                    ((ConceptRelation.concept1_id == concept.id) & 
                     (ConceptRelation.concept2_id == other_concept.id)) |
                    ((ConceptRelation.concept1_id == other_concept.id) & 
                     (ConceptRelation.concept2_id == concept.id))
                ).first()
                
                if not existing:
                    relation = ConceptRelation(
                        concept1_id=concept.id,
                        concept2_id=other_concept.id,
                        relation_type=relation_type,
                        strength=similarity
                    )
                    relations.append(relation)
        
        return relations
    
    def _calculate_concept_similarity(self, concept1, concept2):
        """Calculate similarity between two concepts"""
        similarity_score = 0.0
        
        # 1. Name similarity (Jaccard similarity of words)
        words1 = set(concept1.name.lower().split())
        words2 = set(concept2.name.lower().split())
        
        if words1 and words2:
            jaccard = len(words1.intersection(words2)) / len(words1.union(words2))
            similarity_score += jaccard * 0.4
        
        # 2. Category similarity
        if concept1.category == concept2.category:
            similarity_score += 0.3
        
        # 3. Co-occurrence in documents
        common_docs = set([d.id for d in concept1.documents]) & set([d.id for d in concept2.documents])
        if common_docs:
            co_occurrence = len(common_docs) / max(len(concept1.documents), len(concept2.documents))
            similarity_score += co_occurrence * 0.3
        
        return min(similarity_score, 1.0)
    
    def _determine_relation_type(self, concept1, concept2, similarity):
        """Determine the type of relationship between concepts"""
        # Simple heuristics for relation type determination
        if similarity > 0.8:
            return 'synonym'
        elif concept1.category == concept2.category:
            return 'related'
        elif 'design' in concept1.name and 'design' in concept2.name:
            return 'related'
        elif similarity > 0.6:
            return 'related'
        else:
            return 'weak_relation'
    
    def build_concept_graph(self, min_strength=0.3):
        """Build a graph of concept relationships"""
        concepts = Concept.query.all()
        relations = ConceptRelation.query.filter(ConceptRelation.strength >= min_strength).all()
        
        graph = {
            'nodes': [
                {
                    'id': concept.id,
                    'name': concept.name,
                    'category': concept.category,
                    'frequency': concept.frequency,
                    'size': min(concept.frequency * 2, 20)  # Node size based on frequency
                }
                for concept in concepts
            ],
            'edges': [
                {
                    'source': relation.concept1_id,
                    'target': relation.concept2_id,
                    'type': relation.relation_type,
                    'strength': relation.strength,
                    'width': relation.strength * 5  # Edge width based on strength
                }
                for relation in relations
            ]
        }
        
        return graph
    
    def suggest_related_documents(self, document_id, limit=5):
        """Suggest documents related to the given document based on shared concepts"""
        document = Document.query.get(document_id)
        if not document:
            return []
        
        # Get concepts for this document
        doc_concepts = [c.id for c in document.concepts]
        
        if not doc_concepts:
            return []
        
        # Find documents that share concepts
        related_docs = db.session.query(
            Document.id,
            Document.title,
            Document.summary,
            db.func.count(document_concepts.c.concept_id).label('shared_concepts')
        ).join(
            document_concepts, Document.id == document_concepts.c.document_id
        ).filter(
            document_concepts.c.concept_id.in_(doc_concepts),
            Document.id != document_id
        ).group_by(
            Document.id, Document.title, Document.summary
        ).order_by(
            db.desc('shared_concepts')
        ).limit(limit).all()
        
        return [
            {
                'id': doc.id,
                'title': doc.title,
                'summary': doc.summary,
                'shared_concepts': doc.shared_concepts
            }
            for doc in related_docs
        ]
    
    def process_document_concepts(self, document_id):
        """Complete concept processing pipeline for a document"""
        document = Document.query.get(document_id)
        if not document or not document.content:
            return []
        
        # Extract concepts from document content
        concepts = self.extract_concepts_from_text(document.content, document_id)
        
        # Save concepts to database
        saved_concepts = self.save_concepts_to_db(concepts, document_id)
        
        # Find and save concept relations
        all_relations = []
        for concept in saved_concepts:
            relations = self.find_concept_relations(concept.id)
            all_relations.extend(relations)
        
        # Save relations to database
        for relation in all_relations:
            db.session.add(relation)
        
        db.session.commit()
        
        return saved_concepts