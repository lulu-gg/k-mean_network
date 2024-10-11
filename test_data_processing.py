import pytest
import pandas as pd
import io
from data_processing import process_data

def test_process_data():
    # Buat data uji dengan lebih banyak sampel
    data = {
        'Department': ['Sales', 'HR', 'IT', 'Finance', 'Marketing', 'Support', 'Operations', 'Admin'],
        'Sent/Received': ['100KB/200KB', '200KB/300KB', '150KB/250KB', '300KB/400KB', '120KB/220KB', '180KB/280KB', '170KB/270KB', '140KB/240KB'],
        'Application': ['Social Media', 'Office Apps', 'Online Shopping', 'Meeting Apps', 'Streaming', 'Gambling', 'Personal Website', 'Illegal Content']
    }
    df = pd.DataFrame(data)
    
    # Simpan data ke file Excel sementara dalam memori
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)  # Kembali ke awal buffer

    # Panggil fungsi process_data menggunakan buffer
    elbow_plot_url, cluster_plot_url, hist_plot_url, usage_plot_url, confusion_matrix_url, table_html = process_data(excel_buffer, 'xlsx')
    
    # Pastikan hasil tidak kosong
    assert elbow_plot_url is not None
    assert cluster_plot_url is not None
    assert hist_plot_url is not None
    assert usage_plot_url is not None
    assert table_html is not None

if __name__ == "__main__":
    pytest.main()
