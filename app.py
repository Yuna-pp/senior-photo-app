import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ExifTags import TAGS
import datetime
import os
from pillow_heif import register_heif_opener

# 启动 HEIC 格式支持
register_heif_opener()

st.set_page_config(page_title="相册助手", layout="centered")
st.title("📸 相册助手（稳如泰山版）")

def get_accurate_date(image):
    try:
        exif = image.getexif()
        if exif:
            for tag_id, value in exif.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name in ["DateTimeOriginal", "DateTime"]:
                    date_str = str(value)[:10].replace(":", "-")
                    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # 尝试深度扫描
        info = image.info
        if 'exif' in info:
            exif_raw = image._getexif()
            if exif_raw:
                for tag_id, value in exif_raw.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    if tag_name == "DateTimeOriginal":
                        date_str = str(value)[:10].replace(":", "-")
                        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        pass
    return None

# --- 侧边栏设置 ---
st.sidebar.header("⚙️ 第一步：文字设置")

# 1. 地点默认为空，不填写则不显示
location = st.sidebar.text_input("1. 手动输入地点 (可留空):", "") 

color_options = {
    "亮黄色 (Yellow)": "#FFFF00", "纯白色 (White)": "#FFFFFF",
    "大红色 (Red)": "#FF0000", "草绿色 (Green)": "#00FF00",
    "紫色 (Purple)": "#800080", "深蓝色 (Blue)": "#0000FF", "黑色 (Black)": "#000000"
}
selected_color = color_options[st.sidebar.selectbox("2. 选择颜色:", list(color_options.keys()))]
font_size = st.sidebar.slider("3. 字的大小:", 50, 1000, 300)

uploaded_file = st.file_uploader("第二步：上传照片", type=["jpg", "png", "jpeg", "heic", "HEIC"])

if uploaded_file:
    try:
        raw_img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(raw_img)
        
        detected_date = get_accurate_date(img)
        
        if detected_date:
            final_date = st.sidebar.date_input("4. 自动检测到日期:", detected_date)
        else:
            final_date = st.sidebar.date_input("4. 未检测到日期，请手动选择:", datetime.date.today())

        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        st.sidebar.header("📍 第二步：位置微调")
        pos_x = st.sidebar.slider("左右位置:", 0, w, int(w * 0.1))
        pos_y = st.sidebar.slider("上下移动:", 0, h, int(h * 0.8))

        # 拼接文字：如果地点为空，只显示日期
        if location.strip():
            display_text = f"{final_date} {location}"
        else:
            display_text = f"{final_date}"

        try:
            font = ImageFont.truetype("font.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # --- 已移除描边代码，字体更显简洁 ---
        draw.text(
            (pos_x, pos_y), 
            display_text, 
            fill=selected_color, 
            font=font
        )
        
        st.image(img, caption="预览效果 (长按保存)", use_container_width=True)
        st.success("调整完成！满意的话就分享给朋友们吧")
        
    except Exception as e:
        st.error(f"处理出错: {e}")
