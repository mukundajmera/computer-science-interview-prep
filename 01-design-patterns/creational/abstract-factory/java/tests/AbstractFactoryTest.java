import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

import abstractfactory.v2.DatabaseFactoryDemo.*;
import abstractfactory.v3.CloudResourceFactoryDemo.*;

public class AbstractFactoryTest {

    @Test
    @DisplayName("WindowsFactory creates Windows components with expected behaviors")
    void testWindowsFactoryCreatesWindowsComponents() {
        GUIFactory factory = new WindowsFactory();
        Button button = factory.createButton();
        Checkbox checkbox = factory.createCheckbox();
        TextField textField = factory.createTextField();

        assertNotNull(button);
        assertNotNull(checkbox);
        assertNotNull(textField);

        assertDoesNotThrow(() -> button.render());
        assertDoesNotThrow(() -> button.onClick());

        assertFalse(checkbox.isChecked());
        checkbox.toggle();
        assertTrue(checkbox.isChecked());

        textField.setValue("test-value");
        assertEquals("test-value", textField.getValue());
    }

    @Test
    @DisplayName("MacFactory creates Mac components with expected behaviors")
    void testMacFactoryCreatesMacComponents() {
        GUIFactory factory = new MacFactory();
        Button button = factory.createButton();
        Checkbox checkbox = factory.createCheckbox();
        TextField textField = factory.createTextField();

        assertNotNull(button);
        assertNotNull(checkbox);
        assertNotNull(textField);

        assertDoesNotThrow(() -> button.render());
        assertDoesNotThrow(() -> button.onClick());

        assertFalse(checkbox.isChecked());
        checkbox.toggle();
        assertTrue(checkbox.isChecked());

        textField.setValue("mac-value");
        assertEquals("mac-value", textField.getValue());
    }

    @Test
    @DisplayName("GUIFactoryProvider correctly resolves OS factories and rejects invalid OS")
    void testGUIFactoryProviderResolvesOS() {
        GUIFactory winFactory = GUIFactoryProvider.getFactory("windows");
        assertTrue(winFactory instanceof WindowsFactory);

        GUIFactory macFactory = GUIFactoryProvider.getFactory("mac");
        assertTrue(macFactory instanceof MacFactory);

        assertThrows(IllegalArgumentException.class, () -> GUIFactoryProvider.getFactory("unsupported_os"));
    }

    @Test
    @DisplayName("v2 DatabaseFactory produces dialect-coherent components")
    void testDatabaseFactoryComponents() {
        DatabaseFactory pgFactory = new PostgresFactory();
        DbConnection pgConn = pgFactory.createConnection();
        assertEquals("POSTGRESQL", pgConn.getDialect());
        assertFalse(pgConn.isOpen());
        pgConn.open();
        assertTrue(pgConn.isOpen());

        DbCommand pgCmd = pgFactory.createCommand();
        assertTrue(pgCmd.execute("SELECT 1").contains("PostgreSQL"));

        DbTransaction pgTx = pgFactory.createTransaction();
        assertFalse(pgTx.isActive());
        pgTx.begin();
        assertTrue(pgTx.isActive());
        pgTx.commit();
        assertFalse(pgTx.isActive());

        DatabaseFactory mysqlFactory = new MySqlFactory();
        DbConnection mysqlConn = mysqlFactory.createConnection();
        assertEquals("MYSQL", mysqlConn.getDialect());
    }

    @Test
    @DisplayName("v3 CloudResourceFactoryRegistry provisions resources safely")
    void testCloudResourceFactory() {
        CloudFactory aws = CloudProviderRegistry.getFactory("aws");
        assertEquals("AWS", aws.getCloudProvider());

        ComputeInstance vm = aws.createCompute();
        assertEquals("STOPPED", vm.getStatus());
        String launch = vm.launch("c5.xlarge");
        assertTrue(launch.contains("aws-ec2-c5.xlarge"));
        assertEquals("RUNNING", vm.getStatus());

        ObjectStorage storage = aws.createStorage();
        byte[] payload = "test-bytes".getBytes();
        storage.putObject("test-bucket", "obj1", payload);
        assertArrayEquals(payload, storage.getObject("test-bucket", "obj1"));

        KeyVault vault = aws.createKeyVault();
        vault.setSecret("api_key", "sec-123");
        assertEquals("sec-123", vault.getSecret("api_key"));

        assertThrows(IllegalArgumentException.class, () -> CloudProviderRegistry.getFactory("unknown_cloud"));
    }
}
