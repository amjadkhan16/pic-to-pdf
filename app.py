import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import io
import os

st.set_page_config(
    page_title="PicToPDF — Free Image to PDF Converter",
    page_icon="📄",
    layout="centered",
)

# ---- AD SLOT ----
# Apne ad network ka code yahan paste karein:
# - Google AdSense: AdSense dashboard se mila ad code (ye tool AdSense-friendly hai)
# - Ya backup: Monetag / Adsterra / PropellerAds ka code
AD_CODE = """
<!-- AD SPACE: apna ad code yahan paste karein -->
"""


def show_ad():
    if AD_CODE.strip().startswith("<!--"):
        st.info("🔲 **Ad space** — ad network ka code lagane par yahan ad ayega.")
    else:
        components.html(AD_CODE, height=150, scrolling=False)


# A4 size at 150 DPI (good quality, reasonable file size)
A4_PORTRAIT = (1240, 1754)
A4_LANDSCAPE = (1754, 1240)


def load_image(file):
    img = Image.open(file)
    # PDF needs RGB — convert transparent/palette images
    if img.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    return img


def fit_to_page(img, page_size):
    """Resize image to fit inside page, centered on white background."""
    page = Image.new("RGB", page_size, (255, 255, 255))
    img = img.copy()
    img.thumbnail(page_size, Image.LANCZOS)
    x = (page_size[0] - img.width) // 2
    y = (page_size[1] - img.height) // 2
    page.paste(img, (x, y))
    return page


def move_image(idx, direction):
    order = st.session_state["img_order"]
    new_idx = idx + direction
    if 0 <= new_idx < len(order):
        order[idx], order[new_idx] = order[new_idx], order[idx]
        st.session_state["img_order"] = order


def remove_image(idx):
    order = st.session_state["img_order"]
    order.pop(idx)
    st.session_state["img_order"] = order


# ---------------- NAV ----------------
page = st.sidebar.radio("Pages", ["🏠 Converter", "🔒 Privacy Policy", "✉️ Contact"])

# ---------------- CONTACT PAGE ----------------
if page == "✉️ Contact":
    st.title("✉️ Contact")
    st.write(
        "Koi sawal, feedback ya copyright se mutaliq darkhwast ho to "
        "neeche diye gaye email par rabta karein:"
    )
    CONTACT_EMAIL = "amjad786gcf@gmail.com"
    st.markdown(f"📧 **Email:** `{CONTACT_EMAIL}`")
    st.write("Hum aam tor par 48 hours ke andar jawab dene ki koshish karte hain.")
    st.divider()
    st.caption("© 2026 PicToPDF. All rights reserved.")

# ---------------- PRIVACY POLICY PAGE ----------------
elif page == "🔒 Privacy Policy":
    st.title("🔒 Privacy Policy")
    st.caption("Last updated: October 2026")
    st.markdown("""
**PicToPDF** ("we", "our", "this website") respects your privacy. This policy
explains what information is handled when you use our free image to PDF converter.

### 1. Information we collect
We do **not** require any account, sign-up, or login. We do not ask for your
name, email address, or any personal details to use the converter.

### 2. How the service works
- The images you upload are used only to create your PDF file.
- Files are processed temporarily on the server only to deliver your PDF
  to you, and are deleted automatically afterwards.
- We do **not** store your images, your PDFs, or any file on our servers
  permanently. Your files never leave the conversion process.

### 3. Cookies and advertising
- This website may display advertisements served by third-party ad networks
  (for example Google AdSense, Monetag, Adsterra, or PropellerAds).
- These ad partners may use cookies or similar technologies to show you
  relevant ads and to measure ad performance. You can control cookies through
  your browser settings.
- We do not control how third-party advertisers use cookies; please review
  their own privacy policies.

### 4. Acceptable use
This tool is intended for converting images you own or have the right to use.
Do not upload content that violates anyone's copyright or privacy rights.

### 5. Children's privacy
This website is not directed at children under 13, and we do not knowingly
collect information from children.

### 6. Changes to this policy
We may update this Privacy Policy from time to time. The "Last updated" date
at the top will reflect the latest version.

### 7. Contact
Questions about this policy? Reach us through the **Contact** page.
""")
    st.divider()
    st.caption("© 2026 PicToPDF. All rights reserved.")

# ---------------- CONVERTER (HOME) ----------------
else:
    st.title("📄 PicToPDF")
    st.write("**Free Image to PDF Converter** — tasveerein upload karo, tartib set karo, PDF download karo. Koi signup nahi, koi limit nahi.")

    show_ad()

    if "img_order" not in st.session_state:
        st.session_state["img_order"] = []

    uploaded = st.file_uploader(
        "Tasveerein chuno",
        type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"],
        accept_multiple_files=True,
        help="Ek se zyada images select kar sakte ho",
    )

    # Add newly uploaded files to the order list (avoid duplicates)
    if uploaded:
        existing_names = {e["name"] for e in st.session_state["img_order"]}
        for f in uploaded:
            if f.name not in existing_names:
                st.session_state["img_order"].append({"name": f.name, "file": f})

    order = st.session_state["img_order"]

    if order:
        st.divider()
        st.subheader(f"📷 {len(order)} images")
        st.caption("Tartib badalne ke liye ↑ ↓ dabao — PDF mein yehi order hoga.")

        for i, item in enumerate(order):
            col1, col2, col3 = st.columns([2, 5, 3])
            with col1:
                try:
                    thumb = load_image(item["file"])
                    thumb.thumbnail((120, 120))
                    st.image(thumb)
                except Exception:
                    st.write("🖼️")
            with col2:
                st.write(f"**{i + 1}.** {item['name']}")
            with col3:
                b1, b2, b3 = st.columns(3)
                with b1:
                    st.button("↑", key=f"up_{i}", disabled=(i == 0),
                              on_click=move_image, args=(i, -1))
                with b2:
                    st.button("↓", key=f"dn_{i}", disabled=(i == len(order) - 1),
                              on_click=move_image, args=(i, 1))
                with b3:
                    st.button("✕", key=f"rm_{i}", on_click=remove_image, args=(i,))

        if st.button("🗑 Sab saaf karo"):
            st.session_state["img_order"] = []
            st.rerun()

        st.divider()
        page_size = st.selectbox(
            "Page size",
            ["Original size (har image apne size par)", "A4 Portrait", "A4 Landscape"],
        )

        if st.button("📄 PDF Banao", type="primary"):
            with st.spinner("PDF ban rahi hai..."):
                try:
                    pages = []
                    for item in order:
                        img = load_image(item["file"])
                        if page_size.startswith("A4 Portrait"):
                            img = fit_to_page(img, A4_PORTRAIT)
                        elif page_size.startswith("A4 Landscape"):
                            img = fit_to_page(img, A4_LANDSCAPE)
                        pages.append(img)

                    buf = io.BytesIO()
                    pages[0].save(buf, format="PDF", save_all=True,
                                  append_images=pages[1:] if len(pages) > 1 else [])
                    pdf_bytes = buf.getvalue()
                    st.session_state["pdf_data"] = pdf_bytes
                    st.success(f"✅ PDF tayyar! ({len(pages)} pages, {len(pdf_bytes) / 1024:.0f} KB)")
                except Exception as e:
                    st.error(f"PDF banane mein masla: {e}")

        pdf_data = st.session_state.get("pdf_data")
        if pdf_data:
            st.download_button(
                "⬇ PDF Download Karo",
                data=pdf_data,
                file_name="pictopdf.pdf",
                mime="application/pdf",
                type="primary",
            )
    else:
        st.info("👆 Upar se tasveerein upload karo shuru karne ke liye.")

    st.divider()
    show_ad()
    st.caption(
        "Tumhari images server par save nahi hotin — PDF bante hi sab delete ho jata hai. "
        "100% free, koi watermark nahi."
    )
