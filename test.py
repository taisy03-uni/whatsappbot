from Whatapp import WhatsApp
import time 

bot = WhatsApp()
while True:
    unread = bot.send_message()
    if unread:
        print(unread)
    else:
        print(unread)
    userinput = input("Do you want to coninue (y/n)")
    if userinput == "y":
        bot.send_message_to_chat(unread)
    # request input from user to continue otherwise break
    #TODO
    time.sleep(20)# Check every 5 seconds