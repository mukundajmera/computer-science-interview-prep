
import java.util.ArrayList;
import java.util.List;

public class Cart {
    private List<MenuItem> items;

    public Cart() {
        this.items = new ArrayList<>();
    }

    public void addItem(MenuItem item) {
        items.add(item);
    }

    public List<MenuItem> getItems() {
        return items;
    }

    public double getTotal() {
        return items.stream().mapToDouble(MenuItem::getPrice).sum();
    }
    
    public void clear() {
        items.clear();
    }
}
