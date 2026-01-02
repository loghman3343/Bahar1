
import streamlit as st
import pandas as pd
import random

# تنظیمات اصلی صفحه (Full Width)
st.set_page_config(page_title="سامانه جامع مدیریت بهار ۱", layout="wide")

# طراحی اختصاصی CSS برای شبیه‌سازی دقیق پورتال دانشگاه علوم پزشکی
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn&display=swap');
    * { font-family: 'Vazirmatn', sans-serif; direction: rtl; }
    .stApp { background-color: #f0f2f5; }
    
    /* سایدبار تیره مشابه عکس ارسالی */
    [data-testid="stSidebar"] { background-color: #2c3e50 !important; border-left: 1px solid #1e2b37; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* کارت‌های رنگی داشبورد */
    .dashboard-card {
        padding: 20px;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* استایل بخش‌بندی تنظیمات */
    .ward-container {
        background: white;
        padding: 25px;
        border-radius: 12px;
        border-right: 8px solid #3498db;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .shift-header {
        font-weight: bold;
        padding: 5px 15px;
        border-radius: 5px;
        color: white;
        display: inline-block;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# مدیریت حافظه (Session State)
if "wards" not in st.session_state: st.session_state.wards = {}
if "staff" not in st.session_state: st.session_state.staff = {}

# ==================== منوی کناری (Sidebar) ====================
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🌐 پورتال مدیریت</h2>", unsafe_allow_html=True)
    st.divider()
    # استفاده از رادیو باتن ساده برای جلوگیری از ارور کتابخانه‌های نصب نشده
    menu = st.radio("انتخاب عملیات:", 
                    ["📊 داشبورد سیستم", "🏢 پیکربندی بخش‌ها", "👥 ثبت پرسنل", "📅 خروجی نهایی"],
                    index=1) # پیش‌فرض روی تنظیمات بخش
    st.divider()
    st.write("🆔 نسخه سامانه: 2.0.1")

# ==================== صفحه ۱: داشبورد عملکرد ====================
if menu == "📊 داشبورد سیستم":
    st.title("📊 داشبورد نظارتی حضور و غیاب")
    
    # کارت‌های رنگی مشابه عکس ارسالی شما
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="dashboard-card" style="background-color: #e74c3c;"><b>۴۴:۳۷</b><br>تأخیر کل</div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="dashboard-card" style="background-color: #e67e22;"><b>۱۱:۰۵</b><br>تعجیل خروج</div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="dashboard-card" style="background-color: #27ae60;"><b>۱۶۸ روز</b><br>حضور فعال</div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="dashboard-card" style="background-color: #2980b9;"><b>۴۹:۵۳</b><br>اضافه کار</div>', unsafe_allow_html=True)

    st.subheader("📆 نمای وضعیت تردد روزانه")
    # شبیه‌سازی تقویم رنگی
    grid_cols = st.columns(10)
    for i in range(1, 31):
        grid_cols[(i-1)%10].info(f"روز {i}")

# ==================== صفحه ۲: تنظیمات بخش‌ها (خواسته اصلی شما) ====================
elif menu == "🏢 پیکربندی بخش‌ها":
    st.title("🏢 مدیریت بخش‌ها و ظرفیت جنسیتی")
    
    # افزودن بخش جدید
    with st.container():
        col_w1, col_w2 = st.columns([3, 1])
        w_input = col_w1.text_input("نام بخش جدید را وارد کنید (مثلاً: اورژانس):", key="new_w_input")
        if col_w2.button("➕ افزودن بخش"):
            if w_input and w_input not in st.session_state.wards:
                st.session_state.wards[w_input] = {
                    "morn": {"f": 0, "m": 0}, 
                    "eve": {"f": 0, "m": 0}, 
                    "night": {"f": 0, "m": 0}
                }
                st.rerun()

    st.divider()

    # نمایش و تنظیم هر بخش
    for w_name, config in list(st.session_state.wards.items()):
        st.markdown(f"<div class='ward-container'>", unsafe_allow_html=True)
        h1, h2 = st.columns([5, 1])
        h1.subheader(f"📍 تنظیمات بخش: {w_name}")
        if h2.button("🗑️ حذف کل بخش", key=f"del_{w_name}"):
            del st.session_state.wards[w_name]
            st.rerun()

        # تنظیم سه شیفت
        s1, s2, s3 = st.columns(3)
        
        with s1:
            st.markdown("<span class='shift-header' style='background-color:#f1c40f; color:black;'>☀️ شیفت صبح</span>", unsafe_allow_html=True)
            config["morn"]["f"] = st.number_input(f"تعداد خانم (صبح) - {w_name}", 0, 15, value=config["morn"]["f"], key=f"mf_{w_name}")
            config["morn"]["m"] = st.number_input(f"تعداد آقا (صبح) - {w_name}", 0, 15, value=config["morn"]["m"], key=f"mm_{w_name}")
            
        with s2:
            st.markdown("<span class='shift-header' style='background-color:#2ecc71'>🌆 شیفت عصر</span>", unsafe_allow_html=True)
            config["eve"]["f"] = st.number_input(f"تعداد خانم (عصر) - {w_name}", 0, 15, value=config["eve"]["f"], key=f"ef_{w_name}")
            config["eve"]["m"] = st.number_input(f"تعداد آقا (عصر) - {w_name}", 0, 15, value=config["eve"]["m"], key=f"em_{w_name}")
            
        with s3:
            st.markdown("<span class='shift-header' style='background-color:#34495e'>🌙 شیفت شب</span>", unsafe_allow_html=True)
            config["night"]["f"] = st.number_input(f"تعداد خانم (شب) - {w_name}", 0, 15, value=config["night"]["f"], key=f"nf_{w_name}")
            config["night"]["m"] = st.number_input(f"تعداد آقا (شب) - {w_name}", 0, 15, value=config["night"]["m"], key=f"nm_{w_name}")
            
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== صفحه ۳: ثبت پرسنل ====================
elif menu == "👥 ثبت پرسنل":
    st.title("👥 مدیریت بانک اطلاعاتی پرسنل")
    with st.form("staff_reg"):
        c1, c2, c3 = st.columns([3, 2, 1])
        p_name = c1.text_input("نام و نام خانوادگی:")
        p_gen = c2.selectbox("جنسیت:", ["خانم", "آقا"])
        if c3.form_submit_button("ثبت در سیستم"):
            if p_name:
                st.session_state.staff[p_name] = {"gen": p_gen, "shifts": 0}
                st.rerun()
    
    if st.session_state.staff:
        df = pd.DataFrame([{"نام": k, "جنسیت": v["gen"]} for k, v in st.session_state.staff.items()])
        st.table(df)

# ==================== صفحه ۴: خروجی نهایی ====================
elif menu == "📅 خروجی نهایی":
    st.title("📅 تولید برنامه عملیاتی")
    days = st.number_input("تعداد روزهای ماه:", 1, 31, 30)
    
    if st.button("🚀 شروع فرآیند چیدمان هوشمند"):
        if not st.session_state.wards or not st.session_state.staff:
            st.error("❌ ابتدا بخش‌ها و پرسنل را تنظیم کنید.")
        else:
            for s in st.session_state.staff.values(): s["shifts"] = 0
            
            for w_name, w_cfg in st.session_state.wards.items():
                st.subheader(f"✅ برنامه نهایی بخش: {w_name}")
                plan_data = []
                for d in range(1, days + 1):
                    row = {"تاریخ": f"1404/10/{d:02d}"}
                    avail = list(st.session_state.staff.keys())
                    random.shuffle(avail)
                    
                    for sk, sl in [("morn", "صبح"), ("eve", "عصر"), ("night", "شب")]:
                        f_req, m_req = w_cfg[sk]["f"], w_cfg[sk]["m"]
                        selected = []
                        # انتخاب خانم‌ها
                        f_pool = [n for n in avail if st.session_state.staff[n]["gen"] == "خانم"]
                        for _ in range(f_req):
                            if f_pool: p = f_pool.pop(0); selected.append(p); avail.remove(p)
                        # انتخاب آقایان
                        m_pool = [n for n in avail if st.session_state.staff[n]["gen"] == "آقا"]
                        for _ in range(m_req):
                            if m_pool: p = m_pool.pop(0); selected.append(p); avail.remove(p)
                        row[sl] = " / ".join(selected) if selected else "---"
                    plan_data.append(row)
                
                df_res = pd.DataFrame(plan_data)
                st.dataframe(df_res, use_container_width=True)
                st.download_button(f"📥 دریافت فایل اکسل {w_name}", df_res.to_csv(index=False).encode('utf-8-sig'), f"{w_name}.csv")
