import gradio as gr
import PyPDF2
#from io import BytesIO
#import os

#from huggingface_hub import InferenceClient


def simplify_text(text: str) -> str:
    if not text.strip():
        return "No text selected"

    try:
        return "simplified text"

    except Exception as e:
        return f"Error during model inference: {e}"


def process_pdf(pdf_file) -> tuple[str, str]:
    if pdf_file is None:
        return "", "Please upload a PDF file."

    pdf_text = ""
    try:
        with open(pdf_file.name, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                extracted_page_text = page.extract_text()
                if extracted_page_text:
                    pdf_text += extracted_page_text + "\n\n"

        if not pdf_text.strip():
            return "", "Could not extract text from the PDF. It might be an image-only PDF or empty."

        return pdf_text, "PDF successfully loaded. Highlight text to simplify."
    except Exception as e:
        return "", f"Error processing PDF: {e}"


with gr.Blocks(title="EasyRead", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # EasyRead: Simplify Complex English Texts for Non-Native Speakers
        
        **Goal:** Help non-native English speakers read complex or old books (e.g., Shakespeare, classic literature).
        
        **Instructions:**
        1.  **Upload a PDF** file using the 'Upload PDF' button.
        2.  The extracted text will appear in the 'Original Text' area.
        3.  **Highlight any part of the text** in the 'Original Text' box to get its simplified version.
        4.  The simplified output will appear in the 'Simplified Version' box below.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            pdf_upload_button = gr.File(
                label="Upload PDF",
                file_types=[".pdf"],
                height=150
            )
            pdf_status_message = gr.Markdown("No PDF uploaded yet.", elem_id="pdf_status")

        with gr.Column(scale=2):
            original_text_display = gr.Textbox(
                label="Original Text (from PDF)",
                lines=25,
                interactive=True,
                autoscroll=False,
                max_lines=30,
                placeholder="Upload a PDF to see its text here. Then highlight text to simplify.",
                elem_id="original_text_area"
            )
            gr.Markdown("---")
            simplified_output = gr.Textbox(
                label="Simplified Version",
                lines=8,
                interactive=False,
                autoscroll=True,
                placeholder="Simplified text will appear here after you highlight text above.",
                elem_id="simplified_text_area"
            )


    pdf_upload_button.upload(
        fn=process_pdf,
        inputs=pdf_upload_button,
        outputs=[original_text_display, pdf_status_message],
        show_progress="full"
    )

    original_text_display.select(
        fn=simplify_text,
        inputs=gr.State(None),
        outputs=simplified_output,
        trigger_mode="always_last",
        js="""
        (original_text_area, simplified_text_area) => {
            const textarea = document.getElementById("original_text_area").querySelector("textarea");
            const selectedText = textarea.value.substring(textarea.selectionStart, textarea.selectionEnd);
            return selectedText;
        }
        """
    )

    gr.HTML("""
        <style>
            #original_text_area textarea {
                min-height: 400px !important; /* Make the text area tall */
                height: auto !important; /* Allow it to adjust if content is smaller */
                font-family: 'Inter', sans-serif; /* Consistent font */
                font-size: 1.1em;
                line-height: 1.6;
                padding: 20px;
                box-sizing: border-box; /* Include padding in element's total width and height */
            }
            #simplified_text_area textarea {
                min-height: 150px !important;
                font-family: 'Inter', sans-serif;
                font-size: 1.0em;
                line-height: 1.5;
                padding: 15px;
                background-color: #f0f8ff; /* Light blue background for output */
                border: 1px solid #cceeff;
                box-sizing: border-box;
            }
            .gradio-container {
                max-width: 1200px; /* Max width for the entire app */
                margin: auto; /* Center the app */
                padding: 20px;
            }
            h1 {
                text-align: center;
                color: #333;
            }
            h2 {
                color: #555;
            }
            /* Style for the file upload button to make it more prominent */
            .gradio-file input[type="file"] {
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
            }
        </style>
    """)


demo.launch()