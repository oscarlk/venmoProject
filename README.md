# Venmo Analytics Platform

A full-stack web application that analyzes personal Venmo transaction patterns and generates insights that are not available in the native Venmo application.

The platform ingests Venmo transaction data and computes analytics such as **average payback time**, **top interaction partners**, and **payment trends** to help users better understand their spending and repayment behaviors.

---

# Demo

Working Demo:  
https://drive.google.com/file/d/1H1P5uHx4OyU9GiyUxEJeG8Ze0Bh7LwlK/view

---

# Tech Stack

## Frontend
- React
- JavaScript
- HTML / CSS

## Backend
- Python
- Flask
- REST APIs

## Additional Tools
- OAuth authentication
- Environment variable configuration
- JSON data processing
- Material Design UI

---

# Key Features

## Transaction Analytics

Compute insights from Venmo transaction history including:

- Average payback time between users
- Most frequent transaction partners
- Payment direction (who pays whom most often)

---

## Data Ingestion Strategy

Venmo does not provide a public-facing API for accessing user transaction data. Because of this limitation, I implemented a custom data ingestion approach using the email notifications that Venmo sends for each transaction.

The backend retrieves these emails and uses regular expressions to extract key transaction fields such as:

- Sender or recipient
- Transaction amount
- Timestamp
- Email subject and metadata

This parsing layer converts the unstructured email content into structured transaction data that can then be processed by the analytics engine.

While this approach introduces some additional processing overhead, it enables the system to work with real Venmo transaction data despite the absence of official APIs.

## Interactive Web Interface

The React frontend provides a user-friendly interface for viewing analytics and interacting with the system.

---

## Custom Backend APIs

The Flask backend exposes REST endpoints that process transaction data and return structured analytics results to the frontend.

---

# System Architecture

```
                +-------------------+
                |   React Frontend  |
                |  UI / Analytics   |
                +---------+---------+
                          |
                          | REST API
                          |
                +---------v---------+
                |   Flask Backend   |
                |  API Endpoints    |
                +---------+---------+
                          |
                          | Data Processing
                          |
                +---------v---------+
                | Analytics Engine  |
                | Transaction Logic |
                +---------+---------+
                          |
                          |
                +---------v---------+
                | Venmo Transaction |
                |       Data        |
                +-------------------+
```

---

# How the System Works

1. The frontend sends requests to the Flask backend.
2. The backend processes Venmo transaction data.
3. Custom analytics algorithms compute insights such as payback time and transaction rankings.
4. The backend returns structured JSON responses.
5. The frontend visualizes the results for the user.

---

# Repository Structure

```
venmoProject
│
├── frontend
│   ├── src
│   └── React application
│
├── backend
│   ├── server.py
│   └── analytics logic
│
└── README.md
```

---

# Setup Instructions

## Backend

Navigate to the backend directory.

```bash
cd backend
```

Install Python dependencies.

```bash
pip install -r requirements.txt
```

Create a `.env` file with required environment variables.

Start the backend server.

```bash
python server.py
```

---

## Frontend

Navigate to the frontend directory.

```bash
cd frontend
```

Install dependencies.

```bash
npm install
```

Start the development server.

```bash
npm run dev
```

The application should now be running locally.

---

# Engineering Decisions

## Flask Backend

Flask was chosen because it provides a lightweight framework for building REST APIs quickly while keeping the backend logic simple and easy to extend.

---

## React Frontend

React enables component-based UI development and simplifies building interactive analytics dashboards.

---

## REST API Architecture

Using REST APIs allows the frontend and backend to remain decoupled and enables the backend to evolve independently.

---

## Custom Analytics Logic

The backend computes metrics such as average payback time by analyzing reciprocal transactions between users and calculating the time differences between payments.

---

# Future Improvements

Several improvements could be made to scale the system further.

## Database Integration
Currently transaction data is processed in memory. Introducing a database would allow the system to scale to larger datasets.

---

## Authentication Refactor

One improvement I would make is replacing the current Simple Gmail-based integration with the Google Auth library directly. This change would require migrating the existing API calls and authentication flow, but it would reduce abstraction overhead, give finer control over OAuth token management, and make the system more robust, maintainable, and easier to extend as the project grows.

---

## Performance Optimization

Another improvement would be lowering the latency of loading analytics in the application. As the transaction dataset grows, computing results on demand can become slower and create a less responsive experience. To address this, I would consider precomputing frequently requested metrics, introducing a caching layer for repeated queries, and restructuring parts of the backend processing pipeline to avoid unnecessary recomputation. This would improve responsiveness and make the system scale more effectively.
