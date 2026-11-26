
public class VideoRank {
    private final String videoId;
    private final long viewCount;
    private final int rank;

    public VideoRank(String videoId, long viewCount, int rank) {
        this.videoId = videoId;
        this.viewCount = viewCount;
        this.rank = rank;
    }

    public String getVideoId() {
        return videoId;
    }

    public long getViewCount() {
        return viewCount;
    }

    public int getRank() {
        return rank;
    }
}
