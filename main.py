import os
from collections import defaultdict

import streamlit as st
from PIL import Image

from foo import sha256_hash, perceptual_hash, convolution_hash, sobel_hash, sharpen_hash


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

        # === Status ===
        progress_bar = st.progress(0)
        images = os.listdir(dir_path)
        total_images = len(images)

        for i, img in enumerate(images):
            img_path = os.path.join(dir_path, img)

            # === Hashes ===
            sha256 = sha256_hash(img_path)
            perceptual = perceptual_hash(img_path)
            convolution = convolution_hash(img_path)
            sobel = sobel_hash(img_path)
            sharpen = sharpen_hash(img_path)

            # === Store hashes in dictionaries ===
            st.session_state.sha256_dict[sha256].add(img_path)
            st.session_state.perceptual_dict[perceptual].add(img_path)
            st.session_state.convolution_dict[convolution].add(img_path)
            st.session_state.sobel_dict[sobel].add(img_path)
            st.session_state.sharpen_dict[sharpen].add(img_path)

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

    for hash_dict, hash_name in [
        (st.session_state.sha256_dict, "SHA256"),
        (st.session_state.perceptual_dict, "Perceptual Hash"),
        (st.session_state.convolution_dict, "Convolution Hash"),
        (st.session_state.sobel_dict, "Sobel Hash"),
        (st.session_state.sharpen_dict, "Sharpen Hash"),
    ]:
        duplicates_groups = []
        for group in hash_dict.values():
            difference = group - already_found
            if len(difference) > 0:
                already_found.update(difference)
                duplicates_groups.append(difference)

        for group in duplicates_groups:
            group = list(group)
            standard = group[0]
            for img in group[1:]:
                if img not in st.session_state.skip:
                    st.image(
                        [Image.open(standard), Image.open(img)],
                        caption=["Original", "Possible duplicate"],
                        width=200,
                    )
                    st.write(img.split("/")[-1])
                    if st.button("Skip", key=img, type="secondary"):
                        st.session_state.skip.add(img)
                        st.rerun()
                    duplicates_names.append(img.split("/")[-1])

    st.write(len(duplicates_names))
    st.write("^(" + "|".join(duplicates_names) + ")$")


if __name__ == "__main__":
    st.title("🔍 Find Duplicate Images")

    image_path = st.text_input(
        "Directory with images", placeholder="Enter path to images directory"
    )
    if "start_processed" in st.session_state:
        start_processing(image_path)

    if st.button("Start check", type="primary"):
        if image_path:
            st.session_state.start_processed = True
            start_processing(image_path)
        else:
            st.warning("Please enter a directory path")
