<template>
  <el-config-provider :locale="zhCn">
    <FloatButton type="primary" @click="haveTool = !haveTool;getgidInfo" :left="20" :bottom="25" :width="40" :height="40">
      <template #icon>
        @
      </template>
    </FloatButton>
    <!-- 获取提及工具 -->
<el-dialog
    v-model="haveTool"
    title="提及获取工具"
    @open="getgidInfo"
  >
    <div v-loading="spinning" element-loading-text="加载中...">
      <el-form label-width="80px">
        <el-form-item label="服务器ID" style="white-space: nowrap;">
          <el-input
            v-model="gid"
            placeholder="请输入服务器ID"
            @blur="getgidInfo"
          />
        </el-form-item>
        <template v-if="haveGinfo">
                    <el-form-item label="服务器名称" style="white-space: nowrap;">
            <span>{{ ginfo.gname }}</span>
          </el-form-item>
          <h3>提及频道</h3>
          <el-form-item label="选择频道">
            <el-select
              v-model="selectedValue"
              placeholder="选择频道"
              @change="change"
              style="width: 75%;"
            >
              <el-option
                v-for="opt in options"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
            <el-button type="primary" :disabled="!selectedValue" @click="copycid">复制</el-button>
          </el-form-item>
          <el-form-item>
            <span>频道ID: {{ selectedValue }}</span>
          </el-form-item>
          <el-divider />

          <h3>提及角色</h3>
          <el-form-item label="选择角色" style="white-space: nowrap;">
            <el-select
              v-model="groupid"
              placeholder="选择角色"
              @change="change"
              style="width: 75%;"
            >
              <el-option
                v-for="grp in groups"
                :key="grp.value"
                :label="grp.label"
                :value="grp.value"
              />
            </el-select>
            <el-button type="primary" :disabled="!groupid" @click="copygupid">复制</el-button>
          </el-form-item>
          <el-form-item>
            <span>角色ID: {{ groupid }}</span>
          </el-form-item>
          <el-divider />

          <h3>提及成员</h3>
          <el-form-item label="短ID：">
            <el-input
              v-model="shortid"
              placeholder="请输入短ID"
              @blur="searchUser"
            />
          </el-form-item>
          <el-form-item label="选择成员" style="white-space: nowrap;">
            <el-select
              v-model="memberid"
              placeholder="选择成员"
              @change="change"
              style="width: 75%;"
            >
              <el-option
                v-for="user in userlist"
                :key="user.value"
                :label="user.label"
                :value="user.value"
              />
            </el-select>
            <el-button type="primary" :disabled="!memberid" @click="copymid">复制</el-button>
          </el-form-item>
          <el-form-item>
            <span>成员ID: {{ memberid }}</span>
          </el-form-item>
        </template>
      </el-form>
    </div>
  </el-dialog>
  <div v-if="p == 1">
    <el-page-header @back="testButton" >
    <template #content>
      <span class="text-large font-600 mr-3"> 消息推送工具 </span>
    </template>
        <template #extra>
      <el-switch
        v-model="darkMode"
        inline-prompt          
        @change="toggleDarkMode"
      >
        <template #active-action>🌙</template>
        <template #inactive-action>☀️</template>
      </el-switch>
    </template>
  </el-page-header>
    <el-alert
      title=""
      type="primary"
    >
      <template #default>
        <div class="alert-content">
        <span>请不要滥用这些功能，更不要使用发送消息功能骚扰他人和违规使用，服务器主请保管好安全密钥，以免造成不必要的麻烦。如果你有任何想法或者建议，欢迎前往服务器反馈</span>
        
        <el-button  type="primary" @click="openurl" link>加入服务器</el-button>
      </div>
      </template>
    </el-alert>
    <div v-if="opendebug">
      <el-alert title="" type="warning">
        <template #default>
          <div class="alert-content">
            <el-button type="warning" @click="closeDebug" link>调试模式已开启，点击关闭调试模式</el-button>
          </div>
        </template>
      </el-alert>
    </div>
    <!-- 和上面要有间隔 -->
    <div :style="{ padding: '5px' }"></div>
    <el-card shadow="hover">
          <template #header>
      <div class="card-header">
        <span>消息推送工具</span>
      </div>
    </template>
      <Flex wrap="wrap" style="width: 100%; max-width: 650px">
        <el-button type="primary" @click="p = 3" plain>
          <template #icon>
            <SendHorizontal :size="23" :style="{ fill: 'none' }" />
          </template>
          发送文本消息
        </el-button>
        <el-button type="primary" @click="p = 2" plain>
          <template #icon>
            <MessageSquareCode :size="23" :style="{ fill: 'none' }" />
          </template>
          发送消息卡片
        </el-button>
        <el-button type="primary" @click="p = 5" plain>
          <template #icon>
            <LetterText :size="23" :style="{ fill: 'none' }" />
          </template>
          发送富文本
        </el-button>
        <!-- task为空就不显示 -->
        <div v-if="taskid.length != 0">
          <el-button type="primary" @click="usergettask" plain>
            <template #icon>
              <Logs :size="23" :style="{ fill: 'none' }" />
            </template>
            查看批量进程
          </el-button>
        </div>
      </Flex>
    </el-card>
  </div>
  <div v-if="p == 2">
    <el-page-header @back="back1" >
      <template #content>
        <span class="text-large font-600 mr-3"> 发送消息卡片 </span>
      </template>
              <template #extra>
      <el-switch
        v-model="darkMode"
        inline-prompt          
        @change="toggleDarkMode"
      >
        <template #active-action>🌙</template>
        <template #inactive-action>☀️</template>
      </el-switch>
    </template>
    </el-page-header>
    <!-- <f-alert :alert-list="alertList1" simple title="注意：" type="warning" /> -->
    <!-- <Alert message="提示：点击色块快速选择颜色" type="info" /> -->
    <!-- 最上方和最右边留空隙 -->
    <div style="padding-left: 10px; padding-right: 10px">
      <div :style="{ padding: '5px' }"></div>
      <h3>标题设置</h3>
      <el-input
        v-model="bttext"
        maxlength="50"

        placeholder="卡片标题"
        :style="{ padding: '5px' }"
      >
        <template #prepend>
          <span>卡片标题</span>
        </template>
      </el-input>
      <!-- <div :style="{ padding: '5px' }"></div> -->
      <text>卡片标题背景色从：</text>
      <br />
      <Space :width="150">
        <ColorPicker
          v-model:value="color"
          placement="bottom"
          :showAlpha="false"
        />
      </Space>
      <br />
      <text>到：</text>
      <br />
      <Space :width="150">
        <ColorPicker v-model:value="color2" :showAlpha="false" />
      </Space>
      <br />
      <div :style="{ padding: '5px' }"></div>
      <text>卡片标题文本颜色：</text>
      <br />
      <Space :width="150">
        <ColorPicker v-model:value="color3" :showAlpha="false" />
      </Space>
      <br />
      <div :style="{ padding: '5px' }"></div>
      <text>标题预览：</text>
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
      <text>启用按钮：</text>
      <Switch v-model="openbotton" />
      <div v-if="openbotton">
        <div :style="{ padding: '5px' }"></div>
        <!-- <f-text>按钮文本：</f-text> -->
        <el-input
          v-model="bottontext"
          maxlength="10"
          showCount="true"
          placeholder="按钮文本"
        >
          <template #prepend>
            <span>按钮文本</span>
          </template>
        </el-input>
        <div :style="{ padding: '5px' }"></div>
        <!-- <f-text>按钮链接：</f-text> -->
        <el-input
          v-model="bottonurl"
          maxlength="200"
          showCount="true"
          placeholder="按钮链接"
        >
          <template #prepend>
            <span>按钮链接</span>
          </template>
        </el-input>
        <div :style="{ padding: '5px' }"></div>
        <text>按钮颜色：</text>
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
        :theme="mdTheme"
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
      <el-button type="primary" @click="send = true">发送</el-button>
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
    <el-page-header @back="back1" >
      <template #content>
        <span class="text-large font-600 mr-3"> 发送文本消息 </span>
      </template>
              <template #extra>
      <el-switch
        v-model="darkMode"
        inline-prompt          
        @change="toggleDarkMode"
      >
        <template #active-action>🌙</template>
        <template #inactive-action>☀️</template>
      </el-switch>
    </template>
    </el-page-header>
    <!-- <f-alert :alert-list="alertList1" simple title="注意：" type="warning" /> -->
    <v-text>文本：</v-text>
    <el-input v-model="textmsg" type="textarea" />
    <el-button type="primary" @click="send = true">发送</el-button>

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
    <el-page-header @back="back1" >
      <template #content>
        <span class="text-large font-600 mr-3"> 消息推送进程信息 </span>
      </template>
              <template #extra>
      <el-switch
        v-model="darkMode"
        inline-prompt          
        @change="toggleDarkMode"
      >
        <template #active-action>🌙</template>
        <template #inactive-action>☀️</template>
      </el-switch>
    </template>
    </el-page-header>
    <el-Alert
      title="提示：进程在云服务器运行，你可以随时退出，之后点击首页的查看批量进程即可回到此页面"
      type="primary"
    />
<el-descriptions title="进程信息" border>
  <el-descriptions-item label="成员数量">{{ usernum }}</el-descriptions-item>
  <el-descriptions-item label="成功数量">
    <span style="color: #52c41a">{{ successnum }}</span>
  </el-descriptions-item>
  <el-descriptions-item label="失败数量">
    <span style="color: #ff4d4f">{{ failnum }}</span>
  </el-descriptions-item>
  <el-descriptions-item label="创建时间">{{ Ttime }}</el-descriptions-item>
  <el-descriptions-item label="进程id" :span="2">{{ taskid }}</el-descriptions-item>
  <el-descriptions-item label="状态" :span="3">
    <el-badge :value="status" :type="taskrun ? 'primary' : 'success'" />
  </el-descriptions-item>
  <el-descriptions-item label="剩余时间">{{ time_remaining }}</el-descriptions-item>
  <el-descriptions-item label="完成时间">{{ endtime }}</el-descriptions-item>
</el-descriptions>
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
    <el-page-header @back="back1">
      <template #content>
        <span class="text-large font-600 mr-3"> 测试工具 </span>
      </template>
      <template #extra>
        <el-switch
          v-model="darkMode"
          inline-prompt
          @change="toggleDarkMode"
        >
          <template #active-action>🌙</template>
          <template #inactive-action>☀️</template>
        </el-switch>
      </template>
    </el-page-header>
    <div style="display: flex; flex-wrap: wrap; gap: 16px">
      <!-- 修改默认服务器id -->
      <el-card shadow="hover" style="width: 300px;">
        <template #header>
          <span>修改默认服务器id</span>
        </template>
        <el-input
          v-model="gid"
          placeholder="服务器id"
          style="width: 75%; margin-bottom: 8px"
          @keyup.enter="saveGid"
        />
        <el-button type="primary" @click="saveGid">保存</el-button>
      </el-card>

      <!-- 修改默认进程id -->
      <el-card shadow="hover" style="width: 300px;">
        <template #header>
          <span>修改默认进程id</span>
        </template>
        <el-input
          v-model="taskid"
          placeholder="进程id"
          style="width: 75%; margin-bottom: 8px"
          @keyup.enter="saveTaskid"
        />
        <el-button type="primary" @click="saveTaskid">保存</el-button>
      </el-card>

      <!-- 获取服务器信息 -->
      <el-card shadow="hover" style="width: 300px;">
        <template #header>
          <span>获取服务器信息</span>
        </template>
        <div v-if="haveGinfo">
          <div style="margin-bottom: 8px;">
            <span>服务器名称：{{ ginfo.gname }}</span>
          </div>
          <el-tag type="success" v-if="ginfo.white" style="margin-right: 4px;">可信服务器</el-tag>
          <el-tag type="danger" v-if="ginfo.black" style="margin-right: 4px;">黑名单服务器</el-tag>
          <el-tag type="info" v-if="ginfo.free" style="margin-right: 4px;">免费使用</el-tag>
          <el-select
            v-model="selectedValue"
            :options="options"
            placeholder="选择频道"
            style="width: 75%; margin: 8px 0"
            @change="change"
            filterable
          >
            <el-option
              v-for="opt in options"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
          <el-button type="primary" @click="copycid" style="margin-bottom: 8px;">复制</el-button>
          <div>
            <span>频道ID: {{ selectedValue }}</span>
          </div>
        </div>
        <el-input
          v-model="gid"
          placeholder="服务器id"
          style="width: 75%; margin: 8px 0"
          @keyup.enter="getgidInfo"
        />
        <el-button type="primary" @click="getgidInfo">获取</el-button>
      </el-card>

      <!-- debug -->
      <el-card shadow="hover" style="width: 300px;">
        <template #header>
          <span>debug</span>
        </template>
        <el-input
          v-model="apiuri"
          placeholder="api地址"
          style="margin-bottom: 8px"
        >
          <template #prepend>API地址</template>
        </el-input>
        <span style="margin-right: 8px;">debug：</span>
        <el-switch v-model="opendebug" @change="handleDebugChange" />
      </el-card>
    </div>
  </div>
  <div v-if="p == 5">
    <el-page-header @back="back1" >
      <template #content>
        <span class="text-large font-600 mr-3"> 发送富文本 </span>
      </template>
              <template #extra>
      <el-switch
        v-model="darkMode"
        inline-prompt          
        @change="toggleDarkMode"
      >
        <template #active-action>🌙</template>
        <template #inactive-action>☀️</template>
      </el-switch>
    </template>
    </el-page-header>
    <!-- <f-alert :alert-list="alertList1" simple title="注意：" type="warning" /> -->
    <div :style="{ padding: '7px' }">
      <el-input
        v-model="bttext"
        maxlength="50"
        placeholder="标题"
      >
        <template #prepend>
          <span>标题</span>
        </template>
      </el-input>
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

      <el-button type="primary" @click="send = true">发送</el-button>

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
  </div></el-config-provider>
</template>

<script setup lang="ts">
import {
  Button,
  Switch,
  Divider,
  Progress,
  Result,
  ColorPicker,
  Space,
  Flex,
  FloatButton,
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
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { ElMessage } from 'element-plus'
import 'element-plus/dist/index.css' // 不导入这个的话ElMessage就没有样式
import type { Themes } from "md-editor-v3";

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
const options = ref<{ label: string; value: string }[]>([]);
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

const groups = ref<{ label: string; value: string }[]>([]); // 服务器角色列表
const groupid = ref(""); // 选中的角色id
const userlist = ref<{ label: string; value: string }[]>([]); // 服务器成员列表
const memberid = ref(""); // 选中的成员id
// 是否打开提及工具
const haveTool = ref(false);

let taskTimer: number | null = null;   // 统一保存定时器 ID
let isFetching = false;                // 请求锁（防并发）

const handleDebugChange = (val: string | number | boolean) => {
  const value = Boolean(val);
  // 保存到本地存储
  localStorage.setItem("debug", String(value));
  ElMessage({message:"保存成功",type:"success"})
  if (value) {
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
  ElMessage({message:"调试模式已关闭",type:"success"});
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
  // 复制频道ID时需要${#selectedValue.value}格式
  navigator.clipboard.writeText(`\${#${selectedValue.value}}`);
  ElMessage({
    message: "复制成功",
    type: "success",
  });
};
const copygupid = () => {
  // 复制角色ID时需要${@&groupid.value}格式
  navigator.clipboard.writeText(`\${@&${groupid.value}}`);
  ElMessage({
    message: "复制成功",
    type: "success",
  });
};
const copymid = () => {
  // 复制成员ID时需要${@!memberid.value}格式
  navigator.clipboard.writeText(`\${@!${memberid.value}}`);
  ElMessage({
    message: "复制成功",
    type: "success",
  });
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
  ElMessage({message:"保存成功",type:"success"})
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
  ElMessage({message:"保存成功",type:"success"})
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
  ElMessage({message:"保存成功",type:"success"})
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
        // 获取角色信息，在data.data.result.roles中，id转换为value，name转换为label
        if (data.data.result && data.data.result.roles) {
          type Role = { id: string; name: string };
          groups.value = data.data.result.roles.map((role: Role) => ({
            label: role.name,
            value: role.id
          }));
          // groups里面再加一个全体成员，值是服务器id
          groups.value.push({ label: "全体成员", value: gid.value });
        }

        getchannel();
        ElMessage({message:data.msg,type:"success"});
      } else {
        ElMessage({message:data.msg,type:"error"})
        spinning.value = false;
      }
    })
    .catch((error) => {
      console.error(error);
      spinning.value = false;
    });
};

// 短id获取用户
// GET /searchUser?gid={gid}&shortid={shortid}
const shortid = ref("");
const searchUser = () => {
  spinning.value = true;
  fetch(apiuri.value + "/searchUser?gid=" + gid.value + "&shortid=" + shortid.value)
    .then((response) => response.json())
    .then((data) => {
      if (data.ok == true) {
        userlist.value = data.data;
        spinning.value = false;
        ElMessage({message:data.msg,type:"success"});
      } else {
        ElMessage({message:data.msg,type:"error"});
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
        ElMessage({message:"卡片json获取成功",type:"success"});
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
      if (data.ok === true) {
        if (payload.sendall === true) {
          ElMessage({message:"任务已创建",type:"success"});
          taskid.value = data.taskid;
          // 写入本地存储
          localStorage.setItem("taskid", data.taskid);

          startPolling();
          p.value = 4;
        } else {
          ElMessage({message:"发送成功！",type:"success"});
        }
      } else {
        ElMessage({message:`发送失败！(${data.msg})`,type:"error"});
        if (data.msg == "为了安全性，请点击下方加入服务器按钮，以获取密钥") {
          notKey.value = true;
        }
      }
    })
    .catch((error) => {
      console.error(error);
      sdloading.value = false;
      ElMessage({message:"发送失败！",type:"error"});
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
          ElMessage({message:"任务已创建",type:"success"});
          taskid.value = data.taskid;
          localStorage.setItem("taskid", data.taskid);
          p.value = 4;

          startPolling();   // 启动轮询
        } else {
          ElMessage({message:"发送成功！",type:"success"});
        }
      } else {
        ElMessage({message:`发送失败！(${data.msg})`,type:"error"});
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
      if (data.ok === true) {
        if (payload.sendall === true) {
          ElMessage({message:"任务已创建",type:"success"});
          taskid.value = data.taskid;
          // 写入本地存储
          localStorage.setItem("taskid", data.taskid);

          startPolling();
          p.value = 4;
        } else {
          ElMessage({message:"发送成功！",type:"success"});
        }
      } else {
        ElMessage({message:`发送失败！(${data.msg})`,type:"error"});
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

const mdTheme = ref<Themes | undefined>(undefined);
const darkMode = ref(false);
function toggleDarkMode(val: string | number | boolean) {
  const html = document.documentElement
  // 将 val 转换为布尔值
  const isDark = Boolean(val)
  if (isDark) {
    html.classList.add('dark')
    darkMode.value = true
    mdTheme.value = "dark";
  } else {
    html.classList.remove('dark')
    darkMode.value = false
    mdTheme.value = "light";
  }
  localStorage.setItem('theme', isDark ? 'dark' : 'light')
}
// toggleDarkMode(true);

const savedTheme = localStorage.getItem('theme')
if (savedTheme === 'dark') {
  toggleDarkMode(true)
}

// 本地存储读取gid
const gidlocal = localStorage.getItem("gid");
if (gidlocal) {
  gid.value = gidlocal;
  // getchannel()
}

</script>

<style scoped>
.alert-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
</style>
