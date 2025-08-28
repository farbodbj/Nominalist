import random
import re
from typing import List
from src.services.name_service import NameService
from openai import OpenAI
import os 
import logging
logger = logging.getLogger(__name__)

class CreatorAgent:
    """AI-powered agent responsible for creating username candidates."""
    
    def __init__(self, name_service: NameService):
        self.name_service = name_service
        self.client = OpenAI(base_url = os.getenv("OPENAI_BASE_URL"))
        self.rules = [
            self._add_underscore,
            self._add_numbers,
            self._add_year,
            self._add_dots,
            self._add_prefix,
            self._add_suffix,
            self._make_lowercase,
            self._remove_spaces,
            self._add_random_suffix
        ]
    
    def create_usernames(self, input_name: str) -> List[str]:
        """
        Create 10-12 username candidates using AI and rules.
        """
        # Get English version of the name
        english_name = self.name_service.get_english_name(input_name)
        logger.info(f"found english name: {english_name}")
        usernames = []
        
        # Generate AI-powered creative usernames (5-6 usernames)
        ai_usernames = self._generate_ai_usernames(english_name)
        usernames.extend(ai_usernames)
        
        # Apply traditional rules (4-5 usernames) 
        rule_usernames = self._generate_rule_based_usernames(english_name)
        usernames.extend(rule_usernames)
        
        # Remove duplicates and ensure we have 10-12 candidates
        unique_usernames = list(dict.fromkeys(usernames))
        
        # If we have fewer than 10, add more variations
        base_name = english_name.lower().replace(' ', '')
        while len(unique_usernames) < 10:
            variation = self._create_variation(base_name)
            if variation not in unique_usernames:
                unique_usernames.append(variation)
        
        return unique_usernames[:12]
    
    def _generate_ai_usernames(self, name: str) -> List[str]:
        """Generate creative usernames using AI."""
        try:
            prompt = f"""
            Generate 6 creative and unique usernames based on the name "{name}".
            
            Requirements:
            - Each username should be 4-20 characters long
            - Use only letters, numbers, and underscores
            - Be creative but professional
            - Avoid offensive content
            - Make them memorable and easy to type
            - Consider variations like abbreviations, wordplay, or combinations
            
            Examples of good usernames: john_dev, sarah_codes, mike_pro, anna_x, dev_alex
            
            Return only the usernames, one per line, no extra text or numbering.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.8
            )
            
            ai_usernames = []
            content = response.choices[0].message.content.strip()
            
            for line in content.split('\n'):
                username = line.strip()
                # Clean and validate username
                username = re.sub(r'[^a-zA-Z0-9_]', '', username)
                if 4 <= len(username) <= 20 and username:
                    ai_usernames.append(username.lower())
            
            return ai_usernames[:6]
            
        except Exception as e:
            print(f"AI generation failed: {e}")
            # Fallback to creative generation
            return self._generate_creative_usernames(name)
    
    def _generate_rule_based_usernames(self, name: str) -> List[str]:
        """Generate usernames using traditional rules."""
        usernames = []
        
        # Apply first 5 rules
        for rule in self.rules[:5]:
            try:
                username = rule(name)
                if username and len(username) >= 3:
                    usernames.append(username)
            except Exception:
                continue
        
        return usernames
    
    def _add_underscore(self, name: str) -> str:
        """Add underscore between names or at the end."""
        clean_name = name.replace(' ', '_').lower()
        return clean_name
    
    def _add_numbers(self, name: str) -> str:
        """Add random numbers to the name."""
        clean_name = name.replace(' ', '').lower()
        return f"{clean_name}{random.randint(1, 999)}"
    
    def _add_year(self, name: str) -> str:
        """Add a year to the name."""
        clean_name = name.replace(' ', '').lower()
        year = random.choice([2020, 2021, 2022, 2023, 2024])
        return f"{clean_name}{year}"
    
    def _add_dots(self, name: str) -> str:
        """Add dots between names."""
        return name.replace(' ', '.').lower()
    
    def _add_prefix(self, name: str) -> str:
        """Add common prefixes."""
        clean_name = name.replace(' ', '').lower()
        prefixes = ['the', 'mr', 'ms', 'dr', 'prof']
        prefix = random.choice(prefixes)
        return f"{prefix}_{clean_name}"
    
    def _add_suffix(self, name: str) -> str:
        """Add common suffixes."""
        clean_name = name.replace(' ', '').lower()
        suffixes = ['_official', '_real', '_pro', '_user', '_dev']
        suffix = random.choice(suffixes)
        return f"{clean_name}{suffix}"
    
    def _make_lowercase(self, name: str) -> str:
        """Simple lowercase version."""
        return name.replace(' ', '').lower()
    
    def _remove_spaces(self, name: str) -> str:
        """Remove spaces and special characters."""
        return re.sub(r'[^a-zA-Z0-9]', '', name).lower()
    
    def _add_random_suffix(self, name: str) -> str:
        """Add random suffix."""
        clean_name = name.replace(' ', '').lower()
        suffixes = ['x', 'z', 'pro', '007', 'tech', 'dev']
        suffix = random.choice(suffixes)
        return f"{clean_name}_{suffix}"
    
    def _generate_creative_usernames(self, name: str) -> List[str]:
        """Generate creative username variations."""
        base_name = name.replace(' ', '').lower()
        creative = []
        
        # Reverse name
        creative.append(base_name[::-1])
        
        # Mix with common words
        words = ['cool', 'super', 'mega', 'ultra', 'prime']
        creative.append(f"{random.choice(words)}_{base_name}")
        
        # First letter + numbers
        if base_name:
            creative.append(f"{base_name[0]}{base_name}{random.randint(10, 99)}")
        
        # Add 'x' variations
        creative.append(f"{base_name}x{random.randint(1, 9)}")
        
        return creative[:4]
    
    def _create_variation(self, base_name: str) -> str:
        """Create a simple variation of the base name."""
        variations = [
            f"{base_name}{random.randint(100, 999)}",
            f"{base_name}_v{random.randint(1, 9)}",
            f"user_{base_name}",
            f"{base_name}_new"
        ]
        return random.choice(variations)
