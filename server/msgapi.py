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
import os
from pyinstrument import Profiler

TASK_DIR = 'tasks/'

# 是否开启性能分析
ENABLE_PROFILING = False

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

app = flask.Flask(__name__)

@app.after_request
def cors(environ):
    environ.headers['Access-Control-Allow-Origin']='*'
    environ.headers['Access-Control-Allow-Method']='*'
    environ.headers['Access-Control-Allow-Headers']='*'
    return environ

def build_session():
    session = requests.Session()

    # 开启 keep-alive（requests 默认是 keep-alive，但显式写更稳）
    session.headers.update({
        "Connection": "keep-alive"
    })

    # 配置连接池（关键）
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=100,  # 总连接池
        pool_maxsize=100,      # 单主机最大连接数
        max_retries=3,         # 重试
        pool_block=True        # 连接不够时等待
    )

    # 对 https 应用这个连接池
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session

# 全局 Session（而不是每次函数调用内部创建）
session = build_session()
# session.verify = False 

roks=[]
errs=[]
texttypes=[]
ids=[]

def Wjson(filename, data):
    # 原子写入：先写入临时文件，再替换
    tmpfile = filename + '.tmp'
    with open(tmpfile, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    # 增加重试机制，防止 PermissionError
    for i in range(10):
        try:
            os.replace(tmpfile, filename)
            break
        except PermissionError:
            if i == 9:
                raise
            time.sleep(0.1)
    return 0

def Rjson(filename):
    # 加重试机制，防止读取时文件被占用
    for i in range(10):
        try:
            with open(filename,'r',encoding='utf-8') as f:
                data=json.load(f)
            return data
        except (PermissionError, json.JSONDecodeError):
            if i == 9:
                raise
            time.sleep(0.1)

def is_valid_filename(name):
    if len(name) != 36:
        return False
    return re.fullmatch(r'[\w\-]+', name) is not None

# 如果没有data.json文件，则创建一个默认的
if not os.path.exists('data.json'):
    default_data = {
        "black_list": [],
        "white_list": [],
        "free_list": ["ALL"],
        "keys": {
            "example_guild_id": "example_key"
        }
    }
    Wjson('data.json', default_data)
    logger.warning("data.json 文件不存在，已创建默认文件，请根据需要修改配置再使用，参见：https://github.com/wangdage12/fanbook-bot-message")

# 如果没有token.json文件，则创建一个默认的
if not os.path.exists('token.json'):
    default_token = {
        "token": "your_bot_token_here"
    }
    Wjson('token.json', default_token)
    logger.warning("token.json 文件不存在，已创建默认文件，请将机器人 token 填入该文件后再使用")

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

# 富文本适配
def process_rich_text(delta):
    """处理富文本delta，转换图片字段并标注提及"""
    # 处理图片字段
    delta = _process_images(delta)
    
    # 处理用户提及
    delta = _process_user_mentions(delta)
    
    # 处理频道提及
    delta = _process_channel_mentions(delta)
    
    # 处理角色提及
    delta = _process_role_mentions(delta)
    
    return delta

def _process_images(delta):
    """处理图片字段转换"""
    for item in delta:
        if 'insert' in item and isinstance(item['insert'], dict) and 'image' in item['insert']:
            item['insert']['source'] = item['insert'].pop('image')
            item['insert']["_type"] = 'image'
            item['insert']["_inline"] = False
    return delta

def _process_user_mentions(delta):
    """处理用户提及"""
    pattern = r"(\$\{@![^}]{1,100}\})"
    return _process_mentions(delta, pattern, "at")

def _process_channel_mentions(delta):
    """处理频道提及"""
    pattern = r"(\$\{#[^}]{1,100}\})"
    return _process_mentions(delta, pattern, "channel")

def _process_role_mentions(delta):
    """处理角色提及"""
    pattern = r"(\$\{@&[^}]{1,100}\})"
    return _process_mentions(delta, pattern, "at")

def _process_mentions(delta, pattern, attribute_key):
    """通用的提及处理函数"""
    result = []
    for item in delta:
        if not isinstance(item.get("insert"), str):
            result.append(item)
            continue
            
        insert_text = item["insert"]
        parts = re.split(pattern, insert_text)
        
        for part in parts:
            if not part:
                continue
            if re.match(pattern, part):
                result.append({
                    "insert": part,
                    "attributes": {attribute_key: part}
                })
            else:
                new_item = {"insert": part}
                # 保留原有属性
                if "attributes" in item:
                    new_item["attributes"] = item["attributes"]
                result.append(new_item)
    
    return result

# 验证颜色是否符合要求
def is_valid_color(color):
    # 检查颜色是否为6位十六进制数
    if re.fullmatch(r'#[0-9a-fA-F]{6}', color):
        return True
    else:
        return False

bottoken=Rjson('token.json')['token']

def get_members(token='',tabs=[{"start":0, "end":99}],guid='',chlid='',userid='',name='',session=session):#获取成员列表
    url=f'https://a1.fanbook.mobi/api/bot/{token}/v2/guild/members'
    headers={'Content-Type': 'application/json'}
    body={
    "guild_id":guid,
    "channel_id":chlid,
    "user_id":userid,
    "ranges":tabs
}
    body=json.dumps(body)
    r=session.post(url,headers=headers,data=body)
    return json.loads(r.text)

def sendMessage(token='',chlid='',text='',sl=0,yz=0,name='',session=session):
    # global roks,errs,texttypes,ids
    rok=roks[ids.index(name)]
    err=errs[ids.index(name)]
    texttype=texttypes[ids.index(name)]
    url=f'https://a1.fanbook.mobi/api/bot/{token}/getPrivateChat'#获取私聊频道
    headers={'Content-Type': 'application/json'}
    #print(chlid)
    body=json.dumps({"user_id":int(chlid)})
    r=session.post(url,headers=headers,data=body)
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
        r=fanbookbotapi.sendmessage(token=token,chatid=int(chlid),type=texttype,text=text,session=session)
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
    r=session.post(url,headers=headers,data=body)
    return json.loads(r.text)

# 如果没有tasks文件夹，则创建一个
if not os.path.exists(TASK_DIR[:-1]):
    os.makedirs(TASK_DIR[:-1])

def SendMessageForAllUser(clid='', gid='', token='', text='', sl=0, yz=0, name='', Ttime=''):
    if ENABLE_PROFILING:
        profiler = Profiler()
        profiler.start()

    # ---- 基础检查 ----
    if name not in ids:
        logger.error(f"name '{name}' 不存在于 ids 中")
        return

    idx = ids.index(name)
    err = errs[idx]
    texttype = texttypes[idx]

    chlid = str(clid)
    gid = str(gid)
    botid = '1' # 这个不管是多少都是一样的

    userids = []
    tabsdata = 0

    try:
        logger.info('开始验证机器人权限')
        roks[idx] -= 1

        # ---- 分页获取成员 ----
        while True:
            try:
                cylb = get_members(
                    token=token,
                    guid=gid,
                    userid=botid,
                    chlid=chlid,
                    tabs=[{"start": tabsdata, "end": tabsdata + 99}],
                    name=name
                )
            except Exception as e:
                logger.exception("获取成员列表失败（API 调用异常）")
                break

            ops = cylb.get('result', {}).get('ops', [])
            if not ops:
                logger.error("成员列表返回为空或格式不正确")
                break

            items = ops[0].get('items', [])
            for item in items:
                if 'User' in item:
                    userids.append(item['User']['user_id'])

            logger.info(f'获取成员成功，当前累计 {len(userids)} 人')

            Wjson(
                filename=TASK_DIR + name + '.json',
                data={
                    "usernum": len(userids),
                    "sendnum": sl,
                    "errnum": errs[idx],
                    "oknum": roks[idx],
                    "msg": "正在获取成员列表",
                    "time": Ttime,
                    "time_remaining": str(len(userids) * 0.25)
                }
            )

            # 是否已取完
            if len(items) < 99:
                logger.info(f'成员列表获取完成，总共 {len(userids)} 人')
                Wjson(
                    filename=TASK_DIR + name + '.json',
                    data={
                        "usernum": len(userids),
                        "sendnum": sl,
                        "errnum": errs[idx],
                        "oknum": roks[idx],
                        "msg": "获取完成，即将发送消息",
                        "time": Ttime,
                        "time_remaining": str(len(userids) * 0.25)
                    }
                )
                break

            tabsdata += 99

        # ---- 发送消息 ----
        for uid in userids:
            try:
                sendMessage(token=token, chlid=uid, text=text, sl=sl, name=name, session=session)
            except Exception as e:
                logger.exception(f"发送消息失败 user_id={uid}")
                errs[idx] += 1
                continue

            sl += 1
            Wjson(
                filename=TASK_DIR + name + '.json',
                data={
                    "usernum": len(userids),
                    "sendnum": sl,
                    "errnum": errs[idx],
                    "oknum": roks[idx] + 1,
                    "msg": "正在发送消息",
                    "time": Ttime,
                    "time_remaining": str((len(userids) - sl) * 0.25)
                }
            )

        # ---- profiling ----
        if ENABLE_PROFILING:
            profiler.stop()
            with open('SendMessageForAllUser_profile.html', 'w') as f:
                f.write(profiler.output_html())

        logger.info(f'发送完成：成功 {roks[idx] + 1} 次，失败 {errs[idx]} 次')

        Wjson(
            filename=TASK_DIR + name + '.json',
            data={
                "usernum": len(userids),
                "sendnum": sl,
                "errnum": errs[idx],
                "oknum": roks[idx] + 1,
                "msg": "发送完成",
                "time": Ttime,
                "endtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "time_remaining": '0'
            }
        )

    except Exception as e:
        logger.exception("SendMessageForAllUser 运行时出现未捕获异常")
        logger.error("可能是 token 不正确")


# SendMessageForAllUser(clid=433212507046281216,gid='433204455396081664',token='0f2de7ac66727cd9fcec1ee43559c561f6abf3f1e202c5a06c2ae4a3f6cf94ab795fbfbe39ad311a18ad1ff314388d1c',text='text',name=str(uuid.uuid1()))

def get_err_msg(code):
    if code == 1021:
        return '频道不存在'
    if code == 1012:
        return '机器人没有权限'
    if code == 1001:
        return '参数错误'
    if code == 5103:
        return '消息内容json格式不正确'
    if code == 5104:
        return '消息长度超过限制'
    if code == 5105:
        return '不支持该消息类型'
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
        r=fanbookbotapi.sendmessage(token=bottoken,chatid=cid,type='fanbook',text=json.dumps({'width': None, 'height': None, 'data':json.dumps(data) , 'notification': None, 'come_from_icon': None, 'come_from_name': None, 'template': None, 'no_seat_toast': None, 'type': 'messageCard'}),session=session).text
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
        r=fanbookbotapi.sendmessage(token=bottoken,chatid=cid,type='text',text=text,session=session).text
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
    """
    Handles the sending of rich text (Quill v2) messages to a specified channel or as a broadcast to all users in a guild.
    
    Validates server security credentials and blacklist status before processing. Accepts a JSON-formatted rich text delta, modifies image fields for compatibility, and appends server origin information based on whitelist status. For broadcast messages, initiates a background thread to send the message to all users and returns a task ID. For single-channel messages, sends the message directly and returns the API response. Returns an error if the rich text format is invalid or if security checks fail.
    
    Returns:
        dict: A result object indicating success or failure, with additional information such as a task ID or error message.
    """
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
        try:
            delta=json.loads(text)
        except json.JSONDecodeError:
            logger.error(f'服务器{gid}发送富文本消息到频道{cid}失败，富文本格式错误')
            return {'ok':False,'msg':'富文本格式错误，请检查富文本格式'}
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
        delta=process_rich_text(delta)

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
        return {'ok': True, 'taskid': taskid}
    else:
        logger.info(f'服务器{gid}发送富文本消息到频道{cid}')
        try:
            delta = json.loads(text)
        except json.JSONDecodeError:
            logger.error(f'服务器{gid}发送富文本消息到频道{cid}失败，富文本格式错误')
            return {'ok': False, 'msg': '富文本格式错误，请检查富文本格式'}
        delta = process_rich_text(delta)
                
        logger.debug(f'富文本json：{delta}')
        # 目前有一个bug，图片在pc端上非常小，web端上非常大，目前不清楚原因
        msg={
            "type": "richText",
            "title": bt,
            # "document": json.dumps(delta),# 这个是富文本去掉所有样式的数组，但是直接传普通的富文本似乎也可以
            "v2":json.dumps(delta),# 这个是富文本的Quill v2版本，包含所有样式，不传这个只传上面的document会导致富文本样式丢失
            "v":2# 这个是富文本的版本号，必须为2
        }
        r=fanbookbotapi.sendmessage(token=bottoken,chatid=cid,type='fanbook',text=json.dumps(msg),session=session).text
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
        
# 发送原始json数据
@app.route('/sendRaw', methods=['post'])
def sendRaw():
    """发送原始json数据到指定频道
    """
    data = flask.request.get_json(force=True)  # 获取 JSON 数据
    cid = data.get('cid')
    gid = data.get('gid')
    key = data.get('key')
    to_all = data.get('to_all')
    jsondata = data.get('jsondata') 
    
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
    
    logger.info(f'服务器{gid}发送原始json数据到频道{cid}')
    
    typeisok=False

    try:
        if jsondata['type']=='column':
            logger.info('检测到json数据为卡片类型，进行封装')
            jsondata={"type":"task","content":jsondata}
            typeisok=True
    except:
        pass
    try:
        if jsondata['tag']=='column':
            logger.info('检测到json数据为复杂卡片类型，进行封装')
            jsondata={'width': None, 'height': None, 'data':json.dumps(jsondata) , 'notification': None, 'come_from_icon': None, 'come_from_name': None, 'template': None, 'no_seat_toast': None, 'type': 'messageCard'}
            typeisok=True
    except:
        pass
    if typeisok==False:
        logger.warning('无法确定json数据格式，直接发送原始数据')
    if to_all==True:
        white_list=Rjson('data.json')
        white_list=white_list['white_list']
        logger.info(f'服务器{gid}批量发送原始json数据到{cid}')
        if gid not in white_list:
            return {'ok':False,'msg':'为了安全性，只有白名单服务器才能使用批量发送原始json数据功能'}

        taskid=str(uuid.uuid1())
        t = threading.Thread(target=SendMessageForAllUser, args=(int(cid),gid,bottoken,json.dumps(jsondata),0,0,taskid,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        ids.append(taskid)
        roks.append(0)
        errs.append(0)
        texttypes.append('fanbook')
        # 启动线程
        t.start()
        return {'ok':True,'taskid':taskid}
    r=fanbookbotapi.sendmessage(token=bottoken,chatid=cid,type='fanbook',text=json.dumps(jsondata),session=session).text
    data=json.loads(r)
    if data['ok']==True:
        return data
    else:
        logger.warning(f'服务器{gid}发送消息到频道{cid}失败，错误码{data["error_code"]}')
        logger.debug(f'原始json数据：{jsondata}')
        try:
            data['msg']=get_err_msg(data['error_code'])
        except:
            data['msg']='未知错误'
        return data
    
# 检测消息类型接口
@app.route('/detectMessageType', methods=['post'])
def detectMessageType():
    """检测消息类型接口
    """
    data = flask.request.get_json(force=True)  # 获取 JSON 数据
    
    try:
        jsondata = json.loads(data.get('jsondata')) 
    except:
        return {'ok':False,'msg':'json数据格式错误，无法解析'}
    
    typeisok=False
    try:
        if jsondata['type']=='column':
            logger.info('检测到json数据为卡片类型')
            typeisok=True
            return {'ok':True,'type':'card','msg':'未封装的卡片消息（任务卡片）'}
    except:
        pass
    try:
        if jsondata['tag']=='column':
            logger.info('检测到json数据为复杂卡片类型')
            typeisok=True
            return {'ok':True,'type':'complex_card','msg':'未封装的复杂卡片消息'}
    except:
        pass
    if typeisok==False:
        # 无法确定类型
        logger.info('无法确定json数据格式')
        logger.debug(f'原始json数据：{jsondata}')
        return {'ok':True,'type':'unknown','msg':'无法确定消息数据类型'}
    
@app.route('/getTask', methods=['get'])
def getTask():
    try:
        name=flask.request.args.get('pid')
        # 验证任务ID是否合法，防止路径遍历攻击，并且满足：只符合uuid4长度、不允许含有data、token
        if not is_valid_filename(name):
            return {'ok': False, 'msg': '非法的任务ID'}
        d=Rjson(TASK_DIR+name+'.json')
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
    response = session.post(url, headers=headers, data=body)
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
        response = session.post(url, headers=headers, data=body)
        # logger.info(response.text)
        d=json.loads(response.text)
        gname=d['result']['name']
        logger.info(f'服务器{gid}({gname})获取基本信息成功')
        return {'ok':True,'white':white,'black':black,'free':free,'msg':'获取基本信息成功','data':d,'gname':gname}
    except Exception as e:
        # print(e)
        logger.info(f'服务器{gid}获取基本信息失败'+ str(e))
        return {'ok': False, 'white': False, 'black': False, 'msg': '获取基本信息失败'}

# 查询用户
@app.route('/searchUser', methods=['GET'])
def searchUser():
    """
    搜索服务器成员，输入服务器id和用户短id(或者昵称)，返回用户信息
    """
    gid = flask.request.args.get('gid')
    shortid = flask.request.args.get('shortid')
    if not shortid or not gid:
        return {'ok': False, 'msg': '缺少参数'}

    url_by_name = f'https://a1.fanbook.cn/api/bot/{bottoken}/searchGuildMemberByName'
    url_by_query = f'https://a1.fanbook.cn/api/bot/{bottoken}/searchGuildMember'
    headers = {'Content-Type': 'application/json'}

    # 通过短id查询
    body_name = json.dumps({'guild_id': int(gid), 'username': [shortid]})
    res_name = session.post(url_by_name, headers=headers, data=body_name)
    d = res_name.json()

    # 通过昵称查询
    body_query = json.dumps({'guild_id': int(gid), 'query': shortid})
    res_query = session.post(url_by_query, headers=headers, data=body_query)
    searRes = res_query.json()

    logger.info(f'搜索用户: byName={d}, byQuery={searRes}')

    # 合并两个结果，去重（以 user id 为唯一标识）
    users = {}
    if d.get('ok') and 'result' in d:
        for item in d['result']:
            u = item['user']
            users[u['id']] = {"value": str(u['id']), "label": str(u['first_name'])}

    if searRes.get('ok') and 'result' in searRes:
        for item in searRes['result']:
            u = item['user']
            users[u['id']] = {"value": str(u['id']), "label": str(u['first_name'])}

    if users:
        return {'ok': True, 'data': list(users.values()), 'msg': '搜索用户成功'}
    else:
        return {'ok': False, 'data': [], 'msg': '搜索用户失败，可能是用户不存在'}

@app.route('/', methods=['GET'])
def index():
    return {"msg": "欢迎使用WDG Fanbook消息平台API，要了解更多，请查看：https://github.com/wangdage12/fanbook-bot-message", "ok": True}

if __name__ == '__main__':
    logger.info("初始化完成，开始运行")
    app.run(host='0.0.0.0', port=5051)