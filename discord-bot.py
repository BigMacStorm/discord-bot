import os
from dotenv import load_dotenv
import discord
import praw
from discord.ext import tasks

load_dotenv()
reddit_user_agent = "discord-bot:v1.0 (by /u/bigmacstorm)"

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reddit = praw.Reddit(client_id=os.environ.get('REDDIT_CLIENT_ID'),
                                  client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
                                  user_agent=reddit_user_agent)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!hello'):
            await message.reply('Hello!', mention_author=True)

        if message.content.startswith('!get'):
            subreddit = self.reddit.subreddit(self.get_subreddit(message.content))
            output = ''
            for submission in subreddit.new(limit=5):
                output += f'{submission.title}\n'
            await message.reply(output, mention_author=True)
    
    def get_subreddit(self, content: str):
        index = content.find('!get')
        words = content[index:].split()
        return words[1]



intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(os.environ.get('SECRET_KEY'))