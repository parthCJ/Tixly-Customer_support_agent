"""
AI Service - Handles ticket classification and AI-powered analysis
Uses Groq API (free tier) for fast LLM inference
"""
import os
import json
from typing import Dict, Any, Optional
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TicketAIService:
    """AI service for ticket classification and analysis"""
    
    def __init__(self):
        """Initialize Groq client"""
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("⚠️  Warning: GROQ_API_KEY not found in environment variables")
            print("   AI classification will be disabled")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)
            self.model = "llama-3.3-70b-versatile"  # Updated model (Nov 2024)
    
    def classify_ticket(self, subject: str, description: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Classify a support ticket using AI
        
        Args:
            subject: Ticket subject line
            description: Ticket description/body
            metadata: Additional context (order_id, customer info, etc.)
        
        Returns:
            Dictionary with:
                - category: Predicted category (SHIPPING, BILLING, etc.)
                - priority: Predicted priority (LOW, MEDIUM, HIGH, CRITICAL)
                - sentiment: Customer sentiment (positive, neutral, negative)
                - urgency_keywords: List of urgency indicators found
                - extracted_info: Extracted entities (order_id, dates, amounts, etc.)
                - confidence: AI confidence score (0-1)
                - reasoning: Brief explanation of classification
        """
        if not self.client:
            # Return default classification if AI is disabled
            return self._fallback_classification()
        
        try:
            # Build the classification prompt
            prompt = self._build_classification_prompt(subject, description, metadata)
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert customer support ticket classifier. Analyze tickets and provide accurate categorization, priority assessment, and entity extraction. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=500,
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            
            # Validate and normalize the response
            return self._normalize_classification(result)
            
        except Exception as e:
            print(f"❌ AI classification error: {str(e)}")
            return self._fallback_classification()
    
    def generate_suggested_reply(self, ticket_data: Dict[str, Any], kb_context: str = None) -> str:
        """
        Generate an AI-suggested reply for a ticket
        
        Args:
            ticket_data: Full ticket information
            kb_context: Relevant knowledge base articles (from RAG search)
        
        Returns:
            Suggested reply text
        """
        if not self.client:
            return "AI reply generation is currently unavailable. Please respond manually."
        
        try:
            # If no KB context provided, search for it
            if kb_context is None:
                from .kb_service import search_knowledge_base
                
                # Search KB for relevant articles
                kb_articles = search_knowledge_base(
                    subject=ticket_data.get('subject', ''),
                    description=ticket_data.get('description', ''),
                    category=ticket_data.get('category'),
                    n_results=2  # Get top 2 most relevant articles
                )
                
                # Format KB context
                if kb_articles:
                    kb_context = "\n\n".join([
                        f"KB Article: {article['title']}\n{article['content'][:500]}..."
                        for article in kb_articles
                        if article['relevance_score'] > 0.5  # Only use if relevant enough
                    ])
            
            # Build reply generation prompt
            prompt = self._build_reply_prompt(ticket_data, kb_context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful customer support agent. Write professional, empathetic, and concise responses to customer tickets. Be solution-focused and friendly."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,  # Higher temperature for more natural responses
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Reply generation error: {str(e)}")
            return "Unable to generate suggested reply. Please respond manually."
    
    def _build_classification_prompt(self, subject: str, description: str, metadata: Dict[str, Any] = None) -> str:
        """Build the prompt for ticket classification"""
        
        # Add metadata context if available
        context = ""
        if metadata:
            if metadata.get("order_id"):
                context += f"\nOrder ID: {metadata['order_id']}"
            if metadata.get("customer_name"):
                context += f"\nCustomer: {metadata['customer_name']}"
        
        prompt = f"""Analyze this customer support ticket and classify it:

Subject: {subject}
Description: {description}{context}

Provide a JSON response with the following structure:
{{
    "category": "<one of: SHIPPING, BILLING, PRODUCT, ACCOUNT, TECHNICAL, REFUND, GENERAL, OTHER>",
    "priority": "<one of: LOW, MEDIUM, HIGH, CRITICAL>",
    "sentiment": "<one of: positive, neutral, negative>",
    "urgency_keywords": ["<list of urgency indicators like 'urgent', 'asap', 'immediately'>"],
    "extracted_info": {{
        "order_id": "<order number if mentioned>",
        "amount": "<dollar amount if mentioned>",
        "date_mentioned": "<any specific dates>",
        "product_name": "<product name if mentioned>"
    }},
    "confidence": <float between 0 and 1>,
    "reasoning": "<brief explanation of your classification>"
}}

Classification guidelines:
- CRITICAL priority: System down, security issue, payment failure, angry customer
- HIGH priority: Order issues, refund requests, cannot access account
- MEDIUM priority: General questions, minor issues, feature requests
- LOW priority: General inquiries, feedback, compliments

- Negative sentiment: Frustrated, angry, disappointed language
- Neutral sentiment: Matter-of-fact, informational
- Positive sentiment: Happy, satisfied, compliments
"""
        return prompt
    
    def _build_reply_prompt(self, ticket_data: Dict[str, Any], kb_context: str = None) -> str:
        """Build the prompt for reply generation"""
        
        kb_section = ""
        if kb_context:
            kb_section = f"\n\nRelevant Knowledge Base Info:\n{kb_context}"
        
        prompt = f"""Generate a professional response to this customer support ticket:

Subject: {ticket_data.get('subject', 'N/A')}
Description: {ticket_data.get('description', 'N/A')}
Category: {ticket_data.get('category', 'GENERAL')}
Priority: {ticket_data.get('priority', 'MEDIUM')}{kb_section}

Write a helpful, empathetic response that:
1. Acknowledges the customer's issue
2. Provides a solution or next steps
3. Is professional but friendly
4. Is concise (2-3 paragraphs max)

Do not include a signature or greeting (that will be added automatically).
"""
        return prompt
    
    def _normalize_classification(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and validate the AI classification result"""
        
        # Map AI categories to our enum values
        category_mapping = {
            "SHIPPING": "shipping_delay",
            "BILLING": "billing_issue",
            "PRODUCT": "product_defect",
            "ACCOUNT": "account_access",
            "TECHNICAL": "technical_support",
            "REFUND": "refund_request",
            "GENERAL": "general_inquiry",
            "OTHER": "other"
        }
        
        # Map priorities to lowercase (enum values)
        priority_mapping = {
            "LOW": "low",
            "MEDIUM": "medium",
            "HIGH": "high",
            "CRITICAL": "critical"
        }
        
        # Normalize category
        category_upper = result.get("category", "GENERAL").upper()
        category = category_mapping.get(category_upper, "general_inquiry")
        
        # Normalize priority
        priority_upper = result.get("priority", "MEDIUM").upper()
        priority = priority_mapping.get(priority_upper, "medium")
        
        # Normalize sentiment
        sentiment = result.get("sentiment", "neutral").lower()
        if sentiment not in ["positive", "neutral", "negative"]:
            sentiment = "neutral"
        
        # Ensure confidence is a float between 0 and 1
        confidence = float(result.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))
        
        return {
            "category": category,
            "priority": priority,
            "sentiment": sentiment,
            "urgency_keywords": result.get("urgency_keywords", []),
            "extracted_info": result.get("extracted_info", {}),
            "confidence": confidence,
            "reasoning": result.get("reasoning", "No reasoning provided")
        }
    
    def _fallback_classification(self) -> Dict[str, Any]:
        """Fallback classification when AI is unavailable"""
        return {
            "category": "GENERAL",
            "priority": "MEDIUM",
            "sentiment": "neutral",
            "urgency_keywords": [],
            "extracted_info": {},
            "confidence": 0.0,
            "reasoning": "AI classification unavailable - using defaults"
        }


# Global AI service instance
ai_service = TicketAIService()


def classify_ticket(subject: str, description: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Convenience function to classify a ticket
    
    Usage:
        result = classify_ticket("Order issue", "My order hasn't arrived", {"order_id": "123"})
        print(result['category'])  # "SHIPPING"
        print(result['priority'])   # "HIGH"
    """
    return ai_service.classify_ticket(subject, description, metadata)


def generate_reply(ticket_data: Dict[str, Any], kb_context: str = None) -> str:
    """
    Convenience function to generate a suggested reply
    
    Usage:
        reply = generate_reply(ticket_data)
        print(reply)
    """
    return ai_service.generate_suggested_reply(ticket_data, kb_context)
