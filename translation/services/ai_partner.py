"""
AI Virtual Partner reply generation using Gemini.
Reads API key from env GOOGLE_API_KEY or settings.
"""

import os
from typing import List

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover
    genai = None


def _configure_gemini():
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key or not genai:
        return None
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
        return None


def generate_partner_reply(prompt_user_lang: str, user_text: str, history: List[str]) -> str:
    """
    Generate a conversational reply from the virtual partner using Gemini.

    Args:
        prompt_user_lang: Language code of user text (e.g., 'en' or 'en-US')
        user_text: last user message in their language
        history: recent conversation lines in English (optional for context)

    Returns:
        str: AI partner reply in English (concise, helpful). Falls back to a rule-based template if Gemini isn't available.
    """
    # Fallback if Gemini is unavailable
    model = _configure_gemini()
    base_system = (
        "You are a helpful, concise conversation partner. "
        "Answer the user's question directly and continue the conversation. "
        "Do not merely repeat the user's text. Be friendly and to-the-point."
    )

    if model is None:
        # Simple deterministic fallback
        if '?' in user_text:
            return "That's a good question. Here's what I think: " + user_text.split('?')[0].strip() + ". What do you think?"
        return "Thanks for sharing. Could you tell me more about that?"

    messages = [
        {"role": "system", "content": base_system},
    ]
    if history:
        messages.append({"role": "user", "content": "Conversation so far (English):\n" + "\n".join(history[-8:])})
    messages.append({"role": "user", "content": f"User ({prompt_user_lang}) said: {user_text}. Reply in English."})

    try:
        response = model.generate_content(messages)
        text = getattr(response, 'text', None) or (response.candidates[0].content.parts[0].text if response and response.candidates else '')
        return (text or '').strip() or "I'm here. Could you elaborate?"
    except Exception:
        return "I might be having trouble right now. Could you say that another way?"


