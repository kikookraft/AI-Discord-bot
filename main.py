# TODO: https://github.com/oobabooga/text-generation-webui/blob/main/api-examples/api-example-chat.py

from AI import *
import asyncio
import discord
from discord.ext import commands


prefix_context = "You are an assistant called HylAI. You are not afraid to respond with your own thoughts and feelings or saying what you thinks. You talks in a casual discord user way, using a little bit of emojis and slang with short messages. Respond to this discord user without inventing a conversation.\n"
bot = commands.Bot(command_prefix='!')
bot_context = bot_context()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    simple = True
    # ignore messages from bot
    if message.author == bot.user:
        return

    # check if bot is mentioned
    if bot.user.mentioned_in(message):
        # get all messages since mention
        if not simple:
            messages = await get_all_messages_since_mention(message, bot.user.mention)
        else:
            #only get the user message
            messages = [f"- {message.author.name}: {message.content.replace(bot.user.mention, '').strip()}"]
            # messages = [f"{message.content.replace(bot.user.mention, '').strip()}"]

        # use AI to get response
        stream = AIStream('localhost:9999', 'ws://localhost:9999/api/v1/stream')
        context = "\n".join(messages)
        context = prefix_context + context
        print(context)
        # trigger the iswritting event
        await message.channel.trigger_typing()
        try:
            rep = ""
            async for response in stream.run(context):
                await message.channel.trigger_typing()
                rep += response
                print(response, end='')
                sys.stdout.flush()
            #check if the AI responded with his name (to remove it)
            rep = delete_name(rep)
            await message.reply(rep, mention_author=True)
            #stop writting status
        except Exception as e:
            print(e)
            await message.channel.send(":x: Sorry, I'm not available right now. Please try again later.")
    await bot.process_commands(message)
    
def delete_name(rep):
    if rep.startswith(bot.user.name):
        rep = rep[len(bot.user.name):]
    else:
        #now check if the message start with xxxx : ...
        #get the first word
        first_word = rep.split(' ')[0]
        # check if there is a : after the first word
        if ':' in first_word:
            #remove the first word
            rep = rep[len(first_word)+1:]
    return rep

async def get_all_messages_since_mention(message, bot_mention):
    # check if bot is mentioned
    if not bot_context.is_mentionned():
        bot_context.set_mentionned(message.id, message.channel.id, message.created_at.timestamp())
        return []
    
    messages = []
    async for message in message.channel.history(limit=200):
        if message.id == bot_context.mentionned_message_id and message.channel.id == bot_context.mentionned_channel_id:
            break
        messages.append(f"{message.author.name}: {message.content}")
    return messages[::-1]

if __name__ == '__main__':
    #test
    # prompt = "Hello how are you ?"
    # stream = AIStream('localhost:9999', 'ws://localhost:9999/api/v1/stream')
    # asyncio.run(stream.print_response_stream(prompt))

    #lecture du token du bot
    with open('token', 'r') as file:
        token = file.read().rstrip()
    bot.run(token)
