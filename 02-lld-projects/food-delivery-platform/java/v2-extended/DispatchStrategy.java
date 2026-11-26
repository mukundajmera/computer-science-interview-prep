
import java.util.List;

public interface DispatchStrategy {
    Driver dispatch(Restaurant restaurant, List<Driver> drivers);
}
