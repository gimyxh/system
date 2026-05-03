# 1. تثبيت المكتبات
!pip install -q streamlit
!npm install -g localtunnel

import os

# 2. كود النظام (نسخة إدارة المناديب والخصوصية)
app_code = """
import streamlit as st
import pandas as pd
import os

# إعدادات الصفحة
st.set_page_config(page_title="Mustafa Express Management", layout="wide")

# مسارات الملفات على الدرايف
db_path = '/content/drive/MyDrive/MySystem/shipping_data.xlsx'
users_path = '/content/drive/MyDrive/MySystem/users.xlsx'

# دالة تحميل البيانات
def load_data(path, columns):
    if os.path.exists(path):
        df = pd.read_excel(path)
        return df
    return pd.DataFrame(columns=columns)

# --- نظام الحماية المطور ---
# حفظ حالة الدخول في المتصفح (عشان م يطلبش الباسورد مع كل ريفريش طول ما التاب مفتوح)
if 'auth' not in st.session_state:
    st.session_state['auth'] = {'logged_in': False, 'user': None, 'role': None}

# التأكد من وجود جدول مستخدمين (لو مش موجود بنعمل حساب الأدمن الافتراضي)
users_df = load_data(users_path, ['username', 'password', 'role', 'name'])
if users_df.empty:
    users_df = pd.DataFrame([['admin', '123', 'Owner', 'عبد الرحمن']], columns=['username', 'password', 'role', 'name'])
    users_df.to_excel(users_path, index=False)

def login():
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
                st.error("خطأ في البيانات، حاول تاني")

if not st.session_state['auth']['logged_in']:
    login()
else:
    # --- واجهة النظام بعد الدخول ---
    role = st.session_state['auth']['role']
    user_full_name = st.session_state['auth']['name']
    
    st.sidebar.success(f"مرحباً: {user_full_name}")
    
    # تحديد القائمة حسب الصلاحية
    options = ["لوحة الإحصائيات", "إضافة شحنة", "البحث وتحديث الحالة"]
    if role == "Owner":
        options.append("إدارة المناديب ⚙️")
    
    menu = st.sidebar.selectbox("القائمة", options)
    df = load_data(db_path, ['مسلسل', 'الكود', 'الاسم', 'الرقم', 'المحافظه', 'العنوان', 'الشركه الراسله', 'السعر', 'سعر المستلم', 'الشحن', 'الحاله', 'الملاحظات', 'المندوب'])

    # --- إدارة المناديب (لصاحب السيستم فقط) ---
    if menu == "إدارة المناديب ⚙️":
        st.title("👥 إضافة وإدارة حسابات المناديب")
        with st.form("add_user"):
            new_u = st.text_input("اسم المستخدم الجديد (بالانجليزي)")
            new_p = st.text_input("كلمة السر")
            new_n = st.text_input("اسم المندوب الفعلي")
            new_r = st.selectbox("الصلاحية", ["Delegate", "Owner"])
            if st.form_submit_button("إنشاء الحساب"):
                new_user = pd.DataFrame([[new_u, new_p, new_r, new_n]], columns=users_df.columns)
                updated_users = pd.concat([users_df, new_user], ignore_index=True)
                updated_users.to_excel(users_path, index=False)
                st.success(f"تم عمل حساب لـ {new_n} بنجاح!")
        
        st.write("### المستخدمين الحاليين")
        st.table(users_df[['username', 'role', 'name']])

    # --- لوحة الإحصائيات ---
    elif menu == "لوحة الإحصائيات":
        st.title("📊 التقارير المالية")
        actual_count = df[df['الكود'].notna()].shape[0]
        total_net = pd.to_numeric(df['سعر المستلم'], errors='coerce').sum() - pd.to_numeric(df['الشحن'], errors='coerce').sum()
        
        c1, c2 = st.columns(2)
        c1.metric("العدد الفعلي", f"{actual_count}")
        c2.metric("إجمالي الصافي", f"{total_net:,.2f} ج.م")
        
        st.divider()
        province_stats = df.groupby('المحافظه').agg({'سعر المستلم': 'sum', 'الشحن': 'sum'}).reset_index()
        province_stats['الصافي'] = province_stats['سعر المستلم'] - province_stats['الشحن']
        st.table(province_stats)

    # --- إضافة شحنة ---
    elif menu == "إضافة شحنة":
        st.title("➕ تسجيل شحنة")
        with st.form("add_form"):
            col1, col2 = st.columns(2)
            with col1:
                serial = st.text_input("المسلسل")
                code = st.text_input("الكود")
                name = st.text_input("الاسم")
                phone = st.text_input("الرقم")
            with col2:
                city = st.text_input("المحافظة")
                r_price = st.number_input("سعر المستلم", value=0.0)
                s_price = st.number_input("الشحن", value=0.0)
                # لو مندوب، اسمه ينزل تلقائي
                delegate_val = user_full_name if role == "Delegate" else st.text_input("المندوب")
            
            if st.form_submit_button("حفظ"):
                new_row = pd.DataFrame([[serial, code, name, phone, city, "", "", 0, r_price, s_price, "قيد الانتظار", "", delegate_val]], columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_excel(db_path, index=False)
                st.success("تم التسييف!")

    # --- البحث والتعديل ---
    elif menu == "البحث وتحديث الحالة":
        st.title("🔍 البحث والتعديل")
        search = st.text_input("ابحث هنا...")
        # المندوب يشوف شحناته بس؟ (ممكن نفعلها لو حبيت)
        display_df = df if role == "Owner" else df[df['المندوب'] == user_full_name]
        filtered = display_df[display_df.astype(str).apply(lambda x: search.lower() in x.str.lower().values, axis=1)]
        st.dataframe(filtered)
        
        st.divider()
        if not filtered.empty:
            target_codes = filtered['الكود'].unique().tolist()
            sel_code = st.selectbox("اختر الكود للتعديل", target_codes)
            new_stat = st.selectbox("الحالة", ["قيد الانتظار", "تم الاستلام", "مرتجع", "مؤجل"])
            if st.button("تحديث"):
                df.loc[df['الكود'] == sel_code, 'الحاله'] = new_stat
                df.to_excel(db_path, index=False)
                st.success("تم التحديث!")
                st.rerun()

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state['auth'] = {'logged_in': False, 'user': None, 'role': None}
        st.rerun()
"""

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

# 3. التشغيل
import urllib
print("الرقم السري لفك النفق:")
print(urllib.request.urlopen('https://ident.me').read().decode('utf8'))
!streamlit run app.py & npx localtunnel --port 8501
