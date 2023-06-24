from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

bot = ChatBot("Ron Obvious")

trainer = ListTrainer(bot)

trainer.train([
    "Hello",
    "Hi there!",
    "How are you doing?",
    "I'm doing great.",
    "That is good to hear"
])

while True:
    try:
        #获取用户输入
        message = input("您:")
        #获取回复
        response = bot.get_response(message)
        #输出回复
        print(response)
    except (KeyboardInterrupt, EOFError, SystemExit):
         break