from llama_cpp import Llama
from memory import Memory
import config as cfg
import prompt
from datetime import datetime

if __name__=="__main__":
    llm = Llama(model_path=cfg.MODEL_PATH, embedding=True, n_ctx=2048)
    mem = Memory(llm)
    history = []

    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        user_input = "[[User]]: " + input("[[User]]: ")
        memories = mem.get_relevant(user_input, cfg.MEM_TOP_K)
        history.append(user_input)
        mem.add(user_input)
        print(memories)
        ctx = prompt.generate(now, memories, history)
        print(ctx)
        bot_output = llm(ctx, stop=["[[User]]"], echo=False)
        print("[[AI]]: " + bot_output.get("choices")[0]["text"])
        history.append("[[AI]]: " + bot_output.get("choices")[0]["text"])
        if len(history) > 10:
            history = history[-10:]
