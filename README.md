<div align="center">
  <img src="https://i.imgur.com/your-project-logo.png" alt="Project Logo" width="150">
  <h1>🚀 AI Focus & Attention Tracker 🚀</h1>
  <p>
    <strong>Your personal real-time focus analyst, powered by Computer Vision.</strong>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.9-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/Framework-FastAPI-green.svg" alt="FastAPI">
    <img src="https://img.shields.io/badge/Computer%20Vision-OpenCV%20%7C%20MediaPipe-orange.svg" alt="CV">
    <img src="https://img.shields.io/badge/Monitoring-Prometheus%20%7C%20Grafana-yellow.svg" alt="Monitoring">
    <img src="https://img.shields.io/badge/Container-Docker-blue.svg" alt="Docker">
  </p>
</div>

---

This project is a complete system that uses your webcam to analyze your head pose in real-time, determining whether you are focused, distracted, or looking away. All data is then streamed to a live Grafana dashboard, giving you powerful insights into your attention patterns.

It's a perfect tool for students, developers, and professionals looking to understand and improve their concentration during work or study sessions.

![Dashboard Screenshot](https://i.imgur.com/your-dashboard-screenshot.png) 
*(Note: You can replace this with a real screenshot of your working dashboard!)*

## ✨ Features

-   **👁️ Real-time Head Pose Estimation:** Utilizes OpenCV and Google's MediaPipe to accurately detect facial landmarks and calculate head yaw, pitch, and roll angles from a live webcam feed.
-   **🧠 Focus State Analysis:** A smart, rule-based system classifies your attention state into categories like "Focused," "Distracted," "Looking Down," etc.
-   **🖥️ Live Frontend Display:** A clean, simple web interface shows your webcam feed and your current focus status.
-   **📊 Prometheus Metrics:** The robust FastAPI backend exposes custom time-series metrics for every aspect of the analysis.
-   **📈 Grafana Dashboard:** A beautiful, pre-configured Grafana dashboard visualizes your focus data, showing:
    -   A color-coded timeline of your focus state.
    -   A pie chart breaking down your focus state distribution.
    -   Time-series graphs for the raw head pose angles.

## 🛠️ Tech Stack

| Category          | Technology                                       |
| ----------------- | ------------------------------------------------ |
| **Backend** | `Python 3.9`, `FastAPI`                          |
| **Computer Vision** | `OpenCV`, `MediaPipe`                            |
| **Frontend** | `HTML`, `JavaScript`, `CSS`                      |
| **Monitoring** | `Prometheus`, `Grafana`                          |
| **Containerization**| `Docker`, `Docker Compose`                       |

## 🚀 Getting Started

Follow these steps to get the project up and running on your local machine.

### Prerequisites

-   You must have **Docker** and **Docker Compose** installed on your system. You can download them from the official [Docker website](https://www.docker.com/products/docker-desktop).

### Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd real-time-focus-tracker
    ```

2.  **Clean Up Old Docker Environment (Very Important First Step):**
    To prevent issues with cached data, it's crucial to run these cleanup commands before the first launch and whenever you make significant changes.
    ```bash
    # Stop any running containers for this project
    docker-compose down

    # Remove old data volumes to clear the Grafana cache
    docker-compose down --volumes
    ```

3.  **Build and Run the Containers:**
    This single command will build the application image from scratch and start all three services.
    ```bash
    docker-compose up --build
    ```
    Wait for the logs to show that all three services are running. You should see `focus_tracker_app | INFO: Application startup complete.` without any errors.

---

## 🕹️ How to Use

Once the Docker containers are running, you can access the different parts of the application.

### 1. The Focus Tracker UI

This is the main user interface where you see your webcam feed.

-   **Open the `index.html` file** located in the `frontend` directory of the project. You can simply double-click it to open it in your default web browser.
-   Your browser will ask for permission to use your camera. **You must click "Allow"**.
-   The status should change from "Disconnected" to **"Connected,"** and you will see your focus state being analyzed in real-time.

### 2. The Grafana Dashboard

This is where you can see the analytics and visualizations.

-   **URL:** `http://localhost:3000`
-   **Username:** `admin`
-   **Password:** `admin`
-   The "AI Focus & Attention Tracker" dashboard should be pre-loaded and visible on the home page.

### 3. The Prometheus UI

This is the backend monitoring system where you can see the raw metrics.

-   **URL:** `http://localhost:9090`
-   To verify it's working, navigate to **Status > Targets**. You should see the `fastapi-app` endpoint with a green "UP" status.

## 📂 Project Structure

.
├── app/
│ ├── api/
│ │ └── endpoints/
│ │ └── tracking.py # WebSocket endpoint for CV analysis
│ ├── core/
│ │ ├── init.py
│ │ └── config.py # Application settings
│ ├── services/
│ │ └── focus_analyzer.py # Logic for analyzing focus state
│ ├── vision/
│ │ └── head_pose.py # Head pose estimation logic
│ └── main.py # FastAPI application entrypoint
├── frontend/
│ └── index.html # The main user interface
├── monitoring/
│ ├── grafana/
│ │ └── provisioning/ # Grafana dashboard and datasource configs
│ └── prometheus/
│ └── prometheus.yml # Prometheus configuration
├── Dockerfile
├── docker-compose.yml
└── requirements.txt

yaml
Copy
Edit

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](<your-repo-url/issues>).

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
