"""
CrewAI Tools for Customer Support Agents
Custom tools that agents can use to access knowledge base and perform actions
"""

from typing import Optional, List, ClassVar

try:
    from crewai_tools import BaseTool
except ImportError:
    # Fallback for different crewai versions
    try:
        from crewai.tools import BaseTool
    except ImportError:
        print("⚠️  Could not import BaseTool from crewai - tools will be disabled")
        BaseTool = object  # Fallback

from pydantic import BaseModel, Field, ConfigDict


class KnowledgeBaseSearchInput(BaseModel):
    """Input schema for knowledge base search"""

    query: str = Field(..., description="The search query to find relevant articles")
    top_k: int = Field(default=3, description="Number of top results to return")


class KnowledgeBaseSearchTool(BaseTool):
    """Tool for searching the knowledge base"""

    name: str = "Knowledge Base Search"
    description: str = """
    Search the company knowledge base for relevant articles, FAQs, and documentation.
    Use this tool to find solutions to customer problems, policies, and procedures.
    Input should be a clear search query describing the issue or topic.
    """
    args_schema: type[BaseModel] = KnowledgeBaseSearchInput
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def __init__(self, kb_service=None):
        super().__init__()
        self.kb_service = kb_service

    def _run(self, query: str, top_k: int = 3) -> str:
        """Execute the knowledge base search"""
        if not self.kb_service:
            return "Knowledge base service not available"

        try:
            # Search the knowledge base
            results = self.kb_service.search(query=query, n_results=top_k)

            if not results:
                return "No relevant articles found in the knowledge base"

            # Format results for agent consumption
            formatted_results = []
            for i, result in enumerate(results, 1):
                score = result.get("relevance_score", result.get("score", 0.0))
                formatted_results.append(
                    f"{i}. {result['title']}\n"
                    f"   Category: {result['category']}\n"
                    f"   Relevance: {score:.2f}\n"
                    f"   Content: {result['content'][:200]}...\n"
                )

            return "\n".join(formatted_results)

        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"


class TicketCategoryValidatorInput(BaseModel):
    """Input schema for ticket category validation"""

    category: str = Field(..., description="The proposed ticket category")


class TicketCategoryValidatorTool(BaseTool):
    """Tool for validating ticket categories"""

    name: str = "Ticket Category Validator"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    description: str = """
    Validate if a proposed ticket category is valid according to the system.
    Valid categories are: SHIPPING, BILLING, TECHNICAL, PRODUCT, ACCOUNT, REFUND, GENERAL
    Use this to ensure your classification matches system requirements.
    """
    args_schema: type[BaseModel] = TicketCategoryValidatorInput

    VALID_CATEGORIES: ClassVar[List[str]] = [
        "SHIPPING",
        "BILLING",
        "TECHNICAL",
        "PRODUCT",
        "ACCOUNT",
        "REFUND",
        "GENERAL",
    ]

    def _run(self, category: str) -> str:
        """Validate the category"""
        category_upper = category.upper()

        if category_upper in self.VALID_CATEGORIES:
            return f"✓ Category '{category_upper}' is valid"
        else:
            return (
                f"✗ Category '{category}' is invalid. "
                f"Valid categories: {', '.join(self.VALID_CATEGORIES)}"
            )


class TicketPriorityValidatorInput(BaseModel):
    """Input schema for ticket priority validation"""

    priority: str = Field(..., description="The proposed ticket priority")


class TicketPriorityValidatorTool(BaseTool):
    """Tool for validating ticket priorities"""

    name: str = "Ticket Priority Validator"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    description: str = """
    Validate if a proposed ticket priority is valid according to the system.
    Valid priorities are: LOW, MEDIUM, HIGH, CRITICAL
    Use this to ensure your priority assessment matches system requirements.
    """
    args_schema: type[BaseModel] = TicketPriorityValidatorInput

    VALID_PRIORITIES: ClassVar[List[str]] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def _run(self, priority: str) -> str:
        """Validate the priority"""
        priority_upper = priority.upper()

        if priority_upper in self.VALID_PRIORITIES:
            return f"✓ Priority '{priority_upper}' is valid"
        else:
            return (
                f"✗ Priority '{priority}' is invalid. "
                f"Valid priorities: {', '.join(self.VALID_PRIORITIES)}"
            )


class SentimentAnalysisInput(BaseModel):
    """Input schema for sentiment analysis"""

    text: str = Field(..., description="The text to analyze for sentiment")


class UrgencyKeywordsInput(BaseModel):
    """Input schema for urgency detection"""

    text: str = Field(..., description="The text to scan for urgency keywords")


class UrgencyKeywordDetectorTool(BaseTool):
    """Tool for detecting urgency keywords in customer messages"""

    name: str = "Urgency Keyword Detector"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    description: str = """
    Detect urgency indicators in customer messages.
    Returns a list of urgency-related keywords found in the text.
    Use this to help assess ticket priority.
    """
    args_schema: type[BaseModel] = UrgencyKeywordsInput

    URGENCY_KEYWORDS: ClassVar[List[str]] = [
        "urgent",
        "asap",
        "immediately",
        "emergency",
        "critical",
        "frustrated",
        "angry",
        "unacceptable",
        "disappointed",
        "losing money",
        "business impact",
        "deadline",
        "needed yesterday",
    ]

    def _run(self, text: str) -> str:
        """Detect urgency keywords"""
        text_lower = text.lower()
        found_keywords = [kw for kw in self.URGENCY_KEYWORDS if kw in text_lower]

        if not found_keywords:
            return "No urgency keywords detected"

        return f"Urgency keywords found: {', '.join(found_keywords)}"


def create_support_tools(kb_service=None) -> List[BaseTool]:
    """
    Create and return all support tools for CrewAI agents

    Args:
        kb_service: Optional knowledge base service instance

    Returns:
        List of CrewAI tools
    """
    tools = [
        TicketCategoryValidatorTool(),
        TicketPriorityValidatorTool(),
        UrgencyKeywordDetectorTool(),
    ]

    # Add KB search tool if service is available
    if kb_service:
        tools.insert(0, KnowledgeBaseSearchTool(kb_service=kb_service))

    return tools
