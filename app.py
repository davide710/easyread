import gradio as gr

def display_selected_text(selected_text: gr.SelectData):
  """
  This function is triggered when text is selected in the Textbox.
  It returns the highlighted text.

  Args:
    selected_text: An object containing the selected text.
  """
  return selected_text.value

with gr.Blocks() as demo:
  gr.Markdown("## Highlight Text Example")
  gr.Markdown("Highlight any portion of the text in the box below to see the selected text displayed.")
  
  # The Textbox with some initial text.
  # The .select() method links the display_selected_text function
  # to the text selection event.
  input_text = gr.Textbox(
      "Go ahead and highlight some of this text!",
      label="Input Text"
  )
  
  # A separate Textbox to show the output from the function.
  output_text = gr.Textbox(label="Highlighted Text")
  
  # The select event triggers the function call.
  # 'input_text' is the input component, and the function's return
  # value is sent to the 'output_text' component.
  input_text.select(display_selected_text, None, output_text)

# Launch the Gradio app
demo.launch()