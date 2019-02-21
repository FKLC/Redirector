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
                f"{message.author.display_name} mentioned you on https://discordapp.com/channels/{message.guild.id}/{message.channel.id}/"
            )


client.run(environ.get("TOKEN"), bot=True)
