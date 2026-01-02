
import streamlit as st
import pandas as pd
import random

# ------------------ تنظیمات صفحه ------------------
st.set_page_config(
    page_title="داشبورد مدیریتی بهار ۱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------ CSS ------------------
st.markdown("""
<style>
.main { background-color: #f8f9fa; }
.stMetric { background-color: #ffffff; padding: 15px; border-radius: 15px;
box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #1e3c72; }
.request-card { background-color: #fff3cd; padding: 10px;
border-radius: 10px; border-right: 5px solid #ffc107; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# ------------------ Session State ------------------
if "login" not in st.session_state: st.session_state.login = False
if "staff" not in st.session_state: st.session_state.staff = {}
if "wards" not in st.session_state:
    st.session_state.wards = {
        "تریاژ": {"morn": 2, "eve": 2, "night": 2},
        "سرم تراپی": {"morn": 1, "eve": 1, "night": 2},
    }
if "final_df" not in st.session_state: st.session_state.final_df = None


# ================== موتور چیدمان ==================
def generate_schedule(staff, wards, days):
    for s in staff.values():
        s["total_shifts"] = 0

    last_night_day = {}
    rows = []

    for d in range(1, days + 1):
        day_row = {"تاریخ": f"روز {d}"}
        used_today = set()

        for ward, req in wards.items():
            for shift, key in [("صبح", "morn"), ("عصر", "eve"), ("شب", "night")]:
                needed = req[key]
                chosen = []

                for _ in range(needed):
                    eligible = []
                    for name, data in staff.items():
                        if name in used_today:
                            continue
                        if d in data["offs"]:
                            continue
                        if shift in data["day_prefs"].get(d, []):
                            continue
                        if shift == "شب" and d - last_night_day.get(name, 0) < 2:
                            continue
                        eligible.append(name)

                    if not eligible:
                        chosen.append("⚠️ کمبود")
                        continue

                    eligible.sort(key=lambda x: staff[x]["total_shifts"])
                    pick = eligible[0]

                    gender = "خ" if staff[pick]["gender"] == "خانم" else "آ"
                    chosen.append(f"{pick} ({gender})")

                    staff[pick]["total_shifts"] += 1
                    used_today.add(pick)
                    if shift == "شب":
                        last_night_day[pick] = d

                day_row[f"{ward}-{shift}"] = " / ".join(chosen)

        rows.append(day_row)

    return pd.DataFrame(rows)


# ================== ورود ==================
if not st.session_state.login:
    st.title("🏥 پنل مدیریت بیمارستان")
    u = st.text_input("نام کاربری")
    p = st.text_input("رمز عبور", type="password")
    if st.button("ورود"):
        if u == "admin" and p == "1234":
            st.session_state.login = True
            st.rerun()
else:
    st.title("🏥 سامانه برنامه‌ریزی هوشمند بهار")

    if st.button("خروج"):
        st.session_state.login = False
        st.rerun()

    # ---------- Metrics ----------
    c1, c2, c3 = st.columns(3)
    c1.metric("کل پرسنل", len(st.session_state.staff))
    c2.metric("بخش‌ها", len(st.session_state.wards))
    c3.metric("درخواست‌ها", sum(len(v["day_prefs"]) for v in st.session_state.staff.values()))

    # ---------- Tabs ----------
    t1, t2, t3, t4 = st.tabs([
        "👥 پرسنل",
        "🏖️ مرخصی",
        "⚙️ بخش‌ها",
        "📅 تولید برنامه"
    ])

    with t1:
        n = st.text_input("نام پرسنل")
        g = st.selectbox("جنسیت", ["خانم", "آقا"])
        if st.button("افزودن"):
            st.session_state.staff[n] = {
                "gender": g,
                "offs": [],
                "day_prefs": {},
                "total_shifts": 0
            }
            st.success("ثبت شد")

        if st.session_state.staff:
            df = pd.DataFrame([
                {"نام": k, "جنسیت": v["gender"], "شیفت": v["total_shifts"]}
                for k, v in st.session_state.staff.items()
            ])
            st.dataframe(df, use_container_width=True)

    with t2:
        if st.session_state.staff:
            p = st.selectbox("پرسنل", list(st.session_state.staff))
            days = st.multiselect("روزهای مرخصی", range(1, 32))
            if st.button("ذخیره"):
                st.session_state.staff[p]["offs"] = days

    with t3:
        for w, cfg in st.session_state.wards.items():
            st.subheader(w)
            cfg["morn"] = st.number_input("صبح", 0, 10, cfg["morn"], key=w+"m")
            cfg["eve"] = st.number_input("عصر", 0, 10, cfg["eve"], key=w+"e")
            cfg["night"] = st.number_input("شب", 0, 10, cfg["night"], key=w+"n")

    with t4:
        days = st.number_input("تعداد روز", 1, 31, 30)
        if st.button("🚀 تولید برنامه"):
            st.session_state.final_df = generate_schedule(
                st.session_state.staff,
                st.session_state.wards,
                days
            )
            st.balloons()

        if st.session_state.final_df is not None:
            st.dataframe(st.session_state.final_df, use_container_width=True)
            st.download_button(
                "دانلود CSV",
                st.session_state.final_df.to_csv(index=False).encode("utf-8-sig"),
                "schedule.csv"
            )
