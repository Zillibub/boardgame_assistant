import discord
import openai
import time
from discord import Interaction
from discord.ext import commands
from discord import app_commands
from settings import settings

intents = discord.Intents.default()
intents.message_content = True

# Your OpenAI API Key
openai_key = 'YOUR_OPENAI_API_KEY'
discord_client = commands.Bot(command_prefix='!', intents=intents)
openai_client = openai.Client(api_key=openai_key)

# List of available assistants
assistants = {
    "Assistant1": "assistant_id_1",
    "Assistant2": "assistant_id_2",
    "Assistant3": "assistant_id_3"
}

# A dictionary to store threads for each chat
chat_threads = {}


# The logic to create a new assistant and thread should be added here
def create_assistant_and_thread():
    # Use the OpenAI API to create the assistant and thread
    thread = openai_client.beta.threads.create()
    # Return the assistant_id and thread_id
    return thread.id


@discord_client.event
async def on_ready():
    print(f'We have logged in as {discord_client.user}')
    try:
        synced = await discord_client.tree.sync()
        print(f'Synced: {len(synced)} commands')
    except Exception as e:
        print(e)


@discord_client.tree.command(name="get_assistants")
async def get_assistants(interaction: discord.Interaction):
    await interaction.response.send_message(f'Available assistants: {assistants}')


@discord_client.hybrid_command(name='select_assistant', description='Select an assistant for this chat.')
async def select_assistant(ctx, assistant_name):
    if assistant_name in assistants:
        thread = openai_client.beta.threads.create()
        chat_threads[ctx.channel.id] = (assistants[assistant_name], thread.id)

        await ctx.send(f'Selected {assistant_name} as your assistant.')
    else:
        await ctx.send(f'No assistant named {assistant_name} found.')


@discord_client.command(name='current_assistant', description='Get the current assistant for this chat.')
async def current_assistant(ctx):
    if ctx.channel.id in chat_threads:
        assistant_id, thread_id = chat_threads[ctx.channel.id]
        await ctx.send(f'Current assistant: {assistant_id}')
    else:
        await ctx.send('No assistant selected.')


@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    if discord_client.user.mentioned_in(message):
        # If the command is a question for the assistant

        if message.channel.id in chat_threads:
            # If an assistant has been selected for this chat

            assistant_id, thread_id = chat_threads[message.channel.id]
            result = await answer(message.content, assistant_id, thread_id)
            for r in result:
                await message.channel.send(r)
        else:
            # If no assistant has been selected for this chat

            await message.channel.send('Please select an assistant first.')
    else:
        # If the message is not a command for the bot
        await discord_client.process_commands(message)


async def answer(question, assistant_id, thread_id):
    run = openai_client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=question
    )
    while run.status == "queued" or run.status == "in_progress":
        run = openai_client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        time.sleep(0.2)

    messages = openai_client.beta.threads.messages.list(
        thread_id=thread_id
    )
    return messages


discord_client.run(settings.discord_bot_token)
