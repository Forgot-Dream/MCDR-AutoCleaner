# MCDR-AutoCleaner

一个适用于 [MCDReforged](https://github.com/Fallen-Breath/MCDReforged)(version >= 0.7.0)  的自动扫地机插件.

需要 [MinecraftItemAPI](https://github.com/Forgot-Dream/MinecraftItemAPI) 作为前置.

## Feature / 特性

1. 死亡自动停机 / Automatic shutdown of death.
2. 避免白名单内物品被删除 / Avoid deleting items in the whitelist.
3. 可自定义的时长 / Customizable duration.
4. 添加白名单时，会自动判断是否为MC的物品id，避免小天才 / When adding a white list, it will automatically determine whether it is the item id of MC, to avoid genius.

## Usage / 使用方法

1. 复制`AutoCleaner.py`到`/plugins` | copy `AutoCleaner.py` to `/plugins`
2. 重载MCDR | Reload MCDR

## Command / 命令

`!!ac` 查看命令

`!!ac start <time>` 以 <time>(可取45-600) 秒间隔清理物品
  
`!!ac killall` 立即清理所有物品

`!!ac stop` 停止运行

`!!ac status` 显示扫地机状态

`!!ac whitelist add <item>` 加<item>到白名单

`!!ac whitelist remove <item>` 移除白名单中<item>
  
`!!ac whitelist list` 列出白名单内物品

## 接下来还要做什么

1. 添加黑名单模式，并且支持切换
2. Lazy

## Log

2020-7-19 更新白名单模式 命令提示尚未更新
