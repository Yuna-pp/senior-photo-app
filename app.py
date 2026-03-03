import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import datetime
import io
import base64
from pillow_heif import register_heif_opener
from PIL.ExifTags import TAGS

register_heif_opener()
st.set_page_config(page_title="父母相册助手", layout="centered")

# --- 1. CSS 优化：缩紧间距但不拥挤，解决布局问题 ---
st.markdown("""
    <style>
    /* 强力锁定界面间距：紧凑而不拥挤 */
    div[data-testid="stVerticalBlock"] > div { margin-top: -15px !important; }
    /* 给输入组件留点呼吸空间，防止挤在一起 */
    .stNumberInput, .stTextInput, .stDateInput { margin-top: -10px !important; margin-bottom: 5px !important; }
    /* 针对手机端的滑块位置微调 */
    .stSlider { padding-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_and_fix_image(file):
    raw_img = Image.open(file)
    full_img = ImageOps.exif_transpose(raw_img)
    return full_img

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

def get_image_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=95)
    return base64.b64encode(buffered.getvalue()).decode()

st.title("📸 父母相册助手 (稳如泰山版)")

uploaded_file = st.file_uploader("第一步：上传照片", type=["jpg", "jpeg", "png", "heic", "heif", "dng"])

# --- 2. 核心黑科技：在上方挖个“坑”先占位 ---
# 这个占位符将确保处理好的图片出现在设置按钮的上方
image_placeholder = st.empty()

if uploaded_file:
    full_img = load_and_fix_image(uploaded_file)
    w_full, h_full = full_img.size

    st.sidebar.header("🎨 样式与精确位置")
    color_options = {"亮黄色": "#FFFF00", "纯白色": "#FFFFFF", "大红色": "#FF0000", "黑色": "#000000"}
    selected_color = color_options[st.sidebar.selectbox("文字颜色:", list(color_options.keys()))]
    
    # 滑块仍然在侧边栏，保留伸缩功能
    pos_x = st.sidebar.slider("左右挪动:", 0, w_full, int(w_full * 0.1))
    pos_y = st.sidebar.slider("上下挪动:", 0, h_full, int(h_full * 0.8))

    # --- 3. 设置区 (依然在图片的下方) ---
    # 我们不在主区域用 columns 了，改为垂直排列，给大爷大妈更大的操作空间，防止拥挤
    st.subheader("⚙️ 调整文字信息")
    location = st.text_input("地点 (不填不显示):", "")
    font_size = st.number_input("字的大小 (手机端建议300-600):", 50, 2000, 400)
    detected_date = get_accurate_date(full_img)
    final_date = st.date_input("日期确认 (不准可改):", detected_date if detected_date else datetime.date.today())

    # --- 4. 绘图与渲染逻辑 ---
    display_text = f"{final_date} {location}" if location.strip() else f"{final_date}"
    processed_img = full_img.copy()
    draw = ImageDraw.Draw(processed_img)
    try:
        font = ImageFont.truetype("font.ttf", font_size)
    except:
        font = ImageFont.load_default()
    draw.text((pos_x, pos_y), display_text, fill=selected_color, font=font)

    # Base64 处理，解决微信 0B 保存问题
    img_base64 = get_image_base64(processed_img)
    
    # --- 核心修复：将处理好的图片塞回上方的占位符里 ---
    # 这样图片就在设置按钮的上面了
    # 我们还在 HTML 标签里限制了间距，防止再次出现“跑马地”
    image_placeholder.markdown(
        f'<img src="data:image/jpeg;base64,{img_base64}" style="width:100%; margin-bottom: 10px;">',
        unsafe_allow_html=True
    )
    
    st.success("✅ 处理完成！")
    st.info("直接长按保存即可。")

else:
    st.info("请先上传照片。上传后会自动在下方显示调整选项。")
