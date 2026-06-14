<template>
  <div class="auth-guard">
    <div class="auth-container">
      <!-- 主卡片 -->
      <div class="auth-card" :class="{ shake: isShaking, success: isSuccess }">
        <!-- 头部 -->
        <div class="auth-header">
          <div class="auth-icon">{{ isSuccess ? '🎉' : '🔐' }}</div>
          <h1 class="auth-title">{{ isSuccess ? '欢迎回来！' : '访问验证' }}</h1>
          <p class="auth-subtitle">{{ isSuccess ? '万哥，系统已为您准备好' : '只有认识系统开发者的人才能访问' }}</p>
        </div>
        
        <!-- 验证区域 -->
        <div class="auth-body" v-if="!isSuccess">
          <div class="question-card">
            <div class="question-icon">❓</div>
            <div class="question-text">请问，系统开发者的名字是？</div>
          </div>
          
          <div class="input-wrapper" :class="{ error: showError, correct: isSuccess }">
            <input 
              v-model="answer"
              type="text"
              class="answer-input"
              placeholder="请输入答案..."
              @keyup.enter="checkAnswer"
              :disabled="isChecking"
              ref="inputRef"
            />
            <div class="input-border"></div>
          </div>
          
          <button 
            class="submit-btn" 
            @click="checkAnswer"
            :disabled="!answer.trim() || isChecking"
          >
            <span v-if="!isChecking">确认访问</span>
            <span v-else class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </button>
          
          <!-- 提示信息 -->
          <div v-if="showError" class="error-message">
            <div class="error-icon">{{ errorEmoji }}</div>
            <div class="error-text">{{ errorMessage }}</div>
          </div>
        </div>
        
        <!-- 成功区域 -->
        <div class="success-body" v-else>
          <div class="success-animation">
            <div class="confetti" v-for="n in 20" :key="n"></div>
          </div>
          <div class="success-text">正在进入系统...</div>
        </div>
      </div>
      
      <!-- 底部装饰 -->
      <div class="auth-footer">
        <div class="hint-text">💡 提示：他的称呼是两个字</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  token: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['authenticated'])

const answer = ref('')
const isChecking = ref(false)
const showError = ref(false)
const isShaking = ref(false)
const isSuccess = ref(false)
const errorEmoji = ref('😅')
const errorMessage = ref('')
const inputRef = ref(null)
const adminRole = ref('user')

const wrongAnswers = {
  default: {
    emoji: '😅',
    message: '答错啦！再想想看...'
  },
  variations: [
    { emoji: '🤔', message: '嗯...好像不对哦' },
    { emoji: '😂', message: '哈哈，这个答案有点意思' },
    { emoji: '🙃', message: '差一点点，但不是这个' },
    { emoji: '🙈', message: '哎呀，不是不是' },
    { emoji: '🦄', message: '神兽也无法帮你通过验证' },
    { emoji: '🎮', message: '游戏结束了，重新开始吧' },
    { emoji: '🌪️', message: '错误答案引发了龙卷风！' },
    { emoji: '🎭', message: '演技不错，但答案不对' },
    { emoji: '🎪', message: '马戏团表演结束，请重新作答' },
    { emoji: '🚀', message: '发射失败，请检查燃料（答案）' },
  ]
}

// 管理员强密码
const ADMIN_PASSWORD = 'Wg@2026WC!Admin#Strong'

const getBallStyle = (n) => {
  const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
  const size = Math.random() * 100 + 50
  return {
    width: `${size}px`,
    height: `${size}px`,
    background: `linear-gradient(135deg, ${colors[n-1]}, ${colors[(n+1) % 6]})`,
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    animationDelay: `${n * 0.5}s`,
    animationDuration: `${Math.random() * 10 + 10}s`
  }
}

const checkAnswer = () => {
  if (!answer.value.trim() || isChecking.value) return
  
  isChecking.value = true
  showError.value = false
  
  // 模拟验证延迟
  setTimeout(() => {
    const input = answer.value.trim()
    
    // 管理员密码
    if (input === ADMIN_PASSWORD) {
      isSuccess.value = true
      isChecking.value = false
      adminRole.value = 'admin'
      
      // 不再存储验证信息到localStorage（由App.vue负责）
      
      // 2秒后跳转
      setTimeout(() => {
        emit('authenticated', 'admin')
      }, 2000)
    }
    // 普通用户密码（万哥）
    else if (input === '万哥' || input.toLowerCase() === 'wange') {
      isSuccess.value = true
      isChecking.value = false
      adminRole.value = 'user'
      
      // 不再存储验证信息到localStorage（由App.vue负责）
      
      // 2秒后跳转
      setTimeout(() => {
        emit('authenticated', 'user')
      }, 2000)
    }
    // 错误答案
    else {
      isChecking.value = false
      showError.value = true
      isShaking.value = true
      
      const randomIndex = Math.floor(Math.random() * wrongAnswers.variations.length)
      const randomError = wrongAnswers.variations[randomIndex]
      errorEmoji.value = randomError.emoji
      errorMessage.value = randomError.message
      
      answer.value = ''
      
      setTimeout(() => {
        isShaking.value = false
        inputRef.value?.focus()
      }, 500)
    }
  }, 800)
}

onMounted(() => {
  inputRef.value?.focus()
})
</script>

<style scoped>
.auth-guard {
  position: fixed;
  inset: 0;
  background-image: url('/worldcup/auth-bg-pc.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  z-index: 9999;
}

/* 背景遮罩层 */
.auth-guard::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.auth-container {
  position: relative;
  width: 100%;
  max-width: 480px;
  padding: 20px;
  z-index: 10;
}

/* 增强卡片背景 */
.auth-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 40px 32px;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.auth-card.shake {
  animation: shake 0.5s ease-in-out;
}

.auth-card.success {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-10px); }
  20%, 40%, 60%, 80% { transform: translateX(10px); }
}

/* 头部 */
.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-icon {
  font-size: 4rem;
  margin-bottom: 16px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.auth-title {
  font-size: 2rem;
  font-weight: 800;
  color: #1a472a;
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.auth-subtitle {
  font-size: 1rem;
  color: #666;
  margin: 0;
}

/* 问题卡片 */
.question-card {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.question-icon {
  font-size: 2.5rem;
}

.question-text {
  font-size: 1.1rem;
  font-weight: 600;
  line-height: 1.5;
}

/* 输入框 */
.input-wrapper {
  position: relative;
  margin-bottom: 20px;
}

.answer-input {
  width: 100%;
  padding: 16px 20px;
  font-size: 1.2rem;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  outline: none;
  transition: all 0.3s ease;
  background: white;
  font-weight: 600;
}

.answer-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.answer-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.input-wrapper.error .answer-input {
  border-color: #f5576c;
  animation: inputShake 0.3s ease;
}

.input-wrapper.correct .answer-input {
  border-color: #28a745;
}

@keyframes inputShake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  padding: 16px;
  font-size: 1.1rem;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-dots span {
  animation: dots 1.4s infinite;
  display: inline-block;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dots {
  0%, 80%, 100% { opacity: 0; }
  40% { opacity: 1; }
}

/* 错误信息 */
.error-message {
  margin-top: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #fff5f5, #ffe0e0);
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  animation: fadeIn 0.3s ease;
}

.error-icon {
  font-size: 2rem;
}

.error-text {
  font-size: 1rem;
  font-weight: 600;
  color: #c62828;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 成功动画 */
.success-body {
  text-align: center;
  padding: 20px;
}

.success-animation {
  position: relative;
  height: 100px;
  margin-bottom: 20px;
}

.confetti {
  position: absolute;
  width: 10px;
  height: 10px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  animation: confetti 1s ease-out forwards;
  opacity: 0;
}

.confetti:nth-child(odd) {
  background: linear-gradient(135deg, #f093fb, #f5576c);
}

.confetti:nth-child(3n) {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  border-radius: 50%;
}

.confetti:nth-child(4n) {
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  transform: rotate(45deg);
}

@keyframes confetti {
  0% {
    opacity: 1;
    transform: translate(0, 0) rotate(0deg);
  }
  100% {
    opacity: 0;
    transform: translate(var(--x, 100px), var(--y, 100px)) rotate(720deg);
  }
}

.confetti:nth-child(1) { --x: -100px; --y: 100px; animation-delay: 0s; }
.confetti:nth-child(2) { --x: 100px; --y: 100px; animation-delay: 0.05s; }
.confetti:nth-child(3) { --x: 0px; --y: 150px; animation-delay: 0.1s; }
.confetti:nth-child(4) { --x: -150px; --y: 50px; animation-delay: 0.15s; }
.confetti:nth-child(5) { --x: 150px; --y: 50px; animation-delay: 0.2s; }
.confetti:nth-child(6) { --x: -50px; --y: 150px; animation-delay: 0.25s; }
.confetti:nth-child(7) { --x: 50px; --y: 150px; animation-delay: 0.3s; }
.confetti:nth-child(8) { --x: -100px; --y: 80px; animation-delay: 0.35s; }
.confetti:nth-child(9) { --x: 100px; --y: 80px; animation-delay: 0.4s; }
.confetti:nth-child(10) { --x: 0px; --y: 120px; animation-delay: 0.45s; }

.success-text {
  font-size: 1.3rem;
  font-weight: 700;
  color: #1a472a;
  animation: pulse 1s ease infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* 底部提示 */
.auth-footer {
  text-align: center;
  margin-top: 24px;
}

.hint-text {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .auth-guard {
    background-image: url('/worldcup/auth-bg-mobile.jpg');
  }
  
  .auth-container {
    padding: 16px;
  }
  
  .auth-card {
    padding: 32px 24px;
    border-radius: 20px;
  }
  
  .auth-icon {
    font-size: 3rem;
  }
  
  .auth-title {
    font-size: 1.6rem;
  }
  
  .question-card {
    padding: 16px;
  }
  
  .question-icon {
    font-size: 2rem;
  }
  
  .question-text {
    font-size: 1rem;
  }
  
  .answer-input {
    padding: 14px 16px;
    font-size: 1.1rem;
  }
  
  .submit-btn {
    padding: 14px;
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .auth-card {
    padding: 24px 20px;
    border-radius: 16px;
  }
  
  .auth-icon {
    font-size: 2.5rem;
  }
  
  .auth-title {
    font-size: 1.4rem;
  }
  
  .auth-subtitle {
    font-size: 0.9rem;
  }
  
  .question-card {
    flex-direction: column;
    text-align: center;
    gap: 8px;
  }
  
  .answer-input {
    padding: 12px 14px;
    font-size: 1rem;
  }
}
</style>
