# AgentHub – Multi-Agent Problem Solver

AgentHub is a next-generation, multi-agent problem-solving platform built with Google's Agent Development Kit (ADK). It combines role-based AI orchestration with web-grounded research and iterative solution refinement. Designed for hackathons and production deployment, AgentHub dynamically identifies expertise roles, gathers evidence, and produces comprehensive outputs for real-world scenarios.

---

## 🚀 Key Features

- **Multi-Agent Orchestration:** Sophisticated agent coordination using Google ADK's SequentialAgent framework.
- **Dynamic Role Identification:** Automatically determines the expert roles required for each problem.
- **Web-Grounded Research:** Uses real-time Google Search for data collection and fact verification.
- **Evidence-Based Analysis:** Structured insights with citations and benchmarks.
- **Iterative Problem Solving:** Multi-stage refinement and validation.
- **Cloud-Native Architecture:** Google Cloud Platform (GCP) ready with Vertex AI integration.
- **Observability & Monitoring:** Logging, tracing, and analytics via BigQuery and OpenTelemetry.
- **Production-Ready Deployment:** Terraform, Docker, CI/CD pipelines included.

---

## 🏗️ Architecture

```
agenthub/
├── app/
│   ├── agent.py            # Multi-agent system core
│   ├── server.py           # FastAPI backend (ADK integration)
│   └── utils/
│       ├── gcs.py          # GCP storage helpers
│       ├── tracing.py      # OpenTelemetry integration
│       └── typing.py       # Type definitions
├── .cloudbuild/
│   ├── deploy-to-prod.yaml
│   ├── pr_checks.yaml
│   └── staging.yaml
├── deployment/
│   ├── terraform/
│   └── README.md
├── notebooks/
│   ├── adk_app_testing.ipynb
│   └── evaluating_adk_agent.ipynb
├── tests/
│   ├── unit/
│   ├── integration/
│   └── load_test/
├── Dockerfile
├── Makefile
├── pyproject.toml
└── uv.lock
```

### Specialized Agents

- **Data Collector Agent:** Gathers structured data, stats, and benchmarks.
- **Role Identifier Agent:** Detects which expert roles are needed.
- **Prompt Generator Agent:** Crafts role-specific prompts.
- **Role Thought Collector Agent:** Aggregates evidence-based reasoning per role.
- **Fact Checker Agent:** Validates facts and references with web searches.
- **Iterative Refiner Agent:** Improves solution quality in multiple passes.
- **Visual Formatter Agent:** Presents results in actionable formats.

---

## 🛠️ Technology Stack

- **Backend/AI:** Google ADK, FastAPI, Vertex AI, Gemini 2.5 Flash, OpenTelemetry
- **Cloud/Infra:** Google Cloud Platform, Cloud Run, BigQuery, Terraform, Docker
- **Dev Tools:** uv, pytest, ruff, mypy, Jupyter

---

## 📋 Prerequisites

- Python 3.10+
- uv (Python package manager)
- Google Cloud SDK
- Terraform
- Docker (optional)
- make

---

## 🚀 Quick Start

### 1. Installation

```sh
git clone <repository-url>
cd agenthub
make install
```

### 2. Interactive Playground

```sh
make playground
```
Visit [http://localhost:8501](http://localhost:8501) to chat with the multi-agent system and monitor agent interactions.

### 3. Local API Server

```sh
make local-backend
```
API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🎯 Usage Example

**Problem Solving**

```python
problem = """
How can we reduce carbon emissions in urban transportation while maintaining economic viability and user satisfaction?
"""
```

**API Call**

```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "Design a sustainable supply chain for electric vehicle batteries",
        "session_id": "unique-session-id"
    }
)
solution = response.json()
```

---

## 🧪 Testing

```sh
make test      # Run all tests
make lint      # Lint, format, spell check, type check
```

---

## 🚀 Deployment

### Development (Cloud Run)

```sh
gcloud config set project YOUR_DEV_PROJECT_ID
make backend
```

### Production

- **Infra Setup:**  
  `uvx agent-starter-pack setup-cicd`
- **Manual Terraform:**  
  `make setup-dev-env`
- **Enable IAP (optional):**  
  `make backend IAP=true`

**Environment Variables:**

```sh
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_VERTEXAI=True
AGENT_ENGINE_SESSION_NAME=agenthub
ALLOW_ORIGINS=https://yourdomain.com,http://localhost:3000
```

---

## 📊 Monitoring

- **Logging/Tracing:** OpenTelemetry, Cloud Logging, Cloud Trace
- **Analytics:** BigQuery
- **Dashboards:** Use Looker Studio templates for agent metrics and system health

---

## 🔧 Configuration

**Agent Model:**  
Edit `app/agent.py` for agent settings.

**FastAPI Middleware:**  
Edit `app/server.py` to customize CORS, authentication, etc.

---

## 🔐 Security

- Google Cloud IAM and Identity-Aware Proxy for authentication
- API security via rate limiting and input validation
- Google Secret Manager for secrets

---

## 🤝 Collaborators

- **sriram.k@prodapt.com**
- **saketh.gv@prodapt.com**
- **ishwarya.ms@prodapt.com**
- **srisusharitha.k@prodapt.com**
- **youvashri.j@prodapt.com**

---

## 📚 Resources

- Google ADK Documentation
- Vertex AI Documentation
- Notebooks in `/notebooks/`
- [Google Cloud AI Community](https://cloud.google.com/community)
- [Agent Development Kit on GitHub](https://github.com/google/agent-development-kit)

---

## 🙏 Acknowledgments

Thanks to Google Cloud for the ADK, the open-source community, and all contributors.

**Built with 💡 by the AgentHub team**