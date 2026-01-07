# Distributed Relay Chat

A scalable, real-time chat application built with a **Microservices Architecture**. This project demonstrates the implementation of a distributed system using Python (FastAPI), Docker, Redis Pub/Sub, and hybrid database persistence (SQL & NoSQL).

![Project Status](https://img.shields.io/badge/status-closed-success)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![Docker](https://img.shields.io/badge/docker-compose-orange)

## Overview

This project was developed as a capstone assignment for the Distributed Systems course at CEFET-MG (Federal Center for Technological Education of Minas Gerais). The main goal was to decouple application logic into independent microservices to ensure High Availability and Horizontal Scalability, adhering to strict academic requirements for distributed architecture.

Unlike a monolithic chat application, this system separates authentication from messaging and uses a Message Broker (Redis) to broadcast messages across different service instances.

### Key Features
* **Microservices Architecture:** Independent services for Authentication and Chat.
* **Real-Time Communication:** Bi-directional messaging using WebSockets.
* **Distributed Messaging:** Uses Redis Pub/Sub to synchronize messages across multiple backend instances.
* **Hybrid Persistence:** 
  * **PostgreSQL**: For structured user data and secure authentication.
  * **MongoDB:** For high-speed storage of chat history (unstructured logs).
* **User Experience:** * Real-time notification badges (red dot).
    * Dynamic user list.
    * Context-aware history loading.
* **Load Testing:** Includes scripts to simulate concurrent users.

---

## Architecture

The system is composed of the following containers orchestrated by Docker Compose:

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | Nginx/HTML/JS | Serves the UI and connects to APIs via Reverse Proxy. |
| **Auth Service** | FastAPI + Postgres | Handles User Registration and Login (JWT/Hashing). |
| **Chat Service** | FastAPI + Mongo | Manages WebSocket connections and chat history. |
| **Message Broker** | Redis | Distributes messages to all active containers (Pub/Sub). |

### Data Flow
1.  **Login:** User authenticates via HTTP (REST) against the Auth Service.
2.  **Connection:** User establishes a WebSocket connection with the Chat Service.
3.  **Messaging:** 
    * When User A sends a message, it is saved to MongoDB.
    * The message is published to Redis.
    * Redis broadcasts it to all Chat Service replicas.
    * The instance holding User B's connection delivers the message.

---

## Tech Stack

* **Language:** Python 3.12
* **Framework:** FastAPI (Async I/O)
* **Databases:** PostgreSQL, MongoDB
* **Broker:** Redis
* **Infrastructure:** Docker, Docker Compose
* **Testing:** Pytest, AsyncIO

---

## Getting Started

### Prerequisites
* Docker & Docker Compose installed.
* Python 3.x (only for running local tests/scripts).

### Installation & Execution

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/gbernalle/relay-chat.git](https://github.com/gbernalle/relay-chat.git)
    cd relay-chat
    ```

2.  **Start the environment:**
    This command builds the images and starts the containers in detached mode.
    ```bash
    docker compose up --build -d
    ```

3.  **Access the Application:**
    Open your browser and navigate to:
    * **App:** `http://localhost` (or your local IP, e.g., `http://192.168.x.x`)
    * **Auth API Docs:** `http://localhost:8001/docs`
    * **Chat API Docs:** `http://localhost:8002/docs`

---

## Testing

The project includes both Unit Tests (logic) and Integration Tests (system).

### 1. Setup Local Environment
To run tests outside Docker, install the dependencies:
```bash
pip install pytest requests websockets httpx psycopg2-binary
```
### 2. Running Unit Tests
Tests the authentication logic using an in-memory database (SQLite mock).

```bash
# Linux/Mac
DATABASE_URL="sqlite:///:memory:" pytest tests/test_unit_auth.py

# Windows (PowerShell)
$env:DATABASE_URL="sqlite:///:memory:"; pytest tests/test_unit_auth.py
```

### 3. Running integration Tests
Tests the full flow (Login -> WebSocket -> History) against the running Docker containers. Ensure Docker is running before executing this command.

```bash
python tests/test_integration.py
```

### 4. Load Testing(Concurrency)
Simulates 10 simultaneous bots connecting and sending messages to test the WebSocket stability.

```bash
python teste_carga.py
```