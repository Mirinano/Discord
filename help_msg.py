#!python3.6
main_help = """Help Message
```
/help <command>
```
See help message for command.

You can use the following command:
```
{}
```"""

help_cmd = {
    "op2" : [
        "/ban",
        "/unban",
        "/kick",
        "/stop",
        "/send-dm",
        "/edit-dm",
        "/del-dm",
        "/get-dm",
        "/user",
        "/spam",
        "/alert",
        "/statistics"
    ],
    "op3" : [
        "/send-msg",
        "/edit-msg",
        "/get-log",
        "/system-message",
        "/ls"
    ],
    "op4" : [
        "$$send-log$$",
        "$$send-log-today$$",
        "$$stop-server$$ ##undone",
        "$$restart-server$$ ##undon",
        "$$mass-spam$$"
    ]
}

help_message = {
    "ban" : """```
/ban <user> 
<*option> = <value>
<text>
```
Bans a Member from the server they belong to.
```
required:
    user | user-mention or user-id. ex: /ban @test#111 123456 789012
option: 
    day | default: 1      | int<1-7>. How many days before the message is deleted.
    dm  | default: config | bool<true, false>. Whether to send DM to the target person.
    dm-original | default: false | bool<true, false>. Whether to send the original dm message. If true, text written after option specification will be sent. If false, boilerplate text will be sent.
    text | The text of the original message to send. Ignored if dm-original is false.
```""",

    "unban" : """```
/unban <user>
```
Unbans a User from the server they are banned from.
```
required:
    user | user-mention or user-id. ex: /unban @test#111 123456 789012
```""",

    "kick" : """```
/kick <user> 
<*option> = <value>
<text>
```
Kicks a Member from the server they belong to.
```
required:
    user | user-mention or user-id. ex: /kick @test#111 123456 789012
option: 
    day  | default: 1      | int<1-7>. How many days before the message is deleted.
    dm   | default: config | bool<true, false>. Whether to send DM to the target person. 
    dm-original | default: false | bool<true, false>. Whether to send the original dm message. If true, text written after option specification will be sent. If false, boilerplate text will be sent.
    text | The text of the original message to send. Ignored if dm-original is false.
```""",

    "stop" : """```
/stop <user>
```
Stop writing members. A dedicated title is granted.
```
required:
    user | user-mention or user-id. ex: /stop @test#111 123456 789012
```""",

    "spam" : """```
/spam <action>
<word>
```
Check spam words and add spam words.
```
option:
    action | default: check | <check, add, remove>.
    word   | default: None  | Add or remove words to auto-ban. Write one word per line.
```""",

    "statistics" : """```
/statistics <type>
```
Get server statistics.
When simple is specified, simple statistical information is displayed.
```
option:
    type | default: None | <None, simple>.
```""",

    "send-dm" : """```
/send-dm <user>
<text>
```
Send DM message to server members.
```
required:
    user | user-mention or user-id. ex: /send-dm @test#111 123456 789012
    text | The text to send.
```""",

    "edit-dm" : """```
/edit-dm
<url>
<text>
```
Edit DM message by Bot sent.
```
required:
    url  | message url link or "@me/channel-id/message-id"
    text | New text to send
```""",

    "del-dm" :"""```
/del-dm
<url>
```
Delete DM by BOTs.
```
required:
    url  | message url link or "@me/channel-id/message-id"
```""",

    "get-dm" : """```
/get-dm <user>
<*option> = <value>
```
Get Dm logs with members.
If no option is specified, the latest 100 messages are retrieved.

Use `/get-log` to specify the DM channel ID for the user.

```
required:
    user | user-mention or user-id. ex: /get-dm @test#111
option:
    limit    | default: 100   | int. The number of messages to retrieve.
    before   | default: None  | YYYY/MM/DDThh:mm:ss. 
    after    | default: None  | YYYY/MM/DDThh:mm:ss. 
    around   | default: None  | YYYY/MM/DDThh:mm:ss.
    encoding | default: utf-8 | the name of the encoding used to decode or encode the file. ex. Shift-JIS
```""",

    "user" : """```
/user <user>
```
Get User Info.
```
required:
    user | user-mention or user-id. ex: /user @test#111
```""",

    "send-msg" : """```
/send-msg <channel>
<text>
```
Send Message to channel.
```
required:
    channel | channel id or channel mention
    text    | The text to send.
```""",

    "edit-msg" : """```
/edit-msg
<url>
<text>
```
Edit Message by Bot sent.
```
required:
    url  | message url link or "server-id/channel-id/message-id
    text | New text.
```""",

    "get-log" : """```
/get-log <channel>
<*option> = <value>
```
Get Channel Message Log.
If no option is specified, the latest 100 messages are retrieved.
```
required:
    channel  | channel mention or channel id. Channel you want to get log.
option:
    limit    | default: 100   | int. The number of messages to retrieve.
    before   | default: None  | YYYY/MM/DDThh:mm:ss or message_id. 
    after    | default: None  | YYYY/MM/DDThh:mm:ss or message_id. 
    around   | default: None  | YYYY/MM/DDThh:mm:ss or message_id.
    encoding | default: utf-8 | the name of the encoding used to decode or encode the file. ex. Shift-JIS
```""",

    "ls" : """```
/le
```
show system message files.""",

    "system-message" : """```
/system-message <action>
fp = <value>
<content>

attachments: new system file
```
Edit files such as system messages.
All files under the BOT directory can be overwritten. Directories and files can be checked with the "/ dir" command.
Specify the file path with a complete name.
```
parameter:
    action | default: show  | <show|edit>.
    fp     | default: None  | edit file path.
option:
    content| default: None  | new content.
    attachiments | file to overwrite. It takes precedence over content.
```""",

    "$$send-log$$" : """```
$$send-log$$
```
Force yesterday's message log to be sent.
This command is set by the producer for management purposes to force the action that BOT performs at startup.""",


    "$$send-log-today$$" : """```
$$send-log-today$$
```
The message log of the day is forcibly sent.
It is intended to be used when an administrator wants to check logs immediately.""",

    "$$stop-server$$" : """```
$$stop-server$$
```
All members are prohibited from sending messages except those with higher positions than BOT.
First, sending a message is prohibited from the role setting.
Next, scan the authority setting of the channel and change it to disallowed if there is an individual permission.
The change will be as complete as possible, but the operation will increase depending on the setting.
Since the authority change is saved in the log, it can be restored by performing the BOT operation in reverse order.
You can also use the "$$restart-server$$" command to restart, but the restart command is never perfect.""",

    "$$restart-server$$" : """```
$$restart-server$$
```
This command restores a server that has been stopped with the $$stop-server$$ command.
Perform recovery based on the log file of the $$stop-server$$ command.
The return with this command is not complete. Recovery by the administrator is also required.""",

    "$$global-spam$$" : """```
$$global-spam$$ <action>
<word*>
```
This command adds spam words that are common to all BOTs managed by BOT developers.
Although intended for use by BOT developers, users with administrator privileges on the installed server can also be used.
```
Check spam words and add spam words.
```
option:
    action | default: check | <add, remove>.
    word   | default: None  | Add or remove words to auto-ban. Write one word per line.
```"""
}
