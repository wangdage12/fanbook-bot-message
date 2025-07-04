<template>
  <f-dialog
    v-model:visible="localVisible"
    title="发送到频道[分离组件]"
    :on-open="onOpen"
  >
    <Spin :spinning="spinning" indicator="dynamic-circle">
      <f-text>服务器ID：</f-text>
      <f-input
        v-model="gid"
        type="text"
        @blur="onBlur"
        placeholder="请输入服务器ID"
      />
      <Select
        :options="options"
        width="200px"
        placeholder="选择频道"
        @change="change"
        v-model="selectedValue"
      />
    </Spin>
    <Tooltip tooltip="为了安全所生成的密钥，若没有请服务器主找开发者获取">
      <Input
        v-model:value="key"
        password
        placeholder="请输入服务器安全密钥"
        addonBefore="服务器安全密钥"
      />
    </Tooltip>
    <br />
    <f-text>推送到频道中所有成员的私信：</f-text>
    <Switch v-model="sendall" />
    <template #footer>
      <f-button
        type="primary"
        :on-click="handleSend"
        :disabled="disabled"
        :loading="loading"
      >
        发送到频道
      </f-button>
    </template>
  </f-dialog>
</template>

<script setup lang="ts">
import { ref, watch, defineEmits, defineProps } from "vue";
import { Input, Switch, Select, Spin, Tooltip } from "vue-amazing-ui";
const props = defineProps({
  visible: Boolean, // 控制弹窗的显示与隐藏
  options: Array, // 频道列表
  spinning: Boolean, // 加载状态
  loading: Boolean, // 发送状态
  onOpen: Function, // 打开弹窗时的逻辑（如 getchannel）
  gid: { type: String, default: "" }, // 新增，服务器ID要从父组件传入，否则无法自动获取
});

const emit = defineEmits(["update:visible", "send"]);

const localVisible = ref(props.visible);
watch(
  () => props.visible,
  (val) => {
    localVisible.value = val;
  },
);
watch(localVisible, (val) => {
  emit("update:visible", val);
});

// gid 初始值由 props.gid 决定
const gid = ref(props.gid);
watch(
  () => props.gid,
  (val) => {
    gid.value = val;
  },
);

const key = ref("");
const selectedValue = ref("");
const sendall = ref(false);
const disabled = ref(true);

function onBlur() {
  props.onOpen?.();
}

// function change(value) {
//   selectedValue.value = value
// }
const change = (value: string) => {
  selectedValue.value = value;
  if (selectedValue.value == "") {
    disabled.value = true;
  } else {
    disabled.value = false;
  }
};

function handleSend() {
  emit("send", {
    gid: gid.value,
    key: key.value,
    channel: selectedValue.value,
    sendall: sendall.value,
  });
}
</script>
