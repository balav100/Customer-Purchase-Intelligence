# Customer Purchase Intelligence

An end-to-end retail analytics project built with Python, PostgreSQL, SQL, RFM analysis, K-Means clustering, and Streamlit.

The project takes transactional retail data from data validation and exploratory analysis through database-backed analytics and an interactive dashboard.

## Project Overview

The workflow follows:

**Data → Validation → EDA → PostgreSQL → SQL Analytics → RFM → K-Means → Streamlit**

The project focuses on understanding:

- Customer purchasing behavior
- Revenue and order trends
- Product performance
- Geographic performance
- Customer value
- Customer segmentation
- Customer retention and cohort behavior

## Dataset

The final PostgreSQL table contains:

| Metric | Value |
|---|---:|
| Transactions | 392,692 |
| Customers | 4,338 |
| Orders / Invoices | 18,532 |
| PostgreSQL Table Size | 47 MB |
| First Transaction | 2010-12-01 |
| Last Transaction | 2011-12-09 |

**Table:** `retail_transactions`

## Data Validation

The dataset was validated before analysis.

Checks included:

- Transaction count
- Customer count
- Invoice count
- Date range
- NULL values
- Negative quantities
- Non-positive prices
- Transaction-level anomalies

### Validation Results

| Check | Result |
|---|---:|
| NULL customer IDs | 0 |
| NULL invoice numbers | 0 |
| NULL stock codes | 0 |
| NULL invoice dates | 0 |
| NULL quantities | 0 |
| NULL unit prices | 0 |
| Negative quantities | 0 |
| Zero-price transactions | 4 |

The four zero-price transactions were retained because they contain valid transaction information and contribute zero revenue.

## Exploratory Data Analysis

EDA was performed to understand the structure and behavior of the transaction data before moving the analytical workload into PostgreSQL.

The analysis covers:

- Revenue trends
- Order volume
- Customer activity
- Monthly activity
- Product performance
- Geographic distribution
- Transaction patterns
- Customer purchasing behavior

## PostgreSQL Analytics

The cleaned data was loaded into PostgreSQL and used as the analytical layer of the application.

The project contains **10 SQL analytical queries** covering the main business questions used by the dashboard.

The queries analyze areas including:

- Revenue
- Orders
- Customers
- Products
- Geographic performance
- Monthly performance
- Customer behavior
- Business performance metrics

The dashboard retrieves analytical results from PostgreSQL rather than relying on hardcoded values.

## Database Indexing

Indexes were created on frequently filtered columns.

```sql
CREATE INDEX idx_retail_invoice_date
ON retail_transactions(invoice_date);

CREATE INDEX idx_retail_customer_id
ON retail_transactions(customer_id);

CREATE INDEX idx_retail_country
ON retail_transactions(country);

CREATE INDEX idx_retail_stock_code
ON retail_transactions(stock_code);
```

Index usage was verified with `EXPLAIN ANALYZE`.

### Performance Results

| Test | Index | Execution Time |
|---|---|---:|
| Invoice date | `idx_retail_invoice_date` | 143.485 ms |
| Customer ID | `idx_retail_customer_id` | 1.487 ms |
| Country | `idx_retail_country` | 225.277 ms |
| Stock code | `idx_retail_stock_code` | 2.803 ms |

All four tested queries used index-only scans and reported:

```text
Heap Fetches: 0
```

## RFM Customer Analysis

Customer purchasing behavior is analyzed using RFM:

- **Recency** — how recently a customer purchased
- **Frequency** — how frequently a customer purchased
- **Monetary** — how much a customer spent

The process is:

```text
Transactions
     ↓
Customer Aggregation
     ↓
Recency / Frequency / Monetary
     ↓
RFM Features
```

## K-Means Customer Segmentation

K-Means clustering is applied to the RFM features to group customers with similar purchasing behavior.

```text
Customer Transactions
        ↓
RFM Calculation
        ↓
Feature Preparation
        ↓
K-Means Clustering
        ↓
Customer Segments
        ↓
Dashboard
```

The resulting segments are used in the dashboard to compare customer behavior and value.

## Streamlit Dashboard

The final application is built with Streamlit and connected to PostgreSQL.

### Executive Overview

High-level business KPIs and performance trends.

### Customer Intelligence

Customer activity, purchasing behavior, and customer value.

### Product Performance

Product-level transaction and performance analysis.

### Geographic Analysis

Sales and customer activity across countries.

### RFM Analysis

Customer value and segmentation analysis.

### Cohort Analysis

Customer purchasing and retention behavior over time.

### Interactive Filters

Users can filter and explore the underlying data through the dashboard.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application and data analysis |
| Pandas | Data manipulation |
| NumPy | Numerical operations |
| PostgreSQL | Database and SQL analytics |
| Psycopg2 | PostgreSQL connectivity |
| Scikit-learn | K-Means clustering |
| Streamlit | Interactive dashboard |
| Plotly | Interactive visualizations |
| Matplotlib | Exploratory visualization |
| Seaborn | Exploratory visualization |
| Jupyter Notebook | Data inspection and EDA |

## Project Structure

```text
Customer-Purchase-Intelligence/
│
├── app/
│   └── app.py
│
├── sql/
│   ├── 01_...
│   ├── 02_...
│   ├── 03_...
│   ├── 04_...
│   ├── 05_...
│   ├── 06_...
│   ├── 07_...
│   ├── 08_...
│   ├── 09_...
│   └── 10_...
│
├── notebooks/
│   ├── 01_dataset_inspection.ipynb
│   └── 02_eda.ipynb
│
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

### Clone the Repository

```bash
git clone https://github.com/<your-username>/Customer-Purchase-Intelligence.git
cd Customer-Purchase-Intelligence
```

### Create a Virtual Environment

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### Install Dependencies

```powershell
pip install -r requirements.txt
```

### Configure PostgreSQL

Create a PostgreSQL database and load the `retail_transactions` table.

Store database credentials using environment variables.

Example:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

Do not commit `.env` to GitHub.

### Run the Dashboard

```powershell
python -m streamlit run app/app.py
```

## Testing

The project was validated across the data, database, and application layers.

### Data Validation

- Transaction count
- Customer count
- Invoice count
- Date range
- NULL checks
- Quantity validation
- Price validation

### SQL Testing

All **10 analytical SQL queries** were executed successfully in PostgreSQL.

### Database Performance Testing

The four analytical indexes were tested using `EXPLAIN ANALYZE`.

### Dashboard Testing

The Streamlit application was tested across:

- Executive Overview
- Customer Intelligence
- Product Performance
- Geographic Analysis
- RFM Analysis
- Cohort Analysis
- Interactive filters
- Reset functionality

## Limitations

- The analysis is based on historical transaction data.
- Customer segmentation depends on the transaction history available for each customer.
- K-Means results depend on the selected RFM features and preprocessing.
- The dashboard reflects the data available in the PostgreSQL database.
- The project is intended as an analytics portfolio project rather than a production-scale retail platform.

## Future Improvements

- Cloud-hosted PostgreSQL
- Streamlit deployment
- Automated data ingestion
- Scheduled database refreshes
- Automated data-quality testing
- Customer-level drill-down
- Model monitoring
- Automated RFM refresh
- Customer segment tracking over time

## Author

**Balasubramaniam V**

An end-to-end data analytics project combining Python, SQL, PostgreSQL, machine learning, and interactive dashboard development.
