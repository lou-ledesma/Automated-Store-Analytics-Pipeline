# Automated Store Analytics Pipeline

A production-grade data orchestration system that automates the ingestion, transformation, and analysis of retail transaction data through Apache Airflow. Demonstrates end-to-end ETL automation with containerized infrastructure, data quality validation, and scheduled report generation.

---

## Overview

This project showcases a complete data pipeline architecture: raw data ingestion → automated cleaning → warehouse loading → analytical queries → stakeholder reporting. Built with Apache Airflow for orchestration, Docker for infrastructure consistency, and MySQL for data persistence, the system eliminates manual data processing and enables reliable, scheduled analytics delivery.

### Key Capabilities

- **Orchestrated ETL**: Airflow DAG-driven workflow with automated task dependencies and error handling
- **Data Quality**: Python-based data cleaning and validation before warehouse ingestion
- **Infrastructure as Code**: Docker containerization for reproducible, environment-agnostic deployment
- **Scheduled Analytics**: Automated report generation and email distribution on defined schedules
- **Data Warehousing**: Normalized MySQL schema with optimized queries for business reporting

---

## Technical Architecture

### System Components

#### 1. **Workflow Orchestration** (`airflow_dag/Store_DAG.py`)

The core orchestration engine defining the entire data pipeline:

- **DAG Definition**: Acyclic directed graph specifying task dependencies, scheduling, and retry logic
- **Task Design**:
  - Data extraction from source files
  - Invocation of data cleaning operations
  - Database operations (table creation, data loading, transformations)
  - Analytical query execution and report generation
  - Email notification with results
- **Scheduling**: Automated execution on defined intervals (daily, weekly, or custom schedules)
- **Monitoring**: Airflow UI integration for real-time task status, logs, and failure alerts
- **Idempotency & Atomicity**: Designed to handle re-runs without data duplication or inconsistency

**Technical Stack**: Python, Apache Airflow, DAG composition patterns

---

#### 2. **Infrastructure Configuration** (`docker_configs/docker-compose-LocalExecutor.yml`)

Container orchestration and service definition:

- **Airflow Services**: Web server, scheduler, and executor configured for LocalExecutor
- **MySQL Integration**: Database service configuration and networking
- **Volume Mounts**: Persistent storage for DAG files, logs, and configurations
- **Environment Variables**: Secret management and service parameterization
- **Network Isolation**: Internal service communication with proper port exposure

**Deployment**: Single `docker-compose up` command brings entire stack online

**Use Case**: Eliminates environment drift; ensures consistent behavior across development, testing, and production

---

#### 3. **Data Cleaning & Validation** (`python_script/datacleaner.py`)

Python module implementing data quality and transformation logic:

- **Input Validation**: Schema verification, required field checking
- **Data Cleaning Operations**:
  - Type casting and format standardization
  - Handling missing/null values (imputation, deletion, or flagging)
  - Outlier detection and remediation
  - Duplicate record identification and removal
  - Text normalization (trimming, case standardization, encoding)
- **Business Logic Validation**: Domain-specific constraints (e.g., positive transaction amounts, valid dates)
- **Quality Metrics**: Logging of records rejected, transformed, and loaded for audit trails
- **Error Handling**: Graceful failure with detailed logging for troubleshooting

**Integration**: Imported and executed within Airflow DAG as a Python operator

---

#### 4. **Database & Analytics** (`sql_files/`)

Modular SQL scripts organized by function:

**`mysql.cnf`** - Database connectivity configuration
- Connection parameters (host, port, credentials)
- Character set and timezone specifications
- Connection pooling settings

**`create_table.sql`** - Schema definition
- Table structure for cleaned transaction data
- Column definitions with appropriate types and constraints
- Primary keys and indexes for query optimization
- Comment documentation for downstream analytics teams

**`adjust_date.sql`** - Temporal data transformation
- Date parsing and standardization
- Timezone conversion if applicable
- Fiscal period calculation or date bucketing
- Handles date format inconsistencies in raw data

**`insert_into_table.sql`** - Data loading operation
- Bulk insert of cleaned records into warehouse
- Error handling for constraint violations
- Transaction management for data consistency

**`select_from_table.sql`** - Analytical reporting queries
- Aggregations by store, product category, time period
- Key metrics (sales, transactions, customer counts)
- Formatted output for email distribution or dashboard ingestion

---

#### 5. **Raw Data Source** (`store_files/raw_store_transactions.csv`)

Input dataset containing retail transaction records:

- **Schema**: Transaction ID, Store ID, Product Category, Amount, Quantity, Transaction Date, Payment Method, Customer ID
- **Grain**: Individual transaction-level records
- **Volume**: Complete transaction history for configured stores

**Data Quality Considerations**: This raw data is expected to contain inconsistencies (missing values, format variations, duplicates) that the `datacleaner.py` module remedies before warehouse loading.

---

## Data Flow & Pipeline Logic

```
Raw Data (CSV)
    ↓
[Extract Task] - Read raw_store_transactions.csv
    ↓
[Clean Task] - datacleaner.py validates, transforms, and standardizes records
    ↓
[Create Schema Task] - create_table.sql establishes warehouse structure
    ↓
[Adjust Data Task] - adjust_date.sql handles temporal transformations
    ↓
[Load Task] - insert_into_table.sql populates warehouse
    ↓
[Query Task] - select_from_table.sql generates analytical results
    ↓
[Notify Task] - Email reports to stakeholders
```

**Key Design Principle**: Each task is independent and rerunnable. Failed tasks can be retried without affecting the entire pipeline.

---

## Deployment & Execution

### Prerequisites

- Docker & Docker Compose installed
- Git repository cloned locally
- Sufficient disk space for MySQL database and Airflow metadata

### Quick Start

1. **Navigate to project root**:
   ```bash
   cd Automated-Store-Analytics-Pipeline
   ```

2. **Start services**:
   ```bash
   docker-compose -f docker_configs/docker-compose-LocalExecutor.yml up -d
   ```

3. **Access Airflow UI**:
   - Open `http://localhost:8080` in browser
   - Default credentials: airflow / airflow

4. **Trigger DAG**:
   - Navigate to DAGs section
   - Enable `Store_DAG`
   - Click "Trigger DAG" or wait for scheduled execution

5. **Monitor Execution**:
   - View task logs in Airflow UI
   - Check email for generated reports

### Configuration Adjustments

- **Schedule Frequency**: Modify `schedule_interval` in `Store_DAG.py` (e.g., `@daily`, `@weekly`, `0 9 * * MON` for 9 AM Mondays)
- **Email Recipients**: Update email configuration in DAG definition
- **Database Credentials**: Modify `mysql.cnf` or use environment variables
- **Data Source Path**: Update file path in extract task to point to actual data location

---

## Technical Decisions & Best Practices

### Why Airflow?

- **Orchestration**: Complex multi-step workflows with conditional branching and retries
- **Visibility**: Centralized monitoring and logging across all pipeline tasks
- **Reliability**: Built-in handling for failure recovery and idempotent re-execution
- **Scalability**: Executor options (LocalExecutor for single-machine, Celery for distributed)

### Data Quality Strategy

- **Separation of Concerns**: Cleaning logic isolated in dedicated Python module, reusable across contexts
- **Fail-Fast Validation**: Quality checks early in pipeline prevent downstream errors
- **Audit Trail**: Logging of rejected/transformed records for compliance and troubleshooting
- **Idempotency**: Data cleaning produces consistent output regardless of execution count

### Infrastructure Design

- **Containerization**: Docker eliminates "works on my machine" problems; ensures reproducibility
- **LocalExecutor**: Sufficient for single-machine deployments; can scale to Celery executor for distributed systems
- **Persistent Volumes**: Database and Airflow metadata survive container restarts
- **Network Isolation**: Services communicate via defined network; reduces external dependencies

### SQL Organization

- **Modular Scripts**: Each SQL file addresses single responsibility (schema, loading, reporting)
- **Parameterization**: Scripts designed to accept variables for flexibility across environments
- **Index Strategy**: Indexes on date and ID columns optimize analytical queries
- **Comments**: Documentation for non-obvious business logic or transformations

---

## Monitoring & Troubleshooting

### Airflow UI Indicators

- **Green tasks**: Successfully completed
- **Red tasks**: Failed execution; click to view detailed logs
- **Yellow tasks**: Currently running
- **Gray tasks**: Not yet executed

### Common Issues & Resolution

| Issue | Cause | Resolution |
|---|---|---|
| **Task timeout** | Long-running operations or data volume | Adjust timeout in DAG; optimize SQL queries |
| **Database connection errors** | Incorrect credentials or network isolation | Verify `mysql.cnf`; check Docker network settings |
| **Email delivery failed** | SMTP configuration incorrect | Configure email settings in Airflow web UI |
| **Data quality rejections** | Unexpected format in raw data | Review rejection logs in `datacleaner.py` output |

### Logs & Debugging

- **Airflow Logs**: Available in Airflow UI (Logs tab on task instance)
- **Container Logs**: `docker-compose logs -f airflow-scheduler` or `airflow-webserver`
- **Database Logs**: MySQL query logs available in container (configure as needed)

---

## Extensions & Future Enhancements

- **Data Validation Framework**: Implement Great Expectations for declarative data quality checks
- **Incremental Loading**: Partition data by date; load only new records (delta) rather than full refresh
- **BI Integration**: Connect to Tableau, Power BI, or Looker for dashboard automation
- **Alerting**: Threshold-based alerts (e.g., sales anomalies) triggered by query results
- **Distributed Execution**: Migrate to Celery executor for parallel task execution across multiple machines
- **Data Lineage**: Integrate OpenLineage for end-to-end data provenance and dependency mapping

---

## Project Structure

```
Automated-Store-Analytics-Pipeline/
│
├── airflow_dag/
│   └── Store_DAG.py
│
├── docker_configs/
│   └── docker-compose-LocalExecutor.yml
│
├── python_script/
│   └── datacleaner.py
│
├── sql_files/
│   ├── mysql.cnf
│   ├── create_table.sql
│   ├── adjust_date.sql
│   ├── insert_into_table.sql
│   └── select_from_table.sql
│
├── store_files/
│   └── raw_store_transactions.csv
│
└── README.md
```

---

## Tools & Dependencies

| Component | Purpose | Version |
|---|---|---|
| **Apache Airflow** | Workflow orchestration and scheduling | 2.x+ |
| **Python** | DAG and data cleaning scripting | 3.8+ |
| **Docker & Docker Compose** | Containerization and service orchestration | Latest |
| **MySQL** | Relational data warehouse | 5.7+ or 8.0+ |
| **Pandas** | Data manipulation in cleaning module | Latest |
| **SQLAlchemy** | ORM and database connectivity | Latest |

---

## Author

**Lou Ledesma** | Analytics Engineer | https://www.linkedin.com/in/loubriel-ledesma/

Specialized in data orchestration, ETL pipeline design, and building scalable data infrastructure. This project demonstrates proficiency in workflow automation, containerized deployment, data quality engineering, and production systems design.

---

## License

This project is provided as-is for educational and reference purposes.

---

## Notes

- **Data Privacy**: Ensure sensitive information (credentials, PII) is managed via environment variables, not committed to version control
- **Production Readiness**: For production deployments, implement secrets management (AWS Secrets Manager, HashiCorp Vault), upgrade to Celery executor, and implement comprehensive monitoring
- **Backups**: Configure regular database backups; store configuration files in version-controlled repositories

---

## Disclaimers

1. This project is for educational and analytical purposes. Sports betting involves financial risk. Users should conduct their own analysis and adhere to applicable gambling regulations in their jurisdiction.
2. README.md file description was generated using Perplexity AI.
