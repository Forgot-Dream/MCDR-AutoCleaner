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
§7''' + Prefix + ''' whilelist add <物品> §r添加<物品>进入白名单
§7''' + Prefix + ''' whilelist remove <物品> §r从白名单中删除<物品>
§7''' + Prefix + ''' whilelist list §r显示白名单中已有的物品'''

#帮助信息
def help_message(server ,info):
    server.tell(info.player,HelpMessage)
    
#MCDR-帮助信息
def on_load(server ,old):
    server.add_help_message('!!ac','定时清理器')
    if not os.path.isfile(ConfigFilePath):
        with open(ConfigFilePath, 'w+') as f:
            f.write('[{"item_name": []}]')
            f.close()
    
    
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
        if command[1].isdigit() == True:
            server.say('§7[§9AutoC§r/§bINFO§7] §b清理了 §e{} §b物品'.format(command[1]))
            item_counter = False
            return
        elif content.find('No entity was found') != -1:
            server.say('§7[§9AutoC§r/§bINFO§7] §b清理了 §e0 §b物品')
        elif content.find('No entity was found') == -1:
            server.say('§7[§9AutoC§r/§bINFO§7] §b清理了 §e1 §b物品')
        item_counter = False
        
        
    if not info.is_player and content.endswith('<--[HERE]'):
	    content = content.replace('<--[HERE]', '')
                
    if len(command) == 0 or command[0] != Prefix:
        return
    del command[0]
    
    #命令提示
    if len(command) == 0:
        help_message(server ,info)
        
    #开机
    elif len(command) in [1,2] and command[0] == 'start':
        if stop:
            server.tell(info.player,'§7[§9AutoC§r/§cERROR§7] §c扫地机已在运行，请勿重复开启')
            return
        elif len(command) == 2:
            if command[1].isdigit() == True:
                if int(command[1]) >= 45 and int(command[1]) <= 600:
                    maxtime = command[1]
                    ac_start(server ,info)
                else:
                    server.tell(info.player,'§7[§9AutoC§r/§cERROR§7] §c请输入在 §l§e45-600 §r§c之间的整数')
                    return
            else:
                server.tell(info.player,'§7[§9AutoC§r/§cERROR§7] §c请输入在 §l§e45-600 §r§c之间的整数')
                return
        else:
            maxtime = command[1] if len(command) == 2 else '60'
            ac_start(server ,info)
            
    #停机
    elif len(command) == 1 and command[0] == 'stop':
        ac_stop(server ,info)
        
    #状态检测
    elif len(command) == 1 and command[0] == 'status':
        server.tell(info.player ,'§7--------§bMCD AutoCleaner Status§7--------')
        server.tell(info.player ,'§b扫地机状态：§e{}'.format(stop))
        if stop:
            server.tell(info.player ,'§b清扫间隔：§e{} s'.format(maxtime))
            server.tell(info.player ,'§b离下次清扫还剩: §e{} s'.format(int(maxtime) - time_counter))
            
    #直接清理所有物品
    elif len(command) == 1 and command[0] == 'killall':
        kill_item(server)
        
    #白名单相关
    elif len(command) in [2,3] and command[0] == 'whitelist':
        if command[1] == 'list':
            with open(ConfigFilePath, 'r') as f:
                js = json.load(f)
                lines = js[0]["item_name"]
                server.tell(info.player ,'§7--------§bMCD AutoCleaner Whitelist§7--------')
                for i in range(len(lines)):
                    name = lines[i].replace('\n', '').replace('\r', '')
                    server.tell(info.player,'§e' + name)
        elif command [1] == 'add' and len(command) == 3:
            api = server.get_plugin_instance('MinecraftItemAPI') #从MinecraftItemAPI获取物品信息
            if api.getMinecraftItemInfo(command[2]):
                with open(ConfigFilePath, 'r') as f:
                    js = json.load(f)
                    js_list = js[0]['item_name']
                    if not command[2] in js_list:
                        js_list.append(command[2])
                        js_new = []
                        temp = {}
                        temp['item_name'] = js_list
                        js_new.append(temp)
                        f.close()
                    else:
                        server.tell(info.player,'§7[§9AutoC§r/§cERROR§7] §e' + command[2] + ' §c已存在于白名单')
                        f.close()
                        return
                with open(ConfigFilePath, 'w') as f:
                    f.write(json.dumps(js_new,ensure_ascii=False))
                    f.close
                server.tell(info.player,'§7[§9AutoC§r/§bINFO§7] §e' + command[2] + ' §b已添加')
            else:
                server.tell(info.player,'§7[§9AutoC§r/§cERROR§7] §e' + command[2] + ' §c非正确的MC物品ID')
        elif command [1] == 'remove' and len(command) == 3:
            with open(ConfigFilePath, 'r') as f:
                js = json.load(f)
                js_list = js[0]['item_name']
                if command[2] in js_list:
                    js_list.remove(command[2])
                    js_new = []
                    temp = {}
                    temp['item_name'] = js_list
                    js_new.append(temp)
                    f.close()
                else:
                    server.tell(info.player,'§7[§9AutoC§r/§cERROR§7] §c未在白名单文件中找到 §e' + command[2])
                    f.close()
                    return
            with open(ConfigFilePath, 'w') as f:
                f.write(json.dumps(js_new,ensure_ascii=False))
                f.close
            server.tell(info.player,'§7[§9AutoC§r/§bINFO§7] §e' + command[2] + ' §b已从白名单中删除')
        else:
            server.tell(info.player,'§7[§9AutoC§r/§cERROR§7] §c参数错误，请输入 §7§l' + Prefix + ' §r§c查看具体命令')
    else:
        server.tell(info.player,'§7[§9AutoC§r/§cERROR§7] §c参数错误，请输入 §7§l' + Prefix + ' §r§c查看具体命令')
    
    #停机
def ac_stop(server ,info):
    global stop
    global time_counter
    if stop:
        stop = False
        server.say('§7[§9AutoC§r/§bINFO§7] §b扫地机停止运行')
        time_counter = None
    else:
        server.tell(info.player,'§7[§9AutoC§r/§cERROR§7] §b扫地机未开启')

    #NBT格式写入
def get_exception(name):
    return ',nbt=!{Item:{id:"minecraft:' + name + '"}}'
    
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
    cmd = 'kill @e[type=item'
    with open(ConfigFilePath, 'r') as f:
        js = json.load(f)
        lines = js[0]['item_name']
        
        for i in range(len(lines)):
            name = lines[i].replace('\n', '').replace('\r', '')
            cmd = cmd + get_exception(name)
    cmd = cmd + ']'
    server.execute(cmd)
    item_counter = True