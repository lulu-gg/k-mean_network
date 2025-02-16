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
    try:
        # Debug: Print untuk memeriksa file yang diupload
        print("File received:", request.files['file'].filename)
        
        file = request.files['file']
        if file.filename == '':
            print("Debug: No file selected")
            return render_template('index.html', message='No selected file')
        
        file_bytes = file.read()
        excel_buffer = io.BytesIO(file_bytes)
        excel_buffer.seek(0)
        
        file_extension = file.filename.split('.')[-1].lower()
        print("Debug: File extension:", file_extension)

        # Test pembacaan file
        try:
            if file_extension == 'xlsb':
                test_read = pd.read_excel(excel_buffer, engine='pyxlsb')
            else:
                test_read = pd.read_excel(excel_buffer, engine='openpyxl')
            print("Debug: Successfully read Excel file, shape:", test_read.shape)
        except Exception as e:
            print("Debug: Error reading Excel:", str(e))
            raise

        # Reset buffer position
        excel_buffer.seek(0)
        
        # Process data dengan print debugging
        print("Debug: Starting data processing...")
        results = process_data(excel_buffer, file_extension)
        print("Debug: Data processing completed")
        
        # Debug: Check results
        print("Debug: Number of results returned:", len(results))
        
        # Unpack results dengan explicit checking
        if len(results) != 8:
            print("Debug: Incorrect number of results returned. Expected 8, got:", len(results))
            raise ValueError("Incorrect number of results")
            
        (elbow_plot_html, cluster_plot_html, usage_plot_html, table_html,
         usage_totals_html, serious_apps_html, hourly_html, dept_html) = results
        
        # Debug: Check if any result is None
        for i, result in enumerate([elbow_plot_html, cluster_plot_html, usage_plot_html, 
                                  table_html, usage_totals_html, serious_apps_html, 
                                  hourly_html, dept_html]):
            if result is None:
                print(f"Debug: Result {i} is None")

        return render_template(
            'test.html', 
            elbow_plot_html=elbow_plot_html,
            cluster_plot_html=cluster_plot_html,
            usage_plot_html=usage_plot_html,
            table_html=table_html,
            usage_totals_html=usage_totals_html,
            serious_apps_html=serious_apps_html,
            hourly_html=hourly_html,
            dept_html=dept_html
        )
    except Exception as e:
        print("Debug: Error in upload_file:", str(e))
        import traceback
        print("Debug: Full traceback:")
        print(traceback.format_exc())
        return render_template('index.html', message=f"Error: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)