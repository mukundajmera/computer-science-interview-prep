package v2_extended;

import java.util.*;

/**
 * LinkedIn Connection System - V2 Extended
 * 
 * Recommendation strategy interface and implementations.
 */
interface RecommendationStrategy {
    List<User> getRecommendations(User user, Collection<User> allUsers, int count);
}

/**
 * Recommend users with most mutual connections.
 */
class MutualConnectionsStrategy implements RecommendationStrategy {
    @Override
    public List<User> getRecommendations(User user, Collection<User> allUsers, int count) {
        Map<User, Integer> scores = new HashMap<>();
        
        for (User candidate : allUsers) {
            if (candidate.equals(user) || user.isConnectedTo(candidate)) {
                continue;
            }
            int mutualCount = user.getMutualConnections(candidate).size();
            if (mutualCount > 0) {
                scores.put(candidate, mutualCount);
            }
        }
        
        List<Map.Entry<User, Integer>> sortedList = new ArrayList<>(scores.entrySet());
        sortedList.sort((a, b) -> b.getValue().compareTo(a.getValue()));
        
        List<User> recommendations = new ArrayList<>();
        for (int i = 0; i < Math.min(count, sortedList.size()); i++) {
            recommendations.add(sortedList.get(i).getKey());
        }
        return recommendations;
    }
}

/**
 * Recommend users with shared skills.
 */
class SharedSkillsStrategy implements RecommendationStrategy {
    @Override
    public List<User> getRecommendations(User user, Collection<User> allUsers, int count) {
        Map<User, Integer> scores = new HashMap<>();
        
        for (User candidate : allUsers) {
            if (candidate.equals(user) || user.isConnectedTo(candidate)) {
                continue;
            }
            int sharedSkills = user.getCommonSkills(candidate).size();
            if (sharedSkills > 0) {
                scores.put(candidate, sharedSkills);
            }
        }
        
        List<Map.Entry<User, Integer>> sortedList = new ArrayList<>(scores.entrySet());
        sortedList.sort((a, b) -> b.getValue().compareTo(a.getValue()));
        
        List<User> recommendations = new ArrayList<>();
        for (int i = 0; i < Math.min(count, sortedList.size()); i++) {
            recommendations.add(sortedList.get(i).getKey());
        }
        return recommendations;
    }
}

/**
 * Recommend users from the same company.
 */
class SameCompanyStrategy implements RecommendationStrategy {
    @Override
    public List<User> getRecommendations(User user, Collection<User> allUsers, int count) {
        List<User> recommendations = new ArrayList<>();
        String userCompany = user.getCompany();
        
        if (userCompany == null || userCompany.isEmpty()) {
            return recommendations;
        }
        
        for (User candidate : allUsers) {
            if (candidate.equals(user) || user.isConnectedTo(candidate)) {
                continue;
            }
            if (userCompany.equalsIgnoreCase(candidate.getCompany())) {
                recommendations.add(candidate);
                if (recommendations.size() >= count) {
                    break;
                }
            }
        }
        return recommendations;
    }
}

/**
 * Combined strategy using weighted scores.
 */
class CombinedStrategy implements RecommendationStrategy {
    private static final int MUTUAL_WEIGHT = 3;
    private static final int SKILLS_WEIGHT = 2;
    private static final int COMPANY_WEIGHT = 2;

    @Override
    public List<User> getRecommendations(User user, Collection<User> allUsers, int count) {
        Map<User, Integer> scores = new HashMap<>();
        
        for (User candidate : allUsers) {
            if (candidate.equals(user) || user.isConnectedTo(candidate)) {
                continue;
            }
            
            int score = 0;
            
            // Mutual connections
            score += user.getMutualConnections(candidate).size() * MUTUAL_WEIGHT;
            
            // Shared skills
            score += user.getCommonSkills(candidate).size() * SKILLS_WEIGHT;
            
            // Same company
            if (user.getCompany() != null && !user.getCompany().isEmpty() &&
                user.getCompany().equalsIgnoreCase(candidate.getCompany())) {
                score += COMPANY_WEIGHT;
            }
            
            if (score > 0) {
                scores.put(candidate, score);
            }
        }
        
        List<Map.Entry<User, Integer>> sortedList = new ArrayList<>(scores.entrySet());
        sortedList.sort((a, b) -> b.getValue().compareTo(a.getValue()));
        
        List<User> recommendations = new ArrayList<>();
        for (int i = 0; i < Math.min(count, sortedList.size()); i++) {
            recommendations.add(sortedList.get(i).getKey());
        }
        return recommendations;
    }
}
