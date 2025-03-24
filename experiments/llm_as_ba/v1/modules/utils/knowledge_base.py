from typing import List, Dict, Any, Optional
from ..schemas import KnowledgeBase


def get_knowledge_base_entries(
    knowledge_base: KnowledgeBase,
    top_n: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Get all or some entries from the knowledge base.
    
    Args:
        knowledge_base (KnowledgeBase): The knowledge base to summarize
        top_n (Optional[int]): If specified, limit the top N entries
        
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing entries
    """
    entries = knowledge_base.entries
    
    # Take all entries or limit if top_n is specified
    if top_n is not None:
        entries = entries[:top_n]
    
    # Format the entries for display
    summary = []
    for entry in entries:
        summary.append({
            # Initial request data
            "request_id": entry.request_id,
            "request_content": entry.request_content,
            "service": entry.service,
            "executor_comment": entry.executor_comment,
            "chat_history": entry.chat_history,
            
            # LLM output data
            "intent_text": entry.intent_text,
            "intent_source": entry.intent_source,
            "scenario_type": entry.scenario_type,
            "scenario_details": entry.scenario_details,
        })
    
    return summary 