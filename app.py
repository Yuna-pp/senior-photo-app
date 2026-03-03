import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ExifTags import TAGS
import datetime
import os
from pillow_heif import register_heif_opener

# 启动 HEIF/HEIC 格式支持 (涵盖苹果和新型安卓机)
register_heif_opener()

st.set_page_config(page_title="父母相册助手", layout="centered")
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
        
        # 深度扫描元数据
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

# 1. 地点设置：默认空着，用户不填就不显示
location = st.sidebar.text_input("1. 输入地点 (不填则不显示):", "") 

color_options = {
    "亮黄色 (Yellow)": "#FFFF00", "纯白色 (White)": "#FFFFFF",
    "大红色 (Red)": "#FF0000", "草绿色 (Green)": "#00FF00",
    "紫色 (Purple)": "#800080", "深蓝色 (Blue)": "#0000FF", "黑色 (Black)": "#000000"
}
selected_color = color_options[st.sidebar.selectbox("2. 选择颜色:", list(color_options.keys()))]
font_size = st.sidebar.slider("3. 字的大小:", 50, 1000, 300)

# 2. 增强型上传器：加入了更多安卓常见的格式后缀
# RAW 格式通常非常大，建议提醒父母尽量上传普通照片
uploaded_file = st.file_uploader(
    "第二步：上传照片 (支持所有手机格式)", 
    type=["jpg", "jpeg", "png", "heic", "heif", "dng", "JPG", "JPEG", "PNG", "HEIC", "HEIF", "DNG"]
)

if uploaded_file:
    try:
        raw_img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(raw_img)
        
        detected_date = get_accurate_date(img)
        final_date = st.sidebar.date_input("4. 确认日期:", detected_date if detected_date else datetime.date.today())

        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        st.sidebar.header("📍 第二步：位置微调")
        pos_x = st.sidebar.slider("左右位置:", 0, w, int(w * 0.1))
        pos_y = st.sidebar.slider("上下位置:", 0, h, int(h * 0.8))

        # 拼接逻辑：如果地点为空，则只显示日期
        if location.strip():
            display_text = f"{final_date} {location}"
        else:
            display_text = f"{final_date}"

        try:
            font = ImageFont.truetype("font.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # --- 核心修改：已完全移除描边 (stroke)，回归极简 ---
        draw.text(
            (pos_x, pos_y), 
            display_text, 
            fill=selected_color, 
            font=font
        )
        
        st.image(img, caption="预览效果 (满意后长按保存)", use_container_width=True)
        st.success("调整完成！快去分享给给朋友们吧~")
        
    except Exception as e:
        st.error(f"抱歉，这类照片格式比较特殊，处理失败: {e}")
