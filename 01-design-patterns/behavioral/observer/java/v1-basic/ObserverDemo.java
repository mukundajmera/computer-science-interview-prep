/**
 * Observer Pattern - V1 Basic: Weather Station
 */

import java.util.*;

// Observer Interface
interface Observer {
    void update(float temperature, float humidity, float pressure);
}

// Subject Interface
interface Subject {
    void attach(Observer observer);
    void detach(Observer observer);
    void notifyObservers();
}

// Concrete Subject
class WeatherStation implements Subject {
    private List<Observer> observers = new ArrayList<>();
    private float temperature;
    private float humidity;
    private float pressure;
    
    @Override
    public void attach(Observer observer) {
        observers.add(observer);
        System.out.println("Observer attached. Total: " + observers.size());
    }
    
    @Override
    public void detach(Observer observer) {
        observers.remove(observer);
        System.out.println("Observer detached. Total: " + observers.size());
    }
    
    @Override
    public void notifyObservers() {
        for (Observer observer : observers) {
            observer.update(temperature, humidity, pressure);
        }
    }
    
    public void setMeasurements(float temperature, float humidity, float pressure) {
        System.out.println("\n--- Weather Update ---");
        this.temperature = temperature;
        this.humidity = humidity;
        this.pressure = pressure;
        notifyObservers();
    }
}

// Concrete Observers
class CurrentConditionsDisplay implements Observer {
    private String name;
    
    public CurrentConditionsDisplay(String name) {
        this.name = name;
    }
    
    @Override
    public void update(float temperature, float humidity, float pressure) {
        System.out.printf("[%s] Current: %.1fF, %.1f%% humidity%n", 
            name, temperature, humidity);
    }
}

class StatisticsDisplay implements Observer {
    private float tempSum = 0;
    private int numReadings = 0;
    
    @Override
    public void update(float temperature, float humidity, float pressure) {
        tempSum += temperature;
        numReadings++;
        float avgTemp = tempSum / numReadings;
        System.out.printf("[Statistics] Avg Temp: %.1fF (%d readings)%n", 
            avgTemp, numReadings);
    }
}

class ForecastDisplay implements Observer {
    private float lastPressure = 0;
    
    @Override
    public void update(float temperature, float humidity, float pressure) {
        String forecast;
        if (pressure > lastPressure) {
            forecast = "Improving weather on the way!";
        } else if (pressure < lastPressure) {
            forecast = "Watch out for cooler, rainy weather";
        } else {
            forecast = "More of the same";
        }
        lastPressure = pressure;
        System.out.println("[Forecast] " + forecast);
    }
}

class AlertDisplay implements Observer {
    private float alertThreshold;
    
    public AlertDisplay(float threshold) {
        this.alertThreshold = threshold;
    }
    
    @Override
    public void update(float temperature, float humidity, float pressure) {
        if (temperature > alertThreshold) {
            System.out.printf("[ALERT] High temperature: %.1fF (threshold: %.1fF)%n",
                temperature, alertThreshold);
        }
    }
}

public class ObserverDemo {
    public static void main(String[] args) {
        // Create subject
        WeatherStation weatherStation = new WeatherStation();
        
        // Create and register observers
        CurrentConditionsDisplay phoneDisplay = new CurrentConditionsDisplay("Phone");
        CurrentConditionsDisplay webDisplay = new CurrentConditionsDisplay("Web");
        StatisticsDisplay stats = new StatisticsDisplay();
        ForecastDisplay forecast = new ForecastDisplay();
        AlertDisplay alert = new AlertDisplay(90);
        
        weatherStation.attach(phoneDisplay);
        weatherStation.attach(webDisplay);
        weatherStation.attach(stats);
        weatherStation.attach(forecast);
        weatherStation.attach(alert);
        
        // Simulate weather changes
        weatherStation.setMeasurements(80, 65, 30.4f);
        weatherStation.setMeasurements(82, 70, 29.2f);
        weatherStation.setMeasurements(95, 90, 29.0f);  // Triggers alert
        
        // Remove an observer
        System.out.println("\n--- Removing Phone Display ---");
        weatherStation.detach(phoneDisplay);
        weatherStation.setMeasurements(78, 60, 30.1f);
    }
}
