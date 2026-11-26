package abstractfactory.v3;

import java.util.HashMap;
import java.util.Map;

/**
 * v3-advanced: Extensible Cloud Infrastructure Abstract Factory with Dynamic Registry.
 * Enforces multi-cloud compatibility across compute, storage, and secrets management,
 * paired with a thread-safe factory registry.
 */
public class CloudResourceFactoryDemo {

    public interface ComputeInstance {
        String launch(String instanceType);
        String getStatus();
    }

    public interface ObjectStorage {
        void putObject(String bucket, String key, byte[] data);
        byte[] getObject(String bucket, String key);
    }

    public interface KeyVault {
        void setSecret(String key, String secret);
        String getSecret(String key);
    }

    public interface CloudFactory {
        String getCloudProvider();
        ComputeInstance createCompute();
        ObjectStorage createStorage();
        KeyVault createKeyVault();
    }

    // --- AWS Family ---

    public static class Ec2ComputeInstance implements ComputeInstance {
        private String status = "STOPPED";

        @Override
        public String launch(String instanceType) {
            this.status = "RUNNING";
            return "aws-ec2-" + instanceType + "-launched";
        }

        @Override
        public String getStatus() {
            return status;
        }
    }

    public static class S3ObjectStorage implements ObjectStorage {
        private final Map<String, byte[]> store = new HashMap<>();

        @Override
        public void putObject(String bucket, String key, byte[] data) {
            store.put(bucket + "/" + key, data);
        }

        @Override
        public byte[] getObject(String bucket, String key) {
            return store.get(bucket + "/" + key);
        }
    }

    public static class AwsSecretsManager implements KeyVault {
        private final Map<String, String> secrets = new HashMap<>();

        @Override
        public void setSecret(String key, String secret) {
            secrets.put(key, secret);
        }

        @Override
        public String getSecret(String key) {
            return secrets.get(key);
        }
    }

    public static class AwsCloudFactory implements CloudFactory {
        @Override
        public String getCloudProvider() {
            return "AWS";
        }

        @Override
        public ComputeInstance createCompute() {
            return new Ec2ComputeInstance();
        }

        @Override
        public ObjectStorage createStorage() {
            return new S3ObjectStorage();
        }

        @Override
        public KeyVault createKeyVault() {
            return new AwsSecretsManager();
        }
    }

    // --- GCP Family ---

    public static class GceComputeInstance implements ComputeInstance {
        private String status = "TERMINATED";

        @Override
        public String launch(String instanceType) {
            this.status = "ACTIVE";
            return "gcp-gce-" + instanceType + "-provisioned";
        }

        @Override
        public String getStatus() {
            return status;
        }
    }

    public static class GcsObjectStorage implements ObjectStorage {
        private final Map<String, byte[]> store = new HashMap<>();

        @Override
        public void putObject(String bucket, String key, byte[] data) {
            store.put(bucket + "/" + key, data);
        }

        @Override
        public byte[] getObject(String bucket, String key) {
            return store.get(bucket + "/" + key);
        }
    }

    public static class GcpSecretManager implements KeyVault {
        private final Map<String, String> secrets = new HashMap<>();

        @Override
        public void setSecret(String key, String secret) {
            secrets.put(key, secret);
        }

        @Override
        public String getSecret(String key) {
            return secrets.get(key);
        }
    }

    public static class GcpCloudFactory implements CloudFactory {
        @Override
        public String getCloudProvider() {
            return "GCP";
        }

        @Override
        public ComputeInstance createCompute() {
            return new GceComputeInstance();
        }

        @Override
        public ObjectStorage createStorage() {
            return new GcsObjectStorage();
        }

        @Override
        public KeyVault createKeyVault() {
            return new GcpSecretManager();
        }
    }

    // --- Dynamic Provider Registry ---

    public static class CloudProviderRegistry {
        private static final Map<String, CloudFactory> FACTORIES = new HashMap<>();

        static {
            register("aws", new AwsCloudFactory());
            register("gcp", new GcpCloudFactory());
        }

        public static synchronized void register(String providerName, CloudFactory factory) {
            FACTORIES.put(providerName.toLowerCase(), factory);
        }

        public static synchronized CloudFactory getFactory(String providerName) {
            CloudFactory factory = FACTORIES.get(providerName.toLowerCase());
            if (factory == null) {
                throw new IllegalArgumentException("Unknown cloud provider: " + providerName);
            }
            return factory;
        }
    }

    public static void main(String[] args) {
        CloudFactory awsFactory = CloudProviderRegistry.getFactory("aws");
        ComputeInstance vm = awsFactory.createCompute();
        String id = vm.launch("t3.medium");
        System.out.println("Launched AWS instance: " + id + ", Status: " + vm.getStatus());
    }
}
