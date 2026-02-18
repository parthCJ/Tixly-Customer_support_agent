"""
CrewAI Service - Multi-Agent Customer Support System
Uses CrewAI to orchestrate specialized agents for ticket processing
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from .crewai_tools import create_support_tools

# Load environment variables
load_dotenv()


class CustomerSupportCrew:
    """Multi-agent crew for customer support ticket processing"""
    
    def __init__(self, kb_service=None):
        """
        Initialize the customer support crew
        
        Args:
            kb_service: Optional knowledge base service for RAG
        """
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("⚠️  Warning: GROQ_API_KEY not found in environment variables")
            print("   CrewAI agents will be disabled")
            self.llm = None
        else:
            # Initialize Groq LLM for all agents
            self.llm = ChatGroq(
                api_key=self.api_key,
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=1000
            )
        
        self.kb_service = kb_service
        
        # Create tools for agents
        self.tools = create_support_tools(kb_service=kb_service)
        
        # Initialize agents
        self.triage_agent = self._create_triage_agent()
        self.knowledge_agent = self._create_knowledge_agent()
        self.response_agent = self._create_response_agent()
        self.quality_agent = self._create_quality_agent()
    
    def _create_triage_agent(self) -> Agent:
        """Create the triage agent for ticket classification"""
        # Tools for triage: category validator, priority validator, urgency detector
        triage_tools = [t for t in self.tools if 'validator' in t.name.lower() or 'urgency' in t.name.lower()]
        
        return Agent(
            role="Customer Support Triage Specialist",
            goal="Accurately classify and prioritize incoming customer support tickets",
            backstory="""You are an experienced customer support triage specialist with 
            years of experience in analyzing customer issues. You excel at quickly 
            understanding the core problem, identifying urgency indicators, and 
            classifying tickets into the correct categories. You have a keen eye for 
            sentiment analysis and can detect frustrated or upset customers.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=triage_tools
        # Tools for KB agent: knowledge base search
        kb_tools = [t for t in self.tools if 'knowledge' in t.name.lower()]
        
        return Agent(
            role="Knowledge Base Expert",
            goal="Find the most relevant solutions and articles from the knowledge base",
            backstory="""You are a knowledge management expert who knows the company's 
            entire knowledge base inside out. You excel at finding relevant solutions, 
            FAQs, and documentation that can help resolve customer issues. You can 
            quickly identify which articles will be most helpful for specific problems.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=kb_tools if kb_tools else []cumentation that can help resolve customer issues. You can 
            quickly identify which articles will be most helpful for specific problems.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_response_agent(self) -> Agent:
        """Create the response generation agent"""
        return Agent(
            role="Customer Response Specialist",
            goal="Generate empathetic, professional, and solution-oriented responses",
            backstory="""You are a seasoned customer service representative known for 
            your excellent communication skills. You write clear, empathetic responses 
            that address customer concerns while maintaining a professional yet friendly 
            tone. You always provide actionable solutions and next steps.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_quality_agent(self) -> Agent:
        """Create the quality assurance agent"""
        return Agent(
            role="Quality Assurance Manager",
            goal="Review and improve customer responses for quality and accuracy",
            backstory="""You are a quality assurance manager with high standards for 
            customer service. You review all responses to ensure they are professional, 
            accurate, empathetic, and provide clear solutions. You check for tone, 
            completeness, and adherence to company policies.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def process_ticket(self, subject: str, description: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a ticket through the multi-agent workflow
        
        Args:
            subject: Ticket subject line
            description: Ticket description/body
            metadata: Additional context (order_id, customer info, etc.)
        
        Returns:
            Dictionary with:
                - category: Predicted category
                - priority: Predicted priority
                - sentiment: Customer sentiment
                - urgency_keywords: List of urgency indicators
                - extracted_info: Extracted entities
                - confidence: AI confidence score
                - suggested_reply: Generated response
                - kb_articles: Relevant knowledge base articles
                - reasoning: Triage reasoning
                - quality_score: Response quality score
        """
        if not self.llm:
            return self._fallback_response()
        
        try:
            # Prepare ticket context
            ticket_context = f"""
            Subject: {subject}
            Description: {description}
            
            Additional Context:
            {self._format_metadata(metadata)}
            """
            
            # Task 1: Triage and Classification
            triage_task = Task(
                description=f"""
                Analyze the following customer support ticket and provide classification:
                
                {ticket_context}
                
                Provide:
                1. Category (SHIPPING, BILLING, TECHNICAL, PRODUCT, ACCOUNT, REFUND, GENERAL)
                2. Priority (LOW, MEDIUM, HIGH, CRITICAL)
                3. Sentiment (positive, neutral, negative, frustrated, angry)
                4. Urgency keywords found in the message
                5. Extracted information (order IDs, dates, amounts, product names, etc.)
                6. Confidence score (0.0 to 1.0)
                7. Brief reasoning for your classification
                
                Format your response as structured data.
                """,
                agent=self.triage_agent,
                expected_output="Structured classification with category, priority, sentiment, and reasoning"
            )
            
            # Task 2: Knowledge Base Search
            kb_task = Task(
                description=f"""
                Based on the ticket classification, identify the most relevant knowledge base 
                articles or solutions that could help resolve this customer issue:
                
                {ticket_context}
                
                Search for:
                1. Direct solutions to the problem
                2. Related FAQ articles
                3. Step-by-step guides
                4. Policy documents if needed
                
                Provide a list of relevant article titles and brief summaries.
                """,
                agent=self.knowledge_agent,
                expected_output="List of relevant knowledge base articles with summaries"
            )
            
            # Task 3: Response Generation
            response_task = Task(
                description=f"""
                Generate a professional, empathetic customer response based on:
                
                Ticket:
                {ticket_context}
                
                Use the classification and knowledge base findings to create a response that:
                1. Acknowledges the customer's issue with empathy
                2. Provides a clear solution or next steps
                3. References relevant knowledge base articles if helpful
                4. Maintains a professional yet friendly tone
                5. Includes specific actions the customer should take
                6. Sets proper expectations for resolution time
                
                Keep the response concise but complete (150-300 words).
                """,
                agent=self.response_agent,
                expected_output="A complete, professional customer response ready to send"
            )
            
            # Task 4: Quality Review
            quality_task = Task(
                description=f"""
                Review the generated customer response for quality assurance:
                
                Original Ticket:
                {ticket_context}
                
                Evaluate:
                1. Tone and empathy
                2. Clarity of solution
                3. Completeness of response
                4. Professional language
                5. Actionable next steps
                
                Provide:
                - Quality score (0.0 to 1.0)
                - Improvements if needed
                - Final approved response
                """,
                agent=self.quality_agent,
                expected_output="Quality score and final approved response"
            )
            
            # Create and run the crew
            crew = Crew(
                agents=[
                    self.triage_agent,
                    self.knowledge_agent,
                    self.response_agent,
                    self.quality_agent
                ],
                tasks=[triage_task, kb_task, response_task, quality_task],
                process=Process.sequential,  # Tasks run in sequence
                verbose=True
            )
            
            # Execute the crew workflow
            result = crew.kickoff()
            
            # Parse and structure the results
            return self._parse_crew_result(result, ticket_context)
            
        except Exception as e:
            print(f"❌ Error in CrewAI processing: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._fallback_response()
    
    def _format_metadata(self, metadata: Optional[Dict[str, Any]]) -> str:
        """Format metadata for display"""
        if not metadata:
            return "No additional context provided"
        
        formatted = []
        for key, value in metadata.items():
            if value:
                formatted.append(f"- {key}: {value}")
        
        return "\n".join(formatted) if formatted else "No additional context provided"
    
    def _parse_crew_result(self, result, ticket_context: str) -> Dict[str, Any]:
        """
        Parse the crew execution result into structured format
        
        Note: CrewAI returns the final task output. We'll need to parse it.
        """
        try:
            # Get the final output
            final_output = str(result)
            
            # Extract structured data from the output
            # This is a simplified parser - in production, you'd want more robust parsing
            
            # Default structured response
            structured_result = {
                "category": self._extract_value(final_output, "category", "GENERAL"),
                "priority": self._extract_value(final_output, "priority", "MEDIUM"),
                "sentiment": self._extract_value(final_output, "sentiment", "neutral"),
                "urgency_keywords": self._extract_keywords(final_output),
                "extracted_info": {},
                "confidence": 0.85,
                "reasoning": "Multi-agent analysis completed",
                "suggested_reply": self._extract_response(final_output),
                "kb_articles": self._extract_kb_articles(final_output),
                "quality_score": self._extract_quality_score(final_output),
                "crew_output": final_output  # Keep full output for debugging
            }
            
            return structured_result
            
        except Exception as e:
            print(f"⚠️  Error parsing crew result: {str(e)}")
            return self._fallback_response()
    
    def _extract_value(self, text: str, field: str, default: str) -> str:
        """Extract a specific field value from text"""
        # Simple extraction - look for patterns like "Category: BILLING"
        import re
        pattern = rf"{field}[:\s]+([A-Z_]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).upper() if match else default
    
    def _extract_keywords(self, text: str) -> list:
        """Extract urgency keywords"""
        urgency_words = ["urgent", "asap", "immediately", "critical", "emergency", "frustrated", "angry"]
        found = [word for word in urgency_words if word.lower() in text.lower()]
        return found[:3]  # Return top 3
    
    def _extract_response(self, text: str) -> str:
        """Extract the generated response from the output"""
        # Look for response section
        lines = text.split("\n")
        response_lines = []
        in_response = False
        
        for line in lines:
            if "response" in line.lower() or "dear" in line.lower() or "hi" in line.lower():
                in_response = True
            
            if in_response and line.strip():
                response_lines.append(line)
        
        if response_lines:
            return "\n".join(response_lines[-20:])  # Get last 20 lines as response
        
        return "Thank you for contacting support. We are reviewing your request and will respond shortly."
    
    def _extract_kb_articles(self, text: str) -> list:
        """Extract knowledge base articles mentioned"""
        # Simple extraction of article mentions
        articles = []
        if "article" in text.lower() or "faq" in text.lower():
            articles.append({
                "title": "Relevant documentation found",
                "summary": "Please check our knowledge base for detailed guides"
            })
        return articles
    
    def _extract_quality_score(self, text: str) -> float:
        """Extract quality score from QA review"""
        import re
        pattern = r"quality[:\s]+([0-9.]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except:
                pass
        return 0.85  # Default good quality score
    
    def _fallback_response(self) -> Dict[str, Any]:
        """Fallback response when CrewAI is unavailable"""
        return {
            "category": "GENERAL",
            "priority": "MEDIUM",
            "sentiment": "neutral",
            "urgency_keywords": [],
            "extracted_info": {},
            "confidence": 0.5,
            "reasoning": "CrewAI unavailable - using fallback classification",
            "suggested_reply": "Thank you for contacting us. We have received your request and will respond shortly.",
            "kb_articles": [],
            "quality_score": 0.0
        }


# Example usage function for testing
def test_crewai_service():
    """Test the CrewAI service with a sample ticket"""
    crew_service = CustomerSupportCrew()
    
    test_ticket = {
        "subject": "Order not delivered - URGENT",
        "description": """
        I ordered a laptop 2 weeks ago (Order #12345) and it still hasn't arrived. 
        I paid extra for express shipping and I needed it for work. This is very 
        frustrating! I've sent multiple emails with no response. Please help ASAP!
        """,
        "metadata": {
            "order_id": "12345",
            "customer_name": "John Doe",
            "customer_email": "john@example.com"
        }
    }
    
    result = crew_service.process_ticket(
        subject=test_ticket["subject"],
        description=test_ticket["description"],
        metadata=test_ticket["metadata"]
    )
    
    print("\n" + "="*80)
    print("CREWAI PROCESSING RESULT")
    print("="*80)
    print(f"Category: {result['category']}")
    print(f"Priority: {result['priority']}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Quality Score: {result['quality_score']}")
    print(f"\nSuggested Reply:\n{result['suggested_reply']}")
    print("="*80)


if __name__ == "__main__":
    test_crewai_service()
