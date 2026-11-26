
public class Submission {
    private String id;
    private String userId;
    private String problemId;
    private String language;
    private String code;
    private Verdict verdict;

    public Submission(String id, String userId, String problemId, String language, String code) {
        this.id = id;
        this.userId = userId;
        this.problemId = problemId;
        this.language = language;
        this.code = code;
        this.verdict = Verdict.PENDING;
    }

    public String getId() { return id; }
    public String getProblemId() { return problemId; }
    public String getLanguage() { return language; }
    public String getCode() { return code; }
    public Verdict getVerdict() { return verdict; }
    public boolean updateVerdict(Verdict verdict) {
        if (this.verdict != Verdict.PENDING) {
            return false;
        }
        this.verdict = verdict;
        return true;
    }
}
