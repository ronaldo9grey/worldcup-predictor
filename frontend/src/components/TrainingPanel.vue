<template>
  <div class="training-panel">
    <!-- 训练历史摘要 -->
    <div class="history-summary" v-if="trainingSummary.has_trained">
      <h3>📊 上次训练记录</h3>
      <div class="summary-cards">
        <div class="summary-card">
          <div class="summary-label">最佳模型</div>
          <div class="summary-value">{{ getModelName(trainingSummary.best_model) }}</div>
          <div class="summary-accuracy">{{ (trainingSummary.best_accuracy || 0).toFixed(1) }}%</div>
        </div>
        <div class="summary-card" v-for="(info, model) in trainingSummary.models" :key="model">
          <div class="summary-label">{{ getModelName(model) }}</div>
          <div class="summary-accuracy">{{ (info.accuracy * 100).toFixed(1) }}%</div>
          <div class="summary-time">{{ formatTime(info.training_time) }}</div>
        </div>
      </div>
    </div>

    <!-- 训练状态 -->
    <div class="training-status" v-if="isTraining">
      <h3>🔄 训练进行中</h3>
      <div class="progress-section">
        <div v-for="(progress, modelName) in trainingProgress" :key="modelName" class="progress-item">
          <div class="progress-header">
            <span class="model-icon">{{ getModelIcon(modelName) }}</span>
            <span class="model-name">{{ getModelName(modelName) }}</span>
            <span class="progress-text">{{ progress.current_epoch }}/{{ progress.total_epochs }}</span>
          </div>
          <div class="progress-bar-container">
            <div class="progress-bar" :style="{ width: (progress.current_epoch / progress.total_epochs * 100) + '%' }"></div>
          </div>
          <div class="progress-details">
            <span>Loss: {{ progress.current_loss.toFixed(4) }}</span>
            <span>Acc: {{ (progress.accuracy * 100).toFixed(1) }}%</span>
          </div>
          <div class="progress-message">{{ progress.message }}</div>
        </div>
      </div>
    </div>

    <!-- 训练控制 -->
    <div class="training-controls">
      <h3>🎮 训练控制</h3>
      <div class="control-buttons">
        <button class="btn-train" @click="startTraining" :disabled="isTraining">
          {{ isTraining ? '训练中...' : '🚀 开始训练' }}
        </button>
        <button class="btn-load" @click="loadModels" :disabled="isTraining">
          📂 加载模型
        </button>
        <button class="btn-refresh" @click="refreshStatus">
          🔄 刷新状态
        </button>
      </div>
      <div class="training-config">
        <label>
          <span>神经网络轮数:</span>
          <input type="number" v-model.number="nnEpochs" :disabled="isTraining" min="10" max="500">
        </label>
        <label>
          <span>随机森林树数:</span>
          <input type="number" v-model.number="rfEstimators" :disabled="isTraining" min="10" max="500">
        </label>
      </div>
    </div>

    <!-- 训练结果详情 -->
    <div class="training-results" v-if="trainingResults && Object.keys(trainingResults).length > 0">
      <h3>📋 训练结果详情</h3>
      
      <!-- 神经网络结果 -->
      <div v-if="trainingResults.neural_network" class="result-section">
        <div class="result-header" @click="toggleResult('nn')">
          <span class="model-icon">🧠</span>
          <span class="model-name">神经网络</span>
          <span class="result-accuracy">{{ (trainingResults.neural_network.validation_accuracy * 100).toFixed(1) }}%</span>
          <span class="toggle-icon">{{ expandedResults.nn ? '▼' : '▶' }}</span>
        </div>
        
        <div v-show="expandedResults.nn" class="result-body">
          <div class="result-info">
            <div class="info-row">
              <span class="info-label">训练轮数</span>
              <span class="info-value">{{ trainingResults.neural_network.epochs }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">最终损失</span>
              <span class="info-value">{{ trainingResults.neural_network.final_loss.toFixed(4) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">验证准确率</span>
              <span class="info-value highlight">{{ (trainingResults.neural_network.validation_accuracy * 100).toFixed(1) }}%</span>
            </div>
            <div class="info-row">
              <span class="info-label">训练时间</span>
              <span class="info-value">{{ trainingResults.neural_network.elapsed_seconds?.toFixed(1) || '-' }}秒</span>
            </div>
          </div>
          
          <!-- 训练历史图表 -->
          <div v-if="trainingResults.neural_network.training_history" class="training-chart">
            <h4>训练曲线</h4>
            <div class="chart-container">
              <div class="chart-row header">
                <span>Epoch</span>
                <span>Loss</span>
                <span>Accuracy</span>
              </div>
              <div v-for="log in trainingResults.neural_network.training_history" :key="log.epoch" class="chart-row">
                <span>{{ log.epoch }}</span>
                <span class="loss">{{ log.loss.toFixed(4) }}</span>
                <span class="acc">{{ (log.accuracy * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 随机森林结果 -->
      <div v-if="trainingResults.random_forest" class="result-section">
        <div class="result-header" @click="toggleResult('rf')">
          <span class="model-icon">🌲</span>
          <span class="model-name">随机森林</span>
          <span class="result-accuracy">{{ (trainingResults.random_forest.final_accuracy * 100).toFixed(1) }}%</span>
          <span class="toggle-icon">{{ expandedResults.rf ? '▼' : '▶' }}</span>
        </div>
        
        <div v-show="expandedResults.rf" class="result-body">
          <div class="result-info">
            <div class="info-row">
              <span class="info-label">决策树数量</span>
              <span class="info-value">{{ trainingResults.random_forest.epochs }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">准确率</span>
              <span class="info-value highlight">{{ (trainingResults.random_forest.final_accuracy * 100).toFixed(1) }}%</span>
            </div>
          </div>
          
          <!-- 特征重要性 -->
          <div v-if="trainingResults.random_forest.feature_importance" class="feature-importance">
            <h4>特征重要性</h4>
            <div class="importance-list">
              <div v-for="(value, name) in sortedFeatureImportance" :key="name" class="importance-item">
                <span class="feature-name">{{ name }}</span>
                <div class="importance-bar">
                  <div class="importance-fill" :style="{ width: (value * 100) + '%' }"></div>
                </div>
                <span class="importance-value">{{ (value * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 系统状态 -->
    <div class="system-status">
      <h3>⚙️ 系统状态</h3>
      <div class="status-grid">
        <div class="status-item">
          <span class="status-label">模型已加载</span>
          <span class="status-value" :class="{ active: systemStatus.models_loaded?.neural_network }">
            {{ systemStatus.models_loaded?.neural_network ? '✅' : '❌' }} 神经网络
          </span>
          <span class="status-value" :class="{ active: systemStatus.models_loaded?.random_forest }">
            {{ systemStatus.models_loaded?.random_forest ? '✅' : '❌' }} 随机森林
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">训练状态</span>
          <span class="status-value" :class="{ active: !systemStatus.is_training }">
            {{ systemStatus.is_training ? '🔄 训练中' : '✅ 就绪' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const API_BASE = '/worldcup/api/training'

// 状态
const trainingSummary = ref({ has_trained: false })
const trainingProgress = ref({})
const trainingResults = ref({})
const systemStatus = ref({ models_loaded: {}, is_training: false })
const isTraining = ref(false)

// 配置
const nnEpochs = ref(100)
const rfEstimators = ref(100)

// 展开状态
const expandedResults = ref({ nn: true, rf: true })

// 定时器
let progressTimer = null

// 模型名称映射
const modelNames = {
  neural_network: '神经网络',
  random_forest: '随机森林',
  bayesian: '贝叶斯模型'
}

const modelIcons = {
  neural_network: '🧠',
  random_forest: '🌲',
  bayesian: '🧮'
}

const getModelName = (key) => modelNames[key] || key
const getModelIcon = (key) => modelIcons[key] || '📊'

// 格式化时间
const formatTime = (isoString) => {
  if (!isoString) return '-'
  const date = new Date(isoString)
  return date.toLocaleString('zh-CN', { 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// 排序的特征重要性
const sortedFeatureImportance = computed(() => {
  const importance = trainingResults.value.random_forest?.feature_importance || {}
  return Object.fromEntries(
    Object.entries(importance).sort((a, b) => b[1] - a[1])
  )
})

// 切换结果展开
const toggleResult = (key) => {
  expandedResults.value[key] = !expandedResults.value[key]
}

// 加载训练摘要
const loadSummary = async () => {
  try {
    const res = await fetch(`${API_BASE}/summary`)
    trainingSummary.value = await res.json()
  } catch (e) {
    console.error('加载训练摘要失败', e)
  }
}

// 加载训练结果
const loadResults = async () => {
  try {
    const res = await fetch(`${API_BASE}/results`)
    const data = await res.json()
    trainingResults.value = data.results || {}
  } catch (e) {
    console.error('加载训练结果失败', e)
  }
}

// 加载系统状态
const loadStatus = async () => {
  try {
    const res = await fetch(`${API_BASE}/status`)
    systemStatus.value = await res.json()
    isTraining.value = systemStatus.value.is_training
  } catch (e) {
    console.error('加载系统状态失败', e)
  }
}

// 加载训练进度
const loadProgress = async () => {
  try {
    const res = await fetch(`${API_BASE}/progress`)
    const data = await res.json()
    trainingProgress.value = data.progress || {}
    
    // 检查是否还在训练
    const stillTraining = Object.values(data.progress).some(
      p => p && p.status === 'training'
    )
    
    if (!stillTraining && isTraining.value) {
      // 训练完成，停止轮询并加载结果
      isTraining.value = false
      clearInterval(progressTimer)
      progressTimer = null
      await loadResults()
      await loadSummary()
    }
  } catch (e) {
    console.error('加载训练进度失败', e)
  }
}

// 开始训练
const startTraining = async () => {
  if (isTraining.value) return
  
  isTraining.value = true
  
  try {
    const res = await fetch(`${API_BASE}/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nn_epochs: nnEpochs.value,
        rf_estimators: rfEstimators.value,
        train_all: true
      })
    })
    
    const data = await res.json()
    console.log('训练已启动:', data)
    
    // 开始轮询进度
    if (!progressTimer) {
      progressTimer = setInterval(loadProgress, 500)
    }
    
  } catch (e) {
    console.error('启动训练失败', e)
    isTraining.value = false
  }
}

// 加载模型
const loadModels = async () => {
  try {
    const res = await fetch(`${API_BASE}/load`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        models: ['neural_network', 'random_forest']
      })
    })
    
    const data = await res.json()
    console.log('模型加载结果:', data)
    await loadStatus()
    
  } catch (e) {
    console.error('加载模型失败', e)
  }
}

// 刷新状态
const refreshStatus = async () => {
  await Promise.all([
    loadSummary(),
    loadResults(),
    loadStatus()
  ])
}

// 初始化
onMounted(async () => {
  await refreshStatus()
  
  // 如果正在训练，开始轮询
  if (systemStatus.value.is_training) {
    isTraining.value = true
    progressTimer = setInterval(loadProgress, 500)
  }
})

onUnmounted(() => {
  if (progressTimer) {
    clearInterval(progressTimer)
  }
})
</script>

<style scoped>
.training-panel {
  padding: 16px;
  max-width: 900px;
  margin: 0 auto;
}

h3 {
  color: #1a472a;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e8f5e9;
  font-size: 16px;
}

/* 历史摘要 */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.summary-card {
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  padding: 12px;
  border-radius: 10px;
  text-align: center;
}

.summary-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 14px;
  font-weight: bold;
  color: #1b5e20;
}

.summary-accuracy {
  font-size: 20px;
  font-weight: bold;
  color: #2e7d32;
  margin-top: 4px;
}

.summary-time {
  font-size: 11px;
  color: #888;
  margin-top: 4px;
}

/* 训练状态 */
.progress-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.progress-item {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 8px;
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.model-icon {
  font-size: 20px;
}

.model-name {
  font-weight: bold;
  flex: 1;
}

.progress-text {
  font-size: 12px;
  color: #666;
}

.progress-bar-container {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4caf50 0%, #8bc34a 100%);
  transition: width 0.3s;
}

.progress-details {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}

.progress-message {
  font-size: 12px;
  color: #888;
}

/* 训练控制 */
.control-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.btn-train, .btn-load, .btn-refresh {
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-train {
  background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
  color: white;
}

.btn-train:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
}

.btn-train:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-load, .btn-refresh {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
}

.btn-load:hover, .btn-refresh:hover {
  background: #e8f5e9;
}

.training-config {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.training-config label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.training-config input {
  width: 80px;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

/* 训练结果 */
.result-section {
  background: white;
  border-radius: 10px;
  margin-bottom: 12px;
  border: 1px solid #e0e0e0;
  overflow: hidden;
}

.result-header {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f5f5f5;
  cursor: pointer;
  gap: 12px;
}

.result-header:hover {
  background: #e8f5e9;
}

.result-accuracy {
  background: #4caf50;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: bold;
}

.toggle-icon {
  margin-left: auto;
  color: #666;
}

.result-body {
  padding: 12px;
}

.result-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 6px;
}

.info-label {
  color: #666;
  font-size: 13px;
}

.info-value {
  font-weight: 500;
  color: #333;
}

.info-value.highlight {
  color: #2e7d32;
  font-weight: bold;
}

/* 训练图表 */
.training-chart {
  margin-top: 12px;
}

.training-chart h4 {
  color: #1a472a;
  font-size: 13px;
  margin-bottom: 8px;
}

.chart-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.chart-row {
  display: grid;
  grid-template-columns: 50px 80px 80px;
  gap: 8px;
  padding: 6px 0;
  font-size: 12px;
}

.chart-row.header {
  font-weight: bold;
  color: #666;
  border-bottom: 1px solid #ddd;
}

.chart-row .loss {
  color: #f44336;
}

.chart-row .acc {
  color: #4caf50;
  font-weight: 500;
}

/* 特征重要性 */
.feature-importance {
  margin-top: 12px;
}

.feature-importance h4 {
  color: #1a472a;
  font-size: 13px;
  margin-bottom: 8px;
}

.importance-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.importance-item {
  display: grid;
  grid-template-columns: 120px 1fr 50px;
  gap: 8px;
  align-items: center;
}

.feature-name {
  font-size: 12px;
  color: #333;
}

.importance-bar {
  height: 20px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.importance-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50 0%, #8bc34a 100%);
  border-radius: 4px;
  transition: width 0.5s;
}

.importance-value {
  font-size: 12px;
  color: #666;
  text-align: right;
}

/* 系统状态 */
.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.status-item {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 8px;
}

.status-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.status-value {
  display: inline-block;
  font-size: 13px;
  color: #333;
  margin-right: 12px;
}

.status-value.active {
  color: #2e7d32;
}

@media (max-width: 600px) {
  .training-panel {
    padding: 12px;
  }
  
  .control-buttons {
    flex-direction: column;
  }
  
  .btn-train, .btn-load, .btn-refresh {
    width: 100%;
  }
  
  .importance-item {
    grid-template-columns: 100px 1fr 40px;
  }
}
</style>
