
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Arrays;

public class TestCodeJudge {

    @Test
    public void testAcVerdict() throws Exception {
        CodeJudge judge = createJudge();
        Problem p = new Problem("p1", Arrays.asList(new TestCase("1 2", "1 2")), 1000, 256000);
        judge.addProblem(p);

        Submission s = new Submission("s1", "u1", "p1", "PYTHON", "print('1 2')");
        judge.submit(s);

        Thread.sleep(500); // give time for v3
        assertEquals(Verdict.AC, judge.getVerdict("s1"));
        stopJudge(judge);
    }

    @Test
    public void testWaVerdict() throws Exception {
        CodeJudge judge = createJudge();
        Problem p = new Problem("p1", Arrays.asList(new TestCase("1 2", "1 2")), 1000, 256000);
        judge.addProblem(p);

        Submission s = new Submission("s2", "u1", "p1", "PYTHON", "WA");
        judge.submit(s);

        Thread.sleep(500);
        assertEquals(Verdict.WA, judge.getVerdict("s2"));
        stopJudge(judge);
    }

    @Test
    public void testTleVerdict() throws Exception {
        CodeJudge judge = createJudge();
        Problem p = new Problem("p1", Arrays.asList(new TestCase("1 2", "1 2")), 1000, 256000);
        judge.addProblem(p);

        Submission s = new Submission("s3", "u1", "p1", "PYTHON", "TLE");
        judge.submit(s);

        Thread.sleep(500);
        assertEquals(Verdict.TLE, judge.getVerdict("s3"));
        stopJudge(judge);
    }

    @Test
    public void testMleVerdict() throws Exception {
        CodeJudge judge = createJudge();
        Problem p = new Problem("p1", Arrays.asList(new TestCase("1 2", "1 2")), 1000, 256000);
        judge.addProblem(p);

        Submission s = new Submission("s4", "u1", "p1", "PYTHON", "MLE");
        judge.submit(s);

        Thread.sleep(500);
        assertEquals(Verdict.MLE, judge.getVerdict("s4"));
        stopJudge(judge);
    }

    @Test
    public void testReVerdict() throws Exception {
        CodeJudge judge = createJudge();
        Problem p = new Problem("p1", Arrays.asList(new TestCase("1 2", "1 2")), 1000, 256000);
        judge.addProblem(p);

        Submission s = new Submission("s5", "u1", "p1", "PYTHON", "RE");
        judge.submit(s);

        Thread.sleep(500);
        assertEquals(Verdict.RE, judge.getVerdict("s5"));
        stopJudge(judge);
    }

    @Test
    public void testCeVerdict() throws Exception {
        CodeJudge judge = createJudge();
        Submission s = new Submission("s_ce", "u1", "missing_problem", "PYTHON", "print('hi')");
        judge.submit(s);

        Thread.sleep(500);
        assertEquals(Verdict.CE, judge.getVerdict("s_ce"));
        stopJudge(judge);
    }

    @Test
    public void testMissingSubmission() {
        CodeJudge judge = createJudge();
        assertNull(judge.getVerdict("none"));
        stopJudge(judge);
    }

    private CodeJudge createJudge() {
        try {
            // Check if constructor has int parameter (v3)
            return CodeJudge.class.getConstructor(int.class).newInstance(2);
        } catch (NoSuchMethodException e) {
            try {
                return CodeJudge.class.getConstructor().newInstance();
            } catch (Exception ex) {
                throw new RuntimeException(ex);
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private void stopJudge(CodeJudge judge) {
        try {
            judge.getClass().getMethod("stop").invoke(judge);
        } catch (NoSuchMethodException e) {
            // ignore for v1 and v2
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
