from flask import Flask, request, jsonify
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
from minio_config import minio_client, MINIO_BUCKET
import pandas as pd
from pandas_agent import pandas_agent
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

        For example:

        <question>How old is Jane?</question>
        <logic>Use `person_name_search` since you can use the query `Jane`</logic>
        <question>Who has id 320</question>
        <logic>Use `python_repl` since even though the question is about a person, you don't know their name so you can't include it.</logic>
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