<template>
  <el-dialog
    v-model="localVisible"
    title="发送到频道"
    @open="onOpen"
    width="420px"
    :draggable="true"
  >
    <!-- 加载遮罩 -->
    <div v-loading="spinning">
      <!-- 服务器 ID -->
      <div class="field">
        <span class="label">服务器ID：</span>
        <el-input
          v-model="gid"
          placeholder="请输入服务器ID"
          @blur="onBlur"
          class="w-200"
        />
      </div>

      <!-- 频道选择 -->
      <el-select
        v-model="selectedValue"
        placeholder="选择频道"
        class="w-200 field"
        @change="handleChange"
      >
        <el-option
          v-for="item in options"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>

      <!-- 安全密钥 -->
      <el-tooltip
        content="为了安全所生成的密钥，若没有请服务器主找开发者获取"
        placement="top"
      >
        <el-input
          v-model="key"
          type="password"
          placeholder="请输入服务器安全密钥"
          class="field"
        >
          <template #prepend>服务器安全密钥</template>
        </el-input>
      </el-tooltip>

      <!-- 推送到全部成员私信 -->
      <div class="field">
        <span class="label">推送到频道中所有成员的私信：</span>
        <el-switch v-model="sendall" />
      </div>
    </div>

    <!-- 底部按钮 -->
    <template #footer>
      <el-button
        type="primary"
        @click="handleSend"
        :disabled="disabled"
        :loading="loading"
      >
        发送到频道
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue'
import type { PropType } from 'vue'

interface Option {
  label: string
  value: string | number
}

const props = defineProps({
  visible: Boolean,
  options: {
    type: Array as PropType<Option[]>,
    default: () => [],
  },
  spinning: Boolean,
  loading: Boolean,
  onOpen: {
    type: Function as PropType<() => any>,
    required: false,
  },
  gid: {
    type: String as PropType<string>,
    default: '',
  },
})

// 添加 gid-change emit
const emit = defineEmits(['update:visible', 'send', 'gid-change'])

// 弹窗显隐
const localVisible = ref(props.visible)
watch(
  () => props.visible,
  (val) => (localVisible.value = val),
)
watch(localVisible, (val) => emit('update:visible', val))

// 服务器 ID
const gid = ref(props.gid)
watch(
  () => props.gid,
  (val) => (gid.value = val),
)

// 监听本地gid变化，emit到父组件
watch(gid, (val) => {
  emit('gid-change', val)
})

// 其余表单数据
const key = ref('')
const selectedValue = ref('')
const sendall = ref(false)
const disabled = ref(true)

// 服务器 ID 失焦，向父级请求频道列表
function onBlur() {
  props.onOpen?.()
}

// 频道下拉框变更
function handleChange(val: string | number) {
  selectedValue.value = String(val)
  disabled.value = selectedValue.value === ''
}

// 点击发送
function handleSend() {
  emit('send', {
    gid: gid.value,
    key: key.value,
    channel: selectedValue.value,
    sendall: sendall.value,
  })
}
</script>

<style scoped>
.w-200 {
  width: 200px;
}
.field {
  margin-bottom: 12px;
}
.label {
  margin-right: 4px;
}
</style>
