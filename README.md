<<<<<<< HEAD
# Cloud-Based AI Career Assistant Platform

An intelligent, cloud-compatible Flask web application designed to help candidate job applicants evaluate their placement readiness through NLP-driven resume parsing, target skill gap analysis, customized learning recommendations, and interactive topic-based mock interview preparation.

---

## 🚀 Key Features

*   **Secure Authentication**: Session-based candidate logins (sign-up, sign-in, and log-out routes).
*   **NLP Resume Parser**: Extracts text content from PDF formats, removes NLTK stopwords, tokenizes tech stacks, and calculates an initial alignment score.
*   **Skill Gap Visualizer**: Compares candidate credentials against target industry roles (Python Developer, Backend Dev, ML Engineer, Data Analyst, DevOps) and maps gaps side-by-side.
*   **Curriculum Paths Engine**: Dynamically displays recommended syllabus pathways and links based on identified career gap priorities.
*   **Weighted Readiness Score**: Evaluates candidate readiness using a composite coefficient formula: `40% Resume parsing score + 30% Aptitude metrics + 30% Interview Q&A completion rate`.
*   **Q&A Practice Portal**: Topic-based questions across Python, SQL, Docker, Git, AWS, HR, and Behavioral rounds with answer toggles, bookmark tracking, and completion scoring.
*   **Telemetry & Observability**: Integrated AWS CloudWatch logging and private AWS S3 storage adapters.
*   **Orchestration & CI/CD**: Ready-to-use Docker configs and Jenkinsfile declarative pipelines.

---

## 🛠️ Technology Stack

*   **Backend**: Python 3.12, Flask, Flask-SQLAlchemy (SQLite ORM), Flask-Login
*   **NLP Text Engine**: PyPDF2, Natural Language Toolkit (NLTK Tokenizer)
*   **Data Visualization**: Chart.js, HTML5 canvas, Bootstrap 5, Custom CSS3
*   **DevOps / Infrastructure**: AWS S3, AWS CloudWatch Logs, IAM Profiles, AWS EC2, Docker, docker-compose, Jenkins CI/CD pipelines

---

## 📂 Folder Structure

```
AI-Career-Assistant/
├── app/
│   ├── auth/                   # Session management & user blueprints
│   ├── dashboard/              # Core metrics & stats dashboard
│   ├── resume/                 # PDF extraction & NLP skill parser
│   ├── interview/              # Question banks, bookmarks & completion checks
│   ├── skill_gap/              # Comparative skill analysis templates
│   ├── readiness/              # Readiness scores & status coefficients
│   ├── models/                 # SQLAlchemy database schemas (user, resume, prep, readiness)
│   ├── static/                 # Stylesheets (styles.css) and script files
│   ├── templates/              # Jinja2 views (layout & blocks)
│   └── utils/                  # AWS S3 loaders, logging modules & nltk setups
├── datasets/
│   └── skill_roles.json        # 5 target roles, 16 curriculum pathways
├── questions/                  # Preloaded mock questions (JSON)
├── tests/                      # Automated unittest suites (auth, parsing, readiness)
├── uploads/                    # Local PDF files storage (gitignored)
├── Dockerfile                  # Production container build recipe
├── docker-compose.yml          # Container configuration with persistence volumes
├── Jenkinsfile                 # Jenkins declarative CI/CD pipeline
├── requirements.txt            # Python packages manifest
├── app.py                      # Flask runner & DB preloader script
└── config.py                   # Environment configuration classes
```

---

## 💻 Local Setup & Execution

### 1. Installation
Open a terminal in the project directory:
```bash
# Create and activate python virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install package requirements
pip install -r requirements.txt
```

### 2. Run Flask Dev Server
```bash
# Runs app.py on port 5000 (pre-populates database on startup)
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 📦 Container Orchestration (Docker)

To run the containerized application locally (requires Docker):
```bash
# Build and run the app in the background
docker-compose up --build -d

# Verify container logs
docker-compose logs -f
```
The compose configuration mounts local volumes (`./db` and `./uploads`) to host directories, ensuring that database updates and resume uploads persist across container restarts.

---

## 🧪 Running Automated Tests

A comprehensive suite of unit and integration tests is included. Run the tests using the following command:
```bash
# Run all test cases in the tests/ folder
python -m unittest discover -s tests
```

### Scripted Verification Runners
Individual feature check scripts are located in the project root:
*   `python verify_app.py`: Verification of application factory.
*   `python verify_auth.py`: Verification of registration, duplication, and logins.
*   `python verify_analyzer.py`: Verification of NLP scanner & parsing algorithms.
*   `python verify_skill_gap.py`: Verification of role match & course recommended targets.
*   `python verify_readiness.py`: Verification of weighted readiness scores and dashboard gauges.
*   `python verify_interview.py`: Verification of bookmarks & completion database toggles.

---

## 📄 Documentation Links
*   Refer to [AWS_DEPLOYMENT_GUIDE.md](file:///E:/AI-Career-Assistant/AWS_DEPLOYMENT_GUIDE.md) for full cloud configuration steps (IAM, S3, EC2, Jenkins Pipelines, and CloudWatch Logs).
*   Refer to [API_DOCUMENTATION.md](file:///E:/AI-Career-Assistant/API_DOCUMENTATION.md) for complete backend endpoint descriptions, JSON payloads, and schemas.
=======
# Profyle-AI
>>>>>>> e8d3935ff3ced87bd635d70289d4f6a5074f39a0
