import os

import discord
from discord.ext import commands, tasks
import dbl

bot = commands.Bot(command_prefix="r!", help_command=None)
bot.redirect_counter = 0


@bot.event
async def on_ready():
    presence_updater.start()


@bot.event
async def on_message(message):
    for mention in message.raw_mentions:
        message.content = message.content.replace(f"<@{mention}>", "")
        message.content = message.content.replace(f"<@!{mention}>", "")

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
        bot.redirect_counter += len(message.mentions)
        return
    await bot.process_commands(message)


@bot.command()
async def to(ctx, channel: str, limit_or_after_id: int, before_id: int = 0):
    if len(ctx.message.channel_mentions) == 1:
        if limit_or_after_id > 25 and before_id != 0:
            before_message = await ctx.channel.fetch_message(before_id)
            after_message = await ctx.channel.fetch_message(limit_or_after_id)
            messages = [
                before_message,
                *(
                    await ctx.history(
                        limit=25, before=before_message, after=after_message
                    ).flatten()
                ),
                after_message,
            ]
        elif limit_or_after_id > 25 and before_id == 0:
            await ctx.send(f"You can't redirect more than 25 messages at a time!")
        else:
            messages = await ctx.history(limit=limit_or_after_id + 1).flatten()
            messages.reverse()

        embed = discord.Embed(
            title="Messages Redirected",
            description=f"Source Channel: #{ctx.channel.name}",
        )
        for message in messages:
            embed.add_field(
                name=f"{message.author.name}#{message.author.discriminator} ({message.author.nick})",
                value=message.content if message.content else "<Unsupported Content>",
                inline=False,
            )
        await ctx.message.channel_mentions[0].send(embed=embed)
        await ctx.channel.delete_messages(messages)
        bot.redirect_counter += len(messages)
    else:
        await ctx.send(f"Channels must be mentioned like `#{channel}`")


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Redirector Bot",
        description="Redirector Bot is a discord server moderation bot. "
        "It helps you to keep clean your chat with removing and sending "
        "DMs to users if message content is only mention of users. "
        "Also it can redirect messages to other channels. "
        "List of commands are:",
        color=0xEEE657,
    )

    embed.add_field(
        name="@<someone>",
        value="Redirects any mention to mentioned user DM if message content is empty",
        inline=False,
    )
    embed.add_field(
        name="r!to #channel last_n_messages",
        value="Redirects last n messages into the mentioned channel",
        inline=False,
    )
    embed.add_field(
        name="r!to #channel after_message_id before_message_id",
        value="Redirects messages around after_message_id and before_message_id into the mentioned channel",
        inline=False,
    )

    await ctx.send(embed=embed)


@tasks.loop(seconds=60)
async def presence_updater():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(
            name=f"FKLC.dev | r!help | {bot.redirect_counter} messages redirected!"
        ),
    )


class DBLAPI(commands.Cog):
    """Handles interactions with the discordbots.org API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = os.environ.get("DBL_TOKEN")
        self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True)


bot.add_cog(DBLAPI(bot))
bot.run(os.environ.get("TOKEN"))
