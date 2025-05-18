
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import io
import zipfile
import os

st.title("🎓 مولد شهادات التقدير")

# Upload certificate template image
template_file = st.file_uploader("📄 ارفع صورة شهادة التقدير (PNG أو JPG)", type=["png", "jpg", "jpeg"])

# Upload names file
names_file = st.file_uploader("📋 ارفع ملف الأسماء (TXT أو Excel)", type=["txt", "csv", "xlsx"])

# Font size input
font_size = st.number_input("🔠 حجم الخط", min_value=10, max_value=100, value=50)

# Position input
x_pos = st.number_input("📍 الموقع الأفقي لكتابة الاسم (X)", min_value=0, value=520)
y_pos = st.number_input("📍 الموقع الرأسي لكتابة الاسم (Y)", min_value=0, value=250)

# Generate button
if st.button("🚀 إنشاء الشهادات"):
    if not template_file or not names_file:
        st.error("يرجى رفع صورة الشهادة وملف الأسماء أولاً.")
    else:
        # Read names
        try:
            if names_file.name.endswith(".txt"):
                names = names_file.read().decode("utf-8").splitlines()
                names = [n.strip() for n in names if n.strip()]
            else:
                df = pd.read_excel(names_file) if names_file.name.endswith(".xlsx") else pd.read_csv(names_file)
                names = df.iloc[:, 0].dropna().astype(str).tolist()
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة الأسماء: {e}")
            names = []

        # Prepare output zip
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for name in names:
                with Image.open(template_file).convert("RGB") as im:
                    draw = ImageDraw.Draw(im)
                    try:
                        font = ImageFont.truetype("arialbd.ttf", font_size)
                    except:
                        font = ImageFont.load_default()

                    text_width = draw.textlength(name, font=font)
                    draw.text((x_pos - text_width / 2, y_pos), name, font=font, fill="black")

                    output_img = io.BytesIO()
                    im.save(output_img, format="PNG")
                    zip_file.writestr(f"{name}.png", output_img.getvalue())

        zip_buffer.seek(0)
        st.success(f"تم إنشاء {len(names)} شهادة بنجاح!")
        st.download_button("⬇️ تحميل الشهادات كملف ZIP", data=zip_buffer, file_name="certificates.zip")
