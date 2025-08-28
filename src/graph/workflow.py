
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from src.agents.creator import CreatorAgent
from src.agents.reviewer import ReviewerAgent
from src.services.name_service import NameService
from src.services.database_service import DatabaseService

class UsernameState(BaseModel):
    """State model for the username recommendation workflow."""
    input_name: str
    candidate_usernames: List[str] = []
    final_usernames: List[str] = []
    error: str = ""

class UsernameWorkflow:
    """LangGraph workflow for username recommendation."""
    
    def __init__(self):
        self.name_service = NameService()
        self.db_service = DatabaseService()
        self.creator_agent = CreatorAgent(self.name_service)
        self.reviewer_agent = ReviewerAgent(self.db_service)
        
        # Build the graph
        self.graph: StateGraph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        graph = StateGraph(UsernameState)
        
        # Add nodes
        graph.add_node("creator", self._creator_node)
        graph.add_node("reviewer", self._reviewer_node)
        
        # Add edges
        graph.add_edge("creator", "reviewer")
        graph.add_edge("reviewer", END)
        
        # Set entry point
        graph.set_entry_point("creator")
        
        return graph.compile()
    
    def _creator_node(self, state: UsernameState) -> Dict[str, Any]:
        """Creator agent node."""
        try:
            candidate_usernames = self.creator_agent.create_usernames(state.input_name)
            return {"candidate_usernames": candidate_usernames}
        except Exception as e:
            return {"error": f"Creator error: {str(e)}"}
    
    def _reviewer_node(self, state: UsernameState) -> Dict[str, Any]:
        """Reviewer agent node."""
        try:
            if state.error:
                return {"final_usernames": []}
            
            final_usernames = self.reviewer_agent.review_and_rank(state.candidate_usernames)
            return {"final_usernames": final_usernames}
        except Exception as e:
            return {"error": f"Reviewer error: {str(e)}"}
    
    def generate_usernames(self, input_name: str) -> List[str]:
        """
        Generate username recommendations for the given input name.
        """
        initial_state = UsernameState(input_name=input_name)
        result = self.graph.invoke(initial_state)
        
        return result['final_usernames']
