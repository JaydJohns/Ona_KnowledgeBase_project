from flask import Blueprint, request, jsonify, current_app
from backend.models.document import Concept, ConceptRelation, Document, db
from backend.services.concept_analyzer import ConceptAnalyzer
from sqlalchemy import func, desc

concepts_bp = Blueprint('concepts', __name__)

@concepts_bp.route('/', methods=['GET'])
def get_concepts():
    """Get all concepts with optional filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'frequency')  # frequency, name, created_date
        
        query = Concept.query
        
        if category:
            query = query.filter(Concept.category == category)
        
        if search:
            query = query.filter(Concept.name.contains(search.lower()))
        
        # Apply sorting
        if sort_by == 'frequency':
            query = query.order_by(desc(Concept.frequency))
        elif sort_by == 'name':
            query = query.order_by(Concept.name)
        elif sort_by == 'created_date':
            query = query.order_by(desc(Concept.created_date))
        
        concepts = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'concepts': [concept.to_dict() for concept in concepts.items],
            'total': concepts.total,
            'pages': concepts.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        current_app.logger.error(f"Get concepts error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@concepts_bp.route('/<int:concept_id>', methods=['GET'])
def get_concept(concept_id):
    """Get a specific concept with its relationships and documents"""
    try:
        concept = Concept.query.get_or_404(concept_id)
        
        # Get related concepts
        relations = ConceptRelation.query.filter(
            (ConceptRelation.concept1_id == concept_id) |
            (ConceptRelation.concept2_id == concept_id)
        ).all()
        
        related_concepts = []
        for relation in relations:
            if relation.concept1_id == concept_id:
                related_concept = relation.concept2
            else:
                related_concept = relation.concept1
            
            related_concepts.append({
                'concept': related_concept.to_dict(),
                'relation_type': relation.relation_type,
                'strength': relation.strength
            })
        
        # Get documents containing this concept
        documents = [
            {
                'id': doc.id,
                'title': doc.title,
                'summary': doc.summary,
                'upload_date': doc.upload_date.isoformat() if doc.upload_date else None
            }
            for doc in concept.documents
        ]
        
        return jsonify({
            'concept': concept.to_dict(),
            'related_concepts': related_concepts,
            'documents': documents
        })
        
    except Exception as e:
        current_app.logger.error(f"Get concept error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@concepts_bp.route('/categories', methods=['GET'])
def get_concept_categories():
    """Get all concept categories with counts"""
    try:
        categories = db.session.query(
            Concept.category,
            func.count(Concept.id).label('count')
        ).group_by(Concept.category).order_by(desc('count')).all()
        
        return jsonify({
            'categories': [
                {'name': cat[0], 'count': cat[1]}
                for cat in categories
            ]
        })
        
    except Exception as e:
        current_app.logger.error(f"Get concept categories error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@concepts_bp.route('/graph', methods=['GET'])
def get_concept_graph():
    """Get concept relationship graph"""
    try:
        min_strength = request.args.get('min_strength', 0.3, type=float)
        category = request.args.get('category')
        
        analyzer = ConceptAnalyzer()
        graph = analyzer.build_concept_graph(min_strength=min_strength)
        
        # Filter by category if specified
        if category:
            # Filter nodes
            category_nodes = [node for node in graph['nodes'] if node['category'] == category]
            category_node_ids = {node['id'] for node in category_nodes}
            
            # Filter edges to only include connections between category nodes
            category_edges = [
                edge for edge in graph['edges']
                if edge['source'] in category_node_ids and edge['target'] in category_node_ids
            ]
            
            graph = {
                'nodes': category_nodes,
                'edges': category_edges
            }
        
        return jsonify(graph)
        
    except Exception as e:
        current_app.logger.error(f"Get concept graph error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@concepts_bp.route('/analyze/<int:document_id>', methods=['POST'])
def analyze_document_concepts(document_id):
    """Analyze and extract concepts from a document"""
    try:
        document = Document.query.get_or_404(document_id)
        
        if document.processing_status != 'completed':
            return jsonify({'error': 'Document not yet processed'}), 400
        
        analyzer = ConceptAnalyzer()
        concepts = analyzer.process_document_concepts(document_id)
        
        return jsonify({
            'message': f'Extracted {len(concepts)} concepts from document',
            'concepts': [concept.to_dict() for concept in concepts]
        })
        
    except Exception as e:
        current_app.logger.error(f"Analyze document concepts error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@concepts_bp.route('/relations', methods=['GET'])
def get_concept_relations():
    """Get concept relationships"""
    try:
        concept_id = request.args.get('concept_id', type=int)
        relation_type = request.args.get('relation_type')
        min_strength = request.args.get('min_strength', 0.0, type=float)
        
        query = ConceptRelation.query
        
        if concept_id:
            query = query.filter(
                (ConceptRelation.concept1_id == concept_id) |
                (ConceptRelation.concept2_id == concept_id)
            )
        
        if relation_type:
            query = query.filter(ConceptRelation.relation_type == relation_type)
        
        if min_strength > 0:
            query = query.filter(ConceptRelation.strength >= min_strength)
        
        relations = query.order_by(desc(ConceptRelation.strength)).all()
        
        return jsonify({
            'relations': [relation.to_dict() for relation in relations]
        })
        
    except Exception as e:
        current_app.logger.error(f"Get concept relations error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@concepts_bp.route('/similar/<int:document_id>', methods=['GET'])
def get_similar_documents(document_id):
    """Get documents similar to the given document based on shared concepts"""
    try:
        limit = request.args.get('limit', 5, type=int)
        
        analyzer = ConceptAnalyzer()
        similar_docs = analyzer.suggest_related_documents(document_id, limit=limit)
        
        return jsonify({
            'similar_documents': similar_docs
        })
        
    except Exception as e:
        current_app.logger.error(f"Get similar documents error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@concepts_bp.route('/stats', methods=['GET'])
def get_concept_stats():
    """Get concept statistics"""
    try:
        total_concepts = Concept.query.count()
        total_relations = ConceptRelation.query.count()
        
        # Top categories
        top_categories = db.session.query(
            Concept.category,
            func.count(Concept.id).label('count')
        ).group_by(Concept.category).order_by(desc('count')).limit(10).all()
        
        # Most frequent concepts
        top_concepts = Concept.query.order_by(desc(Concept.frequency)).limit(10).all()
        
        # Relation type distribution
        relation_types = db.session.query(
            ConceptRelation.relation_type,
            func.count(ConceptRelation.id).label('count')
        ).group_by(ConceptRelation.relation_type).all()
        
        return jsonify({
            'total_concepts': total_concepts,
            'total_relations': total_relations,
            'top_categories': [
                {'category': cat[0], 'count': cat[1]}
                for cat in top_categories
            ],
            'top_concepts': [concept.to_dict() for concept in top_concepts],
            'relation_types': [
                {'type': rt[0], 'count': rt[1]}
                for rt in relation_types
            ]
        })
        
    except Exception as e:
        current_app.logger.error(f"Get concept stats error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@concepts_bp.route('/merge', methods=['POST'])
def merge_concepts():
    """Merge two concepts into one"""
    try:
        data = request.get_json()
        primary_id = data.get('primary_id')
        secondary_id = data.get('secondary_id')
        
        if not primary_id or not secondary_id:
            return jsonify({'error': 'Both primary_id and secondary_id required'}), 400
        
        primary_concept = Concept.query.get_or_404(primary_id)
        secondary_concept = Concept.query.get_or_404(secondary_id)
        
        # Merge frequency
        primary_concept.frequency += secondary_concept.frequency
        
        # Transfer document relationships
        for doc in secondary_concept.documents:
            if doc not in primary_concept.documents:
                primary_concept.documents.append(doc)
        
        # Transfer concept relationships
        relations_to_update = ConceptRelation.query.filter(
            (ConceptRelation.concept1_id == secondary_id) |
            (ConceptRelation.concept2_id == secondary_id)
        ).all()
        
        for relation in relations_to_update:
            if relation.concept1_id == secondary_id:
                relation.concept1_id = primary_id
            else:
                relation.concept2_id = primary_id
        
        # Delete secondary concept
        db.session.delete(secondary_concept)
        db.session.commit()
        
        return jsonify({
            'message': 'Concepts merged successfully',
            'merged_concept': primary_concept.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Merge concepts error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500