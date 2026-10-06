# file: dashboard_mou.py
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# -----------------------------
# 1. Đọc và làm sạch dữ liệu
# -----------------------------
@st.cache_data
def load_data(file_path):
    if file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path, sheet_name=None)
        data = pd.concat(df.values(), ignore_index=True)
    else:
        data = pd.read_csv(file_path)

    data.columns = data.columns.str.strip().str.lower()
    data = data.fillna("Chưa có thông tin")

    valid_status = ["Đã thực hiện", "Đang thực hiện", "Chưa thực hiện"]
    def normalize_status(x):
        if str(x).strip() in valid_status:
            return str(x).strip()
        else:
            return "Chưa thực hiện"
    data['tình trạng'] = data['tình trạng'].apply(normalize_status)

    # Thêm cột ngày cập nhật nếu chưa có
    if 'ngày cập nhật' not in data.columns:
        data['ngày cập nhật'] = "Chưa cập nhật"

    return data

# -----------------------------
# 2. Giao diện Streamlit
# -----------------------------
st.set_page_config(page_title="MOU Dashboard", layout="wide")
st.title("📊 Dashboard công việc chuẩn bị lễ ký kết MOU - 14/10/2026")

uploaded_file = st.file_uploader("Tải lên file Excel/CSV", type=["xlsx", "csv"])
if uploaded_file:
    df = load_data(uploaded_file)

    # Bộ lọc
    bo_phan = st.sidebar.multiselect("Chọn bộ phận", options=df['bộ phận'].unique())
    trang_thai = st.sidebar.multiselect("Chọn tình trạng", options=df['tình trạng'].unique())

    filtered_df = df.copy()
    if bo_phan:
        filtered_df = filtered_df[filtered_df['bộ phận'].isin(bo_phan)]
    if trang_thai:
        filtered_df = filtered_df[filtered_df['tình trạng'].isin(trang_thai)]

    # -----------------------------
    # 3. Cho phép cập nhật tiến độ
    # -----------------------------
    st.subheader("✏️ Cập nhật tiến độ công việc")
    selected_task = st.selectbox("Chọn hạng mục để cập nhật", filtered_df['hạng mục'].unique())
    new_status = st.selectbox("Trạng thái mới", ["Đã thực hiện", "Đang thực hiện", "Chưa thực hiện"])
    if st.button("Cập nhật"):
        df.loc[df['hạng mục'] == selected_task, 'tình trạng'] = new_status
        df.loc[df['hạng mục'] == selected_task, 'ngày cập nhật'] = datetime.now().strftime("%d/%m/%Y %H:%M")
        st.success(f"✅ Đã cập nhật '{selected_task}' thành '{new_status}'")

    # -----------------------------
    # 4. Hiển thị bảng dữ liệu
    # -----------------------------
    st.subheader("📋 Danh sách công việc")
    st.dataframe(filtered_df, use_container_width=True)

    # -----------------------------
    # 5. Biểu đồ tiến độ
    # -----------------------------
    st.subheader("📈 Thống kê tình trạng công việc")
    status_count = filtered_df.groupby(['bộ phận', 'tình trạng']).size().reset_index(name='số lượng')
    fig = px.bar(status_count, x="bộ phận", y="số lượng", color="tình trạng", barmode="stack")
    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # 6. Biểu đồ tròn tổng quan
    # -----------------------------
    st.subheader("🟢 Tổng quan tình trạng")
    pie_data = filtered_df['tình trạng'].value_counts().reset_index()
    pie_data.columns = ['tình trạng', 'số lượng']
    fig_pie = px.pie(pie_data, names="tình trạng", values="số lượng")
    st.plotly_chart(fig_pie, use_container_width=True)