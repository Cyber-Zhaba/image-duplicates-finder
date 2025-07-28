import os
from collections import defaultdict

import streamlit as st
from PIL import Image

from foo import sha256_hash, perceptual_hash, convolution_hash, sobel_hash, sharpen_hash, gray_convolution_hash


def start_processing(dir_path):
    if "processed" not in st.session_state:
        status_container = st.empty()
        status_container.info("Proceeding...")

        # === Hash storage ===
        st.session_state.sha256_dict = defaultdict(set)
        st.session_state.perceptual_dict = defaultdict(set)
        st.session_state.convolution_dict = defaultdict(set)
        st.session_state.sobel_dict = defaultdict(set)
        st.session_state.sharpen_dict = defaultdict(set)
        st.session_state.gray_convolution_hash = defaultdict(set)

        # === Status ===
        progress_bar = st.progress(0)
        images = os.listdir(dir_path)
        total_images = len(images)

        for i, img in enumerate(images):
            img_path = os.path.join(dir_path, img)

            # === Hashes ===
            if sha256_check:
                sha256 = sha256_hash(img_path)
                st.session_state.sha256_dict[sha256].add(img_path)
            if perceptual_check:
                perceptual = perceptual_hash(img_path)
                st.session_state.perceptual_dict[perceptual].add(img_path)
            if convolution_check:
                convolution = convolution_hash(img_path)
                st.session_state.convolution_dict[convolution].add(img_path)
            if sobel_check:
                sobel = sobel_hash(img_path)
                st.session_state.sobel_dict[sobel].add(img_path)
            if sharpen_check:
                sharpen = sharpen_hash(img_path)
                st.session_state.sharpen_dict[sharpen].add(img_path)
            if gray_convolution_check:
                gray = gray_convolution_hash(img_path)
                st.session_state.gray_convolution_hash[gray].add(img_path)

            # === Update status ===
            progress_percent = int((i + 1) / total_images * 100)
            progress_bar.progress(progress_percent)

        status_container.empty()
        st.success("✅ Proceeding completed!")

        st.session_state.processed = True
        st.session_state.skip = set()

    # === Print results ===
    already_found = set()
    duplicates_names = []

    for hash_dict, hash_name, show in [
        (st.session_state.sha256_dict, "SHA256", sha256_check),
        (st.session_state.perceptual_dict, "Perceptual Hash", perceptual_check),
        (st.session_state.convolution_dict, "Convolution Hash", convolution_check),
        (st.session_state.sobel_dict, "Sobel Hash", sobel_check),
        (st.session_state.sharpen_dict, "Sharpen Hash", sharpen_check),
        (st.session_state.gray_convolution_hash, "Gray Convolution Hash", gray_convolution_check),
    ]:
        if not show:
            continue
        st.write(f"### {hash_name}")
        duplicates_groups = []
        for group in hash_dict.values():
            difference = group - already_found
            if len(difference) > 1:
                already_found.update(difference)
                already_found.remove(next(iter(difference)))
                duplicates_groups.append(difference)

        for group in duplicates_groups:
            group = list(group)
            standard = group[0]
            for img in group[1:]:
                if img not in st.session_state.skip:
                    col1, col2 = st.columns([0.48, 0.48], gap="medium")

                    with col1:
                        st.image(
                            Image.open(standard),
                            caption="Original",
                            width=image_size
                        )

                    with col2:
                        st.image(
                            Image.open(img),
                            caption="Possible duplicate",
                            width=image_size
                        )
                    # st.image(
                    #     [Image.open(standard), Image.open(img)],
                    #     caption=["Original", "Possible duplicate"],
                    #     width=image_size,
                    # )
                    st.write(img.split("/")[-1])
                    if st.button("Skip", key=img, type="secondary"):
                        st.session_state.skip.add(img)
                        st.rerun()
                    duplicates_names.append(img.split("/")[-1].split("\\")[-1])

    st.write(len(duplicates_names))
    st.write("(" + "|".join(duplicates_names) + ")$")


if __name__ == "__main__":
    st.title("🔍 Find Duplicate Images")

    image_path = st.text_input(
        "Directory with images", placeholder="Enter path to images directory"
    )

    # Enable or disable hash functions
    sha256_check = st.checkbox("SHA256", value=True)
    perceptual_check = st.checkbox("Perceptual Hash", value=True)
    convolution_check = st.checkbox("Convolution Hash", value=True)
    sobel_check = st.checkbox("Sobel Hash", value=True)
    sharpen_check = st.checkbox("Sharpen Hash",value=True)
    gray_convolution_check = st.checkbox("Gray Convolution Hash", value=True)

    image_size = st.slider("Image size to display", 200, 800, 350)
    if "start_processed" in st.session_state:
        start_processing(image_path)

    if st.button("Start check", type="primary"):
        if image_path:
            st.session_state.start_processed = True
            start_processing(image_path)
        else:
            st.warning("Please enter a directory path")
