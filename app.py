import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ExifTags import TAGS
import datetime
import os
# --- NEW: Import HEIC support ---
# --- 新增：导入 HEIC 格式支持 ---
from pillow_heif import register_heif_opener

# Start the HEIC "translator"
# 启动 HEIC “翻译官”
register_heif_opener()

st.set_page_config(page_title="父母相册助手", layout="centered")
st.title("📸 父母相册助手 (V2.4 苹果兼容版)")

# --- Function: Get Original Date ---
def get_safe_date(image):
    try:
        exif = image._getexif()
        if exif:
            for tag_id, value in exif.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == "DateTimeOriginal":
                    # Parse Jan 4, 2026 format
                    date_str = str(value)[:10].replace(":", "-")
                    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        pass
    return datetime.date(2026, 1, 4) # Default fallback

# --- Sidebar: User Controls ---
st.sidebar.header("⚙️ 第一步：文字设置")
location = st.sidebar.text_input("1. 输入地点:", "澳门")

color_options = {
    "亮黄色 (Yellow)": "#FFFF00", "纯白色 (White)": "#FFFFFF",
    "大红色 (Red)": "#FF0000", "草绿色 (Green)": "#00FF00",
    "紫色 (Purple)": "#800080", "深蓝色 (Blue)": "#0000FF", "黑色 (Black)": "#000000"
}
selected_color = color_options[st.sidebar.selectbox("2. 选择颜色:", list(color_options.keys()))]
font_size = st.sidebar.slider("3. 字的大小:", 50, 1000, 300)

# --- Updated File Uploader: Added heic support ---
# --- 更新上传器：增加了 heic 支持 ---
uploaded_file = st.file_uploader("第二步：上传照片 (支持苹果 HEIC 格式)", type=["jpg", "png", "jpeg", "heic", "HEIC"])

if uploaded_file:
    try:
        raw_img = Image.open(uploaded_file)
        # Fix orientation [cite: 2026-02-26]
        img = ImageOps.exif_transpose(raw_img)
        
        detected_date = get_safe_date(img)
        final_date = st.sidebar.date_input("4. 确认日期:", detected_date)

        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        st.sidebar.header("📍 第二步：位置微调")
        pos_x = st.sidebar.slider("左右移动:", 0, w, int(w * 0.1))
        pos_y = st.sidebar.slider("上下移动:", 0, h, int(h * 0.8))

        display_text = f"{final_date} {location}"

        # Load Font (Ensure font.ttf is in GitHub!)
        try:
            font = ImageFont.truetype("font.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Draw with black outline for visibility [cite: 2026-02-26]
        draw.text(
            (pos_x, pos_y), 
            display_text, 
            fill=selected_color, 
            font=font,
            stroke_width=int(font_size/15),
            stroke_fill="#000000"
        )
        
        st.image(img, caption="预览效果 (满意后长按保存)", use_container_width=True)
        st.success("苹果 HEIC 格式也搞定啦！")
        
    except Exception as e:
        st.error(f"坏了，还是打不开: {e}")
