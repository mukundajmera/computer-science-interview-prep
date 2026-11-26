package v1_basic;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class PostSearchService {
    // Map of postId to Post
    private final Map<String, Post> posts = new ConcurrentHashMap<>();
    
    // Inverted index: term -> set of postIds
    private final Map<String, Set<String>> invertedIndex = new ConcurrentHashMap<>();
    
    // Stop words
    private static final Set<String> STOP_WORDS = Set.of(
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "is", "are", "was", "were"
    );
    
    // Pattern to match words
    private static final Pattern WORD_PATTERN = Pattern.compile("\\b\\w+\\b");

    private List<String> tokenizeAndFilter(String content) {
        if (content == null) {
            return Collections.emptyList();
        }
        
        List<String> tokens = new ArrayList<>();
        var matcher = WORD_PATTERN.matcher(content.toLowerCase());
        while (matcher.find()) {
            String token = matcher.group();
            if (!STOP_WORDS.contains(token)) {
                tokens.add(token);
            }
        }
        return tokens;
    }

    public void indexPost(Post post) {
        if (post == null || post.getPostId() == null) {
            return;
        }
        
        posts.put(post.getPostId(), post);
        
        // Index content words
        List<String> tokens = tokenizeAndFilter(post.getContent());
        for (String token : tokens) {
            invertedIndex.computeIfAbsent(token, k -> ConcurrentHashMap.newKeySet()).add(post.getPostId());
        }
        
        // Index tags
        if (post.getTags() != null) {
            for (String tag : post.getTags()) {
                if (tag != null && !tag.trim().isEmpty()) {
                    invertedIndex.computeIfAbsent(tag.toLowerCase(), k -> ConcurrentHashMap.newKeySet()).add(post.getPostId());
                }
            }
        }
    }

    public List<Post> searchByKeyword(String keyword, int limit) {
        if (keyword == null || keyword.trim().isEmpty()) {
            return Collections.emptyList();
        }
        
        List<String> tokens = tokenizeAndFilter(keyword);
        if (tokens.isEmpty()) {
            return Collections.emptyList();
        }
        
        String term = tokens.get(0);
        Set<String> postIds = invertedIndex.getOrDefault(term, Collections.emptySet());
        
        return postIds.stream()
                .map(posts::get)
                .filter(Objects::nonNull)
                .sorted(Comparator.comparing(Post::getTimestamp).reversed())
                .limit(limit)
                .collect(Collectors.toList());
    }

    public List<Post> searchByTag(String tag, int limit) {
        if (tag == null || tag.trim().isEmpty()) {
            return Collections.emptyList();
        }
        
        Set<String> postIds = invertedIndex.getOrDefault(tag.toLowerCase(), Collections.emptySet());
        
        return postIds.stream()
                .map(posts::get)
                .filter(Objects::nonNull)
                .sorted(Comparator.comparing(Post::getTimestamp).reversed())
                .limit(limit)
                .collect(Collectors.toList());
    }

    public List<Post> searchBooleanAnd(List<String> keywords, int limit) {
        if (keywords == null || keywords.isEmpty()) {
            return Collections.emptyList();
        }
        
        List<String> allTokens = new ArrayList<>();
        for (String keyword : keywords) {
            allTokens.addAll(tokenizeAndFilter(keyword));
        }
        
        if (allTokens.isEmpty()) {
            return Collections.emptyList();
        }
        
        Set<String> resultIds = new HashSet<>(invertedIndex.getOrDefault(allTokens.get(0), Collections.emptySet()));
        
        for (int i = 1; i < allTokens.size(); i++) {
            Set<String> currentIds = invertedIndex.getOrDefault(allTokens.get(i), Collections.emptySet());
            resultIds.retainAll(currentIds);
            if (resultIds.isEmpty()) {
                break;
            }
        }
        
        return resultIds.stream()
                .map(posts::get)
                .filter(Objects::nonNull)
                .sorted(Comparator.comparing(Post::getTimestamp).reversed())
                .limit(limit)
                .collect(Collectors.toList());
    }

    public void deletePost(String postId) {
        if (postId == null) {
            return;
        }
        
        Post post = posts.remove(postId);
        if (post != null) {
            // Remove from content index
            List<String> tokens = tokenizeAndFilter(post.getContent());
            for (String token : tokens) {
                Set<String> postIds = invertedIndex.get(token);
                if (postIds != null) {
                    postIds.remove(postId);
                }
            }
            
            // Remove from tags index
            if (post.getTags() != null) {
                for (String tag : post.getTags()) {
                    if (tag != null && !tag.trim().isEmpty()) {
                        Set<String> postIds = invertedIndex.get(tag.toLowerCase());
                        if (postIds != null) {
                            postIds.remove(postId);
                        }
                    }
                }
            }
        }
    }
}