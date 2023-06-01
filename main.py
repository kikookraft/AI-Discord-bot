import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    # Ignore les messages du bot lui-même
    if message.author == bot.user:
        return

    # Vérifie si le bot est mentionné dans le message
    if bot.user.mentioned_in(message):
        # Récupère le contexte en lisant les messages précédents
        context = await get_message_context(message)

        # Envoie la question à l'IA pour obtenir une réponse
        question = message.content.replace(bot.user.mention, '').strip()
        answer = await get_ai_response(question, context)

        # Envoie la réponse de l'IA sur Discord
        await message.channel.send(answer)

    await bot.process_commands(message)

async def get_message_context(message):
    # Récupère les derniers messages dans le même channel
    channel = message.channel
    messages = await channel.history(limit=5).flatten()
    context = [msg.content for msg in messages if msg.author != bot.user]

    return context

async def get_ai_response(question, context):
    # Appel à votre IA pour obtenir une réponse en fonction de la question et du contexte
    # Remplacez cette fonction par votre propre logique d'appel à l'IA
    # Vous pouvez utiliser des bibliothèques d'IA telles que OpenAI GPT-3 ou TensorFlow

    # Exemple simplifié avec une réponse aléatoire
    import random
    answers = ["Je ne suis pas sûr.", "Peut-être.", "Je vais vérifier.", "C'est possible.", "Je ne pense pas.", "Non."]
    return random.choice(answers)

#lecture du token du bot
with open('token', 'r') as file:
    token = file.read().rstrip()
bot.run(token)
