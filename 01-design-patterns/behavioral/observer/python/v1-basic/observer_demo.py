"""
Observer Pattern - V1 Basic: Weather Station
"""
from abc import ABC, abstractmethod
from typing import List

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')



# Observer Interface
class Observer(ABC):
    @abstractmethod
    def update(self, temperature: float, humidity: float, pressure: float) -> None:
        pass


# Subject Interface
class Subject(ABC):
    @abstractmethod
    def attach(self, observer: Observer) -> None:
        pass
    
    @abstractmethod
    def detach(self, observer: Observer) -> None:
        pass
    
    @abstractmethod
    def notify_observers(self) -> None:
        pass


# Concrete Subject
class WeatherStation(Subject):
    def __init__(self):
        self._observers: List[Observer] = []
        self._temperature = 0.0
        self._humidity = 0.0
        self._pressure = 0.0
    
    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)
        print(f"Observer attached. Total: {len(self._observers)}")
    
    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)
        print(f"Observer detached. Total: {len(self._observers)}")
    
    def notify_observers(self) -> None:
        for observer in self._observers:
            observer.update(self._temperature, self._humidity, self._pressure)
    
    def set_measurements(self, temperature: float, humidity: float, pressure: float) -> None:
        print("\n--- Weather Update ---")
        self._temperature = temperature
        self._humidity = humidity
        self._pressure = pressure
        self.notify_observers()


# Concrete Observers
class CurrentConditionsDisplay(Observer):
    def __init__(self, name: str):
        self.name = name
    
    def update(self, temperature: float, humidity: float, pressure: float) -> None:
        print(f"[{self.name}] Current: {temperature:.1f}F, {humidity:.1f}% humidity")


class StatisticsDisplay(Observer):
    def __init__(self):
        self._temp_sum = 0.0
        self._num_readings = 0
    
    def update(self, temperature: float, humidity: float, pressure: float) -> None:
        self._temp_sum += temperature
        self._num_readings += 1
        avg = self._temp_sum / self._num_readings
        print(f"[Statistics] Avg Temp: {avg:.1f}F ({self._num_readings} readings)")


class ForecastDisplay(Observer):
    def __init__(self):
        self._last_pressure = 0.0
    
    def update(self, temperature: float, humidity: float, pressure: float) -> None:
        if pressure > self._last_pressure:
            forecast = "Improving weather on the way!"
        elif pressure < self._last_pressure:
            forecast = "Watch out for cooler, rainy weather"
        else:
            forecast = "More of the same"
        self._last_pressure = pressure
        print(f"[Forecast] {forecast}")


class AlertDisplay(Observer):
    def __init__(self, threshold: float):
        self._threshold = threshold
    
    def update(self, temperature: float, humidity: float, pressure: float) -> None:
        if temperature > self._threshold:
            print(f"[ALERT] High temperature: {temperature:.1f}F "
                  f"(threshold: {self._threshold:.1f}F)")


if __name__ == "__main__":
    # Create subject
    weather_station = WeatherStation()
    
    # Create and register observers
    phone_display = CurrentConditionsDisplay("Phone")
    web_display = CurrentConditionsDisplay("Web")
    stats = StatisticsDisplay()
    forecast = ForecastDisplay()
    alert = AlertDisplay(90)
    
    weather_station.attach(phone_display)
    weather_station.attach(web_display)
    weather_station.attach(stats)
    weather_station.attach(forecast)
    weather_station.attach(alert)
    
    # Simulate weather changes
    weather_station.set_measurements(80, 65, 30.4)
    weather_station.set_measurements(82, 70, 29.2)
    weather_station.set_measurements(95, 90, 29.0)  # Triggers alert
    
    # Remove an observer
    print("\n--- Removing Phone Display ---")
    weather_station.detach(phone_display)
    weather_station.set_measurements(78, 60, 30.1)
