"""
Pre-built role templates with realistic job descriptions.
These load into the JD field when a user selects a role.
"""

ROLE_TEMPLATES = {
    "Data Analyst": """
**Position: Data Analyst**

We are looking for a detail-oriented Data Analyst to join our analytics team.

**Required Skills & Qualifications:**
- Proficiency in SQL (complex queries, window functions, CTEs)
- Strong experience with Python (Pandas, NumPy, Matplotlib, Seaborn)
- Experience with BI tools: Tableau or Power BI
- Statistical analysis and hypothesis testing
- Data cleaning and ETL pipeline experience
- Understanding of A/B testing methodology
- Experience with Excel/Google Sheets for reporting
- Familiarity with cloud data warehouses (BigQuery, Redshift, or Snowflake)
- Communication skills to present insights to non-technical stakeholders

**Nice to have:**
- Experience with dbt or Airflow
- Basic ML knowledge (scikit-learn)
- Experience with APIs and JSON data
""",

    "Frontend Engineer": """
**Position: Frontend Engineer (React)**

We're seeking a skilled Frontend Engineer to build exceptional user interfaces.

**Required Skills & Qualifications:**
- Expert-level JavaScript (ES6+, async/await, closures, prototypes)
- React.js — hooks, context API, component architecture, performance optimisation
- TypeScript — types, interfaces, generics
- CSS/SCSS — Flexbox, Grid, responsive design, CSS-in-JS
- REST API integration and state management (Redux, Zustand, or React Query)
- Testing: Jest, React Testing Library
- Git version control and code review practices
- Browser performance optimisation (Lighthouse, Core Web Vitals)
- Accessibility (WCAG 2.1)

**Nice to have:**
- Next.js / SSR experience
- GraphQL (Apollo Client)
- CI/CD pipelines
- Micro-frontend architecture
""",

    "AI/ML Engineer": """
**Position: Machine Learning Engineer**

Join our AI team to build and deploy production ML systems.

**Required Skills & Qualifications:**
- Python — expert level (OOP, decorators, async, type hints)
- Machine Learning fundamentals (supervised/unsupervised learning, regularisation, evaluation metrics)
- Deep Learning: PyTorch or TensorFlow — model building, training loops, debugging
- MLOps: model deployment, monitoring, versioning (MLflow, DVC)
- Large Language Models (LLMs): fine-tuning, prompt engineering, RAG architectures
- Vector databases (Pinecone, Chroma, Weaviate)
- FastAPI or Flask for model serving
- Docker and containerisation
- SQL and data pipeline basics
- Distributed computing (Spark or Dask) is a plus

**Nice to have:**
- Hugging Face ecosystem
- LangChain / LlamaIndex
- AWS/GCP/Azure ML services
""",

    "Backend Engineer": """
**Position: Backend Software Engineer (Python/Node)**

Building scalable, reliable APIs and backend systems.

**Required Skills & Qualifications:**
- Python (FastAPI, Django, or Flask) OR Node.js (Express, NestJS)
- RESTful API design and GraphQL
- Relational databases: PostgreSQL or MySQL — schema design, query optimisation, indexing
- NoSQL: MongoDB or Redis
- Microservices architecture and event-driven design
- Message queues: RabbitMQ or Kafka
- Docker and Kubernetes basics
- Authentication: JWT, OAuth2, session management
- Unit and integration testing
- Monitoring and observability (logging, tracing)

**Nice to have:**
- gRPC / Protocol Buffers
- Cloud platforms (AWS, GCP, Azure)
- CI/CD (GitHub Actions, Jenkins)
""",

    "DevOps/SRE Engineer": """
**Position: DevOps / Site Reliability Engineer**

Own the infrastructure and deployment pipeline for our platform.

**Required Skills & Qualifications:**
- Linux administration and shell scripting (Bash)
- Docker and Kubernetes — cluster management, Helm charts, autoscaling
- Infrastructure as Code: Terraform or Pulumi
- CI/CD pipelines: GitHub Actions, Jenkins, or GitLab CI
- Cloud platforms: AWS, GCP, or Azure (at least one — deep knowledge)
- Monitoring and alerting: Prometheus, Grafana, PagerDuty
- Log management: ELK stack or Datadog
- Networking: DNS, load balancers, VPNs, firewalls, TLS/SSL
- Security best practices: RBAC, secrets management (Vault), IAM
- Incident response and postmortem culture

**Nice to have:**
- Service mesh (Istio, Linkerd)
- Cost optimisation strategies
- FinOps knowledge
""",

    "Product Manager": """
**Position: Product Manager**

Drive product strategy and execution for our B2B SaaS platform.

**Required Skills & Qualifications:**
- Product discovery: user research, customer interviews, problem framing
- Product strategy: roadmap prioritisation, OKRs, business cases
- Agile methodologies: Scrum, Kanban, sprint planning, backlog grooming
- Data analysis: defining metrics, reading dashboards, A/B test interpretation
- Cross-functional collaboration with engineering, design, sales, marketing
- Writing PRDs, user stories, acceptance criteria
- Stakeholder management and executive communication
- UX/design thinking principles
- Understanding of technical concepts (APIs, databases, cloud infrastructure basics)

**Nice to have:**
- SQL for self-serve analytics
- Experience with enterprise/B2B SaaS
- Pricing and packaging strategy
- PLG (Product-Led Growth) experience
""",

    "Full Stack Engineer": """
**Position: Full Stack Engineer**

Building features end-to-end across our web platform.

**Required Skills & Qualifications:**
- Frontend: React.js / Next.js, TypeScript, Tailwind CSS
- Backend: Node.js (Express/NestJS) or Python (FastAPI/Django)
- Databases: PostgreSQL, Redis
- REST APIs and GraphQL
- Authentication and authorisation (JWT, OAuth2)
- Git, code review, CI/CD
- Docker for local development
- Testing: unit, integration, e2e (Cypress or Playwright)
- Performance optimisation (both frontend and backend)
- Agile development practices

**Nice to have:**
- Cloud deployment (AWS/Vercel/Railway)
- Message queues
- WebSockets / real-time features
""",
}
