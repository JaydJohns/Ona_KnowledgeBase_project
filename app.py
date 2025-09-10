from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from backend.models.document import db
from backend.api.documents import documents_bp
from backend.api.concepts import concepts_bp
from backend.api.search import search_bp
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///second_brain.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    app.register_blueprint(concepts_bp, url_prefix='/api/concepts')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Second Brain Knowledge Repository API',
            'version': '1.0.0',
            'endpoints': {
                'documents': '/api/documents',
                'concepts': '/api/concepts',
                'search': '/api/search'
            }
        })
    
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy'})
    
    # Serve static files for frontend
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory('static', filename)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)