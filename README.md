
# Second Brain Knowledge Repository

A modern knowledge management system for Human-Computer Interaction (HCI) and general documents, featuring intelligent document organization, concept extraction, advanced search, analytics, and interactive visualization.

## 🚀 Features

### Document Management
- **Multi-format Upload**: PDF, Word (.pdf, .docx, .doc), Text, PowerPoint, Excel
- **Automatic Processing**: Text extraction, content/summary generation, metadata
- **Smart Organization**: Tagging, categorization, and file type detection
- **Pagination & Detail Views**: Browse, search, and view full document details

### Concept Extraction & Knowledge Graph
- **HCI-Focused**: Pre-trained with HCI terminology
- **Concept Detection**: Pattern, NLP, and statistical methods
- **Relationship Mapping**: Automatic concept graph and category classification
- **Interactive Visualization**: Explore concepts and their relationships

### Advanced Search
- **Hybrid Search**: Keyword, semantic, and concept-based
- **Suggestions**: Auto-complete and query suggestions
- **Filters**: By file type, date, concepts, and more
- **Result Highlighting**: Context-aware highlights and matched concepts

### Analytics & Dashboard
- **Statistics**: Document and concept counts, file type breakdowns, trends
- **Dashboard**: Overview of repository health and activity

### Web Interface
- **Modern React UI**: Responsive, mobile-friendly, and accessible
- **Component Library**: Reusable, clean UI components
- **Real-time Feedback**: Progress tracking, error handling, and notifications

## 🏗️ Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Frontend   │<──>│   Backend    │<──>│   Database   │
│   (React)    │    │   (Flask)    │    │   (SQLite)   │
└──────────────┘    └──────────────┘    └──────────────┘
```

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Backend Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Ona_KnowledgeBase_project/second_brain_package
   ```
2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Start the backend server**
   ```bash
   python app.py
   ```
   The API will be available at `http://localhost:5000`

### Frontend Setup
1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```
2. **Install Node.js dependencies**
   ```bash
   npm install
   ```
3. **Create a .env file**
   ```env
   REACT_APP_API_URL=http://localhost:5000/api
   ```
4. **Start the development server**
   ```bash
   npm start
   ```
   The web interface will be available at `http://localhost:3000`

### Docker Setup (Optional)
See INSTALLATION.md for full Docker instructions.

### Test Interface
For quick API testing:
```
http://localhost:5000/static/test.html
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React)       │◄──►│   (Flask)       │◄──►│   (SQLite)      │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • Document API  │    │ • Documents     │
│ • Upload        │    │ • Concept API   │    │ • Concepts      │
│ • Search        │    │ • Search API    │    │ • Relations     │
│ • Visualization │    │ • Processing    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Backend Components
- **Flask API**: RESTful endpoints for all operations
- **Document Processor**: PDF/Word text extraction and analysis
- **Concept Analyzer**: HCI-focused concept detection and linking
- **Search Engine**: Multi-modal search with TF-IDF and embeddings
- **Content Extractor**: NLP pipeline for text processing

### Frontend Components
- **React Application**: Modern single-page application
- **Component Library**: Reusable UI components
- **State Management**: React Query for data fetching and caching
- **Visualization**: Force-directed graph with D3.js integration

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- Node.js 16+ (for frontend development)
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd second-brain-knowledge-repository
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server**
   ```bash
   python app.py
   ```
   
   The API will be available at `http://localhost:5000`

### Frontend Setup (Optional)

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```
   
   The web interface will be available at `http://localhost:3000`

### Test Interface

For quick testing without setting up the full frontend:

1. **Access the test interface**
   ```
   http://localhost:5000/static/test.html
   ```

2. **Test API endpoints directly**
   ```bash
   # Get system status
   curl http://localhost:5000/
   
   # Get document statistics
   curl http://localhost:5000/api/documents/stats
   
   # Search documents
   curl "http://localhost:5000/api/search?q=usability"
   ```

## 📖 Usage Guide

### 1. Uploading Documents

**Via Web Interface:**
1. Navigate to the Upload page
2. Drag and drop files or click to select
3. Supported formats: PDF, DOCX, DOC
4. Monitor upload progress and processing status

**Via API:**
```bash
curl -X POST -F "file=@document.pdf" http://localhost:5000/api/documents/upload
```

### 2. Searching Documents

**Basic Search:**
- Enter keywords in the search box
- Use quotes for exact phrases: `"user interface"`
- Search across titles, content, and summaries

**Advanced Search:**
- Filter by file type, date range, or concepts
- Use different search modes: keyword, semantic, concept, or hybrid
- Boost recent documents or title matches

**Search Examples:**
```
usability testing          # Find documents about usability testing
"heuristic evaluation"     # Exact phrase search
accessibility AND mobile   # Boolean search
```

### 3. Exploring Concepts

**Concept Browser:**
- View all extracted concepts organized by category
- Sort by frequency, name, or creation date
- Filter by HCI categories (usability, accessibility, etc.)

**Knowledge Graph:**
- Interactive visualization of concept relationships
- Adjust minimum relationship strength
- Color-coded by concept category
- Click nodes to explore connections

### 4. Document Analysis

**Automatic Processing:**
- Text extraction from PDF and Word documents
- Concept detection using HCI terminology
- Relationship discovery between concepts
- Readability analysis and statistics

**Manual Analysis:**
- Re-analyze documents to update concepts
- Merge similar concepts
- Explore document similarities

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=sqlite:///second_brain.db

# Security
SECRET_KEY=your-secret-key-here

# File Upload
MAX_CONTENT_LENGTH=52428800  # 50MB

# Processing
ENABLE_EMBEDDINGS=true
ENABLE_SPACY=true
```

### HCI Concept Categories

The system includes pre-defined HCI concept categories:

- **Interaction Design**: UI, UX, interface design, wireframes
- **Usability**: Testing methods, heuristics, evaluation
- **Cognitive Psychology**: Mental models, cognitive load, attention
- **Input Methods**: Mouse, keyboard, touch, gesture, voice
- **Evaluation Methods**: User studies, A/B testing, analytics
- **Design Principles**: Affordance, feedback, consistency
- **Accessibility**: WCAG, screen readers, inclusive design
- **Mobile Computing**: Responsive design, touch interaction
- **Social Computing**: Collaboration, social media, communities
- **Visualization**: Information visualization, data representation

## 📊 API Reference

### Documents

```http
GET    /api/documents              # List documents
POST   /api/documents/upload       # Upload document
GET    /api/documents/{id}         # Get document details
GET    /api/documents/{id}/content # Get document content
DELETE /api/documents/{id}         # Delete document
GET    /api/documents/stats        # Get statistics
```

### Concepts

```http
GET    /api/concepts               # List concepts
GET    /api/concepts/{id}          # Get concept details
GET    /api/concepts/categories    # List categories
GET    /api/concepts/graph         # Get concept graph
POST   /api/concepts/analyze/{id}  # Analyze document concepts
GET    /api/concepts/relations     # Get relationships
GET    /api/concepts/similar/{id}  # Get similar documents
POST   /api/concepts/merge         # Merge concepts
```

### Search

```http
GET    /api/search                 # Search documents
GET    /api/search/suggestions     # Get search suggestions
GET    /api/search/analytics       # Get search analytics
POST   /api/search/reindex         # Rebuild search index
GET    /api/search/similar         # Find similar documents
POST   /api/search/advanced        # Advanced search
```

## 🛠️ Development

### Project Structure

```
second-brain-knowledge-repository/
├── backend/
│   ├── api/           # API endpoints
│   ├── models/        # Database models
│   ├── services/      # Business logic
│   └── utils/         # Utility functions
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   └── services/    # API services
│   └── public/          # Static assets
├── uploads/           # Uploaded documents
├── processed_docs/    # Processed content
├── static/           # Static files
├── app.py            # Main application
└── requirements.txt  # Python dependencies
```

### Adding New Features

1. **Backend**: Add new API endpoints in `backend/api/`
2. **Frontend**: Create new components in `frontend/src/components/`
3. **Models**: Define new database models in `backend/models/`
4. **Services**: Add business logic in `backend/services/`

### Testing

```bash
# Run backend tests
python -m pytest tests/

# Run frontend tests
cd frontend && npm test

# Test API endpoints
curl -X GET http://localhost:5000/health
```

## 🔍 Troubleshooting

### Common Issues

**Upload Fails:**
- Check file size (max 50MB)
- Verify file format (PDF, DOCX, DOC)
- Ensure sufficient disk space

**Concept Extraction Not Working:**
- Install required NLP libraries
- Check document text quality
- Verify HCI terminology database

**Search Returns No Results:**
- Rebuild search index: `POST /api/search/reindex`
- Check document processing status
- Verify search query syntax

**Frontend Not Loading:**
- Check if backend is running on port 5000
- Verify CORS configuration
- Check browser console for errors

### Performance Optimization

**Large Document Collections:**
- Use PostgreSQL instead of SQLite
- Enable database indexing
- Implement pagination for large result sets

**Slow Search:**
- Rebuild search indexes regularly
- Use semantic search sparingly
- Implement result caching

## 📈 Roadmap

### Planned Features

- [ ] **Enhanced NLP**: Integration with advanced language models
- [ ] **Collaboration**: Multi-user support and sharing
- [ ] **Export**: PDF reports and data export
- [ ] **Integration**: Zotero, Mendeley, and citation managers
- [ ] **Analytics**: Advanced usage analytics and insights
- [ ] **Mobile App**: Native mobile applications
- [ ] **Cloud Sync**: Cloud storage and synchronization

### Version History

- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Enhanced concept extraction and visualization
- **v1.2.0**: Advanced search and filtering capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Human-Computer Interaction research community
- Open source libraries and frameworks used
- Contributors and testers

## 📞 Support

For questions, issues, or feature requests:
- Create an issue on GitHub
- Check the troubleshooting guide
- Review the API documentation

---

**Built with ❤️ for the HCI research community**