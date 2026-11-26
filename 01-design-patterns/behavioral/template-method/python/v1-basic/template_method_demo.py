"""
Template Method Pattern - Data Processing
"""
from abc import ABC, abstractmethod


# Abstract Class with Template Method
class DataProcessor(ABC):
    def process_data(self) -> None:
        """Template method - defines algorithm skeleton"""
        self.read_data()
        self.parse_data()
        self.analyze_data()
        self.generate_report()
    
    def read_data(self) -> None:
        print("Reading data from source...")
    
    def generate_report(self) -> None:
        print("Generating final report")
    
    @abstractmethod
    def parse_data(self) -> None:
        pass
    
    @abstractmethod
    def analyze_data(self) -> None:
        pass


# Concrete Implementations
class CSVProcessor(DataProcessor):
    def parse_data(self) -> None:
        print("Parsing CSV: splitting by commas")
    
    def analyze_data(self) -> None:
        print("Analyzing CSV: calculating statistics")


class JSONProcessor(DataProcessor):
    def parse_data(self) -> None:
        print("Parsing JSON: building object tree")
    
    def analyze_data(self) -> None:
        print("Analyzing JSON: traversing nodes")


class XMLProcessor(DataProcessor):
    def parse_data(self) -> None:
        print("Parsing XML: building DOM tree")
    
    def analyze_data(self) -> None:
        print("Analyzing XML: XPath queries")
    
    def generate_report(self) -> None:
        print("Generating XML report with XSLT")


if __name__ == "__main__":
    print("=== CSV Processing ===")
    csv = CSVProcessor()
    csv.process_data()
    
    print("\n=== JSON Processing ===")
    json_proc = JSONProcessor()
    json_proc.process_data()
    
    print("\n=== XML Processing ===")
    xml = XMLProcessor()
    xml.process_data()
