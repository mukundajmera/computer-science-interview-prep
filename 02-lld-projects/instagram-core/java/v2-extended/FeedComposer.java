import java.util.List;
import java.util.ArrayList;
import java.util.Set;
import java.util.HashSet;
import java.util.Map;
import java.util.HashMap;
import java.util.Comparator;

public class FeedComposer {
    private final MediaPostServiceV2 postService;
    private final FollowGraphService followGraph;

    public FeedComposer(MediaPostServiceV2 postService, FollowGraphService followGraph) {
        this.postService = postService;
        this.followGraph = followGraph;
    }

    public List<PostMetadata> composeFeed(String userId, String cursor, int limit) {
        List<PostMetadata> standardFeed = postService.getUserFeed(userId);
        Set<String> validFollowees = followGraph.getFollowees(userId);

        List<PostMetadata> filteredStandard = new ArrayList<>();
        for (PostMetadata p : standardFeed) {
            if ((p.getUserId().equals(userId) || validFollowees.contains(p.getUserId())) && postService.getPost(p.getPostId()).isPresent()) {
                filteredStandard.add(p);
            }
        }

        Set<String> celebrityFollowees = new HashSet<>();
        for (String uid : validFollowees) {
            if (followGraph.isCelebrity(uid)) {
                celebrityFollowees.add(uid);
            }
        }

        List<PostMetadata> celebrityPosts = new ArrayList<>();
        for (PostMetadata post : postService.getAllPosts().values()) {
            if (celebrityFollowees.contains(post.getUserId())) {
                celebrityPosts.add(post);
            }
        }

        Map<String, PostMetadata> allPostsMap = new HashMap<>();
        for (PostMetadata p : filteredStandard) {
            allPostsMap.put(p.getPostId(), p);
        }
        for (PostMetadata p : celebrityPosts) {
            allPostsMap.put(p.getPostId(), p);
        }

        List<PostMetadata> allPosts = new ArrayList<>();
        for (PostMetadata p : allPostsMap.values()) {
            boolean isPrivate = followGraph.isPrivate(p.getUserId());
            if (!isPrivate || p.getUserId().equals(userId) || validFollowees.contains(p.getUserId())) {
                allPosts.add(p);
            }
        }

        allPosts.sort((p1, p2) -> {
            int timeCmp = Long.compare(p2.getTimestamp(), p1.getTimestamp());
            if (timeCmp != 0) {
                return timeCmp;
            }
            return p2.getPostId().compareTo(p1.getPostId());
        });

        if (cursor != null && !cursor.isEmpty()) {
            String[] parts = cursor.split("_");
            long cursorTimestamp = Long.parseLong(parts[0]);
            String cursorPostId = parts[1];

            List<PostMetadata> filtered = new ArrayList<>();
            for (PostMetadata p : allPosts) {
                if (p.getTimestamp() < cursorTimestamp || 
                   (p.getTimestamp() == cursorTimestamp && p.getPostId().compareTo(cursorPostId) < 0)) {
                    filtered.add(p);
                }
            }
            allPosts = filtered;
        }

        return allPosts.size() > limit ? allPosts.subList(0, limit) : allPosts;
    }
}
