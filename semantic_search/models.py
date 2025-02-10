from pydantic import BaseModel
from typing import Optional, List

class DocumentUpload(BaseModel):
 """
 Data model for uploading a document.
 """
 content: str
 title: Optional[str] = None


class DocumentResponse(BaseModel):
 """
 Data model for representing a stored document.
 """
 id: str
 content: str
 title: Optional[str] = None


class QueryRequest(BaseModel):
 """
 Data model for a search query.
 """
 query: str
 n_results: Optional[int] = 5  # Default number of results


class QueryResponse(BaseModel):
 """
 Data model for search query responses.
 """
 results: List[DocumentResponse]