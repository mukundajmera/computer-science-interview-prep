import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import singleton.v1.Singleton;
import singleton.v1.Singleton;
import singleton.v1.Singleton;
import java.lang.reflect.Method;
import java.lang.reflect.InvocationTargetException;

public class SingletonTest {

    @Test
    @DisplayName("Singleton.getInstance() returns the exact same instance")
    void testSingletonReturnsSameInstance() {
        Singleton instance1 = Singleton.getInstance();
        Singleton instance2 = Singleton.getInstance();

        assertNotNull(instance1);
        assertSame(instance1, instance2);
    }

    @Test
    @DisplayName("Singleton method execution runs without exception")
    void testSingletonMethodExecution() {
        Singleton instance = Singleton.getInstance();
        assertDoesNotThrow(() -> instance.doSomething());
    }

    @Test
    @DisplayName("Singleton clone method throws CloneNotSupportedException")
    void testSingletonCloneThrowsException() throws Exception {
        Singleton instance = Singleton.getInstance();
        Method cloneMethod = Singleton.class.getDeclaredMethod("clone");
        cloneMethod.setAccessible(true);

        InvocationTargetException thrown = assertThrows(InvocationTargetException.class, () -> {
            cloneMethod.invoke(instance);
        });
        assertTrue(thrown.getCause() instanceof CloneNotSupportedException);
    }
}
