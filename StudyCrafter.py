import streamlit as st
import fitz  # PyMuPDF
import io
import time
from streamlit_pdf_viewer import pdf_viewer


st.markdown("""
<style>

.block-container
{
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-top: 1rem;
}

</style>
""", unsafe_allow_html=True)

def app():

    # Utility functions
    def hex_to_rgb_percent(hex_color):
        """Convert hex color format to a tuple of RGB values in the range 0 to 1."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) / 255.0 for i in range(0, 6, 2))


    def process_pdf(input_pdf_bytes, page_number, notes_text, font_name, color, position, bg_color, text_color,
                    include_date, total_progress, total_files, current_file_index, progress_text, file_counter):
        doc = fitz.open("pdf", input_pdf_bytes)
        new_pdf = fitz.open()
        num_pages = len(doc)
        for page_index, page in enumerate(doc):
            if page_index + 1 != page_number:
                new_pdf.insert_pdf(doc, from_page=page_index, to_page=page_index)
                continue
            
            rect = page.rect
            if position == 'Right':
                new_page = new_pdf.new_page(width=rect.width * 2, height=rect.height)
                new_page.show_pdf_page(fitz.Rect(0, 0, rect.width, rect.height), doc, page.number)
                notes_rect = fitz.Rect(rect.width, 0, rect.width * 2, rect.height)
                mid_x = rect.width
            
            elif position == 'Bottom':
                new_page = new_pdf.new_page(width=rect.width, height=rect.height * 2)
                new_page.show_pdf_page(fitz.Rect(0, 0, rect.width, rect.height), doc, page.number)
                notes_rect = fitz.Rect(0, rect.height, rect.width, rect.height * 2)
                mid_y = rect.height
                new_page.draw_line([0, mid_y], [rect.width, mid_y], color=(0, 0, 0), width=1)
                mid_x = rect.width / 2

            new_page.draw_rect(notes_rect, color=bg_color, fill=bg_color)
            new_page.insert_text(
                [notes_rect.x0 + 20, notes_rect.y0 + 35],
                notes_text,
                fontsize=15,
                color=text_color,
                fontname=font_name
            )

            if include_date:
                if font_name == "Courier":
                    date_x_position = notes_rect.x1 - 236
                elif font_name == "Times-Roman":
                    date_x_position = notes_rect.x1 - 170
                else:
                    date_x_position = notes_rect.x1 - 185
                new_page.insert_text(
                    [date_x_position, notes_rect.y0 + 35],
                    "Date: ___ / ___ / ______",
                    fontsize=15,
                    color=text_color,
                    fontname=font_name
                )
            
            if position in ['Right', 'Left']:
                new_page.draw_line([mid_x, 0], [mid_x, rect.height], color=(0, 0, 0), width=1)

            total_progress_value = (current_file_index + (page_index + 1) / num_pages) / total_files
            total_progress.progress(total_progress_value)
            progress_percent = total_progress_value * 100
            progress_text.markdown(
                f"<div style='text-align: center; font-size:20px; font-weight:bold;'> Progress: {progress_percent:.2f}%</div>",
                unsafe_allow_html=True)
            file_counter.markdown(
                f"<div style='text-align: center; font-size:20px; font-weight:bold;'>Processing file {current_file_index + 1} of {total_files}</div>",
                unsafe_allow_html=True)
            time.sleep(0.1)
        
        output_pdf_stream = io.BytesIO()
        new_pdf.save(output_pdf_stream)
        output_pdf_stream.seek(0)
        doc.close()
        new_pdf.close()
        return output_pdf_stream


    # Main UI layout

    gradient_text_html = """
        <style>
        .gradient-text {
            font-weight: bold;
            background: -webkit-linear-gradient(left, #07539e, #4fc3f7, #ffffff);
            background: linear-gradient(to right, #07539e, #4fc3f7, #ffffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline;
            font-size: 3em;
        }
        </style>
        <div class="gradient-text">NotesCrafter</div>
        """

    # Render the gradient text
    st.markdown(gradient_text_html, unsafe_allow_html=True)
    st.markdown('<b> NotesCrafter -The Ultimate study tool for :orange[adding notes directly to your PDFs!] ✒️📄', unsafe_allow_html=True)
    st.markdown('<b>Tired of juggling PDFs and sticky notes?</b> **NotesCrafter** lets you upload PDFs, select pages, and add personalized notes effortlessly—no more flipping between pages or losing track of your thoughts. Streamline your workflow and stay organized! 🚀',unsafe_allow_html=True)
    


    # Customization Section
    if 'text_color' not in st.session_state:
        st.session_state.text_color = '#000000'

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div style="text-align: left;font-size:170%;margin-bottom: 10px"><b> Page Position and Fonts</b></div>',
            unsafe_allow_html=True)
        position = st.radio(
            "Position of Notes Section",
            ["Right", "Bottom"],
            horizontal=True,
            help="Choose where the notes section will be added on the page."
        )
        st.write('')
        font_name = st.radio(
            "Font for Notes and Date",
            ["Courier", "Times-Roman"],
            horizontal=True,
            help="Select the font for the notes text."
        )
        
        notes_text = st.text_input("Title", "Enter Notes Title", help="Enter the text to be displayed in the notes section.")

    with col2:
        page_number = st.number_input("Enter the page number where you want to add notes", min_value=1, step=1, help="Enter the page number where you want to add notes.")
        st.markdown(
            '<div style="text-align: left;font-size:170%;margin-bottom: 10px"><b> Notes Content</b></div>',
            unsafe_allow_html=True)
        notes_content = st.text_area("Enter the Notes", help="Enter the notes text to be displayed below the title.")

    bg_color = (1, 1, 1)  # White background
    color = (0, 0, 0)  # Black color for lines (not used)
    text_color = (0, 0, 0)  # Black text color
    spacing = 20

    st.markdown("<hr>", unsafe_allow_html=True)

    # File Upload Section
    st.markdown(
        '<div style="text-align: center;font-size:170%;margin-bottom: 7px"><b>📤 Upload PDF Files</b></div>',
        unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

    st.write('')
    st.write('')
    st.write('')
    

    # Check if processed_files is in session state, if not initialize it
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []

    if 'start_processing' not in st.session_state:
        st.session_state.start_processing = False

    def start_processing():
        st.session_state.start_processing = True
        st.session_state.processed_files = []

    if uploaded_files:
        # Total progress bar and text elements
        total_files = len(uploaded_files)
        total_progress = st.progress(0)
        progress_text = st.empty()
        file_counter = st.empty()
        st.markdown("<hr>", unsafe_allow_html=True)
        # Process PDF and display
        st.markdown(
            '<div style="text-align: center;font-size:170%;margin-bottom: 6px"><b>🛠 Process PDFs</b></div>',
            unsafe_allow_html=True)
        
       

        if st.button("🖨️ :orange[Click me for your notes] 🖨️", use_container_width=True, key="start_button"):
            start_processing()
            for i, uploaded_file in enumerate(uploaded_files):
                with st.spinner(f"Processing {uploaded_file.name}"):
                    binary_pdf = uploaded_file.read()
                    input_pdf_stream = io.BytesIO(binary_pdf)
                    input_pdf_stream.seek(0)  # Reset the stream position
                    output_pdf_stream = process_pdf(
                        input_pdf_stream.getvalue(), page_number, f"{notes_text}\n{notes_content}", font_name, color, position,
                        bg_color, text_color, False, total_progress, total_files, i, progress_text, file_counter
                    )

                    # Save the output stream to a separate variable for each file
                    output_stream = output_pdf_stream.getvalue()
                    st.session_state.processed_files.append(
                        (uploaded_file.name, output_stream, f"download_{i}_{time.time()}"))  # Add unique key
            
            # After processing all files, display them
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(
                '<div style="text-align: center;font-size:170%;margin-bottom: 10px"><b>🔎 View Processed PDFs</b></div>',
                unsafe_allow_html=True)

    for j, (file_name, output_stream, unique_key) in enumerate(st.session_state.processed_files):
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="text-align: center;font-size:170%;margin-bottom: 10px"><b>🔎 View PDF</b></div>',
            unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"➔ {j + 1} -  {file_name}   ✅")
        with col2:
            st.download_button(
                label="Download",
                data=output_stream,
                file_name=f"{file_name}_withNotes.pdf",
                mime="application/pdf",
                use_container_width=True,
                key=f"download_{j}_{time.time()}"
            )

        # Display the output PDF
        pdf_viewer(output_stream, width=1200, height=600, pages_vertical_spacing=2, annotation_outline_size=2,
                pages_to_render=[])

# Run the app
if __name__ == "__main__":
    app()
