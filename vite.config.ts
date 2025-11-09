import { sentryVitePlugin } from "@sentry/vite-plugin";
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { visualizer } from 'rollup-plugin-visualizer';

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools(), sentryVitePlugin({
    org: "wdg1122",
    project: "botmsg"
  }), AutoImport({
      resolvers: [ElementPlusResolver()],
      // 可选：自动导入 Element Plus 的 API，如 ElMessage 等
      imports: ['vue', 'vue-router'],
      dts: 'src/auto-imports.d.ts',
    }), Components({
    resolvers: [ElementPlusResolver()],
    dts: 'src/components.d.ts',
  }), visualizer({ open: true }), sentryVitePlugin({
    org: "wdg1122",
    project: "botmsg"
  })],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },

  build: {
    sourcemap: true
  }
})