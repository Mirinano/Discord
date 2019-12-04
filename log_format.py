#message logs
msg_log = """送信時刻: {time}
送信者: {user} (ID: {user_id})
メッセージID: {msg_id}
メッセージタイプ: {msg_type}
添付ファイル: {attachments}
embedの有無: {embed}
内容: {content}"""
msg_change_log = """変更時間: {after_time}
送信時間: {before_time}
送信者: {user} (ID: {user_id})
メッセージID: {msg_id}
メッセージタイプ: {msg_type}
添付ファイル: {attachments}
embedの有無: {embed}
変更前の内容:
{before_content}
******************************
変更後の内容:
{after_content}"""
msg_delete_log = """削除時間: {delete_time}
送信時刻: {time}
送信者: {user} (ID: {user_id})
メッセージID: {msg_id}
メッセージタイプ: {msg_type}
添付ファイル: {attachments}
embedの有無: {embed}
内容: {content}"""

msg_log_result = """```
【メッセージログ取得結果】
チャンネル  : {channel}
メッセージ数: {msg_count}
書き込み者数: {user_count}

コマンドログ
limit   : {limit}
before  : {before}
after   : {after}
around  : {around}
reverse : {reverse}
encoding: {encoding}

コマンド開始時刻: {start_time}
コマンド終了時刻: {finish_time}
```"""

msg_url = "https://discordapp.com/channels/{server}/{ch}/{msg}"

#control role
role_not_found = "アイドルの名前を間違えていませんか？`+color アイドル名`と記入してください。"
role_color_changed = "<@{0}>Pさんのお名前を{1}カラーに変更しました！"
role_color_reset = "<@{0}>Pさんの名前の色をリセットしました！"
role_changed = "<@{0}>Pさんの担当表示を変更しました！"
role_list = "役職一覧:\n{0}"

#member join/remove
join_member_message = """時刻: {time}
参加メンバー名: {user}
メンション: <@{user_id}> (ID: {user_id})
アカウント作成時刻: {user_create}
現在のメンバー数: {count}
入室案内送信: {send_ch}
DM送信: {send_dm}"""
remove_member_message = """時刻: {time}
退出メンバー名: {user}
メンション: <@{user_id}> (ID: {user_id})
アカウント作成時刻: {user_create}
現在のメンバー数: {count}"""

disagreement_rule_action_fail = """【緊急: ルール不同意者への対処】{op}
発生時刻: {time}
対象者　: {target}
内容　　: ルールへの不同意を示す"❌"を選択。
対処ログ: {log}
"""

#voice log
voice_start_message = """時刻: {time}
{user} (<@{user_id}> {user_id})が {ch_name} (ID: {ch_id})でボイスチャットを開始しました。
ログを取ります。"""
voice_finish_message = """{ch_name} (ID: {ch_id})でのボイスチャットが終了しました。
終了時刻: {time}
稼働時間: {operating_time}"""
voice_start = """開始時刻: {time}
チャンネル: {name} (ID: {id})\n"""
voice_finish = """終了時刻: {time}
稼働時間: {operating_time}\n"""
voice_join   = "{time} | 参加 | 参加人数: {count} | {user} (ID: {user_id}) | {status}\n"
voice_remove = "{time} | 退出 | 参加人数: {count} | {user} (ID: {user_id}) | {status}\n"
voice_move_before = "移動先: {ch} | {status}"
voice_move_after  = "移動元: {ch} | {status}"
voice_change      = "{time} | 変更 | 参加人数: {count} | {user} | {content}\n"
voice_change_status_self = "{status} を {action} に変更しました。"
voice_change_status_server = "管理者の操作により {status} を {action} に変更しました。"
voice_status = "マイク: {self_mic} | スピーカー: {self_speaker} | サーバー側マイク: {mic} | サーバー側スピーカー: {speaker}"

#cmd msg
cmd_cancel  = "コマンドの実行を中止します。"
cmd_accept  = "コマンドを実行します。"
cmd_fail    = "コマンドの実行に失敗しました。"
cmd_success = "コマンドの実行に成功しました。"
cmd_nopermissions = "コマンドの実行に必要な権限がありません。\n必要な権限: {}"

filepath_not_specified = "ファイルパスが未指定です。"
file_is_not_exit = "指定されたファイルは存在しません。"
new_content_not_specified = "更新後の文章が指定されていません。"

system_file_update_log = """【システムファイルの更新】
file name: {fp}
```
{content}
```
更新前のファイルを添付します。"""

#send/edit/del message
channel_not_specified = "チャンネルが未指定です。"
channel_different = "チャンネルIDが違います。"
channel_not_send_message = "チャンネルに書き込むための権限がありません。"
msg_not_specified = "メッセージURLが未指定または不正な値です。"
msg_get_error = "メッセージの取得に失敗しました。権限の設定等を確認してください。"
msg_author_different = "メッセージの投稿者がBOT自身ではないため編集/削除できません。"
msg_not_difinition = "メッセージの内容が未設定です。"
send_message = """【メッセージ送信確認】
<#{ch_id}> に次のメッセージを送信します。
添付ファイルの数は{file_count}件です。
------------------------
{content}
------------------------
コマンド承認: {op_level}
実行に必要な承認人数: {accept_count}
中止に必要な承認人数: {cancel_count}"""
send_message_result = """メッセージの送信が完了しました。
送信したメッセージへのリンク。
https://discordapp.com/channels/{server}/{ch}/{msg}

添付ファイルがある場合、これ以外にもメッセージのリンクがあります。"""
edit_message = """【メッセージ編集確認】
次のメッセージの内容を以下のように編集します。
対象メッセージ: https://discordapp.com/channels/{server}/{ch}/{msg}
------------------------
{content}
------------------------
コマンド承認: {op_level}
実行に必要な承認人数: {accept_count}
中止に必要な承認人数: {cancel_count}
"""
edit_message_success = "メッセージの編集が完了しました。"

#send/edit/del dm
user_not_specified = "ユーザーが未指定です。"
user_different = "ユーザーIDが違います。ユーザーIDを確認してください。"
user_not_found = "このサーバーに存在しないユーザーを指定しています。ユーザーIDを確認してください。"
private_ch_not_found = "ユーザーとのDM履歴がありません。"
send_dm = """【ダイレクトメッセージ送信確認】
{user}に次のメッセージを送信します。
添付ファイルの数は{file_count}件です。
------------------------
{content}
------------------------
コマンド承認: {op_level}
実行に必要な承認人数: {accept_count}
中止に必要な承認人数: {cancel_count}"""
send_dm_fail = "ダイレクトメッセージの送信に失敗しました。\n対象者がサーバーメンバーからのDMの受け取りを不許可にしている可能性があります。"
delete_dm = """【ダイレクトメッセージ削除確認】
次のメッセージを削除します。
対象メッセージ: https://discordapp.com/channels/@me/{ch}/{msg}
------------------------
{content}
------------------------
コマンド承認: {op_level}
実行に必要な承認人数: {accept_count}
中止に必要な承認人数: {cancel_count}
"""
del_message_success = "メッセージの削除に成功しました。"
del_message_fail = "メッセージの削除に失敗しました。ess"

#receive dm
receive_dm = """【DM受信】
送信者: {author}
送信時間: {time}
URL: https://discordapp.com/channels/@me/{ch}/{msg}
------------------------
{content}"""
recieve_dm_edit = """【DM編集検知】
編集者: {author}
編集時間: {time}
URL: https://discordapp.com/channels/@me/{ch}/{msg}
------------before------------
{before}
------------after------------
{after}"""
receive_dm_delete = """【DM削除検知】
削除者: {author}
削除時間: {time}
URL: https://discordapp.com/channels/@me/{ch}/{msg}
------------------------
{content}"""

#user info
get_user_info_result = """【ユーザー情報照会結果】
メンション: <@{user_id}>
```
Name: {user_name}
ID  : {user_id}
BOT?: {bot}
createat  : {created_at}
avatar url: {avatar}
in server?: {server}
"""
user_is_server_member = """{server}
Nick name: {nick}
joined at: {join}
roles:
\t{roles}
```"""

#ban/kick result message
kick_result = "kicked!"
ban_result = "baned!"
unban_result = "unban!"
ban_kick_result_log = """{action} log
命令時間: {start_time}
完了時間: {end_time}
{details}"""
ban_kick_result_user = """対象ID: {user_id}
{info}"""
user_info = """アカウント名: {user}
メンション: <@{user_id}> (ID: {user_id})
アカウント作成時刻: {user_create}
DM送信: {dm}
__{action}: {judg}__"""
ban_kick_check = """【{action}実行確認】
実行者: {cmder}
対象者: 
\t{targets}
DM送信: {send_dm}
DM内容: {dm_content}
------------------------
コマンド承認: {op_level}
実行に必要な承認人数: {accept_count}
中止に必要な承認人数: {cancel_count}
"""

#stop
stop_result = """【発言の禁止処置】
次のユーザーの発言を一時的に停止しました。
{users}
処置の解除には、役職を管理(Manage Role)権限を持つ管理メンバーによる手動対応が必要です。"""

#statistics
statistics = """【統計情報】
サーバー名: {server_name}
サーバーID: {server_id}
サーバー作成時刻: {server_create}

オーナー: {owner} (ID: {owner_id})
メンバー数: {member_count}

1日のメッセージ総数: {msg_count}
1日の書き込み者数: {writer_count}

サーバーリージョン: {region}
AFK時間: {afk_time}

最上位役職: {top_role}
\t{top_users}

デフォルトチャンネル: {default_channel}
デフォルトロール: {default_role}

招待リンク一覧: 
\t{invites}

役職一覧:
\t{roles}

チャンネル一覧:
\t{channels}
"""
statistics_simple = """```
【統計情報】
サーバー名: {server_name}
サーバーID: {server_id}
サーバー作成時刻: {server_create}
オーナー: {owner} (ID: {owner_id})
メンバー数: {member_count}
サーバーリージョン: {region}
AFK時間: {afk_time}
最上位役職: {top_role}
\t{top_users}
デフォルトチャンネル: {default_channel}
デフォルトロール: {default_role}
招待リンク一覧: 
\t{invites}
```"""
statistics_full = """【統計情報】
サーバー名: {server_name}
サーバーID: {server_id}
サーバー作成時刻: {server_create}

オーナー: {owner} (ID: {owner_id})
メンバー数: {member_count}

過去24時間のメッセージ総数: {msg_count}
\tチャンネル毎のメッセージ数:
\t{ch_msg_count}
過去24時間の書き込み者数: {writer_count}
\t書き込み者一覧:
\t{}

サーバーリージョン: {region}
AFK時間: {afk_time}

最上位役職: {top_role}
\t{top_users}

デフォルトチャンネル: {default_channel}
デフォルトロール: {default_role}

招待リンク一覧: 
\t{invites}

役職一覧:
\t{roles}

チャンネル一覧:
\t{channels}
"""
save_invite = """URL: {URL}
{indent}\t作成時刻　: {created_at}
{indent}\t使用回数　: {uses}
{indent}\t仕様上限　: {max_uses}
{indent}\t作成者　　: {inviter}
{indent}\tチャンネル: {channel}
"""
member_count = "Memver Count: {}"

alert = """【{level}：{detail}】 {mentions}
検知時刻　: {time}
理由　　　: {reason}
対処　　　: {action}
チャンネル: {channel}
対象者　　: {author}
リンク　　: {url}
----------------------------------------
{content}"""
alert_reasen_match = "次のワードを含むメッセージ: {}"

show_spam = """【グローバルスパムワード】
```
{globals}
```
【ローカルスパムワード】
```
{local}
```"""

show_alert = """【アラートワード】
```
{local}
```"""

report_developer = """【Message Report】
```
Msg ID        : {msg_id}
Msg Time      : {time}
Edit Time     : {edit_time}
Msg type      : {type}
Server        : {server}
Channel       : {channel}
Author        : {author}
Attachments   : {attachments}
Embeds        : {embeds}
Mentions      : {mentions}
CH Mentions   : {ch_mentions}
Role Mentions : {role_mentions}
---------------------------------------------------
{content}
```"""
