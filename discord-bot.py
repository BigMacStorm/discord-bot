import os
from dotenv import load_dotenv
import discord
import asyncpraw
from discord.ext import tasks
import asyncio
from prawcore.exceptions import RequestException
import socket
import pickle
import signal
import sys
import os
import datetime

load_dotenv()
reddit_user_agent = ""

class Job():
    def __init__(self, user_id, subreddit_name, channel_id):
        self.user_id = user_id
        self.channel_id = channel_id
        self.subreddit_name = subreddit_name
        self.last_post_time = None
    
    def get_last_post_time(self):
        return self.last_post_time

    def set_last_post_time(self, time):
        self.last_post_time = time

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_task = None
        self.jobs = []

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        self.load_jobs()

    async def setup_hook(self):
        self.bg_task = self.loop.create_task(self.job_processing_loop())

    async def process_single_job(self, job):
        try:
            async with asyncio.timeout(5):  # Timeout for the *entire job processing*
                subreddit = await self.reddit.subreddit(job.subreddit_name)
                submission_list = []
                async for submission in subreddit.new(limit=5):
                    submission_list.append(submission)

                submission_list.reverse() # Reverse the list

                for submission in submission_list:
                    if job.get_last_post_time() is None or submission.created_utc > job.get_last_post_time():
                        embed = self.build_embed(submission)
                        try:
                            channel = await self.fetch_channel(job.channel_id) # Needs await
                            await channel.send(f"<@{job.user_id}>", embed=embed) # Needs await
                            job.set_last_post_time(submission.created_utc)
                        except Exception as e:
                            print(f"Error sending message: {e}")
            self.save_jobs()  # Save jobs *after* processing within the timeout

        except (RequestException, socket.gaierror, ConnectionRefusedError, asyncio.TimeoutError) as e: # Include TimeoutError
            print(f"Error fetching posts from {job.subreddit_name}: {e}")
            await asyncio.sleep(20)  # Sleep after error (important!)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    async def job_processing_loop(self):
        await self.wait_until_ready()
        while not self.is_closed():
            while not self.reddit: # Wait for reddit to be initialized
                await asyncio.sleep(1)
            await asyncio.sleep(10)
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Checking for new posts...")
            tasks = [self.process_single_job(job) for job in self.jobs]
            await asyncio.gather(*tasks)
            

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!subscribe'):
            await self.add_subscription(message)

        if message.content.startswith('!unsubscribe'):
            await self.remove_subscription(message)
    
    def build_embed(self, submission):
            embed = discord.Embed(
                title=submission.title,
                description=submission.selftext[:2000] + "..." if submission.selftext else "",
                url=f"https://www.reddit.com{submission.permalink}",
                color=discord.Color.blue()
            )

            
            embed.set_author(name=f"/u/{submission.author.name}", url=f"https://www.reddit.com/u/{submission.author.name}")
            if submission.over_18:
                embed.add_field(name="NSFW", value="This post is NSFW", inline=True)
            embed.add_field(name="Score", value=submission.score, inline=True)
            embed.add_field(name="Comments", value=submission.num_comments, inline=True)

            if submission.is_video:
                embed.add_field(name="Video Post", value="This post contains a video", inline=True)
            elif submission.is_self:
                pass 
            elif submission.url: 
                try:
                    embed.set_image(url=submission.url) 
                except:
                    embed.add_field(name="Link", value=submission.url, inline=True) 
            return embed

    
    def get_subreddit_name(self, content: str):
        index = content.find(' ')
        words = content[index-1:].split()
        return words[1]

    async def add_subscription(self, message):
        job = Job(message.author.id, self.get_subreddit_name(message.content).lower(), message.channel.id)
        try:
            self.add_to_jobs(job)
            await message.reply(f'Subscribed to {job.subreddit_name}', mention_author=True)
        except Exception as e:
            print(f"Error adding job: {job} - {e}")
            await message.reply(f'Failure to subscribe to {job.subreddit_name}, please try again.', mention_author=True)

    async def remove_subscription(self, message):
        subreddit = await self.reddit.subreddit(self.get_subreddit_name(message.content).lower())
        try:
            self.remove_from_jobs(message, subreddit)
            await message.reply(f'Unsubscribed to {subreddit.display_name}', mention_author=True)
        except Exception as e:
            print(f"Error removing job: {message.user}, {subreddit} - {e}")
            await message.reply(f'Failure to unsubscribe to {subreddit.display_name}, please try again.', mention_author=True)
            

    def load_jobs(self):
        try:
            with open('jobs.pkl', 'rb') as f:
                self.jobs = pickle.load(f)
        except (FileNotFoundError, EOFError):
            print('No subscriptions found on load, this could be normal')
    
    def save_jobs(self, error=False):
        try:
            jobs_copy = self.jobs.copy()
            with open('jobs.pkl', 'wb') as f:
                pickle.dump(jobs_copy, f)
        except Exception as e:
            print(f"Error saving subscriptions: {e}")
            if error:
                raise e
    
    def add_to_jobs(self, job):
        self.load_jobs()
        self.jobs.append(job)
        try:
            self.save_jobs(error=True)
        except Exception as e:
            self.jobs.remove(job)
            raise e
    
    def remove_from_jobs(self, message, subreddit):
        self.load_jobs()
        for job in self.jobs:
            if job.user_id == message.author.id and job.subreddit_name == subreddit.display_name:
                self.jobs.remove(job)
        self.save_jobs(error=True)

async def main():
    reddit = asyncpraw.Reddit(client_id=os.environ.get('REDDIT_CLIENT_ID'),
                            client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
                            user_agent=os.environ.get('REDDIT_USER_AGENT'))

    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    client.reddit = reddit

    try: # Add try/except block
        await client.start(os.environ.get('SECRET_KEY')) # Use client.start()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally: # Add finally block
        await reddit.close()
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
    