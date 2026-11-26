from logger_factory import LoggerFactory
from log_level import LogLevel

def main():
    factory = LoggerFactory.get_instance()
    
    root = factory.get_logger("root")
    root.set_level(LogLevel.INFO)
    
    app_logger = factory.get_logger("com.app")
    app_logger.set_level(LogLevel.DEBUG)
    
    service_logger = factory.get_logger("com.app.service")
    
    print(f"Root effective level: {root.get_effective_level().name}")
    print(f"com.app effective level: {app_logger.get_effective_level().name}")
    print(f"com.app.service effective level: {service_logger.get_effective_level().name}") # Should inherit DEBUG
    
    root.info("This is an info message from root")
    app_logger.debug("This is a debug message from app")
    service_logger.trace("This trace should not be printed")
    service_logger.debug("This debug from service should be printed")
    
    factory.shutdown()

if __name__ == "__main__":
    main()
