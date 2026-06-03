<template>
  <div class="verify-panel">
    <div class="verify-header">
      <span class="verify-title">⚙️ 结果验证</span>
      <button @click="showVerifyPanel = !showVerifyPanel" class="toggle-btn">
        {{ showVerifyPanel ? '收起' : '展开' }}
      </button>
    </div>
    
    <div v-if="showVerifyPanel" class="verify-body">
      <div class="verify-row">
        <select v-model="selectedGroup" class="verify-select">
          <option value="">选择小组</option>
          <option v-for="g in 'ABCDEFGHIJKL'.split('')" :key="g" :value="g">{{ g }}组</option>
        </select>
        
        <select v-model="selectedMatch" class="verify-select">
          <option value="">选择比赛</option>
          <option v-for="i in 6" :key="i" :value="i-1">第{{ i }}场</option>
        </select>
        
        <select v-model="selectedResult" class="verify-select">
          <option value="">选择结果</option>
          <option value="HOME_WIN">主胜</option>
          <option value="DRAW">平局</option>
          <option value="AWAY_WIN">客胜</option>
        </select>
      </div>
      
      <button @click="verifyMatch" class="verify-btn" :disabled="!canVerify">
        确认验证
      </button>
      
      <div v-if="verifyResult" class="verify-result">
        <div :class="['result-badge', verifyResult.success ? 'success' : 'error']">
          {{ verifyResult.success ? '✓ 验证成功' : '✗ 验证失败' }}
        </div>
        <div v-if="verifyResult.success" class="result-detail">
          已验证 {{ verifyResult.verified_count }} 个预测
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  setup() {
    const showVerifyPanel = ref(false)
    const selectedGroup = ref('')
    const selectedMatch = ref('')
    const selectedResult = ref('')
    const verifyResult = ref(null)
    
    const canVerify = computed(() => {
      return selectedGroup.value && selectedMatch.value !== '' && selectedResult.value
    })
    
    async function verifyMatch() {
      if (!canVerify.value) return
      
      const matchId = `${selectedGroup.value}_${selectedMatch.value}`
      
      try {
        const resp = await fetch(
          `/worldcup/api/user/verify/${matchId}?result=${selectedResult.value}`,
          { method: 'POST' }
        )
        const data = await resp.json()
        
        verifyResult.value = data
        
        // 3秒后清空结果
        setTimeout(() => {
          verifyResult.value = null
        }, 3000)
      } catch (e) {
        console.error('验证失败', e)
        verifyResult.value = { success: false, error: e.message }
      }
    }
    
    return {
      showVerifyPanel, selectedGroup, selectedMatch, selectedResult,
      verifyResult, canVerify, verifyMatch
    }
  }
}
</script>

<style scoped>
.verify-panel {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.verify-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.verify-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #666;
}

.toggle-btn {
  padding: 4px 12px;
  background: #f0f0f0;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
}

.verify-body {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.verify-row {
  display: flex;
  gap: 8px;
}

.verify-select {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.85rem;
  outline: none;
}

.verify-select:focus {
  border-color: #667eea;
}

.verify-btn {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
}

.verify-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.verify-result {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  text-align: center;
}

.result-badge {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.result-badge.success {
  color: #27ae60;
}

.result-badge.error {
  color: #e74c3c;
}

.result-detail {
  font-size: 0.85rem;
  color: #666;
}
</style>