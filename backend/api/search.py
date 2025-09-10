from flask import Blueprint, request, jsonify, current_app
from backend.services.search_engine import SearchEngine
from datetime import datetime
import json

search_bp = Blueprint('search', __name__)

# Global search engine instance
search_engine = None

def get_search_engine():
    """Get or create search engine instance"""
    global search_engine
    if search_engine is None:
        search_engine = SearchEngine()
    return search_engine

@search_bp.route('/', methods=['GET'])
def search_documents():
    """Search documents with various options"""
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'hybrid')  # keyword, semantic, concept, hybrid
        limit = request.args.get('limit', 20, type=int)
        
        # Parse filters
        filters = {}
        
        # File type filter
        file_type = request.args.get('file_type')
        if file_type:
            filters['file_type'] = file_type
        
        # Date range filter
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        if start_date or end_date:
            date_range = {}
            if start_date:
                date_range['start'] = datetime.fromisoformat(start_date)
            if end_date:
                date_range['end'] = datetime.fromisoformat(end_date)
            filters['date_range'] = date_range
        
        # Concept filter
        concepts = request.args.get('concepts')
        if concepts:
            try:
                concept_ids = [int(c) for c in concepts.split(',')]
                filters['concepts'] = concept_ids
            except ValueError:
                pass
        
        # Word count filters
        min_words = request.args.get('min_words', type=int)
        max_words = request.args.get('max_words', type=int)
        if min_words:
            filters['min_word_count'] = min_words
        if max_words:
            filters['max_word_count'] = max_words
        
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400
        
        # Perform search
        engine = get_search_engine()
        results = engine.search_documents(
            query=query,
            search_type=search_type,
            filters=filters,
            limit=limit
        )
        
        # Format results
        formatted_results = []
        for result in results:
            doc = result['document']
            formatted_result = {
                'document': {
                    'id': doc.id,
                    'title': doc.title,
                    'summary': doc.summary,
                    'filename': doc.original_filename,
                    'file_type': doc.file_type,
                    'word_count': doc.word_count,
                    'upload_date': doc.upload_date.isoformat() if doc.upload_date else None,
                    'processed_date': doc.processed_date.isoformat() if doc.processed_date else None
                },
                'score': result['score'],
                'search_type': result['search_type'],
                'highlights': result.get('highlights', [])
            }
            
            # Add search method info for hybrid searches
            if 'search_methods' in result:
                formatted_result['search_methods'] = result['search_methods']
            
            # Add concept match info
            if 'matched_concepts' in result:
                formatted_result['matched_concepts'] = result['matched_concepts']
            
            formatted_results.append(formatted_result)
        
        return jsonify({
            'query': query,
            'search_type': search_type,
            'total_results': len(formatted_results),
            'results': formatted_results,
            'filters_applied': filters
        })
        
    except Exception as e:
        current_app.logger.error(f"Search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@search_bp.route('/suggestions', methods=['GET'])
def get_search_suggestions():
    """Get search query suggestions"""
    try:
        partial_query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        if len(partial_query) < 2:
            return jsonify({'suggestions': []})
        
        engine = get_search_engine()
        suggestions = engine.suggest_query_completions(partial_query, limit=limit)
        
        return jsonify({'suggestions': suggestions})
        
    except Exception as e:
        current_app.logger.error(f"Search suggestions error: {str(e)}")
        return jsonify({'error': 'Failed to get suggestions'}), 500

@search_bp.route('/analytics', methods=['GET'])
def get_search_analytics():
    """Get search analytics and statistics"""
    try:
        engine = get_search_engine()
        analytics = engine.get_search_analytics()
        
        return jsonify(analytics)
        
    except Exception as e:
        current_app.logger.error(f"Search analytics error: {str(e)}")
        return jsonify({'error': 'Failed to get analytics'}), 500

@search_bp.route('/reindex', methods=['POST'])
def reindex_documents():
    """Rebuild search indexes"""
    try:
        global search_engine
        search_engine = SearchEngine()  # Rebuild indexes
        
        analytics = search_engine.get_search_analytics()
        
        return jsonify({
            'message': 'Search indexes rebuilt successfully',
            'analytics': analytics
        })
        
    except Exception as e:
        current_app.logger.error(f"Reindex error: {str(e)}")
        return jsonify({'error': 'Failed to rebuild indexes'}), 500

@search_bp.route('/similar', methods=['GET'])
def find_similar_documents():
    """Find documents similar to a given document"""
    try:
        document_id = request.args.get('document_id', type=int)
        limit = request.args.get('limit', 5, type=int)
        
        if not document_id:
            return jsonify({'error': 'document_id parameter is required'}), 400
        
        # Get the document
        from backend.models.document import Document
        document = Document.query.get_or_404(document_id)
        
        if not document.content:
            return jsonify({'error': 'Document has no content for similarity search'}), 400
        
        # Use document title and summary as query
        query = f"{document.title} {document.summary}".strip()
        if not query:
            query = document.content[:200]  # Use first 200 chars of content
        
        engine = get_search_engine()
        results = engine.search_documents(
            query=query,
            search_type='semantic',
            filters={'min_word_count': 50},  # Exclude very short documents
            limit=limit + 1  # Get one extra to exclude the original document
        )
        
        # Remove the original document from results
        similar_docs = []
        for result in results:
            if result['document'].id != document_id:
                similar_docs.append({
                    'document': {
                        'id': result['document'].id,
                        'title': result['document'].title,
                        'summary': result['document'].summary,
                        'filename': result['document'].original_filename,
                        'word_count': result['document'].word_count,
                        'upload_date': result['document'].upload_date.isoformat() if result['document'].upload_date else None
                    },
                    'similarity_score': result['score']
                })
        
        return jsonify({
            'document_id': document_id,
            'similar_documents': similar_docs[:limit]
        })
        
    except Exception as e:
        current_app.logger.error(f"Similar documents error: {str(e)}")
        return jsonify({'error': 'Failed to find similar documents'}), 500

@search_bp.route('/advanced', methods=['POST'])
def advanced_search():
    """Advanced search with complex queries and filters"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        query = data.get('query', '').strip()
        search_config = data.get('search_config', {})
        filters = data.get('filters', {})
        limit = data.get('limit', 20)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Parse search configuration
        search_type = search_config.get('type', 'hybrid')
        boost_title = search_config.get('boost_title', False)
        boost_recent = search_config.get('boost_recent', False)
        
        engine = get_search_engine()
        results = engine.search_documents(
            query=query,
            search_type=search_type,
            filters=filters,
            limit=limit
        )
        
        # Apply additional boosting if requested
        if boost_title or boost_recent:
            for result in results:
                doc = result['document']
                
                # Boost documents with query terms in title
                if boost_title and doc.title:
                    query_terms = query.lower().split()
                    title_lower = doc.title.lower()
                    title_matches = sum(1 for term in query_terms if term in title_lower)
                    if title_matches > 0:
                        result['score'] *= (1 + title_matches * 0.2)
                
                # Boost recent documents
                if boost_recent and doc.upload_date:
                    days_old = (datetime.now() - doc.upload_date).days
                    if days_old < 30:  # Boost documents less than 30 days old
                        recency_boost = max(0.1, 1 - (days_old / 30) * 0.3)
                        result['score'] *= (1 + recency_boost)
            
            # Re-sort after boosting
            results.sort(key=lambda x: x['score'], reverse=True)
        
        # Format results
        formatted_results = []
        for result in results:
            doc = result['document']
            formatted_result = {
                'document': doc.to_dict(),
                'score': result['score'],
                'search_type': result['search_type'],
                'highlights': result.get('highlights', [])
            }
            formatted_results.append(formatted_result)
        
        return jsonify({
            'query': query,
            'search_config': search_config,
            'filters': filters,
            'total_results': len(formatted_results),
            'results': formatted_results
        })
        
    except Exception as e:
        current_app.logger.error(f"Advanced search error: {str(e)}")
        return jsonify({'error': 'Advanced search failed'}), 500