import imp
import os

PluginFolder = "./plugins"
MainModule = "__init__"

def get_plugins():
    plugins = []
    possible_plugins = os.listdir(PluginFolder)
    for i in possible_plugins:
        location = os.path.join(PluginFolder, i)
        if not os.path.isdir(location) or not MainModule + ".py" in os.listdir(location):
            continue
        info = imp.find_module(MainModule, [location])
        plugins.append({"name": i, "info": info})

    return plugins

def load_plugin(plugin):
    return imp.load_module(MainModule, *plugin["info"])