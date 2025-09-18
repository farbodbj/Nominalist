
import os
from typing import List, Tuple
import re
from openai import OpenAI
from src.services.database_service import DatabaseService

class ReviewerAgent:
    """AI-powered agent responsible for reviewing and ranking username candidates."""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.client = OpenAI(base_url = os.getenv("OPENAI_BASE_URL"))
    
    def review_and_rank(self, input_name: str, usernames: List[str]) -> List[str]:
        """
        Review usernames, filter out existing ones, and return top 3.
        """
        # Filter out existing usernames
        available_usernames = self._filter_existing_usernames(usernames)
        
        if not available_usernames:
            return []
        
        # Use AI to enhance ranking, combined with rule-based scoring
        ranked_usernames = self._ai_enhanced_ranking(input_name, available_usernames)
        
        # Return top 3
        return ranked_usernames[:3]
    
    def _filter_existing_usernames(self, usernames: List[str]) -> List[str]:
        """Filter out usernames that already exist in the database."""
        existing_usernames = self.db_service.check_multiple_usernames(usernames)
        return [u for u in usernames if u.lower() not in existing_usernames]
    
    def _ai_enhanced_ranking(self, input_name: str, usernames: List[str]) -> List[str]:
        """
        Use AI to enhance ranking combined with traditional scoring.
        """
        try:
            # Get AI evaluation
            ai_rankings = self._get_ai_ranking(input_name, usernames)
            
            # Get traditional scoring
            traditional_scores = {}
            for username in usernames:
                traditional_scores[username] = self._calculate_traditional_score(username)
            
            # Combine AI and traditional scoring
            combined_scores = {}
            for username in usernames:
                ai_score = ai_rankings.get(username, 50)  # Default middle score
                traditional_score = traditional_scores[username]
                
                # Weighted combination: 60% AI, 40% traditional
                combined_score = (ai_score * 0.6) + (traditional_score * 0.4)
                combined_scores[username] = combined_score
            
            # Sort by combined score
            sorted_usernames = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
            return [username for username, _ in sorted_usernames]
            
        except Exception as e:
            print(f"AI ranking failed: {e}")
            # Fallback to traditional ranking
            return self._rank_usernames_traditional(usernames)
    
    def _get_ai_ranking(self, input_name: str, usernames: List[str]) -> dict:
        """Get AI-based ranking of usernames."""
        try:
            usernames_text = '\n'.join([f"{i+1}. {username}" for i, username in enumerate(usernames)])
            
            prompt = f"""
            Evaluate and score these usernames for a given input name from 0-100 based on:
            - Memorability and ease of remembering
            - Professional appearance
            - Ease of typing and pronunciation
            - Uniqueness and creativity
            - Overall appeal for social media/professional use
            - Alignment with the input name of the user 
            
            Input name: {input_name}
            Usernames to evaluate: {usernames_text}
            
            Respond with ONLY the scores in this exact format:
            username1: score
            username2: score
            ...
            
            Example format:
            john_dev: 85
            sarah_codes: 92
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            # Parse AI response
            ai_scores = {}
            content = response.choices[0].message.content.strip()
            
            for line in content.split('\n'):
                if ':' in line:
                    try:
                        username, score_str = line.split(':', 1)
                        username = username.strip()
                        score = int(score_str.strip())
                        ai_scores[username] = min(100, max(0, score))  # Clamp between 0-100
                    except (ValueError, IndexError):
                        continue
            
            return ai_scores
            
        except Exception as e:
            print(f"AI scoring failed: {e}")
            return {}
    
    def _rank_usernames_traditional(self, usernames: List[str]) -> List[str]:
        """Traditional ranking method as fallback."""
        scored_usernames = []
        
        for username in usernames:
            score = self._calculate_traditional_score(username)
            scored_usernames.append((username, score))
        
        # Sort by score (descending)
        scored_usernames.sort(key=lambda x: x[1], reverse=True)
        
        return [username for username, _ in scored_usernames]
    
    def _calculate_traditional_score(self, username: str) -> int:
        """
        Calculate a traditional quality score for a username.
        Returns score 0-100 for consistency with AI scoring.
        """
        score = 50  # Base score
        
        # Length scoring (6-15 characters is optimal)
        length = len(username)
        if 6 <= length <= 15:
            score += 20
        elif 4 <= length <= 20:
            score += 10
        else:
            score -= 10
        
        # Avoid too many numbers
        number_count = len(re.findall(r'\d', username))
        if number_count <= 2:
            score += 10
        else:
            score -= 5
        
        # Prefer readable patterns
        if re.match(r'^[a-zA-Z][a-zA-Z0-9_]*', username):
            score += 5
        else:
            score -= 5
        
        return score 