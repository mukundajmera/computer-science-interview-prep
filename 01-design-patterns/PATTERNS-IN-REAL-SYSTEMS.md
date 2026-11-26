# Patterns in Real Systems

This document maps the 23 Gang of Four (GoF) design patterns to concrete examples in real-world libraries, frameworks, and large-scale infrastructure.

## Creational Patterns

### Singleton
**Description:** Ensure a class only has one instance, and provide a global point of access to it.

**Real-World API Examples:**
- JDK: `java.lang.Runtime#getRuntime()`
- Spring: Default Bean Scope (Singleton Beans)
- Python stdlib: `logging.getLogger()`
- Django: `django.conf.settings`

### Factory Method
**Description:** Define an interface for creating an object, but let subclasses decide which class to instantiate.

**Real-World API Examples:**
- JDK: `java.util.Calendar#getInstance()`
- Spring: `FactoryBean#getObject()`
- Python stdlib: `xml.etree.ElementTree.Element`
- Django: `django.core.files.storage.get_storage_class()`

### Abstract Factory
**Description:** Provide an interface for creating families of related or dependent objects without specifying their concrete classes.

**Real-World API Examples:**
- JDK: `javax.xml.parsers.DocumentBuilderFactory#newInstance()`
- Spring: `BeanFactory` / `ApplicationContext`
- Python stdlib: `abc.ABCMeta` (for defining abstract factories)
- Django: `django.forms.formsets.formset_factory()`

### Builder
**Description:** Separate the construction of a complex object from its representation so that the same construction process can create different representations.

**Real-World API Examples:**
- JDK: `java.lang.StringBuilder#append()`
- Spring: `org.springframework.web.reactive.function.client.WebClient.Builder`
- Python stdlib: `urllib.request.Request` (simulates builder pattern by setting attributes)
- Django: `django.db.models.query.QuerySet` (chaining methods like `filter()`, `exclude()`)

### Prototype
**Description:** Specify the kinds of objects to create using a prototypical instance, and create new objects by copying this prototype.

**Real-World API Examples:**
- JDK: `java.lang.Object#clone()`
- Spring: `prototype` Bean Scope
- Python stdlib: `copy.deepcopy()`
- Django: `django.db.models.Model._meta` (cloning metadata)

## Structural Patterns

### Adapter
**Description:** Convert the interface of a class into another interface clients expect.

**Real-World API Examples:**
- JDK: `java.util.Arrays#asList()`
- Spring: `HandlerInterceptorAdapter` (deprecated) or `WebMvcConfigurerAdapter`
- Python stdlib: `logging.config.dictConfig` (adapts dict to logging config)
- Django: `django.contrib.auth.middleware.AuthenticationMiddleware`

### Bridge
**Description:** Decouple an abstraction from its implementation so that the two can vary independently.

**Real-World API Examples:**
- JDK: JDBC API (`java.sql.Driver` vs `java.sql.Connection`)
- Spring: `ViewResolver` and `View`
- Python stdlib: `os` module (bridges Python logic with OS-specific implementations)
- Django: Database Backends (`django.db.backends`)

### Composite
**Description:** Compose objects into tree structures to represent part-whole hierarchies.

**Real-World API Examples:**
- JDK: `java.awt.Container#add(Component)`
- Spring: `CompositeCacheManager`
- Python stdlib: `xml.etree.ElementTree.Element`
- Django: `django.template.NodeList`

### Decorator
**Description:** Attach additional responsibilities to an object dynamically.

**Real-World API Examples:**
- JDK: `java.io.BufferedInputStream(InputStream)`
- Spring: `TransactionAwareCacheDecorator`
- Python stdlib: `@property`, `@staticmethod`, `@classmethod`
- Django: `@login_required`, `@require_http_methods`

### Facade
**Description:** Provide a unified interface to a set of interfaces in a subsystem.

**Real-World API Examples:**
- JDK: `javax.faces.context.FacesContext`
- Spring: `JdbcTemplate`
- Python stdlib: `os` module (facade over posix/nt)
- Django: `django.shortcuts.render()`

### Flyweight
**Description:** Use sharing to support large numbers of fine-grained objects efficiently.

**Real-World API Examples:**
- JDK: `java.lang.Integer#valueOf(int)`
- Spring: `PropertySourcesPlaceholderConfigurer` (string interning)
- Python stdlib: String interning (`sys.intern`)
- Django: `django.db.models.fields.Field` instances shared across model instances

### Proxy
**Description:** Provide a surrogate or placeholder for another object to control access to it.

**Real-World API Examples:**
- JDK: `java.lang.reflect.Proxy`
- Spring: AOP Proxies (CGLIB, JDK Dynamic Proxies)
- Python stdlib: `weakref.proxy`
- Django: `django.utils.functional.SimpleLazyObject`

## Behavioral Patterns

### Chain of Responsibility
**Description:** Avoid coupling the sender of a request to its receiver by giving more than one object a chance to handle the request.

**Real-World API Examples:**
- JDK: `java.util.logging.Logger#log()`
- Spring: `HandlerInterceptor`, `SecurityFilterChain`
- Python stdlib: `logging.Handler` hierarchy
- Django: Middleware framework (`django.utils.deprecation.MiddlewareMixin`)

### Command
**Description:** Encapsulate a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations.

**Real-World API Examples:**
- JDK: `java.lang.Runnable`
- Spring: `org.springframework.jdbc.core.PreparedStatementCreator`
- Python stdlib: `sqlite3.Cursor.execute()` (stores query to execute)
- Django: `django.core.management.BaseCommand` (management commands)

### Interpreter
**Description:** Given a language, define a representation for its grammar along with an interpreter that uses the representation to interpret sentences in the language.

**Real-World API Examples:**
- JDK: `java.util.regex.Pattern`
- Spring: SpEL (`ExpressionParser`)
- Python stdlib: `re` module (regex parsing)
- Django: Template rendering engine (`django.template.Engine`)

### Iterator
**Description:** Provide a way to access the elements of an aggregate object sequentially without exposing its underlying representation.

**Real-World API Examples:**
- JDK: `java.util.Iterator`
- Spring: `CompositeIterator`
- Python stdlib: `iter()`, `next()` functions
- Django: QuerySet iteration (`QuerySet.__iter__()`)

### Mediator
**Description:** Define an object that encapsulates how a set of objects interact. Mediator promotes loose coupling by keeping objects from referring to each other explicitly.

**Real-World API Examples:**
- JDK: `java.util.Timer`
- Spring: `ApplicationEventPublisher`
- Python stdlib: `threading.Condition`
- Django: Signal dispatcher (`django.dispatch.Signal`)

### Memento
**Description:** Without violating encapsulation, capture and externalize an object's internal state so that the object can be restored to this state later.

**Real-World API Examples:**
- JDK: `java.util.Date` (state can be restored via `setTime`)
- Spring: `StateManageableMessageContext`
- Python stdlib: `pickle` module (serializing and restoring state)
- Django: `django.db.models.Model.save()` (using `update_fields` to restore state partially)

### Observer
**Description:** Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically.

**Real-World API Examples:**
- JDK: `java.util.Observer` / `java.util.Observable` (deprecated in Java 9+)
- Spring: `ApplicationListener`
- Python stdlib: `asyncio.Event`
- Django: Signals (`django.db.models.signals.post_save`)

### State
**Description:** Allow an object to alter its behavior when its internal state changes. The object will appear to change its class.

**Real-World API Examples:**
- JDK: `java.util.concurrent.ThreadPoolExecutor` (running, shutdown, terminated)
- Spring: Spring Statemachine framework
- Python stdlib: `asyncio.Future` (pending, cancelled, finished)
- Django: Form validation states (`is_bound`, `is_valid()`)

### Strategy
**Description:** Define a family of algorithms, encapsulate each one, and make them interchangeable. Strategy lets the algorithm vary independently from clients that use it.

**Real-World API Examples:**
- JDK: `java.util.Comparator#compare()`
- Spring: `ResourceLoader` / `PlatformTransactionManager`
- Python stdlib: `sorted()` (key argument)
- Django: Authentication backends (`AUTHENTICATION_BACKENDS`)

### Template Method
**Description:** Define the skeleton of an algorithm in an operation, deferring some steps to subclasses.

**Real-World API Examples:**
- JDK: `java.util.AbstractList#get()`
- Spring: `JdbcTemplate` / `RestTemplate`
- Python stdlib: `cmd.Cmd` (provides a framework for line-oriented command interpreters)
- Django: Class-Based Views (`django.views.generic.View.dispatch()`)

### Visitor
**Description:** Represent an operation to be performed on the elements of an object structure. Visitor lets you define a new operation without changing the classes of the elements on which it operates.

**Real-World API Examples:**
- JDK: `java.nio.file.FileVisitor`
- Spring: `BeanDefinitionVisitor`
- Python stdlib: `ast.NodeVisitor`
- Django: Query compiler AST traversal (`django.db.models.sql.compiler.SQLCompiler`)

## Pattern-to-Infrastructure Mapping

How these patterns scale up to High-Level Design (HLD) concepts.

| Design Pattern | Infrastructure / HLD Concept | Link |
|---|---|---|
| Singleton | Database Connection Pooling | [Concept](../03-hld-concepts/relational-databases/) |
| Factory Method | API Gateway Routing | [Concept](../03-hld-concepts/api-gateway/) |
| Abstract Factory | Multi-Region Cloud Deployments | [Concept](../03-hld-concepts/multi-region-active-active/) |
| Builder | Elasticsearch Query DSL | [Concept](../03-hld-concepts/elasticsearch/) |
| Prototype | Container Image Cloning | [Concept](../03-hld-concepts/workflow-orchestration/) |
| Adapter | Legacy System Integration (Anti-Corruption Layer) | [Concept](../03-hld-concepts/microservices-communication/) |
| Bridge | Multi-Cloud Storage Abstraction | [Concept](../03-hld-concepts/large-blob-handling/) |
| Composite | Directory Services / LDAP | [Concept](../03-hld-concepts/microservice-security/) |
| Decorator | API Rate Limiting Middleware | [Concept](../03-hld-concepts/rate-limiting/) |
| Facade | BFF (Backend for Frontend) | [Concept](../03-hld-concepts/api-design/) |
| Flyweight | CDN Edge Caching | [Concept](../03-hld-concepts/cdn/) |
| Proxy | Reverse Proxy / Load Balancing | [Concept](../03-hld-concepts/load-balancing/) |
| Chain of Responsibility | WAF (Web Application Firewall) | [Concept](../03-hld-concepts/microservice-security/) |
| Command | Saga Pattern / Outbox Pattern | [Concept](../03-hld-concepts/distributed-transactions-saga-outbox/) |
| Interpreter | Log Query Parsing (e.g., Splunk/ELK) | [Concept](../03-hld-concepts/observability/) |
| Iterator | Database Cursor Pagination | [Concept](../03-hld-concepts/api-design/) |
| Mediator | Kafka as Event Bus | [Concept](../03-hld-concepts/kafka/) |
| Memento | Database Snapshots / Backup | [Concept](../03-hld-concepts/database-replication/) |
| Observer | Pub/Sub Messaging | [Concept](../03-hld-concepts/message-queues/) |
| State | Circuit Breaker | [Concept](../03-hld-concepts/resilience-patterns/) |
| Strategy | Load Balancing Algorithms (Round Robin vs. Least Connections) | [Concept](../03-hld-concepts/load-balancing/) |
| Template Method | CI/CD Pipeline Stages | [Concept](../03-hld-concepts/workflow-orchestration/) |
| Visitor | Distributed Tracing (e.g., Jaeger/Zipkin traversing trace trees) | [Concept](../03-hld-concepts/monitoring-observability/) |
