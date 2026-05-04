import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# إعدادات الصفحة
st.set_page_config(page_title="Mustafa Express Live", layout="wide")

# الرابط ده تم تعديله ليكون رابط تحميل مباشر (Direct Export)
# ده الرابط السحري اللي بيخلي جوجل درايف يبعت الداتا فوراً للبرنامج
excel_url = "https://docs.google.com/spreadsheets/d/17YzcGVZNAuqirCr1keNqKJFtx9AQBiok/export?format=xlsx"

@st.cache_data(ttl=10) # تحديث كل 10 ثواني عشان تشوف التغيير لحظي
def load_data_from_drive():
    try:
        # بنقول لجوجل "احنا عاوزين نحمل الملف ده"
        response = requests.get(excel_url)
        # بنقرأ محتوى الملف كأنه إكسل
        data = pd.read_excel(BytesIO(response.content))
        return data
    except Exception as e:
        return pd.DataFrame()

# --- نظام الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("📦 دخول نظام مصطفى إكسبريس - أونلاين")
    with st.form("login"):
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة السر", type="password")
        if st.form_submit_button("دخول"):
            if u == "admin" and p == "123":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة")
else:
    st.sidebar.success("✅ متصل بجوجل درايف")
    df = load_data_from_drive()
    
    menu = st.sidebar.selectbox("القائمة", ["لوحة الإحصائيات", "البحث وتحديث الحالة"])

    if menu == "لوحة الإحصائيات":
        st.title("📊 التقارير المالية (مباشر من الدرايف)")
        if not df.empty:
            # تنظيف البيانات لضمان الحسابات
            df['سعر المستلم'] = pd.to_numeric(df['سعر المستلم'], errors='coerce').fillna(0)
            df['الشحن'] = pd.to_numeric(df['الشحن'], errors='coerce').fillna(0)
            
            actual_count = len(df[df['الكود'].notna()]) # عدد الشغل الفعلي
            total_net = df['سعر المستلم'].sum() - df['الشحن'].sum()
            
            c1, c2 = st.columns(2)
            c1.metric("عدد الشحنات الحقيقي", f"{actual_count}")
            c2.metric("إجمالي الصافي", f"{total_net:,.2f} ج.م")
            
            st.divider()
            st.subheader("📍 صافي الحسابات لكل محافظة")
            
            # تجميع البيانات حسب المحافظة
            prov_stats = df.groupby('المحافظه').agg({'سعر المستلم':'sum', 'الشحن':'sum'}).reset_index()
            prov_stats['الصافي'] = prov_stats['سعر المستلم'] - prov_stats['الشحن']
            
            # عرض الجدول
            st.table(prov_stats)
            
            # عرض جدول البيانات بالكامل تحت للتأكد
            st.subheader("📋 سجل البيانات بالكامل")
            st.dataframe(df)
        else:
            st.error("⚠️ لم يتم استلام بيانات. تأكد من أن ملف الإكسل (Sharing) معمول 'Anyone with the link'.")

    elif menu == "البحث وتحديث الحالة":
        st.title("🔍 استعلام سريع")
        q = st.text_input("ابحث بالاسم أو الموبايل أو الكود")
        if not df.empty:
            res = df[df.astype(str).apply(lambda x: q.lower() in x.str.lower().values, axis=1)]
            st.dataframe(res)
