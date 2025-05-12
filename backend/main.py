import os
import io
import base64
from QueryOutput import write_query
from langgraph.graph import START, StateGraph
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from minio_config import minio_client, MINIO_BUCKET
import pandas as pd
from pandas_agent import pandas_agent
import matplotlib.pyplot as plt
from execute_analysis_query import execute_analysis_query
from State import State
from execute_sql_query import execute_sql_query
from generate_answer import generate_answer
from generate_chart import generate_chart
from analysis_router import route_analysis
from flask import send_file
from llm import llm


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

graph_builder = StateGraph(State).add_sequence(
    [write_query, execute_sql_query, generate_answer]
)

graph_builder.add_edge(START, "write_query")
graph = graph_builder.compile()

@app.route('/api/query', methods=['POST'])
def handle_query():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({'error': 'No question provided'}), 400
    
    question = data['question']
    result = None
    
    # Stream through the graph and collect the final result
    for step in graph.stream(
        {"question": question}, stream_mode="updates"
    ):
        print(step)
        result = step
    
    return jsonify(result)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        try:
            # Read the file content
            file_content = file.read()
            file_size = len(file_content)
            print(f"File size: {file_size} bytes")
            
            if file_size == 0:
                return jsonify({'error': 'Empty file uploaded'}), 400
            
            # Create a BytesIO object from the file content
            file_buffer = io.BytesIO(file_content)
            
            # Upload file to MinIO
            minio_client.put_object(
                MINIO_BUCKET,
                filename,
                file_buffer,
                file_size,
                content_type=file.content_type
            )
            
            print(f"File {filename} uploaded successfully to MinIO")
            
            # Get file metadata and preview
            file_buffer.seek(0)
            try:
                df = pd.read_csv(file_buffer)
                preview = df.head(5).to_dict(orient='records')
                metadata = {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'dtypes': df.dtypes.astype(str).to_dict()
                }
            except Exception as e:
                preview = None
                metadata = None
            
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'size': file_size,
                # 'preview': preview,
                'metadata': metadata
            })
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return jsonify({'error': str(e)}), 500

def generate_content_description(df):
    """Generate a natural language description of the CSV content using LLM."""
    try:
        # Prepare the data for the prompt
        sample_data = df.head(3).to_dict(orient='records')
        
        prompt = f"""You are a data analyst. Analyze this dataset and provide a concise but informative description.
        Focus on:
        1. What kind of data this appears to be
        2. Key columns and their purposes
        3. Any notable patterns or characteristics
        4. Potential use cases for this data
        5. Convert NaN values to null
        
        Dataset Information:
        Number of rows: {len(df)}
        Number of columns: {len(df.columns)}
        Column names: {df.columns.tolist()}
        Data types: {df.dtypes.astype(str).to_dict()}
        Sample data (first 3 rows): {sample_data}
        
        Provide a clear, concise description in 2-3 sentences."""
        
        # Generate the description using the existing LLM
        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        print(f"Error generating content description: {str(e)}")
        return "Unable to generate content description."

@app.route('/api/file-metadata/<filename>', methods=['GET'])
def get_file_metadata(filename):
    try:
        # Get the file from MinIO
        response = minio_client.get_object(MINIO_BUCKET, filename)
        file_buffer = io.BytesIO(response.read())
        
        # Read CSV and get metadata
        df = pd.read_csv(file_buffer)
        preview = df.head(5).to_dict(orient='records')
        metadata = {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict()
        }
        
        # Generate content description using LLM
        content_description = generate_content_description(df)
        
        return jsonify({
            'filename': filename,
            'preview': preview,
            'metadata': metadata,
            'content_description': content_description
        })
    except Exception as e:
        print(f"Error getting file metadata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_charts():
    data = request.get_json()

    if not data or 'filename' not in data or 'query' not in data:
        return jsonify({'error': 'Missing filename or query'}), 400
    
    try:
        result = generate_chart(data['filename'], data['query'])
        # Convert AnalysisResult to dict for JSON serialization
        result_dict = {
            'code_blocks': [block.model_dump() for block in result.code_blocks],
            'explanations': [exp.model_dump() for exp in result.explanations],
            'data_tables': [table.model_dump() for table in result.data_tables],
            'visualizations': [viz.model_dump() for viz in result.visualizations],
            'metadata': result.metadata,
            'timestamp': result.timestamp.isoformat()
        }
        
        return jsonify({
            'message': 'Analysis completed successfully',
            'data': result_dict
        })
    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/csv-query', methods=['POST'])
def handle_csv_query():
    data = request.get_json()
    if not data or 'filename' not in data or 'query' not in data:
        return jsonify({'error': 'Missing filename or question'}), 400
    
    try:
        # Get the file from MinIO        
        response = minio_client.get_object(MINIO_BUCKET, data['filename'])
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
        
        print("Agent created successfully")
        # Run the query
        result = execute_analysis_query(data['filename'], data['query'])
        
        if 'error' in result:
            return jsonify(result), 500
            
        return jsonify(result)
    except Exception as e:
        print(f"Error processing CSV query: {str(e)}")
        return jsonify({'error': str(e)}), 500

def short_description(filename: str, query: str):
    response = minio_client.get_object(MINIO_BUCKET, filename)
    csv_data = io.BytesIO(response.read())
    df = pd.read_csv(csv_data, sep=',')
    return df.head().to_markdown()


@app.route('/files/<filename>')
def serve_file(filename):
    # Download from MinIO to a temp file, then serve
    data = minio_client.get_object(MINIO_BUCKET, filename)
    temp_path = f'/tmp/{filename}'
    with open(temp_path, 'wb') as f:
        f.write(data.read())
    return send_file(temp_path, mimetype='image/png')



def main():
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()
