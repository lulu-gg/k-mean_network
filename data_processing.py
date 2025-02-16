import pandas as pd
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
    return None

def process_data(file_path_or_buffer, file_extension):
    # Membaca data dari file Excel
    if file_extension == 'xlsb':
        data = pd.read_excel(file_path_or_buffer, engine='pyxlsb')
    else:
        data = pd.read_excel(file_path_or_buffer, engine='openpyxl')

    # Pilih kolom yang relevan
    selected_columns = ['Username', 'Department', 'Sent/Received', 'Application']
    data_selected = data[selected_columns].copy()

    # Menyimpan nama asli Department dan Application sebelum encoding
    data_selected['Department_Original'] = data_selected['Department']
    data_selected['Application_Original'] = data_selected['Application']

    # Membagi kolom 'Sent/Received'
    sent_received_split = data_selected['Sent/Received'].str.split('/', expand=True)
    data_selected['Sent'] = sent_received_split[0].fillna('0B')
    data_selected['Received'] = sent_received_split[1].fillna('0B')

    # Konversi ukuran menjadi angka
    data_selected['Sent'] = data_selected['Sent'].astype(str).apply(convert_size)
    data_selected['Received'] = data_selected['Received'].astype(str).apply(convert_size)

    # Mengklasifikasikan 'Usage'
    data_selected['Application'] = data_selected['Application'].astype(str)
    data_selected['Usage'] = data_selected['Application'].apply(classify_usage)

    # Encoding kategori hanya untuk keperluan standarisasi
    le_department = LabelEncoder()
    le_application = LabelEncoder()
    data_selected['Department'] = le_department.fit_transform(data_selected['Department'])
    data_selected['Application'] = le_application.fit_transform(data_selected['Application'])

    # Standarisasi data
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data_selected[['Department', 'Received', 'Application']])

    # Tentukan jumlah cluster optimal dengan Elbow Method
    wcss = []
    max_clusters = min(10, len(data_selected))
    for i in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=i, random_state=42, n_init=10)
        kmeans.fit(data_scaled)
        wcss.append(kmeans.inertia_)

    # Plot Elbow Method
    elbow_fig = px.line(x=range(1, max_clusters + 1), y=wcss, markers=True, title='Elbow Method for Determining Optimal Number of Clusters')
    elbow_plot_html = pio.to_html(elbow_fig, full_html=False)

    # Tentukan jumlah cluster optimal
    optimal_clusters = min(3, max_clusters)
    kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
    data_selected['Cluster'] = kmeans.fit_predict(data_scaled)

    # Pemetaan hasil klaster ke kategori 'Usage'
    cluster_to_usage = {
        0: 'Normal Usage',
        1: 'Minor Cyberloafing',
        2: 'Serious Cyberloafing'
    }

    # Perbarui semua nilai Usage menggunakan klaster jika belum terklasifikasi
    data_selected['Usage'] = data_selected.apply(
        lambda row: cluster_to_usage[row['Cluster']] if row['Usage'] is None else row['Usage'], axis=1
    )

    # Plot klaster dengan angka seperti sebelumnya
    cluster_fig = px.scatter(
        data_selected, 
        x='Department', 
        y='Application', 
        color='Cluster', 
        title='Cluster Visualization'
    )
    cluster_plot_html = pio.to_html(cluster_fig, full_html=False)

    # Plot distribusi Usage
    usage_counts = data_selected['Usage'].value_counts().reset_index()
    usage_counts.columns = ['Usage', 'count']
    usage_fig = px.bar(usage_counts, x='Usage', y='count', title='Usage Distribution')
    usage_plot_html = pio.to_html(usage_fig, full_html=False)

    # 📌 Total Sent and Received per category (Now in Bar Chart)
    usage_totals = data_selected.groupby('Usage').agg({'Sent': 'sum', 'Received': 'sum'}).reset_index()

    usage_totals_fig = px.bar(
        usage_totals, 
        x='Usage', 
        y=['Sent', 'Received'], 
        title='Total Sent and Received Data by Usage Category',
        barmode='group',
        labels={'value': 'Data Usage (Bytes)', 'variable': 'Type'}
    )
    
    # Konversi ke HTML agar bisa ditampilkan di template
    usage_totals_html = pio.to_html(usage_totals_fig, full_html=False)

    # 📌 Menampilkan Username dalam Data Table dengan nama asli Department & Application
    table_html = data_selected[['Username', 'Department_Original', 'Application_Original', 'Sent', 'Received', 'Usage', 'Cluster']].to_html(classes='table table-striped', index=False, table_id="data-table")
    return elbow_plot_html, cluster_plot_html, usage_plot_html, table_html, usage_totals_html
