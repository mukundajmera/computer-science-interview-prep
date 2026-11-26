/**
 * Observer Pattern - V2 Variant: Stock Market Ticker
 */

import java.util.*;

final class StockQuote {
    private final String symbol;
    private final double price;
    private final double previousPrice;

    StockQuote(String symbol, double price, double previousPrice) {
        this.symbol = symbol;
        this.price = price;
        this.previousPrice = previousPrice;
    }

    public String getSymbol() { return symbol; }
    public double getPrice() { return price; }
    public double getPreviousPrice() { return previousPrice; }
    public double getChange() { return price - previousPrice; }
}

interface StockObserver {
    void update(StockQuote quote);
}

class StockTicker {
    private final List<StockObserver> observers = new ArrayList<>();
    private final Map<String, Double> prices = new HashMap<>();

    public void attach(StockObserver observer) {
        if (!observers.contains(observer)) {
            observers.add(observer);
        }
    }

    public void detach(StockObserver observer) {
        observers.remove(observer);
    }

    public StockQuote updatePrice(String symbol, double price) {
        double previous = prices.getOrDefault(symbol, price);
        prices.put(symbol, price);
        StockQuote quote = new StockQuote(symbol, price, previous);
        notifyObservers(quote);
        return quote;
    }

    private void notifyObservers(StockQuote quote) {
        for (StockObserver observer : new ArrayList<>(observers)) {
            observer.update(quote);
        }
    }
}

class PortfolioDisplay implements StockObserver {
    private final Map<String, Integer> shares;
    private final Map<String, Double> lastPrices = new HashMap<>();

    PortfolioDisplay(Map<String, Integer> shares) {
        this.shares = new HashMap<>(shares);
    }

    public Map<String, Double> getLastPrices() {
        return Collections.unmodifiableMap(lastPrices);
    }

    public double getTotalValue() {
        double total = 0.0;
        for (Map.Entry<String, Integer> entry : shares.entrySet()) {
            total += entry.getValue() * lastPrices.getOrDefault(entry.getKey(), 0.0);
        }
        return total;
    }

    @Override
    public void update(StockQuote quote) {
        if (shares.containsKey(quote.getSymbol())) {
            lastPrices.put(quote.getSymbol(), quote.getPrice());
        }
    }
}

class PriceAlert implements StockObserver {
    private final String symbol;
    private final double threshold;
    private final List<String> messages = new ArrayList<>();

    PriceAlert(String symbol, double threshold) {
        this.symbol = symbol;
        this.threshold = threshold;
    }

    public List<String> getMessages() {
        return Collections.unmodifiableList(messages);
    }

    @Override
    public void update(StockQuote quote) {
        if (symbol.equals(quote.getSymbol()) && quote.getPrice() >= threshold) {
            messages.add(String.format(
                "%s crossed %.2f at %.2f",
                quote.getSymbol(),
                threshold,
                quote.getPrice()
            ));
        }
    }
}

class MovingAverageDisplay implements StockObserver {
    private final int windowSize;
    private final Map<String, Deque<Double>> pricesBySymbol = new HashMap<>();

    MovingAverageDisplay(int windowSize) {
        if (windowSize <= 0) {
            throw new IllegalArgumentException("windowSize must be positive");
        }
        this.windowSize = windowSize;
    }

    @Override
    public void update(StockQuote quote) {
        Deque<Double> prices = pricesBySymbol.computeIfAbsent(quote.getSymbol(), key -> new ArrayDeque<>());
        prices.addLast(quote.getPrice());
        while (prices.size() > windowSize) {
            prices.removeFirst();
        }
    }

    public double averageFor(String symbol) {
        Deque<Double> prices = pricesBySymbol.get(symbol);
        if (prices == null || prices.isEmpty()) {
            return 0.0;
        }
        double total = 0.0;
        for (double price : prices) {
            total += price;
        }
        return total / prices.size();
    }
}

public class StockTickerDemo {
    public static void main(String[] args) {
        StockTicker ticker = new StockTicker();
        PortfolioDisplay portfolio = new PortfolioDisplay(Map.of("ORCL", 4, "MSFT", 2));
        PriceAlert alert = new PriceAlert("ORCL", 120.0);
        MovingAverageDisplay movingAverage = new MovingAverageDisplay(3);

        ticker.attach(portfolio);
        ticker.attach(alert);
        ticker.attach(movingAverage);

        for (StockQuote quote : Arrays.asList(
                ticker.updatePrice("ORCL", 118.0),
                ticker.updatePrice("MSFT", 410.0),
                ticker.updatePrice("ORCL", 125.5))) {
            System.out.printf("%s: %.2f (%+.2f)%n", quote.getSymbol(), quote.getPrice(), quote.getChange());
        }

        System.out.printf("Portfolio value: %.2f%n", portfolio.getTotalValue());
        System.out.printf("ORCL moving average: %.2f%n", movingAverage.averageFor("ORCL"));
        System.out.println("Alerts: " + alert.getMessages());
    }
}
