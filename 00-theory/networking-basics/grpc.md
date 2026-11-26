# gRPC

A high-performance RPC framework. Understanding gRPC helps in designing efficient microservices communication.

---

## 📖 What is gRPC?

> **gRPC Remote Procedure Call - a high-performance, open-source RPC framework using Protocol Buffers and HTTP/2.**

### REST vs gRPC

```
REST:                              gRPC:
┌────────────────────────┐        ┌────────────────────────┐
│ JSON over HTTP/1.1     │        │ Protobuf over HTTP/2   │
│ Human-readable         │        │ Binary format          │
│ Larger payloads        │        │ Smaller payloads       │
│ Simple                 │        │ More efficient         │
└────────────────────────┘        └────────────────────────┘
```

---

## 🔧 How gRPC Works

### Protocol Buffers (Protobuf)

```protobuf
// user.proto - Define the service and messages
syntax = "proto3";

package user;

// Service definition
service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc CreateUser(CreateUserRequest) returns (User);
  rpc ListUsers(ListUsersRequest) returns (stream User);
}

// Message definitions
message User {
  int32 id = 1;
  string name = 2;
  string email = 3;
}

message GetUserRequest {
  int32 id = 1;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}
```

### Generated Code

```java
// Auto-generated client stub
UserServiceGrpc.UserServiceBlockingStub stub = 
    UserServiceGrpc.newBlockingStub(channel);

GetUserRequest request = GetUserRequest.newBuilder()
    .setId(123)
    .build();

User user = stub.getUser(request);
System.out.println(user.getName());
```

---

## 🔄 Communication Patterns

### 1. Unary RPC (Request-Response)

```
Client ──Request──▶ Server
Client ◀─Response── Server
```

```protobuf
rpc GetUser(GetUserRequest) returns (User);
```

### 2. Server Streaming

```
Client ──Request──▶ Server
Client ◀─Response1─ Server
Client ◀─Response2─ Server
Client ◀─Response3─ Server
```

```protobuf
rpc ListUsers(ListRequest) returns (stream User);
```

### 3. Client Streaming

```
Client ──Request1──▶ Server
Client ──Request2──▶ Server
Client ──Request3──▶ Server
Client ◀──Response── Server
```

```protobuf
rpc UploadLogs(stream LogEntry) returns (UploadResult);
```

### 4. Bidirectional Streaming

```
Client ◀───────────────────▶ Server
       (Both send streams)
```

```protobuf
rpc Chat(stream Message) returns (stream Message);
```

---

## ⚖️ gRPC vs REST

| Aspect | gRPC | REST |
|--------|------|------|
| **Protocol** | HTTP/2 | HTTP/1.1 (usually) |
| **Format** | Protocol Buffers (binary) | JSON (text) |
| **Performance** | ~10x faster | Slower |
| **Browser Support** | Limited (needs proxy) | Full |
| **Streaming** | Built-in (4 patterns) | Workarounds needed |
| **Contract** | Strict (proto files) | Loose (OpenAPI optional) |
| **Learning Curve** | Steeper | Easier |
| **Debugging** | Harder (binary) | Easier (human-readable) |

---

## 🎯 When to Use gRPC

### ✅ Good Fit

```
├── Microservices internal communication
├── Low-latency requirements
├── Polyglot environments (many languages)
├── Streaming data (real-time)
├── Mobile clients (bandwidth sensitive)
└── Strong typing important
```

### ❌ Not Ideal

```
├── Public APIs (browser compatibility)
├── Simple CRUD applications
├── Team new to RPC concepts
├── Need human-readable debugging
└── Extensive tooling ecosystem needed
```

---

## 🏗️ gRPC in Microservices

```
┌─────────────────────────────────────────────────────────┐
│                    API Gateway                          │
│              (REST for external clients)                │
└────────────────────────┬────────────────────────────────┘
                         │ gRPC (internal)
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │  User    │    │  Order   │    │ Payment  │
   │ Service  │◀──▶│ Service  │◀──▶│ Service  │
   └──────────┘    └──────────┘    └──────────┘
              gRPC         gRPC
```

---

## 🔧 Implementation Example

### Server (Go)

```go
type userServer struct {
    pb.UnimplementedUserServiceServer
}

func (s *userServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.User, error) {
    // Fetch user from database
    user := &pb.User{
        Id:    req.Id,
        Name:  "Alice",
        Email: "alice@example.com",
    }
    return user, nil
}

func main() {
    lis, _ := net.Listen("tcp", ":50051")
    s := grpc.NewServer()
    pb.RegisterUserServiceServer(s, &userServer{})
    s.Serve(lis)
}
```

### Client (Python)

```python
import grpc
import user_pb2
import user_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = user_pb2_grpc.UserServiceStub(channel)

request = user_pb2.GetUserRequest(id=123)
response = stub.GetUser(request)

print(f"User: {response.name}, Email: {response.email}")
```

---

## 🎯 Interview Questions

### Q1: "Why would you choose gRPC over REST for microservices?"

**Answer**:
"I'd choose gRPC for internal microservices because:
1. **Performance**: Protobuf is 3-10x faster than JSON
2. **Streaming**: Native support for real-time data
3. **Strong typing**: Proto files enforce contracts
4. **Code generation**: Stubs in any language from one proto
5. **HTTP/2**: Multiplexing, header compression

But I'd still use REST for:
- Public APIs (browser compatibility)
- Simple services (less overhead)"

### Q2: "How do you handle errors in gRPC?"

**Answer**:
```go
// Server-side
if user == nil {
    return nil, status.Errorf(codes.NotFound, "user %d not found", id)
}

// Client-side
resp, err := client.GetUser(ctx, req)
if err != nil {
    st, ok := status.FromError(err)
    if ok && st.Code() == codes.NotFound {
        // Handle not found
    }
}
```

"gRPC uses status codes similar to HTTP (OK, NotFound, InvalidArgument, etc.). Include detailed error messages for debugging."

### Q3: "How do you version gRPC APIs?"

**Answer**:
"Several strategies:
1. **Package versioning**: `package user.v1;` → `package user.v2;`
2. **Additive changes**: Add new fields (backward compatible)
3. **New services**: UserServiceV2 alongside UserService
4. **Field deprecation**: Mark fields as deprecated, remove later

Proto3 is designed for backward compatibility - old clients can read new messages by ignoring unknown fields."

---

## 📋 Proto Best Practices

```protobuf
// Use meaningful package names
package mycompany.userservice.v1;

// Reserve deleted field numbers
message User {
  reserved 4, 15;  // Previously used fields
  reserved "old_field_name";
  
  int32 id = 1;
  string name = 2;
}

// Use wrapper types for nullable fields
import "google/protobuf/wrappers.proto";
message Product {
  google.protobuf.StringValue description = 1;  // nullable
}
```

---

## 🔗 Cross-References

- **HTTP/2**: Foundation for gRPC
- **Microservices**: Common gRPC use case
- **REST API Design**: Alternative approach
- **Message Queues**: For async communication

---

*💡 Pro Tip: gRPC shines for internal service-to-service communication. For public APIs, consider gRPC-Gateway to expose REST endpoints while using gRPC internally.*
