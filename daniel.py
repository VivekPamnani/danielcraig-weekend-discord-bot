import discord
from discord.ext import tasks, commands
import datetime
from dotenv import load_dotenv
import os
import json

load_dotenv()
# intents = discord.Intents(messages=True)
# client = commands.Bot(command_prefix='$')
client = discord.Client(intents=discord.Intents.all())

# This function will be called every week to post the GIF
@tasks.loop(hours=168)
async def post_gif(channel):
    # Send the GIF to the channel
    await channel.send('https://tenor.com/view/james-bond-the-weeknd-daniel-craig-007-gif-21565879')

# This function is called on request, will loop every minute and when the time is right, will start the post_gif task loop.
@tasks.loop(minutes=1)
async def set_time(channel):
    dt = datetime.datetime.now()
    if(dt.weekday() == 5 and dt.hour >= 19 and dt.minute >= 15):
        if not post_gif.is_running():
            post_gif.start(channel)

# When the bot is ready. Just a simple console message.
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

# When a message is sent in the server. Daniel will send the GIF in the channel the first 'Daniel start' message happened. 
# The GIF channel can be changed by invoking 'Daniel stop' in the current channel followed by 'Daniel start' in the desired channel.
@client.event
async def on_message(message):
    # Ignore messages from Daniel.
    if message.author == client.user:
        return
    
    # If 'Daniel start', start.
    if(message.content == 'Daniel start'):
        # print("Is post_gif running?", "Yes" if post_gif.is_running() else "No")
        # print("Is set_time running?", "Yes" if set_time.is_running() else "No")

        filename = message.guild.id

        # If bot is new to a server, create a .json file for that server with the default state.
        if not os.path.exists(str(filename) + '.json'):
            with open(str(filename) + '.json', 'w') as f:
                default_state = { 
                    'START_PROMPT_COUNT': 0,
                    'FIRST_PROMPT_TIME': '1000-01-01 00:00:00'
                }
                json.dump(default_state, f)

        # Read the .json file corresponding the current server, and update the state.          
        with open(str(filename) + '.json', 'r') as f:
            state = json.load(f)
            state['START_PROMPT_COUNT'] += 1
            first_prompt_time = datetime.datetime.strptime(state['FIRST_PROMPT_TIME'], "%Y-%m-%d %H:%M:%S")
            if(first_prompt_time + datetime.timedelta(minutes=15) < datetime.datetime.now()):
                state['START_PROMPT_COUNT'] = 1
                state['FIRST_PROMPT_TIME'] = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")

        # Save the updated state in the .json file.
        with open(str(filename) + '.json', 'w') as f:
            json.dump(state, f)

        # Check if task is already in motion. 
        # If not, start the tasks.
        if not set_time.is_running() and not post_gif.is_running():
            set_time.start(message.channel)
            await message.channel.send("Weekend is coming. Daniel is watching the clock.")
        # Else, have fun.
        else:
            match state['START_PROMPT_COUNT']:
                case 1:
                    await message.channel.send("Weekend is coming. Daniel is watching the clock.")
                case 2:
                    await message.channel.send("Daniel is on a chair right in front of clock, don't worry.")
                case 3:
                    await message.channel.send("I know you're really excited for the weekend, but rest assured Daniel is watching the clock for you.")
                case 4:
                    await message.channel.send("Here's a <3 personally sent by Daniel himself, he's by the clock.")
                case 5:
                    await message.channel.send("Bored? Try chat.openai.com, go nuts!")
                case default:
                    await message.channel.send("I can't entertain you further, I'm sorry. :(")

        # If post_gif is already running, stop the set_time task.
        # There is a nuance here that if we invoke 'Daniel start' only once, the interpreter might reach here before the task has started (because it is async).
        if post_gif.is_running():
            set_time.stop()
        
        # print("Is post_gif running?", "Yes" if post_gif.is_running() else "No")
        # print("Is set_time running?", "Yes" if set_time.is_running() else "No")

    # If 'Daniel stop', stop.
    elif(message.content == 'Daniel stop'):
        await message.channel.send("Daniel stopped. And then they lived the rest of their lives hoping for a weekend to arrive.")
        if set_time.is_running():
            set_time.stop()
        if post_gif.is_running():
            post_gif.stop()

# Save your bot's API token in a .env file as "API_TOKEN=<your token>"
client.run(os.environ.get('API_TOKEN'))
