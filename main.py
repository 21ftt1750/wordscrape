import discord
from discord.ext import commands
import csv
import os
from dotenv import load_dotenv
import random
from borneoBulettin import scrape_and_save_news  

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

def read_csv(category):
    with open('borneo_bulletin.csv', 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        filtered_rows = [row for row in reader if row['Category'].lower() == category.lower()]
        articles = [f"\n**Article {index + 1}:** {row['Article']}\n**Date Published:** {row['Date']}\n**Link:** {row['Link']}" for index, row in enumerate(filtered_rows)]
        return articles

def create_button_callback(category):
    async def button_callback(interaction: discord.Interaction):
        await on_button_click(interaction, category)
    return button_callback

async def send_category_selection(ctx, selected_category=None):
    categories = ['national', 'sea', 'world', 'business', 'technology', 'lifestyle', 'entertainment', 'sports', 'features']
    view = discord.ui.View()
    for category in categories:
        emoji = '📰'  
        button = discord.ui.Button(label=f" {category.capitalize()} {emoji}", style=discord.ButtonStyle.secondary)
        button.callback = create_button_callback(category)
        view.add_item(button)
    
    # Send the category selection message with buttons
    message = await ctx.send("Enter the realm of magic! 🧙🏻‍♂️ Choose a mystical category! 🪄✨", view=view)

@client.event
async def on_button_click(interaction, category):
    news = read_csv(category)
    if news:
        await interaction.channel.send(f'Behold! Herein lie the freshest chronicles of **{category.capitalize()} news**:')
        for article in news:
            await interaction.channel.send(content=article)
    else:
        await interaction.channel.send(content=f'No {category.capitalize()} news found.')

    await send_category_selection(interaction.channel, category)

@client.event
async def on_ready():
    print(f'{client.user} is now running!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!scrolls'):  # Check if the message starts with the prefix '!scrolls'
        await message.channel.send("Gather ye, for the ethereal threads of the latest tidings beckon, a moment's patience I seek... 🔮")
        scrape_and_save_news()  # Call the function to scrape news
        await send_category_selection(message.channel)  # Proceed with sending the news
    elif message.content.startswith('!sorcery'):  # Check if the message starts with the prefix '!sorcery'
        await message.channel.send("Behold, the ethereal commands beckon: \n- **!scrolls**: Unravel the latest mystical scrolls from Borneo Bulletin. \n- **?scrolls**: Receive the enigmatic whispers of Borneo Bulletin's news through the mystic channels of DMs.")
    elif message.content.startswith('!'):
        # Handle other commands with the prefix
        responses = [
            "Lost amidst the arcane whispers 🌪️ Venture forth with '**!scrolls**' for the latest lore. Unveil all secrets using '**!sorcery**' 🌟!",
            "An enigma hangs in the air 🌀 Embrace '**!scrolls**' to uncover hidden 🧙‍♂️ realms, or invoke '**!sorcery**' for celestial guidance 🌌!",
            "Apologies for the mystical haze 🌌 Embark on your journey with '**!scrolls**' 📜. Plunge deeper into the unknown with '**!sorcery**' ✨!"


        ]
        response = random.choice(responses)
        await message.channel.send(response)
    elif message.content.startswith('?scrolls'):  # Check if the message starts with the prefix '?scrolls' for DM
        await message.author.send("Gather ye, for the ethereal threads of the latest tidings beckon, a moment's patience I seek... 🔮")
        scrape_and_save_news()  # Call the function to scrape news
        await send_category_selection(message.author)  # Send the category selection message as DM

def main():
    client.run(TOKEN)

if __name__ == '__main__':
    main()
