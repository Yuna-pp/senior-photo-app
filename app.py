import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ExifTags import TAGS
import datetime
import os
from pillow_heif import register_heif_opener

# 启动 HEIC 转换器
register_heif_opener()

st.set_page_config(page_title="父母相册助手", layout="centered")
st.title("老人相册助手")

# --- 优化后的日期抓取函数 ---
def get_original_date(image):
    try:
        exif = image._getexif()
        if exif:
            for tag_id, value in exif.items():
                tag_name = TAGS.get(tag_id, tag_id)
                # 兼容多种可能的日期标签
                if tag_name in ["DateTimeOriginal", "DateTimeDigitized", "DateTime"]:
                    # 转换格式: "2025:10:07 15:33:00" -> "2025-10-07"
                    date_str = str(value)[:10].replace(":", "-")
                    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        pass
    # 彻底删除硬编码的 2026-01-04，改为默认今天
    return datetime.date.today()

# --- 侧边栏设置 ---
st.sidebar.header("⚙️ 文字设置")

# 地点默认设为空，提醒用户输入真实地点
location = st.sidebar.text_input("1. 手动输入地点:", placeholder="例如：俄罗斯堪察加")

color_options = {
    "亮黄色 (Yellow)": "#FFFF00", "纯白色 (White)": "#FFFFFF",
    "大红色 (Red)": "#FF0000", "草绿色 (Green)": "#00FF00",
    "紫色 (Purple)": "#800080", "深蓝色 (Blue)": "#0000FF", "黑色 (Black)": "#000000"
}
selected_color = color_options[st.sidebar.selectbox("2. 选择颜色:", list(color_options.keys()))]
font_size = st.sidebar.slider("3. 字的大小:", 50, 1000, 300)

uploaded_file = st.file_uploader("上传照片 (支持 HEIC)", type=["jpg", "png", "jpeg", "heic", "HEIC"])

if uploaded_file:
    try:
        raw_img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(raw_img)
        
        # 自动获取日期
        detected_date = get_original_date(img)
        # 用户可以在日历里微调
        final_date = st.sidebar.date_input("4. 确认日期:", detected_date)

        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        st.sidebar.header("📍 位置微调")
        pos_x = st.sidebar.slider("左右位置:", 0, w, int(w * 0.1))
        pos_y = st.sidebar.slider("上下位置:", 0, h, int(h * 0.8))

        # 拼接文字
        display_text = f"{final_date} {location}"

        try:
            font = ImageFont.truetype("font.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # 画带黑边的字
        draw.text(
            (pos_x, pos_y), 
            display_text, 
            fill=selected_color, 
            font=font,
            stroke_width=int(font_size/15),
            stroke_fill="#000000"
        )
        
        st.image(img, caption="预览效果", use_container_width=True)
        st.success("这回日期应该准了！记得在左边改一下地名哦。")
        
    except Exception as e:
        st.error(f"处理失败: {e}")
