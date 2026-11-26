public class Demo {
    public static void main(String[] args) {
        StoreSelector selector = new StoreSelector();
        StoreSelector.Workload payments = new StoreSelector.Workload(true, false, true, false);
        StoreSelector.Workload feed = new StoreSelector.Workload(false, true, false, true);
        System.out.println(selector.chooseStore(payments));
        System.out.println(selector.chooseStore(feed));
    }
}
