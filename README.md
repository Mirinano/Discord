# Discord Bot Code

Discord Bot code for administrator support.

The following system is implemented.

  BAN command\n
  UNBAN command\n
  Kick command\n
  STOP command\n
  DM send / edit / delete commands\n
  Send / edit message command\n
  Message log acquisition function (DM, normal)\n
  Statistical information acquisition command\n
  User information inquiry command\n
  Automatic BAN function (anti-spam function)\n
  Message alert function\n
  Message log storage function\n
  Message log transmission function\n
  Voice channel operation log storage function\n
  Translation function\n
  Automatic job title assignment function
  
Program file description\n
  main.py: This program starts BOT.\n
  bot.py: A basic file that describes all the code that BOT processes.\n
  API_tolen.py: Describes the API key for the GCP translation API.\n
  cmd_msg.py: Stores messages used when executing program commands.\n
  cmd_trigger.py: Describes the commands that can be executed in the program and their op levels. It is recommended to change it with cmd_msg.py to eliminate differences in op permissions.\n
  help_msg.py: Contains help messages about commands that can be executed by the program.\n
  log_format.py: Describes the format for outputting the log of commands executed by the program.\n
  words.py: A file that specifies important words that are used many times in the program.\n
  fw_wrap.py: A program that splits non-breaking character strings at appropriate points.\n
  
  new_bot.py: This is a program that creates basic files in a batch when adding a BOT. Copy format.json and format directory of bot directory.
  
  spam.txt: Describes all BOT common spam words. The delimiter is a line feed.
