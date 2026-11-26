package v2_extended;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class RollingFileAppender implements Appender {
    private final String name;
    private final String filePath;
    private final long maxSizeBytes;
    private final int backupCount;
    private final Formatter formatter;
    private final Lock lock = new ReentrantLock();

    public RollingFileAppender(String name, String filePath, long maxSizeBytes, int backupCount, Formatter formatter) {
        this.name = name;
        this.filePath = filePath;
        this.maxSizeBytes = maxSizeBytes;
        this.backupCount = backupCount;
        this.formatter = formatter != null ? formatter : new PatternFormatter("[%d{yyyy-MM-dd HH:mm:ss}] [%t] %-5level %logger - %msg%n");
    }

    @Override
    public void append(LogEvent event) {
        lock.lock();
        try {
            String msg = formatter.format(event) + "\n";
            File file = new File(filePath);
            if (file.exists() && file.length() + msg.getBytes().length > maxSizeBytes) {
                rollOver();
            }
            try (FileWriter writer = new FileWriter(file, true)) {
                writer.write(msg);
            } catch (IOException e) {
                e.printStackTrace();
            }
        } finally {
            lock.unlock();
        }
    }

    private void rollOver() {
        for (int i = backupCount - 1; i > 0; i--) {
            File sfn = new File(filePath + "." + i);
            File dfn = new File(filePath + "." + (i + 1));
            if (sfn.exists()) {
                if (dfn.exists()) {
                    dfn.delete();
                }
                sfn.renameTo(dfn);
            }
        }
        File dfn = new File(filePath + ".1");
        if (dfn.exists()) {
            dfn.delete();
        }
        File file = new File(filePath);
        if (file.exists()) {
            file.renameTo(dfn);
        }
    }

    @Override
    public String getName() {
        return name;
    }
}
