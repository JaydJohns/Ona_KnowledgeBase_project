import re
import numpy as np
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from backend.models.document import Document, Concept, db, document_concepts
from sqlalchemy import func, or_, and_

class SearchEngine:
    def __init__(self):
        self.setup_embeddings()
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.document_embeddings = {}
        self.build_search_index()
    
    def setup_embeddings(self):
        """Setup sentence transformer for semantic search"""
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except:
            self.embedding_model = None
    
    def build_search_index(self):
        """Build search indexes for documents"""
        documents = Document.query.filter(Document.processing_status == 'completed').all()
        
        if not documents:
            return
        
        # Build TF-IDF index
        corpus = []
        doc_ids = []
        
        for doc in documents:
            if doc.content:
                corpus.append(doc.content)
                doc_ids.append(doc.id)
        
        if corpus:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words='english',
                min_df=1,
                max_df=0.8
            )
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
            self.doc_ids = doc_ids
        
        # Build semantic embeddings index
        if self.embedding_model:
            for doc in documents:
                if doc.content:
                    try:
                        embedding = self.embedding_model.encode(doc.content[:1000])  # Limit text length
                        self.document_embeddings[doc.id] = embedding
                    except:
                        continue
    
    def search_documents(self, query, search_type='hybrid', filters=None, limit=20):
        """
        Search documents using different methods
        
        Args:
            query: Search query string
            search_type: 'keyword', 'semantic', 'concept', 'hybrid'
            filters: Dictionary of filters (file_type, date_range, concepts)
            limit: Maximum number of results
        """
        if not query.strip():
            return []
        
        results = []
        
        if search_type in ['keyword', 'hybrid']:
            keyword_results = self._keyword_search(query, filters, limit)
            results.extend(keyword_results)
        
        if search_type in ['semantic', 'hybrid'] and self.embedding_model:
            semantic_results = self._semantic_search(query, filters, limit)
            results.extend(semantic_results)
        
        if search_type in ['concept', 'hybrid']:
            concept_results = self._concept_search(query, filters, limit)
            results.extend(concept_results)
        
        # Merge and rank results
        merged_results = self._merge_search_results(results, search_type)
        
        return merged_results[:limit]
    
    def _keyword_search(self, query, filters=None, limit=20):
        """Perform keyword-based search using TF-IDF"""
        results = []
        
        # Database text search
        db_query = Document.query.filter(Document.processing_status == 'completed')
        
        # Apply filters
        if filters:
            db_query = self._apply_filters(db_query, filters)
        
        # Search in title, content, and summary
        search_terms = query.lower().split()
        conditions = []
        
        for term in search_terms:
            term_conditions = [
                Document.title.ilike(f'%{term}%'),
                Document.content.ilike(f'%{term}%'),
                Document.summary.ilike(f'%{term}%')
            ]
            conditions.append(or_(*term_conditions))
        
        if conditions:
            db_query = db_query.filter(and_(*conditions))
        
        documents = db_query.limit(limit * 2).all()  # Get more for ranking
        
        # Rank using TF-IDF if available
        if self.tfidf_vectorizer and self.tfidf_matrix is not None:
            try:
                query_vector = self.tfidf_vectorizer.transform([query])
                similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
                
                # Create document similarity mapping
                doc_similarities = {}
                for i, doc_id in enumerate(self.doc_ids):
                    doc_similarities[doc_id] = similarities[i]
                
                # Rank documents by similarity
                for doc in documents:
                    similarity = doc_similarities.get(doc.id, 0.0)
                    if similarity > 0.01:  # Minimum threshold
                        results.append({
                            'document': doc,
                            'score': similarity,
                            'search_type': 'keyword',
                            'highlights': self._extract_highlights(doc, query)
                        })
            except:
                # Fallback to simple ranking
                for doc in documents:
                    score = self._calculate_simple_relevance(doc, query)
                    results.append({
                        'document': doc,
                        'score': score,
                        'search_type': 'keyword',
                        'highlights': self._extract_highlights(doc, query)
                    })
        else:
            # Simple relevance scoring
            for doc in documents:
                score = self._calculate_simple_relevance(doc, query)
                results.append({
                    'document': doc,
                    'score': score,
                    'search_type': 'keyword',
                    'highlights': self._extract_highlights(doc, query)
                })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def _semantic_search(self, query, filters=None, limit=20):
        """Perform semantic search using sentence embeddings"""
        if not self.embedding_model or not self.document_embeddings:
            return []
        
        results = []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Calculate similarities with all documents
            similarities = []
            for doc_id, doc_embedding in self.document_embeddings.items():
                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1),
                    doc_embedding.reshape(1, -1)
                )[0][0]
                similarities.append((doc_id, similarity))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Get top documents
            top_doc_ids = [doc_id for doc_id, sim in similarities[:limit * 2] if sim > 0.1]
            
            if top_doc_ids:
                db_query = Document.query.filter(Document.id.in_(top_doc_ids))
                
                # Apply filters
                if filters:
                    db_query = self._apply_filters(db_query, filters)
                
                documents = db_query.all()
                
                # Create results with similarity scores
                doc_similarities = dict(similarities)
                for doc in documents:
                    similarity = doc_similarities.get(doc.id, 0.0)
                    results.append({
                        'document': doc,
                        'score': similarity,
                        'search_type': 'semantic',
                        'highlights': self._extract_semantic_highlights(doc, query)
                    })
        
        except Exception as e:
            print(f"Semantic search error: {e}")
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def _concept_search(self, query, filters=None, limit=20):
        """Search documents based on concepts"""
        results = []
        
        # Find concepts matching the query
        concept_query = Concept.query.filter(
            or_(
                Concept.name.ilike(f'%{query}%'),
                Concept.description.ilike(f'%{query}%')
            )
        ).all()
        
        if not concept_query:
            return results
        
        concept_ids = [c.id for c in concept_query]
        
        # Find documents containing these concepts
        doc_concept_query = db.session.query(
            Document,
            func.count(document_concepts.c.concept_id).label('concept_matches'),
            func.avg(document_concepts.c.relevance_score).label('avg_relevance')
        ).join(
            document_concepts, Document.id == document_concepts.c.document_id
        ).filter(
            document_concepts.c.concept_id.in_(concept_ids),
            Document.processing_status == 'completed'
        ).group_by(Document.id)
        
        # Apply filters
        if filters:
            doc_concept_query = self._apply_filters(doc_concept_query, filters)
        
        documents = doc_concept_query.order_by(
            func.count(document_concepts.c.concept_id).desc()
        ).limit(limit).all()
        
        for doc_result in documents:
            doc = doc_result[0] if isinstance(doc_result, tuple) else doc_result
            concept_matches = doc_result[1] if isinstance(doc_result, tuple) else 1
            avg_relevance = doc_result[2] if isinstance(doc_result, tuple) else 0.5
            
            # Calculate concept-based score
            score = (concept_matches * avg_relevance) / len(concept_ids)
            
            results.append({
                'document': doc,
                'score': score,
                'search_type': 'concept',
                'highlights': self._extract_concept_highlights(doc, concept_query),
                'matched_concepts': concept_matches
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def _apply_filters(self, query, filters):
        """Apply search filters to query"""
        if not filters:
            return query
        
        if 'file_type' in filters and filters['file_type']:
            query = query.filter(Document.file_type.contains(filters['file_type']))
        
        if 'date_range' in filters and filters['date_range']:
            date_range = filters['date_range']
            if 'start' in date_range:
                query = query.filter(Document.upload_date >= date_range['start'])
            if 'end' in date_range:
                query = query.filter(Document.upload_date <= date_range['end'])
        
        if 'concepts' in filters and filters['concepts']:
            concept_ids = filters['concepts']
            query = query.join(
                document_concepts, Document.id == document_concepts.c.document_id
            ).filter(document_concepts.c.concept_id.in_(concept_ids))
        
        if 'min_word_count' in filters:
            query = query.filter(Document.word_count >= filters['min_word_count'])
        
        if 'max_word_count' in filters:
            query = query.filter(Document.word_count <= filters['max_word_count'])
        
        return query
    
    def _merge_search_results(self, results, search_type):
        """Merge and rank results from different search methods"""
        if search_type != 'hybrid':
            return results
        
        # Group results by document ID
        doc_results = defaultdict(list)
        for result in results:
            doc_id = result['document'].id
            doc_results[doc_id].append(result)
        
        # Merge scores for documents found by multiple methods
        merged_results = []
        for doc_id, doc_result_list in doc_results.items():
            if len(doc_result_list) == 1:
                merged_results.append(doc_result_list[0])
            else:
                # Combine scores from different search methods
                combined_score = 0
                search_types = []
                highlights = []
                
                for result in doc_result_list:
                    # Weight different search types
                    weight = {
                        'keyword': 0.4,
                        'semantic': 0.4,
                        'concept': 0.2
                    }.get(result['search_type'], 0.3)
                    
                    combined_score += result['score'] * weight
                    search_types.append(result['search_type'])
                    highlights.extend(result.get('highlights', []))
                
                # Bonus for being found by multiple methods
                method_bonus = len(set(search_types)) * 0.1
                combined_score += method_bonus
                
                merged_results.append({
                    'document': doc_result_list[0]['document'],
                    'score': combined_score,
                    'search_type': 'hybrid',
                    'search_methods': list(set(search_types)),
                    'highlights': highlights[:5]  # Limit highlights
                })
        
        return sorted(merged_results, key=lambda x: x['score'], reverse=True)
    
    def _calculate_simple_relevance(self, document, query):
        """Calculate simple relevance score based on term frequency"""
        query_terms = query.lower().split()
        score = 0
        
        # Check title (higher weight)
        if document.title:
            title_lower = document.title.lower()
            for term in query_terms:
                if term in title_lower:
                    score += 2.0
        
        # Check summary (medium weight)
        if document.summary:
            summary_lower = document.summary.lower()
            for term in query_terms:
                score += summary_lower.count(term) * 1.0
        
        # Check content (lower weight but more comprehensive)
        if document.content:
            content_lower = document.content.lower()
            for term in query_terms:
                score += min(content_lower.count(term) * 0.1, 1.0)  # Cap content score per term
        
        return score
    
    def _extract_highlights(self, document, query):
        """Extract text highlights around query terms"""
        highlights = []
        query_terms = [term.lower() for term in query.split()]
        
        text_sources = [
            ('title', document.title),
            ('summary', document.summary),
            ('content', document.content)
        ]
        
        for source_type, text in text_sources:
            if not text:
                continue
            
            text_lower = text.lower()
            for term in query_terms:
                if term in text_lower:
                    # Find all occurrences
                    start = 0
                    while True:
                        pos = text_lower.find(term, start)
                        if pos == -1:
                            break
                        
                        # Extract context around the term
                        context_start = max(0, pos - 50)
                        context_end = min(len(text), pos + len(term) + 50)
                        context = text[context_start:context_end]
                        
                        # Highlight the term
                        highlighted = re.sub(
                            re.escape(term),
                            f"<mark>{term}</mark>",
                            context,
                            flags=re.IGNORECASE
                        )
                        
                        highlights.append({
                            'source': source_type,
                            'text': highlighted,
                            'position': pos
                        })
                        
                        start = pos + 1
                        
                        if len(highlights) >= 3:  # Limit highlights
                            break
            
            if len(highlights) >= 3:
                break
        
        return highlights[:3]
    
    def _extract_semantic_highlights(self, document, query):
        """Extract semantically relevant highlights"""
        # For now, use keyword-based highlights
        # Could be enhanced with more sophisticated semantic matching
        return self._extract_highlights(document, query)
    
    def _extract_concept_highlights(self, document, concepts):
        """Extract highlights based on concept matches"""
        highlights = []
        
        for concept in concepts:
            if document.content and concept.name.lower() in document.content.lower():
                pos = document.content.lower().find(concept.name.lower())
                if pos != -1:
                    context_start = max(0, pos - 50)
                    context_end = min(len(document.content), pos + len(concept.name) + 50)
                    context = document.content[context_start:context_end]
                    
                    highlighted = re.sub(
                        re.escape(concept.name),
                        f"<mark>{concept.name}</mark>",
                        context,
                        flags=re.IGNORECASE
                    )
                    
                    highlights.append({
                        'source': 'concept',
                        'text': highlighted,
                        'concept': concept.name
                    })
        
        return highlights[:3]
    
    def suggest_query_completions(self, partial_query, limit=10):
        """Suggest query completions based on document content and concepts"""
        suggestions = []
        
        if len(partial_query) < 2:
            return suggestions
        
        # Get concept suggestions
        concepts = Concept.query.filter(
            Concept.name.ilike(f'{partial_query}%')
        ).order_by(Concept.frequency.desc()).limit(limit).all()
        
        for concept in concepts:
            suggestions.append({
                'text': concept.name,
                'type': 'concept',
                'frequency': concept.frequency
            })
        
        # Get title suggestions
        documents = Document.query.filter(
            Document.title.ilike(f'%{partial_query}%'),
            Document.processing_status == 'completed'
        ).limit(5).all()
        
        for doc in documents:
            suggestions.append({
                'text': doc.title,
                'type': 'title',
                'document_id': doc.id
            })
        
        return suggestions[:limit]
    
    def get_search_analytics(self):
        """Get search analytics and statistics"""
        total_docs = Document.query.filter(Document.processing_status == 'completed').count()
        total_concepts = Concept.query.count()
        
        # Most frequent search terms (would need to track search queries)
        top_concepts = Concept.query.order_by(Concept.frequency.desc()).limit(10).all()
        
        return {
            'total_searchable_documents': total_docs,
            'total_concepts': total_concepts,
            'index_status': {
                'tfidf_built': self.tfidf_matrix is not None,
                'embeddings_built': len(self.document_embeddings) > 0,
                'documents_indexed': len(self.doc_ids) if hasattr(self, 'doc_ids') else 0
            },
            'top_concepts': [concept.to_dict() for concept in top_concepts]
        }