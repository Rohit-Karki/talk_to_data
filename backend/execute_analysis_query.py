from flask import Flask, request, jsonify
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
from configs.minio_config import minio_client, MINIO_BUCKET
import pandas as pd
from agents.pandas_agent import pandas_agent
import io

def execute_analysis_query(filename: str, query: str):
    """Execute Analysis query."""

    try:
        # Get the file from MinIO        
        response = minio_client.get_object(MINIO_BUCKET, filename)
        
        # Read the CSV data into a BytesIO buffer
        csv_data = io.BytesIO(response.read())
        print("CSV data loaded into buffer")
        
        # Try reading with different parameters
        try:
            df = pd.read_csv(csv_data, sep=',')
        except:
            csv_data.seek(0)
            try:
                df = pd.read_csv(csv_data, sep=';')
            except:
                csv_data.seek(0)
                df = pd.read_csv(csv_data, sep=None, engine='python')
        
        # Define your prompt template
        TEMPLATE = """You are working with a pandas dataframe in Python. The name of the dataframe is `df`.
        It is important to understand the attributes of the dataframe before working with it. This is the result of running `df.head().to_markdown()`

        <df>
        {dhead}
        </df>

        You are not meant to use only these rows to answer questions - they are meant as a way of telling you about the shape and schema of the dataframe.
        You also do not have use only the information here to answer questions - you can run intermediate queries to do exploratory data analysis to give you more information as needed.

        When answering questions, follow these steps:
        1. First, analyze the question and break it down into smaller parts
        2. Think about what data you need to answer each part
        3. Plan your approach and what pandas operations you'll need
        4. Execute your plan step by step
        5. Verify your results make sense
        6. Provide a clear explanation of your findings

        For each step, explain your reasoning before taking action. This helps ensure accurate and well-thought-out answers.

        For example:

        <question>How old is Jane?</question>
        <logic>
        1. First, I need to find Jane's record in the dataframe
        2. I should use `person_name_search` since we have the name "Jane"
        3. After finding Jane's record, I'll extract her age
        4. I'll verify the age is within reasonable bounds
        5. Finally, I'll explain how I found this information
        </logic>

        <question>Who has id 320</question>
        <logic>
        1. We need to find a record with id 320
        2. Since we don't have a name to search with, we'll use `python_repl`
        3. We'll filter the dataframe for id 320
        4. We'll verify we found exactly one record
        5. We'll explain what information we found about this person
        </logic>

        Always provide a clear explanation of your findings and the reasoning behind your approach.
        """  # noqa: E501

        # Format the template with the dataframe's head
        template = TEMPLATE.format(dhead=df.head().to_markdown())

        # Create a ChatPromptTemplate
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", template),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
                ("human", query),
            ]
        )
        
        # Create pandas agent
        agent = pandas_agent(df)
        print("Agent created successfully")
        
        # Run the query
        result = agent.invoke(prompt)
        
        # Return only the serializable parts
        return {
            'output': result.get('output', ''),
            'message': 'Query processed successfully'
        }
    except Exception as e:
        print(f"Error processing CSV query: {str(e)}")
        return {'error': str(e)}