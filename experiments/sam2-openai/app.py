import streamlit as st
import cv2
import numpy as np
from PIL import Image

from utils.sam2_floor_mask import get_floor_mask
from utils.openai_reasoning import analyze_flooring_reference
from utils.apply_flooring import apply_floor

st.set_page_config(layout="wide")
st.title("AI Flooring Visualizer (Local + SAM2 + OpenAI)")

base_img_file = st.file_uploader("Upload Base Room Image", type=["jpg","png"])
ref_img_file = st.file_uploader("Upload Flooring Reference Image", type=["jpg","png"])

if base_img_file and ref_img_file:
    base_img = np.array(Image.open(base_img_file).convert("RGB"))
    ref_img = np.array(Image.open(ref_img_file).convert("RGB"))

    col1, col2 = st.columns(2)
    col1.image(base_img, caption="Base Image", use_column_width=True)
    col2.image(ref_img, caption="Flooring Reference", use_column_width=True)

    if st.button("Apply Flooring"):
        with st.spinner("Detecting floor (SAM2)..."):
            mask = get_floor_mask(base_img)

        with st.spinner("Analyzing flooring reference (LLM)..."):
            reasoning = analyze_flooring_reference(ref_img_file.read())
            st.code(reasoning, language="json")

        with st.spinner("Applying flooring..."):
            result = apply_floor(base_img, mask, ref_img)

        st.image(result, caption="Result", use_column_width=True)

        st.download_button(
            "Download Result",
            data=cv2.imencode(".png", cv2.cvtColor(result, cv2.COLOR_RGB2BGR))[1].tobytes(),
            file_name="flooring_result.png"
        )
