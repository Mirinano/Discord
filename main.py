#!python3.6
import sys, os
import asyncio
import threading
import time, datetime
import json
import shutil
import re

import discord

import bot
from __init__ import Developer
import log_format
import fw_wrap
import cmd_trigger

try:
    name = sys.argv[1]
except:
    name = input("BOT NAME: ")

config_file = "./config/{}.json".format(name)

try:
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)
except:
    print("config file is not found!!!")
    sys.exit(0)

client = discord.Client()

bot = bot.Bot(config, client)

@client.event
async def on_ready():
    print("Launch completed")
    await bot.launch_report()
    # login action
    await bot.login()
    # send last day log file for zipfile
    if config["send_logzipfile"]:
        await bot.send_msg_logs()

@client.event
async def on_message(message):
    if bot.check_server(message.channel):
        await bot.spam_alert(message)

        if config["save_message_log"]:
            bot.save_msg_log(message)
        
        #user only action
        if message.author != client.user:
            if config["translation"]:
                if config.get("auto_translation"):
                    if message.channel.id == config["auto_translation_ch"]:
                        await bot.auto_translation(message)
                if bot.check_cmd_start(message, cmd_trigger.translation): #tranlsation
                    await bot.translation_bot(message)

            if config["auto_role"]:
                if message.channel.id == config["auto_role_ch"]:
                    await bot.role_control(message)

            if bot.check_cmd_start(message, cmd_trigger.ban): #ban
                await bot.ban(message)
            elif bot.check_cmd_start(message, cmd_trigger.unban): #unban
                await bot.unban(message)
            elif bot.check_cmd_start(message, cmd_trigger.kick): #kick
                await bot.kick(message)
            elif bot.check_cmd_start(message, cmd_trigger.stop): #stop
                await bot.stop(message)
            elif bot.check_cmd_start(message, cmd_trigger.send_dm): #send dm
                await bot.send_dm(message)
            elif bot.check_cmd_start(message, cmd_trigger.edit_dm): #edit dm
                await bot.edit_msg(message, True, op=cmd_trigger.edit_dm[1])
            elif bot.check_cmd_start(message, cmd_trigger.del_dm): #del dm
                await bot.del_dm(message)
            elif bot.check_cmd_start(message, cmd_trigger.get_dm): #get dm
                await bot.get_msg_log(message, True, op=cmd_trigger.get_dm[1])
            elif bot.check_cmd_start(message, cmd_trigger.cmd_help): #help
                await bot.help(message)
            elif bot.check_cmd_start(message, cmd_trigger.statistics): #statistics
                await bot.statistics_cmd(message)
            elif bot.check_cmd_start(message, cmd_trigger.spam): #spam
                await bot.spam_cmd(message)
            elif bot.check_cmd_start(message, cmd_trigger.alert): #alert
                await bot.alert_cmd(message)
            elif bot.check_cmd_start(message, cmd_trigger.user): #user
                await bot.user(message)
            elif bot.check_cmd_start(message, cmd_trigger.send_msg): #send_msg
                await bot.send_msg(message)
            elif bot.check_cmd_start(message, cmd_trigger.edit_msg): #edit_msg
                await bot.edit_msg(message)
            elif bot.check_cmd_start(message, cmd_trigger.get_msg_log): #get_msg_log
                await bot.get_msg_log(message)
            elif bot.check_cmd_start(message, cmd_trigger.ls): #ls
                await bot.ls(message)
            elif bot.check_cmd_start(message, cmd_trigger.system_message): #system_message
                await bot.system_message(message)
            else:
                pass

    if message.author != client.user:
        if not isinstance(message.channel, discord.TextChannel):
            if config["receive_dm"]:
                await bot.receive_dm(message)

    # send message log
    if config["send_logzipfile"]:
        await bot.log_request(message)
        if bot.check_cmd_start(message, cmd_trigger.send_zip): #force send msg log
            await bot.send_msg_logs()
        elif bot.check_cmd_start(message, cmd_trigger.send_today_zip): #send today's msg log
            await bot.send_today_msg_log()
        else:
            pass
    
    if bot.check_cmd_start(message, cmd_trigger.mass_spam): #mass spam
        await bot.spam(message, cat="global")

    # test
    if message.content.startswith("&&test&&"):
        await bot.test(message)

@client.event
async def on_message_edit(before, after):
    if bot.check_server(before.channel):
        await bot.spam_alert(after)
        if config["save_message_log"]:
            bot.save_msg_change_log(before, after)
        else:
            pass
    if before.author != client.user:
        if not isinstance(before.channel, discord.TextChannel):
            await bot.receive_dm_edit(before, after)

@client.event
async def on_message_delete(message):
    if bot.check_server(message.channel):
        if config["save_message_log"]:
            bot.save_msg_delete_log(message)
        else:
            pass
    if message.author != client.user:
        if not isinstance(message.channel, discord.TextChannel):
            await bot.receive_dm_delete(message)

@client.event
async def on_member_join(member):
    if bot.check_server(member.guild):
        if config["send_member_join/remove_log"]:
            await bot.member_join_log(member)

@client.event
async def on_member_remove(member):
    if bot.check_server(member.guild):
        if config["send_member_join/remove_log"]:
            await bot.member_remove_log(member)

@client.event
async def on_voice_state_update(member, before, after):
    if bot.check_server(member.guild):
        if config["save_voice_log"]:
            await bot.save_voice_log(member, before, after)

"""
@client.event
async def on_reaction_add(reaction, user):
    if config["reaction_authentication"]:
        await bot.rule_reaction_add(reaction, user)
    if config["count_role"]:
        await bot.count_role(reaction, user)

@client.event
async def on_reaction_remove(reaction, user):
    if config["reaction_authentication"]:
        await bot.rule_reaction_remove(reaction, user)
"""

@client.event
async def on_raw_reaction_add(payload):
    if config["reaction_authentication"]:
        await bot.raw_rule_reaction_add(payload)
    if config["count_role"]:
        await bot.raw_count_role(payload)

@client.event
async def on_raw_reaction_remove(payload):
    if config["reaction_authentication"]:
        await bot.raw_rule_reaction_remove(payload)

client.run(config["TOKEN"])
