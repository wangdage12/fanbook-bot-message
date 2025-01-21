<template>
  <Message ref="message" />
  <div v-if="p == 1">
    <f-page-header :on-back="testButton" title="bot工具" />
    <Alert
      message="请不要滥用这些功能，更不要使用发送消息功能骚扰他人和违规使用，服务器主请保管好安全密钥，以免造成不必要的麻烦。"
      type="info"
    />
    <Alert message="提示" description="如果你有任何想法或者建议，欢迎前往反馈" type="info" closable>
      <template #actions>
        <Space vertical gap="small" align="center">
          <Button size="small" type="primary" @click="openurl">前往反馈</Button>
        </Space>
      </template>
    </Alert>
    <Card hoverable title="消息推送工具" :width="300">
      <Button type="primary" @click="p = 3">发送文本消息</Button>
      <br />
      <br />
      <Button type="primary" @click="p = 2">发送消息卡片</Button>
      <br />
      <br />
      <!-- task为空就不显示 -->
      <div v-if="taskid.length != 0">
        <Button type="primary" @click="usergettask">查看批量进程</Button>
      </div>
    </Card>
  </div>
  <div v-if="p == 2">
    <f-page-header :on-back="back1" title="发送消息卡片" />
    <f-alert :alert-list="alertList1" simple title="注意：" type="warning" />
    <!-- <Alert message="提示：点击色块快速选择颜色" type="info" /> -->
    <!-- 最上方和最右边留空隙 -->
    <div style="padding-left: 10px; padding-right: 10px">
      <f-text>卡片标题背景色从：</f-text>
      <br />
      <Space :width="150">
        <ColorPicker v-model:value="color" />
      </Space>
      <br />
      <f-text>到：</f-text>
      <br />
      <Space :width="150">
        <ColorPicker v-model:value="color2" />
      </Space>
      <br />
      <f-text>卡片标题文本颜色：</f-text>
      <br />
      <Space :width="150">
        <ColorPicker v-model:value="color3" />
      </Space>
      <br />
      <f-text>卡片标题：</f-text>
      <Input v-model:value="bttext" maxlength="50" showCount="true" placeholder="卡片标题" />
      <br />
      <f-text>标题预览：</f-text>
      <!-- 创建一个预览渐变色块，里面显示标题 -->
      <br />
      <div
        :style="{
          background: 'linear-gradient(to right, ' + color + ', ' + color2 + ')',
          color: color3,
          padding: '10px',
          borderRadius: '5px',
          marginTop: '10px',
          width: '300px',
        }"
      >
        {{ bttext }}
      </div>

      <Divider />
      <f-text>启用按钮：</f-text>
      <Switch v-model="openbotton" />
      <div v-if="openbotton">
        <f-text>按钮文本：</f-text>
        <Input v-model:value="bottontext" maxlength="10" showCount="true" placeholder="按钮文本" />
        <f-text>按钮链接：</f-text>
        <Input v-model:value="bottonurl" maxlength="200" showCount="true" placeholder="按钮链接" />
        <f-text>按钮颜色：</f-text>
        <br />
        <Space :width="150">
          <ColorPicker v-model:value="bottoncolor" />
        </Space>
      </div>
      <!-- <Divider />
    <f-text>启用图片：</f-text>
    <Switch v-model="img" />

    <div v-if="img">
      <f-text>图片链接：</f-text>
      <Input v-model:value.lazy="imgurl" maxlength="200" showCount="true" placeholder="图片链接" />
    </div> -->
      <Divider />
      <f-text>卡片内容：</f-text>
      <MdEditor v-model="text" :toolbars="toolbars" noUploadImg @onSave="onSave" />
      <!-- <Textarea
      v-model:value="text"
      placeholder="卡片内容，支持Markdown语法"
      showCount="true"
      maxlength="800"
    /> -->

      <Button type="primary" @click="send = true">发送</Button>
    </div>
    <f-dialog v-model:visible="send" title="发送到频道">
      <Spin :spinning="spinning" indicator="dynamic-circle">
        <f-text>服务器ID：</f-text>
        <f-input v-model="gid" type="text" :on-blur="getchannel" placeholder="请输入服务器ID" />
        <Select
          :options="options"
          width="200px"
          placeholder="选择频道"
          @change="change"
          v-model="selectedValue"
        />
      </Spin>
      <f-text>服务器安全密钥：</f-text>
      <Tooltip tooltip="为了安全所生成的密钥，若没有请服务器主找开发者获取">
        <Input v-model:value="key" password placeholder="请输入服务器安全密钥" />
      </Tooltip>
      <br />
      <f-text>推送到频道中所有成员的私信：</f-text>
      <Switch v-model="sendall" />
      <template #footer>
        <f-button type="primary" :on-click="sendmsg" :disabled="disabled" :loading="sdloading"
          >发送到频道</f-button
        >
      </template>
    </f-dialog>
    <div v-if="notKey">
      <Result
        status="error"
        title="服务器未设置安全密钥"
        sub-title="为了安全性，请点击下方加入服务器按钮，以获取密钥"
      >
        <template #extra>
          <Button @click="onconsole">关闭</Button>
          <Button type="primary" @click="onjoin">加入服务器</Button>
        </template>
      </Result>
    </div>
  </div>
  <div v-if="p == 3">
    <f-page-header :on-back="back1" title="发送文本消息" />
    <f-alert :alert-list="alertList1" simple title="注意：" type="warning" />
    <v-text>文本：</v-text>
    <Textarea v-model:value.lazy="textmsg" />
    <Button type="primary" @click="send = true">发送</Button>

    <f-dialog v-model:visible="send" title="发送到频道">
      <Spin :spinning="spinning" indicator="dynamic-circle">
        <f-text>服务器ID：</f-text>
        <f-input v-model="gid" type="text" :on-blur="getchannel" placeholder="请输入服务器ID" />
        <Select
          :options="options"
          width="200px"
          placeholder="选择频道"
          @change="change"
          v-model="selectedValue"
        />
      </Spin>
      <f-text>服务器安全密钥：</f-text>
      <Tooltip tooltip="为了安全所生成的密钥，若没有请服务器主找开发者获取">
        <Input v-model:value="key" password placeholder="请输入服务器安全密钥" />
      </Tooltip>
      <br />
      <f-text>推送到频道中所有成员的私信：</f-text>
      <Switch v-model="sendall" />
      <template #footer>
        <f-button type="primary" :on-click="sendtext" :disabled="disabled" :loading="sdloading"
          >发送到频道</f-button
        >
      </template>
    </f-dialog>
    <div v-if="notKey">
      <Result
        status="error"
        title="服务器未设置安全密钥"
        sub-title="为了安全性，请点击下方加入服务器按钮，以获取密钥"
      >
        <template #extra>
          <Button @click="onconsole">关闭</Button>
          <Button type="primary" @click="onjoin">加入服务器</Button>
        </template>
      </Result>
    </div>
  </div>
  <div v-if="p == 4">
    <f-page-header :on-back="back1" title="消息推送进程信息" />
    <Alert
      message="提示：进程在云服务器运行，你可以随时退出，之后点击首页的查看批量进程即可回到此页面"
      type="info"
    />
    <Descriptions title="进程信息" bordered>
      <DescriptionsItem label="成员数量">{{ usernum }}</DescriptionsItem>
      <DescriptionsItem label="成功数量" :contentStyle="{ color: '#52c41a' }">{{
        successnum
      }}</DescriptionsItem>
      <DescriptionsItem label="失败数量" :contentStyle="{ color: '#ff4d4f' }">{{
        failnum
      }}</DescriptionsItem>
      <DescriptionsItem label="创建时间">{{ Ttime }}</DescriptionsItem>
      <DescriptionsItem label="进程id" :span="2">{{ taskid }}</DescriptionsItem>
      <DescriptionsItem label="状态" :span="3">
        <Badge :status="taskrun ? 'processing' : 'success'" :text="status" />
      </DescriptionsItem>
      <DescriptionsItem label="剩余时间">{{ time_remaining }}</DescriptionsItem>
      <DescriptionsItem label="完成时间">{{ endtime }}</DescriptionsItem>
      <!-- <DescriptionsItem label="Negotiated Amount">$80.00</DescriptionsItem>
    <DescriptionsItem label="Discount">$20.00</DescriptionsItem>
    <DescriptionsItem label="Official Receipts">$60.00</DescriptionsItem> -->
    </Descriptions>
    <Progress
      :stroke-width="10"
      :stroke-color="{
        '0%': '#108ee9',
        '100%': '#87d068',
        direction: 'right',
      }"
      :percent="ProgressNum"
    />
  </div>
  <div v-if="p == 100">
    <f-page-header :on-back="back1" title="测试工具" />

    <div style="display: flex; flex-wrap: wrap; gap: 16px">
      <Card hoverable title="修改默认服务器id" :width="300">
        <Input v-model:value="gid" placeholder="服务器id" @enter="saveGid" width="75%" />
        <Button type="primary" @click="saveGid">保存</Button>
      </Card>

      <Card hoverable title="修改默认进程id" :width="300">
        <Input v-model:value="taskid" placeholder="进程id" @enter="saveTaskid" width="75%" />
        <Button type="primary" @click="saveTaskid">保存</Button>
      </Card>
      <Card hoverable title="获取服务器信息" :width="300">
        <div v-if="haveGinfo">
          <text>服务器名称：{{ ginfo.gname }}</text>
          <Tag color="green" v-if="ginfo.white">可信服务器</Tag>
          <Tag color="red" v-if="ginfo.black">黑名单服务器</Tag>
          <Tag color="cyan" v-if="ginfo.free">免费使用</Tag>
          <Select
            :options="options"
            width="75%"
            placeholder="选择频道"
            @change="change"
            v-model="selectedValue"
          />
          <Button type="primary" @click="copycid">复制</Button>
          <br />
          <text>频道ID:{{ selectedValue }} </text>
        </div>

        <Input v-model:value="gid" placeholder="服务器id" @enter="getgidInfo" width="75%" />
        <Button type="primary" @click="getgidInfo">获取</Button>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  Alert,
  Button,
  Card,
  Input,
  Switch,
  Textarea,
  Divider,
  Select,
  Spin,
  Message,
  Descriptions,
  DescriptionsItem,
  Badge,
  Progress,
  Tooltip,
  Result,
  Tag,
  ColorPicker,
  Space,
} from 'vue-amazing-ui'

import 'vue-amazing-ui/css'
import { ref } from 'vue'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import type { ToolbarNames } from 'md-editor-v3'

const p = ref(1)
const color = ref('#00afee')
const color2 = ref('#f2f2f2')
const color3 = ref('#f2f2f2')
const bttext = ref('标题')
const openbotton = ref(true)
const bottontext = ref('按钮')
const bottonurl = ref('https://in.fanbook.cn/LmgLJF3N')
const bottoncolor = ref('#00afee')
const img = ref(true)
const imgurl = ref('')
const text = ref('')
const send = ref(false)
const options = ref([])
const selectedValue = ref('')
const gid = ref('')
const spinning = ref(false)
const disabled = ref(true)
const sdloading = ref(false)
const message = ref()
const apiuri = ref('http://127.0.0.1:5051')
const server = ref('https://124.221.67.43/botmsg')
const testapi = ref('http://127.0.0.1:5051')
const textmsg = ref('')
const isdev = ref(false)
const sendall = ref(false)
const usernum = ref(0)
const successnum = ref(0)
const failnum = ref(0)
const status = ref('')
const taskid = ref('')
const taskrun = ref(false)
const ProgressNum = ref(0)
const Ttime = ref('')
const alertList1 = ref([
  '禁止发送违规消息',
  '禁止发送引流广告消息',
  '禁止频繁发送私信',
  '违规服务器永久禁止使用',
])
const toolbars: ToolbarNames[] = [
  'bold',
  'italic',
  '-',
  'title',
  'quote',
  'unorderedList',
  'orderedList',
  '-',
  'code',
  'link',
  'image',
  '-',
  'revoke',
  'next',
  'save',
  '=',
  'pageFullscreen',
  'fullscreen',
  'preview',
  'previewOnly',
  'catalog',
]

const ginfo = ref()
const key = ref('')
const notKey = ref(false)
const endtime = ref('-')
const onconsole = () => {
  notKey.value = false
}

const haveGinfo = ref(false)

const copycid = () => {
  navigator.clipboard.writeText(selectedValue.value)
  message.value?.success('复制成功')
}

const testButton = () => {
  testButtonSum.value++
  if (testButtonSum.value == 5) {
    p.value = 100
    testButtonSum.value = 0
  }
}

const testButtonSum = ref(0)

const openurl = () => {
  window.open('http://f2.wdg.cloudns.ch/from1/')
}

const time_remaining = ref()

const onSave = (v: string) => {
  console.log(v)
  // 保存到本地存储
  localStorage.setItem('textmsg', v)
  message.value?.success('保存成功')
}

// 本地存储读取textmsg
const textmsglocal = localStorage.getItem('textmsg')
if (textmsglocal) {
  text.value = textmsglocal
}

const saveGid = () => {
  // gid保存到本地存储
  localStorage.setItem('gid', gid.value)
  message.value?.success('保存成功')
}

const onjoin = () => {
  // 跳转到指定页面
  window.open('https://in.fanbook.cn/LmgLJF3N')
}

// 本地存储读取taskid
const taskidlocal = localStorage.getItem('taskid')
if (taskidlocal) {
  taskid.value = taskidlocal
}

const saveTaskid = () => {
  // taskid保存到本地存储
  localStorage.setItem('taskid', taskid.value)
  message.value?.success('保存成功')
}

// 通过/config.json获取server地址
fetch('/config.json')
  .then((response) => response.json())
  .then((data) => {
    apiuri.value = data.server
  })
  .catch((error) => {
    console.error(error)
  })

// if (location.hostname == 'localhost') {
//   isdev.value = true
//   apiuri.value = testapi.value
// } else {
//   apiuri.value = server.value
// }
// apiuri.value = server.value
const change = () => {
  if (selectedValue.value == '') {
    disabled.value = true
  } else {
    disabled.value = false
  }
}

const getgidInfo = () => {
  spinning.value = true
  // GET http://127.0.0.1:5051/info?gid={gid}
  fetch(apiuri.value + '/info?gid=' + gid.value)
    .then((response) => response.json())
    .then((data) => {
      if (data.ok == true) {
        ginfo.value = data
        spinning.value = false
        haveGinfo.value = true
        getchannel()
        message.value?.success(data.msg)
      } else {
        message.value?.error(data.msg)
        spinning.value = false
      }
    })
    .catch((error) => {
      console.error(error)
      spinning.value = false
    })
}

const getchannel = () => {
  spinning.value = true
  // GET http://127.0.0.1:5051/get?gid={gid}
  fetch(apiuri.value + '/get?gid=' + gid.value)
    .then((response) => response.json())
    .then((data) => {
      options.value = data.data
      spinning.value = false
      // gid保存到本地存储
      localStorage.setItem('gid', gid.value)
    })
    .catch((error) => {
      console.error(error)
      spinning.value = false
    })
}

// 本地存储读取gid
const gidlocal = localStorage.getItem('gid')
if (gidlocal) {
  gid.value = gidlocal
  getchannel()
}

const sendmsg = () => {
  sdloading.value = true
  const url =
    apiuri.value +
    `/sendmessage?cid=${encodeURIComponent(selectedValue.value)}&color1=${encodeURIComponent(color.value)}&color2=${encodeURIComponent(color2.value)}&textcolor=${encodeURIComponent(color3.value)}&button=${encodeURIComponent(bottontext.value)}&openbutton=${encodeURIComponent(openbotton.value)}&botton=${encodeURIComponent(bottontext.value)}&burl=${encodeURIComponent(bottonurl.value)}&btcolor=${encodeURIComponent(bottoncolor.value)}&openimg=${encodeURIComponent(img.value)}&img=${encodeURIComponent(imgurl.value)}&mdtext=${encodeURIComponent(text.value)}&bt=${encodeURIComponent(bttext.value)}&gid=${encodeURIComponent(gid.value)}&key=${encodeURIComponent(key.value)}&type=${sendall.value}`

  console.log('Request URL:', url)

  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      console.log(data)
      sdloading.value = false
      send.value = false
      if (data.ok == true) {
        if (sendall.value == true) {
          message.value.success('任务已创建')
          taskid.value = data.taskid
          // 写入本地存储
          localStorage.setItem('taskid', data.taskid)

          gettask()
          setInterval(gettask, 300)
          p.value = 4
        } else {
          message.value.success('发送成功！')
        }
      } else {
        message.value.error(`发送失败！(${data.msg})`)
        if (data.msg == '为了安全性，请点击下方加入服务器按钮，以获取密钥') {
          notKey.value = true
        }
      }
    })
    .catch((error) => {
      console.error(error)
      sdloading.value = false
      message.value.error('发送失败！')
    })
}

const sendtext = () => {
  sdloading.value = true
  const url =
    apiuri.value +
    `/sendtext?cid=${encodeURIComponent(selectedValue.value)}&text=${encodeURIComponent(textmsg.value)}&type=${encodeURIComponent(sendall.value)}&gid=${encodeURIComponent(gid.value)}&key=${encodeURIComponent(key.value)}`

  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      console.log(data)
      sdloading.value = false
      send.value = false
      if (data.ok == true) {
        if (sendall.value == true) {
          message.value.success('任务已创建')
          taskid.value = data.taskid
          // 写入本地存储
          localStorage.setItem('taskid', data.taskid)

          gettask()
          setInterval(gettask, 300)
          p.value = 4
        } else {
          message.value.success('发送成功！')
        }
      } else {
        message.value.error(`发送失败！(${data.msg})`)
        if (data.msg == '为了安全性，请点击下方加入服务器按钮，以获取密钥') {
          notKey.value = true
        }
      }
    })
}

const gettask = () => {
  // GET http://127.0.0.1:5051/get?gid={gid}
  fetch(apiuri.value + '/getTask?pid=' + taskid.value)
    .then((response) => response.json())
    .then((data) => {
      if (data.msg == '发送完成') {
        status.value = data.msg
        ProgressNum.value = 100
        taskrun.value = false
        status.value = data.msg
        usernum.value = data.usernum
        successnum.value = data.oknum
        failnum.value = data.errnum
        Ttime.value = data.time
        endtime.value = data.endtime
      } else {
        taskrun.value = true
        status.value = data.msg
        usernum.value = data.usernum
        successnum.value = data.oknum
        failnum.value = data.errnum
        Ttime.value = data.time
        ProgressNum.value = ((successnum.value + failnum.value) / usernum.value) * 100
        if (ProgressNum.value < 0) {
          ProgressNum.value = 0
        }
      }
      time_remaining.value = data.time_remaining //返回秒

      // 换算时间
      const hours = Math.floor(time_remaining.value / 3600)
      const minutes = Math.floor((time_remaining.value % 3600) / 60)
      const seconds = (time_remaining.value % 60).toFixed(0)

      // 格式化时间
      const formattedTime = `${hours.toString().padStart(2, '0')}:${minutes
        .toString()
        .padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`

      // 更新显示
      time_remaining.value = formattedTime

      // 保留1位小数
      ProgressNum.value = Number(ProgressNum.value.toFixed(1))
    })
    .catch((error) => {
      console.error(error)
    })
}

const usergettask = () => {
  p.value = 4
  setInterval(gettask, 500)
}

const back1 = () => {
  p.value = 1
}
</script>

<style scoped></style>
