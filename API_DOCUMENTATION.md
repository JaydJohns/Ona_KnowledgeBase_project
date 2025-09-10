# API Documentation

The Second Brain Knowledge Repository provides a comprehensive REST API for managing documents, concepts, and search functionality.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, the API does not require authentication. For production deployments, consider implementing:
- API key authentication
- JWT tokens
- OAuth 2.0

## Response Format

All API responses follow a consistent JSON format:

### Success Response
```json
{
  "data": { ... },
  "message": "Success message",
  "status": "success"
}
```

### Error Response
```json
{
  "error": "Error description",
  "status": "error",
  "code": 400
}
```

## Rate Limiting

- **Default**: 100 requests per minute per IP
- **Upload**: 10 requests per minute per IP
- **Search**: 50 requests per minute per IP

## Documents API

### List Documents
Retrieve a paginated list of documents.

```http
GET /api/documents
```

#### Parameters
| Parameter   | Type    | Default | Description                      |
|-------------|---------|---------|----------------------------------|
| `page`      | integer | 1       | Page number                      |
| `per_page`  | integer | 20      | Items per page (max 100)         |
| `status`    | string  | -       | Filter by processing status      |
| `file_type` | string  | -       | Filter by file type              |

#### Example Request
```bash
curl "http://localhost:5000/api/documents?page=1&per_page=10&status=completed"
```

#### Example Response
```json
{
  "documents": [
    {
      "id": 1,
      "filename": "hci_principles_20231201_abc123.pdf",
      "original_filename": "HCI Principles.pdf",
      "file_type": "application/pdf",
      "file_size": 1024000,
      "upload_date": "2023-12-01T10:30:00Z",
      "processed_date": "2023-12-01T10:31:15Z",
      "title": "Human-Computer Interaction Principles",
      "summary": "An overview of fundamental HCI principles...",
      "word_count": 1250,
      "page_count": 8,
      "processing_status": "completed"
    }
  ],
  "total": 25,
  "pages": 3,
  "current_page": 1,
  "per_page": 10
}
```

### Upload Document
Upload a new document for processing.

```http
POST /api/documents/upload
```

#### Request
- **Content-Type**: `multipart/form-data`
- **Body**: File upload with key `file`

#### Supported Formats
- PDF (`.pdf`)
- Microsoft Word (`.docx`, `.doc`)
- Text (`.txt`)
- PowerPoint (`.ppt`, `.pptx`)
- Excel (`.xls`, `.xlsx`)
- Maximum size: 50MB

#### Example Request
```bash
curl -X POST \
  -F "file=@document.pdf" \
  http://localhost:5000/api/documents/upload
```

#### Example Response

```json
{
  "message": "Document uploaded and processed successfully",
  "document": {
    "id": 26,
    "filename": "document_20231201_def456.pdf",
    "original_filename": "document.pdf",
    "processing_status": "processing",
    "upload_date": "2023-12-01T11:00:00Z"
  }
}
```

### Get Document

Retrieve details for a specific document.

```http
GET /api/documents/{id}
```

#### Example Request

```bash
curl http://localhost:5000/api/documents/1
```

#### Example Response

```json
{
  "document": {
    "id": 1,
    "filename": "hci_principles_20231201_abc123.pdf",
    "original_filename": "HCI Principles.pdf",
    "file_type": "application/pdf",
    "file_size": 1024000,
    "upload_date": "2023-12-01T10:30:00Z",
    "processed_date": "2023-12-01T10:31:15Z",
    "title": "Human-Computer Interaction Principles",
    "summary": "An overview of fundamental HCI principles...",
    "word_count": 1250,
    "page_count": 8,
    "processing_status": "completed",
    "metadata": {
      "author": "Dr. Jane Smith",
      "creation_date": "2023-11-15",
      "language": "en"
    }
  }
}
```

### Get Document Content

Retrieve the full text content of a document.

```http
GET /api/documents/{id}/content
```

#### Example Request

```bash
curl http://localhost:5000/api/documents/1/content
```

#### Example Response

```json
{
  "document_id": 1,
  "title": "Human-Computer Interaction Principles",
  "content": "Human-Computer Interaction (HCI) is a multidisciplinary field...",
  "summary": "An overview of fundamental HCI principles..."
}
```

### Delete Document

Delete a document and its associated data.

```http
DELETE /api/documents/{id}
```

#### Example Request

```bash
curl -X DELETE http://localhost:5000/api/documents/1
```

#### Example Response

```json
{
  "message": "Document deleted successfully"
}
```

### Document Statistics

Get statistics about the document collection.

```http
GET /api/documents/stats
```

#### Example Response

```json
{
  "total_documents": 25,
  "completed_documents": 23,
  "failed_documents": 1,
  "processing_documents": 1,
  "total_words": 125000,
  "file_types": [
    {
      "type": "application/pdf",
      "count": 18
    },
    {
      "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "count": 7
    }
  ]
}
```

## Concepts API

### List Concepts

Retrieve a list of extracted concepts.

```http
GET /api/concepts
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 50 | Items per page |
| `category` | string | - | Filter by category |
| `search` | string | - | Search concept names |
| `sort_by` | string | frequency | Sort by: frequency, name, created_date |

#### Example Request

```bash
curl "http://localhost:5000/api/concepts?category=usability&sort_by=frequency"
```

#### Example Response

```json
{
  "concepts": [
    {
      "id": 1,
      "name": "usability testing",
      "description": "Method for evaluating user interface effectiveness",
      "category": "usability",
      "frequency": 15,
      "created_date": "2023-12-01T10:31:20Z"
    }
  ],
  "total": 150,
  "pages": 3,
  "current_page": 1,
  "per_page": 50
}
```

### Get Concept

Retrieve details for a specific concept including relationships.

```http
GET /api/concepts/{id}
```

#### Example Response

```json
{
  "concept": {
    "id": 1,
    "name": "usability testing",
    "description": "Method for evaluating user interface effectiveness",
    "category": "usability",
    "frequency": 15,
    "created_date": "2023-12-01T10:31:20Z"
  },
  "related_concepts": [
    {
      "concept": {
        "id": 2,
        "name": "heuristic evaluation",
        "category": "evaluation_methods"
      },
      "relation_type": "related",
      "strength": 0.8
    }
  ],
  "documents": [
    {
      "id": 1,
      "title": "Usability Testing Methods",
      "summary": "Comprehensive guide to usability testing...",
      "upload_date": "2023-12-01T10:30:00Z"
    }
  ]
}
```

### Concept Categories

Get all concept categories with counts.

```http
GET /api/concepts/categories
```

#### Example Response

```json
{
  "categories": [
    {
      "name": "usability",
      "count": 25
    },
    {
      "name": "interaction_design",
      "count": 18
    },
    {
      "name": "accessibility",
      "count": 12
    }
  ]
}
```

### Concept Graph

Get concept relationship graph data.

```http
GET /api/concepts/graph
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_strength` | float | 0.3 | Minimum relationship strength |
| `category` | string | - | Filter by category |

#### Example Response

```json
{
  "nodes": [
    {
      "id": 1,
      "name": "usability testing",
      "category": "usability",
      "frequency": 15,
      "size": 20
    }
  ],
  "edges": [
    {
      "source": 1,
      "target": 2,
      "type": "related",
      "strength": 0.8,
      "width": 4
    }
  ]
}
```

### Analyze Document Concepts

Extract and analyze concepts from a specific document.

```http
POST /api/concepts/analyze/{document_id}
```

#### Example Response

```json
{
  "message": "Extracted 12 concepts from document",
  "concepts": [
    {
      "id": 1,
      "name": "user interface",
      "category": "interaction_design",
      "frequency": 8
    }
  ]
}
```

### Concept Relations

Get concept relationships with filtering options.

```http
GET /api/concepts/relations
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `concept_id` | integer | Filter by specific concept |
| `relation_type` | string | Filter by relation type |
| `min_strength` | float | Minimum relationship strength |

### Similar Documents

Find documents similar to a given document based on shared concepts.

```http
GET /api/concepts/similar/{document_id}
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 5 | Maximum number of results |

#### Example Response

```json
{
  "similar_documents": [
    {
      "id": 5,
      "title": "Advanced Usability Methods",
      "summary": "In-depth exploration of usability testing...",
      "filename": "advanced_usability.pdf",
      "word_count": 2500,
      "upload_date": "2023-11-28T14:20:00Z",
      "shared_concepts": 8
    }
  ]
}
```

### Concept Statistics

Get statistics about concepts and relationships.

```http
GET /api/concepts/stats
```

#### Example Response

```json
{
  "total_concepts": 150,
  "total_relations": 89,
  "top_categories": [
    {
      "category": "usability",
      "count": 25
    }
  ],
  "top_concepts": [
    {
      "id": 1,
      "name": "user interface",
      "frequency": 45
    }
  ],
  "relation_types": [
    {
      "type": "related",
      "count": 65
    },
    {
      "type": "synonym",
      "count": 24
    }
  ]
}
```

### Merge Concepts

Merge two concepts into one.

```http
POST /api/concepts/merge
```

#### Request Body

```json
{
  "primary_id": 1,
  "secondary_id": 2
}
```

#### Example Response

```json
{
  "message": "Concepts merged successfully",
  "merged_concept": {
    "id": 1,
    "name": "user interface",
    "frequency": 25
  }
}
```

## Search API

### Search Documents

Search across documents using various methods.

```http
GET /api/search
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | string | **required** | Search query |
| `type` | string | hybrid | Search type: keyword, semantic, concept, hybrid |
| `limit` | integer | 20 | Maximum results |
| `file_type` | string | - | Filter by file type |
| `start_date` | string | - | Filter by upload date (ISO format) |
| `end_date` | string | - | Filter by upload date (ISO format) |
| `concepts` | string | - | Comma-separated concept IDs |
| `min_words` | integer | - | Minimum word count |
| `max_words` | integer | - | Maximum word count |

#### Example Request

```bash
curl "http://localhost:5000/api/search?q=usability%20testing&type=hybrid&limit=10"
```

#### Example Response

```json
{
  "query": "usability testing",
  "search_type": "hybrid",
  "total_results": 8,
  "results": [
    {
      "document": {
        "id": 1,
        "title": "Usability Testing Methods",
        "summary": "Comprehensive guide to usability testing...",
        "filename": "usability_methods.pdf",
        "file_type": "application/pdf",
        "word_count": 2500,
        "upload_date": "2023-12-01T10:30:00Z",
        "processed_date": "2023-12-01T10:31:15Z"
      },
      "score": 0.95,
      "search_type": "hybrid",
      "search_methods": ["keyword", "semantic"],
      "highlights": [
        {
          "source": "title",
          "text": "<mark>Usability Testing</mark> Methods",
          "position": 0
        },
        {
          "source": "content",
          "text": "...effective <mark>usability testing</mark> requires...",
          "position": 156
        }
      ]
    }
  ],
  "filters_applied": {
    "file_type": null,
    "date_range": null,
    "concepts": null
  }
}
```

### Search Suggestions

Get search query suggestions and auto-completions.

```http
GET /api/search/suggestions
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Partial query |
| `limit` | integer | Maximum suggestions (default: 10) |

#### Example Response

```json
{
  "suggestions": [
    {
      "text": "usability testing",
      "type": "concept",
      "frequency": 15
    },
    {
      "text": "Usability Testing Methods",
      "type": "title",
      "document_id": 1
    }
  ]
}
```

### Search Analytics

Get search system analytics and statistics.

```http
GET /api/search/analytics
```

#### Example Response

```json
{
  "total_searchable_documents": 25,
  "total_concepts": 150,
  "index_status": {
    "tfidf_built": true,
    "embeddings_built": true,
    "documents_indexed": 25
  },
  "top_concepts": [
    {
      "id": 1,
      "name": "user interface",
      "frequency": 45
    }
  ]
}
```

### Reindex Documents

Rebuild search indexes for all documents.

```http
POST /api/search/reindex
```

#### Example Response

```json
{
  "message": "Search indexes rebuilt successfully",
  "analytics": {
    "total_searchable_documents": 25,
    "documents_indexed": 25
  }
}
```

### Find Similar Documents

Find documents similar to a given document using semantic search.

```http
GET /api/search/similar
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `document_id` | integer | **required** Reference document ID |
| `limit` | integer | Maximum results (default: 5) |

#### Example Response

```json
{
  "document_id": 1,
  "similar_documents": [
    {
      "document": {
        "id": 5,
        "title": "Advanced Usability Methods",
        "summary": "In-depth exploration...",
        "filename": "advanced_usability.pdf",
        "word_count": 2500,
        "upload_date": "2023-11-28T14:20:00Z"
      },
      "similarity_score": 0.87
    }
  ]
}
```

### Advanced Search

Perform advanced search with complex queries and configurations.

```http
POST /api/search/advanced
```

#### Request Body

```json
{
  "query": "usability testing methods",
  "search_config": {
    "type": "hybrid",
    "boost_title": true,
    "boost_recent": true
  },
  "filters": {
    "file_type": "application/pdf",
    "date_range": {
      "start": "2023-01-01",
      "end": "2023-12-31"
    },
    "concepts": [1, 5, 12],
    "min_word_count": 1000
  },
  "limit": 15
}
```

#### Example Response

```json
{
  "query": "usability testing methods",
  "search_config": {
    "type": "hybrid",
    "boost_title": true,
    "boost_recent": true
  },
  "filters": {
    "file_type": "application/pdf",
    "date_range": {
      "start": "2023-01-01",
      "end": "2023-12-31"
    },
    "concepts": [1, 5, 12],
    "min_word_count": 1000
  },
  "total_results": 12,
  "results": [
    {
      "document": {
        "id": 1,
        "title": "Usability Testing Methods",
        "summary": "Comprehensive guide...",
        "word_count": 2500
      },
      "score": 0.98,
      "search_type": "hybrid",
      "highlights": [...]
    }
  ]
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 413 | Payload Too Large - File size exceeds limit |
| 415 | Unsupported Media Type - Invalid file format |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

## Status Codes

### Document Processing Status

- `pending` - Document uploaded, waiting for processing
- `processing` - Document is being processed
- `completed` - Processing completed successfully
- `failed` - Processing failed with errors

### Search Types

- `keyword` - Traditional keyword-based search
- `semantic` - Semantic similarity search using embeddings
- `concept` - Concept-based search
- `hybrid` - Combination of multiple search methods

### Concept Categories

- `interaction_design` - UI/UX design concepts
- `usability` - Usability testing and evaluation
- `cognitive_psychology` - Cognitive science concepts
- `input_methods` - Input devices and methods
- `evaluation_methods` - Research and evaluation methods
- `design_principles` - Design principles and guidelines
- `accessibility` - Accessibility and inclusive design
- `mobile_computing` - Mobile interface design
- `social_computing` - Social and collaborative systems
- `visualization` - Information visualization

## SDK and Libraries

### Python SDK

```python
import requests

class SecondBrainAPI:
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
    
    def upload_document(self, file_path):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.base_url}/documents/upload", files=files)
        return response.json()
    
    def search(self, query, search_type="hybrid", limit=20):
        params = {'q': query, 'type': search_type, 'limit': limit}
        response = requests.get(f"{self.base_url}/search", params=params)
        return response.json()

# Usage
api = SecondBrainAPI()
result = api.upload_document("document.pdf")
search_results = api.search("usability testing")
```

### JavaScript SDK

```javascript
class SecondBrainAPI {
    constructor(baseUrl = 'http://localhost:5000/api') {
        this.baseUrl = baseUrl;
    }
    
    async uploadDocument(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.baseUrl}/documents/upload`, {
            method: 'POST',
            body: formData
        });
        
        return response.json();
    }
    
    async search(query, options = {}) {
        const params = new URLSearchParams({
            q: query,
            type: options.type || 'hybrid',
            limit: options.limit || 20,
            ...options
        });
        
        const response = await fetch(`${this.baseUrl}/search?${params}`);
        return response.json();
    }
}

// Usage
const api = new SecondBrainAPI();
const result = await api.uploadDocument(fileInput.files[0]);
const searchResults = await api.search('usability testing');
```

## Webhooks (Future Feature)

Future versions will support webhooks for real-time notifications:

- Document processing completed
- New concepts discovered
- Search index updated
- System health alerts

---

For more information, see the [main documentation](README.md) or [installation guide](INSTALLATION.md).