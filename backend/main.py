import os
import io
from QueryOutput import write_query
from langgraph.graph import START, StateGraph
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from configs.minio_config import minio_client, MINIO_BUCKET
import pandas as pd
from execute_analysis_query import execute_analysis_query
from State import State
from execute_sql_query import execute_sql_query
from generate_answer import generate_answer
from generate_chart import generate_chart
from analysis_router import route_analysis
from flask import send_file
from llm import llm
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from langchain.prompts import PromptTemplate
from datetime import datetime
from rag_query import SMSRetriever
import json
import sqlite3
from rag_query import rag_query


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

graph_builder = StateGraph(State).add_sequence(
    [write_query, execute_sql_query, generate_answer]
)

graph_builder.add_edge(START, "write_query")
graph = graph_builder.compile()

# Add SQLite database setup
def init_db():
    conn = sqlite3.connect('data/analysis.db')
    c = conn.cursor()
    
    # Create threads table with additional columns
    c.execute('''
        CREATE TABLE IF NOT EXISTS threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            last_query TEXT NOT NULL,
            last_updated TIMESTAMP NOT NULL,
            file_name TEXT,
            file_metadata TEXT
        )
    ''')
    
    # Create chat_messages table
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            FOREIGN KEY (thread_id) REFERENCES threads (id)
        )
    ''')
    
    # Create data_tables table
    c.execute('''
        CREATE TABLE IF NOT EXISTS data_tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            headers TEXT NOT NULL,  -- JSON array of headers
            data TEXT NOT NULL,     -- JSON array of rows
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (thread_id) REFERENCES threads (id)
        )
    ''')
    
    # Create notes table
    c.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            FOREIGN KEY (thread_id) REFERENCES threads (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

def get_db():
    conn = sqlite3.connect('data/analysis.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

retriever = SMSRetriever("sms_data.csv")

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

class ContentDescription(BaseModel):
    data_type: str = Field(description="Type of data in the dataset")
    key_columns: List[str] = Field(description="List of key columns and their purposes")
    patterns: List[str] = Field(description="Notable patterns or characteristics")
    use_cases: List[str] = Field(description="Potential use cases for this data")
    summary: str = Field(description="A concise 2-3 sentence summary of the dataset")

def generate_content_description(df):
    """Generate a natural language description of the CSV content using LLM."""
    try:
        # Prepare the data for the prompt
        sample_data = df.head(3).to_dict(orient='records')
        
        # Create parser and prompt template
        parser = PydanticOutputParser(pydantic_object=ContentDescription)
        
        prompt = PromptTemplate(
            template="""You are a data analyst. Analyze this dataset and provide a structured description.
            Focus on:
            1. What kind of data this appears to be
            2. Key columns and their purposes
            3. Any notable patterns or characteristics
            4. Potential use cases for this data
            5. Convert NaN values to null
            
            Dataset Information:
            Number of rows: {rows}
            Number of columns: {columns}
            Column names: {column_names}
            Data types: {dtypes}
            Sample data (first 3 rows): {sample_data}
            
            {format_instructions}
            """,
            input_variables=["rows", "columns", "column_names", "dtypes", "sample_data"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        # Format and invoke the prompt
        formatted_prompt = prompt.format(
            rows=len(df),
            columns=len(df.columns),
            column_names=df.columns.tolist(),
            dtypes=df.dtypes.astype(str).to_dict(),
            sample_data=sample_data
        )
        
        # Generate and parse the response
        response = llm.invoke(formatted_prompt)
        result = parser.parse(response.content)
        
        # Return a formatted string representation
        return f"{result.summary}\n\nKey columns: {', '.join(result.key_columns)}\nPatterns: {', '.join(result.patterns)}\nUse cases: {', '.join(result.use_cases)}"
        
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
    thread = None
    if not data or 'thread_id':
        thread_metadata = {
            'title': data.get('title', ''),
            'last_query': data.get('query', ''),
            'file_name': data.get('filename'),
            'file_metadata': data.get('file_metadata', {})
        }
        thread = create_thread(thread_metadata)
        print(thread)
    else:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM threads WHERE id = ?', (data['thread_id'],))
        thread = dict(c.fetchone())
        conn.close()

    add_chat_message(
        thread_id=thread['id'],
        role='user',
        content=f"{data['query']}")
    
    if not data or 'filename' not in data or 'query' not in data:
        return jsonify({'error': 'Missing filename or query'}), 400
    
    try:
        result = generate_chart(data['filename'], data['query']).values()
        
        # Convert AnalysisResult to dict for JSON serialization
        result_dict = {
            'code_blocks': [block.model_dump() for block in result.code_blocks],
            'explanations': [exp.model_dump() for exp in result.explanations],
            'data_tables': [table.model_dump() for table in result.data_tables],
            'visualizations': [viz.model_dump() for viz in result.visualizations],
            'metadata': result.metadata,
            'timestamp': result.timestamp.isoformat()
        }
        
        result_content = json.dumps(result_dict)
        
        add_chat_message(thread_id=thread['id'], role='assistant', content=result_content)
        
        _ = [add_data_table(thread_id=thread['id'], data=data_table) for data_table in result_dict['data_tables']]

        return jsonify({
            'message': 'Analysis completed successfully',
            "thread": thread,
            'data': result_dict,            
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
        print("Result: ", result)
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

@app.route('/api/threads', methods=['GET'])
def get_threads():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM threads ORDER BY last_updated DESC')
        threads = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(threads)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/threads', methods=['POST'])
def create_thread(data):
    try:        
        conn = get_db()
        c = conn.cursor()
        
        # Create the thread
        c.execute('''
            INSERT INTO threads (title, last_query, last_updated, file_name, file_metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data.get('title', ''),
            data.get('last_query', ''),
            datetime.now().isoformat(),
            data.get('file_name'),
            json.dumps(data.get('file_metadata', {}))
        ))
        
        thread_id = c.lastrowid
        
        # If file metadata contains content description, create a note
        if data.get('fileMetadata', {}).get('content_description'):
            now = datetime.now().isoformat()
            c.execute('''
                INSERT INTO notes (thread_id, content, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (
                thread_id,
                data['fileMetadata']['content_description'],
                now,
                now
            ))
        
        conn.commit()
        
        # Get the created thread
        c.execute('SELECT * FROM threads WHERE id = ?', (thread_id,))
        new_thread = dict(c.fetchone())
        conn.close()
        
        return new_thread
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/threads/<int:thread_id>/chat', methods=['GET'])
def get_chat_history(thread_id):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            SELECT * FROM chat_messages 
            WHERE thread_id = ? 
            ORDER BY timestamp ASC
        ''', (thread_id,))
        messages = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(messages)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @app.route('/api/threads/<int:thread_id>/chat', methods=['POST'])
def add_chat_message(thread_id, role, content):
    """Add a chat message to the thread."""
    try:
        data = request.get_json()
        conn = get_db()
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO chat_messages (thread_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (
            thread_id,
            role,
            content,
            datetime.now().isoformat()
        ))
        
        message_id = c.lastrowid
        conn.commit()
        
        # Get the created message
        c.execute('SELECT * FROM chat_messages WHERE id = ?', (message_id,))
        message = dict(c.fetchone())
        conn.close()
        
        return jsonify(message)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/threads/<int:thread_id>/data-tables', methods=['GET'])
def get_thread_data_tables(thread_id):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            SELECT * FROM data_tables
            WHERE thread_id = ? 
            ORDER BY created_at DESC
        ''', (thread_id,))
        tables = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(tables)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/threads/<int:thread_id>/data-tables', methods=['POST'])
def add_data_table(thread_id):
    try:        
        data = request.get_json()
        conn = get_db()
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO data_tables (thread_id, title, description, headers, data, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            thread_id,
            data.get('title', ''),
            data.get('description', ''),
            json.dumps(data.get('headers', [])),
            json.dumps(data.get('data', [])),
            datetime.now().isoformat()
        ))
        
        table_id = c.lastrowid
        conn.commit()
        
        # Get the created table
        c.execute('SELECT * FROM data_tables WHERE id = ?', (table_id,))
        new_table = dict(c.fetchone())
        conn.close()
        
        return jsonify(new_table)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/threads/<int:thread_id>/notes', methods=['GET'])
def get_thread_notes(thread_id):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            SELECT * FROM notes 
            WHERE thread_id = ? 
            ORDER BY updated_at DESC
        ''', (thread_id,))
        notes = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(notes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/threads/<int:thread_id>/notes', methods=['POST'])
def add_note(thread_id):
    try:
        data = request.get_json()
        conn = get_db()
        c = conn.cursor()
        
        now = datetime.now().isoformat()
        c.execute('''
            INSERT INTO notes (thread_id, content, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (
            thread_id,
            data.get('content', ''),
            now,
            now
        ))
        
        note_id = c.lastrowid
        conn.commit()
        
        # Get the created note
        c.execute('SELECT * FROM notes WHERE id = ?', (note_id,))
        new_note = dict(c.fetchone())
        conn.close()
        
        return jsonify(new_note)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/threads/<int:thread_id>/notes/<int:note_id>', methods=['PUT'])
def update_note(thread_id, note_id):
    try:
        data = request.get_json()
        conn = get_db()
        c = conn.cursor()
        
        c.execute('''
            UPDATE notes 
            SET content = ?, updated_at = ?
            WHERE id = ? AND thread_id = ?
        ''', (
            data.get('content', ''),
            datetime.now().isoformat(),
            note_id,
            thread_id
        ))
        
        conn.commit()
        
        # Get the updated note
        c.execute('SELECT * FROM notes WHERE id = ?', (note_id,))
        updated_note = dict(c.fetchone())
        conn.close()
        
        return jsonify(updated_note)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rag-query', methods=['POST'])
def handle_rag_query():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({'error': 'Missing filename or question'}), 400
    try:
        answer = retriever.query(data['question'])
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def main():
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()
