package v1_basic;

public class LoggingFrameworkDemo {
    public static void main(String[] args) {
        LoggerFactory factory = LoggerFactory.getInstance();
        
        Logger root = factory.getLogger("root");
        root.setLevel(LogLevel.INFO);
        
        Logger appLogger = factory.getLogger("com.app");
        appLogger.setLevel(LogLevel.DEBUG);
        
        Logger serviceLogger = factory.getLogger("com.app.service");
        
        System.out.println("Root effective level: " + root.getEffectiveLevel());
        System.out.println("com.app effective level: " + appLogger.getEffectiveLevel());
        System.out.println("com.app.service effective level: " + serviceLogger.getEffectiveLevel()); // Should inherit DEBUG
        
        root.info("This is an info message from root");
        appLogger.debug("This is a debug message from app");
        serviceLogger.trace("This trace should not be printed");
        serviceLogger.debug("This debug from service should be printed");
        
        factory.shutdown();
    }
}
