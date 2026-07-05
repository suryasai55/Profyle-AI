# API Endpoint Documentation

This document describes all available routes, parameters, payloads, and transaction rules within the **PlacementReady AI Application**.

---

## 1. Authentication Endpoints

### Register Account
*   **Path**: `/auth/register`
*   **Method**: `GET | POST`
*   **Authentication**: None
*   **Request Parameters (POST Form)**:
    *   `name` (string, required): Full name of the candidate.
    *   `email` (string, required): Email address (must be unique).
    *   `password` (string, required): Password string.
*   **Database Operation**: Inserts a new record in `User` table with a secure `pbkdf2:sha256` password hash.
*   **Response**: Redirects to `/auth/login` on success, or re-renders registration page with validation warnings.

### Login Session
*   **Path**: `/auth/login`
*   **Method**: `GET | POST`
*   **Authentication**: None
*   **Request Parameters (POST Form)**:
    *   `email` (string, required): Login email.
    *   `password` (string, required): Login password.
*   **Response**: Establishes session cookie via Flask-Login and redirects to `/` on success, or returns status warnings on error.

### Logout Session
*   **Path**: `/auth/logout`
*   **Method**: `GET`
*   **Authentication**: Logged-in session required.
*   **Response**: Destroys session cookies and redirects to `/auth/login`.

---

## 2. Dashboard Endpoints

### Main Landing Page
*   **Path**: `/`
*   **Method**: `GET`
*   **Authentication**: None (If logged in, displays custom stats. If anonymous, displays system feature overview).
*   **Response**: Renders `dashboard/index.html`. For authenticated users, it passes:
    *   `metrics.has_resume`: Boolean indicating if user has uploaded a resume.
    *   `metrics.resume_score`: NLP calculated resume score (0-100).
    *   `metrics.readiness_score`: Overall readiness score (0-100).
    *   `metrics.completed_questions`: Number of completed interview prep questions.
    *   `metrics.recent_resumes`: List of last 5 uploaded resumes.

---

## 3. Resume Endpoints

### Upload Resume
*   **Path**: `/resume/upload`
*   **Method**: `GET | POST`
*   **Authentication**: Logged-in session required.
*   **Request Parameters (POST Form)**:
    *   `resume` (File, required): PDF format resume file.
*   **Database Operation**:
    *   Inserts record in `Resume` table (saving filename and detected/missing skills strings).
    *   Auto-creates/updates the user's `PlacementReadiness` record to set the `resume_score` value, recalculates the composite overall placement score.
*   **S3 Integration**: If `USE_S3=True` is enabled in configuration, uploads the file to the S3 bucket and saves `s3_key` in database.
*   **Response**: Redirects to `/resume/results/<resume_id>`.

### View Parsing Results
*   **Path**: `/resume/results/<int:resume_id>`
*   **Method**: `GET`
*   **Authentication**: Logged-in session required (User can only view their own resume).
*   **Response**: Renders `resume/results.html` displaying NLP score, list of matched skill tags, and list of missing skill tags.

---

## 4. Skill Gap Endpoints

### Skill Gap Analysis
*   **Path**: `/skill_gap/analysis`
*   **Method**: `GET`
*   **Authentication**: Logged-in session required.
*   **Query Parameters**:
    *   `role` (string, optional): Target career role. Options: `python_dev` (default), `data_analyst`, `ml_engineer`, `devops_engineer`, `backend_dev`.
*   **Response**: Compares candidate's latest resume skills against database roles mapping. Renders `skill_gap/analysis.html` displaying tech stack matching percentage, missing skills tags, and prioritized course syllabus recommendations.

---

## 5. Placement Readiness Endpoints

### View Composite Scores
*   **Path**: `/readiness/score`
*   **Method**: `GET`
*   **Authentication**: Logged-in session required.
*   **Response**: Fetches user's `PlacementReadiness` row. Renders `readiness/score.html` displaying aggregate Dial metrics, sub-score progress bars (Resume 40% weight, Aptitude 30% weight, Interview 30% weight), and recommendations.

---

## 6. Interview Preparation Endpoints

### Practice Portal
*   **Path**: `/interview/prep`
*   **Method**: `GET`
*   **Authentication**: Logged-in session required.
*   **Query Parameters**:
    *   `category` (string, optional): Filter by topic. Default: `Python`.
    *   `search` (string, optional): Keyword search queries.
*   **Response**: Renders `interview/prep.html` showing sidebar topic completion statistics, search filters, and question lists.

### Toggle Bookmark
*   **Path**: `/interview/bookmark/toggle/<int:question_id>`
*   **Method**: `GET` (or redirect wrapper)
*   **Authentication**: Logged-in session required.
*   **Database Operation**: Inserts or deletes record in `Bookmark` table.
*   **Response**: Redirects to `/interview/prep` with flash message.

### Toggle Completion
*   **Path**: `/interview/complete/toggle/<int:question_id>`
*   **Method**: `GET` (or redirect wrapper)
*   **Authentication**: Logged-in session required.
*   **Database Operation**: Inserts or updates record in `InterviewHistory` table. Recalculates candidate's `interview_score` (`10 * completed_count` capped at 100) and updates `PlacementReadiness` overall score.
*   **Response**: Redirects to `/interview/prep` with flash message.
