import logging
import coloredlogs
# 创建日志记录器
logger = logging.getLogger(__name__)
# 配置 coloredlogs
coloredlogs.install(level='DEBUG', logger=logger)
logger.info("开始加载库")
import flask
import requests
import json
# import sqlite3
import fanbookbotapi
import base64
import time
import uuid
import warnings
import threading
import sentry_sdk
import ctypes
import re


logger.info("加载完成，开始初始化")

sentry_sdk.init(
    dsn="https://3b5e73e391e4f7944b83ca665c1f1a10@o4507525750521856.ingest.us.sentry.io/4508342943940608",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    _experiments={
        # Set continuous_profiling_auto_start to True
        # to automatically start the profiler on when
        # possible.
        "continuous_profiling_auto_start": True,
    },
)

try:
    # 获取控制台窗口句柄
    kernel32 = ctypes.windll.kernel32
    hwnd = kernel32.GetConsoleWindow()

    # 设置窗口标题
    if hwnd != 0:
        kernel32.SetConsoleTitleW("消息平台api")
except:
    pass

# 禁止警告输出
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

bottoken=''

# 创建一个数据库用于存储激活码，包含激活码名称、是否已使用和自增id
# conn = sqlite3.connect('codedata.db')
# c = conn.cursor()
# c.execute('''CREATE TABLE IF NOT EXISTS codes
#              (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, used INTEGER)''')
# conn.commit()


app = flask.Flask(__name__)

@app.after_request
def cors(environ):
    environ.headers['Access-Control-Allow-Origin']='*'
    environ.headers['Access-Control-Allow-Method']='*'
    environ.headers['Access-Control-Allow-Headers']='*'
    return environ

roks=[]
errs=[]
texttypes=[]
ids=[]

def Wjson(filename,data):
    with open(filename,'w',encoding='utf-8') as f:
        json.dump(data,f,indent=4,ensure_ascii=False)
    return 0

def Rjson(filename):
    with open(filename,'r',encoding='utf-8') as f:
        data=json.load(f)
    return data

def is_valid_filename(name):
    if len(name) != 36:
        return False
    return re.fullmatch(r'[\w\-]+', name) is not None

def process_markdown(text):
    # 正则表达式匹配 Markdown 格式的图片
    pattern = r'!\[.*?\]\((.*?)\)'
    
    # 找到所有匹配的图片链接
    matches = re.finditer(pattern, text)
    image_links = [match.group(1) for match in matches]
    
    # 使用正则表达式删除图片
    modified_text = re.sub(pattern, '', text)
    
    # 根据删除后的图片位置分割文本
    split_text = re.split(pattern, text)
    
    # 删除分割后的图片链接
    for i in range(len(split_text)):
        if split_text[i] in image_links:
            split_text[i]='[图片]'
    
    return image_links, modified_text, split_text

# 验证颜色是否符合要求
def is_valid_color(color):
    # 检查颜色是否为6位十六进制数
    if re.fullmatch(r'#[0-9a-fA-F]{6}', color):
        return True
    else:
        return False

bottoken=Rjson('token.json')['token']

def get_members(token='',tabs=[{"start":0, "end":99}],guid='',chlid='',userid='',name=''):#获取成员列表
    url=f'https://a1.fanbook.mobi/api/bot/{token}/v2/guild/members'
    headers={'Content-Type': 'application/json'}
    body={
    "guild_id":guid,
    "channel_id":chlid,
    "user_id":userid,
    "ranges":tabs
}
    body=json.dumps(body)
    r=requests.post(url,headers=headers,data=body,verify=False)
    return json.loads(r.text)

def sendMessage(token='',chlid='',text='',sl=0,yz=0,name=''):
    # global roks,errs,texttypes,ids
    rok=roks[ids.index(name)]
    err=errs[ids.index(name)]
    texttype=texttypes[ids.index(name)]
    url=f'https://a1.fanbook.mobi/api/bot/{token}/getPrivateChat'#获取私聊频道
    headers={'Content-Type': 'application/json'}
    #print(chlid)
    body=json.dumps({"user_id":int(chlid)})
    r=requests.post(url,headers=headers,data=body,verify=False)
    da=json.loads(r.text)
    #print(da)
    if yz==1:
        if da["ok"]==True:
            pass
        else:
            logger.error(f'发送第{str(sl+1)}条消息失败，获取私信频道失败')
            logger.error(f'错误信息：{da}')
            errs[ids.index(name)]+=1
            return da
    chlid=da["result"]["id"]
    try:
        r=fanbookbotapi.sendmessage(token=token,chatid=int(chlid),type=texttype,text=text)
        da=json.loads(r.text)
        if da["ok"]==True:
            logger.info(f'发送第{str(sl+1)}条消息成功')
            roks[ids.index(name)]+=1
        else:
            logger.error(f'发送第{str(sl+1)}条消息失败 {da}')
            errs[ids.index(name)]+=1
        return json.loads(r.text)
    except:
        errs[ids.index(name)]+=1

def get_guild(token='',guid='',userid=''):#获取服务器信息
    url=f'https://a1.fanbook.mobi/api/bot/{token}/guild'
    headers={'Content-Type': 'application/json'}
    body={
    "guild_id":guid,
    "user_id":userid,}
    
    body=json.dumps(body)
    r=requests.post(url,headers=headers,data=body,verify=False)
    return json.loads(r.text)



def SendMessageForAllUser(clid='',gid='',token='',text='',sl=0,yz=0,name='',Ttime=''):
    # global roks,errs,texttypes,ids
    err=errs[ids.index(name)]
    texttype=texttypes[ids.index(name)]
    
    chlid=str(clid)
    gid=str(gid)
    botid='1'

    # qx=sendMessage(token=token,chlid=chlid,text='1')

    notend=True
    userids=[]
    tabsdata=0

    try:
        if True:# if qx["ok"]==true or qx["ok"]==True:
            logger.info('验证成功，机器人有权限发送消息')
            roks[ids.index(name)]-=1
            try:
                try:
                    while notend:
                        cylb=get_members(token=token,guid=gid,userid=botid,chlid=chlid,tabs=[{"start":tabsdata, "end":tabsdata+99}],name=name)
                        rangesdata=cylb['result']["ops"][0]
                        #rangesdata=json.loads(rangesdata[0])
                        rangesdata=rangesdata['items']
                        #print(rangesdata)
                        for x in rangesdata:
                            datatype=x.keys()
                            datatype=list(datatype)
                            if datatype[0]=='User':
                                userids.append(x['User']['user_id'])
                        logger.info(f'获取成员列表成功，已获取{str(len(userids))}个成员')
                        Wjson(filename=name+'.json',data={"usernum":len(userids),"sendnum":sl,"errnum":errs[ids.index(name)],"oknum":roks[ids.index(name)],"msg":"正在获取成员列表","time":Ttime,"time_remaining":str(len(userids)*0.25)})
                        if len(rangesdata)<99:
                            logger.info(f'获取成员列表完成，共获取{str(len(userids))}个成员')
                            notend=False
                            Wjson(filename=name+'.json',data={"usernum":len(userids),"sendnum":sl,"errnum":errs[ids.index(name)],"oknum":roks[ids.index(name)],"msg":"获取完成，即将发送消息","time":Ttime,"time_remaining":str(len(userids)*0.25)})
                            #print(userids)
                        tabsdata+=99
                    for x in userids:
                        #print(x)
                        sendMessage(token=token,chlid=x,text=text,sl=sl,name=name)
                        sl+=1
                        Wjson(filename=name+'.json',data={"usernum":len(userids),"sendnum":sl,"errnum":errs[ids.index(name)],"oknum":roks[ids.index(name)]+1,"msg":"正在发送消息","time":Ttime,"time_remaining":str((len(userids)-sl)*0.25)})
                        
                    time.sleep(1)
                    logger.info(f'发送完成，成功{str(roks[ids.index(name)]+1)}次，失败{str(errs[ids.index(name)])}次')
                    Wjson(filename=name+'.json',data={"usernum":len(userids),"sendnum":sl,"errnum":errs[ids.index(name)],"oknum":roks[ids.index(name)]+1,"msg":"发送完成","time":Ttime,"endtime":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"time_remaining":'0'})
                except:
                    logger.error('获取成员数量失败，你应该检查机器人id和频道id')
                    print(cylb)
            except:
                logger.error('获取成员数量失败，你应该检查服务器id')
        else:
            logger.error('机器人没有权限发送消息或没有发送消息白名单')
    except:
        logger.error('token不正确')

# SendMessageForAllUser(clid=433212507046281216,gid='433204455396081664',token='0f2de7ac66727cd9fcec1ee43559c561f6abf3f1e202c5a06c2ae4a3f6cf94ab795fbfbe39ad311a18ad1ff314388d1c',text='text',name=str(uuid.uuid1()))

def get_err_msg(code):
    if code == 1021:
        return '频道不存在'
    if code == 1012:
        return '机器人没有权限'
    if code == 1001:
        return '参数错误'
    if code == 5104:
        return '消息长度超过限制'
    else:
        return '未知错误：'+str(code)

@app.route('/sendmessage', methods=['GET'])
def send_message():
    # 获取请求参数
    cid = flask.request.args.get('cid')# 频道id
    openimg=flask.request.args.get('openimg')# 是否开启图片
    openbutton=flask.request.args.get('openbutton')# 是否开启按钮
    color=[flask.request.args.get('color1'),flask.request.args.get('color2')]# 卡片颜色
    bt=flask.request.args.get('bt')# 卡片标题
    textcolor=flask.request.args.get('textcolor')# 卡片标题文本颜色
    img=flask.request.args.get('img')# 卡片图片
    # base64编码图片链接
    img = base64.b64encode(img.encode('utf-8')).decode('utf-8')
    
    mdtext=flask.request.args.get('mdtext')# 卡片文本
    btcolor=flask.request.args.get('btcolor')# 按钮颜色
    botton=flask.request.args.get('button')# 按钮文本
    burl=flask.request.args.get('burl')# 按钮链接
    gid=flask.request.args.get('gid')# 服务器id
    ttype=flask.request.args.get('type')# 是否推送到频道的所有用户
    
    key=flask.request.args.get('key')
    
    # getjson参数是不发送请求,用于在前端中获取构建好的卡片数据
    getjson=flask.request.args.get('getjson')

    taskid=str(uuid.uuid1())
    Ttime=time.time()
    
    # 验证颜色是否符合要求
    if not is_valid_color(color[0]):
        # 默认颜色
        color[0] = "#00AFEE"
    if not is_valid_color(color[1]):
        # 默认颜色
        color[1] = "#F2F2F2"
    if not is_valid_color(textcolor):
        # 默认颜色
        textcolor = "#F2F2F2"
    if not is_valid_color(btcolor):
        # 默认颜色
        btcolor = "#00AFEE"
    
    # 格式化时间
    Ttime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(Ttime))
    if getjson!='true':
        is_black=Rjson('data.json')
        is_black=is_black['black_list']
        if gid in is_black:
            logger.error(f'服务器{gid}因违规已被拉黑')
            return {'ok':False,'msg':'该服务器因为违规已被拉黑'}
        
        keys=Rjson('data.json')
        keys=keys['keys']
        # print(key)
        key.replace(" ","")
        gid.replace(" ","")
        # print(gid,']')
        logger.info(f'服务器{gid}发送卡片消息到频道{cid}，密钥为{key}')
        try:
            if keys[gid]!=key:
                logger.error(f'服务器{gid}密钥错误')
                return {'ok':False,'msg':'服务器安全密钥错误'}
        except:
            logger.error(f'服务器{gid}没有密钥')
            return {'ok':False,'msg':'为了安全性，请点击下方加入服务器按钮，以获取密钥'}
    
    image_links, modified_text, split_text = process_markdown(mdtext)
    
    imgindex=0
    
    data={
        "crossAxisAlignment": "stretch",
        "tag": "column",
        "children": [
            {
                "tag": "container",
                "padding": "12,7",
                "gradient": {
                    "colors": color
                },
                "child": {
                    "tag": "text",
                    "data": bt,
                    "style": {
                        "color": textcolor,
                        "fontSize": 16,
                        "fontWeight": "medium"
                    }
                },
                "backgroundColor": "ddeeff00"
            }
        ],
    }
    for i in split_text:
        if i=='[图片]':
            img=image_links[imgindex]
            imgindex+=1
            # base64编码图片链接
            img = base64.b64encode(img.encode('utf-8')).decode('utf-8')
            data['children'].append({
                "tag": "container",
                "child": {
                    "tag": "column",
                    "padding": "12",
                    "children": [
                        {
                            "tag": "container",
                            "padding": "12",
                            "child": {
                                "tag": "image",
                                "src":  "1::00::0::"+img,
                            }
                        }
                    ]
                },
                "backgroundColor": "ffffff"
            })
        else:
            data['children'].append({
                    "tag": "container",
                    "child": {
                        "tag": "column",
                        "crossAxisAlignment": "start",
                        "padding": "12",
                        "children": [
                            {
                                "tag": "container",
                                "padding": "0,8,0,0",
                                "child": {
                                    "tag": "markdown",
                                    "data": i
                                }
                            }
                        ]
                    },
                    "backgroundColor": "ffffff"
                })
    if openbutton=='true':
        data['children'].append({"tag":"container","padding":"12,0,12,12","child":{"tag":"button","category":"outlined","color":btcolor,"size":"medium","widthUnlimited":True,"href":burl,"label":botton}})
    if getjson=='true':
        return data
    if ttype=='true':
        # 创建线程
        ginfo=get_guild(token=bottoken,guid=str(gid),userid='1')
        gname=ginfo['result']['name']
        white_list=Rjson('data.json')
        white_list=white_list['white_list']
        logger.info(f'服务器{gid}({gname})批量发送卡片消息到{cid}')
        if gid not in white_list:
            text1="来自:"+gname+",不是由官方发送,请注意辨别"
        else:
            text1="来自:"+gname+",为可信服务器的消息"
        text=json.dumps({'width': None, 'height': None, 'data':json.dumps(data) , 'notification': None, 'come_from_icon': None, 'come_from_name': text1, 'template': None, 'no_seat_toast': None, 'type': 'messageCard'})
        t = threading.Thread(target=SendMessageForAllUser, args=(int(cid),gid,bottoken,text,0,0,taskid,Ttime))
        ids.append(taskid)
        roks.append(0)
        errs.append(0)
        texttypes.append('text')
        # 启动线程
        t.start()
        return {'ok':True,'taskid':taskid}
    else:
        logger.info(f'服务器{gid}发送卡片消息到{cid}')
        r=fanbookbotapi.sendmessage(token=bottoken,chatid=cid,type='fanbook',text=json.dumps({'width': None, 'height': None, 'data':json.dumps(data) , 'notification': None, 'come_from_icon': None, 'come_from_name': None, 'template': None, 'no_seat_toast': None, 'type': 'messageCard'})).text
        data=json.loads(r)
        if data['ok']==True:
            return data
        else:
            logger.warning(f'服务器{gid}发送卡片消息到{cid}失败，错误码{data["error_code"]}')
            try:
                data['msg']=get_err_msg(data['error_code'])
            except:
                data['msg']='未知错误'
            return data
    
@app.route('/sendtext', methods=['get'])
def sendtext():
    # global ids,roks,errs,texttypes
    cid = flask.request.args.get('cid')
    text = flask.request.args.get('text')
    ttype=flask.request.args.get('type')
    gid=flask.request.args.get('gid')
    key=flask.request.args.get('key')
    taskid=str(uuid.uuid1())
    Ttime=time.time()
    # 格式化时间
    Ttime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(Ttime))
    is_black=Rjson('data.json')
    is_black=is_black['black_list']
    if gid in is_black:
        logger.info(f'服务器{gid}发送消息到频道{cid}，但该服务器因为违规已被拉黑')
        return {'ok':False,'msg':'该服务器因为违规已被拉黑'}
    
    keys=Rjson('data.json')
    keys=keys['keys']
    key.replace(" ","")
    gid.replace(" ","")
    # print(gid,']')
    logger.info(f'服务器{gid}发送消息到频道{cid}，密钥为{key}')
    try:
        if keys[gid]!=key:
            logger.info(f'服务器{gid}发送消息到频道{cid}，但密钥错误')
            return {'ok':False,'msg':'服务器安全密钥错误'}
    except:
        logger.info(f'服务器{gid}发送消息到频道{cid}，无密钥')
        return {'ok':False,'msg':'为了安全性，请点击下方加入服务器按钮，以获取密钥'}
    
    if ttype=='true':
        # SendMessageForAllUser(clid=int(cid),gid=gid,token=bottoken,text='text',name=taskid)
        # 创建线程
        ginfo=get_guild(token=bottoken,guid=str(gid),userid='1')
        gname=ginfo['result']['name']
        white_list=Rjson('data.json')
        white_list=white_list['white_list']
        logger.info(f'服务器{gid}({gname})发送批量消息到{cid}')
        if gid not in white_list:
            text+="\n\n消息来自："+gname+"\n不是由官方发送，请注意辨别"
        else:
            text+="\n\n消息来自："+gname+"\n为可信服务器的消息"
        t = threading.Thread(target=SendMessageForAllUser, args=(int(cid),gid,bottoken,text,0,0,taskid,Ttime))
        ids.append(taskid)
        roks.append(0)
        errs.append(0)
        texttypes.append('text')
        # 启动线程
        t.start()
        return {'ok':True,'taskid':taskid}
    else:
        logger.info(f'服务器{gid}发送消息到频道{cid}')
        r=fanbookbotapi.sendmessage(token=bottoken,chatid=cid,type='text',text=text).text
        data=json.loads(r)
        if data['ok']==True:
            return data
        else:
            logger.warning(f'服务器{gid}发送消息到频道{cid}失败，错误码{data["error_code"]}')
            try:
                data['msg']=get_err_msg(data['error_code'])
            except:
                data['msg']='未知错误'
            return data

@app.route('/sendRichText', methods=['get'])
def sendRichText():
    # global ids,roks,errs,texttypes
    cid = flask.request.args.get('cid')
    text = flask.request.args.get('text')
    ttype=flask.request.args.get('type')
    gid=flask.request.args.get('gid')
    key=flask.request.args.get('key')
    bt= flask.request.args.get('bt')
    taskid=str(uuid.uuid1())
    Ttime=time.time()
    # 格式化时间
    Ttime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(Ttime))
    is_black=Rjson('data.json')
    is_black=is_black['black_list']
    if gid in is_black:
        logger.info(f'服务器{gid}发送消息到频道{cid}，但该服务器因为违规已被拉黑')
        return {'ok':False,'msg':'该服务器因为违规已被拉黑'}
    
    keys=Rjson('data.json')
    keys=keys['keys']
    key.replace(" ","")
    gid.replace(" ","")
    print(gid,']')
    try:
        if keys[gid]!=key:
            logger.info(f'服务器{gid}发送消息到频道{cid}，但密钥错误')
            return {'ok':False,'msg':'服务器安全密钥错误'}
    except:
        logger.info(f'服务器{gid}发送消息到频道{cid}，无密钥')
        return {'ok':False,'msg':'为了安全性，请点击下方加入服务器按钮，以获取密钥'}
    
    if ttype=='true':
        # SendMessageForAllUser(clid=int(cid),gid=gid,token=bottoken,text='text',name=taskid)
        # 创建线程
        ginfo=get_guild(token=bottoken,guid=str(gid),userid='1')
        gname=ginfo['result']['name']
        white_list=Rjson('data.json')
        white_list=white_list['white_list']
        logger.info(f'服务器{gid}({gname})发送批量富文本消息到{cid}')
        delta=json.loads(text)
        if gid not in white_list:
            delta.append({
    "insert": "\n"
  })
            delta.append({
    "attributes": {
      "color": "#00afee"
    },
    "insert": "消息来自："+gname+"\n"
  })        
            delta.append({
    "attributes": {
      "color": "#00afee"
    },
    "insert": "不是由官方发送，请注意辨别"
  })
            delta.append({
    "insert": "\n"
  })
        else:
            delta.append({
    "insert": "\n"
  })
            delta.append({
    "attributes": {
      "color": "#00afee"
    },
    "insert": "消息来自："+gname+"\n"
  })
            delta.append({
    "attributes": {
      "color": "#00afee"
    },
    "insert": "为可信服务器的消息"
  })
            delta.append({
    "insert": "\n"
  })
        # 遍历delta中的每个元素，检查是否有图片，如果insert中有image，将image字段名改为source
        for i in delta:
            if 'insert' in i and isinstance(i['insert'], dict) and 'image' in i['insert']:
                i['insert']['source'] = i['insert'].pop('image')
                i['insert']["_type"]= 'image'
                # i["width"]= 279.0
                # i["height"]= 130.0
                i['insert']["_inline"]= False
        # print(delta)
        logger.debug(f'富文本json：{delta}')
        # 目前有一个bug，图片在pc端上非常小，web端上非常大，目前不清楚原因
        msg={
            "type": "richText",
            "title": bt,
            # "document": json.dumps(delta),# 这个是富文本去掉所有样式的数组，但是直接传普通的富文本似乎也可以
            "v2":json.dumps(delta),# 这个是富文本的Quill v2版本，包含所有样式，不传这个只传上面的document会导致富文本样式丢失
            "v":2# 这个是富文本的版本号，必须为2
        }
        t = threading.Thread(target=SendMessageForAllUser, args=(int(cid),gid,bottoken,json.dumps(msg),0,0,taskid,Ttime))
        ids.append(taskid)
        roks.append(0)
        errs.append(0)
        texttypes.append('text')
        # 启动线程
        t.start()
        return {'ok':True,'taskid':taskid}
    else:
        logger.info(f'服务器{gid}发送富文本消息到频道{cid}')
        delta=json.loads(text)
        # 遍历delta中的每个元素，检查是否有图片，如果insert中有image，将image字段名改为source
        for i in delta:
            if 'insert' in i and isinstance(i['insert'], dict) and 'image' in i['insert']:
                i['insert']['source'] = i['insert'].pop('image')
                i['insert']["_type"]= 'image'
                # i["width"]= 279.0
                # i["height"]= 130.0
                i['insert']["_inline"]= False
        # print(delta)
        logger.debug(f'富文本json：{delta}')
        # 目前有一个bug，图片在pc端上非常小，web端上非常大，目前不清楚原因
        msg={
            "type": "richText",
            "title": bt,
            # "document": json.dumps(delta),# 这个是富文本去掉所有样式的数组，但是直接传普通的富文本似乎也可以
            "v2":json.dumps(delta),# 这个是富文本的Quill v2版本，包含所有样式，不传这个只传上面的document会导致富文本样式丢失
            "v":2# 这个是富文本的版本号，必须为2
        }
        r=fanbookbotapi.sendmessage(token=bottoken,chatid=cid,type='fanbook',text=json.dumps(msg)).text
        data=json.loads(r)
        if data['ok']==True:
            return data
        else:
            logger.warning(f'服务器{gid}发送消息到频道{cid}失败，错误码{data["error_code"]}')
            try:
                data['msg']=get_err_msg(data['error_code'])
            except:
                data['msg']='未知错误'
            return data
    
@app.route('/getTask', methods=['get'])
def getTask():
    try:
        name=flask.request.args.get('pid')
        # 验证任务ID是否合法，防止路径遍历攻击，并且满足：只符合uuid4长度、不允许含有data、token
        if not is_valid_filename(name):
            return {'ok': False, 'msg': '非法的任务ID'}
        d=Rjson(name+'.json')
        logger.info(f'获取任务{name}成功')
        return d
    except:
        logger.info(f'获取任务{flask.request.args.get("pid")}失败')
        return {'ok':False,'msg':'任务不存在'}
    
@app.route('/get', methods=['GET'])
def get():
    gid = flask.request.args.get('gid')
    url=f'https://a1.fanbook.cn/api/bot/{bottoken}/channel/list'
    headers={'Content-Type': 'application/json'}
    body=json.dumps({'guild_id':gid})
    response = requests.post(url, headers=headers, data=body)
    pd=[]
    d=json.loads(response.text)
    if d['ok']==True:
        for i in d['result']:
            if i['type']==0:
                pd.append({'label':i['name'],'value':i['channel_id']})
        logger.info(f'服务器{gid}获取频道列表成功')
        return {'ok':True,'data':pd}
    logger.info(f'服务器{gid}获取频道列表失败')
    return {'ok':False,'data':[]}
    
@app.route('/info', methods=['GET'])
def info():
    """获取服务器基本信息，输入服务器id，返回服务器名称、是否为白名单、是否为黑名单、是否为免费使用
    """
    gid = flask.request.args.get('gid')
    try:
        list=Rjson('data.json')
        white_list=list['white_list']
        black_list=list['black_list']
        free_list=list['free_list']
        if gid in white_list:
            white=True
        else:
            white=False
        if gid in black_list:
            black=True
        else:
            black=False
        if free_list[0]=='ALL':
            free=True
        elif gid in free_list:
            free=True
        else:
            free=False
        url=f'https://a1.fanbook.cn/api/bot/{bottoken}/guild'
        headers={'Content-Type': 'application/json'}
        body=json.dumps({'guild_id':gid,'user_id':'0'})
        response = requests.post(url, headers=headers, data=body)
        # print(response.text)
        logger.info(response.text)
        d=json.loads(response.text)
        gname=d['result']['name']
        logger.info(f'服务器{gid}({gname})获取基本信息成功')
        return {'ok':True,'white':white,'black':black,'free':free,'msg':'获取基本信息成功','data':d,'gname':gname}
    except Exception as e:
        # print(e)
        logger.info(f'服务器{gid}获取基本信息失败'+ str(e))
        return {'ok':False,'white':False,'black':False,'msg':'获取基本信息失败'}

    
if __name__ == '__main__':
    logger.info("初始化完成，开始运行")
    app.run(host='0.0.0.0', port=5051)