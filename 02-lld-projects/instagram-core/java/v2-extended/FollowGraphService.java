import java.util.Set;
import java.util.HashSet;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Collections;

public class FollowGraphService {
    private final int celebrityThreshold;
    private final Map<String, Set<String>> followers = new ConcurrentHashMap<>();
    private final Map<String, Set<String>> followees = new ConcurrentHashMap<>();
    private final Map<String, Boolean> privacy = new ConcurrentHashMap<>();

    public FollowGraphService(int celebrityThreshold) {
        this.celebrityThreshold = celebrityThreshold;
    }

    public void follow(String followerId, String followeeId) {
        followers.computeIfAbsent(followeeId, k -> Collections.synchronizedSet(new HashSet<>())).add(followerId);
        followees.computeIfAbsent(followerId, k -> Collections.synchronizedSet(new HashSet<>())).add(followeeId);
    }

    public void unfollow(String followerId, String followeeId) {
        Set<String> followerSet = followers.get(followeeId);
        if (followerSet != null) followerSet.remove(followerId);

        Set<String> followeeSet = followees.get(followerId);
        if (followeeSet != null) followeeSet.remove(followeeId);
    }

    public Set<String> getFollowers(String userId) {
        return followers.getOrDefault(userId, Collections.emptySet());
    }

    public Set<String> getFollowees(String userId) {
        return followees.getOrDefault(userId, Collections.emptySet());
    }
    
    public boolean isCelebrity(String userId) {
        return getFollowers(userId).size() >= celebrityThreshold;
    }

    public void setPrivacy(String userId, boolean isPrivate) {
        privacy.put(userId, isPrivate);
    }
    
    public boolean isPrivate(String userId) {
        return privacy.getOrDefault(userId, false);
    }
}
