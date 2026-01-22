<template>
  <div v-if="visible" class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>生成的标题与文案</h3>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>
      
      <div class="modal-body">
        <div v-if="!content || (!content.titles.length && !content.copywriting)" class="empty-tip">
          暂无生成内容，请在编辑页点击“生成内容”后再查看。
        </div>
        
        <template v-else>
          <!-- 标题部分 -->
          <div class="section" v-if="content.titles.length > 0">
            <div class="section-header">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16M4 12h16M4 18h10"/></svg>
              <h4>标题建议</h4>
            </div>
            <div class="titles-list">
              <div v-for="(title, i) in content.titles" :key="i" class="title-item">
                <span class="badge">{{ i === 0 ? '推荐' : i }}</span>
                <span class="text">{{ title }}</span>
              </div>
            </div>
          </div>

          <!-- 文案部分 -->
          <div class="section" v-if="content.copywriting">
            <div class="section-header">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
              <h4>正文文案</h4>
            </div>
            <div class="copywriting-box">
              {{ content.copywriting }}
            </div>
          </div>

          <!-- 标签部分 -->
          <div class="section" v-if="content.tags.length > 0">
            <div class="section-header">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
              <h4>话题标签</h4>
            </div>
            <div class="tags-list">
              <span v-for="tag in content.tags" :key="tag" class="tag">#{{ tag }}</span>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  visible: boolean
  content?: {
    titles: string[]
    copywriting: string
    tags: string[]
  }
}>()

defineEmits(['close'])
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 1001;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-content {
  background: white;
  width: 100%;
  max-width: 600px;
  max-height: 80vh;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1a1a1a;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: var(--primary, #ff2442);
}

.section-header h4 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.titles-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.title-item {
  display: flex;
  gap: 10px;
  background: #f8f9fa;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
}

.badge {
  flex-shrink: 0;
  background: #eee;
  color: #999;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  height: fit-content;
}

.title-item:first-child .badge {
  background: var(--primary, #ff2442);
  color: white;
}

.copywriting-box {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.7;
  color: #444;
  white-space: pre-wrap;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  font-size: 13px;
  color: var(--primary, #ff2442);
  background: rgba(255,36,66,0.05);
  padding: 4px 12px;
  border-radius: 100px;
}

.empty-tip {
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 14px;
}
</style>
