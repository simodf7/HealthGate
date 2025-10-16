# HealthGate  
*A Microservice-based AI System for Decision Support and Emergency Department Overcrowding Reduction*  

---

## Table of Contents

- [Overview & Motivation](#overview--motivation)  
- [System Goals](#system-goals)  
- [Stakeholders](#stakeholders)  
- [Functional & Non-Functional Requirements](#functional--non-functional-requirements)  
- [Architecture Overview](#architecture-overview)  
- [System Components](#system-components)  
  - [API Gateway](#api-gateway)  
  - [Authentication Service](#authentication-service)  
  - [Symptoms Ingestion Service](#symptoms-ingestion-service)  
  - [Decision Engine Service](#decision-engine-service)  
  - [Aggregator Service](#aggregator-service)  
  - [Report Management Service](#report-management-service)  
  - [Frontend](#frontend)  
- [Implementation Details](#implementation-details)  
- [Testing & Continuous Monitoring](#testing--continuous-monitoring)  
- [Deployment with Docker](#deployment-with-docker)  
- [Results & Evaluation](#results--evaluation)  
- [Repository Structure](#repository-structure)  
- [Contributing](#contributing)  
- [License & Acknowledgements](#license--acknowledgements)  

---

## Overview & Motivation

Emergency departments worldwide face chronic overcrowding due to the **large number of inappropriate visits** by patients with non-urgent symptoms. This leads to longer waiting times, increased healthcare costs, and greater stress on medical staff.

**HealthGate** addresses this challenge by providing an **AI-driven decision support system** capable of assessing patient-reported symptoms — either spoken or written — and determining whether an emergency visit is necessary.  

The system leverages **Large Language Models (LLMs)**, a **microservice architecture**, and **FHIR-compatible interfaces** to create an interoperable, scalable, and transparent e-health platform.

---

## System Goals

- Reduce inappropriate emergency room visits through intelligent triage suggestions  
- Offer real-time **decision support** to patients and medical staff  
- Integrate heterogeneous health services via **standardized microservices**  
- Ensure data **security, traceability, and scalability**  
- Provide **explainable AI outputs** for clinical trust and accountability  

---

## Stakeholders

- **Patients:** Receive guidance on whether their symptoms require emergency care  
- **Healthcare Professionals:** Access automatically generated reports to accelerate patient assessment  

---

## Functional & Non-Functional Requirements

### Functional
1. User registration (patients and operators)  
2. Secure authentication and session management  
3. Symptom recording (voice or text input)  
4. Automatic transcription, correction, and normalization of inputs  
5. Clinical decision generation (ER recommended or not)  
6. Automatic report generation and storage  
7. Report consultation for both patients and medical staff  
8. Historical record retrieval and update functionality  

### Non-Functional
1. Secure storage of sensitive patient data  
2. Low latency and high responsiveness  
3. Lightweight and mobile-friendly models  
4. Transparent and explainable decision rationale  
5. Scalability for growing user and data volumes  
6. Ease of maintenance and modular extensibility  
7. Robustness to data drift and linguistic variability  

---

## Architecture Overview

HealthGate adopts a **microservice architecture** ensuring modularity, independence, and scalability.  
All communications occur via REST APIs orchestrated by an **API Gateway**.  

Key principles:
- **Single Entry Point:** API Gateway routes all external requests  
- **Independent Services:** Each microservice handles a specific function  
- **Decoupling:** Services can be deployed, updated, or scaled independently  
- **Asynchronous Communication:** Enables high throughput and resilience  

---

## System Components

### API Gateway
- Developed with **FastAPI** (Python)  
- Central entry point for all frontend and API calls  
- Handles:
  - JWT-based authentication and role validation  
  - Routing and load balancing  
  - Fault tolerance (timeouts, retries)  
  - Message transformation and secure header propagation  
- Hides the internal network topology from clients  

---

### Authentication Service
- Built using **FastAPI**, **PostgreSQL**, and **SQLAlchemy (async)**  
- Manages registration, login, and token generation for patients and operators  
- Uses **bcrypt** for password hashing and **JWT** for stateless authentication  
- Exposes REST endpoints:
  - `POST /signup/patient`
  - `POST /signup/operator`
  - `POST /login/patient`
  - `POST /login/operator`  
- Supports **role-based access control (RBAC)** through token payload scopes  

---

### Symptoms Ingestion Service
- Handles **multimodal input**: voice or text  
- Converts audio to text via **Whisper** (Speech-to-Text)  
- Uses **Gemini 2.0 Flash LLM** for linguistic correction and semantic normalization  
- Implements the **Adapter Pattern** to decouple from the Decision Engine  
- Outputs cleaned, structured text in JSON format  
- Asynchronous architecture for parallel processing  

---

### Decision Engine Service
- Core of HealthGate’s reasoning layer  
- Implements a **Retrieval-Augmented Generation (RAG)** pipeline integrating:
  - **LLM (Gemini 2.0 Flash)** for reasoning and natural language generation  
  - **ChromaDB** as a vector store for clinical document retrieval  
  - **SentenceTransformers (all-MiniLM-L6-v2)** for embedding generation  
- Steps:
  1. Query formulation from symptoms + patient history  
  2. Retrieval of relevant clinical guidelines  
  3. Context encoding and response generation  
- Outputs:
  - Decision (“ER recommended / not necessary”)  
  - Explanation based on retrieved evidence  
- Automatically generates and forwards reports to the Report Management Service  

---

### Aggregator Service
- Data orchestration layer  
- Aggregates patient demographic data (from Auth Service) and clinical history (from Report Service)  
- Provides a **unified patient profile** to the Decision Engine  
- Minimizes coupling between analytical and data services  

---

### Report Management Service
- Responsible for **report lifecycle management**  
- Persists and serves clinical reports through a **MongoDB** backend  
- Endpoints:
  - `POST /report` → Create a new report  
  - `GET /reports/id/{patient_id}` → Retrieve all reports by patient ID  
  - `PUT /report/{report_id}` → Update existing reports  
  - `GET /report/pdf/{report_id}` → Export report as PDF  
- Generates PDF reports via **Jinja2** templates + **xhtml2pdf**  
- Enables download, update, and historical access  

---

### Frontend
- Developed in **Streamlit (Python)** for rapid web interface prototyping  
- Communicates exclusively with the API Gateway  
- Modules:
  - `HealthGate.py`: main controller, navigation, and state handling  
  - `login.py` / `signup.py`: user authentication and registration  
  - `patient_ui.py`: symptom entry (voice/text), report consultation  
  - `operator_ui.py`: report search, filtering, and PDF download  
- Real-time feedback through interactive UI components  
- Clean, CSS-based design for clarity and usability  

---

## Implementation Details

- **Language:** Python 3.11+  
- **Frameworks:** FastAPI, Streamlit, SQLAlchemy, httpx  
- **Databases:** PostgreSQL (Auth), MongoDB (Reports)  
- **AI/ML Stack:** Whisper, Gemini 2.0 Flash, SentenceTransformers, ChromaDB  
- **Containerization:** Docker & Docker Compose  
- **Security:** JWT authentication, role-based access control, encrypted storage  
- **Configuration:** Environment variables managed via `.env` file  

---

## Testing & Continuous Monitoring

**Testing Phases:**
1. **Functional Testing:** Verification of REST endpoints for each microservice  
2. **Integration Testing:** Validation of inter-service communication and JWT handling  
3. **Database Testing:** CRUD consistency on PostgreSQL and MongoDB  
4. **Frontend Testing:** UI interaction and state validation via Streamlit  
5. **Decision Model Testing:**  
   - *Operational Testing:* comparison of system vs. expected decisions  
   - *LLM-as-Evaluator Testing:* second LLM evaluates model reasoning  
   - *Robustness Testing:* ensures decision consistency under linguistic variation  

**Continuous Monitoring:**  
Future versions may integrate **Prometheus**, **Grafana**, or **ELK Stack** for live system metrics and centralized logging.

---

## Deployment with Docker

**Local setup:**
```bash
git clone https://github.com/simodf7/HealthGate.git
cd HealthGate
docker-compose up -d --build
```

Each microservice runs in its own container within the shared network `microservices-network`.

**Default ports:**

| Service | Port |
|----------|------|
| API Gateway | 8010 |
| Authentication | 8001 |
| Decision Engine | 8002 |
| Ingestion | 8003 |
| Report Management | 8004 |
| Aggregator | 8005 |
| Frontend | 8501 |

---

## Results & Evaluation

- Full communication among microservices verified  
- Secure and synchronized data flow between PostgreSQL and MongoDB  
- End-to-end interaction between frontend and gateway successful  
- Stable and reproducible local deployment through Docker Compose  
- Robust, modular, and scalable prototype suitable for further clinical integration  

---

## Repository Structure

```
HealthGate/
├── documentation/             # Design docs, SysML diagrams, specifications
├── frontend/                  # Streamlit-based web interface
├── microservices/             # API Gateway, Auth, Ingestion, Decision, Aggregator, Report
├── docker-compose.yml         # Container orchestration file
├── HealthGate.py              # Main frontend launcher
├── .env.example               # Environment configuration template
├── README.md                  # This file
└── varie/                     # Utilities, scripts, helpers
```

---

## Contributing

Contributions are welcome!  
To contribute:

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/your-feature`)  
3. Implement and test your changes  
4. Submit a pull request  

Please ensure:
- Code adheres to style and naming conventions  
- Documentation and tests are updated  
- Services remain independent and decoupled  

---

## License & Acknowledgements

**License:** currently unlicensed (you may add MIT, Apache-2.0, or GPL as appropriate).  

**Acknowledgements:**  
Developed as part of the *AI System Engineering* course at **University of Naples Federico II**, by:  
- **Alessandro Campanella**  
- **Rita Castaldi**  
- **Simone Di Fraia**  
under the supervision of **Prof. Roberto Pietrantuono** (A.Y. 2024-25).  

HealthGate draws inspiration from modern research on microservice architectures, LLM-based decision systems, and FHIR interoperability for digital health ecosystems.
