from flask import Flask, request, render_template
from data_processing import process_data
import io
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    try:
        # Read the file into a memory buffer
        file_bytes = file.read()
        excel_buffer = io.BytesIO(file_bytes)
        
        # Ensure buffer is at the start
        excel_buffer.seek(0)
        
        # Determine file extension
        file_extension = file.filename.split('.')[-1].lower()

        # Test if the file can be read as Excel
        if file_extension == 'xlsb':
            pd.read_excel(excel_buffer, engine='pyxlsb')
        else:
            pd.read_excel(excel_buffer, engine='openpyxl')

        # Call process_data function using buffer
        elbow_plot_html, cluster_plot_html, usage_plot_html, table_html = process_data(excel_buffer, file_extension)
        
        # Debug prints
        print("Elbow Plot HTML:")
        print(elbow_plot_html)
        print("Cluster Plot HTML:")
        print(cluster_plot_html)
        print("Usage Plot HTML:")
        print(usage_plot_html)
        print("Table HTML:")
        print(table_html)
        
        return render_template('test.html', 
                               elbow_plot_html=elbow_plot_html, 
                               cluster_plot_html=cluster_plot_html, 
                               usage_plot_html=usage_plot_html,
                               table_html=table_html)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
