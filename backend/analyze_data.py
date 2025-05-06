import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from minio_config import minio_client, MINIO_BUCKET
from pandas_agent import pandas_agent

def generate_chart(filename: str, query: str) -> str:
    """
    Generate a chart based on the data file and query.
    Returns a base64 encoded PNG image.
    """
    try:
        # Get the file from MinIO
        data = minio_client.get_object(MINIO_BUCKET, filename)
        
        # Read the data into a pandas DataFrame
        # Assuming CSV format for now
        df = pd.read_csv(data)
        
        agent = pandas_agent(df)
        result = agent.invoke({"input": query})
        
        print(result)

        # Create a new figure
        plt.figure(figsize=(10, 6))
        
        # Basic chart generation based on query
        # This is a simple implementation - you might want to use more sophisticated
        # NLP to understand the query and generate appropriate charts
        if 'bar' in query.lower():
            # Simple bar chart of first two columns
            df.head(10).plot(kind='bar', x=df.columns[0], y=df.columns[1])
        elif 'line' in query.lower():
            # Simple line chart of first two columns
            df.head(10).plot(kind='line', x=df.columns[0], y=df.columns[1])
        elif 'scatter' in query.lower():
            # Simple scatter plot of first two columns
            df.plot(kind='scatter', x=df.columns[0], y=df.columns[1])
        else:
            # Default to bar chart
            df.head(10).plot(kind='bar', x=df.columns[0], y=df.columns[1])
        
        plt.title('Data Analysis')
        plt.tight_layout()
        
        # Convert plot to base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return img_str
    except Exception as e:
        raise Exception(f"Error generating chart: {str(e)}") 