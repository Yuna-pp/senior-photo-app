import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ExifTags import TAGS
import datetime
import os
from pillow_heif import register_heif_opener

# 启动全平台格式支持
register_heif_opener()

st.set_page_config(page_title="父母相册助手", layout="centered")

# --- 样式优化：让界面更清爽 ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📸 父母相册助手 (V3.1 零障碍版)")
st.write("第一步：先设置文字，第二步：上传照片")

# --- 函数：读取日期 ---
def get_accurate_date(image):
    try:
        exif = image.getexif()
        if exif:
            for tag_id, value in exif.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name in ["DateTimeOriginal", "DateTime"]:
                    date_str = str(value)[:10].replace(":", "-")
                    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        pass
    return None

# --- 直接在主页面平铺设置区 (取消 st.sidebar) ---
with st.container():
    st.subheader("⚙️ 第一步：文字设置")
    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input("1. 输入地点 (不填不显示):", "")
        color_options = {"亮黄色": "#FFFF00", "纯白色": "#FFFFFF", "大红色": "#FF0000", "黑色": "#000000"}
        selected_color = color_options[st.selectbox("2. 选择颜色:", list(color_options.keys()))]
    with col2:
        font_size = st.slider("3. 字的大小:", 50, 1000, 300)
        # 日期选择也放在这里
        final_date_manual = st.date_input("4. 确认日期 (不准可改):", datetime.date.today())

st.divider()

# --- 第二步：上传照片 ---
uploaded_file = st.file_uploader(
    "第二步：点击下方按钮上传照片", 
    type=["jpg", "jpeg", "png", "heic", "heif", "dng", "JPG", "JPEG", "PNG", "HEIC", "HEIF", "DNG"]
)

if uploaded_file:
    try:
        raw_img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(raw_img)
        
        # 尝试自动修正日期
        detected_date = get_accurate_date(img)
        # 如果自动读到了日期，就用自动的，否则用上面手动选的
        date_to_use = detected_date if detected_date else final_date_manual

        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        st.subheader("📍 第三步：微调位置并保存")
        # 位置滑块也直接放在主页面
        pos_x = st.slider("左右移动:", 0, w, int(w * 0.1))
        pos_y = st.slider("上下移动:", 0, h, int(h * 0.8))

        display_text = f"{date_to_use} {location}" if location.strip() else f"{date_to_use}"

        try:
            font = ImageFont.truetype("font.ttf", font_size)
        except:
            font = ImageFont.load_default()

        draw.text((pos_x, pos_y), display_text, fill=selected_color, font=font)
        
        st.image(img, caption="满意后长按下方图片保存", use_container_width=True)
        st.success("大功告成！快去分享给朋友们吧")
        
    except Exception as e:
        st.error(f"处理失败了，请换一张照片试试: {e}")
