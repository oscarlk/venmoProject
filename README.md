Venmo Analytics Platform

A full-stack web application that analyzes personal Venmo transaction patterns and generates insights that are not available in the native Venmo application.

The platform ingests Venmo transaction data and computes analytics such as average payback time, top interaction partners, and payment trends to help users better understand their spending and repayment behaviors.

Demo

Working Demo:
https://drive.google.com/file/d/1H1P5uHx4OyU9GiyUxEJeG8Ze0Bh7LwlK/view

Tech Stack
Frontend

React

JavaScript

HTML / CSS

Backend

Python

Flask

REST APIs

Additional Tools

OAuth authentication

Environment variable configuration

JSON data processing

Key Features
Transaction Analytics

Compute insights from Venmo transaction history including:

Average payback time between users

Most frequent transaction partners

Payment direction (who pays whom most often)

Interactive Web Interface

The React frontend provides a user-friendly interface for viewing analytics and interacting with the system.

Custom Backend APIs

The Flask backend exposes REST endpoints that process transaction data and return structured analytics results to the frontend.

System Architecture
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
How the System Works

The frontend sends requests to the Flask backend.

The backend processes Venmo transaction data.

Custom analytics algorithms compute insights such as payback time and transaction rankings.

The backend returns structured JSON responses.

The frontend visualizes the results for the user.

Repository Structure
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
Setup Instructions
Backend

Navigate to the backend directory.

cd backend

Install Python dependencies.

pip install -r requirements.txt

Create a .env file with required environment variables.

Start the backend server.

python server.py
Frontend

Navigate to the frontend directory.

cd frontend

Install dependencies.

npm install

Start the development server.

npm run dev

The application should now be running locally.

Engineering Decisions
Flask Backend

Flask was chosen because it provides a lightweight framework for building REST APIs quickly while keeping the backend logic simple and easy to extend.

React Frontend

React enables component-based UI development and simplifies building interactive analytics dashboards.

REST API Architecture

Using REST APIs allows the frontend and backend to remain decoupled and enables the backend to evolve independently.

Custom Analytics Logic

The backend computes metrics such as average payback time by analyzing reciprocal transactions between users and calculating the time differences between payments.

Future Improvements

Several improvements could be made to scale the system further.

Database Integration

Currently transaction data is processed in memory. Introducing a database would allow the system to scale to larger datasets.
