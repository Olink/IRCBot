import sys
import argparse
import itertools
import threading

import Broadcaster
import PluginLoader
import IRCLib.client

target = None
plugins = []
broadcaster = None

def on_connect(connection, event):
    if IRCLib.client.is_channel(target):
        connection.join(target)
        return

def get_lines():
    while(True):
        yield sys.stdin.readline().strip()

def main_loop(connection):
    for line in itertools.takewhile(bool, get_lines()):
        connection.privmsg(target, line)
    connection.quit("IRC Bot test is quiting now")

def on_disconnect(connection, event):
    for p in plugins:
        p.teardown()
    raise SystemExit()

def on_message(connection, event):
    broadcaster.on_chat.fire(event)

def on_chat(event):
    print(event.source.nick + ': ' + event.arguments[0])   

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('server')
    parser.add_argument('nickname')
    parser.add_argument('target')
    parser.add_argument('-p', '--port', default=6667, type=int)
    return parser.parse_args()

def main():
    global target
    global plugins
    global broadcaster

    broadcaster = Broadcaster.Broadcaster()
    broadcaster.on_chat += on_chat
    args = get_args()
    target = args.target
    
    client = IRCLib.client.IRC()

    try:
        c = client.server().connect(args.server, args.port, args.nickname)
    except IRCLib.client.ServerConnectionError:
        print(sys.exc_info()[1])
        raise SystemExit(1)

    index = 0
    plugins = []

    for i in PluginLoader.get_plugins():
        print("Loading plugin " + i["name"])
        plugin = PluginLoader.load_plugin(i)

        plugins.append(plugin)
        plugin.run(broadcaster)

    c.add_global_handler("welcome", on_connect)
    c.add_global_handler("disconnect", on_disconnect)
    c.add_global_handler('pubmsg', on_message)

    threading.Thread(target = main_loop, args = (c,)).start()

    client.process_forever()

if __name__ == '__main__':
    main()
