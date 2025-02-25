# Reddit Post Notifier Bot

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads)

A Discord bot that notifies users when new posts are made in subreddits they subscribe to. Built using discord.py and PRAW.

## Overview

This Discord bot allows users to subscribe to subreddits and receive notifications whenever a new post is made.  It leverages the power of discord.py for Discord integration and PRAW for interacting with the Reddit API.  Users can easily subscribe and unsubscribe to subreddits using simple commands.

## Features

*   **Subreddit Subscription:** Users can subscribe to any subreddit.
*   **New Post Notifications:** The bot will mention subscribed users when a new post is made in their chosen subreddit.
*   **Embed Messages:** Notifications are sent as rich embeds, including the post title, description (truncated if needed), link, author, score, comment count, and media (images or videos).
*   **NSFW Post Handling:**  NSFW posts are flagged in the embed.
*   **Easy Setup:** Simple configuration process.
*   **Job Persistence:** Subscriptions are saved and loaded, so they persist across bot restarts.

## Getting Started

### Prerequisites

*   Python 3.7+
*   Required Python packages: `discord.py`, `asyncpraw`, `python-dotenv`
*   A Discord bot token.  See the [Discord Developer Portal](https://discord.com/developers/applications) for instructions on creating a bot and obtaining a token.
*   Reddit API credentials (client ID, client secret, user agent).  See the [Reddit API documentation](https://www.reddit.com/dev/api/) for instructions on creating an app and obtaining credentials.

### Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/bigmacstorm/discord-bot.git
    ```

2.  Navigate to the project directory:

    ```bash
    cd discord-bot
    ```

3.  Create a virtual environment (recommended):

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

4.  Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

5.  Create a `.env` file in the project directory and add your Discord bot token and Reddit API credentials:

    ```
    SECRET_KEY=YOUR KEY HERE
    REDDIT_CLIENT_SECRET=YOUR SECRET HERE
    REDDIT_CLIENT_ID=YOUR CLIENT ID HERE
    REDDIT_USER_AGENT=YOUR_REDDIT_USER_AGENT  # Example: "discord-bot:v1.0 (by /u/YOUR_REDDIT_USERNAME)"
    ```

### Running the Bot

```bash
python discord-bot.py
```

## Usage

### Commands

*   `!subscribe <subreddit>`: Subscribe to a subreddit.
*   `!unsubscribe <subreddit>`: Unsubscribe from a subreddit.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Todo

*   [ ] Implement a command to list subscribed subreddits.
*   [ ] Add support for a logging framework
*   [ ] Implement error handling for invalid subreddit names.
*   [ ] Add a help command.
*   [ ] Improve embed formatting.
*   [ ] Implement unit tests.
*   [ ] Add more robust error handling for network issues.
*   [ ] Switch to using the discord slash format instead of the text prefix search.
*   [ ] Determine if its appropriate to convert the bot into an application.

## Acknowledgements

*   Thanks to the developers of discord.py and PRAW for their excellent libraries.

## Contact

If you have any questions or suggestions, please feel free to open an issue or contact me.