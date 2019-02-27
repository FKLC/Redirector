import discord
from os import environ

client = discord.Client()


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")


@client.event
async def on_message(message):
    if message.content.lower() == "mr!help":
        await message.channel.send(
            "MentionRedirector Bot is a discord server moderation bot. It"
            " helps you to keep clean your chat with removing and sending"
            " DMs to users if message content is only mention of users."
        )
    else:
        for mention in message.raw_mentions:
            message.content = message.content.replace(
                f"<@{mention}>", ""
            )
            message.content = message.content.replace(
                f"<@!{mention}>", ""
            )
        if (
            message.type == discord.MessageType.default
            and not message.content.strip()
            and not message.attachments
            and not message.embeds
        ):
            await message.delete()
            for mentioned_user in message.mentions:
                await mentioned_user.send(
                    f"{message.author.display_name} mentioned you on"
                    f" https://discordapp.com/channels/{message.guild.id}/{message.channel.id}/"
                )


client.run(environ.get("TOKEN"), bot=True)
