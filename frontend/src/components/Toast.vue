<template>
  <transition name="toast">
    <div v-if="visible" :class="['toast-container', toastType]">
      <div class="toast-icon">{{ icon }}</div>
      <div class="toast-message">{{ message }}</div>
    </div>
  </transition>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const message = ref('')
const toastType = ref('success')
const icon = ref('✓')

function show(msg, type = 'success', duration = 3000) {
  message.value = msg
  toastType.value = type
  
  // 设置图标
  if (type === 'success') {
    icon.value = '✓'
  } else if (type === 'error') {
    icon.value = '✕'
  } else if (type === 'warning') {
    icon.value = '⚠'
  } else if (type === 'info') {
    icon.value = 'ℹ'
  }
  
  visible.value = true
  
  setTimeout(() => {
    visible.value = false
  }, duration)
}

// 导出函数供外部使用
defineExpose({ show })
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 9999;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-size: 1rem;
  font-weight: 600;
  min-width: 200px;
}

.toast-icon {
  font-size: 1.2rem;
}

.toast-message {
  flex: 1;
}

/* 类型样式 */
.success {
  background: linear-gradient(135deg, #d4edda, #c3e6cb);
  color: #155724;
  border: 2px solid #28a745;
}

.error {
  background: linear-gradient(135deg, #f8d7da, #f5c6cb);
  color: #721c24;
  border: 2px solid #dc3545;
}

.warning {
  background: linear-gradient(135deg, #fff3cd, #ffeaa7);
  color: #856404;
  border: 2px solid #ffc107;
}

.info {
  background: linear-gradient(135deg, #d1ecf1, #bee5eb);
  color: #0c5460;
  border: 2px solid #17a2b8;
}

/* 动画 */
.toast-enter-active {
  animation: slideDown 0.3s ease;
}

.toast-leave-active {
  animation: slideUp 0.3s ease;
}

@keyframes slideDown {
  from {
    transform: translateX(-50%) translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(-50%) translateY(0);
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateX(-50%) translateY(0);
    opacity: 1;
  }
  to {
    transform: translateX(-50%) translateY(-100%);
    opacity: 0;
  }
}

/* 移动端优化 */
@media (max-width: 768px) {
  .toast-container {
    top: 10px;
    padding: 10px 16px;
    font-size: 0.9rem;
    min-width: 150px;
  }
}
</style>