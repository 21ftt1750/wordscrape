import discord
from discord.ext import commands
import csv
import os
from dotenv import load_dotenv
import random
from borneoBulettin import scrape_and_save_news  # Import the function

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
        emoji = '📰'  # Example emojis
        button = discord.ui.Button(label=f" {category.capitalize()} {emoji}", style=discord.ButtonStyle.secondary)
        button.callback = create_button_callback(category)
        view.add_item(button)
    
    # Send the category selection message with buttons
    message = await ctx.send("Please choose a category! 🧙🏻‍♂️🪄✨", view=view)

@client.event
async def on_button_click(interaction, category):
    news = read_csv(category)
    if news:
        await interaction.channel.send(f'Here are some of the latest **{category.capitalize()} news** headlines:')
        for article in news:
            await interaction.channel.send(content=article)
    else:
        await interaction.channel.send(content=f'No {category.capitalize()} news found.')
    
    # After displaying news, send category selection again
    await send_category_selection(interaction.channel, category)

@client.event
async def on_ready():
    print(f'{client.user} is now running!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!news'):  # Check if the message starts with the prefix '!news'
        await message.channel.send("Fetching latest news, please wait...")
        scrape_and_save_news()  # Call the function to scrape news
        await send_category_selection(message.channel)  # Proceed with sending the news
    elif message.content.startswith('!help'):  # Check if the message starts with the prefix '!help'
        await message.channel.send("Available Commands:\n- **!news**: Get the latest news from Borneo Bulletin.\n- **?news**: Get the latest news from Borneo Bulletin via DM.")
    elif message.content.startswith('!'):
        # Handle other commands with the prefix
        responses = [
            "I didn't quite catch that command 😓 Please type **'!news'** to get the latest news. **'!help'** to see all the available commands!",
            "Can you repeat that 🤔 or type **'!news'** to start. **'!help'** to see all the commands we have!",
            "Sorry, I don't understand that 🤨 Please use **'!news'** to begin. **'!help'** for more options!"
        ]
        response = random.choice(responses)
        await message.channel.send(response)
    elif message.content.startswith('?news'):  # Check if the message starts with the prefix '?news' for DM
        await message.author.send("Fetching latest news, please wait...")
        scrape_and_save_news()  # Call the function to scrape news
        await send_category_selection(message.author)  # Send the category selection message as DM

def main():
    client.run(TOKEN)

if __name__ == '__main__':
    main()
