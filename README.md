# Discord Bot Code

Discord Bot code for administrator support.
The following system is implemented.
  BAN command
  UNBAN command
  Kick command
  STOP command
  DM send / edit / delete commands
  Send / edit message command
  Message log acquisition function (DM, normal)
  Statistical information acquisition command
  User information inquiry command
  Automatic BAN function (anti-spam function)
  Message alert function
  Message log storage function
  Message log transmission function
  Voice channel operation log storage function
  Translation function
  Automatic job title assignment function
  
Program file description
  main.py: This program starts BOT.
  bot.py: A basic file that describes all the code that BOT processes.
  API_tolen.py: Describes the API key for the GCP translation API.
  cmd_msg.py: Stores messages used when executing program commands.
  cmd_trigger.py: Describes the commands that can be executed in the program and their op levels. It is recommended to change it with cmd_msg.py to eliminate differences in op permissions.
  help_msg.py: Contains help messages about commands that can be executed by the program.
  log_format.py: Describes the format for outputting the log of commands executed by the program.
  words.py: A file that specifies important words that are used many times in the program.
  fw_wrap.py: A program that splits non-breaking character strings at appropriate points.
  
  new_bot.py: This is a program that creates basic files in a batch when adding a BOT. Copy format.json and format directory of bot directory.
  
  spam.txt: Describes all BOT common spam words. The delimiter is a line feed.
