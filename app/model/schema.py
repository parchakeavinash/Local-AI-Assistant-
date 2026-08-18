from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal,Optional


class AnswerResponse(BaseModel):
    
    answer: str = Field(..., description="The direct answer to the user's question. Be concise and factual.")

    confidence: float = Field(
        ..., 
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0 to 1.0)"
    )

    sources: list[str] = Field(
        ...,
        description="List of source filenames (e.g., 'notebook.md')"
    )

    reasoning: Optional[str] = Field(
        None,
        description=("Optional: Chain-of-thought step-by-step thinking that produced the answer.")
    )

    def is_confidence(self, threshold:float=0.5) -> bool:
        """Returns True if the model is confident enough to trust this answer."""
        return self.confidence>=threshold

    

    def __str__(self)->str:
        return (
            f'Answer : {self.answer}\n'
            f'confidence : {self.confidence:.2f}\n'
             f"Sources   : {len(self.sources)} chunk(s) referenced"
            
        )



class DocumentChunk(BaseModel):

    chunk_id: str = Field(..., description="Unique ID in ChromaDB")
    content: str = Field(..., description="The actual text of this chunk")
    source_file: str = Field(..., description="Filename this chunk came from")
    chunk_index: int = Field(..., description="Position of this chunk in the source file")
    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Cosine similarity score from ChromaDB (1.0 = perfect match)",
    )


    def __str__(self)->str:
        return (
            f'Chunk ID    : {self.chunk_id}\n'
            f'Source      : {self.source_file}\n'
            f'Index       : {self.chunk_index}\n'
            f'Similarity : {self.similarity_score:.4f}\n'
            f'Content Preview : {self.content[:60]}...'
        )


class BenchmarkResult(BaseModel):

    model_name : str = Field(..., description='which ollama model was used')
    question_id : int  = Field(..., description = 'index of the question in the quesiton bank')
    question: str=Field(..., description='The full text of the question asked')
    category: str= Field(..., description='Question category:factual/conceptual/application/multi_hop/out_of_context')


    answer: str = Field(..., description = 'The answer the model gave')
    confidence: float = Field(..., ge=0.0, le=1.0, description='Model self reported confidence')


    latency_ms:float = Field(..., description ='Total time from prmopt send to valid answer received(millseconds)')
    ram_used_mb:float = Field(..., description='RAM consumed by this single query MB delta before/afeter')
    
    retries : int =Field(..., ge=0, description = 'How many retry attempts were needed ( 0 = first try succeded)')
    success: bool = Field(..., description = 'True if a valid structured response was produced within max_retrives')


    # manual quality rating 
    quality_score: Optional[int] = Field(None, ge=1,le=5,description='Manuall quality rating 1-5(fill this in after reviewing results)')

    def __str__(self)->str:
        status = '[PASS]' if self.success else ['FAIL']
        return(
            f"[Q{self.question_id:02d}] {status} | "
            f"{self.latency_ms:.0f}ms | {self.ram_used_mb:.1f}MB | "
            f"{self.retries} retries | conf: {self.confidence:.0%}"
        )
    

class ConversationTurn(BaseModel):
    """Stores one Q&A pair for multi-turn conversation history."""

    role: str = Field(..., description='user or assistant')
    content: str = Field(..., description='The message text')

    def to_dict(self)->dict:
        return{
            'role':self.role,
            'content':self.content
        }
        