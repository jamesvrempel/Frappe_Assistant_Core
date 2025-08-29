# Architecture Diagram

## System Overview

```mermaid
graph TB
    subgraph "LLM Layer"
        Claude[Claude Desktop]
        GPT[GPT/Custom LLM]
        API[LLM via API]
        Future[Future LLMs]
    end

    subgraph "Integration Layer"
        MCP[MCP Protocol<br/>JSON-RPC 2.0]
        DXT[DXT File Generator<br/>One-Click Setup]
        Bridge[STDIO Bridge]
    end

    subgraph "Frappe Assistant Core"
        Server[MCP Server<br/>API Handler]
        Registry[Tool Registry<br/>20+ Tools]
        
        subgraph "Plugin System"
            CorePlugin[Core Plugin<br/>Always Enabled]
            DataSci[Data Science<br/>Plugin]
            Viz[Visualization<br/>Plugin]
            Custom[Custom<br/>Plugins]
        end
        
        Security[Security Layer<br/>Auth & Permissions]
        Audit[Audit Trail<br/>Logging System]
    end

    subgraph "ERPNext/Frappe"
        Database[(ERPNext<br/>Database)]
        Docs[Documents<br/>Customers, Sales, etc.]
        Reports[Reports<br/>Analytics]
        Workflows[Workflows<br/>Business Logic]
    end

    %% Connections
    Claude --> MCP
    GPT --> MCP
    API --> MCP
    Future --> MCP
    
    Claude -.->|One-Click| DXT
    DXT --> Bridge
    Bridge --> Server
    
    MCP --> Server
    Server --> Registry
    Registry --> CorePlugin
    Registry --> DataSci
    Registry --> Viz
    Registry --> Custom
    
    Server --> Security
    Server --> Audit
    
    CorePlugin --> Database
    DataSci --> Database
    Viz --> Database
    Custom --> Database
    
    Database --> Docs
    Database --> Reports
    Database --> Workflows

    %% Styling
    classDef llm fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef integration fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef core fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef plugin fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef erp fill:#fce4ec,stroke:#c2185b,stroke-width:2px

    class Claude,GPT,API,Future llm
    class MCP,DXT,Bridge integration
    class Server,Registry,Security,Audit core
    class CorePlugin,DataSci,Viz,Custom plugin
    class Database,Docs,Reports,Workflows erp
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant C as Claude/LLM
    participant M as MCP Server
    participant T as Tool Registry  
    participant P as Plugin
    participant E as ERPNext DB

    U->>C: "Create customer Acme Corp"
    C->>M: MCP Request: create_document
    M->>T: Get tool: create_document
    T->>P: Execute Core Plugin Tool
    P->>E: frappe.get_doc().insert()
    E-->>P: Document Created
    P-->>T: Success Response
    T-->>M: Tool Result
    M-->>C: MCP Response
    C-->>U: "Customer created successfully"
    
    Note over M,E: All operations logged in audit trail
    Note over M: Security & permissions enforced
```

## Plugin Architecture Detail

```mermaid
graph LR
    subgraph "External Apps"
        App1[Custom Frappe App]
        App2[Industry-Specific App]
        App3[Third-Party App]
    end
    
    subgraph "Tool Discovery"
        Hooks[hooks.py<br/>assistant_tools]
        Scanner[Plugin Scanner]
        Registry[Tool Registry]
    end
    
    subgraph "Core Plugins"
        CoreP[Core Plugin<br/>Document Operations]
        DataP[Data Science Plugin<br/>Python Execution]
        VizP[Visualization Plugin<br/>Charts & Dashboards]
    end
    
    subgraph "Runtime Management"
        Manager[Plugin Manager]
        Config[Plugin Configuration]
        State[Enable/Disable State]
    end

    App1 --> Hooks
    App2 --> Hooks  
    App3 --> Hooks
    
    Hooks --> Scanner
    Scanner --> Registry
    
    CoreP --> Registry
    DataP --> Registry
    VizP --> Registry
    
    Registry --> Manager
    Manager --> Config
    Manager --> State

    classDef external fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef discovery fill:#f1f8e9,stroke:#388e3c,stroke-width:2px
    classDef plugins fill:#fff8e1,stroke:#f57f17,stroke-width:2px
    classDef management fill:#fce4ec,stroke:#c2185b,stroke-width:2px

    class App1,App2,App3 external
    class Hooks,Scanner,Registry discovery
    class CoreP,DataP,VizP plugins
    class Manager,Config,State management
```

## Security & Permissions Flow

```mermaid
graph TD
    Request[LLM Request] --> Auth{Authenticated?}
    Auth -->|No| Reject[Reject Request]
    Auth -->|Yes| UserCheck{User Enabled?}
    UserCheck -->|No| Reject
    UserCheck -->|Yes| RoleCheck{Has Assistant Role?}
    RoleCheck -->|No| Reject
    RoleCheck -->|Yes| ToolPerm{Tool Allowed?}
    ToolPerm -->|No| Reject
    ToolPerm -->|Yes| DocPerm{ERPNext Permissions?}
    DocPerm -->|No| Reject
    DocPerm -->|Yes| Execute[Execute Tool]
    Execute --> AuditLog[Log to Audit Trail]
    Execute --> Response[Return Response]

    classDef security fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef success fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef reject fill:#fafafa,stroke:#757575,stroke-width:2px

    class Auth,UserCheck,RoleCheck,ToolPerm,DocPerm security
    class Execute,AuditLog,Response success
    class Reject reject
```

## Deployment Architecture Options

```mermaid
graph TB
    subgraph "Single Server Deployment"
        S1[Frappe Bench<br/>+ Assistant Core]
        S1DB[(Database)]
        S1 --> S1DB
    end
    
    subgraph "Multi-Server Deployment"
        LB[Load Balancer]
        S2[App Server 1]
        S3[App Server 2]
        S4[App Server N]
        S2DB[(Shared Database)]
        Redis[(Redis Cache)]
        
        LB --> S2
        LB --> S3
        LB --> S4
        S2 --> S2DB
        S3 --> S2DB
        S4 --> S2DB
        S2 --> Redis
        S3 --> Redis
        S4 --> Redis
    end
    
    subgraph "Cloud Deployment"
        CDN[CDN/CloudFlare]
        K8S[Kubernetes Cluster]
        RDS[(Managed Database)]
        ElastiCache[(Redis Cluster)]
        
        CDN --> K8S
        K8S --> RDS
        K8S --> ElastiCache
    end

    classDef single fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px
    classDef multi fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    classDef cloud fill:#fff3e0,stroke:#ef6c00,stroke-width:2px

    class S1,S1DB single
    class LB,S2,S3,S4,S2DB,Redis multi
    class CDN,K8S,RDS,ElastiCache cloud
```

## Integration Patterns

```mermaid
graph LR
    subgraph "Pattern 1: Direct Claude Desktop"
        CD[Claude Desktop]
        DXT[DXT File]
        STDIO[STDIO Bridge]
        CD --> DXT --> STDIO
    end
    
    subgraph "Pattern 2: API Integration"
        CustomLLM[Custom LLM App]
        HTTP[HTTP API]
        MCP_API[MCP Endpoint]
        CustomLLM --> HTTP --> MCP_API
    end
    
    subgraph "Pattern 3: Webhook/Event"
        External[External System]
        Webhook[Webhook Endpoint]
        Queue[Background Queue]
        External --> Webhook --> Queue
    end
    
    subgraph "Frappe Assistant Core"
        Core[MCP Server]
    end
    
    STDIO --> Core
    MCP_API --> Core
    Queue --> Core

    classDef pattern1 fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef pattern2 fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px  
    classDef pattern3 fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef core fill:#fce4ec,stroke:#c2185b,stroke-width:2px

    class CD,DXT,STDIO pattern1
    class CustomLLM,HTTP,MCP_API pattern2
    class External,Webhook,Queue pattern3
    class Core core
```