import io
import base64
import re
import pandas as pd
import matplotlib.pyplot as plt
from minio_config import minio_client, MINIO_BUCKET
from pandas_agent import pandas_agent
from llm import llm
from State import State


def generate_chart(filename: str, query: str):
    # Define the prompt content
    prompt = """
    The dataset is ALREADY loaded into a DataFrame named 'df'. DO NOT load the data again.

    Before plotting, ensure the data is ready:
    1. Check if columns that are supposed to be numeric are recognized as such. If not, attempt to convert them.
    2. Handle NaN values by filling with mean or median.

    Use package Pandas and Matplotlib ONLY.
    Provide SINGLE CODE BLOCK with a solution using Pandas and Matplotlib plots in a single figure to address the following query:

    - USE SINGLE CODE BLOCK with a solution.
    - Do NOT EXPLAIN the code.
    - DO NOT COMMENT the code.
    - ALWAYS WRAP UP THE CODE IN A SINGLE CODE BLOCK.
    - The code block must start and end with ```

    - Example code format ```code```

    - Colors to use for background and axes of the figure : #F0F0F0
    - Try to use the following color palette for coloring the plots : #8f63ee #ced5ce #a27bf0
    """
    """Answer question using retrieved information as context."""
    # Get the file from MinIO
    data = minio_client.get_object(MINIO_BUCKET, filename)
    
    # Read the data into a pandas DataFrame
    df = pd.read_csv(data)
    
    # Create pandas agent
    agent = pandas_agent(df)
    
    # Get analysis results
    response = agent.invoke(f"{prompt} {query}")
    print(f"response is {response}")
    # if not response or not response.data:
    #     raise ValueError("No response from the agent.")
    # if not response.output:
    #     raise ValueError("No response from the agent.")
    return {"answer": response.output}


messages = [
    {
        "role": "system",
        "content": "You are a helpful Data Visualization assistant who gives a single block without explaining or commenting the code to plot. IF ANYTHING NOT ABOUT THE DATA, JUST politely respond that you don't know.."
    },
    # {
        # "role": "user", "content": prompt
    # }
]

def extract_code_from_markdown(md_text):
    """
    Extract Python code from markdown text.

    Parameters:
    - md_text: Markdown text containing the code

    Returns:
    - The extracted Python code
    """
    # Extract code between the delimiters
    code_blocks = re.findall(r"```(python)?(.*?)```", md_text, re.DOTALL)

    # Strip leading and trailing whitespace and join the code blocks
    code = "\n".join([block[1].strip() for block in code_blocks])

    return code

# def execute_openai_code(response_text: str, df: pd.DataFrame, query):
#     """
#     Execute the code provided by OpenAI in the app.

#     Parameters:
#     - response_text: The response text from OpenAI
#     - df: DataFrame containing the data
#     - query: The user's query
#     """

#     # Extract code from the response text
#     code = extract_code_from_markdown(response_text)

#     # If there's code in the response, try to execute it
#     if code:
#         try:
#             exec(code)
#             st.pyplot()
#         except Exception as e:
#             error_message = str(e)
#             st.error(
#                 f"📟 Apologies, failed to execute the code due to the error: {error_message}"
#             )
#             st.warning(
#                 """
#                 📟 Check the error message and the code executed above to investigate further.

#                 Pro tips:
#                 - Tweak your prompts to overcome the error 
#                 - Use the words 'Plot'/ 'Subplot'
#                 - Use simpler, concise words
#                 - Remember, I'm specialized in displaying charts not in conveying information about the dataset
#             """
#             )
#     else:
#         st.write(response_text)



def generate_chart1(filename: str, query: str) -> dict:
    """
    Generate a chart based on the data file and query.
    Returns a dictionary containing the chart data and analysis results.
    """
    try:
        # Get the file from MinIO
        data = minio_client.get_object(MINIO_BUCKET, filename)
        
        # Read the data into a pandas DataFrame
        df = pd.read_csv(data)
        
        # Create pandas agent
        agent = pandas_agent(df)
        
        # Get analysis results
        analysis_result = agent.invoke({"input": query})
        
        # Create a new figure with custom styling
        plt.style.use('seaborn')
        plt.figure(figsize=(10, 6), facecolor='#F0F0F0')
        ax = plt.gca()
        ax.set_facecolor('#F0F0F0')
        
        # Generate appropriate chart based on the query
        if 'bar' in query.lower():
            df.head(10).plot(kind='bar', x=df.columns[0], y=df.columns[1], ax=ax, color='#8f63ee')
        elif 'line' in query.lower():
            df.head(10).plot(kind='line', x=df.columns[0], y=df.columns[1], ax=ax, color='#a27bf0')
        elif 'scatter' in query.lower():
            df.plot(kind='scatter', x=df.columns[0], y=df.columns[1], ax=ax, color='#ced5ce')
        else:
            # Default to bar chart
            df.head(10).plot(kind='bar', x=df.columns[0], y=df.columns[1], ax=ax, color='#8f63ee')
        
        plt.title('Data Analysis', pad=20)
        plt.tight_layout()
        
        # Convert plot to base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#F0F0F0')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return {
            'chart': img_str,
            'analysis': analysis_result,
            'columns': df.columns.tolist(),
            'shape': df.shape,
            'preview': df.head(5).to_dict('records')
        }
        
    except Exception as e:
        raise Exception(f"Error generating chart: {str(e)}")