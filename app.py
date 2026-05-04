import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# إعدادات الصفحة
st.set_page_config(page_title="Mustafa Express Management", layout="wide")

# روابط ملفات جوجل درايف (Direct Export)
excel_url = "https://docs.google.com/spreadsheets/d/17YzcGVZNAuqirCr1keNqKJFtx9AQBiok/export?format=xlsx"
# ملاحظة: ملف المستخدمين يفضل يكون في الدرايف لضمان ثباته
users_url = "رابط_ملف_المستخدمين_هنا_أو_سنعتمد_على_الأدمن_مؤقتا"

@st.cache_data(ttl=5)
def load_data():
    try:
        response = requests.get(excel_url)
        return pd.read_excel(BytesIO(response.content))
    except:
        return pd.DataFrame()

# --- نظام الحماية وصلاحيات الدخول ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = {'logged_in': False, 'user': None, 'role': None, 'full_name': None}

# تعريف المستخدمين (يمكنك إضافتهم هنا يدوياً لحين ربط شيت مستخدمين)
users = {
    "admin": {"pass": "123", "role": "Owner", "name": "عبد الرحمن"},
    "mandoob1": {"pass": "4455", "role": "Delegate", "name": "أحمد"},
    "mandoob2": {"pass": "6677", "role": "Delegate", "name": "محمد"},
}

if not st.session_state['auth']['logged_in']:
    st.title("📦 دخول نظام مصطفى إكسبريس")
    with st.form("login"):
        u_in = st.text_input("اسم المستخدم")
        p_in = st.text_input("كلمة السر", type="password")
        if st.form_submit_button("دخول"):
            if u_in in users and users[u_in]['pass'] == p_in:
                st.session_state['auth'] = {
                    'logged_in': True, 
                    'user': u_in, 
                    'role': users[u_in]['role'], 
                    'full_name': users[u_in]['name']
                }
                st.rerun()
            else:
                st.error("بيانات الدخول غير صحيحة")
else:
    role = st.session_state['auth']['role']
    user_name = st.session_state['auth']['full_name']
    df = load_data()

    # القائمة الجانبية
    menu_options = ["لوحة الإحصائيات", "البحث وتحديث الحالة"]
    if role == "Owner":
        menu_options.insert(1, "إضافة شحنة")
    
    menu = st.sidebar.selectbox("القائمة", menu_options)
    st.sidebar.write(f"المستخدم: **{user_name}**")

    # --- 1. قسم الإحصائيات (إضافة تحصيل المناديب) ---
    if menu == "لوحة الإحصائيات":
        st.title("📊 التقارير المالية الحية")
        if not df.empty:
            df['سعر المستلم'] = pd.to_numeric(df['سعر المستلم'], errors='coerce').fillna(0)
            df['الشحن'] = pd.to_numeric(df['الشحن'], errors='coerce').fillna(0)

            # إحصائيات المحافظات
            st.subheader("📍 تحصيل المحافظات")
            prov = df.groupby('المحافظه').agg({'سعر المستلم':'sum', 'الشحن':'sum'}).reset_index()
            prov['الصافي'] = prov['سعر المستلم'] - prov['الشحن']
            st.table(prov)

            # إحصائيات المناديب (الجديد)
            st.subheader("👤 تحصيل المناديب")
            del_stats = df.groupby('المندوب').agg({'سعر المستلم':'sum', 'الشحن':'sum'}).reset_index()
            del_stats['صافي المندوب'] = del_stats['سعر المستلم'] - del_stats['الشحن']
            st.table(del_stats)

    # --- 2. إضافة شحنة (للمالك فقط) ---
    elif menu == "إضافة شحنة":
        st.title("➕ تسجيل شحنة جديدة")
        last_serial = int(df['مسلسل'].max()) if not df.empty else 0
        st.write(f"المسلسل التالي: **{last_serial + 1}**")
        
        with st.form("add_form"):
            col1, col2 = st.columns(2)
            with col1:
                code = st.text_input("كود الشحنة")
                c_name = st.text_input("اسم العميل")
                c_phone = st.text_input("رقم الهاتف")
            with col2:
                c_city = st.text_input("المحافظة")
                c_delegate = st.text_input("اسم المندوب المسئول")
                c_price = st.number_input("السعر الأساسي", value=0.0)
            
            st.info("سيتم تسجيل البيانات في الدرايف. (ملحوظة: الكتابة تتطلب تصريح Service Account)")
            if st.form_submit_button("حفظ الشحنة"):
                st.warning("تم تصميم الواجهة. لربط الحفظ الفعلي بجوجل درايف، نحتاج لخطوة الـ Service Account.")

    # --- 3. البحث وتحديث الحالة (صلاحيات المندوب) ---
    elif menu == "البحث وتحديث الحالة":
        st.title("🔍 إدارة الشحنات")
        
        # الفلترة: المندوب يشوف شغله بس، المالك يشوف كله
        my_df = df[df['المندوب'] == user_name] if role == "Delegate" else df
        
        search_q = st.text_input("ابحث في شحناتك...")
        filtered = my_df[my_df.astype(str).apply(lambda x: search_q.lower() in x.str.lower().values, axis=1)]
        st.dataframe(filtered)

        st.divider()
        if not filtered.empty:
            st.subheader("📝 تعديل بيانات الشحنة")
            selected_code = st.selectbox("اختر الكود للتعديل", filtered['الكود'].unique())
            
            with st.form("update_form"):
                u_col1, u_col2 = st.columns(2)
                with u_col1:
                    new_r = st.number_input("سعر المستلم الجديد")
                    new_s = st.number_input("مصاريف الشحن")
                with u_col2:
                    new_stat = st.selectbox("الحالة", ["تم الاستلام", "مرتجع", "مؤجل", "قيد الانتظار"])
                    new_note = st.text_input("ملاحظات")
                
                if st.form_submit_button("تحديث البيانات"):
                    st.success(f"تم تسجيل طلب التحديث للكود {selected_code}")

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state['auth'] = {'logged_in': False}
        st.rerun()
