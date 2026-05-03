import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# إعدادات الصفحة
st.set_page_config(page_title="Mustafa Express Online", layout="wide")

# رابط الملف اللي أنت بعته بعد تحويله لرابط تحميل مباشر
# ملحوظة: لو غيرت الملف، هنحتاج نحدث المعرف (ID) اللي في الرابط ده
file_id = '17YzcGVZNAuqirCr1keNqKJFtx9AQBiok'
excel_url = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx'

@st.cache_data(ttl=60) # تحديث البيانات كل دقيقة
def load_data_from_drive():
    try:
        response = requests.get(excel_url)
        return pd.read_excel(BytesIO(response.content))
    except:
        return pd.DataFrame()

# --- نظام الدخول الموقت (لحين ربط ملف المستخدمين) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("📦 دخول نظام مصطفى إكسبريس - أونلاين")
    with st.form("login"):
        u = st.text_input("المستخدم")
        p = st.text_input("السر", type="password")
        if st.form_submit_button("دخول"):
            if u == "admin" and p == "123":
                st.session_state['logged_in'] = True
                st.rerun()
else:
    st.sidebar.success("تم الاتصال بجوجل درايف ✅")
    df = load_data_from_drive()
    
    menu = st.sidebar.selectbox("القائمة", ["لوحة الإحصائيات", "البحث وتحديث الحالة"])

    if menu == "لوحة الإحصائيات":
        st.title("📊 التقارير المالية الحية")
        if not df.empty:
            actual_count = df.shape[0]
            # تنظيف البيانات للحسابات
            df['سعر المستلم'] = pd.to_numeric(df['سعر المستلم'], errors='coerce').fillna(0)
            df['الشحن'] = pd.to_numeric(df['الشحن'], errors='coerce').fillna(0)
            
            total_net = df['سعر المستلم'].sum() - df['الشحن'].sum()
            
            c1, c2 = st.columns(2)
            c1.metric("عدد الشحنات الحالية", f"{actual_count}")
            c2.metric("إجمالي الصافي العام", f"{total_net:,.2f} ج.م")
            
            st.divider()
            st.subheader("📍 تفاصيل المحافظات")
            prov_stats = df.groupby('المحافظه').agg({'سعر المستلم':'sum', 'الشحن':'sum'}).reset_index()
            prov_stats['الصافي'] = prov_stats['سعر المستلم'] - prov_stats['الشحن']
            st.table(prov_stats)
        else:
            st.warning("جاري تحميل البيانات من جوجل درايف... تأكد من صلاحيات الرابط")

    elif menu == "البحث وتحديث الحالة":
        st.title("🔍 استعلام سريع")
        q = st.text_input("ابحث بالاسم أو الموبايل")
        if not df.empty:
            res = df[df.astype(str).apply(lambda x: q.lower() in x.str.lower().values, axis=1)]
            st.dataframe(res)
