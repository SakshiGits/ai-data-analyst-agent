# Demo
https://github.com/user-attachments/assets/c1a59c64-2eae-4362-b31e-76c158f963bb

# 📊 AI Data Analysis Agent

An AI data analysis Agent built using the Agno Agent framework and groq's model. This agent helps users analyze their data - csv, excel files through natural language queries, powered by Groq's language models and DuckDB for efficient data processing - making data analysis accessible to users regardless of their SQL expertise.

## Features

- 📤 **File Upload Support**: 
  - Upload CSV and Excel files
  - Automatic data type detection and schema inference
  - Support for multiple file formats

- 💬 **Natural Language Queries**: 
  - Convert natural language questions into SQL queries
  - Get instant answers about your data
  - No SQL knowledge required

- 🔍 **Advanced Analysis**:
  - Perform complex data aggregations
  - Filter and sort data
  - Generate statistical summaries
  - Create data visualizations

- 🎯 **Interactive UI**:
  - User-friendly Streamlit interface
  - Real-time query processing
  - Clear result presentation

## How to Run

1. **Setup Environment**
   ```bash
   # Clone the repository
   git clone https://github.com/SakshiGits/ai-data-analyst-agent.git

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   streamlit run ai_data_analyst.py
   ```

## Usage

1. Launch the application using the command above
2. Upload your CSV or Excel file through the Streamlit interface
3. Ask questions about your data in natural language
4. View the results and generated visualizations

Note: The side navigation bar is not responsive for now, I am planning to add functionality to it soon. Feel free to raise a PR if you have ideas.
