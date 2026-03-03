import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import datetime
import os
from pillow_heif import register_heif_opener
from PIL.ExifTags import TAGS

# 1. 基础环境配置
register_heif_opener()
st.set_page_config(page_title="相册助手（稳如泰山版）", layout="centered")

# --- 核心函数：精准抓取日期 ---
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

st.title("📸 相册助手（稳如泰山版）")

# --- 第一步：上传图片 (放在最上方) ---
uploaded_file = st.file_uploader(
    "第一步：点击下方按钮上传照片", 
    type=["jpg", "jpeg", "png", "heic", "heif", "dng", "JPG", "JPEG", "PNG", "HEIC", "HEIF", "DNG"]
)

# 预留图片显示区域
image_placeholder = st.empty()

if uploaded_file:
    try:
        # 基础图片处理
        raw_img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(raw_img)
        w, h = img.size

        # --- 第二步：图片下方输入区 ---
        st.subheader("⚙️ 基础设置")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            location = st.text_input("地点 (不填不显示):", "")
        with col2:
            font_size = st.number_input("字的大小:", 50, 1500, 100)
        with col3:
            detected_date = get_accurate_date(img)
            final_date = st.date_input("确认日期:", detected_date if detected_date else datetime.date.today())

        # --- 第三步：侧边栏优化功能 (颜色、位置) ---
        st.sidebar.header("🎨 高级优化选项")
        color_options = {"亮黄色": "#FFFF00", "纯白色": "#FFFFFF", "大红色": "#FF0000", "黑色": "#000000"}
        selected_color = color_options[st.sidebar.selectbox("选择文字颜色:", list(color_options.keys()))]
        
        st.sidebar.divider()
        st.sidebar.write("📍 微调文字位置")
        pos_x = st.sidebar.slider("左右挪动:", 0, w, int(w * 0.1))
        pos_y = st.sidebar.slider("上下挪动:", 0, h, int(h * 0.8))

        # --- 绘图与渲染 ---
        display_text = f"{final_date} {location}" if location.strip() else f"{final_date}"
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("font.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # 执行绘制 (无描边极简版)
        draw.text((pos_x, pos_y), display_text, fill=selected_color, font=font)
        
        # 将处理好的图片推送到顶部的占位符
        image_placeholder.image(img, caption="预览效果 (满意后长按保存)", use_container_width=True)
        st.success("调整下方参数，图片会实时更新！")
        
    except Exception as e:
        st.error(f"处理出错了: {e}")
else:
    st.info("请先上传照片，上传后会自动显示调整选项。")
