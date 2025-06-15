import gradio as gr

def greet(name):
    return "Hello " + name + "!! easyread will be available soon!"

demo = gr.Interface(fn=greet, inputs="text", outputs="text")
demo.launch()
