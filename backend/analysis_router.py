from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Literal
from llm import llm
from generate_chart import generate_chart
from execute_analysis_query import execute_analysis_query
import logging

logger = logging.getLogger(__name__)

class AnalysisDecision(BaseModel):
    action_type: Literal["chart", "query"] = Field(description="The type of action to take: 'chart' for visualization or 'query' for data analysis")
    explanation: str = Field(description="Explanation of why this action was chosen")
    confidence: float = Field(description="Confidence in the decision")
    suggested_chart_type: str = Field(description="Suggested chart type for data visualization")

def create_analysis_router():
    # Define the prompt template
    template = """
    You are an AI assistant that helps determine whether a user's query requires data visualization (chart) or data analysis (query).
    
    User Query: {query}
    
    Determine if the query is asking for:
    1. Data visualization (chart) - if the user wants to see trends, patterns, or comparisons visually
    2. Data analysis (query) - if the user wants specific information, calculations, or insights
    
    {format_instructions}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["query"],
        partial_variables={"format_instructions": AnalysisDecision.schema_json()}
    )
    
    # Create the chain
    chain = LLMChain(llm=llm, prompt=prompt)
    
    return chain

def route_analysis(filename: str, query: str) -> dict:
    """
    Route the analysis request to either chart generation or query execution based on the user's query.
    
    Args:
        filename (str): The name of the file to analyze
        query (str): The user's query
        
    Returns:
        dict: The result of the analysis with metadata
    """
    try:
        # Create the router
        router = create_analysis_router()
        
        # Get the decision
        decision = router.invoke({"query": query})
        logger.info(f"Router decision: {decision}")
        
        # Parse the decision
        parsed_decision = AnalysisDecision.parse_raw(decision["text"])
        
        result = {
            "metadata": {
                "action_type": parsed_decision.action_type,
                "explanation": parsed_decision.explanation,
                "confidence": parsed_decision.confidence,
                "suggested_chart_type": parsed_decision.suggested_chart_type
            }
        }
        
        # Route to appropriate handler(s)
        if parsed_decision.action_type in ["chart", "both"]:
            try:
                chart_result = generate_chart(filename, query)
                result.update(chart_result)
            except Exception as e:
                logger.error(f"Error generating chart: {str(e)}")
                result["chart_error"] = str(e)
        
        if parsed_decision.action_type in ["query", "both"]:
            try:
                query_result = execute_analysis_query(filename, query)
                # Ensure the query result is serializable
                if isinstance(query_result, dict):
                    result["analysis"] = query_result
                else:
                    result["analysis"] = {"output": str(query_result)}
            except Exception as e:
                logger.error(f"Error executing query: {str(e)}")
                result["query_error"] = str(e)
        
        return result
            
    except Exception as e:
        logger.error(f"Error in analysis routing: {str(e)}")
        # Fallback to basic query execution
        try:
            query_result = execute_analysis_query(filename, query)
            return {
                "metadata": {
                    "action_type": "query",
                    "explanation": "Fallback to query due to routing error",
                    "confidence": 0.0,
                    "error": str(e)
                },
                "analysis": {
                    "output": str(query_result) if not isinstance(query_result, dict) else query_result
                }
            }
        except Exception as fallback_error:
            logger.error(f"Fallback query also failed: {str(fallback_error)}")
            return {
                "metadata": {
                    "action_type": "error",
                    "explanation": "Both routing and fallback failed",
                    "confidence": 0.0,
                    "error": str(e),
                    "fallback_error": str(fallback_error)
                }
            } 