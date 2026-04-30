import streamlit as st
import json
import os
import time
import uuid

# 資料處理功能
DATA_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                tasks = json.load(f)
                for t in tasks:
                    if 'id' not in t: t['id'] = str(uuid.uuid4())
                return tasks
            except:
                return []
    return []

def save_tasks(tasks):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

def add_new_task():
    if st.session_state.task_input_box: 
        st.session_state.tasks.append({
            "id": str(uuid.uuid4()), 
            "name": st.session_state.task_input_box, 
            "done": False
        })
        save_tasks(st.session_state.tasks)
        st.session_state.task_input_box = "" 

# 網頁與樣式配置
st.set_page_config(page_title="個人化番茄鐘與任務看板", page_icon="🍅", layout="wide")

st.markdown("""
<style>
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background: linear-gradient(135deg, #0B101E 0%, #1B1833 50%, #0F172A 100%);
    }

    .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp label, .stApp span {
        color: #F8FAFC !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(12px);
        padding: 10px;
        height: 100%;
    }

    div[data-testid="metric-container"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 15px 0;
        text-align: center;
    }
    div[data-testid="metric-container"] label {
        color: #94A3B8 !important; 
    }
    div[data-testid="metric-container"] div {
        color: #38BDF8 !important; 
        font-weight: 800;
    }

    .stButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #E2E8F0 !important;
        border-radius: 10px !important;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: #38BDF8 !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.3) !important;
        transform: translateY(-2px);
    }

    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(90deg, #3B82F6 0%, #8B5CF6 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: bold;
    }
    .stButton > button[data-testid="baseButton-primary"]:hover {
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.5) !important;
        filter: brightness(1.1);
    }

    .premium-timer {
        text-align: center;
        font-size: 90px;
        font-weight: 800;
        background: linear-gradient(to right, #38BDF8, #818CF8, #C084FC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        font-family: 'Courier New', Courier, monospace;
        letter-spacing: 2px;
        filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.3));
    }

    .stTextInput > div > div > input, .stNumberInput > div > div > input {
        background-color: rgba(0, 0, 0, 0.2) !important;
        color: #E2E8F0 !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px;
    }
    .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 0 1px #8B5CF6 !important;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #38BDF8, #8B5CF6) !important;
    }
</style>
""", unsafe_allow_html=True)

# 初始化資料
if 'tasks' not in st.session_state:
    st.session_state.tasks = load_tasks()
if 'time_left' not in st.session_state:
    st.session_state.time_left = 25 * 60
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'task_input_box' not in st.session_state:
    st.session_state.task_input_box = ""
if 'prev_mins' not in st.session_state:  # 記錄上一次設定的分鐘數
    st.session_state.prev_mins = 25

st.title("🍅 個人化番茄鐘與任務看板")

col_left, col_right = st.columns(2, gap="large")

# 番茄鐘計時器
with col_left:
    with st.container(border=True):
        st.subheader("⏱️ 專注計時")
        
        col_ctrl, col_timer = st.columns([1, 2], vertical_alignment="center")
        
        with col_ctrl:
            input_mins = st.number_input("設定分鐘", min_value=1, value=st.session_state.prev_mins)
            
            if input_mins != st.session_state.prev_mins:
                st.session_state.time_left = input_mins * 60
                st.session_state.prev_mins = input_mins
                st.session_state.is_running = False
            
            c1, c2 = st.columns(2)
            if c1.button("▶️ 開始", type="primary", use_container_width=True): 
                st.session_state.is_running = True
            if c2.button("⏸️ 暫停", use_container_width=True): 
                st.session_state.is_running = False
            if st.button("🔄 重置", use_container_width=True):
                st.session_state.is_running = False
                st.session_state.time_left = input_mins * 60
                st.rerun()

        with col_timer:
            mm, ss = divmod(st.session_state.time_left, 60)
            st.markdown(f"<div class='premium-timer'>{mm:02d}:{ss:02d}</div>", unsafe_allow_html=True)
            
        total_sec = input_mins * 60
        current_progress = 1.0 - (st.session_state.time_left / total_sec) if total_sec > 0 else 0.0
        st.progress(min(max(current_progress, 0.0), 1.0))
        st.write("")
        st.write("")
    if st.session_state.is_running and st.session_state.time_left > 0:
        time.sleep(1)
        st.session_state.time_left -= 1
        st.rerun()
    elif st.session_state.time_left == 0 and st.session_state.is_running:
        st.session_state.is_running = False
        st.balloons()
        st.success(f"時間到！已專注 {input_mins} 分鐘。")


# 任務管理 
with col_right:
    with st.container(border=True):
        st.subheader("📝 任務管理")
        
        done_count = sum(1 for t in st.session_state.tasks if t['done'])
        total_count = len(st.session_state.tasks)
        m1, m2, m3 = st.columns(3)
        m1.metric("今日任務", total_count)
        m2.metric("已完成", done_count)
        m3.metric("達成率", f"{int(done_count/total_count*100) if total_count>0 else 0}%")
        
        st.divider() 
        
        col_in, col_btn = st.columns([4, 1], vertical_alignment="bottom")
        col_in.text_input("新增待辦事項", placeholder="輸入後點擊新增", label_visibility="collapsed", key="task_input_box", on_change=add_new_task)
        col_btn.button("➕ 新增", type="primary", use_container_width=True, on_click=add_new_task)

        st.write("") 
        
        col_pending, col_completed = st.columns(2)
        
        with col_pending:
            st.markdown("#### ⏳ 進行中")
            for i, task in enumerate(st.session_state.tasks):
                if not task['done']:
                    ic1, ic2 = st.columns([0.2, 0.8], vertical_alignment="center")
                    if ic1.checkbox("", value=False, key=f"chk_{task['id']}"):
                        st.session_state.tasks[i]['done'] = True
                        save_tasks(st.session_state.tasks)
                        st.rerun()
                    ic2.write(task['name'])

        with col_completed:
            st.markdown("#### ✅ 已完成")
            for i, task in enumerate(st.session_state.tasks):
                if task['done']:
                    ic1, ic2, ic3 = st.columns([0.15, 0.65, 0.2], vertical_alignment="center")
                    if not ic1.checkbox("", value=True, key=f"chk_{task['id']}"):
                        st.session_state.tasks[i]['done'] = False
                        save_tasks(st.session_state.tasks)
                        st.rerun()
                    ic2.write(f"<span style='color: #888 !important;'>{task['name']}</span>", unsafe_allow_html=True)
                    if ic3.button("🗑️", key=f"del_{task['id']}"):
                        st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                        save_tasks(st.session_state.tasks)
                        st.rerun()
                        
        st.write("") 
        
        if st.button("🧹 一鍵清除所有已完成任務", use_container_width=True):
            st.session_state.tasks = [t for t in st.session_state.tasks if not t['done']]
            save_tasks(st.session_state.tasks)
            st.rerun()
