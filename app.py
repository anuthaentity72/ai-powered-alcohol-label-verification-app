import streamlit as st

st.set_page_config(page_title="AI Alcohol Label Verification App")

st.title("AI-Powered Alcohol Label Verification App")

st.write("Upload an alcohol label image to begin verification.")

uploaded_file = st.file_uploader(
    "Upload Label Image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Label", use_column_width=True)

    st.success("Image uploaded successfully.")
