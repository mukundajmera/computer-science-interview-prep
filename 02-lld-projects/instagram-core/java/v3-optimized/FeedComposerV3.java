import java.util.List;
import java.util.ArrayList;
import java.util.Set;
import java.util.HashSet;
import java.util.Map;
import java.util.HashMap;

public class FeedComposerV3 {
    private final MediaPostServiceV3 postService;
    private final FollowGraphServiceV3 followGraph;

    public FeedComposerV3(MediaPostServiceV3 postService, FollowGraphServiceV3 followGraph) {
        this.postService = postService;
        this.followGraph = followGraph;
    }

    public List<PostMetadataV3> composeFeed(String userId, String cursor, int limit) {
        List<PostMetadataV3> standardFeed = postService.getUserFeed(userId);
        Set<String> validFollowees = followGraph.getFollowees(userId);

        List<PostMetadataV3> filteredStandard = new ArrayList<>();
        for (PostMetadataV3 p : standardFeed) {
            if ((p.getUserId().equals(userId) || validFollowees.contains(p.getUserId())) && postService.get(p.getPostId(), p.getRegion()).isPresent()) {
                filteredStandard.add(p);
            }
        }

        Set<String> celebrityFollowees = new HashSet<>();
        for (String uid : validFollowees) {
            if (followGraph.isCelebrity(uid)) {
                celebrityFollowees.add(uid);
            }
        }

        List<PostMetadataV3> celebrityPosts = new ArrayList<>();
        for (PostMetadataV3 post : postService.getAllPosts().values()) {
            if (celebrityFollowees.contains(post.getUserId())) {
                celebrityPosts.add(post);
            }
        }

        Map<String, PostMetadataV3> allPostsMap = new HashMap<>();
        for (PostMetadataV3 p : filteredStandard) {
            allPostsMap.put(p.getPostId(), p);
        }
        for (PostMetadataV3 p : celebrityPosts) {
            allPostsMap.put(p.getPostId(), p);
        }

        List<PostMetadataV3> allPosts = new ArrayList<>();
        for (PostMetadataV3 p : allPostsMap.values()) {
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

            List<PostMetadataV3> filtered = new ArrayList<>();
            for (PostMetadataV3 p : allPosts) {
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
