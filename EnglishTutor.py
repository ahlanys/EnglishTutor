import openai
import tkinter as tk
from tkinter import scrolledtext

def chat_with_ai(user_input, conversation_history=[], user_level=1):
    openai.api_key = ""
    conversation_history.append({"role": "user", "content": user_input})
    
    system_prompt = """
    You are an English tutor. Your goal is to help the user improve their English skills.
    - If the user makes grammar or vocabulary mistakes, politely correct them and provide explanations.
    - Adjust your responses to match the user's English proficiency level: {} (1=Beginner, 5=Advanced).
    - After correcting, provide an exercise for the user to practice the mistake.
    - Give detailed explanations about grammar and vocabulary corrections.
    """.format(user_level)
    
    if not conversation_history:
        conversation_history.append({"role": "system", "content": system_prompt})
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=conversation_history 
    )
    
    reply = response["choices"][0]["message"]["content"]
    conversation_history.append({"role": "assistant", "content": reply})
    
    # Ajuste do nível de inglês do usuário baseado na resposta
    word_count = len(reply.split())
    if word_count > 20 and user_level < 5:
        user_level += 1
    elif word_count < 10 and user_level > 1:
        user_level -= 1
    
    return reply, conversation_history, user_level

def provide_feedback_and_explanation(response, user_input, is_exercise_done):
    corrections = []
    explanations = []
    feedback_request = f"User said: '{user_input}'. Please provide corrections for any mistakes in the user's response and explain why."
    
    correction_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": "You are an English tutor that provides feedback and corrections."},
            {"role": "user", "content": feedback_request}
        ],
        temperature=0,
        max_tokens=200
    )
    
    correction = correction_response["choices"][0]["message"]["content"].strip()
    
    if correction:
        corrections.append(correction)
        explanations.append("This is the corrected version of your response. Below is the explanation for the correction.")
    else:
        corrections.append("No corrections needed.")
        explanations.append("No explanations needed.")
    
    # Exercício sugerido: pedir para o usuário corrigir a frase
    exercises = []
    if corrections and not is_exercise_done:
        # Ajuste para não duplicar a frase corrigida no exercício
        exercises.append(f"Exercise: Can you correct the sentence: '{user_input}'?")
    
    feedback = "\n".join(corrections) if corrections else "No corrections needed."
    explanation = "\n".join(explanations) if explanations else "No explanations needed."
    practice_exercises = "\n".join(exercises) if exercises else ""
    
    return feedback, explanation, practice_exercises

def send_message_with_feedback():
    user_text = user_input.get()
    if user_text.strip():
        global conversation, user_level, is_exercise_done
        response, conversation, user_level = chat_with_ai(user_text, conversation, user_level)
        
        # Fornecer feedback imediato e explicação baseado na resposta do chatbot
        feedback, explanation, practice_exercise = provide_feedback_and_explanation(response, user_text, is_exercise_done)
        
        # Exibir mensagens
        chat_display.insert(tk.END, f"You: {user_text}\n", "user")
        chat_display.insert(tk.END, f"English Tutor (Level {user_level}): {response}\n", "bot")
        chat_display.insert(tk.END, f"Feedback: {feedback}\n", "assistant")
        chat_display.insert(tk.END, f"Explanation: {explanation}\n", "assistant")
        if practice_exercise:
            chat_display.insert(tk.END, f"Exercise: {practice_exercise}\n", "assistant")
        
        # Marcar que o exercício foi fornecido
        if practice_exercise:
            is_exercise_done = True  # Agora o exercício foi dado, então o bot não repete

        user_input.delete(0, tk.END)
        save_history()

def set_level(level):
    global user_level
    user_level = level
    chat_display.insert(tk.END, f"User set level to {user_level}\n", "system")
    save_history()

def save_history():
    with open("chat_history.txt", "w") as file:
        for message in conversation:
            file.write(f"{message['role'].capitalize()}: {message['content']}\n")

def load_history():
    global conversation
    try:
        with open("chat_history.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                chat_display.insert(tk.END, line, "history")
    except FileNotFoundError:
        pass

# Criar interface gráfica
root = tk.Tk()
root.title("English Tutor Chatbot")

# Exibir área de chat
chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20)
chat_display.grid(row=0, column=1, columnspan=3, padx=10, pady=10)
chat_display.tag_config("user", foreground="blue")
chat_display.tag_config("bot", foreground="green")
chat_display.tag_config("assistant", foreground="purple")
chat_display.tag_config("system", foreground="orange")
chat_display.tag_config("history", foreground="gray")

user_input = tk.Entry(root, width=50)
user_input.grid(row=1, column=1, padx=10, pady=10)

send_button = tk.Button(root, text="Send", command=send_message_with_feedback)
send_button.grid(row=1, column=2, padx=10, pady=10)

conversation = []
user_level = 1
is_exercise_done = False  # Variável para controlar se o exercício já foi dado

# Mensagem inicial do tutor
chat_display.insert(tk.END, "English Tutor: Hello! Let's practice English.\n", "bot")
load_history()

root.mainloop()
