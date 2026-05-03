import streamlit as st
import pandas as pd
import os

# إعدادات الصفحة
st.set_page_config(page_title="Mustafa Express Management", layout="wide")

# ملاحظة هامة: عند التشغيل أونلاين، سنحتاج لربط Google Drive بطريقة "السرية" 
# ولكن لتجربة الواجهة الآن، سنفترض وجود الملفات محلياً
db_path = 'shipping_data.xlsx'
users_path = 'users.xlsx'

# دالة تحميل البيانات
def load_data(path, columns):
    if os.path.exists(path):
        return pd.read_excel(path)
    return pd.DataFrame(columns=columns)

# --- نظام الحماية ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = {'logged_in': False, 'user': None, 'role': None}

# تحميل المستخدمين
users_df = load_data(users_path, ['username', 'password', 'role', 'name'])
if users_df.empty:
    users_df = pd.DataFrame([['admin', '123', 'Owner', 'عبد الرحمن']], columns=['username', 'password', 'role', 'name'])

if not st.session_state['auth']['logged_in']:
    st.title("📦 دخول نظام مصطفى إكسبريس")
    with st.form("login_form"):
        user_input = st.text_input("اسم المستخدم")
        pass_input = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("دخول"):
            user_data = users_df[users_df['username'] == user_input]
            if not user_data.empty and str(user_data.iloc[0]['password']) == pass_input:
                st.session_state['auth'] = {
                    'logged_in': True, 
                    'user': user_input, 
                    'role': user_data.iloc[0]['role'],
                    'name': user_data.iloc[0]['name']
                }
                st.rerun()
            else:
                st.error("خطأ في البيانات")
else:
    # القائمة والوظائف (باقي الكود الذي قمت بتجربته سابقاً)
    role = st.session_state['auth']['role']
    st.sidebar.success(f"مرحباً: {st.session_state['auth']['name']}")
    
    menu = st.sidebar.selectbox("القائمة", ["لوحة الإحصائيات", "إضافة شحنة", "البحث وتحديث الحالة", "إدارة المناديب ⚙️"])
    
    st.info("السيستم الآن يعمل على السيرفر الأونلاين. جاري ربط قاعدة بيانات الدرايف...")
