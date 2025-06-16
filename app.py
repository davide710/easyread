import gradio as gr

def display_selected_text(evt):
  """
  This function is triggered when text is selected in the Textbox.
  It's designed to receive the event data from the .select() method.

  A print statement is added for debugging in the Hugging Face Space logs.
  """
  # This print statement is our key for debugging!
  print(f"Event triggered! Selected text: {evt.value}")
  
  # The function returns the highlighted text value from the event data.
  return evt.value

with gr.Blocks() as demo:
  gr.Markdown("## Highlight Text Example")
  gr.Markdown("Highlight any portion of the text in the box below to see the selected text displayed.")
  
  input_text = gr.Textbox(
      "Go ahead and highlight some of this text!",
      label="Input Text"
  )
  
  output_text = gr.Textbox(label="Highlighted Text")
  
  # This connects the select event to our function.
  # When text is selected in 'input_text', it calls 'display_selected_text'.
  # The event data (which contains the selected text) is automatically
  # passed as the 'evt' argument to our function.
  # The function's return value is then placed in 'output_text'.
  input_text.select(fn=display_selected_text, inputs=None, outputs=output_text)

# Launch the Gradio app
demo.launch()