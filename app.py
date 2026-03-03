import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ExifTags import TAGS, GPSTAGS
import datetime
import os
from pillow_heif import register_heif_opener

register_heif_opener()

st.set_page_config(page_title="相册助手", layout="centered")
st.title("📸 老人相册助手（稳如泰山版）")

# --- 核心函数：提取 GPS 原始坐标 ---
def get_gps_info(image):
    try:
        exif = image.getexif()
        if exif:
            for tag, value in exif.items():
                if TAGS.get(tag) == 'GPSInfo':
                    gps_data = {}
                    for t in value:
                        sub_tag = GPSTAGS.get(t, t)
                        gps_data[sub_tag] = value[t]
                    return gps_data
    except:
        pass
    return None

def get_accurate_date(image):
    try:
        exif = image.getexif()
        if exif:
            for tag_id, value in exif.items():
                if TAGS.get(tag_id) in ["DateTimeOriginal", "DateTime"]:
                    date_str = str(value)[:10].replace(":", "-")
                    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        pass
    return None

# --- 侧边栏 ---
st.sidebar.header("⚙️ 第一步：文字设置")

# 这里保留手动输入，因为这样大爷大妈才能写“埃及看大金字塔”
location = st.sidebar.text_input("1. 手动输入地点:", "埃及金字塔") 

color_options = {"亮黄色 (Yellow)": "#FFFF00", "纯白色 (White)": "#FFFFFF", "大红色 (Red)": "#FF0000", "黑色 (Black)": "#000000"}
selected_color = color_options[st.sidebar.selectbox("2. 选择颜色:", list(color_options.keys()))]
font_size = st.sidebar.slider("3. 字的大小:", 50, 1000, 300)

uploaded_file = st.file_uploader("第二步：上传照片", type=["jpg", "png", "jpeg", "heic", "HEIC"])

if uploaded_file:
    raw_img = Image.open(uploaded_file)
    img = ImageOps.exif_transpose(raw_img)
    
    # 探测坐标
    gps_info = get_gps_info(img)
    if gps_info:
        st.sidebar.info("📍 探测到照片自带 GPS 坐标，由于未连接地图服务器，请在上方手动填入地名。")
    
    detected_date = get_accurate_date(img)
    final_date = st.sidebar.date_input("4. 日期:", detected_date if detected_date else datetime.date.today())

    # 绘图逻辑保持不变...
    draw = ImageDraw.Draw(img)
    w, h = img.size
    pos_x = st.sidebar.slider("左右位置:", 0, w, int(w * 0.1))
    pos_y = st.sidebar.slider("上下移动:", 0, h, int(h * 0.8))
    display_text = f"{final_date} {location}"

    try:
        font = ImageFont.truetype("font.ttf", font_size)
    except:
        font = ImageFont.load_default()

    draw.text((pos_x, pos_y), display_text, fill=selected_color, font=font, stroke_width=int(font_size/12), stroke_fill="#000000")
    st.image(img, use_container_width=True)
    
