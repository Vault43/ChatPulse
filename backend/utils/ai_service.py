import openai
import google.generativeai as genai
import json
import os
from typing import List, Dict, Optional
import itertools
from database import SessionLocal, AIRule, User

class AIService:
    def __init__(self):
        # Initialize OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Initialize Gemini (supports multiple keys)
        self.gemini_api_keys = self._load_gemini_keys()
        self._gemini_key_cycle = itertools.cycle(self.gemini_api_keys) if self.gemini_api_keys else None
    
    async def generate_response(
        self, 
        message: str, 
        user_id: int, 
        session_context: Optional[List[Dict]] = None,
        provider: str = "openai"
    ) -> str:
        """Generate AI response based on user message and custom rules."""
        
        # Get user's custom AI rules
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise Exception("User not found")
            
            # Check subscription limits
            if user.subscription_plan.value == "free":
                # Free plan limitations
                pass  # Could implement daily limits here
            
            # Get custom rules
            rules = db.query(AIRule).filter(
                AIRule.user_id == user_id,
                AIRule.is_active == True
            ).order_by(AIRule.priority.desc()).all()
            
            # Check if message matches any custom rules
            for rule in rules:
                if self._matches_rule(message, rule):
                    return self._apply_rule_template(rule.response_template, message)
            
            # If no custom rules match, use general AI
            return await self._generate_general_ai_response(
                message, user_id, session_context, provider
            )
            
        finally:
            db.close()
    
    def _matches_rule(self, message: str, rule: AIRule) -> bool:
        """Check if message matches rule keywords."""
        if not rule.trigger_keywords:
            return False
        
        try:
            keywords = json.loads(rule.trigger_keywords)
            message_lower = message.lower()
            
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    return True
            
            return False
        except json.JSONDecodeError:
            return False
    
    def _apply_rule_template(self, template: str, message: str) -> str:
        """Apply template with message context."""
        # Simple template replacement
        return template.replace("{message}", message)
    
    async def _generate_general_ai_response(
        self, 
        message: str, 
        user_id: int, 
        session_context: Optional[List[Dict]] = None,
        provider: str = "openai"
    ) -> str:
        """Generate general AI response using OpenAI or Gemini."""
        
        # Build context from session history
        context_messages = []
        if session_context:
            for msg in session_context[-5:]:  # Last 5 messages for context
                role = "user" if msg["message_type"] == "customer" else "assistant"
                context_messages.append({"role": role, "content": msg["content"]})
        
        # Add current message
        context_messages.append({"role": "user", "content": message})
        
        # System prompt
        system_prompt = """You are a helpful AI assistant for a business chat system. 
        Provide professional, friendly, and helpful responses. 
        Keep responses concise and relevant to customer inquiries.
        If you don't know something, admit it politely and offer to connect them with a human representative."""
        
        try:
            if provider == "openai" and self.openai_api_key:
                return await self._openai_response(context_messages, system_prompt)
            elif provider == "gemini" and self.gemini_api_keys:
                return await self._gemini_response(message, system_prompt)
            else:
                # Fallback response
                return "Thank you for your message. Our team will get back to you shortly."
        
        except Exception as e:
            print(f"AI Service Error: {e}")
            return "I apologize, but I'm having trouble responding right now. Please try again later."
    
    async def _openai_response(self, messages: List[Dict], system_prompt: str) -> str:
        """Generate response using OpenAI."""
        
        # Add system message
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=full_messages,
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    async def _gemini_response(self, message: str, system_prompt: str) -> str:
        """Generate response using Gemini."""

        gemini_key = self._get_next_gemini_key()
        if not gemini_key:
            return "Thank you for your message. Our team will get back to you shortly."

        # Note: genai.configure is global, so we configure per request using the selected key.
        genai.configure(api_key=gemini_key)

        model = genai.GenerativeModel('gemini-pro')
        
        # Combine system prompt and message
        full_prompt = f"{system_prompt}\n\nUser: {message}"
        
        response = model.generate_content(full_prompt)
        
        return response.text.strip()
    
    def get_supported_providers(self) -> List[str]:
        """Get list of supported AI providers."""
        providers = []
        if self.openai_api_key:
            providers.append("openai")
        if self.gemini_api_keys:
            providers.append("gemini")
        return providers

    def _load_gemini_keys(self) -> List[str]:
        """Load Gemini keys from env.

        Supported formats:
        - GEMINI_API_KEY (single key)
        - GEMINI_API_KEYS (comma/newline separated)
        - GEMINI_API_KEY_1..GEMINI_API_KEY_20
        """

        keys: List[str] = []

        bulk = os.getenv("GEMINI_API_KEYS")
        if bulk:
            # Allow comma and/or newline separated lists
            raw_parts = bulk.replace("\r\n", "\n").replace("\r", "\n").replace(",", "\n").split("\n")
            keys.extend([p.strip() for p in raw_parts if p.strip()])

        for i in range(1, 21):
            k = os.getenv(f"GEMINI_API_KEY_{i}")
            if k and k.strip():
                keys.append(k.strip())

        single = os.getenv("GEMINI_API_KEY")
        if single and single.strip():
            keys.append(single.strip())

        # Dedupe while preserving order
        deduped: List[str] = []
        seen = set()
        for k in keys:
            if k not in seen:
                deduped.append(k)
                seen.add(k)

        return deduped

    def _get_next_gemini_key(self) -> Optional[str]:
        if not self._gemini_key_cycle:
            return None
        return next(self._gemini_key_cycle)

# Singleton instance
ai_service = AIService()
