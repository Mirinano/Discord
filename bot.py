#!python3.6
import sys, os, shutil, copy
import asyncio, threading
import time, datetime
import json, re, requests
import urllib.parse
import urllib.request
from tabulate import tabulate

import discord #0.16

#original
from __init__ import Developer
import API_token
import log_format 
import fw_wrap
import cmd_trigger
import cmd_msg
import help_msg
import words

class Translation:
    #info
    API_KEY = API_token.translate_API_KEY
    URL = "https://translation.googleapis.com/language/translate/v2"
    
    def translate(self, content:str, target:str) -> tuple:
        detect_sample = content.split("\n")[0] #first line
        source, confidence = self.detect(detect_sample)
        result = self.translation(content, target, source)
        return result, target, source, confidence

    def detect(self, content:str) -> tuple:
        url = Translation.URL + "/detect?key=" + Translation.API_KEY + "&q=" + content
        rr=requests.get(url)
        unit_aa=json.loads(rr.text)
        language = unit_aa["data"]["detections"][0][0]["language"]
        confidence = str(int(unit_aa["data"]["detections"][0][0]["confidence"] * 100))
        return language, confidence

    def translation(self, content:str, target:str, source:str) -> tuple:
        url = Translation.URL + "?key=" + Translation.API_KEY
        content = self.__encode_content(content)
        url += "&q={0}&source={1}&target={2}".format(content, source, target)
        rr=requests.get(url)
        unit_aa = json.loads(rr.text)
        #error check
        try:
            result = unit_aa["data"]["translations"][0]["translatedText"].replace("&#39;", "'").replace("&lt;", "<").replace("&gt;", ">")
        except:
            if unit_aa.get("error") is not None: #API error
                result = "TranslationError: \n\tCode: {0}\n\tMessage: {1}".format(unit_aa["error"]["code"], unit_aa["error"]["message"])
            else:
                result = "TranslationError: Unknown error."
        return result
    
    def __encode_content(self, content):
        return urllib.parse.quote(content, safe='')
    
    def get_translatable_lang(self) -> tuple:
        url = Translation.URL + "/languages?key=" + Translation.API_KEY
        rr=requests.get(url)
        unit_aa=json.loads(rr.text)
        return (d.get("language") for d in unit_aa["data"]["languages"])

    def check_lang(self, lang) -> bool:
        return lang in self.languages
    
    #test method
    def test_translation(self, content:str, target:str, source:str) -> tuple:
        url = Translation.URL + "?key=" + Translation.API_KEY
        content = self.__encode_content(content)
        url += "&q={0}&source={1}&target={2}".format(content, source, target)
        rr=requests.get(url)
        unit_aa=json.loads(rr.text)
        print(unit_aa)

class Bot(Translation):
    def __init__(self, config:dict, client:discord.Client):
        self.config = config
        self.client = client

        #bot info
        self.bot_color = self.change_color_code()
        self.op_role = self.create_op_role()
        self.bot_dir = "./bot/{0}/".format(self.config["NAME"])

        #system message directory
        self.sys_msg_dir = self.bot_dir + "messages/"

        #log directory info
        ##tmp dir
        self.tmp = self.bot_dir + "tmp/"
        ##text log
        self.log_dir = self.bot_dir + "log/"
        self.check_path_exits(self.log_dir)
        self.statistics_log = self.log_dir + "{0}/statistics.txt"
        self.statistics = self.log_dir + "statistics.csv"
        self.msg_log = self.log_dir + "{0}/msg_log/{1}.txt"
        self.msg_change_log = self.log_dir + "{0}/msg_change_log/{1}.txt"
        self.msg_delete_log = self.log_dir + "{0}/msg_delete_log/{1}.txt"
        self.msg_zip_log = self.bot_dir + "zip_log/"
        self.check_path_exits(self.msg_zip_log)
        ##voice log
        voice_log_dir = self.bot_dir + "/voice_log/"
        voice_log_archive_dir = voice_log_dir + "archive/"
        self.voice_log = voice_log_dir + "{}.txt"
        self.voice_log_archive = voice_log_archive_dir + "{}.txt"
        self.check_path_exits(voice_log_archive_dir)
        self.voice_afk_log()

        #setup
        self.load_spam()
        self.load_alert()
        self.load_role()

    async def login(self):
        self.create_op_role_mention()
        await self.set_frequent_data()
        await self.load_capture_message()

    #test method
    async def launch_report(self):
        ch = self.client.get_channel(self.config["launch_report"])
        content = "{0} has started. \nStartup time: {1}".format(self.client.user.name, datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        await self.client.send_message(ch, content)
    
    async def send_test_msg(self):
        ch = self.client.get_channel(self.config["test_ch"])
        content = "this is test msg. \n\ttime:{}".format(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        await self.client.send_message(ch, content)

    #setup method
    async def set_frequent_data(self):
        self.action_server = self.client.get_server(self.config["action_server_id"])
        self.admin_action_ch = self.client.get_channel(self.config["admin_action_ch_id"])

    async def load_capture_message(self):
        if self.config["reaction_authentication"]:
            self.reaction_authentication_msg = await self.capture_message(self.config["reaction_authentication_msg"])
        if self.config["count_role"]:
            self.count_role_msg = await self.capture_message(self.config["count_role_msg"])
        
    async def capture_message(self, url:str) -> discord.Message:
        match = re.search(r"\d+/\d+/\d+", url)
        if match:
            url_list = match.group(0).split("/")
            msg = await self.search_message(url_list[1], url_list[2])
            self.client.messages.append(msg)
            return msg
        else:
            return None

    def load_spam(self):
        fp = self.bot_dir + "spam.txt"
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()
        self.spam_words = set(content.strip().split("\n"))
        with open("spam.txt", "r", encoding="utf-8") as f:
            content = f.read()
        for word in content.strip().split("\n"):
            self.spam_words.add(word)
        self.update_spam()

    def load_alert(self):
        fp = self.bot_dir + "alert.txt"
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()
        self.alert_words = set(content.strip().split("\n"))
        self.update_alert()

    def update_spam(self):
        self.spam_pattern = "|".join(self.spam_words)

    def update_alert(self):
        self.alert_pattern = "|".join(self.alert_words)

    def load_role(self):
        self.color_role = dict()
        self.color_role_set = set()
        fp = self.bot_dir + "role/color_role.txt"
        with open(fp, "r", encoding="utf-8") as f:
            line = f.readline()
            while line:
                try:
                    text = line.strip().split(",")
                    self.color_role[text[0]] = text[1]
                    self.color_role_set.add(text[1])
                except:
                    break
                line = f.readline()
        self.normal_role = dict()
        fp = self.bot_dir + "role/normal_role.txt"
        with open(fp, "r", encoding="utf-8") as f:
            line = f.readline()
            while line:
                try:
                    text = line.strip().split(",")
                except:
                    break
                self.normal_role[text[0]] = text[1]
                line = f.readline()

    #check method
    def check_bot_user(self, msg:discord.Message) -> bool:
        if msg.author == self.client.user:
            return True
        else:
            return False

    def check_op_user(self, msg:discord.Message) -> bool:
        roles = {r.name for r in msg.author.roles}
        for op in ["op2", "op3", "op4"]:
            if self.op_role[op] in roles:
                return True
        return False

    def check_path_exits(self, fp:str, create:bool=True) -> bool:
        dir_path = os.path.dirname(fp)
        if os.path.exists(dir_path):
            return True
        elif create:
            self.create_dir(dir_path)
        else:
            pass
        return False
    
    def check_file_exits(self, fp:str) -> bool:
        return os.path.exists(fp)
    
    def create_dir(self, fp:str) -> None:
        os.makedirs(fp)
        return None
    
    def check_send_log_day(self) -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d")

    def check_server(self, target) -> bool:
        if self.config["action_server_id"] == "": #all server
            return True
        if isinstance(target, discord.Channel):
            return target.server.id == self.config["action_server_id"]
        elif isinstance(target, discord.Server):
            return target.id == self.config["action_server_id"]
        elif isinstance(target, discord.Message):
            if isinstance(target.channel, discord.Channel):
                return target.channel.server.id in self.config["action_server_id"]
            else:
                return False
        elif isinstance(target, discord.Member):
            return target.server.id == self.config["action_server_id"]
        else:
            return False

    def check_cmd_start(self, msg:discord.Message, trigger:tuple) -> bool:
        if msg.content.startswith(trigger[0]):
            if self.config["op"][trigger[1]] in [r.name for r in msg.author.roles]:
                return True
            elif msg.author.server_permissions.administrator:
                return True
            else:
                return False
        return False

    def check_permission_send_msg(self, ch:discord.Channel, member:discord.Member) -> bool:
        return ch.permissions_for(member).send_messages

    def check_permission_read_message_history(self, ch:discord.Channel, member:discord.Member) -> bool:
        return ch.permissions_for(member).read_message_history

    def create_role_set_name(self, member:discord.Member) -> set:
        return {r.name for r in member.roles}
    
    def create_role_set_id(self, member:discord.Member) -> set:
        return {r.id for r in member.roles}

    def create_op_role(self) -> dict:
        r_dict = dict()
        for k, v in self.config["op"].items():
            r_dict[k] = v
            if r_dict.get(v) is None:
                r_dict[v] = list()
            r_dict[v].append(k)
        return r_dict

    def create_op_role_mention(self) -> dict:
        server = self.client.get_server(self.config["action_server_id"])
        r_dict = dict()
        for role in server.roles:
            if role.name in list(self.config["op"].values()):
                if role.name != "@everyone":
                    for key in self.op_role[role.name]:
                        r_dict[key] = role.mention
                else:
                    r_dict["op1"] = "everyone"
        self.op_role_mention = r_dict

    def create_msg_url(self, msg:discord.Message) -> str:
        return log_format.msg_url.format(
            server = "@me" if msg.channel.is_private else msg.server.id,
            ch = msg.channel.id,
            msg = msg.id
        )

    #help action
    async def help(self, msg:discord.Message):
        content = msg.content.strip(" ")
        if content == "/help":
            op_role_name = {self.config["op"]["op2"], self.config["op"]["op3"], self.config["op"]["op4"]}
            member_role = self.create_role_set_name(msg.author)
            target_role = op_role_name & member_role
            op_level = list()
            for role_name in target_role:
                if self.op_role.get(role_name) is not None:
                    op_level = op_level + self.op_role.get(role_name)
            cmd = help_msg.main_help.format("\n".join(["\n".join(help_msg.help_cmd.get(h)) for h in op_level]))
            
            await self.client.send_message(msg.channel, cmd)
        else:
            target = content.split(" ")[1].strip("/ ")
            cmd = help_msg.help_message.get(target)
            cmd = cmd if cmd is not None else "そのようなコマンドはありません。"
            await self.client.send_message(msg.channel, cmd)

    #save log method
    def save_msg_log(self, msg:discord.Message, * , fp:str=None, write:bool=True):
        ch_name = msg.channel.name if isinstance(msg.channel, discord.Channel) else "DM"
        save_content = log_format.msg_log.format(
            time = msg.timestamp.strftime("%Y/%m/%d %H:%M:%S"),
            user = self.save_author(msg.author),
            msg_id = msg.id,
            user_id = msg.author.id,
            msg_type = msg.type.name if isinstance(msg.type, discord.MessageType) else "other type",
            attachments = "\n".join([attach["url"] for attach in msg.attachments]),
            embed = "無" if msg.embeds is None else ("有" if len(msg.embeds) > 0 else "無"),
            content = self.content_fw_wrap(msg.content)
        ) + "\n" + "-"*75 + "\n"
        if write:
            fp = self.msg_log.format(datetime.datetime.now().strftime("%Y-%m-%d"), ch_name) if fp is None else fp
            self.write_file(fp, save_content)
            return None
        else:
            return save_content

    def save_msg_change_log(self, before:discord.Message, after:discord.Message):
        ch_name = after.channel.name if isinstance(after.channel, discord.Channel) else "DM"
        save_content = log_format.msg_change_log.format(
            after_time = after.timestamp.strftime("%Y/%m/%d %H:%M:%S"),
            before_time = before.timestamp.strftime("%Y/%m/%d %H:%M:%S"),
            user = self.save_author(after.author),
            user_id = after.author.id,
            msg_id = after.id,
            msg_type = after.type.name if isinstance(after.type, discord.MessageType) else "other type",
            attachments = "\n".join([attach["url"] for attach in after.attachments]),
            embed = "無" if after.embeds is None else ("有" if len(after.embeds) > 0 else "無"),
            before_content = self.content_fw_wrap(before.content),
            after_content = self.content_fw_wrap(after.content)
        ) + "\n" + "-"*75 + "\n"
        fp = self.msg_change_log.format(datetime.datetime.now().strftime("%Y-%m-%d"), ch_name)
        return self.write_file(fp, save_content)
    
    def save_msg_delete_log(self, msg:discord.Message):
        ch_name = msg.channel.name if isinstance(msg.channel, discord.Channel) else "DM"
        save_content = log_format.msg_delete_log.format(
            delete_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            time = msg.timestamp.strftime("%Y/%m/%d %H:%M:%S"),
            user = self.save_author(msg.author),
            user_id = msg.author.id,
            msg_id = msg.id,
            msg_type = msg.type.name if isinstance(msg.type, discord.MessageType) else "other type",
            attachments = "\n".join([attach["url"] for attach in msg.attachments]),
            embed = "無" if msg.embeds is None else ("有" if len(msg.embeds) > 0 else "無"),
            content = self.content_fw_wrap(msg.content)
        ) + "\n" + "-"*75 + "\n"
        fp = self.msg_delete_log.format(datetime.datetime.now().strftime("%Y-%m-%d"), ch_name)
        return self.write_file(fp, save_content)
    
    def save_author(self, author):
        if isinstance(author, discord.Member):
            if author.nick is not None:
                return "{0} (アカウント名: {1}#{2}, ID: {3})".format(author.nick, author.name, author.discriminator, author.id)
        return "{0}#{1} (ID: {2})".format(author.name, author.discriminator, author.id)

    def save_file(self, url:str, fp:str):
        opener = urllib.request.build_opener()
        opener.addheaders=[("User-Agent", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0")]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url=url, filename=fp) # save file.

    def content_fw_wrap(self, content:str):
        content_list = list()
        for c in content.split("\n"):
            content_list.append("\n".join(fw_wrap.fw_wrap(c, width=70, placeholder="")))
        return "\n".join(content_list)

    def write_file(self, fp:str, content:str, * , dir_create:bool=True, mode="a") -> None:
        self.check_path_exits(fp, create=dir_create)
        with open(fp, mode, encoding="utf-8") as f:
            f.write(content)
        return None

    def create_zip(self, day:str, delete:bool=True) -> str:
        """
        @para day:str %Y-%m-%d

        @return zip file path
        """
        log_dir = self.log_dir + day
        zip_dir = self.msg_zip_log + "-".join(day.split(day)[:1]) #%Y-%m
        zip_file = zip_dir + "/" + day
        self.check_path_exits(zip_dir)
        # create zip file
        shutil.make_archive(zip_file, "zip", root_dir=log_dir)
        zip_file = zip_file + ".zip"
        if delete:
            shutil.rmtree(log_dir)
        return zip_file
    
    def msg_log_dir_list(self, ex_today:bool=True) -> list:
        dirs = list()
        regex = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
        exday = self.check_send_log_day() if ex_today else ""
        for filename in os.listdir(self.log_dir):
            if os.path.isdir(self.log_dir + filename):
                if regex.match(filename) is not None:
                    if filename != exday:
                        dirs.append(filename)
        return dirs

    async def send_msg_logs(self):
        for day in self.msg_log_dir_list():
            zip_file = self.create_zip(day)
            file_name = day + ".zip"
            send_msg = "{}のメッセージログです。".format(day)
            ch = self.client.get_channel(self.config["send_logzipfile_channel"])
            await self.client.send_file(ch, zip_file, content=send_msg, filename=file_name)
    
    async def send_today_msg_log(self):
        day = datetime.datetime.now().strftime("%Y-%m-%d")
        zip_file = self.create_zip(day, delete=False)
        file_name = day + ".zip"
        send_msg = "{}のメッセージログです。".format(day)
        ch = self.client.get_channel(self.config["send_logzipfile_channel"])
        await self.client.send_file(ch, zip_file, content=send_msg, filename=file_name)

    async def statistics_cmd(self, msg:discord.Message):
        #check cmd type
        c = msg.content.split("\n")[0].split(" ")
        if len(c) > 1:
            cmd = c[1]
        else:
            cmd = None
        # swich
        if cmd == "full":
            await self.full_statistics(msg.server, msg.channel)
        elif cmd == "simple":
            await self.simple_statistics(msg.server, msg.channel)
        else:
            await self.save_statistics(msg.server, send_ch=msg.channel, save=False)

    async def save_statistics(self, server:discord.Server, day:datetime.datetime=None, * , send_ch:discord.Channel=None, save=True) -> str:
        day = datetime.datetime.now() if day is None else day
        if save:
            fp = self.statistics_log.format(day.strftime("%Y-%m-%d"))
        else:
            fp = self.tmp + "statistics.txt"
        top_role = self.search_top_role(server)
        msg_count, write_count, ch_msg_count, users = await self.search_recent_messages_users(server)
        content = log_format.statistics.format(
            server_name = server.name,
            server_id = server.id,
            server_create = server.created_at.strftime("%Y/%m/%d %H:%M:%S"),
            owner = self.save_author(server.owner),
            owner_id = server.owner.id,
            member_count = str(server.member_count),
            msg_count = msg_count,
            writer_count = write_count,
            region = str(server.region),
            afk_time = str(server.afk_timeout),
            top_role = self.save_role(top_role),
            top_users = self.save_users(self.search_top_role_users(server, top_role), seq="\n\t"),
            default_channel = self.save_channel(server.default_channel),
            default_role = self.save_role(server.default_role),
            invites = await self.save_invites(server, seq="\n\t" ,indent=1),
            roles = self.save_roles(server, seq="\n\t"),
            channels = self.save_channels(server, seq="\n\t")
        )
        self.write_file(fp, content, mode="w")
        if send_ch is not None:
            try:
                await self.client.send_message(send_ch, content)
            except discord.HTTPException:
                try:
                    await self.client.send_file(send_ch, fp, content="統計情報です。")
                except:
                    pass
        return content

    async def simple_statistics(self, server:discord.Server, send_ch:discord.Channel):
        top_role = self.search_top_role(server)
        content = log_format.statistics_simple.format(
            server_name = server.name,
            server_id = server.id,
            server_create = server.created_at.strftime("%Y/%m/%d %H:%M:%S"),
            owner = self.save_author(server.owner),
            owner_id = server.owner.id,
            member_count = str(server.member_count),
            region = str(server.region),
            afk_time = str(server.afk_timeout),
            top_role = self.save_role(top_role),
            top_users = self.save_users(self.search_top_role_users(server, top_role), seq="\n\t"),
            default_channel = self.save_channel(server.default_channel),
            default_role = self.save_role(server.default_role),
            invites = await self.save_invites_simple(server, seq="\n\t" ,indent=1),
        )
        await self.client.send_message(send_ch, content)

    async def full_statistics(self, server:discord.Server, send_ch:discord.Channel):
        pass

    def search_top_role(self, server:discord.Server) -> discord.Role:
        for role in server.role_hierarchy:
            return role
    
    def search_top_role_users(self, server:discord.Server, role:discord.Role=None) -> list:
        role = self.search_top_role(server) if role is None else role
        user_list = list()
        for member in server.members:
            if role in member.roles:
                user_list.append(member)
            else:
                continue
        return user_list
    
    async def search_recent_messages_users(self, server:discord.Server, day:int=1):
        after = datetime.datetime.today() - datetime.timedelta(days=day)
        msg_count = user_count = 0
        users = list()
        users_set = set()
        ch_msg_count = dict()
        for ch in server.channels:
            if self.check_permission_read_message_history(ch, ch.server.get_member(self.client.user.id)):
                ch_msg_count[ch.id] = 0
                async for message in self.client.logs_from(ch, limit=1000, after=after):
                    ch_msg_count[ch.id] += 1
                    msg_count += 1
                    if not message.author.id in users_set:
                        users_set.add(message.author.id)
                        users.append(message.author)
        return msg_count, len(users_set), ch_msg_count, users

    def save_users(self, users, seq="\n") -> str:
        users = [self.save_author(u) for u in users]
        return seq.join(users)

    def save_users_all(self, server:discord.Server, seq:str="\n", indent:int=0) -> str:
        pass

    def save_author_mention(self, member) -> str:
        return self.save_author(member) + " (<@{0}>)".format(member.id)

    def save_channel(self, channel:discord.Channel, indent=0) -> str:
        if isinstance(channel, discord.Channel):
            return "\t"*indent + "{0} (ID: {1}, type: {2}, pos: {3})".format(channel.name, channel.id, str(channel.type), str(channel.position))
        return ""

    def save_channels(self, server:discord.Server, seq="\n", * , sort:bool=True) -> str:
        channels = list()
        for ch in server.channels:
            channels.append(ch)
        if sort:
            channels.sort(key=lambda x:(str(x.type), x.position))
        channels = [self.save_channel(ch) for ch in channels]
        return seq.join(channels)

    def save_role(self, role:discord.Role, indent=0) -> str:
        return "\t"*indent + "{0} (ID: {1}, pos: {2})".format(role.name, role.id, str(role.position))
    
    def save_roles(self, server:discord.Server, seq="\n", * , sort:bool=True) -> str:
        roles = list()
        for role in server.roles:
            roles.append(role)
        if sort:
            roles.sort(key=lambda x:x.position, reverse=True)
        roles = [self.save_role(r) for r in roles]
        return seq.join(roles)
    
    def save_invite(self, invite:discord.Invite, indent=0) -> str:
        return log_format.save_invite.format(
            indent="\t"*indent,
            URL = invite.url,
            created_at = invite.created_at.strftime("%Y/%m/%d %H:%M:%S"),
            uses = str(invite.uses),
            max_uses = str(invite.max_uses),
            inviter = self.save_author(invite.inviter),
            channel = self.save_channel(invite.channel)
        )

    async def save_invites_simple(self, server:discord.Server, seq="\n", indent=0) -> str:
        invites = list()
        for invite in await self.client.invites_from(server):
            invites.append(invite.code)
        return seq.join(invites)

    async def save_invites(self, server:discord.Server, seq="\n", indent=0) -> str:
        invites = list()
        for invite in await self.client.invites_from(server):
            invites.append(self.save_invite(invite, indent))
        return seq.join(invites)

    #member join/remove action
    async def member_join_log(self, member:discord.Member):
        send_ch = await self.send_welcome_ch()
        send_dm = await self.send_welcome_dm(member)
        content = log_format.join_member_message.format(
            time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            user = self.save_author(member),
            user_id = member.id,
            user_create = member.created_at.strftime("%Y/%m/%d %H:%M:%S"),
            count = str(member.server.member_count),
            send_ch = send_ch,
            send_dm = send_dm
        )
        ch = self.client.get_channel(self.config["member_join/remove_log_ch"])
        await self.client.send_message(ch, content)
        if self.config["member_count"]:
            await self.member_count(member.server)
    
    async def send_welcome_ch(self, file_name:str="welcome-ch") -> str:
        if self.config["welcome_msg_ch"]:
            if self.config["welcome_msg_ch_random"]:
                pass
            try:
                fp = self.sys_msg_dir + "{}.txt".format(file_name)
                with open(fp, "r", encoding="utf-8") as f:
                    content = f.read()
                ch = self.client.get_channel(self.config["welcome_msg_ch_id"])
                await self.client.send_message(ch, content)
                return "成功"
            except Exception as e:
                print(e)
                return "失敗"
        else:
            return "未設定"
    
    async def send_welcome_dm(self, member:discord.Member, file_name:str="welcome-dm") -> str:
        if self.config["welcome_msg_dm"]:
            if self.config["welcome_msg_dm_random"]:
                pass
            try:
                fp = self.sys_msg_dir + "{}.txt".format(file_name)
                with open(fp, "r", encoding="utf-8") as f:
                    content = f.read()
                await self.client.send_message(member, content)
                return "成功"
            except Exception as e:
                print(e)
                return "失敗"
        else:
            return "未設定"

    async def member_remove_log(self, member:discord.Member):
        content = log_format.remove_member_message.format(
            time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            user = self.save_author(member),
            user_id = member.id,
            user_create = member.created_at.strftime("%Y/%m/%d %H:%M:%S"),
            count = str(member.server.member_count)
        )
        ch = self.client.get_channel(self.config["member_join/remove_log_ch"])
        await self.client.send_message(ch, content)
        if self.config["member_count"]:
            await self.member_count(member.server)

    async def member_count(self, server:discord.Server):
        name = log_format.member_count.format(str(server.member_count))
        await self.client.edit_channel(self.client.get_channel(self.config["member_count_ch"]), name=name)

    #reaction authentication system
    async def rule_reaction_add(self, reaction:discord.Reaction, user:discord.Member):
        if reaction.message != self.reaction_authentication_msg:
            return None
        if reaction.emoji == "✅":
            #agreement
            await self.add_role(user, self.config["reaction_authentication_role"])
        elif reaction.emoji == "❌":
            #disagreement
            await self.disagreement_rule(user)
            await self.remove_reaction(reaction.message.id, reaction.message.channel.id, reaction.emoji, user.id)
        else:
            #other reactions
            await self.remove_reaction(reaction.message.id, reaction.message.channel.id, reaction.emoji, user.id)

    #reaction authentication system
    async def rule_reaction_remove(self, reaction:discord.Reaction, user:discord.Member):
        if reaction.message != self.reaction_authentication_msg:
            return None
        if reaction.emoji == "✅":
            await self.remove_role(user, self.config["reaction_authentication_role"])
        return None

    async def disagreement_rule(self, member:discord.Member, *, op:str="op2"):
        fp = self.sys_msg_dir + "disagreement_msg.txt"
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()
        try:
            msg = await self.client.send_message(member, content)
        except:
            log = log_format.disagreement_rule_action_fail.format(
                op = self.op_role_mention[op],
                time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                target = self.save_author_mention(member),
                log = "DMの送信失敗。"
            )
            await self.client.send_message(self.client.get_channel(self.config["admin_action_ch_id"]), log)
            return None
        try:
            await self.__kick(member.id)
        except:
            await self.client.delete_message(msg)
            log = log_format.disagreement_rule_action_fail.format(
                op = self.op_role_mention[op],
                time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                target = self.save_author_mention(member),
                log = "DMの送信成功。キックに__失敗__。送信済みDMを削除。"
            )
            await self.client.send_message(self.client.get_channel(self.config["admin_action_ch_id"]), log)
            return None
        return None

    #count role
    async def count_role(self, reaction:discord.Reaction, user:discord.User):
        if reaction.message != self.count_role_msg:
            return None
        if reaction.emoji != "✅":
            return None
        role_count = self.__count_role(reaction.message.server)
        table = list()
        for k, v in role_count:
            table.append([k, str(v)])
        header = ["role name", "count"]
        result = "```\n" + tabulate(table, headers, tablefmt="grid") + "\n```"
        await self.client.edit_message(self.count_role_msg, result)
        await self.remove_reaction(self.count_role_msg.id, self.count_role_msg.channel.id, "✅", user.id)
        
    def __count_role(self, server:discord.Server=None):
        server = self.client.get_server(self.config["action_server_id"]) if server is None else server
        role_count = dict()
        role_names = [r.name for r in server.roles]
        for role_name in role_names:
            role_count[role_name] = 0
        for member in server.members:
            for role_name in [r.name for r in member.roles]:
                role_count[role_name] += 1
        return role_count

    @asyncio.coroutine
    def remove_reaction(self, msg_id, ch_id, emoji, user_id):
        try:
            emoji = '{}:{}'.format(emoji.name, emoji.id)
        except:
            pass
        yield from self.client.http.remove_reaction(msg_id, ch_id, emoji, user_id)

    #voice log
    async def save_voice_log(self, before:discord.Member, after:discord.Member):
        action = self.voice_action(before, after)
        if action is None:
            self.voice_user_update(before, after)
        elif action == "join":
            if self.voice_start_check(after):
                await self.voice_start_action(after)
            self.voice_join_action(after)
        elif action == "remove":
            self.voice_remove_action(before)
            if self.voice_finish_check(before):
                await self.voice_finish_action(before)
        elif action == "move":
            await self.voice_move_action(before, after)
        else:
            pass
    
    def voice_action(self, before:discord.Member, after:discord.Member) -> str:
        if ((before.voice.voice_channel is None) or before.voice.is_afk) and (after.voice.voice_channel is not None): #user join voice channel
            return "join"
        elif (before.voice.voice_channel is not None) and ((after.voice.voice_channel is None) or after.voice.is_afk): #user remove voice channel
            return "remove"
        elif before.voice.voice_channel != after.voice.voice_channel: #user move voice chanel
            return "move"
        else: #status update
            return None
    
    def save_voice_channel(self, ch:discord.Channel) -> str:
        if isinstance(ch, discord.Channel):
            return "{0} (ID: {1})".format(ch.name, ch.id)
        return ""

    def count_voice_members(self, ch:discord.Channel) -> int:
        return len(ch.voice_members)

    def voice_join_action(self, after:discord.Member):
        fp = self.voice_log.format(after.voice.voice_channel.id)
        status = log_format.voice_status.format(
            self_mic = "無効" if after.voice.self_mute else "有効",
            self_speaker = "無効" if after.voice.self_deaf else "有効",
            mic = "無効" if after.voice.mute else "有効",
            speaker = "無効" if after.voice.deaf else "有効"
        )
        content = log_format.voice_join.format(
            time = datetime.datetime.now().strftime("%Y:%m:%dT%H:%M:%S"),
            count = str(self.count_voice_members(after.voice.voice_channel)),
            user = self.save_author(after),
            user_id = after.id,
            status = status
        )
        self.write_file(fp, content)
    
    def voice_remove_action(self, before:discord.Member):
        fp = self.voice_log.format(before.voice.voice_channel.id)
        status = log_format.voice_status.format(
            self_mic = "無効" if before.voice.self_mute else "有効",
            self_speaker = "無効" if before.voice.self_deaf else "有効",
            mic = "無効" if before.voice.mute else "有効",
            speaker = "無効" if before.voice.deaf else "有効"
        )
        content = log_format.voice_remove.format(
            time = datetime.datetime.now().strftime("%Y:%m:%dT%H:%M:%S"),
            count = str(self.count_voice_members(before.voice.voice_channel)),
            user = self.save_author(before),
            user_id = before.id,
            status = status
        )
        self.write_file(fp, content)

    def voice_user_update(self, before:discord.Member, after:discord.Member):
        fp = self.voice_log.format(after.voice.voice_channel.id)
        if after.voice.deaf != before.voice.deaf:
            status = log_format.voice_change_status_server.format(
                status = "サーバースピーカー",
                action = "無効" if after.voice.deaf else "有効"
            )
        elif after.voice.mute != before.voice.mute:
            status = log_format.voice_change_status_server.format(
                status = "サーバーマイク",
                action = "無効" if after.voice.mute else "有効"
            )
        elif after.voice.self_deaf != before.voice.self_deaf:
            status = log_format.voice_change_status_self.format(
                status = "スピーカー",
                action = "無効" if after.voice.self_deaf else "有効"
            )
        elif after.voice.self_mute != before.voice.self_mute:
            status = log_format.voice_change_status_self.format(
                status = "マイク",
                action = "無効" if after.voice.self_mute else "有効"
            )
        else:
            return None
        content = log_format.voice_change.format(
            time = datetime.datetime.now().strftime("%Y:%m:%dT%H:%M:%S"),
            count = str(self.count_voice_members(after.voice.voice_channel)),
            user = self.save_author(after),
            user_id = after.id,
            content = status
        )
        self.write_file(fp, content)
    
    def voice_start_check(self, after:discord.Member) -> bool:
        return not os.path.exists(self.voice_log.format(after.voice.voice_channel.id))
    
    def voice_finish_check(self, before:discord.Member) -> bool:
        return len(before.voice.voice_channel.voice_members) == 0
    
    async def voice_start_action(self, after:discord.Member):
        start_time = datetime.datetime.now().strftime("%Y:%m:%dT%H:%M:%S")
        fp = self.voice_log.format(after.voice.voice_channel.id)
        content = log_format.voice_start.format(
            time = start_time,
            name = after.voice.voice_channel.name,
            id = after.voice.voice_channel.id
        )
        self.write_file(fp, content)
        content = log_format.voice_start_message.format(
            time = start_time,
            user = self.save_author(after),
            user_id = after.id,
            ch_name = after.voice.voice_channel.name,
            ch_id = after.voice.voice_channel.id
        )
        ch = self.client.get_channel(self.config["send_voice_log_ch"])
        await self.client.send_message(ch, content)
    
    async def voice_finish_action(self, before:discord.Member):
        # pass AFK channel
        if before.voice.voice_channel.id == self.config["AFK_channel"]:
            return None
        
        finish_time = datetime.datetime.now()
        fp = self.voice_log.format(before.voice.voice_channel.id)
        log_file = open(fp, "r", encoding="utf-8")
        log_line = log_file.readline()
        r = re.search(r"\d{4}:\d{2}:\d{2}T\d{2}:\d{2}:\d{2}", log_line)
        start_time = datetime.datetime.strptime(r.group(), "%Y:%m:%dT%H:%M:%S")
        operating_time = finish_time - start_time
        h = str(int(operating_time.seconds / 3600))
        m = str(int((operating_time.seconds % 3600) / 60))
        s = str(int(operating_time.seconds % 60))
        operating_time = "{0}日と{1}時間{2}分{3}秒".format(str(operating_time.days), h, m, s)
        finish_time = finish_time.strftime("%Y:%m:%dT%H:%M:%S")
        finish_content = log_format.voice_finish.format(
            time = finish_time,
            operating_time = operating_time
        )
        new_fp = self.voice_log_archive.format(start_time.strftime("%Y-%m-%dT%H-%M-%S"))
        with open(new_fp, "a", encoding="utf-8") as f:
            f.write(log_line)
            log_line = log_file.readline()
            f.write(finish_content)
            while(log_line):
                f.write(log_line)
                log_line = log_file.readline()
        log_file.close()
        os.remove(fp)
        content = log_format.voice_finish_message.format(
            ch_name = before.voice.voice_channel.name,
            ch_id = before.voice.voice_channel.id,
            time = finish_time,
            operating_time = operating_time
        )
        ch = self.client.get_channel(self.config["send_voice_log_ch"])
        await self.client.send_file(ch, new_fp, content=content)

    async def voice_move_action(self, before:discord.Member, after:discord.Member):
        fp = self.voice_log.format(before.voice.voice_channel.id)
        status = log_format.voice_status.format(
            self_mic = "無効" if before.voice.self_mute else "有効",
            self_speaker = "無効" if before.voice.self_deaf else "有効",
            mic = "無効" if before.voice.mute else "有効",
            speaker = "無効" if before.voice.deaf else "有効"
        )
        content = log_format.voice_remove.format(
            time = datetime.datetime.now().strftime("%Y:%m:%dT%H:%M:%S"),
            count = str(self.count_voice_members(before.voice.voice_channel)),
            user = self.save_author(before),
            user_id = before.id,
            status = log_format.voice_move_before.format(
                ch = self.save_voice_channel(before.voice.voice_channel),
                status = status
            )
        )
        self.write_file(fp, content)
        if self.voice_finish_check(before):
            await self.voice_finish_action(before)
        if self.voice_start_check(after):
            await self.voice_start_action(after)
        fp = self.voice_log.format(after.voice.voice_channel.id)
        status = log_format.voice_status.format(
            self_mic = "無効" if after.voice.self_mute else "有効",
            self_speaker = "無効" if after.voice.self_deaf else "有効",
            mic = "無効" if after.voice.mute else "有効",
            speaker = "無効" if after.voice.deaf else "有効"
        )
        content = log_format.voice_join.format(
            time = datetime.datetime.now().strftime("%Y:%m:%dT%H:%M:%S"),
            count = str(self.count_voice_members(after.voice.voice_channel)),
            user = self.save_author(after),
            user_id = after.id,
            status = log_format.voice_move_after.format(
                ch = self.save_voice_channel(after.voice.voice_channel),
                status = status
            )
        )
        self.write_file(fp, content)

    def voice_afk_log(self):
        fp = self.voice_log.format(self.config["AFK_channel"])
        if not self.check_file_exits(fp):
            content = "AFKチャンネルのログです。\n\n"
            self.write_file(fp, content)
        else:
            return None

    #admin assist
    ## ban/unban/kick
    async def ban(self, msg:discord.Message, * , op:str="op2"):
        start_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        content = msg.content.lstrip(cmd_trigger.ban[0]) #remove trigger ward
        cmd = self.spilit_function(content, 2)
        users_id = self.get_users_id(cmd["rest_first"])
        del_day = self.config["ban_del_msg"] if cmd.get("day") is None else (int(cmd.get("day")) if 0 <= int(cmd.get("day")) < 8 else 0)
        dm = True if cmd.get("dm") == "true" else (False if cmd.get("dm") == "false" else self.config["ban_dm"])
        if dm:
            if cmd.get("dm-original").lower() == "true":
                content = cmd.get("rest_last")
            else:
                fp = self.sys_msg_dir + "ban_msg.txt"
                with open(fp, "r", encoding="utf-8") as f:
                    content = f.read()
        else:
            content = None

        # check
        users_info = dict()
        for user_id in users_id:
            try:
                users_info[user_id] = await self.client.get_user_info(user_id)
            except:
                users_id.remove(user_id)
        accept_count = cancel_count = 1
        check_content = log_format.ban_kick_check.format(
            action = "ban",
            cmder = self.save_author(msg.author),
            targets = "\n\t".join([self.save_author(user) for user in users_info.values()]),
            send_dm = str(dm),
            dm_content = content if dm else "送信無し",
            op_level = self.op_role_mention[op],
            accept_count = str(accept_count),
            cancel_count = str(cancel_count)
        )
        check = await self.check_execute_cmd(msg, accept_count, cancel_count, content=check_content)
        if check:
            # accept
            await self.client.send_message(msg.channel, log_format.cmd_accept)
        else:
            # cancel
            await self.client.send_message(msg.channel, log_format.cmd_cancel)
            return None
        
        result_list = list()
        for user_id in users_id:
            result = dict()
            try:
                result["user_info"] = users_info[user_id]
                try:
                    if content is None:
                        raise "Content is None"
                    await self.send_dm_message(user_id, content)
                    result["dm"] = True
                except:
                    result["dm"] = False
                try:
                    await self.__ban(user_id)
                    result["ban"] = True
                except:
                    result["ban"] = False
            except discord.errors.NotFound:
                result["user_info"] = "User ID:{} is not found.".format(user_id)
            except:
                result["user_info"] = "unexpected error."
            finally:
                result_list.append(self.result_text(result, "ban"))
        end_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        content = log_format.ban_kick_result_log.format(
            action = "ban",
            start_time = start_time,
            end_time = end_time,
            details = "\n".join(result_list)
        )
        ch = self.client.get_channel(self.config["admin_action_ch_id"])
        await self.client.send_message(msg.channel, log_format.ban_result)
        await self.client.send_message(ch, content)
    
    async def unban(self, msg:discord.Message):
        start_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        content = msg.content.lstrip(cmd_trigger.unban[0]) #remove trigger ward
        users_id = self.get_users_id(content)
        result_list = list()
        for user_id in users_id:
            result = dict()
            try:
                result["user_info"] = await self.client.get_user_info(user_id)
                try:
                    await self.__unban(user_id)
                    result["unban"] = True
                except:
                    result["unban"] = False
            except discord.errors.NotFound:
                result["user_info"] = "User ID:{} is not found.".format(user_id)
            except:
                result["user_info"] = "unexpected error."
            finally:
                result["dm"] = False #not send dm all action
                result_list.append(self.result_text(result, "unban"))
        end_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        content = log_format.ban_kick_result_log.format(
            action = "unban",
            start_time = start_time,
            end_time = end_time,
            details = "\n".join(result_list)
        )
        ch = self.client.get_channel(self.config["admin_action_ch_id"])
        await self.client.send_message(msg.channel, log_format.unban_result)
        await self.client.send_message(ch, content)

    async def kick(self, msg:discord.Message, * , op:str="op2"):
        start_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        content = msg.content.lstrip(cmd_trigger.kick[0]) #remove trigger ward
        cmd = self.spilit_function(content, 2)
        users_id = self.get_users_id(cmd["rest_first"])
        dm = True if cmd.get("dm") == "true" else (False if cmd.get("dm") == "false" else self.config["kick_dm"])
        if dm:
            if cmd.get("dm-original") == "true":
                content = cmd.get("rest_last")
            else:
                fp = self.sys_msg_dir + "kick_msg.txt"
                with open(fp, "r", encoding="utf-8") as f:
                    content = f.read()
        else:
            content = None

        # check
        users_info = dict()
        for user_id in users_id:
            try:
                users_info[user_id] = await self.client.get_user_info(user_id)
            except:
                users_id.remove(user_id)
        accept_count = cancel_count = 1
        check_content = log_format.ban_kick_check.format(
            action = "kick",
            cmder = self.save_author(msg.author),
            targets = "\n\t".join([self.save_author(user) for user in users_info.values()]),
            send_dm = str(dm),
            dm_content = content if dm else "送信無し",
            op_level = self.op_role_mention[op],
            accept_count = str(accept_count),
            cancel_count = str(cancel_count)
        )
        check = await self.check_execute_cmd(msg, accept_count, cancel_count, content=check_content)
        if check:
            # accept
            await self.client.send_message(msg.channel, log_format.cmd_accept)
        else:
            # cancel
            await self.client.send_message(msg.channel, log_format.cmd_cancel)
            return None

        result_list = list()
        for user_id in users_id:
            result = dict()
            try:
                result["user_info"] = users_info[user_id]
                try:
                    if content is None:
                        raise "Content is None"
                    await self.send_dm_message(user_id, content)
                    result["dm"] = True
                except:
                    result["dm"] = False
                try:
                    await self.__kick(user_id)
                    result["kick"] = True
                except:
                    result["kick"] = False
            except discord.errors.NotFound:
                result["user_info"] = "User ID:{} is not found.".format(user_id)
            except:
                result["user_info"] = "unexpected error."
            finally:
                result_list.append(self.result_text(result, "kick"))
        end_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        content = log_format.ban_kick_result_log.format(
            action = "kick",
            start_time = start_time,
            end_time = end_time,
            details = "\n".join(result_list)
        )
        ch = self.client.get_channel(self.config["admin_action_ch_id"])
        await self.client.send_message(msg.channel, log_format.kick_result)
        await self.client.send_message(ch, content)

    def result_text(self, result:dict, action:str) -> str:
        if isinstance(result["user_info"], discord.User):
            return log_format.user_info.format(
                user = self.save_author(result["user_info"]),
                user_id = result["user_info"].id,
                user_create = result["user_info"].created_at,
                dm = "success" if result["dm"] else "fail",
                action = action,
                judg = "success" if result[action] else "fail"
            )
        else:
            return result["user_info"]
        
    @asyncio.coroutine
    def __ban(self, user_id,  delete_message_days=1, server_id=None):
        server_id = server_id if server_id is not None else self.config["action_server_id"]
        yield from self.client.http.ban(user_id, server_id, delete_message_days)

    @asyncio.coroutine
    def __unban(self, user_id, server_id=None):
        server_id = server_id if server_id is not None else self.config["action_server_id"]
        yield from self.client.http.unban(user_id, server_id)
    
    @asyncio.coroutine
    def __kick(self, user_id, server_id=None):
        server_id = server_id if server_id is not None else self.config["action_server_id"]
        yield from self.client.http.kick(user_id, server_id)

    def get_users_id(self, data:str) -> list:
        return re.findall(r"\d+", data)
    
    async def get_users_info(self, ids:list):
        users_list = list()
        for id in ids:
            users_list.append(await self.client.get_user_info(id))
        return users_list
    
    @asyncio.coroutine
    def send_dm_message(self, user_id, content=None):
        channel_id = yield from self.get_user_private_channel_by_id(user_id)
        data = yield from self.client.http.send_message(channel_id, content, guild_id=None, tts=None, embed=None)
        channel = self.client.get_channel(data.get('channel_id'))
        message = self.client.connection._create_message(channel=channel, **data)
        return message

    @asyncio.coroutine
    def get_user_private_channel_by_id(self, id:str) -> str:
        found = self.client.connection._get_private_channel_by_user(id)
        if found is None:
            # Couldn't find the user, so start a PM with them first.
            channel = yield from self.start_private_message_by_id(id)
            return channel.id
        else:
            return found.id
    
    @asyncio.coroutine
    def get_user_private_channel_by_id2(self, id:str) -> str:
        found = self.client.connection._get_private_channel_by_user(id)
        if found is None:
            # Couldn't find the user, so start a PM with them first.
            channel = yield from self.start_private_message_by_id(id)
            return channel
        else:
            return found

    @asyncio.coroutine
    def start_private_message_by_id(self, id:str) -> discord.Channel:
        data = yield from self.client.http.start_private_message(id)
        channel = discord.PrivateChannel(me=self.client.user, **data)
        self.client.connection._add_private_channel(channel)
        return channel

    ## spam/alert
    async def spam_alert(self, msg:discord.Message):
        if not self.check_bot_user(msg):
            if not self.check_op_user(msg):
                await self.alert(msg)
                await self.spam(msg)

    async def spam(self, msg:discord.Message):
        match = re.search(self.spam_pattern, msg.content)
        if not match:
            return None
        try:
            await self.__ban(user_id=msg.author.id)
            report = {"level": words.report, "detail": words.dealing_with_spam, "action": words.ban_succsess}
        except:
            #fail
            report = {"level": words.emergency, "detail": words.spam_occurrence, "action": words.ban_fail}
        finally:
            report["time"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            report["reason"] = log_format.alert_reasen_match.format(match.group(0))
            report["mentions"] = self.op_role_mention["op2"]
            await self.alert_report(msg, **report)

    async def alert(self, msg:discord.Message):
        match = re.search(self.alert_pattern, msg.content)
        if not match:
            return None
        report = {
            "level"   : words.warning,
            "detail"  : words.attention_message,
            "action"  : words.no_action,
            "time"    : datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "reason"  : log_format.alert_reasen_match.format(match.group(0)),
            "mentions": self.op_role_mention["op2"]
        }
        await self.alert_report(msg, **report)
    
    async def alert_report(self, msg:discord.Message, **kwargs):
        content = log_format.alert.format(
            channel = self.save_channel(msg.channel),
            author  = self.save_author_mention(msg.author),
            url = self.create_msg_url(msg),
            content = msg.content, 
            **kwargs
        )
        await self.client.send_message(self.admin_action_ch, content)

    async def spam_cmd(self, msg:discord.Message, _type="local", *, op:str="op3"):
        try:
            action = msg.content.split("\n")[0].split()[1].strip().lower()
            targets = set(msg.content.split("\n")[1:])
            kwargs = {"cat": _type, action: targets}
            print(kwargs)
            self.__edit_spam(**kwargs)
        except:
            pass
        finally:
            await self.client.send_message(msg.channel, self.show_spam())
    
    async def alert_cmd(self, msg:discord.Message, *, op:str="op3"):
        try:
            action = msg.content.split("\n")[0].split()[1].strip().lower()
            targets = set(msg.content.split("\n")[1:])
            kwargs = {action: targets}
            self.__edit_alert(**kwargs)
        except:
            pass
        finally:
            await self.client.send_message(msg.channel, self.show_alert())

    def show_spam(self):
        fp = self.bot_dir + "spam.txt"
        with open(fp, "r", encoding="utf-8") as f:
            local = f.read().strip()
        with open("spam.txt", "r", encoding="utf-8") as f:
            _global = f.read().strip()
        return log_format.show_spam.format(local = local, globals=_global)

    def show_alert(self):
        fp = self.bot_dir + "alert.txt"
        with open(fp, "r", encoding="utf-8") as f:
            local = f.read().strip()
        return log_format.show_alert.format(local = local)

    def __edit_spam(self, add:set=set(), remove:set=set(), cat:str="local", **kwargs):
        for a in add:
            self.spam_words.add(a.strip())
        for r in remove:
            self.spam_words.discard(r.strip())
        if cat.lower() == "global":
            fp = "spam.txt"
            ex = self.bot_dir + "spam.txt"
        else:
            fp = self.bot_dir + "spam.txt"
            ex = "spam.txt"
        with open(ex, "r", encoding="utf-8") as f:
            ex_set = set(f.read().strip().split("\n"))
        spam_set2 = copy.deepcopy(self.spam_words)
        new_set = spam_set2 - ex_set
        with open(fp, "w", encoding="utf-8") as f:
            f.write("\n".join(new_set))
        self.update_spam()
    
    def __edit_alert(self, add:set=set(), remove:set=set(), **kwargs):
        for a in add:
            self.alert_words.add(a)
        for r in remove:
            self.alert_words.discard(r)
        fp = self.bot_dir + "alert.txt"
        with open(fp, "w", encoding="utf-8") as f:
            f.write("\n".join(self.alert_words))
        self.update_alert()

    ## send/edit/del normal msg
    async def send_msg(self, msg:discord.Message, * , op:str="op3"):
        content = msg.content.split("\n")
        match = re.search(r"\d+", content[0])
        if match is not None:
            ch_id = match.group(0)
        else:
            # Channel not specified
            await self.client.send_message(msg.channel, log_format.channel_not_specified)
            return None
        ch = self.client.get_channel(ch_id)
        if ch is None:
            # channel id is different
            await self.client.send_message(msg.channel, log_format.channel_different)
            return None
        if not self.check_permission_send_msg(ch, ch.server.get_member(self.client.user.id)):
            # can't send message
            await self.client.send_message(msg.channel, log_format.cmd_nopermissions.format(words.send_messages))
            return None
        try:
            content = "\n".join(content[1:])
        except:
            content = None
        accept_count = cancel_count = 1
        check_content = log_format.send_message.format(
            ch_id = ch_id,
            file_count = str(len(msg.attachments)),
            content = content,
            op_level = self.op_role_mention[op],
            accept_count = str(accept_count),
            cancel_count = str(cancel_count)
        )
        check = await self.check_execute_cmd(msg, accept_count, cancel_count, content=check_content)
        if check:
            # accept
            await self.client.send_message(msg.channel, log_format.cmd_accept)
        else:
            # cancel
            await self.client.send_message(msg.channel, log_format.cmd_cancel)
            return None
        file_list = self.transfer_files(msg)
        send_message = await self.client.send_message(ch, content)
        await self.send_files(ch, file_list)
        result = log_format.send_message_result.format(
            server = send_message.channel.server.id,
            ch = send_message.channel.id,
            msg = send_message.id
        )
        await self.client.send_message(msg.channel, result)
        
    async def edit_msg(self, msg:discord.Message, dm:bool=False, * , op:str="op3"):
        content_list = msg.content.split("\n")
        try:
            url = content_list[1]
        except:
            #url is not found
            await self.client.send_message(msg.channel, log_format.msg_not_specified)
            return None
        if dm:
            pattern = r"@me/\d+/\d+"
        else:
            pattern = r"\d+/\d+/\d+"
        match = re.search(pattern, url)
        if match:
            server_id, ch_id, msg_id = self.split_msg_url(match.group(0))
        else:
            #not match
            await self.client.send_message(msg.channel, log_format.msg_not_specified)
            return None
        try:
            target = await self.search_message(ch_id, msg_id)
        except:
            await self.client.send_message(msg.channel, log_format.msg_get_error)
        if target.author != self.client.user:
            #target message author is not bot.
            await self.client.send_message(msg.channel, log_format.msg_author_different)
            return None
        try:
            content = "\n".join(content_list[2:])
        except:
            # content is None
            await self.client.send_message(msg.channel, log_format.msg_not_difinition)
            return None
        #check
        accept_count = cancel_count = 1
        check_content = log_format.edit_message.format(
            server = server_id,
            ch = ch_id,
            msg = msg_id,
            content = content,
            op_level = self.op_role_mention[op],
            accept_count = str(accept_count),
            cancel_count = str(cancel_count)
        )
        check = await self.check_execute_cmd(msg, accept_count, cancel_count, content=check_content)
        if check:
            # accept
            await self.client.send_message(msg.channel, log_format.cmd_accept)
        else:
            # cancel
            await self.client.send_message(msg.channel, log_format.cmd_cancel)
            return None
        try:
            await self.client.edit_message(target, new_content=content)
            await self.client.send_message(msg.channel, log_format.edit_message_success)
            return None
        except:
            await self.client.send_message(msg.channel, log_format.cmd_fail)
            return None

    async def send_files(self, ch:discord.Channel, file_list:list):
        for fl in file_list:
            if fl["type"] == "url":
                await self.client.send_message(ch, fl["url"])
            elif fl["type"] == "file":
                await self.client.send_file(ch, fl["fp"])
                #delete tmp file
                os.remove(fl["fp"])

    def split_msg_url(self, string:str):
        return tuple(string.split("/"))
        
    @asyncio.coroutine
    def search_message(self, ch_id, msg_id):
        data = yield from self.client.http.get_message(ch_id, msg_id)
        return self.client.connection._create_message(channel=self.client.get_channel(ch_id), **data)

    def transfer_files(self, msg:discord.Message) -> list:
        if not len(msg.attachments) > 0:
            return list()
        opener = urllib.request.build_opener()
        opener.addheaders=[("User-Agent", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0")]
        urllib.request.install_opener(opener)
        file_list = list()
        for attachment in msg.attachments:
            url = attachment["proxy_url"]
            info = dict()
            if attachment["size"] < 8*1024*1024:
                file_name = self.tmp + attachment["filename"]
                info["type"] = "file"
                info["fp"] = file_name
                urllib.request.urlretrieve(url=url, filename=file_name) # save file.
            else:
                info["type"] = "url"
                info["url"] = url
            file_list.append(info)
        del opener
        return file_list

    ## send-dm/edit-dm/del-dm
    async def send_dm(self, msg:discord.Message, *, op:str="op2"):
        content_list = msg.content.split("\n")
        match = re.search(r"\d+", content_list[0])
        if match is not None:
            user_id = match.group(0)
        else:
            # Channel not specified
            await self.client.send_message(msg.channel, log_format.user_not_specified)
            return None
        member = msg.server.get_member(user_id)
        if member is None:
            await self.client.send_message(msg.channel, log_format.user_not_found)
        try:
            content = "\n".join(content_list[1:])
        except:
            content = None
        accept_count = cancel_count = 1
        check_content = log_format.send_dm.format(
            user = self.save_author_mention(member),
            file_count = str(len(msg.attachments)),
            content = content,
            op_level = self.op_role_mention[op],
            accept_count = str(accept_count),
            cancel_count = str(cancel_count)
        )
        check = await self.check_execute_cmd(msg, accept_count, cancel_count, content=check_content)
        if check:
            # accept
            await self.client.send_message(msg.channel, log_format.cmd_accept)
        else:
            # cancel
            await self.client.send_message(msg.channel, log_format.cmd_cancel)
            return None
        file_list = self.transfer_files(msg)
        try:
            send_message = await self.send_dm_message(member.id, content)
            await self.send_files(send_message.channel, file_list)
            result = log_format.send_message_result.format(
                server = "@me",
                ch = send_message.channel.id,
                msg = send_message.id
            )
        except:
            result = log_format.send_dm_fail
        finally:
            await self.client.send_message(msg.channel, result)

    async def del_dm(self, msg:discord.Message, *, op:str="op2"):
        content_list = msg.content.split("\n")
        try:
            url = content_list[1]
        except:
            #url is not found
            await self.client.send_message(msg.channel, log_format.msg_not_specified)
            return None
        match = re.search(r"@me/\d+/\d+", url)
        if match:
            server_id, ch_id, msg_id = self.split_msg_url(match.group(0))
        else:
            #not match
            await self.client.send_message(msg.channel, log_format.msg_not_specified)
            return None
        try:
            target = await self.search_message(ch_id, msg_id)
        except:
            await self.client.send_message(msg.channel, log_format.msg_get_error)
        if target.author != self.client.user:
            #target message author is not bot.
            await self.client.send_message(msg.channel, log_format.msg_author_different)
            return None
        accept_count = cancel_count = 1
        check_content = log_format.delete_dm.format(
            ch = target.channel.id,
            msg = target.id,
            content = target.content,
            op_level = self.op_role_mention[op],
            accept_count = str(accept_count),
            cancel_count = str(cancel_count)
        )
        check = await self.check_execute_cmd(msg, accept_count, cancel_count, content=check_content)
        if check:
            # accept
            await self.client.send_message(msg.channel, log_format.cmd_accept)
        else:
            # cancel
            await self.client.send_message(msg.channel, log_format.cmd_cancel)
            return None
        try:
            await self.client.delete_message(target)
            await self.client.send_message(msg.channel, log_format.del_message_success)
        except:
            await seld.client.send_message(msg.channel, log_format.del_message_fail)

    ##user
    async def user(self, msg:discord.Message, *, op:str="op2"):
        match = re.search(r"\d+", msg.content)
        if match is None:
            await self.client.send_message(msg.channel, log_format.user_not_specified)
            return None
        try:
            user = await self.client.get_user_info(match.group(0))
        except:
            await self.client.send_message(msg.channel, log_format.user_not_found)
            return None
        content = log_format.get_user_info_result.format(
            user_id = user.id,
            user_name = user.name,
            bot = str(user.bot),
            created_at = user.created_at.strftime("%Y/%m/%d %H:%M:%S"),
            avatar = user.avatar_url,
            server = self.server_member(user, msg.server)
        )
        await self.client.send_message(msg.channel, content)
    
    def server_member(self, user:discord.User, server:discord.Server):
        member = server.get_member(user.id)
        if member is None:
            return str(False)
        else:
            return log_format.user_is_server_member.format(
                server = str(True),
                nick = str(member.nick),
                join = member.joined_at.strftime("%Y/%m/%d %H:%M:%S"),
                roles = "\n\t".join([self.save_role(r) for r in member.roles])
            )

    async def user_exist(self, user_id:str) -> bool:
        try:
            await self.client.get_user_info(user_id)
            return True
        except:
            return False

    ## stop
    async def stop(self, msg:discord.Message, * , op:str="op2"):
        #search target users
        targets = re.findall(r"\d+", msg.content, re.S)
        server = msg.server
        result = list()
        for target in targets:
            member = server.get_member(target)
            if member is not None:
                await self.add_roles(member, {self.config["stop"]}, server.id)
                result.append(member)
        content = log_format.stop_result.format(users="\n".join([self.save_author_mention(m) for m in result]))
        await self.client.send_message(msg.channel, content)

    ## get log
    async def get_msg_log(self, msg:discord.Message, dm:bool=False, *, op:str="op3"):
        match = re.search(r"\d+", msg.content.split("\n")[0])
        if match is not None:
            ch_id = match.group(0)
        else:
            # Channel not specified
            content = log_format.user_not_specified if dm else log_format.channel_not_specified
            await self.client.send_message(msg.channel, content)
            return None
        if dm:
            check = await self.user_exist(ch_id)
            if check:
                ch = await self.get_user_private_channel_by_id2(ch_id)      
            else:
                await self.client.send_message(msg.channel, log_format.user_different)
        else:
            ch = self.client.get_channel(ch_id)
        if ch is None:
            # channel id is different
            content = log_format.private_ch_not_found if dm else log_format.channel_different
            await self.client.send_message(msg.channel, content)
            return None
        if not dm:
            if not self.check_permission_read_message_history(ch, ch.server.get_member(self.client.user.id)):
                # can't read message
                await self.client.send_message(msg.channel, log_format.cmd_nopermissions.format(words.read_message_history))
                return None
        
        await self.client.send_message(msg.channel, log_format.cmd_accept)
        # cmd start
        kwargs = self.spilit_function(msg.content, 2)
        fp, result = await self.logs_from(ch, **kwargs)
        await self.client.send_file(msg.channel, fp, content=result) #send result and file
        os.remove(fp) #remove file
        return None

    async def logs_from(self, channel:discord.Channel, limit:str="100", reverse:str="true", encoding:str="utf-8", **kwargs) -> str:
        start_time = datetime.datetime.now()
        limit = int(limit)
        reverse = False if reverse.lower().strip() == "false" else True
        before = await self.get_datetime_or_message(channel, kwargs.get("before"))
        after  = await self.get_datetime_or_message(channel, kwargs.get("after"))
        around = await self.get_datetime_or_message(channel, kwargs.get("around"))
        fp = self.tmp + "msg_log.txt"
        counter = {"MsgCount": 0, "UserIDs" : set()}
        with open(fp, "w", encoding=encoding) as f:
            async for msg in self.client.logs_from(channel, limit=limit, before=before, after=after, around=around, reverse=reverse):
                f.write(self.save_msg_log(msg, write=False))
                self.logs_counter(msg, counter)
        logs_result = log_format.msg_log_result.format(
            channel = self.save_channel(channel),
            msg_count = str(counter["MsgCount"]),
            user_count = str(len(counter["UserIDs"])),
            limit = str(limit),
            before = self.log_reesult_msg_or_datetime(before),
            after  = self.log_reesult_msg_or_datetime(after),
            around = self.log_reesult_msg_or_datetime(around),
            reverse = str(reverse),
            encoding = encoding,
            start_time = start_time.strftime("%Y/%m/%dT%H:%M:%S"),
            finish_time = datetime.datetime.now().strftime("%Y/%m/%dT%H:%M:%S")
        )
        fp = self.insert_file_head((logs_result + "\n" + "-"*75 + "\n"), fp, encoding=encoding)
        return fp, logs_result

    def logs_counter(self, msg:discord.Message, counter:dict) -> dict:
        counter["MsgCount"] += 1
        counter["UserIDs"].add(msg.author.id)

    async def get_datetime_or_message(self, ch:discord.Channel, string:str):
        if string is None:
            return None
        try:
            r = datetime.datetime.strptime(string, "%Y/%m/%dT%H:%M:%S")
        except:
            try:
                r = await self.search_message(ch.id, string)
            except:
                r = None
        finally:
            return r

    def log_reesult_msg_or_datetime(self, target) -> str:
        if isinstance(target, discord.Message):
            return log_format.msg_url.format(
                server = "@me" if target.server is None else target.server.id,
                ch = target.channel.id,
                msg = target.id
            )
        elif isinstance(target, datetime.datetime):
            return target.strftime("%Y/%m/%dT%H:%M:%S")
        else:
            return words.unspecified

    async def ls(self, msg:discord.Message):
        await self.client.send_message(msg.channel, cmd_msg.ls.format(bot=self.config["NAME"]))

    async def system_message(self, msg:discord.Message, * , op:str="op3"):
        content_list = msg.content.split("\n")
        try:
            action = content_list[0].split()[1].strip().lower()
        except:
            action = "show"
        try:
            fp = self.bot_dir + content_list[1].lstrip("fp= ./").strip()
            if not os.path.exists(fp):
                await self.client.send_message(msg.channel, log_format.file_is_not_exit)
                return None
        except:
            await self.client.send_message(msg.channel, log_format.filepath_not_specified)
            return None
        if action == "edit":
            if len(msg.attachments) > 0:
                url = msg.attachments[0]["proxy_url"]
                copy_fp = self.update_system_message(fp, url=url)
            else:
                try:
                    content = "\n".join(content_list[2:])
                except:
                    await self.client.send_message(msg.channel, log_format.new_content_not_specified)
                    return None
                copy_fp = self.update_system_message(fp, content = content)
            await self.edit_system_message_report(msg.channel, fp, copy_fp)
        else:
            await self.show_system_message(msg.channel, fp)
    
    def update_system_message(self, fp, content:str=None, url:str=None) -> str:
        copy_fp = self.tmp + fp.split("/")[-1]
        shutil.copy(fp, copy_fp)
        if url is not None:
            self.save_file(url, fp)
        elif content is not None:
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            pass
        return copy_fp

    async def edit_system_message_report(self, ch:discord.Channel, fp:str, copy_fp:str):
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()
        await self.client.send_file(ch, copy_fp, content=content)

    async def show_system_message(self, ch:discord.Channel, fp:str):
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()
        await self.client.send_message(ch, content)

    ## receive dm
    async def receive_dm(self, msg:discord.Message):
        content = log_format.receive_dm.format(
            author = self.save_author_mention(msg.author),
            time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            ch = msg.channel.id,
            msg = msg.id,
            content = msg.content
        )
        ch = self.client.get_channel(self.config["receive_dm_ch"])
        await self.client.send_message(ch, content)

    async def receive_dm_edit(self, before:discord.Channel, after:discord.Channel):
        content = log_format.recieve_dm_edit.format(
            author = self.save_author_mention(after.author),
            time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            ch = after.channel.id,
            msg = after.id,
            before = before.content,
            after = after.content
        )
        ch = self.client.get_channel(self.config["receive_dm_ch"])
        await self.client.send_message(ch, content)
    
    async def receive_dm_delete(self, msg:discord.Message):
        content = log_format.receive_dm_delete.format(
            author = self.save_author_mention(msg.author),
            time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            ch = msg.channel.id,
            msg = msg.id,
            content = msg.content
        )
        ch = self.client.get_channel(self.config["receive_dm_ch"])
        await self.client.send_message(ch, content)

    ## Control Role
    @asyncio.coroutine
    def replace_role(self, user_id:str, new_roles:list, server_id:str=None):
        server_id = self.config["action_server_id"] if server_id is None else server_id
        yield from self.client.http.replace_roles(user_id, server_id, new_roles)
    
    async def add_roles(self, member:discord.Member, roles:set, server_id:str=None):
        member_roles = {r.id for r in member.roles}
        new_roles = list(member_roles.union(roles))
        await self.replace_role(member.id, new_roles, server_id)

    async def add_role(self, member:discord.Member, role_id:str, server_id:str=None):
        member_roles = {r.id for r in member.roles}
        member_roles.add(role_id)
        new_roles = list(member_roles)
        await self.replace_role(member.id, new_roles, server_id)
    
    async def remove_role(self, member:discord.Member, role_id:str, server_id:str=None):
        member_roles = {r.id for r in member.roles}
        member_roles.discard(role_id)
        new_roles = list(member_roles)
        await self.replace_role(member.id, new_roles, server_id)

    async def role_control(self, msg:discord.Message, *, op:str="op1"):
        if msg.content.startswith("+color"):
            name = msg.content.strip("+color ").split().pop(0)
            try:
                target = self.color_role[name]
            except:
                await self.client.send_message(msg.channel, log_format.role_not_found)
                return None
            member_roles = {r.id for r in msg.author.roles}
            new_roles = self.exclusion_role(member_roles, self.color_role_set)
            new_roles.add(target)
            await self.replace_role(msg.author.id, list(new_roles))
            result = log_format.role_color_changed.format(msg.author.id, name)
            await self.client.send_message(msg.channel, result)
        elif msg.content.startswith("+"):
            targets = msg.content.lstrip("+").strip().split()
            add_roles = set()
            for target in targets:
                role_id = self.normal_role.get(target)
                if role_id is not None:
                    add_roles.add(role_id)
            member_roles = {r.id for r in msg.author.roles}
            new_roles = member_roles.union(add_roles)
            await self.replace_role(msg.author.id, list(new_roles))
            result = log_format.role_changed.format(msg.author.id)
            embed = self.report_user_role_embed(msg.author)
            await self.client.send_message(msg.channel, result, embed=embed)
        elif msg.content.startswith("-color"):
            member_roles = {r.id for r in msg.author.roles}
            new_roles = member_roles - self.color_role_set
            await self.replace_role(msg.author.id, list(new_roles))
            result = log_format.role_color_reset.format(msg.author.id)
            await self.client.send_message(msg.channel, result)
        elif msg.content.startswith("-"):
            targets = msg.content.lstrip("-").strip().split()
            remove_roles = set()
            for target in targets:
                role_id = self.normal_role.get(target)
                if role_id is not None:
                    remove_roles.add(role_id)
            member_roles = {r.id for r in msg.author.roles}
            new_roles = member_roles - remove_roles
            await self.replace_role(msg.author.id, list(new_roles))
            result = log_format.role_changed.format(msg.author.id)
            embed = self.report_user_role_embed(msg.author)
            await self.client.send_message(msg.channel, result, embed=embed)
        else:
            return None

    def exclusion_role(self, roles:set, targets:set) -> set:
        return (roles - targets)

    def report_user_role_embed(self, member:discord.Member) -> discord.Embed:
        roles = "\n".join([("  ・" + r.name) for r in member.roles])
        em = discord.Embed(type = "rich", description = log_format.role_list.format(roles), color=member.color)
        if member.nick is None:
            name = member.name
        else:
            name = member.nick
        em.set_author(name = name, icon_url=member.avatar_url)
        return em

    ## cmd check
    async def check_execute_cmd(self, msg:discord.Message, done_count:int=1, cancel_count:int=1, **kwargs) -> bool:
        timeout = 300 if kwargs.get("timeout") is None else kwargs["timeout"]
        cmder = msg.author
        cmd_role = self.config["op"]["op1"] if kwargs.get("role") is None else kwargs["roke"]
        if kwargs.get("content") is not None:
            msg = await self.client.send_message(msg.channel, kwargs["content"])
        await self.client.add_reaction(msg, "⭕")
        await self.client.add_reaction(msg, "❌")

        def check(reaction:discord.Reaction, user:discord.User):
            if user == self.client.user:
                return False
            member = reaction.message.server.get_member(user.id)
            return cmd_role in {r.name for r in member.roles}
        
        emoji_count = {"done" : 0, "cancel" : 0}
        loop = True
        while loop:
            rec, user = await self.client.wait_for_reaction(message=msg, check=check)
            if str(rec.emoji) == "⭕":
                emoji_count["done"] += 1
                if emoji_count["done"] >= done_count:
                    break
            elif str(rec.emoji) == "❌":
                emoji_count["cancel"] += 1
                if emoji_count["cancel"] >= cancel_count:
                    loop = False
            else:
                continue
        else:
            # cmd cancel
            return False
        # cmd accept
        return True

    #translation bot
    async def translation_bot(self, msg:discord.Message):
        content = msg.content.lstrip(cmd_trigger.translation[0]) # remove trigger word
        content_list = content.split(" ")
        target = content_list.pop(0) # pop target language
        content = " ".join(content_list) #join content list
        results = self.translate(content, target)
        embed = self.translate_embed(results, content, msg)
        await self.client.send_message(msg.channel, results[0], embed=embed)
    
    def translate_embed(self, results:tuple, content:str, msg:discord.Message) -> discord.Embed:
        """
        @para results:tuple (result, target, source, confidence)
        """
        color = msg.author.color if msg.author.color != discord.Colour.default() else discord.Colour(self.bot_color)
        embed = discord.Embed(
            type = "rich",
            timestamp = msg.timestamp,
            description = content[0:30] + ("..." if len(content) >= 30 else ""),
            color = color
        )
        embed.set_author(name = self.user_name(msg.author), icon_url=msg.author.avatar_url)
        # embed.set_author(name = self.user_name(msg.author))
        embed.set_footer(text = "translation: {0} → {1}. language detection confidence: {2}%".format(results[2], results[1], results[3]))
        return embed

    #Basic function
    def user_name(self, author):
        if isinstance(author, discord.Member):
            if author.nick is not None:
                return author.nick
        return author.name

    def change_color_code(self):
        RGB = self.config["color"] #list
        return (RGB[0]*256*256 + RGB[1]*256 + RGB[2])

    def insert_file_head(self, insert_content:str, fp:str, * , new_fp:str=None, encoding:str="utf-8") -> str:
        if new_fp is None:
            new_fp = fp #copy file name
            fp = fp + "dump" #new file name
            if os.path.exists(fp):
                os.remove(fp)
            os.rename(new_fp, fp) #rename to dump file
        with open(new_fp, "w", encoding=encoding) as nf:
            nf.write(insert_content + "\n") #insert
            with open(fp, "r", encoding=encoding) as f:
                line = f.readline()
                while line:
                    nf.write(line) # copy file content
                    line = f.readline()
        os.remove(fp) # remove dump file
        return new_fp

    def spilit_function(self, content, start_line=1, argument=None, punctuation="=", * , split="\n", rest_return=True):
        return_dict = dict()
        content_list = content.split(split)
        if start_line >= 2:
            if rest_return:
                return_dict["rest_first"] = split.join(content_list[:(start_line - 1)])
            else:
                pass
            del content_list[:(start_line - 1)]
        else:
            pass
        if argument is None:
            num = 0
            for cl in content_list:
                if punctuation in cl:
                    cll = cl.split(punctuation)
                    return_dict[cll[0].strip()] = punctuation.join(cll[1:]).strip()
                    num += 1
                else:
                    break
            del content_list[:num]
            if rest_return:
                return_dict["rest_last"] = split.join(content_list)
            else:
                pass
            return return_dict
        elif isinstance(argument, str):
            num = 1
            for cl in content_list:
                if argument in cl.split(punctuation):
                    return_dict[argument] = punctuation.join(cl.split(punctuation)[1:])
                    del content_list[:num]
                    break
                else:
                    num += 1
            if rest_return:
                return_dict["rest_last"] = split.join(content_list)
            else:
                pass
            return return_dict
        elif isinstance(argument, (list, set, tuple)):
            num = 0
            num_else = 0
            for cl in content_list:
                cll = cl.split(punctuation)
                if cll[0] in argument:
                    return_dict[cll[0]] = punctuation.join(cll[1:])
                    num += 1
                    num += num_else
                    num_else = 0
                else:
                    num_else += 1
            del content_list[:num_else]
            if rest_return:
                return_dict["rest_last"] = split.join(content_list)
            else:
                pass
            return return_dict
        else:
            return dict()

    async def report_developer(self, msg:discord.Message):
        content = log_format.report_developer.fromat(
            msg_id = msg.id,
            time = msg.timestamp.strftime("%Y/%m/%d %H:%M:%S"),
            edit_time = msg.edited_timestamp.strftime("%Y/%m/%d %H:%M:%S") if isinstance(msg.edited_timestamp, datetime,datetime) else "not editd",
            type = str(msg.type),
            server = "{0} (ID: {1})".format(msg.server.name, msg.server.id),
            channel = "{0} (ID: {1})".format(msg.channel.name, msg.channel.id),
            author = self.save_author_mention(msg.author),
            embeds = "",
            attachiments = "",
            mentions = "",
            ch_mentions = "",
            role_mentions = "",
            content = msg.content
        )
        await self.send_dm_message(Developer.id, content)

    async def test(self, msg:discord.Message):
        pattern = "|".join(self.spam_words)
        match = re.search(pattern, msg.content)
        if not match:
            print("no match")
        else:
            print("match!")
            print(match.group())

#test
if __name__ == "__main__":
    trans = Translation()
    while True:
        target = input("target: ")
        source = input("source: ")
        content = input("content: ")
        trans.test_translation(content, target, source)
