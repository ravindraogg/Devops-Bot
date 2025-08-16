# 🔧 DevOps Assistant CLI

**Your Senior DevOps Engineer for Production Debugging**

A powerful command-line tool powered by Google's Gemini AI that acts as your personal senior DevOps engineer, helping you debug production issues, analyze logs, and resolve infrastructure problems with expert-level guidance.

## 🚀 Features

- **Expert Log Analysis**: Analyze error logs, stack traces, and system outputs with AI-powered insights
- **Root Cause Analysis**: Identify the underlying causes of production issues
- **Actionable Solutions**: Get both immediate fixes and long-term preventive measures
- **Multi-Platform Support**: Works with Docker, Kubernetes, CI/CD pipelines, and cloud infrastructure
- **Interactive CLI**: Easy-to-use command-line interface with rich formatting
- **Real-time Debugging**: Paste your logs and get instant expert analysis

## 🛠️ Supported Technologies

- **Containers**: Docker, Docker Compose, Kubernetes etc...
- **CI/CD**: GitHub Actions, Jenkins, GitLab CI etc...
- **Databases**: PostgreSQL, MongoDB, MySQL etc...
- **Web Servers**: Nginx, Apache etc...
- **Cloud Platforms**: AWS, Azure, GCP etc...
- **Monitoring**: System logs, application errors, network issues etc...

## 📋 Prerequisites

- Python 3.7+
- Google Gemini API key
- Internet connection for AI analysis

## ⚙️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ravindraogg/Devops-Bot.git
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**:
    create a `.env` file:
   ```env
   GEMINI_API_KEY=your-gemini-api-key-here
   ```

## 🎯 Usage

### Basic Usage

```bash
python devops.py
```

The CLI will start and present you with an interactive interface where you can paste logs, error messages, or describe your production issues.

### Example CLI Session

```
PS D:\Projects\Devops-Bot> python devops.py
╭──────────────────────────────────────────────────────────── Welcome ─────────────────────────────────────────────────────────────╮
│ 🔧 DevOps Assistant CLI 🔧                                                                                                       │
│ Your Senior DevOps Engineer for Production Debugging                                                                             │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Type 'help' for available commands, 'exit' to quit

DevOps (): [ERROR] 2025-08-16 12:07:45 - UnhandledPromiseRejectionWarning: MongoNetworkError: failed to connect to server [localhost:27017] on first connect
⠦ 🤔 Analyzing your issue...

🔍 DevOps Analysis:

Alright, let's break this down. This is a very common error, especially when moving applications into containerized environments.   

The log line is clear: MongoNetworkError: failed to connect to server [localhost:27017]. The application, a Node.js process
(indicated by UnhandledPromiseRejectionWarning), tried to connect to a MongoDB database it expected to find on localhost at port    
27017, and the connection failed.

                                                       1. Root Cause Analysis

The root cause is that the application cannot reach a MongoDB process at localhost:27017 from its own perspective. The key is       
understanding what localhost means in the context where your application is running.

 • On a Developer's Laptop or a Single VM: localhost means "this same machine". The error implies the mongod process is either not  
   running, not listening on port 27017, or is firewalled.
 • Inside a Docker Container: localhost refers to the inside of that specific application container. The database is almost
   certainly running in a different container. Your application is looking for MongoDB inside itself and finding nothing. This is   
   the most frequent cause of this error.
 • Inside a Kubernetes Pod: localhost refers to the pod's network namespace. Similar to Docker, the database will be in a different 
   pod, and localhost is the wrong address. You must use the Kubernetes service discovery mechanism.

                                                 2. Immediate Fix & Debugging Steps

We need to identify where the app and database are and fix the connection string. Let's run some diagnostics.

                                                 Step 1: Verify MongoDB is Running

First, confirm your MongoDB instance is actually running.

 • On a Linux Server (non-containerized):
   
    # Check if the service is active
    sudo systemctl status mongod
   
    # Check which IP address it's listening on.
    # 127.0.0.1 means localhost only. 0.0.0.0 means all interfaces.
    ss -tlpn | grep 27017
   
 • In Docker:
   
    # See if a mongo container is running
    docker ps | grep mongo
   
 • In Kubernetes:
   
    # Find your mongo pod(s)
    kubectl get pods -l app=mongodb # Or whatever label you use
   

                                                 Step 2: Fix The Connection String

This is where the actual fix lies. You must use the correct address for MongoDB in your application's configuration (likely an      
environment variable).

Scenario A: If you are using Docker Compose

Your application must use the Docker service name to connect, not localhost.

 • Example docker-compose.yml:
   
    version: '3.8'
    services:
      myapp:
        image: my-node-app:latest
        ports:
          - "3000:3000"
        environment:
          # WRONG: MONGO_URI=mongodb://localhost:27017/mydatabase
          # CORRECT: Use the service name 'mongo'
          MONGO_URI: mongodb://mongo:27017/mydatabase
        depends_on:
          - mongo
   
      mongo: # This is the service name
        image: mongo:latest
        ports:
          - "27017:27017"
   
 • Fix: Update your application's environment variable (MONGO_URI or similar) to use the service name (mongo in this case).

                                                  3. Long-Term Preventive Measures

 1 Always use Environment Variables for Configuration: Never hardcode connection strings like localhost. Your code should read this 
   from the environment. This makes your application portable across development, staging, and production without code changes.     
   
    // Example in Node.js
    const mongoUri = process.env.MONGO_URI || 'mongodb://localhost:27017/defaultdb';
   
 2 Implement Health Checks: Your application should have a /health endpoint that checks its dependency connections (like the        
   database). In Kubernetes, use this for Liveness and Readiness probes. This prevents traffic from being sent to a pod that can't  
   serve requests because its database connection is down.
   
 3 Improve Application Error Handling: The developer team should wrap the initial database connection logic in a try...catch block  
   (or use a .catch() for promises) to handle this specific MongoNetworkError gracefully.

                                                       4. Verification Steps

 1 Apply the fix by updating your environment variable with the correct connection string.
 2 Restart your application.
    • Docker: docker-compose up -d --force-recreate myapp
    • Kubernetes: kubectl rollout restart deployment/myapp-deployment
 3 Check the new logs.
    • Docker: docker logs <myapp_container_id>
    • Kubernetes: kubectl logs -f <myapp_pod_name>
 4 The MongoNetworkError should be gone. You should see a log message indicating a successful connection to the database.

DevOps ():
```

## 💡 Common Use Cases

### 1. Container Issues
- **CrashLoopBackOff in Kubernetes**
- **Docker container startup failures**
- **Image build problems**

### 2. Database Connection Problems
- **MongoDB connection failures**
- **PostgreSQL authentication issues**
- **Database timeout errors**

### 3. Network and Port Conflicts
- **Port already in use errors**
- **Load balancer configuration issues**
- **Service discovery problems**

### 4. CI/CD Pipeline Failures
- **GitHub Actions SSH errors**
- **Build and deployment failures**
- **Permission and authentication issues**

### 5. Web Server Configuration
- **Nginx configuration errors**
- **Apache startup problems**
- **SSL certificate issues**

## 🔧 What You Get

For every issue you submit, the DevOps Assistant provides:

1. **🔍 Root Cause Analysis**: Deep dive into what's actually causing the problem
2. **⚡ Immediate Fix**: Quick commands and configs to resolve the issue now
3. **🛡️ Long-term Prevention**: Best practices to prevent the issue from recurring
4. **✅ Verification Steps**: Commands to confirm your fix worked

## 📝 Input Examples

You can paste any of these types of inputs:

```bash
# Error logs
[ERROR] 2025-08-16 12:07:45 - Connection refused on port 5432

# Stack traces  
Error: Cannot find module '/usr/src/app/server.js'
    at Function.Module._resolveFilename (internal/modules/cjs/loader.js:581:15)

# Kubernetes events
Warning  BackOff    12s (x4 over 45s)  kubelet  Back-off restarting failed container

# System logs
bind() to 0.0.0.0:80 failed (98: Address already in use)
```

## 🤖 AI-Powered Analysis

The tool leverages Google's Gemini AI model to provide:
- Expert-level troubleshooting
- Context-aware solutions
- Best practice recommendations
- Multi-technology support

## 🔒 Security & Privacy

- Your logs are processed by Google's Gemini AI
- No data is stored permanently by the tool
- API communications are encrypted
- Consider sanitizing sensitive information before analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Google's Gemini AI
- Inspired by the DevOps community's collaborative spirit
- Designed for engineers, by engineers

---

**Ready to debug like a senior DevOps engineer?** 🚀

```bash
python devops.py
```