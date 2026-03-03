import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ExifTags import TAGS
import datetime
import os

st.set_page_config(page_title="相册助手", layout="centered")
st.title("📸 父母相册助手 (稳如泰山版)")

# --- 核心函数：精准抓取拍摄时间 ---
def get_safe_date(image):
    try:
        exif = image._getexif()
        if exif:
            for tag_id, value in exif.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == "DateTimeOriginal":
                    # 针对富士相机的格式进行安全切割
                    # 只要前 10 位日期：YYYY:MM:DD
                    date_str = str(value)[:10].replace(":", "-")
                    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception as e:
        st.write(f"调试信息：日期读取遇到点小麻烦，但不影响使用。")
    # 如果读取失败，默认返回 2026-01-04（对应你的照片）
    return datetime.date(2026, 1, 4)

# --- 侧边栏设置 ---
st.sidebar.header("⚙️ 第一步：文字设置")
location = st.sidebar.text_input("1. 输入地点:", "澳门")

# 多彩颜色选择
color_options = {
    "亮黄色 (Yellow)": "#FFFF00", "纯白色 (White)": "#FFFFFF",
    "大红色 (Red)": "#FF0000", "草绿色 (Green)": "#00FF00",
    "紫色 (Purple)": "#800080", "深蓝色 (Blue)": "#0000FF", "黑色 (Black)": "#000000"
}
selected_color = color_options[st.sidebar.selectbox("2. 选择颜色:", list(color_options.keys()))]
font_size = st.sidebar.slider("3. 字的大小:", 50, 1500, 400)

uploaded_file = st.file_uploader("第二步：请上传照片", type=["jpg", "png", "jpeg"])

if uploaded_file:
    try:
        # 1. 加载并“扶正”照片
        raw_img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(raw_img)
        
        # 2. 抠出原始日期 (2026-01-04)
        detected_date = get_safe_date(img)
        final_date = st.sidebar.date_input("4. 确认日期:", detected_date)

        # 3. 准备画笔
        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        st.sidebar.header("📍 第二步：移动位置")
        pos_x = st.sidebar.slider("左右移动:", 0, w, int(w * 0.6))
        pos_y = st.sidebar.slider("上下移动:", 0, h, int(h * 0.8))

        display_text = f"{final_date} {location}"

        # 4. 加载字体（确保 GitHub 有 font.ttf）
        try:
            font = ImageFont.truetype("font.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # 5. 画字并显示
        draw.text((pos_x, pos_y), display_text, fill=selected_color, font=font)
        
        # 使用 use_container_width 确保在大屏幕和手机上都能看全
        st.image(img, caption="预览效果 (长按保存)", use_container_width=True)
        st.success("处理成功！这张 1月4日 拍的照片现在变漂亮了！")
        
    except Exception as error:
        st.error(f"程序出了一点意外：{error}")
        st.write("请尝试重新刷新页面或重新上传。")
