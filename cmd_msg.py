ban_kick_check = """【{action}実行確認】
実行者: {cmder}
対象者: 
\t{targets}
DM送信: {send_dm}
DM内容: {dm_content}

コマンド承認: {op_level}
実行に必要な承認人数: {accept_count}
中止に必要な承認人数: {cancel_count}
"""

ls = """```
{bot} <- Current directory
|
|- messages
|  |
|  |- ban_msg.txt
|  |- kick_msg.txt
|  |- welcome-ch.txt
|  |- welcome-dm.txt
|  |- disagreement_msg.txt
|
|- roles
   |
   |- color_role.txt
   |- normal_role.txt
```
ex: `./messages/welcome-dm.txt` or `messages/welcome-dm.txt`"""
