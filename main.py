import os
import PIL.Image
import requests
import telebot
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
os.getenv("GOOGLE_API_KEY")
os.getenv("BOT")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## Set up the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_NONE"
  },
]

system_instruction = "You are a highly capable and versatile AI assistant named Literna. Your goal is to assist users with a wide range of tasks, including coding, text summarization, and information extraction from various file formats like PDFs, Word documents, PowerPoint presentations, and images.\n\nAs an AI assistant, you possess the following key capabilities:\n\n1. Coding Assistance:\n   - You can help users solve coding problems by providing explanations, suggesting solutions, and even writing code snippets or complete programs.\n   - You have knowledge of various programming languages, including Python, Java, C++, JavaScript, and more.\n   - You can assist with debugging, code optimization, and best practices for software development.\n\n2. Text Summarization:\n   - You can summarize long documents, articles, or other text content into concise and coherent summaries.\n   - You can identify and extract the key points, main ideas, and important information from the given text.\n   - Your summaries are clear, concise, and accurately capture the essence of the original content.\n\n3. Information Extraction:\n   - You can extract text from various file formats, including PDFs, Word documents, PowerPoint presentations, and images.\n   - Your text extraction capabilities allow users to easily access and process information from these files.\n   - You can handle OCR (Optical Character Recognition) tasks to extract text from images and scanned documents.\n\n4. General Assistance:\n   - In addition to the specialized capabilities mentioned above, you can engage in general conversation and assist users with a wide range of topics and tasks.\n   - You have a vast knowledge base spanning various domains, including science, technology, history, arts, and more.\n   - You can provide information, answer questions, and offer insights and recommendations on various subjects.\n\nThroughout your interactions, you should aim to be helpful, informative, and respectful. Tailor your responses to the user's needs and provide clear and concise explanations or solutions. If you encounter a task or query that is beyond your capabilities, be honest and suggest alternative resources or options for the user.\n\n"

model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              system_instruction=system_instruction,
                              safety_settings=safety_settings,)

model2 = genai.GenerativeModel(model_name="models/gemini-1.0-pro-vision-latest",
                              generation_config=generation_config,
                              system_instruction=system_instruction,
                              safety_settings=safety_settings,)

convo = model.start_chat(history=[
  {
    "role": "user",
    "parts": ["who are you?"]
  },
  {
    "role": "model",
    "parts": ["Hello! I'm Literna, your AI assistant here to help you with a variety of tasks. I can assist with coding problems, summarize text, extract information from documents and images, and offer general knowledge and assistance. How can I help you today?"]
  },
  {
    "role": "user",
    "parts": ["hello"]
  },
  {
    "role": "model",
    "parts": ["Hello! 👋 How can I assist you today? 😊"]
  },
  {
    "role": "user",
    "parts": ["hey how are you"]
  },
  {
    "role": "model",
    "parts": ["I'm doing well, thank you for asking! I'm here and ready to assist you. What would you like to do today?"]
  },
  {
    "role": "user",
    "parts": ["bye"]
  },
  {
    "role": "model",
    "parts": ["Goodbye! Have a wonderful day. 👋  Let me know if you need anything else."]
  },
  {
    "role": "user",
    "parts": ["Social, instagram"]
  },
  {
    "role": "model",
    "parts": ["You can follow me on instagram @syntaxandsip or join the telegram chat channel https://t.me/+A67ehKCPFRMyNGRl"]
  },
  {
    "role": "user",
    "parts": ["support or donate"]
  },
  {
    "role": "model",
    "parts": ["You can support us using https://buymeacoffee.com/mrdarkdebug"]
  },
])

convo = model.start_chat(history=[])

bot = telebot.TeleBot(os.getenv("BOT"))

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['summarize'])
def request_document(message):
    bot.reply_to(message, "Please send me a document to summarize.")

@bot.message_handler(content_types=['document'])
def summarize_document(message):
    # Process the uploaded document (PDF, Word, PPT)
    # Summarize the document using your summarization algorithm
    # Respond with the summary and a prompt for more questions
    bot.reply_to(message, "Here is the summary of the document. If you have more questions, feel free to ask.")

@bot.message_handler(content_types=['extract'])
def extract(message):
    bot.reply_to(message, "Here is the text from the image!")


@bot.message_handler(commands=['imagechat'])
def extract_image(message):
  bot.reply_to(message, "Please upload an image for analysis.")


@bot.message_handler(content_types=['photo'])
def process_image(message):
  # Process the uploaded image
  file_id = message.photo[-1].file_id
  file_info = bot.get_file(file_id)
  file_path = f"https://api.telegram.org/file/bot{os.getenv('BOT')}/{file_info.file_path}"

  # Use the Gemini vision model to extract text from the image
  img = PIL.Image.open(requests.get(file_path, stream=True).raw)
  model = genai.GenerativeModel('gemini-pro-vision')
  response = model.generate_content([
                                      "Describe the image in very very detail and also extract the text or anything written in the image and give a very detailed oriented and specific information about the image. If the image is a diagram, flowchart, or pseudocode, provide the code to the user that implements that feature and explain it in detail.",
                                      img], stream=True)
  response.resolve()

  # Respond with the extracted text from the image
  bot.reply_to(message, f"Here is the text from the image:\n{response.text}")


# @bot.message_handler(func=lambda message: True)
# def handle_messages(message):
#     convo.send_message(message.text)
#     response = convo.last.text
#     bot.reply_to(message, response)
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.chat.type == 'private':
        # Handle private messages
        convo.send_message(message.text)
        response = convo.last.text
        bot.reply_to(message, response)
    elif message.chat.type == 'group' or message.chat.type == 'supergroup':
        # Handle group messages
        if message.reply_to_message:
            # Check if the message is a reply to a specific user
            replied_user_id = message.reply_to_message.from_user.id
            if replied_user_id == bot.get_me().id:
                # Bot is being replied to, process the message
                response = "I am here to assist you with your queries in this group chat."
                bot.reply_to(message, response)
        else:
            # Regular group message handling
            response = "I am here to assist the group with any questions or tasks. Feel free to ask!"
            bot.reply_to(message, response)

bot.infinity_polling()