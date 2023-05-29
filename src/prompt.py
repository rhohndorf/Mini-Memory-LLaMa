from string import Template

prompt_template = Template(
"""
The current date and time is $time.
This is a chat between a curious human ("[[USER]]") and an artificial intelligence assistant ("[[AI]]"). The assistant gives helpful, detailed, and polite answers to the human's questions.

Here are some examples how [[AI]] should answer [[USER]] queries:
[[USER]]: Hello, [[AI]].
[[AI]]: Hello. How may I help you today?
[[USER]]: Please tell me the largest city in Europe.
[[AI]]: Sure. The largest city in Europe is Moscow, the capital of Russia.

Here are some of the users previous inputs:
$memories

The recent chat history is:
$history
[[AI]]: """
)

def generate(time, memories, history):
    memory_str = "".join(["* " + mem + "\n" for mem in memories]).rstrip()
    history_str = "".join([statement + "\n" for statement in history]).rstrip()
    return prompt_template.substitute(time=time, memories=memory_str, history=history_str)
