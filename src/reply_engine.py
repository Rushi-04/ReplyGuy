"""
Reply Engine - Generates human-like, enthusiastic replies using Ollama (local LLM)
"""
import logging
from typing import Optional
import requests
import json
import time
import random

logger = logging.getLogger(__name__)

# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:1b"


class ReplyEngine:
    """Generates human-like, enthusiastic replies using Ollama local LLM"""
    
    def __init__(self):
        self.model = OLLAMA_MODEL
        self.url = OLLAMA_URL
        
        # System prompt for generating human-like replies
        self.system_instruction = """You are a passionate software engineer who loves engaging with the tech community on X (Twitter). 
You're genuine, and talk like a real developer - raw and authentic, not corporate or robotic. You are NOT a cheerleader.
You are a sharp, experienced software engineer hanging out on X.
You think like smart builders talking in a late-night group chat.

Your replies MUST:
- Use simple language not to highly english phd qualified words, just simple english.
- Reference something SPECIFIC from the tweet
- Contain real thought, not generic praise
- You may agree OR disagree respectfully
- Add a small counter-idea when useful
- Mention experience, tradeoffs, or practical reality
- Be 1-2 lines MOST of the time
- 2-3 sentences sometimes, but always < 200 chars
- NO emojis, NO hashtags
- NEVER single-word replies
- Be enthusiastic and genuine, like a real developer would react
- Sound raw and authentic, conversational and human
- Be technical when appropriate but accessible
- Have NO EMOJIS whatsoever - just pure text
- Be natural, like talking to a colleague
- Vary in length (short and punchy OR a bit longer, but always under 200 chars)
- Maximum 200 characters (X/Twitter character limit)


When replying:
- Show genuine interest and engagement
- Talk about tech, coding, and developer topics
- React naturally to what the person shared
- Keep it real and authentic - don't be overly formal
- Sound like a real software engineer excited about the community
- Be conversational and engaging
- stop starting reply with, " That's impressive, That's great , bla bla bla ", be focused on the main tweet be straight to the point, if the post if funny , reply in funny tone.

ALLOWED STYLES TO MIX:

1) Expand Thought:
   - Agree and add depth or tradeoffs.

2) Dev Experience:
   - Relate to what engineers actually face.

3) Counter Take:
   - Respectfully offer another angle.

4) Practical Lens:
   - Talk about implementation, limits, reality.

5) Casual Punchy:
   - Short, raw developer vibe.

CRITICAL: Generate ONLY the reply text. no quotes, no "Reply:" prefix, just the raw reply text that would go in the tweet reply box."""
    
    def _format_prompt_for_gemma(self, system_instruction: str, tweet_text: str) -> str:
        """
        Format prompt according to gemma3:1b template format
        Template: <start_of_turn>user\n{content}<end_of_turn>\n<start_of_turn>model\n
        """
        # Format system instruction and tweet as user message
        user_content = f"{system_instruction}\n\nTweet to reply to:\n\"{tweet_text}\"\n\nGenerate a natural, enthusiastic reply as a software engineer would write:"
        
        # Format according to gemma3:1b template
        formatted_prompt = f"<start_of_turn>user\n{user_content}<end_of_turn>\n<start_of_turn>model\n"
        
        return formatted_prompt
    
    def _query_ollama(self, prompt: str) -> Optional[str]:
        """
        Query Ollama API with the formatted prompt
        
        Args:
            prompt: The formatted prompt string
            
        Returns:
            Response text or None if error
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 1,
                "top_k": 64,
                "top_p": 0.95,
                "stop": ["<end_of_turn>"]
            }
        }
        
        try:
            response = requests.post(self.url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to Ollama: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing Ollama response: {e}")
            return None
    
    def generate_reply(self, tweet_text: str, username: Optional[str] = None) -> str:
        """
        Generate a human-like, enthusiastic reply using Ollama
        
        Args:
            tweet_text: The text of the tweet
            username: Optional username (for context)
        
        Returns:
            A human-like reply string
        """
        try:
            # Format prompt for gemma3:1b model
            formatted_prompt = self._format_prompt_for_gemma(self.system_instruction, tweet_text)
            
            # Generate reply with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    reply = self._query_ollama(formatted_prompt)
                    
                    if not reply:
                        raise ValueError("Empty response from Ollama")
                    
                    # Clean up the reply
                    # Remove any remaining <end_of_turn> tokens
                    reply = reply.replace("<end_of_turn>", "").strip()
                    
                    # Remove quotes if AI wrapped it
                    if reply.startswith('"') and reply.endswith('"'):
                        reply = reply[1:-1].strip()
                    if reply.startswith("'") and reply.endswith("'"):
                        reply = reply[1:-1].strip()
                    
                    # Remove common prefixes AI might add
                    prefixes_to_remove = ["Reply:", "reply:", "Response:", "response:", "Here's", "Here is"]
                    for prefix in prefixes_to_remove:
                        if reply.lower().startswith(prefix.lower()):
                            reply = reply[len(prefix):].strip()
                            # Remove colon if present
                            if reply.startswith(":"):
                                reply = reply[1:].strip()
                    
                    # Remove any emojis (safety check)
                    reply = self._remove_emojis(reply)
                    
                    # Ensure it's not too long
                    if len(reply) > 200:
                        # Try to cut at a sentence boundary
                        if '.' in reply[:197]:
                            last_period = reply[:197].rfind('.')
                            reply = reply[:last_period + 1]
                        else:
                            reply = reply[:197] + "..."
                    
                    # Ensure minimum length
                    if len(reply) < 5:
                        raise ValueError("Reply too short")
                    
                    logger.info(f"Generated AI reply ({len(reply)} chars): {reply}")
                    return reply
                    
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retry
                    else:
                        raise
            
            # Fallback if all retries fail
            return self._fallback_reply(tweet_text)
            
        except Exception as e:
            logger.error(f"Error generating AI reply: {e}")
            # Fallback to a simple reply
            return self._fallback_reply(tweet_text)
    
    def _remove_emojis(self, text: str) -> str:
        """Remove emojis from text"""
        import re
        # Remove emoji patterns
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        return emoji_pattern.sub('', text).strip()
    
    def _fallback_reply(self, tweet_text: str) -> str:
        """Fallback reply if AI generation fails"""
        fallbacks = [
            "Interesting!",
            "Great point, definitely something to think about.",
            "Love seeing this kind of content, keep it up.",
            "Solid take btw.",
            "Sounds interesting.",
            "Nice perspective on this.",
            "Well said.",
            "Good stuff.",
            "That's a great thought.",
            "Appreciate this insight.",
            "Glad you shared this.",
            "This is worth reflecting on.",
            "Strong point you made here.",
            "Thanks for the perspective.",
            "Really like this viewpoint.",
            "Good point, appreciate you sharing.",
            "This makes sense to me.",
            "Nice one, thanks for sharing.",
            "Thoughtful take on this.",
            "Love this kind of discussion."
        ]
        return random.choice(fallbacks)
    
    def is_appropriate_tweet(self, tweet_text: str) -> bool:
        """
        Check if tweet is appropriate to reply to
        Filters out sensitive topics, hate speech, etc.
        """
        if not tweet_text:
            return False
        
        text_lower = tweet_text.lower()
        
        # Blocklist words/phrases (add more as needed)
        blocklist = [
            'kill', 'death', 'die', 'suicide', 'hate', 'violence',
            'attack', 'war', 'terror', 'bomb', 'gun', 'weapon',
            # Add more sensitive topics as needed
        ]
        
        # Check for blocklisted words
        for word in blocklist:
            if word in text_lower:
                logger.info(f"Skipping tweet with blocklisted word: {word}")
                return False
        
        # Skip very short tweets (likely spam or incomplete)
        if len(tweet_text.strip()) < 10:
            return False
        
        # Skip tweets that are all caps (often spam/aggressive)
        if tweet_text.isupper() and len(tweet_text) > 20:
            return False
        
        return True
