import discord
import time
import os
from discord.ext import commands
#you will pip install ---> pip install openai==0.28
import openai
import random
import csv
from dotenv import load_dotenv 
import pandas as pd


load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

explicit_input = ""
chatgpt_output = 'Chat log: /n'
cwd = os.getcwd()
i = 1
 
# Delete the existing chat history file if it exists
if os.path.exists("chat_history.txt"):
    os.remove("chat_history.txt")

# Find an available chat history file
if not os.path.exists(os.path.join(cwd, f'chat_history.txt')):
    history_file = os.path.join(cwd, f'chat_history.txt')
    # Create a new chat history file
    with open(history_file, 'w') as f:
        f.write('\n')
else:
    history_file = os.path.join(cwd, f'chat_history.txt')


# Initialize chat history
chat_history = ''

#OPEN AI STUFF
#Put your key in the .env File and grab it here
openai.api_key = os.getenv("OPEN_API_KEY")


name = ''

role = 'customer service'
with open('movie_quotes.csv', 'r',encoding='utf-8') as data_file:
        # Read the contents of the file into a string variable
        file_contents = data_file.read()
with open('Catchphrase.csv','r',encoding='utf-8') as uva_file:
        catchphrase_file_contents = uva_file.read()
# Define the impersonated role with instructions
impersonated_role = f"""
    You are a bot that is dedicated to giving information about movies, more specifically about movie quotes 
    since all of the data you will be pulling from will be about movie quotes. Only use the CSV data to answer questions about movies.
    Respond with an error message if the question is anything not in the CSV data or if the question is unrelated to movies. You will
    always say "This question is unrelated to movies. I cannot answer that." if the question is irrelevant to movies or the data.
    You will be informed by the CSV data here: {file_contents} and {catchphrase_file_contents} and only use this data. If a user asks
    for a quote or catchphrase that is not from the data, tell them that that data is not present in the data you have stored."""

# Function to complete chat input using OpenAI's GPT-3.5 Turbo
def chatcompletion(user_input, impersonated_role, explicit_input, chat_history):
    output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        temperature=1,
        presence_penalty=0,
        frequency_penalty=0,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": f"{impersonated_role}. Conversation history: {chat_history}"},
            {"role": "user", "content": f"{user_input}. {explicit_input}"},
        ]
    )

    for item in output['choices']:
        chatgpt_output = item['message']['content']

    return chatgpt_output

# Function to handle user chat input
def chat(user_input):
    global chat_history, name, chatgpt_output
    current_day = time.strftime("%d/%m", time.localtime())
    current_time = time.strftime("%H:%M:%S", time.localtime())
    chat_history += f'\nUser: {user_input}\n'
    chatgpt_raw_output = chatcompletion(user_input, impersonated_role, explicit_input, chat_history).replace(f'{name}:', '')
    chatgpt_output = f'{name}: {chatgpt_raw_output}'
    chat_history += chatgpt_output + '\n'
    with open(history_file, 'a') as f:
        f.write('\n'+ current_day+ ' '+ current_time+ ' User: ' +user_input +' \n' + current_day+ ' ' + current_time+  ' ' +  chatgpt_output + '\n')
        f.close()
    return chatgpt_raw_output


#DISCORD STUFF
intents = discord.Intents().all()
client = commands.Bot(command_prefix="!", intents=intents)
movie_quotes_commands = file_contents.splitlines()
catchphrases = catchphrase_file_contents.splitlines()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    channel = client.get_channel(1178214602933284894)  # Replace YOUR_CHANNEL_ID with the actual channel ID
    if channel:
        await channel.send("Welcome to the Movie Bot! Send a message to talk to the bot or type !help to get specific commands.")
 
@client.command(brief='Here is a quote from a specific year', description='Specific year quote')
async def year(ctx,arg):
    found = False
    for quote in movie_quotes_commands:
        if str(arg) in quote:
            parts = quote.split('","')
            parts[0] = "Quote: " + parts[0] +'"'
            parts[1] = "Title: " + parts[1]
            parts[2] = "Type: " + parts[2]
            parts[3] = parts[3].replace('"', '')
            parts[3] = "Year: " + parts[3]
            ret = "```"
            for part in parts:
                ret += part + "\n"
            ret += "```"
            await ctx.send(ret)
            found = True
            break
    if not found:
        await ctx.send("No quotes found.")

@client.command(brief='Here is a random movie quote that ends with an exclamation mark', description='Random yelling quote')
async def yell(ctx):
    yell_quotes = [quote for quote in movie_quotes_commands if "!" in quote]
    
    if yell_quotes:
        random_yell_quote = random.choice(yell_quotes)
        parts = random_yell_quote.split('","')
        parts[0] = "Quote: " + parts[0] +'"'
        parts[1] = "Title: " + parts[1]
        parts[2] = "Type: " + parts[2]
        parts[3] = parts[3].replace('"', '')
        parts[3] = "Year: " + parts[3]
        ret = "```"
        for part in parts:
            ret += part + "\n"
        ret += "```"
        await ctx.send(ret)
    else:
        await ctx.send("No yell quotes found :(")

import pandas as pd
df = pd.read_csv("Catchphrase.csv")

@client.command(brief='Here is a random movie quote from the CSV file', description='Random movie quote')
async def catchphrase(ctx):
    print(catchphrases)
    random_quote = df.sample().values[0]
    ret = "```"
    ret += "Catchphrase: " + random_quote[0] + "\n"
    ret += "Movie:" + random_quote[1] + "\n"
    ret += "Context:" + random_quote[2] + "\n"
    ret += "```"
    await ctx.send(ret)

responses = 0
list_user = []


@client.event
async def on_message(message):
    print(message.content)
    if message.author == client.user:
        return
    print(message.author)
    print(client.user)
    print(message.content)
   # print("Thomas Jefferson Says:" + answer)
    #answer = "Thomas Jefferson Says:" + answer
    if message.content.startswith("!"):
        await client.process_commands(message)
    else:
        answer = chat(message.content)
        await message.channel.send(answer)


@client.command()
@commands.is_owner()
async def shutdown(context):
    exit()
 
client.run(TOKEN)
