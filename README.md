# Talk to Data: LLM-Based Dashboards and Reports from Data Lakehouse

## 1.Problem Statement:

The current process of generating dashboards and reports from data warehouses often involves complex ETL pipelines, predefined metrics, and limited user interaction. Business users frequently lack the ability to explore data dynamically, ask ad-hoc questions, and gain immediate insights from the vast amounts of data stored in the data lakehouse. This results in delays in accessing critical information, reliance on technical teams for even simple data exploration, and a potential disconnect between data insights and timely decision-making.

## 2.What is Talk to Data about?

This research focuses on leveraging Large Language Models (LLMs) to revolutionize the creation and consumption of dashboards and reports directly from a data lakehouse. It explores methods for enabling natural language interaction with data, allowing users to ask questions, request specific visualizations, and generate reports in an intuitive and conversational manner. The research will investigate consuming data both directly from raw tables and from pre-aggregated intermediate tables within the data warehouse to optimize for performance and flexibility. The context of Customer Data Platform (CDP) and customer 360, with a focus on customer segmentation and personalization, will serve as the application domain for this research.

## 3.Objective of Talk to Data:

Moving forward with this topic holds significant potential for several reasons:
    • Enhanced User Empowerment: LLM-powered interfaces can democratize data access, enabling business users without deep technical skills to directly interact with and extract insights from the data lakehouse.
    • Increased Efficiency and Speed: Automating the dashboard and report generation process through natural language queries can significantly reduce the time and effort required compared to traditional methods.
    • Improved Data Exploration and Discovery: LLMs can facilitate more flexible and exploratory data analysis, allowing users to ask nuanced questions and uncover hidden patterns that might be missed with predefined reports.
    • Personalized Insights for CDP and Customer 360: Applying this technology to CDP and customer 360 data can unlock deeper understanding of customer segments, preferences, and behaviors, leading to more effective personalization strategies.
    • Real-time and Ad-hoc Analysis: LLMs can enable users to ask real-time questions and generate on-demand reports, facilitating quicker responses to changing business needs and opportunities.
    • Potential for Innovation: This research can pave the way for novel ways of visualizing and interacting with data, going beyond traditional dashboard and report formats.

## 4.Expected outcomes from the research:

The research is expected to deliver the following outcomes:
    • A framework for building LLM-powered dashboards and reports: This will include architectural considerations, data access strategies (direct vs. intermediate tables), fine tuning, and integration points with the data lakehouse.
    • Sample implementations of approximately 50 dashboard tiles and 50 report elements: These samples will demonstrate the feasibility and capabilities of generating various visualizations and data summaries using natural language queries, covering common metrics and dimensions relevant to CDP and customer 360.
    • Evaluation of different LLM models and prompting techniques: The research will assess the performance, accuracy, and usability of various LLMs in the context of data interaction.
    • Performance analysis of querying raw vs. intermediate tables: The research will evaluate the trade-offs between flexibility and performance when consuming data from different layers of the data warehouse.
    • Insights into the potential impact of LLM-based data exploration on customer segmentation and personalization strategies: The research will explore how this technology can lead to more granular and actionable customer insights.
    • Identification of potential challenges and limitations: The research will also highlight any obstacles encountered and suggest future research directions.

## Project StructureBackend Project
# Talk to Data Project Description

## 1. Backend Project
### Technology Stack
- **Primary Language**: Python
- **Key Components**:
  - Flask API
  - SQL Database (SQLite with Chinook.db)
  - Data Analysis Tools (pandas, chart generation)
  - LLM Integration
  - MinIO Storage Integration

### Purpose
Serves as the main backend service handling data analysis, SQL queries, and chart generation. It includes features for data processing, analysis, and visualization.

## 2. Frontend Project
### Technology Stack
- **Primary Framework**: SvelteKit
- **Additional Technologies**:
  - TypeScript
  - Vite (Build tool)
  - Storybook (Component documentation)

### Purpose
Main user interface for interacting with the data analysis features. Built with modern web technologies focusing on performance and developer experience.

## 3. Finance Adviser Project
### Technology Stack
- **Primary Framework**: SvelteKit
- **Additional Technologies**:
  - TypeScript
  - Tailwind CSS
  - Vite

### Purpose
A specialized frontend application focused on financial advice and analysis, providing a dedicated interface for financial data visualization and recommendations.

## 4. Infrastructure
### Technology Stack
- Docker
- Containerized Deployment

### Purpose
Manages the deployment and orchestration of all services, ensuring consistent development and production environments.
