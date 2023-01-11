#!/usr/bin/env python3

import os
import sys

import discord

MAX_MESSAGE_SIZE = 1500
PATH_TO_LAST_MESSAGE = os.path.join(os.path.dirname(__file__), "last_message.log")


token = os.environ.get("FISH_BOT_TOKEN")
channel_id = int(os.environ.get("FISH_BOT_CHANNEL_ID"))

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


def process_message(msg: str, mention="", odmen_mention="") -> str:
    if "INFO" in msg:
        msg += "\n"
    if "DEBUG" in msg:
        msg = ""
    elif "WARNING" in msg:
        msg = "**{}** {}\n".format(msg.strip(), mention)
    elif "ERROR" in msg:
        msg = "**{}** {} {}\n".format(msg.strip(), mention, odmen_mention) 
    return msg


def read_messages(file, mention="", odmen_mention=""):
    need_to_close = False
    if isinstance(file, str):
        need_to_close = True
        file = open(file, "r")

    messages = []
    msg = ""
    current_content = file.read()

    if need_to_close:
        file.close()

    # read last message content
    if os.path.exists(PATH_TO_LAST_MESSAGE):
        with open(PATH_TO_LAST_MESSAGE) as fin:
            last_message_content = fin.read()
    else:
        last_message_content = ""

    # check that current message differs from last sent message
    if current_content == last_message_content:
        msg = "ERROR: there are no new logs, maybe fish-factory laptope cannot send logs to the bot server {} {}".format(mention, odmen_mention)
        messages.append(msg)
        return messages
    
    # update last message file content
    with open(PATH_TO_LAST_MESSAGE, "w") as fout:
        last_message_content = fout.write(current_content)

    for line in current_content.split("\n"):
        line = process_message(line, mention, odmen_mention)

        if "ERROR" in line or "WARNING" in line:
            if len(msg):
                messages.append(msg)
            messages.append(line)
            msg = ""
        else:
            msg += line

        if len(msg) > MAX_MESSAGE_SIZE:
            messages.append(msg)
            msg = ""

    messages.append(msg)
    return messages


@client.event
async def on_ready():
    try:
        ch = client.get_channel(channel_id)
        g = discord.utils.get(client.guilds, name="mitoclub")

        # role = discord.utils.get(g.roles, name="fisherman")
        user1 = g.get_member_named("byqot")
        user2 = g.get_member_named("kpotoh")

        messages = read_messages(sys.stdin, user1.mention, user2.mention)  # role.mention
        for m in messages:
            await ch.send(m)
        
    except Exception as e:
        print(repr(e))
    finally:
        print("Bot logging out")
        await client.close()


if __name__ == '__main__':
    client.run(token)    
