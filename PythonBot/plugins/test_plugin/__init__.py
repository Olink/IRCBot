def on_chat(event):
    print('test_plugin>' + event.source.nick + ': ' + event.arguments[0])

def run(broadcaster):
    broadcaster.on_chat += on_chat