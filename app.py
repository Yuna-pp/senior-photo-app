import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import datetime
from pillow_heif import register_heif_opener
from PIL.ExifTags import TAGS

# 1. 基础配置
register_heif_opener()
st.set_page_config(page_title="父母相册助手", layout="centered")

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

st.title("📸 父母相册助手 (V3.3 性能优化版)")

# --- 第一步：上传图片 (始终在最上方) ---
uploaded_file = st.file_uploader(
    "第一步：请先上传照片", 
    type=["jpg", "jpeg", "png", "heic", "heif", "dng"]
)

if uploaded_file:
    # 2. 预处理图片
    raw_img = Image.open(uploaded_file)
    img_to_show = ImageOps.exif_transpose(raw_img)
    w, h = img_to_show.size
    
    # --- 第二步：表单控制区 (核心修改：引入 st.form) ---
    # 使用表单包裹所有参数，防止“动一下闪一下” [cite: 2026-02-26]
    with st.form("my_settings_form"):
        st.subheader("⚙️ 调整参数 (全部选好后再点下方确认)")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            location = st.text_input("地点:", "")
        with col2:
            font_size = st.number_input("字的大小:", 50, 1500, 300)
        with col3:
            detected_date = get_accurate_date(img_to_show)
            final_date = st.date_input("日期:", detected_date if detected_date else datetime.date.today())

        # 侧边栏放入表单内，同样实现“批量提交”
        st.sidebar.header("🎨 样式与位置")
        color_options = {"亮黄色": "#FFFF00", "纯白色": "#FFFFFF", "大红色": "#FF0000", "黑色": "#000000"}
        selected_color = color_options[st.sidebar.selectbox("选择颜色:", list(color_options.keys()))]
        
        pos_x = st.sidebar.slider("左右挪动:", 0, w, int(w * 0.1))
        pos_y = st.sidebar.slider("上下挪动:", 0, h, int(h * 0.8))
        
        # 核心按钮：点它才会触发图片刷新 [cite: 2026-02-26]
        submit_button = st.form_submit_button("✅ 确认修改并生成图片")

    # 3. 绘图与显示逻辑
    if submit_button or 'img_processed' not in st.session_state:
        # 执行绘图
        draw = ImageDraw.Draw(img_to_show)
        display_text = f"{final_date} {location}" if location.strip() else f"{final_date}"
        
        try:
            font = ImageFont.truetype("font.ttf", font_size)
        except:
            font = ImageFont.load_default()

        draw.text((pos_x, pos_y), display_text, fill=selected_color, font=font)
        st.session_state.img_processed = img_to_show

    # 显示结果
    st.image(st.session_state.img_processed, caption="满意后长按保存", use_container_width=True)
    st.success("调整下方参数后，请点击红色的‘确认修改’按钮查看新效果。")

else:
    st.info("请先上传照片。")
