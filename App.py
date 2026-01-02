
import streamlit as st
import pandas as pd
import random

# تنظیمات ظاهری سایت
st.set_page_config(page_title="سامانه جامع بهار ۱", layout="wide")

# طراحی گرافیکی اختصاصی (CSS) برای شبیه‌سازی سیستم‌های بیمارستانی
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn&display=swap');
    * { font-family: 'Vazirmatn', sans-serif; direction: rtl; }
    .main { background-color: #f4f6f9; }
    
    /* استایل منوی کناری */
    [data-testid="stSidebar"] { background-color: #232e3c !important; color: white; }
    
    /* کارت‌های داشبورد رنگی */
    .card { padding: 20px; border-radius: 10px; color: white; margin-bottom: 10px; text-align: center; font-weight: bold; }
    .bg-red { background-color: #e74c3c; }
    .bg-green { background-color: #27ae60; }
    .bg-orange { background-color: #f39c12; }
    .bg-blue { background-color: #2980b9; }
    
    /* استایل تنظیمات بخش */
    .ward-box { background: white; padding: 20px; border-radius: 15px; border-right: 10px solid #2980b9; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .shift-tag { padding: 5px 15px; border-radius: 20px; color: white; font-size: 14px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- مدیریت حافظه موقت ---
if "wards" not in st.session_state: st.session_state.wards = {}
if "staff" not in st.session_state: st.session_state.staff = {}

# ==================== منوی کناری (Sidebar) ====================
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🏥 پنل MIS بهار</h2>", unsafe_allow_html=True)
    st.divider()
    page = st.radio("🏠 منوی دسترسی سریع", 
                    ["📊 داشبورد عملکرد", "🏢 تعریف بخش و ظرفیت", "👥 لیست پرسنل", "📋 تولید برنامه نهایی"])
    st.divider()
    st.write("📍 واحد: مدیریت فناوری اطلاعات")

# ==================== ۱. داشبورد (شبیه عکسی که فرستادی) ====================
if page == "📊 داشبورد عملکرد":
    st.title("📊 داشبورد نظارتی")
    
    # کارت‌های رنگی شبیه به تصویر ارسالی شما
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="card bg-red">۴۴:۳۷<br>تأخیر کل</div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="card bg-orange">۱۱:۰۵<br>تعجیل خروج</div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="card bg-green">۱۶۸ روز<br>حضور ماهانه</div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="card bg-blue">۴۹:۵۳<br>اضافه کار</div>', unsafe_allow_html=True)

    st.subheader("📆 نمای وضعیت حضور روزانه")
    days_mock = [random.choice(["✅", "❌", "🌙", "🏥"]) for _ in range(30)]
    cols = st.columns(15)
    for i, icon in enumerate(days_mock):
        cols[i % 15].metric(f"روز {i+1}", icon)

# ==================== ۲. تنظیمات بخش (دقیقاً طبق خواسته شما) ====================
elif page == "🏢 تعریف بخش و ظرفیت":
    st.title("🏢 مدیریت بخش‌ها و نیاز جنسیتی")
    
    with st.container():
        cw1, cw2 = st.columns([3, 1])
        new_ward = cw1.text_input("نام بخش جدید:", placeholder="مثلاً: اورژانس")
        if cw2.button("➕ ثبت بخش جدید"):
            if new_ward:
                st.session_state.wards[new_ward] = {
                    "morn": {"f": 0, "m": 0}, "eve": {"f": 0, "m": 0}, "night": {"f": 0, "m": 0}
                }
                st.rerun()

    st.divider()

    for w, cfg in list(st.session_state.wards.items()):
        st.markdown(f"<div class='ward-box'>", unsafe_allow_html=True)
        h1, h2 = st.columns([5, 1])
        h1.subheader(f"📍 تنظیمات ظرفیت: {w}")
        if h2.button("🗑️ حذف", key=f"d_{w}"):
            del st.session_state.wards[w]
            st.rerun()

        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown("<span class='shift-tag' style='background:#f1c40f'>☀️ صبح</span>", unsafe_allow_html=True)
            cfg["morn"]["f"] = st.number_input(f"تعداد خانم (صبح)-{w}", 0, 15, cfg["morn"]["f"])
            cfg["morn"]["m"] = st.number_input(f"تعداد آقا (صبح)-{w}", 0, 15, cfg["morn"]["m"])
        with s2:
            st.markdown("<span class='shift-tag' style='background:#2ecc71'>🌆 عصر</span>", unsafe_allow_html=True)
            cfg["eve"]["f"] = st.number_input(f"تعداد خانم (عصر)-{w}", 0, 15, cfg["eve"]["f"])
            cfg["eve"]["m"] = st.number_input(f"تعداد آقا (عصر)-{w}", 0, 15, cfg["eve"]["m"])
        with s3:
            st.markdown("<span class='shift-tag' style='background:#2c3e50'>🌙 شب</span>", unsafe_allow_html=True)
            cfg["night"]["f"] = st.number_input(f"تعداد خانم (شب)-{w}", 0, 15, cfg["night"]["f"])
            cfg["night"]["m"] = st.number_input(f"تعداد آقا (شب)-{w}", 0, 15, cfg["night"]["m"])
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== ۳. مدیریت پرسنل ====================
elif page == "👥 لیست پرسنل":
    st.title("👥 مدیریت بانک اطلاعاتی پرسنل")
    with st.form("staff_form"):
        c1, c2, c3 = st.columns([3, 2, 1])
        name = c1.text_input("نام و نام خانوادگی:")
        gen = c2.selectbox("جنسیت:", ["خانم", "آقا"])
        if c3.form_submit_button("ثبت عضو"):
            if name: st.session_state.staff[name] = {"gen": gen, "shifts": 0}
            st.rerun()

    if st.session_state.staff:
        st.table(pd.DataFrame([{"نام": k, "جنسیت": v["gen"]} for k, v in st.session_state.staff.items()]))

# ==================== ۴. تولید برنامه (شبیه عکس دوم شما) ====================
elif page == "📋 تولید برنامه نهایی":
    st.title("📋 برنامه عملیاتی بخش‌ها")
    days = st.number_input("تعداد روزهای ماه:", 1, 31, 30)
    
    if st.button("🚀 شروع پردازش و چیدمان هوشمند"):
        if not st.session_state.wards or not st.session_state.staff:
            st.error("❌ ابتدا بخش‌ها و پرسنل را تعریف کنید.")
        else:
            for s in st.session_state.staff.values(): s["shifts"] = 0
            
            for w_name, w_cfg in st.session_state.wards.items():
                st.subheader(f"✅ برنامه بخش: {w_name}")
                plan = []
                for d in range(1, days + 1):
                    row = {"روز": d}
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
                    plan.append(row)
                
                df_res = pd.DataFrame(plan)
                st.dataframe(df_res, use_container_width=True)
                st.download_button(f"📥 دریافت اکسل {w_name}", df_res.to_csv(index=False).encode('utf-8-sig'), f"{w_name}.csv")

