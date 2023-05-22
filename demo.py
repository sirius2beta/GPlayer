import GPlayer

def onMsg(topic, message):
  if topic == 'testcmd':
    print(f'{topic} : {message}')

gplayer = GPlayer.GPlayer()
gplayer.onMsg = onMsg

