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
# from IPython.display import Image, display

from State import State
from execute_query import execute_query
from generate_answer import generate_answer
from generate_chart import generate_chart

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

graph_builder = StateGraph(State).add_sequence(
    [write_query, execute_query, generate_answer]
)

graph_builder.add_edge(START, "write_query")
graph = graph_builder.compile()

# display(Image(graph.get_graph().draw_mermaid_png()))

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
            
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'size': file_size
            })
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-charts', methods=['POST'])
def analyze_charts():
    data = request.get_json()

    if not data or 'filename' not in data or 'query' not in data:
        return jsonify({'error': 'Missing filename or query'}), 400
    # print("Received data for chart generation:", data)
    
    try:
        result = generate_chart(data['filename'], data['query'])
        return jsonify({
            'message': 'Generating Charts completed successfully',
            'data': result
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
        
        # Debug: Print the actual content of the buffer
        # csv_data.seek(0)
        # content = csv_data.read().decode('utf-8')
        # print("CSV Content:", content[:500])  # Print first 500 characters
        # csv_data.seek(0)
        
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
        
        # print("DataFrame created successfully")
        # print("DataFrame columns:", df.columns.tolist())
        # print("DataFrame shape:", df.shape)
        
        # Create pandas agent
        agent = pandas_agent(df)
        print("Agent created successfully")
        
        # Run the query
        result = agent.invoke(data['query'])
        print(result.output)
        
        return jsonify({
            'message': 'Query processed successfully',
            'result': result.output
        })
    except Exception as e:
        print(f"Error processing CSV query: {str(e)}")
        return jsonify({'error': str(e)}), 500

def main():
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()
