import io
import base64
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from minio_config import minio_client, MINIO_BUCKET
from pandas_agent import pandas_agent
from llm import llm
from State import State
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
import plotly.graph_objects as go
import os

# Define the data models
class CodeBlock(BaseModel):
    code: str
    type: str = Field(..., description="Type of code block (visualization, eda, correlation, etc.)")
    language: str = "python"

class Explanation(BaseModel):
    text: str
    type: str = Field(..., description="Type of explanation (code, chart, data)")
    section: Optional[str] = None

class DataTable(BaseModel):
    headers: List[str]
    data: List[Dict[str, Union[str, float, int]]]
    title: Optional[str] = None
    description: Optional[str] = None

class Visualization(BaseModel):
    type: str = Field(..., description="Type of visualization (line, bar, scatter, etc.)")
    title: str
    description: str
    data: Dict[str, Union[str, float, int]]
    config: Optional[Dict] = None

class AnalysisResult(BaseModel):
    code_blocks: List[CodeBlock]
    explanations: List[Explanation]
    data_tables: List[DataTable]
    visualizations: List[Visualization]
    metadata: Dict[str, Union[List[str], tuple]]
    timestamp: datetime = Field(default_factory=datetime.now)

def extract_data_table(md_text: str) -> List[DataTable]:
    """
    Extract data tables from markdown text.
    
    Args:
        md_text (str): Markdown text containing the data table
        
    Returns:
        List[DataTable]: List of extracted data tables
    """
    # Look for text between Data Table: and the next section
    matches = re.findall(r"Data Table:\s*(.*?)(?=Code Explanation:|Chart Explanation:|$)", 
                        md_text, re.DOTALL | re.IGNORECASE)
    
    if not matches:
        return []
    
    tables = []
    for match in matches:
        # Clean up the extracted text
        table_text = match.strip()
        # Remove any remaining markdown code block markers
        table_text = re.sub(r'```.*?```', '', table_text, flags=re.DOTALL)
        
        # Try to parse the table data
        try:
            # Split into lines and remove empty lines
            lines = [line.strip() for line in table_text.split('\n') if line.strip()]
            if len(lines) < 2:  # Need at least header and one row
                continue
                
            # First line is headers
            headers = [h.strip() for h in lines[0].split('|') if h.strip()]
            if not headers:
                continue
                
            # Parse data rows
            data = []
            for line in lines[1:]:
                row = [cell.strip() for cell in line.split('|') if cell.strip()]
                if len(row) == len(headers):
                    # Convert string values to appropriate types
                    processed_row = {}
                    for header, value in zip(headers, row):
                        try:
                            # Try to convert to number if possible
                            if '.' in value:
                                processed_row[header] = float(value)
                            else:
                                processed_row[header] = int(value)
                        except ValueError:
                            processed_row[header] = value
                    data.append(processed_row)
            
            if data:
                tables.append(DataTable(
                    headers=headers,
                    data=data,
                    title="Analysis Data Table",
                    description="Data used in the analysis"
                ))
        except Exception as e:
            print(f"Error parsing table: {str(e)}")
            continue
    
    return tables

def parse_llm_response(response_text: str) -> AnalysisResult:
    """
    Parse the LLM response into structured output using Pydantic models.
    """
    # Initialize lists for different components
    code_blocks = []
    explanations = []
    data_tables = []
    visualizations = []
    
    # Extract code blocks
    code = extract_code_from_markdown(response_text)
    code_blocks.append(CodeBlock(
        code=code,
        type=determine_code_type(code)
    ))
    
    # Extract explanations
    code_explanation = extract_code_explanation(response_text)
    if code_explanation:
        explanations.append(Explanation(
            text=code_explanation,
            type="code"
        ))
    
    chart_explanation = extract_chart_explanation(response_text)
    if chart_explanation:
        explanations.append(Explanation(
            text=chart_explanation,
            type="chart"
        ))
    
    # Extract data tables
    data_tables = extract_data_table(response_text)
    
    return AnalysisResult(
        code_blocks=code_blocks,
        explanations=explanations,
        data_tables=data_tables,
        visualizations=visualizations,
        metadata={}
    )

def extract_chart_explanation(md_text: str) -> str:
    """
    Extract chart explanation from markdown text.
    
    Args:
        md_text (str): Markdown text containing the chart explanation
        
    Returns:
        str: The extracted chart explanation
    """
    # Look for text between Chart Explanation: and the next section
    matches = re.findall(r"Chart Explanation:\s*(.*?)(?=Code Explanation:|Data Table:|$)", 
                        md_text, re.DOTALL | re.IGNORECASE)
    
    if not matches:
        return ""  # Return empty string if no chart explanation found
    
    # Clean up the extracted text
    explanation = matches[0].strip()
    # Remove any remaining markdown code block markers
    explanation = re.sub(r'```.*?```', '', explanation, flags=re.DOTALL)
    return explanation.strip()

def extract_code_explanation(md_text: str) -> str:
    """
    Extract code explanation from markdown text.
    
    Args:
        md_text (str): Markdown text containing the code explanation
        
    Returns:
        str: The extracted code explanation
    """
    # Look for text between Code Explanation: and the next section
    matches = re.findall(r"Code Explanation:\s*(.*?)(?=Chart Explanation:|Data Table:|$)", 
                        md_text, re.DOTALL | re.IGNORECASE)
    
    if not matches:
        return ""  # Return empty string if no code explanation found
    
    # Clean up the extracted text
    explanation = matches[0].strip()
    # Remove any remaining markdown code block markers
    explanation = re.sub(r'```.*?```', '', explanation, flags=re.DOTALL)
    return explanation.strip()

def determine_chart_type(query: str) -> str:
    """Determine the most appropriate chart type based on the query."""
    query = query.lower()
    if any(word in query for word in ['trend', 'time', 'line']):
        return 'line'
    elif any(word in query for word in ['distribution', 'histogram', 'density']):
        return 'histogram'
    elif any(word in query for word in ['scatter', 'correlation', 'relationship']):
        return 'scatter'
    elif any(word in query for word in ['pie', 'proportion', 'percentage']):
        return 'pie'
    elif any(word in query for word in ['box', 'quartile', 'outlier']):
        return 'box'
    else:
        return 'bar'

def setup_plot_style():
    """Set up consistent plot styling."""
    # plt.style.use('seaborn')
    plt.rcParams['figure.facecolor'] = '#F0F0F0'
    plt.rcParams['axes.facecolor'] = '#F0F0F0'
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.color'] = '#FFFFFF'
    plt.rcParams['grid.alpha'] = 0.3

def extract_code_from_markdown(md_text: str) -> str:
    """
    Extract Python code from markdown text.

    Args:
        md_text (str): Markdown text containing the code

    Returns:
        str: The extracted Python code
    """
    # First try to find code blocks with python specified
    code_blocks = re.findall(r"```python\n(.*?)```", md_text, re.DOTALL)
    if not code_blocks:
        # If no python-specific blocks found, try any code blocks
        code_blocks = re.findall(r"```\n(.*?)```", md_text, re.DOTALL)
    if not code_blocks:
        # If still no blocks found, try blocks without newlines
        code_blocks = re.findall(r"```(.*?)```", md_text, re.DOTALL)
    
    if not code_blocks:
        raise ValueError(f"No code blocks found in response. Raw response:\n{md_text}")
    
    return "\n".join([block.strip() for block in code_blocks])

def generate_chart(filename: str, query: str) -> AnalysisResult:
    """
    Generate chart and analysis with structured output.
    """
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
        """
        
        # Get the response from the agent
        response = agent.invoke({"input": prompt.format(query=query)})
        
        # Parse the response into structured format
        analysis_result = parse_llm_response(response['output'])
        print(f"analysis_result: {analysis_result}")
        
        # Execute code blocks and update visualizations
        for code_block in analysis_result.code_blocks:
            if code_block.type == 'visualization':
                local_vars = {'df': df, 'plt': plt, 'np': np}
                
                try:
                    # Execute the code
                    exec(code_block.code, globals(), local_vars)
                    
                    # Get the current figure
                    fig = plt.gcf()
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