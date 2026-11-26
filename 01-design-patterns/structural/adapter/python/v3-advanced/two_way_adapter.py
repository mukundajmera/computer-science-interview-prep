"""
Adapter Pattern - V3 Advanced: Two-Way Adapter with Context Manager

Scenario: Legacy XML-based system needs to work with new JSON-based system.
Uses Python features: context managers, properties, type hints.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import re


# Legacy System - Uses XML format
class XMLDataSource(ABC):
    @abstractmethod
    def fetch_as_xml(self, query: str) -> str:
        pass
    
    @abstractmethod
    def save_from_xml(self, xml: str) -> None:
        pass


# New System - Uses JSON format
class JSONDataSource(ABC):
    @abstractmethod
    def fetch_as_json(self, query: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def save_from_json(self, data: Dict[str, Any]) -> None:
        pass


# Concrete Legacy System
class LegacyXMLDatabase(XMLDataSource):
    def __init__(self):
        self._storage: Dict[str, str] = {
            "user_1": "<user><id>1</id><name>Alice</name><email>alice@test.com</email></user>",
            "user_2": "<user><id>2</id><name>Bob</name><email>bob@test.com</email></user>",
        }
    
    def fetch_as_xml(self, query: str) -> str:
        print(f"Legacy XML DB: Fetching {query}")
        return self._storage.get(query, "<empty/>")
    
    def save_from_xml(self, xml: str) -> None:
        print("Legacy XML DB: Saving XML data")
        id_match = re.search(r"<id>(\d+)</id>", xml)
        if id_match:
            self._storage[f"user_{id_match.group(1)}"] = xml
    
    def _extract_value(self, xml: str, tag: str) -> Optional[str]:
        match = re.search(f"<{tag}>(.*?)</{tag}>", xml)
        return match.group(1) if match else None


# Concrete New System
class ModernJSONAPI(JSONDataSource):
    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {
            "product_1": {"id": 1, "name": "Laptop", "price": 999.99},
            "product_2": {"id": 2, "name": "Mouse", "price": 29.99},
        }
    
    def fetch_as_json(self, query: str) -> Dict[str, Any]:
        print(f"Modern JSON API: Fetching {query}")
        return self._storage.get(query, {})
    
    def save_from_json(self, data: Dict[str, Any]) -> None:
        print("Modern JSON API: Saving JSON data")
        item_id = f"item_{data.get('id', 'unknown')}"
        self._storage[item_id] = data


# Two-Way Adapter with Context Manager support
class TwoWayDataAdapter(XMLDataSource, JSONDataSource):
    """
    Two-way adapter that can convert between XML and JSON formats.
    Supports Python context manager for resource management.
    """
    
    def __init__(self, xml_source: XMLDataSource = None, 
                 json_source: JSONDataSource = None):
        self._xml_source = xml_source
        self._json_source = json_source
        self._transaction_log: list = []
    
    def __enter__(self):
        """Context manager entry"""
        self._transaction_log = []
        print("Adapter: Starting transaction")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type is None:
            print(f"Adapter: Transaction completed. {len(self._transaction_log)} operations.")
        else:
            print(f"Adapter: Transaction failed. Rolling back.")
        return False
    
    # XMLDataSource implementation
    def fetch_as_xml(self, query: str) -> str:
        self._transaction_log.append(f"fetch_xml:{query}")
        
        if self._xml_source:
            return self._xml_source.fetch_as_xml(query)
        
        # Convert JSON to XML
        json_data = self._json_source.fetch_as_json(query)
        return self._json_to_xml(json_data)
    
    def save_from_xml(self, xml: str) -> None:
        self._transaction_log.append("save_xml")
        
        if self._xml_source:
            self._xml_source.save_from_xml(xml)
            return
        
        # Convert XML to JSON and save
        json_data = self._xml_to_json(xml)
        self._json_source.save_from_json(json_data)
    
    # JSONDataSource implementation
    def fetch_as_json(self, query: str) -> Dict[str, Any]:
        self._transaction_log.append(f"fetch_json:{query}")
        
        if self._json_source:
            return self._json_source.fetch_as_json(query)
        
        # Convert XML to JSON
        xml_data = self._xml_source.fetch_as_xml(query)
        return self._xml_to_json(xml_data)
    
    def save_from_json(self, data: Dict[str, Any]) -> None:
        self._transaction_log.append("save_json")
        
        if self._json_source:
            self._json_source.save_from_json(data)
            return
        
        # Convert JSON to XML and save
        xml_data = self._json_to_xml(data)
        self._xml_source.save_from_xml(xml_data)
    
    # Conversion utilities
    def _json_to_xml(self, data: Dict[str, Any]) -> str:
        if not data:
            return "<empty/>"
        
        parts = ["<item>"]
        for key, value in data.items():
            parts.append(f"<{key}>{value}</{key}>")
        parts.append("</item>")
        return "".join(parts)
    
    def _xml_to_json(self, xml: str) -> Dict[str, Any]:
        if xml == "<empty/>":
            return {}
        
        result = {}
        for tag in ["id", "name", "email", "price"]:
            match = re.search(f"<{tag}>(.*?)</{tag}>", xml)
            if match:
                value = match.group(1)
                # Try to convert to appropriate type
                try:
                    if "." in value:
                        result[tag] = float(value)
                    else:
                        result[tag] = int(value)
                except ValueError:
                    result[tag] = value
        return result
    
    @property
    def transaction_count(self) -> int:
        return len(self._transaction_log)


# Demo
if __name__ == "__main__":
    # Legacy XML system
    legacy_db = LegacyXMLDatabase()
    
    # Modern JSON system
    modern_api = ModernJSONAPI()
    
    # Two-way adapter with context manager
    print("=== Using context manager for transaction safety ===")
    with TwoWayDataAdapter(legacy_db, modern_api) as adapter:
        # JSON client reading from Legacy XML system
        print("\n--- JSON client reading from XML system ---")
        user_json = adapter.fetch_as_json("user_1")
        print(f"Got JSON: {user_json}")
        
        # XML client reading from Modern JSON system
        print("\n--- XML client reading from JSON system ---")
        product_xml = adapter.fetch_as_xml("product_1")
        print(f"Got XML: {product_xml}")
        
        print(f"\nTotal operations: {adapter.transaction_count}")
    
    # Adapter for single source
    print("\n=== Single-source adapter ===")
    xml_only = TwoWayDataAdapter(xml_source=legacy_db)
    xml_only.save_from_json({"id": 3, "name": "Charlie", "email": "charlie@test.com"})
    
    # Verify
    saved = legacy_db.fetch_as_xml("user_3")
    print(f"Saved as XML: {saved}")
