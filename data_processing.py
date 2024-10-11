import pandas as pd
import io
import base64
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
import plotly.express as px
import plotly.io as pio

def convert_size(size):
    if 'KB' in size:
        return float(size.replace('KB', '')) * 1024
    elif 'MB' in size:
        return float(size.replace('MB', '')) * 1024 * 1024
    elif 'B' in size:
        return float(size.replace('B', ''))
    return 0

def classify_usage(application):
    serious_apps = ['gambling', 'personal website', 'illegal content']
    minor_apps = ['social media', 'online shopping', 'streaming']
    normal_apps = ['office apps', 'meeting apps']

    application_str = str(application).lower()
    if any(app in application_str for app in serious_apps):
        return 'Serious Cyberloafing'
    elif any(app in application_str for app in minor_apps):
        return 'Minor Cyberloafing'
    elif any(app in application_str for app in normal_apps):
        return 'Normal Usage'
    return 'Unknown'

def process_data(file_path_or_buffer, file_extension):
    if file_extension == 'xlsb':
        data = pd.read_excel(file_path_or_buffer, engine='pyxlsb')
    else:
        data = pd.read_excel(file_path_or_buffer, engine='openpyxl')
    
    # Select relevant columns
    selected_columns = ['Department', 'Sent/Received', 'Application']
    data_selected = data[selected_columns].copy()

    # Split Sent/Received into two separate columns
    sent_received_split = data_selected['Sent/Received'].str.split('/', expand=True)
    data_selected['Sent'] = sent_received_split[0]
    data_selected['Received'] = sent_received_split[1]

    # Fill NaN values in 'Sent' and 'Received' with '0B' to handle missing data
    data_selected['Sent'] = data_selected['Sent'].fillna('0B')
    data_selected['Received'] = data_selected['Received'].fillna('0B')

    # Convert all entries to strings first
    data_selected['Sent'] = data_selected['Sent'].astype(str)
    data_selected['Received'] = data_selected['Received'].astype(str)

    # Apply the conversion function
    data_selected['Sent'] = data_selected['Sent'].apply(convert_size)
    data_selected['Received'] = data_selected['Received'].apply(convert_size)

    # Ensure 'Application' is a string and classify each application usage
    data_selected['Application'] = data_selected['Application'].astype(str)
    data_selected['Usage'] = data_selected['Application'].apply(classify_usage)

    # Drop the original Sent/Received column
    data_selected = data_selected.drop(columns=['Sent/Received'])

    # Encoding categorical variables
    le_department = LabelEncoder()
    le_application = LabelEncoder()
    le_usage = LabelEncoder()

    data_selected['Department'] = le_department.fit_transform(data_selected['Department'])
    data_selected['Application'] = le_application.fit_transform(data_selected['Application'])
    data_selected['Usage'] = le_usage.fit_transform(data_selected['Usage'])

    # Drop the 'Sent' column as it only contains zeros
    data_selected = data_selected.drop(columns=['Sent'])

    # Standardizing the data
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data_selected)

    # Determine the optimal number of clusters using the elbow method
    wcss = []
    max_clusters = min(10, len(data_selected))  # Max clusters should not exceed the number of samples
    for i in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=i, random_state=42)
        kmeans.fit(data_scaled)
        wcss.append(kmeans.inertia_)

    # Plotting the elbow graph using Plotly
    elbow_fig = px.line(x=range(1, max_clusters + 1), y=wcss, markers=True, title='Elbow Method for Determining Optimal Number of Clusters')
    elbow_plot_html = pio.to_html(elbow_fig, full_html=False)

    # Determine optimal number of clusters (for example, we choose 3 here)
    optimal_clusters = min(3, max_clusters)

    # Fitting the KMeans model
    kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
    data_selected['Cluster'] = kmeans.fit_predict(data_scaled)

    # Plotting the clusters using Plotly
    cluster_fig = px.scatter(data_selected, x='Department', y='Application', color='Cluster', title='Cluster Visualization')
    cluster_plot_html = pio.to_html(cluster_fig, full_html=False)

    # Plotting Usage Distribution using Plotly
    usage_counts = data_selected['Usage'].value_counts().reset_index()
    usage_counts.columns = ['Usage', 'count']
    usage_fig = px.bar(usage_counts, x='Usage', y='count', title='Usage Distribution')
    usage_plot_html = pio.to_html(usage_fig, full_html=False)

    # Convert dataframe to HTML
    pd.set_option('display.max_rows', None)
    table_html = data_selected.to_html(classes='table table-striped')

    return (elbow_plot_html, cluster_plot_html, usage_plot_html, table_html)
