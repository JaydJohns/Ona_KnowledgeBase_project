from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed_date = db.Column(db.DateTime)
    
    # Content fields
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    summary = db.Column(db.Text)
    word_count = db.Column(db.Integer)
    page_count = db.Column(db.Integer)
    
    # Processing status
    processing_status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    error_message = db.Column(db.Text)
    
    # Metadata
    metadata = db.Column(db.Text)  # JSON string for flexible metadata
    
    # Relationships
    concepts = db.relationship('Concept', secondary='document_concepts', back_populates='documents')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'processed_date': self.processed_date.isoformat() if self.processed_date else None,
            'title': self.title,
            'summary': self.summary,
            'word_count': self.word_count,
            'page_count': self.page_count,
            'processing_status': self.processing_status,
            'metadata': json.loads(self.metadata) if self.metadata else {}
        }

class Concept(db.Model):
    __tablename__ = 'concepts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    frequency = db.Column(db.Integer, default=1)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('Document', secondary='document_concepts', back_populates='concepts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'frequency': self.frequency,
            'created_date': self.created_date.isoformat() if self.created_date else None
        }

# Association table for many-to-many relationship
document_concepts = db.Table('document_concepts',
    db.Column('document_id', db.Integer, db.ForeignKey('documents.id'), primary_key=True),
    db.Column('concept_id', db.Integer, db.ForeignKey('concepts.id'), primary_key=True),
    db.Column('relevance_score', db.Float, default=0.0),
    db.Column('context', db.Text)  # Context where concept appears
)

class ConceptRelation(db.Model):
    __tablename__ = 'concept_relations'
    
    id = db.Column(db.Integer, primary_key=True)
    concept1_id = db.Column(db.Integer, db.ForeignKey('concepts.id'), nullable=False)
    concept2_id = db.Column(db.Integer, db.ForeignKey('concepts.id'), nullable=False)
    relation_type = db.Column(db.String(100))  # 'related', 'synonym', 'antonym', 'parent', 'child'
    strength = db.Column(db.Float, default=0.0)  # Relationship strength 0-1
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    concept1 = db.relationship('Concept', foreign_keys=[concept1_id])
    concept2 = db.relationship('Concept', foreign_keys=[concept2_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'concept1': self.concept1.to_dict() if self.concept1 else None,
            'concept2': self.concept2.to_dict() if self.concept2 else None,
            'relation_type': self.relation_type,
            'strength': self.strength,
            'created_date': self.created_date.isoformat() if self.created_date else None
        }