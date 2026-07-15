import asyncio
import logging
import os

from twitchio.ext import commands
from twitchio import eventsub
from flask import Flask
from threading import Thread

app = Flask(__name__)


@app.route("/",methods=["GET"])
def home():
    return "Bot is running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
#logging.basicConfig(level=logging.DEBUG)

class GeneralCommands(commands.Component):

    @commands.command()
    async def ping(self, ctx):
        print("Ping command wexecuted")
        await ctx.send("Pong!")

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            client_id=os.environ["client_id"],
            client_secret=os.environ["client_secret"],
            bot_id=os.environ["bot_id"],
            owner_id=os.environ["owner_id"],
            prefix="!",
        )
        print("Bot init")


    async def event_error(self, error=None):
        print("ERROR:", error)

    async def setup_hook(self):
        print("setup_hook started")

        await self.add_token(
            os.environ["access_token"],
            os.environ["refresh_token"]
        )

        print("token added")

        await self.add_component(GeneralCommands())

        print("component added")

        chat = eventsub.ChatMessageSubscription(
            broadcaster_user_id=self.owner_id,
            user_id=self.bot_id
        )

        print("subscription created")

        await self.subscribe_websocket(chat)

        print("Chat subscription created")


    async def event_ready(self):
        print(f"Logged in as {self.bot_id}")
        me = await self.fetch_users(ids=[self.bot_id])

        print(me)

    async def event_message(self, message):
        print(f"Message from {message.chatter.name}: {message.text}")

        await self.process_commands(message)


async def main():
    try:
        print("Starting bot...")

        Thread(target=run_web, daemon=True).start()

        bot = Bot()

        print("About to start bot")

        await asyncio.wait_for(bot.start(), timeout=30)

    except Exception as e:
        print("MAIN ERROR:", repr(e))


if __name__ == "__main__":
    asyncio.run(main())