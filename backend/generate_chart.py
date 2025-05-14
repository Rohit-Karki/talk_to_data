import io
import base64
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
from configs.minio_config import minio_client, MINIO_BUCKET
from agents.pandas_agent import pandas_agent
from llm import llm
from State import State
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
import plotly.graph_objects as go
import os
from chart_generation.models import AnalysisResult, CodeBlock, Explanation, Visualization
from chart_generation.markdown_parser import (
    extract_code_from_markdown,
    extract_code_explanation,
    extract_chart_explanation,
    extract_data_table
)
from chart_generation.chart_utils import (
    determine_chart_type,
    setup_plot_style,
    determine_code_type
)
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

# Define the data models
class DataTable(BaseModel):
    headers: List[str]
    data: List[Dict[str, Union[str, float, int]]]
    title: Optional[str] = None
    description: Optional[str] = None

def parse_llm_response(response_text: str) -> AnalysisResult:
    """Parse the LLM response into structured output using LangChain's PydanticOutputParser."""
    parser = PydanticOutputParser(pydantic_object=AnalysisResult)
    
    # Create a prompt template that includes format instructions
    prompt = PromptTemplate(
        template="""Analyze the following response and structure it according to the schema:
        {response_text}
        
        {format_instructions}
        """,
        input_variables=["response_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Parse the response using the LLM and parser
    formatted_prompt = prompt.format(response_text=response_text)
    response = llm.invoke(formatted_prompt)
    print(f"response: {response}")
    return parser.parse(response.content)

def generate_chart(filename: str, query: str) -> AnalysisResult:
    """Generate chart and analysis with structured output."""
    try:
        # Get the file from MinIO
        data = minio_client.get_object(MINIO_BUCKET, filename)
        df = pd.read_csv(data)
        
        # Create pandas agent
        agent = pandas_agent(df)
        
        # Define the prompt for chart generation
        prompt = """
        The dataset is ALREADY loaded into a DataFrame named 'df'. DO NOT load the data again.
        
        Create Python code that generates visualization(s) using matplotlib to address this query:
        {query}
        
        You are an experiencied data scientist
        Lets think step by step of why the next action has sense and if there is something to take in account
        
        At the first steps:
            1. Import libraries that you are going to use for data as pandas, numpy and matplotlib
            2. Check if the dataframe `df` exists and inspect its structure and content
            3. Remove non necessary columns
            4. Drop duplicate rows
            
        For intermediate steps during all iterations, use the following procedure:
            (1) First identify the possible solutions and possible blocks of the thought
            (2) If theres is Empty DataFrame, review your previous observation and see if you fail and where
            (3) If you are making new columns or operations, make sure the values you are going to use exists before using it
            
        Then check the following advices:
            1. Find the corresponding metrics, not necessarily the names is exactly equal as the human requested
            2. Check if is necessary to change format of table with pivot, groupby, melt, or other function over the table. When making this changes
            make sure the table is well processed
            3. When generating a new dataset return it to be observed, if necessary, print it
                    

        Use the following format:

        Question: the input question you must answer
        you should always think about what to do in as possible paths
        Thought1: thinks this as the first possibility path
        Thought2: thinks this as the second possibility path
        Thought: which is the best thougth to take action
        Action: python_repl_ast
        Action Input: the input to the action
        Observation: the result of the action
        Remember to maintain the format specifically think about Thougth1 and Thought2
        ... (this Thought1/Thought2/Action/Action Input/Observation can repeat N times)
        Final Thought: I now know the final answer and processed the data correctly
        Final Answer: the final answer to the original input question


        Requirements:
        1. Use ONLY matplotlib for plotting
        2. The code must be a SINGLE code block
        3. The code block must start and end with ```
        4. Use these colors for styling:
           - Background: #F0F0F0
           - Plot colors: #8f63ee, #ced5ce, #a27bf0
           - Text colors: #555555 for labels, #333333 for title
        
        5. Before plotting, handle data preprocessing in this order:
           a. For date columns:
              - Convert to datetime using pd.to_datetime(..., format='%d-%b-%y', errors='coerce')
              - Handle any date format issues
           b. For numeric columns:
              - First check if the column contains string values with commas
              - If yes, use str.replace(',', '') to remove commas
              - Then convert to numeric using pd.to_numeric(..., errors='coerce')
              - Finally, handle NaN values by filling with 0
        
        6. For the response, follow this EXACT structure:
           ```python
           # Data preprocessing
           [Your preprocessing code here]

           # Create figure with subplots if multiple charts are needed
           fig = plt.figure(figsize=(10, 6))  # Always create a figure object
           [Your plotting code here]

           # DO NOT call plt.savefig or plt.close() - the backend will handle this
           # Just create the plot and the backend will capture it

           # Create data table
           table_data = df[['relevant', 'columns']].head().to_dict('records')
           ```
        
        7. After the code block, provide:
           a. Code Explanation:
              - Explain what each part of the code does
              - Why certain preprocessing steps were taken
              - Why specific plot types were chosen

           b. Chart Explanation:
              - Explain what each chart shows
              - Highlight key insights and patterns
              - Point out any notable trends or outliers

           c. Data Table:
              Format your data table in markdown like this:
              | Column1 | Column2 | Column3 |
              |---------|---------|---------|
              | value1  | value2  | value3  |
              | value4  | value5  | value6  |
              
              Make sure to:
              - Include relevant columns that support your analysis
              - Format numbers appropriately
              - Include a title and description of what the table shows
              - Keep the table concise but informative
        
        8. For multiple charts:
           - Use matplotlibs's subplots when appropriate
           - Ensure consistent styling across all charts
           - Provide separate explanations for each chart
           - Include a summary of how the charts relate to each other
        
        Begin!
        """
        
        # Get the response from the agent
        response = agent.invoke({"input": prompt.format(query=query)})
        
        # Parse the response into structured format
        analysis_result = parse_llm_response(response['output'])
        print(f"analysis_result: {analysis_result}")
        
        print(f"code blocks are {analysis_result.code_blocks}")
        # Execute code blocks and update visualizations
        for code_block in analysis_result.code_blocks:
            if code_block.type == 'visualization':
                local_vars = {'df': df, 'plt': plt, 'mdates': mdates, 'np': np}
                
                try:
                    # Execute the code
                    exec(code_block.code, globals(), local_vars)
                    
                    # Get the current figure
                    fig = plt.gcf()
                    print(f"fig: {fig}")
                    if fig and fig.get_size_inches().prod() > 0:  # Check if figure has content
                        # Save to buffer
                        buf = io.BytesIO()
                        fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
                        buf.seek(0)
                        
                        # Convert to base64
                        img_str = base64.b64encode(buf.read()).decode('utf-8')
                        print(f"Created base64 image, length: {len(img_str)}")
                        
                        # Get the chart explanation
                        chart_explanation = next((exp.text for exp in analysis_result.explanations 
                                          if exp.type == 'chart'), "")
                        
                        # Add to visualizations
                        analysis_result.visualizations.append(Visualization(
                            type=determine_chart_type(query),
                            title="Visualization",
                            description=chart_explanation,
                            data={'image': img_str},
                            config={'format': 'png'}
                        ))
                        print(f"Added visualization to result")
                        
                except Exception as e:
                    print(f"Error executing visualization code: {str(e)}")
                finally:
                    # Close any open figures
                    plt.close('all')
        
        # Update metadata
        analysis_result.metadata = {
            'columns': df.columns.tolist(),
            'shape': df.shape
        }
        
        print(f"Final analysis_result.visualizations: {analysis_result.visualizations}")
        return analysis_result
        
    except Exception as e:
        raise Exception(f"Error generating analysis: {str(e)}")

def determine_code_type(code: str) -> str:
    """
    Determine the type of code block based on its content.
    """
    code = code.lower()
    
    if 'plot' in code or 'chart' in code or 'figure' in code:
        return 'visualization'
    elif 'describe' in code or 'info' in code or 'value_counts' in code:
        return 'eda'
    elif 'corr' in code or 'correlation' in code:
        return 'correlation'
    elif 'groupby' in code or 'aggregate' in code:
        return 'aggregation'
    elif 'fillna' in code or 'dropna' in code:
        return 'data_cleaning'
    else:
        return 'general'