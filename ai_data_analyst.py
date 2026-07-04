import tempfile
import csv
import streamlit as st
import pandas as pd
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckdb import DuckDbTools
from agno.tools.pandas import PandasTools

# Function to preprocess and save the uploaded file
def preprocess_and_save(file):
    try:
        # Read the uploaded file into a DataFrame
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, encoding='utf-8', na_values=['NA', 'N/A', 'missing'])
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file, na_values=['NA', 'N/A', 'missing'])
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None, None, None
        
        # Ensure string columns are properly quoted
        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].astype(str).replace({r'"': '""'}, regex=True)
        
        # Parse dates and numeric columns
        for col in df.columns:
            if 'date' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    # Keep as is if conversion fails
                    pass
        
        # Create a temporary file to save the preprocessed data
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_path = temp_file.name
            # Save the DataFrame to the temporary CSV file with quotes around string fields
            df.to_csv(temp_path, index=False, quoting=csv.QUOTE_ALL)
        
        return temp_path, df.columns.tolist(), df  # Return the DataFrame as well
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None, None, None

# Streamlit app
st.title("📊 Data Analyst Agent")

# Sidebar for API keys
with st.sidebar:
    st.header("API Keys")
    groq_key = st.text_input("Enter your Groq API key:", type="password")
    if groq_key:
        st.session_state.groq_key = groq_key
        st.success("API key saved!")
    else:
        st.warning("Please enter your Groq API key to proceed.")

# File upload widget
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None and "groq_key" in st.session_state:
    # Preprocess and save the uploaded file
    temp_path, columns, df = preprocess_and_save(uploaded_file)
    columns_str = "\n".join([f"- {c}" for c in columns])
    
    if temp_path and columns and df is not None:
        # Display the uploaded data as a table
        st.write("Uploaded Data:")
        st.dataframe(df)  # Use st.dataframe for an interactive table
        
        # Display the columns of the uploaded data
        st.write("Uploaded columns:", columns)
        st.subheader("📋 Dataset Information")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Rows", f"{len(df):,}")

        with col2:
            st.metric("Columns", len(df.columns))

        st.write("### Column Names")

        st.dataframe(
            pd.DataFrame({
                "Column": df.columns,
                "Data Type": df.dtypes.astype(str)
            }),
            use_container_width=True
        )

        st.write("### First 5 Rows")

        st.dataframe(df.head(), use_container_width=True)
        
        # Initialize DuckDbTools
        duckdb_tools = DuckDbTools()
        
        # Load the CSV file into DuckDB as a table
        duckdb_tools.load_local_csv_to_table(
            path=temp_path,
            table="uploaded_data",
        )
        
        # Initialize the Agent with DuckDB and Pandas tools
        data_analyst_agent = Agent(
            model=Groq(
                        id="llama-3.3-70b-versatile",
                        api_key=st.session_state.groq_key,
                    ),
            tools=[duckdb_tools, PandasTools()],
            system_message=f"""
            You are an expert data analyst specializing in SQL and business intelligence.

            The uploaded dataset has been loaded into a DuckDB table named:

            uploaded_data

            The available columns are:

            {columns_str}

            Rules:

            1. ONLY use the column names listed above.
            2. NEVER invent or guess column names.
            3. Always inspect the schema before writing SQL.
            4. Use DuckDB SQL syntax.
            5. If the requested information cannot be answered because a column doesn't exist, explain which required column is missing.
            6. Perform calculations whenever useful.
            7. Prefer SQL for aggregations and filtering.
            8. Use Pandas only if SQL is not sufficient.
            9. Explain your reasoning clearly.
            10. Give business insights whenever possible.

            Your answer should include:
            • Short explanation
            • SQL result
            • Business insights

            Examples:

            Vendor -> VendorName

            Money spent -> Dollars

            Purchase amount -> Dollars

            Units purchased -> Quantity

            Shipping -> Freight

            Purchase date -> PODate

            Invoice date -> InvoiceDate

            Payment date -> PayDate
            """,
            markdown=True,
        )
        
        # Initialize code storage in session state
        if "generated_code" not in st.session_state:
            st.session_state.generated_code = None
        
        # Main query input widget
        user_query = st.text_area("Ask a query about the data:")
        
        # Add info message about terminal output
        st.info("💡 Check your terminal for a clearer output of the agent's response")
        
        if st.button("Submit Query"):
            if user_query.strip() == "":
                st.warning("Please enter a query.")
            else:
                try:
                    # Show loading spinner while processing
                    with st.spinner('Processing your query...'):
                        # Get the response from the agent
                        enhanced_query = f"""
                                        The dataset contains these columns:

                                        {", ".join(columns)}

                                        User Question:
                                        {user_query}

                                        Remember:
                                        Use ONLY these exact column names.
                                        Do NOT invent new columns.
                                        """
                        response = data_analyst_agent.run(enhanced_query)

                        # Extract the content from the response object
                        if hasattr(response, 'content'):
                            response_content = response.content
                        else:
                            response_content = str(response)

                    # Display the response in Streamlit
                    st.markdown(response_content)
                
                    
                except Exception as e:
                    st.error(f"Error generating response from the agent: {e}")
                    st.error("Please try rephrasing your query or check if the data format is correct.")