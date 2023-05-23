import GPlayer

def on_msg(topic, message):
  print('onMsg callback;')
  if topic == 'testcmd':
    print(f'{topic} : {message}')

gplayer = GPlayer.GPlayer()
gplayer.on_msg = on_msg
gplayer.sendMsg('Hello PC')

