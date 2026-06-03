<template>
  <div class="model-comparison">
    <!-- Toast提示 -->
    <div v-if="toastMessage" :class="['toast', toastType]">
      {{ toastMessage }}
    </div>
    
    <!-- 贝叶斯详情弹窗 -->
    <div v-if="showBayesianDetail" class="dialog-overlay" @click.self="showBayesianDetail = false">
      <div class="bayesian-dialog">
        <div class="training-header">
          <div class="training-title">🧮 贝叶斯模型详解</div>
          <button @click="showBayesianDetail = false" class="close-btn">✕</button>
        </div>
        
        <div class="dialog-body">
          <div class="bayesian-intro">
            <p>贝叶斯模型<strong>不需要传统训练</strong>，而是基于历史先验概率进行推断</p>
            <p class="intro-note">核心公式：后验概率 = 0.7×模型预测 + 0.3×历史先验</p>
          </div>
          
          <!-- 5步过程 -->
          <div class="process-steps">
            <h4>贝叶斯推断过程（5步）</h4>
            
            <div class="step-item">
              <span class="step-num">1</span>
              <div class="step-content">
                <span class="step-action">收集历史先验概率</span>
                <span class="step-detail">从128场历史世界杯比赛统计各结果频率</span>
              </div>
            </div>
            
            <div class="step-item">
              <span class="step-num">2</span>
              <div class="step-content">
                <span class="step-action">计算基准胜率</span>
                <span class="step-detail">主胜率: 47%, 平局率: 26%, 客胜率: 27%</span>
              </div>
            </div>
            
            <div class="step-item">
              <span class="step-num">3</span>
              <div class="step-content">
                <span class="step-action">建立条件概率表</span>
                <span class="step-detail">根据Elo差距、排名差距等因子建立P(结果|条件)</span>
              </div>
            </div>
            
            <div class="step-item">
              <span class="step-num">4</span>
              <div class="step-content">
                <span class="step-action">应用贝叶斯公式</span>
                <span class="step-detail">后验概率 = 先验概率 × 似然函数</span>
              </div>
            </div>
            
            <div class="step-item">
              <span class="step-num">5</span>
              <div class="step-content">
                <span class="step-action">计算置信区间</span>
                <span class="step-detail">使用Beta分布计算95%置信区间</span>
              </div>
            </div>
          </div>
          
          <!-- 示例演示 -->
          <div class="example-demo">
            <h4>📊 示例：阿根廷 vs 法国（2022决赛）</h4>
            
            <div class="demo-row">
              <div class="demo-col">
                <div class="demo-header">先验概率（历史统计）</div>
                <div class="demo-values">
                  <div>主胜: <span class="val">50%</span></div>
                  <div>平局: <span class="val">25%</span></div>
                  <div>客胜: <span class="val">25%</span></div>
                </div>
                <div class="demo-note">来源: 2018+2022决赛统计</div>
              </div>
              
              <div class="demo-col">
                <div class="demo-header">模型预测（权重计算）</div>
                <div class="demo-values">
                  <div>主胜: <span class="val">43%</span></div>
                  <div>平局: <span class="val">17%</span></div>
                  <div>客胜: <span class="val">40%</span></div>
                </div>
              </div>
            </div>
            
            <div class="formula-box">
              <div class="formula">后验主胜 = 0.7 × 43% + 0.3 × 50% = <strong>45%</strong></div>
            </div>
            
            <div class="result-box">
              <div class="result-header">后验概率（最终输出）</div>
              <div class="result-values">
                <span>阿根廷胜 <strong>45%</strong></span>
                <span>平局 <strong>20%</strong></span>
                <span>法国胜 <strong>35%</strong></span>
              </div>
              <div class="confidence">置信区间: [38%, 52%] → 置信度: 中等</div>
            </div>
          </div>
          
          <!-- 关键说明 -->
          <div class="key-notes">
            <div class="note-title">💡 关键说明</div>
            <div class="note-item">贝叶斯模型无需训练迭代，直接使用历史统计作为先验</div>
            <div class="note-item">结合模型预测，输出更可靠的后验概率和置信区间</div>
            <div class="note-item">对极端预测有"修正"作用，防止过度自信</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 神经网络详情弹窗 -->
    <div v-if="showNeuralNetworkDetail" class="dialog-overlay" @click.self="showNeuralNetworkDetail = false">
      <div class="nn-dialog">
        <div class="training-header">
          <div class="training-title">🧠 神经网络详解</div>
          <button @click="showNeuralNetworkDetail = false" class="close-btn">✕</button>
        </div>
        <div class="dialog-body">
          <div class="bayesian-intro nn-intro">
            <p>神经网络<strong>需要训练</strong>，通过反向传播优化权重</p>
            <p class="intro-note">架构：输入层(13维) → 隐藏层[64,32,16] → 输出层(3类)</p>
          </div>
          <div class="nn-architecture">
            <div class="layer">输入层: 13个特征</div>
            <div class="layer hidden">隐藏层1: 64神经元</div>
            <div class="layer hidden">隐藏层2: 32神经元</div>
            <div class="layer hidden">隐藏层3: 16神经元</div>
            <div class="layer output">输出层: 3类</div>
          </div>
          <div class="training-info">
            <h4>训练过程</h4>
            <div class="step-list">
              <div class="step">前向传播 → 计算预测</div>
              <div class="step">计算损失 → 交叉熵</div>
              <div class="step">反向传播 → 计算梯度</div>
              <div class="step">更新权重 → 梯度下降</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 随机森林详情弹窗 -->
    <div v-if="showRandomForestDetail" class="dialog-overlay" @click.self="showRandomForestDetail = false">
      <div class="rf-dialog">
        <div class="training-header">
          <div class="training-title">🌲 随机森林详解</div>
          <button @click="showRandomForestDetail = false" class="close-btn">✕</button>
        </div>
        <div class="dialog-body">
          <div class="bayesian-intro rf-intro">
            <p>随机森林<strong>需要训练</strong>，通过Bootstrap采样构建决策树</p>
            <p class="intro-note">架构：100棵决策树 + 多数投票</p>
          </div>
          <div class="rf-architecture">
            <div class="tree-count">决策树: 100棵</div>
            <div class="tree-visual">
              <span>🌳</span><span>🌳</span><span>🌳</span><span>...</span><span>100棵</span>
            </div>
          </div>
          <div class="training-info">
            <h4>训练过程</h4>
            <div class="step-list">
              <div class="step">Bootstrap采样</div>
              <div class="step">构建决策树</div>
              <div class="step">重复100次</div>
              <div class="step">多数投票预测</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 上次训练记录 -->
    <div class="history-summary" v-if="trainingHistory.has_trained">
      <h3>📊 上次训练记录</h3>
      <div class="summary-info">
        <span class="best-model">最佳模型: {{ getModelName(trainingHistory.best_model) }}</span>
        <span class="best-accuracy">准确率: {{ ((trainingHistory.best_accuracy || 0) * 100).toFixed(1) }}%</span>
      </div>
    </div>

    <!-- 模型状态卡片 -->
    <div class="model-status-section">
      <h3>🤖 模型状态</h3>
      <div class="model-cards">
        <div class="model-card" :class="{ active: modelsStatus.bayesian?.status === 'ready' }">
          <div class="model-icon">🧮</div>
          <div class="model-info">
            <div class="model-name">贝叶斯模型</div>
            <div class="model-status">{{ modelsStatus.bayesian?.status === 'ready' ? '✅ 就绪' : '⏳ 初始化中' }}</div>
            <div class="model-accuracy-display">
              准确率: <strong>{{ trainingHistory.models?.bayesian ? (trainingHistory.models.bayesian.accuracy * 100).toFixed(1) : '53.1' }}%</strong>
            </div>
          </div>
          <div class="model-weight">权重: {{ (modelWeights.bayesian * 100).toFixed(0) }}%</div>
          <button class="detail-btn" @click="showBayesianDetail = true">📖 详情</button>
        </div>
        
        <div class="model-card" :class="{ active: modelsStatus.neural_network?.status === 'trained' }">
          <div class="model-icon">🧠</div>
          <div class="model-info">
            <div class="model-name">神经网络</div>
            <div class="model-status">{{ modelsStatus.neural_network?.status === 'trained' ? '✅ 已训练' : '⏳ 未训练' }}</div>
            <div class="model-accuracy-display">
              准确率: <strong>{{ trainingHistory.models?.neural_network ? (trainingHistory.models.neural_network.accuracy * 100).toFixed(1) : '-' }}%</strong>
            </div>
          </div>
          <div class="model-weight">权重: {{ (modelWeights.neural_network * 100).toFixed(0) }}%</div>
          <button class="detail-btn" @click="showNeuralNetworkDetail = true">📖 详情</button>
        </div>
        
        <div class="model-card" :class="{ active: modelsStatus.random_forest?.status?.includes('trained') }">
          <div class="model-icon">🌲</div>
          <div class="model-info">
            <div class="model-name">随机森林</div>
            <div class="model-status">{{ modelsStatus.random_forest?.status?.includes('trained') ? '✅ 已训练' : '⏳ 未训练' }}</div>
            <div class="model-accuracy-display">
              准确率: <strong>{{ trainingHistory.models?.random_forest ? (trainingHistory.models.random_forest.accuracy * 100).toFixed(1) : '-' }}%</strong>
            </div>
          </div>
          <div class="model-weight">权重: {{ (modelWeights.random_forest * 100).toFixed(0) }}%</div>
          <button class="detail-btn" @click="showRandomForestDetail = true">📖 详情</button>
        </div>
      </div>
      
      <div class="action-buttons">
        <button class="btn-primary" @click="startTraining" :disabled="isTraining" :class="{ 'btn-disabled': isTraining }">
          {{ isTraining ? '⏳ 训练中...' : '🚀 训练模型' }}
        </button>
        <button class="btn-secondary" @click="loadSavedModels" :disabled="isTraining">
          📂 加载模型
        </button>
        <span v-if="trainingHistory.has_trained" class="training-hint">
          ✅ 已有训练记录 ({{ trainingHistory.training_count || 0 }}次)
        </span>
      </div>
    </div>
    
    <!-- 实时训练进度 -->
    <div class="training-progress-section" v-if="isTraining && Object.keys(trainingProgress).length > 0">
      <h3>🔄 训练进度</h3>
      <div class="progress-cards">
        <div v-for="(progress, modelName) in trainingProgress" :key="modelName" class="progress-card">
          <div class="progress-header">
            <span class="model-icon">{{ getModelIcon(modelName) }}</span>
            <span class="model-name">{{ getModelName(modelName) }}</span>
            <span class="progress-text">{{ progress.current_epoch }}/{{ progress.total_epochs }}</span>
          </div>
          <div class="progress-bar-container">
            <div class="progress-bar" :style="{ width: getProgressPercent(progress) + '%' }"></div>
          </div>
          <div class="progress-details">
            <span>Loss: {{ (progress.current_loss || 0).toFixed(4) }}</span>
            <span>Acc: {{ ((progress.accuracy || 0) * 100).toFixed(1) }}%</span>
          </div>
          <div class="progress-message">{{ progress.message }}</div>
        </div>
      </div>
    </div>
    
    <!-- 训练过程详情 -->
    <div v-if="Object.keys(trainingResults).length > 0" class="training-process-section">
      <h3>🔬 训练过程详情</h3>
      
      <!-- 各模型训练结果 -->
      <div v-for="(result, key) in trainingResults" :key="key" class="model-training-detail">
        <div class="model-header" @click="toggleModel(key)">
          <span class="model-icon">{{ getModelIcon(key) }}</span>
          <span class="model-title">{{ getModelName(key) }}</span>
          <span class="model-accuracy-badge">{{ ((result.validation_accuracy || result.final_accuracy || 0) * 100).toFixed(1) }}%</span>
          <span class="toggle-icon">{{ expandedModels[key] ? '▼' : '▶' }}</span>
        </div>
        
        <div v-show="expandedModels[key]" class="model-content">
          <!-- 基本信息 -->
          <div class="info-grid">
            <!-- 神经网络特有参数 -->
            <template v-if="key === 'neural_network'">
              <div class="info-item">
                <span class="label">训练轮数</span>
                <span class="value">{{ result.epochs || 100 }}</span>
              </div>
              <div class="info-item">
                <span class="label">最终Loss</span>
                <span class="value">{{ (result.final_loss || 0).toFixed(4) }}</span>
              </div>
              <div class="info-item">
                <span class="label">验证准确率</span>
                <span class="value highlight">{{ ((result.validation_accuracy || result.final_accuracy || 0) * 100).toFixed(1) }}%</span>
              </div>
              <div class="info-item">
                <span class="label">训练时间</span>
                <span class="value">{{ result.training_time || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">优化器</span>
                <span class="value">{{ result.optimizer || 'Adam' }}</span>
              </div>
              <div class="info-item">
                <span class="label">学习率</span>
                <span class="value">{{ result.learning_rate || 0.001 }}</span>
              </div>
              <div class="info-item">
                <span class="label">批次大小</span>
                <span class="value">{{ result.batch_size || 32 }}</span>
              </div>
              <div class="info-item">
                <span class="label">激活函数</span>
                <span class="value">{{ result.activation || 'ReLU' }}</span>
              </div>
              <div class="info-item">
                <span class="label">Dropout</span>
                <span class="value">{{ result.dropout || 0.3 }}</span>
              </div>
              <div class="info-item full-width">
                <span class="label">网络架构</span>
                <span class="value code">{{ result.architecture || '输入层(13) → 隐藏层[64,32,16] → 输出层(3)' }}</span>
              </div>
            </template>
            
            <!-- 随机森林特有参数 -->
            <template v-else-if="key === 'random_forest'">
              <div class="info-item">
                <span class="label">决策树数量</span>
                <span class="value">{{ result.n_trees || 100 }}</span>
              </div>
              <div class="info-item">
                <span class="label">验证准确率</span>
                <span class="value highlight">{{ ((result.validation_accuracy || result.final_accuracy || 0) * 100).toFixed(1) }}%</span>
              </div>
              <div class="info-item">
                <span class="label">训练时间</span>
                <span class="value">{{ result.training_time || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">最大深度</span>
                <span class="value">{{ result.max_depth || 10 }}</span>
              </div>
              <div class="info-item">
                <span class="label">最小分裂样本</span>
                <span class="value">{{ result.min_samples_split || 5 }}</span>
              </div>
              <div class="info-item">
                <span class="label">最小叶节点样本</span>
                <span class="value">{{ result.min_samples_leaf || 2 }}</span>
              </div>
              <div class="info-item">
                <span class="label">最大特征数</span>
                <span class="value">{{ result.max_features || 'sqrt' }}</span>
              </div>
              <div class="info-item">
                <span class="label">Bootstrap采样</span>
                <span class="value">{{ result.bootstrap ? '是' : '否' }}</span>
              </div>
            </template>
          </div>
          
          <!-- 训练曲线（神经网络） -->
          <div v-if="result.training_history && result.training_history.length > 0" class="training-logs">
            <h4>训练曲线</h4>
            <div class="logs-chart">
              <div class="log-header">
                <span>Epoch</span>
                <span>Loss</span>
                <span>Accuracy</span>
              </div>
              <div v-for="log in result.training_history" :key="log.epoch" class="log-row">
                <span>{{ log.epoch }}</span>
                <span class="log-loss">{{ log.loss.toFixed(4) }}</span>
                <span class="log-acc">{{ (log.accuracy * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
          
          <!-- 特征重要性 -->
          <div v-if="result.feature_importance" class="model-feature-importance">
            <h4>特征重要性</h4>
            <div class="importance-bars">
              <div v-for="(value, name) in getSortedImportance(result.feature_importance)" :key="name" class="importance-item">
                <span class="feature-name">{{ name }}</span>
                <div class="importance-bar">
                  <div class="importance-fill" :style="{ width: (value * 100) + '%' }"></div>
                </div>
                <span class="importance-value">{{ (value * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
          
          <!-- 模型状态 -->
          <div class="status-badge" :class="result.status">
            {{ result.message || '训练完成' }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 在线学习状态 -->
    <div class="learning-section">
      <div class="learning-header">
        <h3>📚 在线学习</h3>
        <span class="learning-badge" :class="{ active: learningStats.total_events > 0 }">
          {{ learningStats.total_events > 0 ? '学习中' : '待激活' }}
        </span>
      </div>
      
      <!-- 学习进度可视化 -->
      <div class="learning-visual">
        <div class="progress-ring-wrap">
          <svg class="progress-ring" width="120" height="120">
            <circle class="progress-bg" cx="60" cy="60" r="52" />
            <circle class="progress-fill" 
                    cx="60" cy="60" r="52"
                    :style="{strokeDashoffset: 326 - (326 * (learningStats.recent_accuracy || 0))}"
                    :class="{'high': learningStats.recent_accuracy >= 0.7, 'medium': learningStats.recent_accuracy >= 0.5 && learningStats.recent_accuracy < 0.7, 'low': learningStats.recent_accuracy < 0.5}" />
          </svg>
          <div class="progress-text">
            <span class="progress-value">{{ ((learningStats.recent_accuracy || 0) * 100).toFixed(0) }}</span>
            <span class="progress-unit">%</span>
            <span class="progress-label">准确率</span>
          </div>
        </div>
        
        <div class="learning-metrics">
          <div class="metric-row">
            <span class="metric-icon">📊</span>
            <span class="metric-label">学习事件</span>
            <span class="metric-bar">
              <span class="metric-fill" :style="{width: Math.min(100, (learningStats.total_events || 0) * 2) + '%'}"></span>
            </span>
            <span class="metric-value">{{ learningStats.total_events || 0 }}</span>
          </div>
          
          <div class="metric-row">
            <span class="metric-icon">⚡</span>
            <span class="metric-label">学习速率</span>
            <span class="metric-bar">
              <span class="metric-fill rate" :style="{width: ((learningStats.learning_rate || 0.1) * 500) + '%'}"></span>
            </span>
            <span class="metric-value">{{ (learningStats.learning_rate || 0.1).toFixed(3) }}</span>
          </div>
          
          <div class="metric-row">
            <span class="metric-icon">🎯</span>
            <span class="metric-label">权重更新</span>
            <span class="metric-bar">
              <span class="metric-fill update" :style="{width: ((learningStats.weight_updates || 0) / 10) + '%'}"></span>
            </span>
            <span class="metric-value">{{ learningStats.weight_updates || 0 }}次</span>
          </div>
          
          <div class="metric-row">
            <span class="metric-icon">🌊</span>
            <span class="metric-label">概念漂移</span>
            <span :class="['metric-status', driftWarning ? 'warning' : 'normal']">
              {{ driftWarning ? '⚠️ 检测到' : '✅ 正常' }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- 学习历史图表 -->
      <div v-if="learningHistory.length > 0" class="learning-chart">
        <h4>📈 学习趋势</h4>
        <div class="chart-area">
          <svg width="100%" height="120" class="trend-chart">
            <defs>
              <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#667eea;stop-opacity:0.3" />
                <stop offset="100%" style="stop-color:#667eea;stop-opacity:0" />
              </linearGradient>
            </defs>
            <!-- 网格线 -->
            <line x1="40" y1="20" x2="100%" y2="20" stroke="#eee" stroke-dasharray="3,3" />
            <line x1="40" y1="60" x2="100%" y2="60" stroke="#eee" stroke-dasharray="3,3" />
            <line x1="40" y1="100" x2="100%" y2="100" stroke="#eee" stroke-dasharray="3,3" />
            
            <!-- 填充区域 -->
            <path :d="chartAreaPath" fill="url(#lineGradient)" />
            <!-- 折线 -->
            <path :d="chartLinePath" fill="none" stroke="#667eea" stroke-width="2" stroke-linecap="round" />
            <!-- 数据点 -->
            <circle v-for="(point, idx) in chartPoints" :key="idx" 
                    :cx="point.x" :cy="point.y" r="4" fill="#667eea" />
          </svg>
          <div class="chart-labels">
            <span>100%</span>
            <span>50%</span>
            <span>0%</span>
          </div>
        </div>
      </div>
      
      <!-- 快捷操作 -->
      <div class="learning-actions">
        <button class="action-btn" @click="resetLearning" :disabled="!learningStats.total_events">
          🔄 重置学习
        </button>
        <button class="action-btn primary" @click="exportLearning">
          📥 导出数据
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive, computed } from 'vue'

const API_BASE = '/worldcup/api'

// 状态
const modelsStatus = ref({})
const modelWeights = ref({ bayesian: 0.4, neural_network: 0.3, random_forest: 0.3 })
const trainingHistory = ref({ has_trained: false })
const trainingResults = ref({})
const isTraining = ref(false)
const trainingProgress = ref({})
const trainingProcess = ref(null)
const expandedModels = reactive({ bayesian: true, neural_network: true, random_forest: true })
const toastMessage = ref('')
const toastType = ref('success')
const showBayesianDetail = ref(false)  // 贝叶斯详情弹窗
const showNeuralNetworkDetail = ref(false)  // 神经网络详情弹窗
const showRandomForestDetail = ref(false)  // 随机森林详情弹窗

const learningStats = ref({})
const driftWarning = ref(false)
const learningHistory = ref([])

// 计算图表路径
const chartPoints = computed(() => {
  if (learningHistory.value.length === 0) return []
  const data = learningHistory.value.slice(-10) // 最近10个点
  const width = 400
  const startX = 50
  const stepX = (width - startX) / Math.max(1, data.length - 1)
  
  return data.map((item, idx) => ({
    x: startX + idx * stepX,
    y: 100 - (item.accuracy || 0) * 100, // SVG坐标系Y轴反向
    accuracy: item.accuracy
  }))
})

const chartLinePath = computed(() => {
  if (chartPoints.value.length === 0) return ''
  return chartPoints.value.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
})

const chartAreaPath = computed(() => {
  if (chartPoints.value.length === 0) return ''
  const points = chartPoints.value
  const lastX = points[points.length - 1].x
  const linePath = points.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
  return `${linePath} L ${lastX} 100 L ${points[0].x} 100 Z`
})

// 导入computed已在上行完成

let progressTimer = null

// 模型名称
const modelNames = {
  bayesian: '贝叶斯模型',
  neural_network: '神经网络',
  random_forest: '随机森林'
}

const modelIcons = {
  bayesian: '🧮',
  neural_network: '🧠',
  random_forest: '🌲'
}

const getModelName = (key) => modelNames[key] || key
const getModelIcon = (key) => modelIcons[key] || '📊'

// 格式化时间
const formatTime = (isoString) => {
  if (!isoString) return '-'
  const date = new Date(isoString)
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const getProgressPercent = (progress) => {
  if (!progress.total_epochs) return 0
  return (progress.current_epoch / progress.total_epochs * 100)
}

const getSortedImportance = (importance) => {
  return Object.fromEntries(
    Object.entries(importance).sort((a, b) => b[1] - a[1])
  )
}

const toggleModel = (key) => {
  expandedModels[key] = !expandedModels[key]
}


// 显示提示消息
const showToast = (msg, type = 'success') => {
  toastMessage.value = msg
  toastType.value = type
  setTimeout(() => { toastMessage.value = '' }, 3000)
}

// 加载模型状态
const loadModelsStatus = async () => {
  try {
    const res = await fetch(`${API_BASE}/models/status`)
    const data = await res.json()
    modelsStatus.value = data
    if (data.ensemble?.weights) {
      modelWeights.value = data.ensemble.weights
    }
    
    // 加载学习数据
    const learningRes = await fetch(`${API_BASE}/models/learning/status`)
    if (learningRes.ok) {
      const learningData = await learningRes.json()
      learningStats.value = learningData
      learningHistory.value = learningData.history || []
      driftWarning.value = learningData.drift_detected || false
    }
  } catch (e) {
    console.error('加载模型状态失败', e)
  }
}

const resetLearning = async () => {
  if (!confirm('确定要重置学习数据吗？所有学习历史将被清除。')) return
  
  try {
    await fetch(`${API_BASE}/models/learning/reset`, { method: 'POST' })
    learningStats.value = {}
    learningHistory.value = []
    driftWarning.value = false
    showToast('学习数据已重置', 'success')
  } catch (e) {
    console.error(e)
    showToast('重置失败', 'error')
  }
}

const exportLearning = () => {
  const data = {
    stats: learningStats.value,
    history: learningHistory.value,
    exportTime: new Date().toISOString()
  }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `learning-data-${new Date().toISOString().slice(0,10)}.json`
  a.click()
  URL.revokeObjectURL(url)
  showToast('数据已导出', 'success')
}

// 加载训练历史
const loadTrainingHistory = async () => {
  try {
    const res = await fetch(`${API_BASE}/training/summary`)
    const data = await res.json()
    trainingHistory.value = data
    
    // 同时加载详细训练结果
    const resultsRes = await fetch(`${API_BASE}/training/results`)
    const resultsData = await resultsRes.json()
    trainingResults.value = resultsData.results || {}
  } catch (e) {
    console.error('加载训练历史失败', e)
  }
}

// 加载训练进度
const loadProgress = async () => {
  try {
    const res = await fetch(`${API_BASE}/training/progress`)
    const data = await res.json()
    trainingProgress.value = data.progress || {}
    
    // 检查是否还在训练
    const stillTraining = Object.values(data.progress).some(
      p => p && p.status === 'training'
    )
    
    if (!stillTraining && isTraining.value) {
      isTraining.value = false
      clearInterval(progressTimer)
      progressTimer = null
      await loadTrainingHistory()
      await loadModelsStatus()
      showToast('训练完成！', 'success')
    }
  } catch (e) {
    console.error('加载进度失败', e)
  }
}

// 开始训练
const startTraining = async () => {
  if (isTraining.value) {
    showToast('训练正在进行中...', 'warning')
    return
  }
  
  isTraining.value = true
  showToast('开始训练...', 'info')
  
  try {
    const res = await fetch(`${API_BASE}/training/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ train_all: true })
    })
    
    const data = await res.json()
    
    if (!data.success) {
      showToast(data.message || '训练启动失败', 'warning')
      isTraining.value = false
      return
    }
    
    console.log('训练已启动:', data)
    
    if (!progressTimer) {
      progressTimer = setInterval(loadProgress, 500)
    }
  } catch (e) {
    console.error('启动训练失败', e)
    isTraining.value = false
    showToast('训练启动失败', 'error')
  }
}

// 加载已保存模型
const loadSavedModels = async () => {
  try {
    const res = await fetch(`${API_BASE}/training/load`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ models: ['neural_network', 'random_forest'] })
    })
    const data = await res.json()
    console.log('模型加载结果:', data)
    await loadModelsStatus()
    await loadTrainingHistory()
    showToast(data.message || '模型加载成功', 'success')
  } catch (e) {
    console.error('加载模型失败', e)
    showToast('模型加载失败', 'error')
  }
}

// 自动调整权重
// 加载小组比赛

// 加载比赛预测

// 加载学习统计
const loadLearningStats = async () => {
  try {
    const res = await fetch(`${API_BASE}/learning/stats`)
    learningStats.value = await res.json()
  } catch (e) {
    console.error('加载学习统计失败', e)
  }
}

// 初始化
onMounted(async () => {
  await loadModelsStatus()
  await loadTrainingHistory()
  await loadLearningStats()
  
  // 如果正在训练，开始轮询
  const statusRes = await fetch(`${API_BASE}/training/status`)
  const statusData = await statusRes.json()
  if (statusData.is_training) {
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
.model-comparison {
  padding: 16px;
  max-width: 900px;
  margin: 0 auto;
}

/* Toast提示 */
.toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  z-index: 9999;
  animation: fadeIn 0.3s;
}
.toast.success { background: #4caf50; }
.toast.error { background: #f44336; }
.toast.info { background: #2196f3; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-50%) translateY(-10px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

h3 {
  color: #1a472a;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e8f5e9;
  font-size: 16px;
}

/* 上次训练记录 */
.history-summary {
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  padding: 12px;
  border-radius: 10px;
  margin-bottom: 16px;
}

.summary-info {
  display: flex;
  gap: 20px;
  margin-top: 8px;
}

.best-model {
  font-weight: bold;
  color: #1b5e20;
}

.best-accuracy {
  color: #2e7d32;
}

/* 模型状态卡片 */
.model-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.model-card {
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  border-radius: 12px;
  padding: 14px;
  padding-top: 40px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  border: 2px solid #4caf50;
  transition: all 0.3s;
  position: relative;
}

.model-card.active {
  border-color: #4caf50;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
}

.model-icon {
  font-size: 24px;
}

.model-name {
  font-weight: bold;
  color: #1b5e20;
  font-size: 14px;
}

.model-status {
  font-size: 13px;
  color: #666;
}

.model-accuracy-display {
  font-size: 12px;
  color: #2e7d32;
  margin-top: 4px;
}

.model-accuracy-display strong {
  color: #1b5e20;
}

.model-weight {
  font-size: 11px;
  background: #1b5e20;
  color: white;
  padding: 3px 8px;
  border-radius: 10px;
  align-self: flex-start;
}

/* 按钮区域 */
.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 16px;
}

.training-hint {
  font-size: 0.85rem;
  color: #4caf50;
  margin-left: 8px;
}

.btn-disabled {
  opacity: 0.6;
  cursor: not-allowed !important;
}

.btn-primary, .btn-secondary {
  padding: 10px 18px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
}

.btn-secondary:hover {
  background: #e8f5e9;
}

/* 实时训练进度 */
.training-progress-section {
  margin-top: 16px;
  background: #fff3e0;
  border-radius: 12px;
  padding: 16px;
  border: 2px solid #ff9800;
}

.progress-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.progress-card {
  background: white;
  padding: 12px;
  border-radius: 8px;
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.progress-text {
  font-size: 12px;
  color: #666;
  margin-left: auto;
}

.progress-bar-container {
  height: 10px;
  background: #e0e0e0;
  border-radius: 5px;
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
  color: #2e7d32;
}

/* 训练过程详情 */
.training-process-section {
  margin-top: 20px;
  background: #fafafa;
  border-radius: 12px;
  padding: 16px;
}

.data-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}

.overview-item {
  background: white;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.overview-item .label {
  display: block;
  font-size: 11px;
  color: #666;
  margin-bottom: 4px;
}

.overview-item .value {
  font-size: 15px;
  font-weight: bold;
  color: #1b5e20;
}

/* 模型训练详情 */
.model-training-detail {
  background: white;
  border-radius: 10px;
  margin-bottom: 10px;
  border: 1px solid #e0e0e0;
  overflow: hidden;
}

.model-header {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f5f5f5;
  cursor: pointer;
  gap: 10px;
}

.model-header:hover {
  background: #e8f5e9;
}

.model-title {
  flex: 1;
  font-weight: bold;
  color: #1b5e20;
  font-size: 14px;
}

.model-accuracy-badge {
  background: #4caf50;
  color: white;
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 13px;
}

.toggle-icon {
  color: #666;
}

.model-content {
  padding: 12px;
}

/* 基本信息 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 8px;
  margin-bottom: 12px;
}

.info-item {
  background: #f5f5f5;
  padding: 8px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
}

.info-item .label {
  font-size: 11px;
  color: #666;
  margin-bottom: 4px;
}

.info-item .value {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.info-item .value.highlight {
  color: #2e7d32;
  font-weight: bold;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item .value.code {
  font-family: monospace;
  font-size: 12px;
  color: #667eea;
}

/* 训练曲线 */
.training-logs {
  margin-top: 12px;
}

.training-logs h4 {
  color: #2d5a3d;
  font-size: 13px;
  margin-bottom: 8px;
}

.logs-chart {
  background: #fafafa;
  border-radius: 8px;
  padding: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.log-header, .log-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  padding: 6px 8px;
  font-size: 12px;
}

.log-header {
  background: #e8f5e9;
  font-weight: bold;
  color: #2d5a3d;
  border-radius: 4px;
}

.log-row {
  border-bottom: 1px solid #eee;
}

.log-loss { color: #f44336; }
.log-acc { color: #4caf50; font-weight: 500; }

/* 状态徽章 */
.status-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  margin-top: 12px;
}

.status-badge.completed {
  background: #e8f5e9;
  color: #2e7d32;
}

/* 训练步骤 */
.process-steps h4, .hyperparameters h4, .model-feature-importance h4 {
  color: #2d5a3d;
  font-size: 13px;
  margin-bottom: 10px;
}

.step-item {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
  align-items: flex-start;
}

.step-number {
  background: #4caf50;
  color: white;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: bold;
  flex-shrink: 0;
}

.step-action {
  font-weight: 500;
  color: #333;
  font-size: 13px;
}

.step-detail {
  font-size: 12px;
  color: #666;
}

/* 参数 */
.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 8px;
}

.param-item {
  background: #e8f5e9;
  padding: 6px 10px;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.param-name {
  color: #666;
}

.param-value {
  font-weight: 500;
  color: #1b5e20;
}

/* 特征重要性 */
.importance-bars {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.importance-item {
  display: grid;
  grid-template-columns: 90px 1fr 45px;
  gap: 8px;
  align-items: center;
}

.feature-name {
  font-size: 12px;
  color: #333;
}

.importance-bar {
  height: 18px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.importance-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50 0%, #2e7d32 100%);
  border-radius: 4px;
}

.importance-value {
  font-size: 11px;
  color: #666;
  text-align: right;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #ddd;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #666;
}

.legend-color {
  width: 14px;
  height: 14px;
  border-radius: 3px;
}

.legend-color.home {
  background: #4caf50;
}

.legend-color.draw {
  background: #ff9800;
}

.legend-color.away {
  background: #f44336;
}

@media (max-width: 600px) {
  .model-cards {
    grid-template-columns: 1fr;
  }
  
  .comparison-header, .comparison-row {
    grid-template-columns: 70px 1fr 1fr 1fr 55px;
    font-size: 11px;
  }
  
  .importance-item {
    grid-template-columns: 70px 1fr 35px;
  }
  
  .summary-info {
    flex-direction: column;
    gap: 8px;
  }
}

/* 贝叶斯详情按钮 */
.detail-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 10px;
  font-size: 12px;
  background: #fff;
  border: 1px solid #4caf50;
  border-radius: 6px;
  cursor: pointer;
  color: #2e7d32;
  z-index: 10;
  transition: all 0.2s;
}

.detail-btn:hover {
  background: #4caf50;
  color: white;
}

/* 统一弹窗样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.bayesian-dialog,
.nn-dialog,
.rf-dialog {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

.training-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 2px solid #e8f5e9;
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;
}

.training-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1a472a;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  border-radius: 8px;
  cursor: pointer;
  color: #999;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #666;
}

.dialog-body {
  padding: 16px;
}

.bayesian-intro {
  text-align: center;
  padding: 16px;
  background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
  border-radius: 12px;
  color: white;
  margin-bottom: 16px;
}

.bayesian-intro p {
  margin: 4px 0;
  font-size: 0.9rem;
}

.intro-note {
  font-size: 0.8rem;
  opacity: 0.9;
}

.process-steps h4 {
  color: #2e7d32;
  font-size: 0.95rem;
  margin-bottom: 12px;
}

.process-steps .step-item {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 8px;
}

.process-steps .step-num {
  background: #4caf50;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 12px;
  flex-shrink: 0;
}

.process-steps .step-content {
  flex: 1;
}

.process-steps .step-action {
  font-weight: 600;
  color: #1b5e20;
  font-size: 0.9rem;
}

.process-steps .step-detail {
  display: block;
  font-size: 0.8rem;
  color: #666;
  margin-top: 2px;
}

.example-demo {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.example-demo h4 {
  color: #1b5e20;
  font-size: 0.95rem;
  margin-bottom: 12px;
}

.demo-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}

.demo-col {
  background: white;
  border-radius: 8px;
  padding: 12px;
}

.demo-header {
  font-weight: 600;
  font-size: 0.85rem;
  color: #1b5e20;
  margin-bottom: 8px;
  text-align: center;
}

.demo-values {
  text-align: center;
}

.demo-values div {
  padding: 4px 0;
  font-size: 0.85rem;
}

.demo-values .val {
  color: #4caf50;
  font-weight: 600;
}

.demo-note {
  font-size: 0.7rem;
  color: #666;
  text-align: center;
  margin-top: 8px;
  font-style: italic;
}

.formula-box {
  background: white;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  margin-bottom: 12px;
}

.formula {
  font-family: monospace;
  font-size: 0.95rem;
  color: #333;
}

.formula strong {
  color: #1b5e20;
  font-size: 1.1rem;
}

.result-box {
  background: white;
  border-radius: 8px;
  padding: 12px;
  border: 2px solid #4caf50;
}

.result-header {
  text-align: center;
  font-weight: 600;
  color: #1b5e20;
  margin-bottom: 10px;
}

.result-values {
  display: flex;
  justify-content: space-around;
  margin-bottom: 10px;
}

.result-values span {
  text-align: center;
  font-size: 0.85rem;
}

.result-values strong {
  display: block;
  font-size: 1.1rem;
  color: #1b5e20;
}

.confidence {
  text-align: center;
  font-size: 0.8rem;
  color: #666;
  padding-top: 8px;
  border-top: 1px dashed #ddd;
}

.key-notes {
  background: #fff8e1;
  border-radius: 12px;
  padding: 16px;
}

.note-title {
  font-weight: 600;
  font-size: 0.95rem;
  color: #f57c00;
  margin-bottom: 10px;
}

.note-item {
  font-size: 0.85rem;
  color: #333;
  margin-bottom: 6px;
  padding-left: 8px;
  border-left: 3px solid #f57c00;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 神经网络弹窗 - 样式已统一 */

.nn-intro {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}

.rf-intro {
  background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%) !important;
}

.nn-architecture, .rf-architecture {
  padding: 16px;
  margin-bottom: 16px;
}

.layer {
  padding: 8px 12px;
  margin: 6px 0;
  background: #f5f5f5;
  border-radius: 6px;
  font-size: 0.85rem;
}

.layer.hidden {
  background: #e8eaf6;
  color: #5c6bc0;
}

.layer.output {
  background: #e8f5e9;
  color: #4caf50;
  font-weight: 600;
}

.tree-count {
  text-align: center;
  font-size: 1rem;
  font-weight: 600;
  color: #2e7d32;
  margin-bottom: 12px;
}

.tree-visual {
  display: flex;
  justify-content: center;
  gap: 8px;
  font-size: 1.2rem;
}

.training-info h4 {
  color: #333;
  font-size: 0.95rem;
  margin-bottom: 10px;
}

.step-list {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 12px;
}

.step-list .step {
  padding: 6px 0;
  font-size: 0.85rem;
  color: #555;
  border-bottom: 1px dashed #ddd;
}

.step-list .step:last-child {
  border-bottom: none;
}
/* 在线学习优化样式 */
.learning-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.learning-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.learning-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #1a472a;
}

.learning-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  background: #f5f5f5;
  color: #999;
}

.learning-badge.active {
  background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
  color: white;
}

.learning-visual {
  display: flex;
  gap: 32px;
  align-items: flex-start;
  margin-bottom: 24px;
}

.progress-ring-wrap {
  position: relative;
}

.progress-ring {
  transform: rotate(-90deg);
}

.progress-bg {
  fill: none;
  stroke: #e0e0e0;
  stroke-width: 8;
}

.progress-fill {
  fill: none;
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 326;
  transition: stroke-dashoffset 0.5s ease, stroke 0.3s;
}

.progress-fill.high { stroke: #4caf50; }
.progress-fill.medium { stroke: #ff9800; }
.progress-fill.low { stroke: #f44336; }

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.progress-value {
  font-size: 2rem;
  font-weight: 700;
  color: #333;
}

.progress-unit {
  font-size: 1rem;
  color: #999;
}

.progress-label {
  display: block;
  font-size: 0.75rem;
  color: #666;
  margin-top: 4px;
}

.learning-metrics {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metric-row {
  display: grid;
  grid-template-columns: 30px 80px 1fr 60px;
  gap: 12px;
  align-items: center;
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.metric-icon {
  font-size: 1rem;
}

.metric-label {
  font-size: 0.85rem;
  color: #555;
}

.metric-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.metric-fill.rate {
  background: linear-gradient(90deg, #4caf50 0%, #8bc34a 100%);
}

.metric-fill.update {
  background: linear-gradient(90deg, #2196f3 0%, #03a9f4 100%);
}

.metric-value {
  font-size: 0.85rem;
  font-weight: 600;
  color: #333;
  text-align: right;
}

.metric-status {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.metric-status.normal {
  background: #e8f5e9;
  color: #2e7d32;
}

.metric-status.warning {
  background: #fff3e0;
  color: #e65100;
}

.learning-chart {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 20px;
}

.learning-chart h4 {
  margin: 0 0 12px 0;
  font-size: 0.9rem;
  color: #333;
}

.chart-area {
  position: relative;
}

.trend-chart {
  display: block;
}

.chart-labels {
  position: absolute;
  left: 0;
  top: 0;
  display: flex;
  flex-direction: column;
  gap: 40px;
  font-size: 0.7rem;
  color: #999;
}

.chart-labels span {
  position: relative;
  top: 12px;
}

.learning-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: #f5f5f5;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover:not(:disabled) {
  background: #e8f5e9;
  border-color: #4caf50;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.action-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

@media (max-width: 768px) {
  .learning-visual {
    flex-direction: column;
    align-items: center;
  }
  
  .learning-metrics {
    width: 100%;
  }
  
  .metric-row {
    grid-template-columns: 30px 1fr 60px;
  }
  
  .metric-bar {
    display: none;
  }
}
</style>
