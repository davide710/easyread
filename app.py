import gradio as gr
def on_copy(copy_data: gr.CopyData):
    return f"Copied text: {copy_data.value}"
with gr.Blocks() as demo:
    textbox = gr.Textbox("Hello World!")
    copied = gr.Textbox()
    textbox.copy(on_copy, None, copied)
demo.launch()