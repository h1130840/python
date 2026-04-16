import streamlit as st
import json
import os
import time
import uuid

# --- 資料處理功能 ---
DATA_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                tasks = json.load(f)
                for t in tasks:
                    if 'id' not in t:
                        t['id'] = str(uuid.uuid4())
                return tasks
            except:
                return []
    return []

def save_tasks(tasks):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

# --- 網頁配置 ---
st.set_page_config(page_title="番茄鐘工作法", page_icon="🍅", layout="centered")

st.title("🍅 個人化番茄鐘與任務看板")
st.markdown("---")

# 初始化任務與計時器資料
if 'tasks' not in st.session_state:
    st.session_state.tasks = load_tasks()
if 'time_left' not in st.session_state:
    st.session_state.time_left = 25 * 60
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# ==========================================
# 區塊一：番茄鐘計時 
# ==========================================
st.subheader("⏱️ 專注時間")

# 設定區
col_mins, col_btns = st.columns([1, 1], vertical_alignment="bottom")
with col_mins:
    input_mins = st.number_input("設定專注時間 (分鐘)", min_value=1, value=25)
    # 如果手動更改了分數且計時器沒在跑，就更新剩餘時間
    if not st.session_state.is_running and st.session_state.time_left != input_mins * 60:
        st.session_state.time_left = input_mins * 60

with col_btns:
    c1, c2, c3 = st.columns(3)
    # 開始/繼續按鈕
    if c1.button("▶️ 開始"):
        st.session_state.is_running = True
    # 暫停按鈕
    if c2.button("⏸️ 暫停"):
        st.session_state.is_running = False
    # 重設按鈕
    if c3.button("🔄 重設"):
        st.session_state.is_running = False
        st.session_state.time_left = input_mins * 60


m, s = divmod(st.session_state.time_left, 60)

timer_html = f"""
    <div style='text-align: center;'>
        <h1 style='color: #000000; font-size: 150px; margin: 20px 0;'>{m:02d}:{s:02d}</h1>
    </div>
"""
st.markdown(timer_html, unsafe_allow_html=True)

# 進度條
progress = st.progress(0.0)
total_duration = input_mins * 60
if total_duration > 0:
    current_progress = 1.0 - (st.session_state.time_left / total_duration)
    progress.progress(min(max(current_progress, 0.0), 1.0))

# 計時邏輯：當狀態為「正在運行」且「還有時間」時
if st.session_state.is_running and st.session_state.time_left > 0:
    time.sleep(1)
    st.session_state.time_left -= 1
    st.rerun()  # 強制重新渲染網頁以更新數字

# 時間到提醒
if st.session_state.time_left == 0 and st.session_state.is_running:
    st.session_state.is_running = False
    st.balloons()
    st.success(f"時間到！已專注 {mins} 分鐘。")

st.markdown("---")

# ==========================================
# 區塊二：任務輸入
# ==========================================
st.subheader("📝 任務管理")

new_task = st.text_input("輸入待辦事項", placeholder="例如：完成作業...")
if st.button("➕ 新增任務", use_container_width=True):
    if new_task:
        st.session_state.tasks.append({"id": str(uuid.uuid4()), "name": new_task, "done": False})
        save_tasks(st.session_state.tasks)
        st.rerun()

st.write("") 

# ==========================================
# 區塊三：分欄顯示任務清單
# ==========================================
col_pending, col_completed = st.columns(2)

with col_pending:
    st.markdown("### ⏳ 進行中")
    for i, task in enumerate(st.session_state.tasks):
        if not task['done']:
            inner_col1, inner_col2 = st.columns([0.15, 0.85], vertical_alignment="center")
            is_checked = inner_col1.checkbox("", value=task['done'], key=f"check_{task['id']}")
            if is_checked != task['done']:
                st.session_state.tasks[i]['done'] = is_checked
                save_tasks(st.session_state.tasks)
                st.rerun()
            inner_col2.write(task['name'])

with col_completed:
    st.markdown("### ✅ 已完成")
    for i, task in enumerate(st.session_state.tasks):
        if task['done']:
            inner_col1, inner_col2, inner_col3 = st.columns([0.15, 0.65, 0.2], vertical_alignment="center")
            is_checked = inner_col1.checkbox("", value=task['done'], key=f"check_{task['id']}")
            if is_checked != task['done']:
                st.session_state.tasks[i]['done'] = is_checked
                save_tasks(st.session_state.tasks)
                st.rerun()
            inner_col2.write(task['name'])
            if inner_col3.button("🗑️", key=f"del_{task['id']}"):
                st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                save_tasks(st.session_state.tasks)
                st.rerun()

# ==========================================
# 區塊四：底部操作區
# ==========================================
st.markdown("---") 

if st.button("🧹 清除所有已完成任務", use_container_width=True):
    st.session_state.tasks = [t for t in st.session_state.tasks if not t['done']]
    save_tasks(st.session_state.tasks)
    st.rerun()
