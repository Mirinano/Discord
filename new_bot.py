import sys, os, shutil

argv = sys.argv

try:
    name = argv[1]
except:
    name = input("BOT name: ")

#create new config file
print("create config file")
fp = "./config/{}.json".format(name)
shutil.copyfile("./config/format.json", fp)
print("\tsuccess!")
print("\t\t", fp)

#create setting directory
print("create bot dir")
fp = "./bot/{}".format(name)
shutil.copytree("./bot/format", fp)
print("\tsuccess!")
print("\t\t", fp)
