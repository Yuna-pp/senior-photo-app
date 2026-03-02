import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import datetime
import os

st.set_page_config(page_title="相册助手", layout="centered")
st.title("📸 父母专属相册加字助手")

# 1. 侧边栏：大爷大妈的操作台
st.sidebar.header("⚙️ 调整文字设置")
location = st.sidebar.text_input("1. 输入地点 (Location):", "北京")
date_choice = st.sidebar.date_input("2. 选择日期 (Date):", datetime.date.today())

# 增加字号上限到 2000，解决“看不见”的问题
font_size = st.sidebar.slider("3. 字的大小 (Font Size):", 50, 2000, 400)
text_color = st.sidebar.color_picker("4. 字的颜色 (Text Color):", "#FFFF00")

# 2. 上传照片
uploaded_file = st.file_uploader("请上传照片:", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # 动态调整位置滑块的范围
    pos_x = st.sidebar.slider("左右位置:", 0, width, int(width * 0.5))
    pos_y = st.sidebar.slider("上下位置:", 0, height, int(height * 0.8))

    display_text = f"{date_choice} {location}"

    # 3. 核心修复：加载咱们自己带的字体
    font_path = "ziti.ttf"
    if os.path.exists(font_path):
        # 只要找到了这个文件，字号大小就绝对管用！
        font = ImageFont.truetype(font_path, font_size)
    else:
        st.error("⚠️ 还没找到 font.ttf 字体文件，请去 GitHub 上传！")
        font = ImageFont.load_default()

    # 画字
    draw.text((pos_x, pos_y), display_text, fill=text_color, font=font)

    # 显示大图
    st.image(img, caption="预览效果 (满意后长按保存)", use_column_width=True)
    st.success("处理成功！长按上方大图保存到手机。")
