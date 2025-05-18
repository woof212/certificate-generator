
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import io
import zipfile
import arabic_reshaper
from bidi.algorithm import get_display

st.title("🎓 مولد شهادات التقدير")

template_file = st.file_uploader("📄 ارفع صورة شهادة التقدير (PNG أو JPG)", type=["png", "jpg", "jpeg"])
names_file = st.file_uploader("📋 ارفع ملف الأسماء (TXT أو Excel)", type=["txt", "csv", "xlsx"])
font_size = st.number_input("🔠 حجم الخط", min_value=10, max_value=100, value=60)
x_pos = st.number_input("📍 الموقع الأفقي لكتابة الاسم (X)", min_value=0, value=520)
y_pos = st.number_input("📍 الموقع الرأسي لكتابة الاسم (Y)", min_value=0, value=250)

if st.button("🚀 إنشاء الشهادات"):
    if not template_file:
        st.error("يرجى رفع صورة الشهادة.")
    else:
        # Read names
        names = []
        if names_file:
            try:
                if names_file.name.endswith(".txt"):
                    names = names_file.read().decode("utf-8").splitlines()
                    names = [n.strip() for n in names if n.strip()]
                else:
                    df = pd.read_excel(names_file) if names_file.name.endswith(".xlsx") else pd.read_csv(names_file)
                    names = df.iloc[:, 0].dropna().astype(str).tolist()
            except Exception as e:
                st.error(f"حدث خطأ أثناء قراءة الأسماء: {e}")
        else:
            names = ["أحمد علي"]

        # Prepare output zip
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for name in names:
                reshaped_text = arabic_reshaper.reshape(name)
                bidi_text = get_display(reshaped_text)

                with Image.open(template_file).convert("RGB") as im:
                    draw = ImageDraw.Draw(im)
                    try:
                        font = ImageFont.truetype("arialbd.ttf", font_size)
                    except:
                        try:
                            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
                        except:
                            font = ImageFont.load_default()

                    text_width = draw.textlength(bidi_text, font=font)
                    draw.text((x_pos - text_width / 2, y_pos), bidi_text, font=font, fill="black")

                    output_img = io.BytesIO()
                    im.save(output_img, format="PNG")
                    zip_file.writestr(f"{name}.png", output_img.getvalue())

        zip_buffer.seek(0)
        st.success(f"تم إنشاء {len(names)} شهادة بنجاح!")
        st.download_button("⬇️ تحميل الشهادات كملف ZIP", data=zip_buffer, file_name="certificates.zip")
