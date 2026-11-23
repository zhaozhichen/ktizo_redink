<template>
  <div class="container">
    <div class="page-header">
      <h1 class="page-title">系统设置</h1>
      <p class="page-subtitle">查看 Ktizo 统一管理的 AI 模型</p>
    </div>
    <div v-if="loading" class="loading-container" role="status">
      <div class="spinner"></div>
      <p>加载配置中...</p>
    </div>
    <div v-else-if="error" class="settings-container card" role="alert">
      <p>{{ error }}</p>
      <button class="btn" @click="loadConfig">重新加载</button>
    </div>
    <div v-else-if="config" class="settings-container card">
      <h2 class="section-title">AI 设置由管理员统一管理</h2>
      <p>文本模型：{{ config.text_generation.providers[config.text_generation.active_provider]?.model }}</p>
      <p>图片模型：{{ config.image_generation.providers[config.image_generation.active_provider]?.model }}</p>
      <p class="section-desc">如需更改模型或凭据，请在 Ktizo 的集中配置中修改。</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getConfig, type Config } from '../api'

const loading = ref(true)
const error = ref('')
const config = ref<Config | null>(null)

async function loadConfig() {
  loading.value = true
  error.value = ''
  config.value = null
  try {
    const response = await getConfig()
    if (!response.success || !response.ai_managed || !response.config) {
      throw new Error('无法确认集中配置，请检查服务端配置。')
    }
    config.value = response.config
  } catch {
    error.value = '暂时无法读取集中配置，请稍后重试。'
  } finally {
    loading.value = false
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.settings-container { max-width: 900px; margin: 0 auto; }
.section-title { font-size: 18px; font-weight: 600; margin-bottom: 4px; color: #1a1a1a; }
.section-desc { font-size: 14px; color: #666; }
.loading-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 20px; color: #666; }
</style>
