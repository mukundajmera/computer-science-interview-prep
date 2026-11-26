import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.lang.reflect.Method;
import java.lang.reflect.Constructor;
import static org.junit.jupiter.api.Assertions.*;

public class OnlineCodeJudgeAll_versionsTest {
    @Test
    public void testTerminalVerdictDoesNotChangeV2() throws Exception {
        Class<?> judgeClass = Class.forName("CodeJudge");
        Class<?> problemClass = Class.forName("Problem");
        Class<?> testCaseClass = Class.forName("TestCase");
        Class<?> submissionClass = Class.forName("Submission");
        Class<?> verdictClass = Class.forName("Verdict");
        
        Constructor<?> judgeConstructor = judgeClass.getConstructor();
        Object judge = judgeConstructor.newInstance();
        
        Constructor<?> tcConstructor = testCaseClass.getConstructor(String.class, String.class);
        Object tc = tcConstructor.newInstance("in", "out");
        
        Constructor<?> probConstructor = problemClass.getConstructor(String.class, List.class, int.class, int.class);
        Object problem = probConstructor.newInstance("p1", Collections.singletonList(tc), 1000, 100000);
        
        Method addProblemMethod = judgeClass.getMethod("addProblem", problemClass);
        addProblemMethod.invoke(judge, problem);
        
        Constructor<?> subConstructor = submissionClass.getConstructor(String.class, String.class, String.class, String.class, String.class);
        Object submission = subConstructor.newInstance("s1", "u1", "p1", "PYTHON", "TLE");
        
        Method submitMethod = judgeClass.getMethod("submit", submissionClass);
        submitMethod.invoke(judge, submission);
        
        Method getVerdictMethod = submissionClass.getMethod("getVerdict");
        Object verdict = getVerdictMethod.invoke(submission);
        
        Object expectedVerdict = Enum.valueOf((Class<Enum>) verdictClass, "TLE");
        assertEquals(expectedVerdict, verdict);
        
        Method updateVerdictMethod = submissionClass.getMethod("updateVerdict", verdictClass);
        Object newVerdict = Enum.valueOf((Class<Enum>) verdictClass, "AC");
        boolean updated = (boolean) updateVerdictMethod.invoke(submission, newVerdict);
        
        assertFalse(updated);
        
        Object finalVerdict = getVerdictMethod.invoke(submission);
        assertEquals(expectedVerdict, finalVerdict);
    }

    @Test
    public void testTerminalVerdictDoesNotChangeV3() throws Exception {
        Class<?> judgeClass = Class.forName("OnlineCodeJudge");
        Class<?> problemClass = Class.forName("OnlineCodeJudge$Problem");
        Class<?> testCaseClass = Class.forName("OnlineCodeJudge$TestCase");
        Class<?> submissionClass = Class.forName("OnlineCodeJudge$Submission");
        Class<?> verdictClass = Class.forName("OnlineCodeJudge$Verdict");
        
        Constructor<?> judgeConstructor = judgeClass.getConstructor(int.class);
        Object judge = judgeConstructor.newInstance(2);
        
        Constructor<?> tcConstructor = testCaseClass.getConstructor(String.class, String.class);
        Object tc = tcConstructor.newInstance("in", "out");
        
        Constructor<?> probConstructor = problemClass.getConstructor(String.class, List.class, int.class, int.class);
        Object problem = probConstructor.newInstance("p1", Collections.singletonList(tc), 1000, 100000);
        
        Method addProblemMethod = judgeClass.getMethod("addProblem", problemClass);
        addProblemMethod.invoke(judge, problem);
        
        Constructor<?> subConstructor = submissionClass.getConstructor(String.class, String.class, String.class, String.class, String.class);
        Object submission = subConstructor.newInstance("s1", "u1", "p1", "PYTHON", "TLE");
        
        Method submitMethod = judgeClass.getMethod("submit", submissionClass);
        submitMethod.invoke(judge, submission);
        
        Thread.sleep(500);
        
        Method getVerdictMethod = submissionClass.getMethod("getVerdict");
        Object verdict = getVerdictMethod.invoke(submission);
        
        Object expectedVerdict = Enum.valueOf((Class<Enum>) verdictClass, "TLE");
        assertEquals(expectedVerdict, verdict);
        
        Method updateVerdictMethod = submissionClass.getMethod("updateVerdict", verdictClass);
        Object newVerdict = Enum.valueOf((Class<Enum>) verdictClass, "AC");
        boolean updated = (boolean) updateVerdictMethod.invoke(submission, newVerdict);
        
        assertFalse(updated);
        
        Object finalVerdict = getVerdictMethod.invoke(submission);
        assertEquals(expectedVerdict, finalVerdict);
        
        Method stopMethod = judgeClass.getMethod("stop");
        stopMethod.invoke(judge);
    }
}
