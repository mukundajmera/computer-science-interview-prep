public class Demo {
    public static void main(String[] args) {
        System.out.println(new CapSystem(CapSystem.Mode.CP).readDuringPartition());
        System.out.println(new CapSystem(CapSystem.Mode.AP).readDuringPartition());
    }
}
