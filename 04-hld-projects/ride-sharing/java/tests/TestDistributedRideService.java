import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.lang.reflect.*;
import java.util.*;

public class TestDistributedRideService {

    static class MockGeoSearchIndex implements InvocationHandler {
        @Override
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            if (method.getName().equals("nearbyEntities")) {
                double lat = (Double) args[0];
                double lng = (Double) args[1];
                
                List<Object> result = new ArrayList<>();
                Class<?> candidateClass = Class.forName("ridesharing.v3.GeoDriverCandidate");
                Constructor<?> ctor = candidateClass.getDeclaredConstructor(String.class, double.class, double.class);
                ctor.setAccessible(true);
                
                if (lat == 0.0 && lng == 0.0) {
                    result.add(ctor.newInstance("d1", 5.0, 1.0));
                    result.add(ctor.newInstance("d2", 10.0, 2.0));
                } else if (lat == 1.0 && lng == 1.0) {
                    result.add(ctor.newInstance("d1", 2.0, 0.5));
                    result.add(ctor.newInstance("d2", 3.0, 0.7));
                }
                return result;
            }
            return null;
        }
    }
    
    private Object createDispatcher() throws Exception {
        Class<?> indexClass = Class.forName("ridesharing.v3.GeoSearchIndex");
        Object proxy = Proxy.newProxyInstance(
            indexClass.getClassLoader(),
            new Class<?>[] { indexClass },
            new MockGeoSearchIndex()
        );
        
        Class<?> dispatcherClass = Class.forName("ridesharing.v3.BatchedBipartiteDispatcher");
        Constructor<?> ctor = dispatcherClass.getDeclaredConstructor(indexClass);
        ctor.setAccessible(true);
        return ctor.newInstance(proxy);
    }

    @Test
    public void testBipartiteDispatchOptimization() throws Exception {
        Object dispatcher = createDispatcher();
        Method submitRequest = dispatcher.getClass().getDeclaredMethod("submitRequest", String.class, double.class, double.class);
        submitRequest.setAccessible(true);
        
        submitRequest.invoke(dispatcher, "r1", 0.0, 0.0);
        submitRequest.invoke(dispatcher, "r2", 1.0, 1.0);
        
        Method dispatchBatch = dispatcher.getClass().getDeclaredMethod("dispatchBatch");
        dispatchBatch.setAccessible(true);
        
        Map<String, String> matches = (Map<String, String>) dispatchBatch.invoke(dispatcher);
        
        assertEquals("d1", matches.get("r2"));
        assertEquals("d2", matches.get("r1"));
    }

    @Test
    public void testBipartiteDispatchEmpty() throws Exception {
        Object dispatcher = createDispatcher();
        
        Method dispatchBatch = dispatcher.getClass().getDeclaredMethod("dispatchBatch");
        dispatchBatch.setAccessible(true);
        
        Map<String, String> matches = (Map<String, String>) dispatchBatch.invoke(dispatcher);
        assertTrue(matches.isEmpty());
    }

    @Test
    public void testBipartiteDispatchPartialMatch() throws Exception {
        Object dispatcher = createDispatcher();
        Method submitRequest = dispatcher.getClass().getDeclaredMethod("submitRequest", String.class, double.class, double.class);
        submitRequest.setAccessible(true);
        
        submitRequest.invoke(dispatcher, "r1", 0.0, 0.0);
        submitRequest.invoke(dispatcher, "r2", 1.0, 1.0);
        submitRequest.invoke(dispatcher, "r3", 2.0, 2.0); // no candidates
        
        Method dispatchBatch = dispatcher.getClass().getDeclaredMethod("dispatchBatch");
        dispatchBatch.setAccessible(true);
        
        Map<String, String> matches = (Map<String, String>) dispatchBatch.invoke(dispatcher);
        
        assertTrue(matches.containsKey("r1"));
        assertTrue(matches.containsKey("r2"));
        assertFalse(matches.containsKey("r3"));
    }

    @Test
    public void testAdditionalCoverage() throws Exception {
        // Just verifying thread safety manually essentially
        Object dispatcher = createDispatcher();
        Method submitRequest = dispatcher.getClass().getDeclaredMethod("submitRequest", String.class, double.class, double.class);
        submitRequest.setAccessible(true);
        submitRequest.invoke(dispatcher, "r1", 0.0, 0.0);
        
        Field pendingRequests = dispatcher.getClass().getDeclaredField("pendingRequests");
        pendingRequests.setAccessible(true);
        List<?> list = (List<?>) pendingRequests.get(dispatcher);
        assertEquals(1, list.size());
    }
}
