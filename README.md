# fanbook-bot-message  
fanbook bot消息平台  

fanbook bot消息平台是为了解决普通fanbook服务器无法使用消息推送功能而诞生，我写代码是业余水平，尤其是前端，也不想写多复杂，写的烂是正常现象，能用就行  

**本项目需要有发送消息白名单机器人，由于目前申请该项几乎不可能，建议没有白名单的服务器主使用现成的**  
现成的：https://124.221.67.43/botmsg1/  
使用现成的请先前往服务器取得机器人：https://in.fanbook.cn/LmgLJF3N  

## 部署  
### Linux

> Linux下使用1panel演示  

如果你只需要使用自己的机器人发送消息，只需要前往发布页面找到web.zip下载下来解压放网站目录里面(套二级目录请修改index.html)  
如果需要定制代码，改完代码以后就先在电脑上按照平时的方法运行build即可，然后取得静态文件  

**确保网站根目录下有config.json，请先修改这个**
config.json：
```json
{"server":"后端地址"}
```  

源码下载下来，找到server文件夹，扔服务器上  
然后新建一个python运行环境  
![image](https://github.com/user-attachments/assets/2164f41e-93b4-445a-b562-c3c640bf17ec)  
启动命令：`pip install -r requirements.txt && python msgapi.py`  
后端完成：  
![PixPin_2024-12-30_00-59-41](https://github.com/user-attachments/assets/cc9f5eae-4b7f-43c0-bbfc-d0913e18600a)  

后端没问题了就去修改server目录下的token.json，把里面的token的值改为你机器人的token，然后重启后端程序  
然后确定config.json是后端地址即可  

### Windows

下载bot python框架：https://124.221.67.43/fbBot.zip  

**将server里面的东西复制到框架根目录下面**  

后端完成：
![image](https://github.com/user-attachments/assets/b411f701-82ad-47d1-b3bb-2f3301e8c4f9)  

按照linux的方法扔前端目录、改文件即可
