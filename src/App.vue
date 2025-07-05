<template>
  <Message ref="message" />
  <div v-if="p == 1">
    <f-page-header :on-back="testButton" title="bot工具" />
    <Alert
      message="请不要滥用这些功能，更不要使用发送消息功能骚扰他人和违规使用，服务器主请保管好安全密钥，以免造成不必要的麻烦。如果你有任何想法或者建议，欢迎前往服务器反馈"
      type="info"
    >
      <template #actions>
        <Space vertical gap="small" align="center">
          <Button size="small" type="primary" @click="openurl"
            >加入服务器</Button
          >
        </Space>
      </template>
    </Alert>
    <div v-if="opendebug">
      <Alert message="已开启调试模式" type="warning">
        <template #actions>
          <Button size="small" type="text" @click="closeDebug"
            >关闭调试模式</Button
          >
        </template>
      </Alert>
    </div>
    <!-- 和上面要有间隔 -->
    <div :style="{ padding: '5px' }"></div>
    <Card hoverable title="消息推送工具">
      <Flex wrap="wrap" style="width: 100%; max-width: 650px">
        <Button type="primary" @click="p = 3" ghost>
          <template #icon>
            <SendHorizontal :size="23" :style="{ fill: 'none' }" />
          </template>
          发送文本消息
        </Button>
        <Button type="primary" @click="p = 2" ghost>
          <template #icon>
            <MessageSquareCode :size="23" :style="{ fill: 'none' }" />
          </template>
          发送消息卡片
        </Button>
        <Button type="primary" @click="p = 5" ghost>
          <template #icon>
            <LetterText :size="23" :style="{ fill: 'none' }" />
          </template>
          发送富文本
        </Button>
        <!-- task为空就不显示 -->
        <div v-if="taskid.length != 0">
          <Button type="primary" @click="usergettask" ghost>
            <template #icon>
              <Logs :size="23" :style="{ fill: 'none' }" />
            </template>
            查看批量进程
          </Button>
        </div>
      </Flex>
    </Card>
  </div>
  <div v-if="p == 2">
    <f-page-header :on-back="back1" title="发送消息卡片" />
    <f-alert :alert-list="alertList1" simple title="注意：" type="warning" />
    <!-- <Alert message="提示：点击色块快速选择颜色" type="info" /> -->
    <!-- 最上方和最右边留空隙 -->
    <div style="padding-left: 10px; padding-right: 10px">
      <div :style="{ padding: '5px' }"></div>
      <h3>标题设置</h3>
      <Input
        v-model:value="bttext"
        maxlength="50"
        showCount="true"
        placeholder="卡片标题"
        addonBefore="卡片标题"
        :style="{ padding: '5px' }"
      />
      <!-- <div :style="{ padding: '5px' }"></div> -->
      <f-text>卡片标题背景色从：</f-text>
      <br />
      <Space :width="150">
        <ColorPicker
          v-model:value="color"
          placement="bottom"
          :showAlpha="false"
        />
      </Space>
      <br />
      <f-text>到：</f-text>
      <br />
      <Space :width="150">
        <ColorPicker v-model:value="color2" :showAlpha="false" />
      </Space>
      <br />
      <div :style="{ padding: '5px' }"></div>
      <f-text>卡片标题文本颜色：</f-text>
      <br />
      <Space :width="150">
        <ColorPicker v-model:value="color3" :showAlpha="false" />
      </Space>
      <br />
      <div :style="{ padding: '5px' }"></div>
      <f-text>标题预览：</f-text>
      <!-- 创建一个预览渐变色块，里面显示标题 -->
      <br />
      <div
        :style="{
          background:
            'linear-gradient(to right, ' + color + ', ' + color2 + ')',
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
      <h3>按钮设置</h3>
      <div :style="{ padding: '5px' }"></div>
      <f-text>启用按钮：</f-text>
      <Switch v-model="openbotton" />
      <div v-if="openbotton">
        <div :style="{ padding: '5px' }"></div>
        <!-- <f-text>按钮文本：</f-text> -->
        <Input
          v-model:value="bottontext"
          maxlength="10"
          showCount="true"
          placeholder="按钮文本"
          addonBefore="按钮文本"
        />
        <div :style="{ padding: '5px' }"></div>
        <!-- <f-text>按钮链接：</f-text> -->
        <Input
          v-model:value="bottonurl"
          maxlength="200"
          showCount="true"
          placeholder="按钮链接"
          addonBefore="按钮链接"
        />
        <div :style="{ padding: '5px' }"></div>
        <f-text>按钮颜色：</f-text>
        <br />
        <Space :width="150">
          <ColorPicker v-model:value="bottoncolor" :showAlpha="false" />
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
      <h3>卡片内容</h3>
      <div :style="{ padding: '5px' }"></div>
      <MdEditor
        v-model="text"
        :toolbars="toolbars"
        noUploadImg
        @onSave="onSave"
      />
      <!-- <Textarea
      v-model:value="text"
      placeholder="卡片内容，支持Markdown语法"
      showCount="true"
      maxlength="800"
    /> -->
      <!-- debug模式才显示 -->
      <div v-if="opendebug">
        <vue-monaco-editor
          v-model:value="cardjson"
          language="json"
          theme="vs-dark"
          :options="{ automaticLayout: true }"
          style="height: 400px; margin-top: 20px"
        />
      </div>
      <Button type="primary" @click="send = true">发送</Button>
    </div>
    <SendToChannel
      v-model:visible="send"
      :options="options"
      :spinning="spinning"
      :loading="sdloading"
      :onOpen="getchannel"
      :gid="gid"
      @send="sendmsg"
    />
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

    <SendToChannel
      v-model:visible="send"
      :options="options"
      :spinning="spinning"
      :loading="sdloading"
      :onOpen="getchannel"
      :gid="gid"
      @send="sendtext"
    />
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
        <Input
          v-model:value="gid"
          placeholder="服务器id"
          @enter="saveGid"
          width="75%"
        />
        <Button type="primary" @click="saveGid">保存</Button>
      </Card>

      <Card hoverable title="修改默认进程id" :width="300">
        <Input
          v-model:value="taskid"
          placeholder="进程id"
          @enter="saveTaskid"
          width="75%"
        />
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

        <Input
          v-model:value="gid"
          placeholder="服务器id"
          @enter="getgidInfo"
          width="75%"
        />
        <Button type="primary" @click="getgidInfo">获取</Button>
      </Card>
      <Card hoverable title="debug" :width="300">
        <Input
          v-model:value="apiuri"
          placeholder="api地址"
          addonBefore="API地址"
        />
        <f-text>debug：</f-text>
        <Switch v-model="opendebug" @change="handleDebugChange" />
      </Card>
    </div>
  </div>
  <div v-if="p == 5">
    <f-page-header :on-back="back1" title="发送富文本" />
    <f-alert :alert-list="alertList1" simple title="注意：" type="warning" />
    <div :style="{ padding: '7px' }">
      <Input
        v-model:value="bttext"
        maxlength="50"
        showCount="true"
        placeholder="标题"
        addonBefore="标题"
      />
    </div>
    <QuillEditor
      theme="snow"
      @update:content="onEditorUpdate"
      :options="editorOptions"
      style="min-height: 250px"
      ref="quillRef"
    />
    <div>
      <!-- <textarea
        v-model="deltaContent"
        rows="10"
        style="width: 100%; margin-top: 20px"
        readonly
      ></textarea> -->
      <!-- 编辑器更新时触发事件 -->
      <!-- debug下才显示json编辑器 -->
      <div v-if="opendebug">
        <vue-monaco-editor
          v-model:value="deltaContent"
          language="json"
          theme="vs-dark"
          :options="{ automaticLayout: true }"
          style="height: 400px; margin-top: 20px"
          :onChange="VSonEditorUpdate"
        />
      </div>

      <Button type="primary" @click="send = true">发送</Button>

      <SendToChannel
        v-model:visible="send"
        :options="options"
        :spinning="spinning"
        :loading="sdloading"
        :onOpen="getchannel"
        :gid="gid"
        @send="sendRichText"
      />
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
  Message,
  Descriptions,
  DescriptionsItem,
  Badge,
  Progress,
  Result,
  Tag,
  ColorPicker,
  Space,
  Flex,
} from "vue-amazing-ui";

import "vue-amazing-ui/css";
import { ref } from "vue";
import { MdEditor } from "md-editor-v3";
import "md-editor-v3/lib/style.css";
import type { ToolbarNames } from "md-editor-v3";
import "@vueup/vue-quill/dist/vue-quill.snow.css";
import eruda from "eruda";
import {
  SendHorizontal,
  MessageSquareCode,
  LetterText,
  Logs,
} from "lucide-vue-next";
import SendToChannel from "@/components/SendToChannel.vue";

// 自定义 image handler
function imageHandler(this: any) {
  const url = prompt("请输入图片 URL");
  if (url) {
    // this.quill 即为 editor 实例
    const range = this.quill.getSelection(true);
    // 在光标位置插入 image
    this.quill.insertEmbed(range.index, "image", url, "user");
    // 把光标移到图片后面
    this.quill.setSelection(range.index + 1);
  }
}
const editorOptions = {
  theme: "snow",
  modules: {
    toolbar: {
      container: [
        [{ header: [1, 2, 3, false] }],
        [{ size: ["small", false, "large", "huge"] }], // 字号
        ["bold", "italic", "underline", "strike"], // 粗体，斜体，下划线，删除线
        [{ list: "ordered" }, { list: "bullet" }], // 有序/无序列表
        [{ indent: "-1" }, { indent: "+1" }], // 缩进
        [{ direction: "rtl" }], // 文字方向
        [{ color: [] }, { background: [] }], // 文字颜色、背景颜色
        [{ align: [] }], // 对齐方式
        ["blockquote", "code-block"], // 引用、代码块
        ["link", "image"], // 插入链接、图片
        ["clean"], // 清除格式
      ],
      handlers: {
        // 覆盖 image 按钮的默认行为
        image: imageHandler,
      },
    },
  },
};

const p = ref(1);
const color = ref("#00AFEE");
const color2 = ref("#F2F2F2");
const color3 = ref("#F2F2F2");
const bttext = ref("标题");
const openbotton = ref(true);
const bottontext = ref("按钮");
const bottonurl = ref("https://in.fanbook.cn/LmgLJF3N");
const bottoncolor = ref("#00AFEE");
const img = ref(true);
const imgurl = ref("");
const text = ref("");
const send = ref(false);
const options = ref([]);
const selectedValue = ref("");
const gid = ref("");
const spinning = ref(false);
const disabled = ref(true);
const sdloading = ref(false);
const message = ref();
const apiuri = ref("http://127.0.0.1:5051");
const server = ref("https://124.221.67.43/botmsg");
const testapi = ref("http://127.0.0.1:5051");
const textmsg = ref("");
const isdev = ref(false);
const sendall = ref(false);
const usernum = ref(0);
const successnum = ref(0);
const failnum = ref(0);
const status = ref("");
const taskid = ref("");
const taskrun = ref(false);
const ProgressNum = ref(0);
const Ttime = ref("");
const opendebug = ref(false); // 是否开启debug模式
const alertList1 = ref([
  "禁止发送违规消息",
  "禁止发送引流广告消息",
  "禁止频繁发送私信",
  "违规服务器永久禁止使用",
]);
const toolbars: ToolbarNames[] = [
  "bold",
  "italic",
  "-",
  "title",
  "quote",
  "unorderedList",
  "orderedList",
  "-",
  "code",
  "link",
  "image",
  "-",
  "revoke",
  "next",
  "save",
  "=",
  "pageFullscreen",
  "fullscreen",
  "preview",
  "previewOnly",
  "catalog",
];

const deltaContent = ref("");
const cardjson = ref(""); // 存储服务器构建好的卡片json

let taskTimer: number | null = null;   // 统一保存定时器 ID
let isFetching = false;                // 请求锁（防并发）

const handleDebugChange = (value: boolean) => {
  // 保存到本地存储
  localStorage.setItem("debug", String(value));
  message.value?.success("保存成功");
  if (opendebug.value) {
    eruda.init();
    console.log("调试模式已开启");
  } else {
    eruda.destroy();
    console.log("调试模式已关闭");
  }
  opendebug.value = value;
};
// 检查本地存储是否有debug设置
const debugLocal = localStorage.getItem("debug");
if (debugLocal) {
  opendebug.value = debugLocal === "true";
}
// 如果开启了调试模式，则初始化 eruda
if (opendebug.value) {
  eruda.init();
  console.log("调试模式已开启");
}
// 关闭调试模式
const closeDebug = () => {
  opendebug.value = false;
  localStorage.setItem("debug", "false");
  eruda.destroy();
  message.value?.success("调试模式已关闭");
  console.log("调试模式已关闭");
};

const onEditorUpdate = (content: any) => {
  deltaContent.value = JSON.stringify(content.ops, null, 2);
};
const quillRef = ref();

const VSonEditorUpdate = (value: string) => {
  try {
    const parsed = JSON.parse(value);
    quillRef.value?.getQuill()?.setContents(parsed); // 设置编辑器内容
    deltaContent.value = value;
  } catch (e) {
    console.warn("无效的 JSON 格式");
  }
};

const ginfo = ref();
const key = ref("");
const notKey = ref(false);
const endtime = ref("-");
const onconsole = () => {
  notKey.value = false;
};

const haveGinfo = ref(false);

const copycid = () => {
  navigator.clipboard.writeText(selectedValue.value);
  message.value?.success("复制成功");
};

const testButton = () => {
  testButtonSum.value++;
  if (testButtonSum.value == 5) {
    p.value = 100;
    testButtonSum.value = 0;
  }
};

const testButtonSum = ref(0);

const openurl = () => {
  window.open("https://in.fanbook.cn/LmgLJF3N");
};

const time_remaining = ref();

const onSave = (v: string) => {
  console.log(v);
  // 保存到本地存储
  localStorage.setItem("textmsg", v);
  message.value?.success("保存成功");
  // 如果是debug模式,则获取cardjson
  if (opendebug.value) {
    getCardJson();
  }
};

// 本地存储读取textmsg
const textmsglocal = localStorage.getItem("textmsg");
if (textmsglocal) {
  text.value = textmsglocal;
}

const saveGid = () => {
  // gid保存到本地存储
  localStorage.setItem("gid", gid.value);
  message.value?.success("保存成功");
};

const onjoin = () => {
  // 跳转到指定页面
  window.open("https://in.fanbook.cn/LmgLJF3N");
};

// 本地存储读取taskid
const taskidlocal = localStorage.getItem("taskid");
if (taskidlocal) {
  taskid.value = taskidlocal;
}

const saveTaskid = () => {
  // taskid保存到本地存储
  localStorage.setItem("taskid", taskid.value);
  message.value?.success("保存成功");
};

// 通过/config.json获取server地址
fetch("/config.json")
  .then((response) => response.json())
  .then((data) => {
    apiuri.value = data.server;
  })
  .catch((error) => {
    console.error(error);
  });

// if (location.hostname == 'localhost') {
//   isdev.value = true
//   apiuri.value = testapi.value
// } else {
//   apiuri.value = server.value
// }
// apiuri.value = server.value
const change = () => {
  if (selectedValue.value == "") {
    disabled.value = true;
  } else {
    disabled.value = false;
  }
};

const getgidInfo = () => {
  spinning.value = true;
  // GET http://127.0.0.1:5051/info?gid={gid}
  fetch(apiuri.value + "/info?gid=" + gid.value)
    .then((response) => response.json())
    .then((data) => {
      if (data.ok == true) {
        ginfo.value = data;
        spinning.value = false;
        haveGinfo.value = true;
        getchannel();
        message.value?.success(data.msg);
      } else {
        message.value?.error(data.msg);
        spinning.value = false;
      }
    })
    .catch((error) => {
      console.error(error);
      spinning.value = false;
    });
};

const getchannel = () => {
  spinning.value = true;
  // GET http://127.0.0.1:5051/get?gid={gid}
  fetch(apiuri.value + "/get?gid=" + gid.value)
    .then((response) => response.json())
    .then((data) => {
      options.value = data.data;
      spinning.value = false;
      // gid保存到本地存储
      localStorage.setItem("gid", gid.value);
    })
    .catch((error) => {
      console.error(error);
      spinning.value = false;
    });
};

// 获取卡片json的函数,请求参数是sendmsg的,url后面多一个&getjson=true
const getCardJson = () => {
  const url =
    apiuri.value +
    `/sendmessage?cid=${encodeURIComponent(selectedValue.value)}&color1=${encodeURIComponent(color.value)}&color2=${encodeURIComponent(color2.value)}&textcolor=${encodeURIComponent(color3.value)}&button=${encodeURIComponent(bottontext.value)}&openbutton=${encodeURIComponent(openbotton.value)}&botton=${encodeURIComponent(bottontext.value)}&burl=${encodeURIComponent(bottonurl.value)}&btcolor=${encodeURIComponent(bottoncolor.value)}&openimg=${encodeURIComponent(img.value)}&img=${encodeURIComponent(imgurl.value)}&mdtext=${encodeURIComponent(text.value)}&bt=${encodeURIComponent(bttext.value)}&gid=${encodeURIComponent(gid.value)}&key=${encodeURIComponent(key.value)}&type=${sendall.value}&getjson=true`;
  // 发送请求,将返回的json数据赋值给cardjson
  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      if (true) {
        cardjson.value = JSON.stringify(data, null, 2);
        message.value?.success("卡片json获取成功");
      } else {
        message.value?.error(`获取卡片json失败！(${data})`);
      }
    });
};

const sendmsg = (payload: {
  gid: string;
  key: string;
  channel: string;
  sendall: boolean;
}) => {
  sdloading.value = true;
  const url =
    apiuri.value +
    `/sendmessage?cid=${encodeURIComponent(payload.channel)}&color1=${encodeURIComponent(color.value)}&color2=${encodeURIComponent(color2.value)}&textcolor=${encodeURIComponent(color3.value)}&button=${encodeURIComponent(bottontext.value)}&openbutton=${encodeURIComponent(openbotton.value)}&botton=${encodeURIComponent(bottontext.value)}&burl=${encodeURIComponent(bottonurl.value)}&btcolor=${encodeURIComponent(bottoncolor.value)}&openimg=${encodeURIComponent(img.value)}&img=${encodeURIComponent(imgurl.value)}&mdtext=${encodeURIComponent(text.value)}&bt=${encodeURIComponent(bttext.value)}&gid=${encodeURIComponent(payload.gid)}&key=${encodeURIComponent(payload.key)}&type=${payload.sendall}`;

  console.log("Request URL:", url);

  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      sdloading.value = false;
      send.value = false;
      if (data.ok == true) {
        if (payload.sendall == true) {
          message.value.success("任务已创建");
          taskid.value = data.taskid;
          // 写入本地存储
          localStorage.setItem("taskid", data.taskid);

          startPolling();
          p.value = 4;
        } else {
          message.value.success("发送成功！");
        }
      } else {
        message.value.error(`发送失败！(${data.msg})`);
        if (data.msg == "为了安全性，请点击下方加入服务器按钮，以获取密钥") {
          notKey.value = true;
        }
      }
    })
    .catch((error) => {
      console.error(error);
      sdloading.value = false;
      message.value.error("发送失败！");
    });
};

const sendtext = (payload: {
  gid: string;
  key: string;
  channel: string;
  sendall: boolean;
}) => {
  sdloading.value = true;
  const url =
    apiuri.value +
    `/sendtext?cid=${encodeURIComponent(payload.channel)}&text=${encodeURIComponent(textmsg.value)}&type=${encodeURIComponent(payload.sendall)}&gid=${encodeURIComponent(payload.gid)}&key=${encodeURIComponent(payload.key)}`;

  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      sdloading.value = false;
      send.value = false;

      if (data.ok) {
        if (payload.sendall) {
          message.value.success("任务已创建");
          taskid.value = data.taskid;
          localStorage.setItem("taskid", data.taskid);
          p.value = 4;

          startPolling();   // 启动轮询
        } else {
          message.value.success("发送成功！");
        }
      } else {
        message.value.error(`发送失败！(${data.msg})`);
        if (data.msg === "为了安全性，请点击下方加入服务器按钮，以获取密钥") {
          notKey.value = true;
        }
      }
    });
};

// 统一管理轮询
function startPolling() {
  // 先清掉旧的定时器
  if (taskTimer !== null) {
    clearInterval(taskTimer);
  }

  // 立即执行一次
  gettask();

  // 再开始新的定时器
  taskTimer = setInterval(gettask, 300) as unknown as number;
}


const sendRichText = (payload: {
  gid: string;
  key: string;
  channel: string;
  sendall: boolean;
}) => {
  sdloading.value = true;
  const url =
    apiuri.value +
    `/sendRichText?cid=${encodeURIComponent(payload.channel)}&text=${encodeURIComponent(deltaContent.value)}&type=${encodeURIComponent(payload.sendall)}&gid=${encodeURIComponent(payload.gid)}&key=${encodeURIComponent(payload.key)}&bt=${encodeURIComponent(bttext.value)}`;

  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      sdloading.value = false;
      send.value = false;
      if (data.ok == true) {
        if (payload.sendall == true) {
          message.value.success("任务已创建");
          taskid.value = data.taskid;
          // 写入本地存储
          localStorage.setItem("taskid", data.taskid);

          startPolling();
          p.value = 4;
        } else {
          message.value.success("发送成功！");
        }
      } else {
        message.value.error(`发送失败！(${data.msg})`);
        if (data.msg == "为了安全性，请点击下方加入服务器按钮，以获取密钥") {
          notKey.value = true;
        }
      }
    });
};

const gettask = () => {
  if (isFetching) return;      // 加锁：上一轮未结束就跳过
  isFetching = true;
  // GET http://127.0.0.1:5051/get?gid={gid}
  fetch(apiuri.value + "/getTask?pid=" + taskid.value)
    .then((response) => response.json())
    .then((data) => {
      if (data.msg == "发送完成") {
        status.value = data.msg;
        ProgressNum.value = 100;
        taskrun.value = false;
        status.value = data.msg;
        usernum.value = data.usernum;
        successnum.value = data.oknum;
        failnum.value = data.errnum;
        Ttime.value = data.time;
        endtime.value = data.endtime;
      } else {
        taskrun.value = true;
        status.value = data.msg;
        usernum.value = data.usernum;
        successnum.value = data.oknum;
        failnum.value = data.errnum;
        Ttime.value = data.time;
        ProgressNum.value =
          ((successnum.value + failnum.value) / usernum.value) * 100;
        if (ProgressNum.value < 0) {
          ProgressNum.value = 0;
        }
      }
      time_remaining.value = data.time_remaining; //返回秒

      // 换算时间
      const hours = Math.floor(time_remaining.value / 3600);
      const minutes = Math.floor((time_remaining.value % 3600) / 60);
      const seconds = (time_remaining.value % 60).toFixed(0);

      // 格式化时间
      const formattedTime = `${hours.toString().padStart(2, "0")}:${minutes
        .toString()
        .padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;

      // 更新显示
      time_remaining.value = formattedTime;

      // 保留1位小数
      ProgressNum.value = Number(ProgressNum.value.toFixed(1));
    })
    .catch((error) => {
      console.error(error);
      isFetching = false; // 发生错误时解锁
    });
     isFetching = false;  
};

const usergettask = () => {
  p.value = 4;
   startPolling();
};

const back1 = () => {
  p.value = 1;
        if (taskTimer !== null) {
          clearInterval(taskTimer);
          taskTimer = null;
        }
};

// 本地存储读取gid
const gidlocal = localStorage.getItem("gid");
if (gidlocal) {
  gid.value = gidlocal;
  // getchannel()
}
</script>

<style scoped>

</style>
