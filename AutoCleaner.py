# -*- coding: utf-8 -*-
import copy
import time
import json
import os

Prefix = '!!ac'
stop = False
item_counter = False
maxtime = 60
time_counter = None
ConfigList = []

ConfigFileFolder = 'config/'
ConfigFilePath = ConfigFileFolder + 'AutoCleaner.json'

HelpMessage = '''
§7------------§bMCD AutoCleaner§7------------
一个可定时的扫地机插件(在白名单中物品可以避免被删除)
§a【格式说明】§r
§7''' + Prefix + '''§r 显示帮助信息
§7''' + Prefix + ''' start §r<时间> 单位：秒 以 <时间>(可取45-600) 秒间隔清理物品
§7''' + Prefix + ''' stop §r停止运行
§7''' + Prefix + ''' killall §r立即清理物品
§7''' + Prefix + ''' status §r显示当前扫地机状态
§7''' + Prefix + ''' whitelist/blacklist add <物品> §r添加<物品>进入白/黑名单
§7''' + Prefix + ''' whitelist/blacklist remove <物品> §r从白/黑名单中删除<物品>
§7''' + Prefix + ''' list §r显示黑名单和白名单中已有的物品
§7''' + Prefix + ''' mode <whitelist/blacklist> §r切换扫地机模式为白名单/黑名单'''

#帮助信息
def help_message(server ,info):
    server.reply(info,HelpMessage)

def write_file(text):
    with open(ConfigFilePath, 'w') as f:
        f.write(json.dumps(text,ensure_ascii=False))
        f.close

def load_config():
    global ConfigList
    with open(ConfigFilePath, 'r') as f:
        ConfigList = json.load(f)

def write_config(mode,type,text,server,info):
    global ConfigList
    whitelist = ConfigList[1]["Whitelist"]
    blacklist = ConfigList[2]["Blacklist"]
    api = server.get_plugin_instance('MinecraftItemAPI')
    if not api.getMinecraftItemInfo(text):
        server.reply(info, 'Unknown Minecraft item ID')
        return
    if mode == 'whitelist':
        if not text in whitelist and type == 'add':
            whitelist.append(text)
            ConfigList[1]["Whitelist"] = whitelist
            write_file(ConfigList)
            server.reply(info, 'Successful')
        elif text in whitelist and type == 'remove':
            whitelist.remove(text)
            ConfigList[1]["Whitelist"] = whitelist
            write_file(ConfigList)
            server.reply(info, 'Successful')
        else:
            server.reply(info,'Failed')
    elif mode == 'blacklist':
        if type == 'add':
                blacklist.append(text)
                ConfigList[2]["Blacklist"] = blacklist
                write_file(ConfigList)
                server.reply(info, 'Successful')
        elif type == 'remove':
                blacklist.remove(text)
                ConfigList[2]["Whitelist"] = blacklist
                write_file(ConfigList)
                server.reply(info, 'Successful')
        else:
            server.reply(info, 'Failed')
    else:
        server.reply(info, 'Unkonwn Mode')

def mode_change(mode):
    global ConfigList
    ConfigList[0]["mode"] = mode
    write_file(ConfigList)

    #停机
def ac_stop(server ,info):
    global stop
    global time_counter
    if stop:
        stop = False
        server.say('§7[§9AutoC§r/§bINFO§7] §b扫地机停止运行')
        time_counter = None
    else:
        server.reply(info,'§7[§9AutoC§r/§cERROR§7] §b扫地机未开启')

    #NBT格式写入
def get_nbt(name,mode):
    if mode == 'whitelist':
        return ',nbt=!{Item:{id:"minecraft:' + name + '"}}'
    else:
        return ',nbt={Item:{id:"minecraft:' + name + '"}}'
    
    #清理计时
def ac_start(server ,info):
    global stop
    global maxtime
    global time_counter
    stop = True
    server.say('§7[§9AutoC§r/§bINFO§7] §b扫地机以 §e{} §b秒间隔开始运行'.format(maxtime))
    maxtimei = int(maxtime)
    while(stop == True):
        for time_counter in range(1 ,maxtimei):
            if stop:
                if maxtimei - time_counter == 30:
                    server.say('§7[§9AutoC§r/§bINFO§7] §b还有 §e30 §b秒，清理掉落物')
                if maxtimei - time_counter <= 5:
                    server.say('§7[§9AutoC§r/§bINFO§7] §b还有 §e{} §b秒，清理掉落物'.format(maxtimei - time_counter))
                time.sleep(1)
            else:
                return
        kill_item(server)
        
    #清理物品
def kill_item(server):
    global item_counter
    mode = ConfigList[0]["mode"]
    cmd = 'kill @e[type=item'
    if mode == 'whitelist':
        lines = ConfigList[1]["Whitelist"]
    elif mode == 'blacklist':
        lines = ConfigList[2]["Blacklist"]
    for i in range(len(lines)):
        name = lines[i].replace('\n', '').replace('\r', '')
        cmd = cmd + get_nbt(name, mode)
    cmd = cmd + ']'
    server.execute(cmd)
    item_counter = True

#MCDR-帮助信息
def on_load(server ,old):
    server.add_help_message('!!ac','定时清理器')
    if not os.path.isfile(ConfigFilePath):
        server.logger.info('[AutoC/WARN] 未找到配置文件，已自动生成')
        with open(ConfigFilePath, 'w+') as f:
            f.write('[{"mode": "whitelist"}, {"Whitelist": []}, {"Blacklist": []}]')
            f.close()
        load_config()
    else:
        load_config()
    
    
#插件退出
def on_unload(server):
    global stop
    stop = False

    
#死亡检测
def on_death_message(server, death_message):
    global stop
    death_split = death_message.split(' ')
    server.say('R.I.P ' + death_split[0])
    if stop:
        stop = False
        server.say('§7[§9AutoC§r/§bINFO§7] §a' + death_split[0] + '§e死亡,扫地机停止运行')
               
    
def on_info(server ,info):
    global item_counter
    global maxtime
    global time_counter
    content = info.content
    command = content.split(' ')
    
    #清理物品总数统计
    if item_counter == True:
        if content.find('Killed ') != -1 and content.find(' entities'):
            server.say('§7[§9AutoC§r/§bINFO§7] §b清理了 §e{} §b物品'.format(command[1]))
            item_counter = False
            return
        elif content.find('No entity was found') != -1:
            server.say('§7[§9AutoC§r/§bINFO§7] §b清理了 §e0 §b物品')
            item_counter = False
        elif content.find('Killed ') != -1:
            server.say('§7[§9AutoC§r/§bINFO§7] §b清理了 §e1 §b物品')
            item_counter = False
        
        
    if len(command) == 0 or command[0] != Prefix:
        return
    del command[0]
    
    #检测是否为玩家或者控制台输入
    if not info.is_user:
        return
    
    #命令提示
    if len(command) == 0:
        help_message(server ,info)
        
    #开机
    elif len(command) in [1,2] and command[0] == 'start':
        if stop:
            server.reply(info,'§7[§9AutoC§r/§cERROR§7] §c扫地机已在运行，请勿重复开启')
            return
        elif len(command) == 2:
            if command[1].isdigit() == True:
                if int(command[1]) >= 45 and int(command[1]) <= 600:
                    maxtime = command[1]
                    ac_start(server ,info)
                else:
                    server.reply(info,'§7[§9AutoC§r/§cERROR§7] §c请输入在 §l§e45-600 §r§c之间的整数')
                    return
            else:
                server.reply(info,'§7[§9AutoC§r/§cERROR§7] §c请输入在 §l§e45-600 §r§c之间的整数')
                return
        else:
            maxtime = command[1] if len(command) == 2 else '60'
            ac_start(server ,info)
            
    #停机
    elif len(command) == 1 and command[0] == 'stop':
        ac_stop(server ,info)
        
    #状态检测
    elif len(command) == 1 and command[0] == 'status':
        server.reply(info,'§7--------§bMCD AutoCleaner Status§7--------')
        server.reply(info,'§b扫地机状态：§e{}'.format(stop))
        server.reply(info,'§b模式: §e{}'.format(ConfigList[0]["mode"]))
        if stop:
            server.reply(info,'§b清扫间隔：§e{} s'.format(maxtime))
            server.reply(info,'§b离下次清扫还剩: §e{} s'.format(int(maxtime) - time_counter))
            
    #直接清理所有物品
    elif len(command) == 1 and command[0] == 'killall':
        kill_item(server)
        
    #白名单相关
    elif len(command) == 1 and command[0] == 'list':
        Whitelist = ConfigList[1]["Whitelist"]
        server.reply(info,'§7--------§bMCD AutoCleaner Whitelist§7--------')
        for i in range(len(Whitelist)):
            name = Whitelist[i].replace('\n', '').replace('\r', '')
            server.reply(info,'§e' + name)
        Blacklist = ConfigList[2]["Blacklist"]
        server.reply(info,'§7--------§bMCD AutoCleaner Blacklist§7--------')
        for i in range(len(Blacklist)):
            name = Blacklist[i].replace('\n', '').replace('\r', '')
            server.reply(info,'§e' + name)

    elif len(command) == 2 and command[0] == 'mode':
        if command[1] == 'whitelist' or command[1] == 'blacklist':
            mode_change(command[1])
            server.reply(info, 'Successful')
        else:
            server.reply(info, 'Unknown Mode')
    elif len(command) == 3 and command [0] == 'whitelist':
        write_config('whitelist', command[1], command[2], server, info)
    elif len(command) == 3 and command [0] == 'blacklist':
        write_config('blacklist', command[1], command[2], server, info)
    elif command[0] == 'test':
        server.reply(info, ConfigList)
    else:
        server.reply(info,'§7[§9AutoC§r/§cERROR§7] §c参数错误，请输入 §7§l' + Prefix + ' §r§c查看具体命令')