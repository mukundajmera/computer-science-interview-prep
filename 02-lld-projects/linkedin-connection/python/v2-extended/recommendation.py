"""
LinkedIn Connection System - V2 Extended

Recommendation strategies.
"""
from abc import ABC, abstractmethod
from typing import List, Collection
from user import User


class RecommendationStrategy(ABC):
    """Interface for recommendation strategies."""
    
    @abstractmethod
    def get_recommendations(self, user: User, all_users: Collection[User], 
                           count: int) -> List[User]:
        pass


class MutualConnectionsStrategy(RecommendationStrategy):
    """Recommend users with most mutual connections."""
    
    def get_recommendations(self, user: User, all_users: Collection[User], 
                           count: int) -> List[User]:
        scores = {}
        
        for candidate in all_users:
            if candidate == user or user.is_connected_to(candidate):
                continue
            mutual_count = len(user.get_mutual_connections(candidate))
            if mutual_count > 0:
                scores[candidate] = mutual_count
        
        sorted_users = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [u for u, _ in sorted_users[:count]]


class SharedSkillsStrategy(RecommendationStrategy):
    """Recommend users with shared skills."""
    
    def get_recommendations(self, user: User, all_users: Collection[User], 
                           count: int) -> List[User]:
        scores = {}
        
        for candidate in all_users:
            if candidate == user or user.is_connected_to(candidate):
                continue
            shared = len(user.get_common_skills(candidate))
            if shared > 0:
                scores[candidate] = shared
        
        sorted_users = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [u for u, _ in sorted_users[:count]]


class CombinedStrategy(RecommendationStrategy):
    """Combined strategy with weighted scores."""
    
    MUTUAL_WEIGHT = 3
    SKILLS_WEIGHT = 2
    COMPANY_WEIGHT = 2
    
    def get_recommendations(self, user: User, all_users: Collection[User], 
                           count: int) -> List[User]:
        scores = {}
        
        for candidate in all_users:
            if candidate == user or user.is_connected_to(candidate):
                continue
            
            score = 0
            score += len(user.get_mutual_connections(candidate)) * self.MUTUAL_WEIGHT
            score += len(user.get_common_skills(candidate)) * self.SKILLS_WEIGHT
            
            if user.company and user.company.lower() == candidate.company.lower():
                score += self.COMPANY_WEIGHT
            
            if score > 0:
                scores[candidate] = score
        
        sorted_users = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [u for u, _ in sorted_users[:count]]
