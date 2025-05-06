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
from analyze_data import generate_chart

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
            # Upload file to MinIO
            minio_client.put_object(
                MINIO_BUCKET,
                filename,
                file,
                file.content_length,
                content_type=file.content_type
            )
            
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    data = request.get_json()
    if not data or 'filename' not in data or 'query' not in data:
        return jsonify({'error': 'Missing filename or query'}), 400
    
    try:
        chart_data = generate_chart(data['filename'], data['query'])
        return jsonify({
            'message': 'Analysis completed successfully',
            'chart_data': chart_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/csv-query', methods=['POST'])
def handle_csv_query():
    data = request.get_json()
    if not data or 'filename' not in data or 'question' not in data:
        return jsonify({'error': 'Missing filename or question'}), 400
    
    try:
        # Get the file from MinIO
        response = minio_client.get_object(MINIO_BUCKET, data['filename'])
        df = pd.read_csv(response)
        
        # Create pandas agent
        agent = pandas_agent(df)
        
        # Run the query
        result = agent.run(data['question'])
        
        # Check if there are any active matplotlib figures
        if plt.get_fignums():
            # Get the current figure
            fig = plt.gcf()
            
            # Convert the figure to a base64 string
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            
            # Clear the figure to free memory
            plt.close('all')
            
            return jsonify({
                'message': 'Query processed successfully',
                'result': result,
                'visualization': {
                    'type': 'image',
                    'data': img_str
                }
            })
        
        return jsonify({
            'message': 'Query processed successfully',
            'result': result
        })
    except Exception as e:
        # Make sure to close any open figures in case of error
        plt.close('all')
        return jsonify({'error': str(e)}), 500

def main():
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()
