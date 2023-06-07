from AI import *
import asyncio
import discord
from discord.ext import commands

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
            messages = [f"{message.author.name}: {message.content}"]

        # send messages to AI
        question = message.content.replace(bot.user.mention, '').strip()

        # use AI to get response
        stream = AIStream('localhost:9999', 'ws://localhost:9999/api/v1/stream')
        context = "\n".join(messages)
        print(context)
        context += question + "\n"
        # trigger the iswritting event
        await message.channel.trigger_typing()
        try:
            rep = ""
            async for response in stream.run(context, message.author.name, True):
                await message.channel.trigger_typing()
                rep += response
                print(response, end='')
                sys.stdout.flush()
            if rep.startswith("Sarah: "):
                rep = rep.replace("Sarah: ", "")
            await message.reply(rep, mention_author=False)
            #stop writting status
        except Exception as e:
            print(e)
            await message.channel.send(":x: Sorry, I'm not available right now. Please try again later.")
    await bot.process_commands(message)
    


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
