from typing import TypedDict, List, Dict, Any


class RAGState(TypedDict):
    query: str
    docs: List[Dict[str, Any]]
    answer: str
    verification: Dict[str, Any]
    confidence: str


#This is the shared memory across nodes.

# LangGraph requires a TypedDict or dataclass

# This defines the contract between nodes

# This is exactly how production LangGraph systems are built