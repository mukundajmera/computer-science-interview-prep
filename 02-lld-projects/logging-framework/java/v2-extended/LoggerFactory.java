package v2_extended;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class LoggerFactory {
    private static LoggerFactory instance;
    private final Map<String, Logger> loggers;
    private final Logger rootLogger;
    private final AsyncLogProcessor asyncProcessor;

    private LoggerFactory() {
        loggers = new ConcurrentHashMap<>();
        // Default async processor with capacity 10000
        asyncProcessor = new AsyncLogProcessor(10000);
        
        // Setup root logger
        rootLogger = new Logger("root", null, asyncProcessor);
        rootLogger.setLevel(LogLevel.INFO);
        // By default, add a console appender to root
        rootLogger.addAppender(new ConsoleAppender("Console"));
        loggers.put("root", rootLogger);
    }

    public static synchronized LoggerFactory getInstance() {
        if (instance == null) {
            instance = new LoggerFactory();
        }
        return instance;
    }
    
    // For testing, allows resetting the factory
    public static synchronized void reset() {
        if (instance != null) {
            instance.shutdown();
            instance = null;
        }
    }

    public Logger getLogger(String name) {
        if (name == null || name.isEmpty() || "root".equalsIgnoreCase(name)) {
            return rootLogger;
        }

        // Avoid ConcurrentHashMap recursive update by checking first
        Logger logger = loggers.get(name);
        if (logger != null) {
            return logger;
        }
        
        // Use synchronized block to prevent concurrent recursive creation issues
        synchronized(this) {
            logger = loggers.get(name);
            if (logger == null) {
                logger = createLogger(name);
                loggers.put(name, logger);
            }
            return logger;
        }
    }

    private Logger createLogger(String name) {
        int lastDotIndex = name.lastIndexOf('.');
        Logger parent;
        if (lastDotIndex == -1) {
            parent = rootLogger;
        } else {
            String parentName = name.substring(0, lastDotIndex);
            parent = getLogger(parentName); // Ensure parent exists
        }
        return new Logger(name, parent, asyncProcessor);
    }
    
    public void shutdown() {
        if (asyncProcessor != null) {
            asyncProcessor.stop();
        }
    }
}
