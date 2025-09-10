from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import RequestEntityTooLarge
from backend.models.document import Document, db
from backend.services.document_processor import DocumentProcessor
import os

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process a document"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        processor = DocumentProcessor()
        
        # Process the document
        document = processor.process_document(file)
        
        return jsonify({
            'message': 'Document uploaded and processed successfully',
            'document': document.to_dict()
        }), 201
        
    except RequestEntityTooLarge:
        return jsonify({'error': 'File too large'}), 413
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Document upload error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/', methods=['GET'])
def get_documents():
    """Get all documents with optional filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        file_type = request.args.get('file_type')
        
        query = Document.query
        
        if status:
            query = query.filter(Document.processing_status == status)
        if file_type:
            query = query.filter(Document.file_type.contains(file_type))
        
        documents = query.order_by(Document.upload_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'documents': [doc.to_dict() for doc in documents.items],
            'total': documents.total,
            'pages': documents.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        current_app.logger.error(f"Get documents error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/<int:document_id>', methods=['GET'])
def get_document(document_id):
    """Get a specific document by ID"""
    try:
        document = Document.query.get_or_404(document_id)
        return jsonify({'document': document.to_dict()})
    except Exception as e:
        current_app.logger.error(f"Get document error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/<int:document_id>/content', methods=['GET'])
def get_document_content(document_id):
    """Get document content"""
    try:
        document = Document.query.get_or_404(document_id)
        return jsonify({
            'document_id': document.id,
            'title': document.title,
            'content': document.content,
            'summary': document.summary
        })
    except Exception as e:
        current_app.logger.error(f"Get document content error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document"""
    try:
        document = Document.query.get_or_404(document_id)
        
        # Delete associated files
        upload_path = os.path.join('uploads', document.filename)
        processed_path = os.path.join('processed_docs', f"{document.id}_{document.filename}.txt")
        
        for path in [upload_path, processed_path]:
            if os.path.exists(path):
                os.remove(path)
        
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'message': 'Document deleted successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Delete document error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/stats', methods=['GET'])
def get_document_stats():
    """Get document statistics"""
    try:
        total_docs = Document.query.count()
        completed_docs = Document.query.filter(Document.processing_status == 'completed').count()
        failed_docs = Document.query.filter(Document.processing_status == 'failed').count()
        processing_docs = Document.query.filter(Document.processing_status == 'processing').count()
        
        total_words = db.session.query(db.func.sum(Document.word_count)).scalar() or 0
        
        file_types = db.session.query(
            Document.file_type, 
            db.func.count(Document.id)
        ).group_by(Document.file_type).all()
        
        return jsonify({
            'total_documents': total_docs,
            'completed_documents': completed_docs,
            'failed_documents': failed_docs,
            'processing_documents': processing_docs,
            'total_words': total_words,
            'file_types': [{'type': ft[0], 'count': ft[1]} for ft in file_types]
        })
        
    except Exception as e:
        current_app.logger.error(f"Get document stats error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500