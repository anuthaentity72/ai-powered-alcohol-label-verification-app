import streamlit as st
import easyocr
import numpy as np
from PIL import Image
from rapidfuzz import fuzz
import re

st.set_page_config(
    page_title="AI Alcohol Label Verification",
    layout="wide"
)

st.title("AI-Powered Alcohol Label Verification App")

st.write(
    "Upload an alcohol label image to extract text and perform a basic compliance review."
)

uploaded_file = st.file_uploader(
    "Upload Label Image",
    type=["png", "jpg", "jpeg"]
)

EXPECTED_WARNING_PHRASE = "GOVERNMENT WARNING"


def extract_text(image):
    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext(np.array(image))
    extracted_text = " ".join([item[1] for item in results])
    return extracted_text


def find_abv(text):
    match = re.search(
        r'(\d{1,2}(?:\.\d+)?)\s*%\s*(?:ALC|ALC\.?/VOL|VOL)?',
        text.upper()
    )

    if match:
        return match.group(1) + "%"

    return None


def find_net_contents(text):
    match = re.search(
        r'(\d+\s*(?:ML|L|OZ|FL OZ))',
        text.upper()
    )

    if match:
        return match.group(1)

    return None


def warning_check(text):
    score = fuzz.partial_ratio(
        EXPECTED_WARNING_PHRASE,
        text.upper()
    )

    return score >= 85, score


if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(
        image,
        caption="Uploaded Label",
        width=500
    )

    with st.spinner("Analyzing label..."):

        extracted_text = extract_text(image)

        abv = find_abv(extracted_text)
        net_contents = find_net_contents(extracted_text)

        warning_found, warning_score = warning_check(extracted_text)

    st.success("Analysis Complete")

    st.subheader("Extracted Text")

    st.text_area(
        "OCR Results",
        extracted_text,
        height=250
    )

    st.subheader("Compliance Review")

    compliance_results = []

    compliance_results.append(
        ("Alcohol Content (ABV)", "PASS" if abv else "MISSING")
    )

    compliance_results.append(
        ("Net Contents", "PASS" if net_contents else "MISSING")
    )

    compliance_results.append(
        ("Government Warning", "PASS" if warning_found else "REVIEW")
    )

    for item, status in compliance_results:

        if status == "PASS":
            st.success(f"{item}: {status}")

        elif status == "REVIEW":
            st.warning(f"{item}: {status}")

        else:
            st.error(f"{item}: {status}")

    st.subheader("Detected Values")

    st.write(f"**ABV:** {abv if abv else 'Not Found'}")
    st.write(f"**Net Contents:** {net_contents if net_contents else 'Not Found'}")
    st.write(f"**Warning Match Score:** {warning_score}%")

    pass_count = sum(
        1 for _, status in compliance_results
        if status == "PASS"
    )

    if pass_count == 3:
        st.success("FINAL RESULT: PASS")

    elif pass_count >= 2:
        st.warning("FINAL RESULT: NEEDS REVIEW")

    else:
        st.error("FINAL RESULT: FAIL")