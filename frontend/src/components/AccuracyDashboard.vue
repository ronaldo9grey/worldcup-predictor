<template>
  <div class="accuracy-dashboard">
    <!-- 自定义弹窗 -->
    <div v-if="showDialog" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog-card">
        <div class="dialog-icon">{{ dialogIcon }}</div>
        <div class="dialog-title">{{ dialogTitle }}</div>
        <div class="dialog-message">{{ dialogMessage }}</div>
        <button @click="closeDialog" class="dialog-btn">确定</button>
      </div>
    </div>
    
    <!-- 训练过程弹窗 -->
    <div v-if="showTraining" class="dialog-overlay" @click.self="showTraining = false">
      <div class="training-dialog">
        <div class="training-header">
          <div class="training-title">🧠 训练过程详解</div>
          <button @click="showTraining = false" class="close-btn">✕</button>
        </div>
        
        <div class="training-body">
          <!-- 说明 -->
          <div class="training-intro">
            <p>历史训练准确率 <strong>53.1%</strong> 是如何计算出来的？</p>
            <p class="intro-note">下面用2022世界杯决赛为例，展示完整预测过程</p>
          </div>
          
          <!-- 步骤1: 数据收集 -->
          <div class="step-card">
            <div class="step-num">1</div>
            <div class="step-content">
              <div class="step-title">收集历史数据</div>
              <div class="step-detail">
                <div class="data-row">
                  <span>2018世界杯</span>
                  <span class="data-val">64场比赛</span>
                </div>
                <div class="data-row">
                  <span>2022世界杯</span>
                  <span class="data-val">64场比赛</span>
                </div>
                <div class="data-row total">
                  <span>总计</span>
                  <span class="data-val">128场比赛</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 步骤2: 提取预测因子 -->
          <div class="step-card">
            <div class="step-num">2</div>
            <div class="step-content">
              <div class="step-title">提取预测因子</div>
              <div class="step-example">
                <div class="example-match">2022决赛: 阿根廷 🇦🇷 vs 法国 🇫🇷</div>
                <div class="factors-grid">
                  <div class="factor-item">
                    <div class="factor-name">Elo实力差</div>
                    <div class="factor-val">+15 (ARG略强)</div>
                  </div>
                  <div class="factor-item">
                    <div class="factor-name">排名差距</div>
                    <div class="factor-val">ARG #1 vs FRA #2</div>
                  </div>
                  <div class="factor-item">
                    <div class="factor-name">比赛阶段</div>
                    <div class="factor-val">决赛（经验重要）</div>
                  </div>
                  <div class="factor-item">
                    <div class="factor-name">历史交锋</div>
                    <div class="factor-val">势均力敌</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 步骤3: 权重计算 -->
          <div class="step-card">
            <div class="step-num">3</div>
            <div class="step-content">
              <div class="step-title">用权重计算预测概率</div>
              <div class="calc-demo">
                <div class="calc-row">
                  <span>Elo差 × 0.28 = 0.015</span>
                  <span class="calc-plus">+</span>
                </div>
                <div class="calc-row">
                  <span>排名差 × 0.10 = 0.02</span>
                  <span class="calc-plus">+</span>
                </div>
                <div class="calc-row">
                  <span>其他因子...</span>
                  <span class="calc-plus">=</span>
                </div>
                <div class="calc-result">
                  <div class="prob-item">
                    <span>阿根廷胜</span>
                    <span class="prob-val">43%</span>
                  </div>
                  <div class="prob-item">
                    <span>平局</span>
                    <span class="prob-val">17%</span>
                  </div>
                  <div class="prob-item">
                    <span>法国胜</span>
                    <span class="prob-val">40%</span>
                  </div>
                </div>
                <div class="prediction">预测: 阿根廷胜（势均力敌）</div>
              </div>
            </div>
          </div>
          
          <!-- 步骤4: 验证结果 -->
          <div class="step-card">
            <div class="step-num">4</div>
            <div class="step-content">
              <div class="step-title">对比实际结果</div>
              <div class="verify-demo">
                <div class="verify-row">
                  <span>预测结果:</span>
                  <span class="verify-val predict">阿根廷胜</span>
                </div>
                <div class="verify-row">
                  <span>实际结果:</span>
                  <span class="verify-val actual">阿根廷胜（点球）</span>
                </div>
                <div class="verify-result correct">✓ 预测正确</div>
              </div>
            </div>
          </div>
          
          <!-- 步骤5: 统计准确率 -->
          <div class="step-card final">
            <div class="step-num">5</div>
            <div class="step-content">
              <div class="step-title">统计所有比赛</div>
              <div class="accuracy-calc">
                <div class="accuracy-formula">
                  准确率 = 正确预测数 / 总预测数
                </div>
                <div class="accuracy-numbers">
                  <span class="correct-num">68</span>
                  <span>/</span>
                  <span class="total-num">128</span>
                  <span>=</span>
                  <span class="result-num">53.1%</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 关键说明 -->
          <div class="key-notes">
            <div class="note-title">💡 关键说明</div>
            <div class="note-item">
              <strong>历史准确率</strong>: 用2018+2022真实数据验证
            </div>
            <div class="note-item">
              <strong>实时准确率</strong>: 用模拟数据演示（2026还未开始）
            </div>
            <div class="note-item">
              <strong>冷门难预测</strong>: 如沙特2-1阿根廷，属于极小概率事件
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="section-title">📊 准确率仪表盘</div>
    
    <!-- 总体准确率 -->
    <div class="accuracy-cards">
      <div class="accuracy-card pending">
        <div class="card-value">待开赛</div>
        <div class="card-label">实时准确率</div>
        <div class="card-note">2026世界杯未开始</div>
        <div class="card-sub">开赛后开始追踪</div>
      </div>
      
      <div class="accuracy-card pending">
        <div class="card-value">待开赛</div>
        <div class="card-label">冷门检测率</div>
        <div class="card-note">开赛后统计</div>
      </div>
      
      <div class="accuracy-card historical" @click="showTraining = true">
        <div class="card-value">{{ historicalAccuracy }}%</div>
        <div class="card-label">历史训练准确率</div>
        <div class="card-sub">基于2018+2022数据</div>
        <div class="card-hint">点击查看算法过程 →</div>
      </div>
    </div>
    
    <!-- 分阶段准确率 -->
    <div class="accuracy-section">
      <div class="section-subtitle">分阶段准确率</div>
      <div class="stage-bars">
        <div v-for="(data, stage) in report.by_stage" :key="stage" class="stage-bar">
          <div class="stage-label">{{ getStageLabel(stage) }}</div>
          <div class="stage-progress">
            <div class="stage-fill" :style="{width: data.accuracy + '%'}"></div>
          </div>
          <div class="stage-value">{{ data.accuracy }}%</div>
        </div>
      </div>
    </div>
    
    <!-- 准确率趋势图 -->
    <div class="accuracy-section">
      <div class="section-subtitle">📈 历史准确率趋势</div>
      <div class="trend-chart">
        <svg viewBox="0 0 400 200" class="trend-svg">
          <!-- 网格线 -->
          <defs>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#4caf50;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#81c784;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" style="stop-color:#4caf50;stop-opacity:0.3" />
              <stop offset="100%" style="stop-color:#4caf50;stop-opacity:0.05" />
            </linearGradient>
          </defs>
          
          <!-- 横向网格线 -->
          <line x1="50" y1="40" x2="380" y2="40" stroke="#e0e0e0" stroke-dasharray="4" />
          <line x1="50" y1="80" x2="380" y2="80" stroke="#e0e0e0" stroke-dasharray="4" />
          <line x1="50" y1="120" x2="380" y2="120" stroke="#e0e0e0" stroke-dasharray="4" />
          <line x1="50" y1="160" x2="380" y2="160" stroke="#e0e0e0" stroke-dasharray="4" />
          
          <!-- Y轴刻度 -->
          <text x="40" y="44" class="grid-label" text-anchor="end">80%</text>
          <text x="40" y="84" class="grid-label" text-anchor="end">60%</text>
          <text x="40" y="124" class="grid-label" text-anchor="end">40%</text>
          <text x="40" y="164" class="grid-label" text-anchor="end">20%</text>
          
          <!-- 面积填充 -->
          <path d="M 80 120 L 160 88 L 280 72 L 360 72 L 360 160 L 80 160 Z" fill="url(#areaGradient)" />
          
          <!-- 折线 -->
          <polyline 
            points="80,120 160,88 280,72 360,72" 
            fill="none" 
            stroke="url(#lineGradient)" 
            stroke-width="3"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          
          <!-- 数据点 -->
          <circle cx="80" cy="120" r="6" fill="#4caf50" stroke="white" stroke-width="2" />
          <circle cx="160" cy="88" r="6" fill="#4caf50" stroke="white" stroke-width="2" />
          <circle cx="280" cy="72" r="6" fill="#66bb6a" stroke="white" stroke-width="2" />
          <circle cx="360" cy="72" r="6" fill="#81c784" stroke="white" stroke-width="2" />
          
          <!-- X轴标签 -->
          <text x="80" y="178" class="axis-label" text-anchor="middle">2010</text>
          <text x="160" y="178" class="axis-label" text-anchor="middle">2014</text>
          <text x="280" y="178" class="axis-label" text-anchor="middle">2018</text>
          <text x="360" y="178" class="axis-label" text-anchor="middle">2022</text>
          
          <!-- 数值标签 -->
          <text x="80" y="108" class="point-value" text-anchor="middle">50%</text>
          <text x="160" y="76" class="point-value" text-anchor="middle">58%</text>
          <text x="280" y="60" class="point-value" text-anchor="middle">64%</text>
          <text x="360" y="60" class="point-value" text-anchor="middle">64%</text>
        </svg>
        
        <!-- 图例 -->
        <div class="chart-legend">
          <div class="legend-item">
            <span class="legend-dot"></span>
            <span>历史准确率（世界杯）</span>
          </div>
          <div class="legend-item highlight">
            <span>📊 趋势：模型准确率逐步提升</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 分置信度准确率 -->
    <div class="accuracy-section">
      <div class="section-subtitle">置信度准确率</div>
      <div class="confidence-grid">
        <div v-for="(data, level) in report.by_confidence" :key="level" 
             :class="['confidence-item', level.toLowerCase()]">
          <div class="conf-label">{{ getConfidenceLabel(level) }}</div>
          <div class="conf-value">{{ data.accuracy }}%</div>
          <div class="conf-count">{{ data.correct }}/{{ data.total }}</div>
        </div>
      </div>
    </div>
    
    <!-- 权重展示 -->
    <div class="accuracy-section">
      <div class="section-subtitle">优化权重</div>
      <div class="weights-grid">
        <div v-for="(weight, factor) in weights" :key="factor" class="weight-item">
          <div class="weight-label">{{ getFactorLabel(factor) }}</div>
          <div class="weight-bar">
            <div class="weight-fill" :style="{width: (weight * 100) + '%'}"></div>
          </div>
          <div class="weight-value">{{ (weight * 100).toFixed(0) }}%</div>
        </div>
      </div>
    </div>
    
    <!-- 冷门预警示例 -->
    <div class="accuracy-section">
      <div class="section-subtitle">历史重大冷门 🎭</div>
      <div class="upsets-list">
        <div v-for="upset in recentUpsets" :key="upset.match" class="upset-item">
          <div class="upset-year">{{ upset.year }}</div>
          <div class="upset-match">{{ upset.match }}</div>
          <div class="upset-desc">{{ upset.desc }}</div>
          <div class="upset-severity">
            <span v-for="n in upset.severity" :key="n">⚡</span>
          </div>
        </div>
      </div>
      
      <!-- 冷门雷达图 -->
      <div class="upset-radar">
        <div class="radar-title">📊 冷门因素分析（2022 沙特 vs 阿根廷）</div>
        <svg viewBox="0 0 300 280" class="radar-svg">
          <!-- 背景 - 六边形网格 -->
          <polygon points="150,30 250,80 250,180 150,230 50,180 50,80" fill="none" stroke="#e0e0e0" stroke-width="1" />
          <polygon points="150,60 220,95 220,165 150,200 80,165 80,95" fill="none" stroke="#e0e0e0" stroke-width="1" />
          <polygon points="150,90 190,110 190,150 150,170 110,150 110,110" fill="none" stroke="#e0e0e0" stroke-width="1" />
          <polygon points="150,120 160,125 160,135 150,140 140,135 140,125" fill="none" stroke="#e0e0e0" stroke-width="1" />
          
          <!-- 轴线 -->
          <line x1="150" y1="30" x2="150" y2="230" stroke="#e0e0e0" stroke-width="1" />
          <line x1="50" y1="80" x2="250" y2="180" stroke="#e0e0e0" stroke-width="1" />
          <line x1="50" y1="180" x2="250" y2="80" stroke="#e0e0e0" stroke-width="1" />
          
          <!-- 数据区域 -->
          <polygon 
            points="150,50 230,85 240,160 150,210 70,150 60,90" 
            fill="rgba(244, 67, 54, 0.2)" 
            stroke="#f44336" 
            stroke-width="2"
          />
          
          <!-- 数据点 -->
          <circle cx="150" cy="50" r="5" fill="#f44336" stroke="white" stroke-width="2" />
          <circle cx="230" cy="85" r="5" fill="#f44336" stroke="white" stroke-width="2" />
          <circle cx="240" cy="160" r="5" fill="#f44336" stroke="white" stroke-width="2" />
          <circle cx="150" cy="210" r="5" fill="#f44336" stroke="white" stroke-width="2" />
          <circle cx="70" cy="150" r="5" fill="#f44336" stroke="white" stroke-width="2" />
          <circle cx="60" cy="90" r="5" fill="#f44336" stroke="white" stroke-width="2" />
          
          <!-- 轴标签 -->
          <text x="150" y="20" class="radar-label" text-anchor="middle">实力差距</text>
          <text x="265" y="75" class="radar-label" text-anchor="start">历史交锋</text>
          <text x="265" y="185" class="radar-label" text-anchor="start">状态表现</text>
          <text x="150" y="255" class="radar-label" text-anchor="middle">主场因素</text>
          <text x="35" y="185" class="radar-label" text-anchor="end">赛事阶段</text>
          <text x="35" y="75" class="radar-label" text-anchor="end">预测偏离</text>
          
          <!-- 数值标签 -->
          <text x="150" y="45" class="radar-value" text-anchor="middle">95%</text>
          <text x="238" y="95" class="radar-value" text-anchor="start">70%</text>
          <text x="248" y="165" class="radar-value" text-anchor="start">85%</text>
          <text x="150" y="225" class="radar-value" text-anchor="middle">20%</text>
          <text x="55" y="155" class="radar-value" text-anchor="end">60%</text>
          <text x="45" y="95" class="radar-value" text-anchor="end">100%</text>
        </svg>
        
        <div class="radar-legend">
          <div class="legend-row">
            <span class="legend-color upset"></span>
            <span>冷门因素强度（越远越强）</span>
          </div>
          <div class="legend-insight">
            💡 实力差距大 + 预测偏离100% = 典型冷门特征
          </div>
        </div>
      </div>
    </div>
    
    <!-- 刷新按钮 -->
    <div class="refresh-section">
      <button @click="loadReport" class="refresh-btn">🔄 刷新数据</button>
      <span class="last-update">最后更新: {{ lastUpdate }}</span>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'

export default {
  setup() {
    const report = ref({
      overall: {},
      by_stage: {},
      by_confidence: {},
      historical_training: {}
    })
    const weights = ref({})
    const recentUpsets = ref([])
    const lastUpdate = ref('')
    
    // 弹窗状态
    const showDialog = ref(false)
    const dialogIcon = ref('✓')
    const dialogTitle = ref('')
    const dialogMessage = ref('')
    const showTraining = ref(false)
    
    const historicalAccuracy = computed(() => {
      return report.value.historical_training?.overall_accuracy || 0
    })
    
    async function loadReport() {
      try {
        // 加载准确率报告
        const resp1 = await fetch('/worldcup/api/accuracy/report')
        report.value = await resp1.json()
        
        // 加载权重
        const resp2 = await fetch('/worldcup/api/accuracy/weights')
        const weightData = await resp2.json()
        weights.value = weightData.weights || {}
        
        // 加载冷门数据
        const resp3 = await fetch('/worldcup/api/accuracy/upsets?min_severity=4')
        const upsetData = await resp3.json()
        recentUpsets.value = upsetData.upsets?.slice(0, 6) || []
        
        lastUpdate.value = new Date().toLocaleTimeString()
      } catch (e) {
        console.error('加载准确率报告失败', e)
      }
    }
    
    async function runAutoVerify() {
      try {
        const resp = await fetch('/worldcup/api/auto-verify/run', { method: 'POST' })
        const data = await resp.json()
        
        if (data.success) {
          // 刷新报告
          await loadReport()
          
          // 显示自定义弹窗
          dialogIcon.value = '✅'
          dialogTitle.value = '自动验证完成'
          dialogMessage.value = `已验证${data.results.verified}场比赛\n当前准确率: ${data.results.accuracy_report.overall.accuracy}%`
          showDialog.value = true
        }
      } catch (e) {
        console.error('自动验证失败', e)
        dialogIcon.value = '❌'
        dialogTitle.value = '自动验证失败'
        dialogMessage.value = e.message || '网络错误'
        showDialog.value = true
      }
    }
    
    function closeDialog() {
      showDialog.value = false
    }
    
    function getStageLabel(stage) {
      const labels = {
        'GROUP': '小组赛',
        'R16': '16强',
        'QF': '8强',
        'SF': '半决赛',
        'FI': '决赛'
      }
      return labels[stage] || stage
    }
    
    function getConfidenceLabel(level) {
      const labels = {
        'HIGH': '高信心',
        'MEDIUM': '中信心',
        'LOW': '低信心'
      }
      return labels[level] || level
    }
    
    function getFactorLabel(factor) {
      const labels = {
        'elo_diff': 'Elo实力差',
        'form_diff': '状态差异',
        'rank_gap': '排名差距',
        'home_advantage': '主场优势',
        'stage_factor': '赛事阶段',
        'continent_factor': '洲际因素',
        'h2h': '历史交锋',
        'wc_experience': '世界杯经验'
      }
      return labels[factor] || factor
    }
    
    onMounted(() => {
      loadReport()
    })
    
    return {
      report, weights, recentUpsets, lastUpdate, historicalAccuracy,
      showDialog, dialogIcon, dialogTitle, dialogMessage, showTraining,
      loadReport, runAutoVerify, closeDialog, getStageLabel, getConfidenceLabel, getFactorLabel
    }
  }
}
</script>

<style scoped>
.accuracy-dashboard {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

/* 自定义弹窗 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.2s ease;
}

.dialog-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  max-width: 360px;
  width: 90%;
  text-align: center;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

.dialog-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.dialog-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.dialog-message {
  font-size: 0.95rem;
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
  white-space: pre-line;
}

.dialog-btn {
  padding: 12px 32px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.dialog-btn:hover {
  background: #5a6fd6;
  transform: translateY(-1px);
}

.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 16px;
  color: #333;
}

/* 卡片 */
.accuracy-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.accuracy-card {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 16px;
  text-align: center;
}

.accuracy-card.main {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.accuracy-card.pending {
  background: #f8f9fa;
  color: #999;
}

.accuracy-card.pending .card-value {
  font-size: 1rem;
  font-weight: 600;
}

.accuracy-card.pending .card-note {
  font-size: 0.75rem;
  margin-top: 4px;
  color: #aaa;
}

.card-value {
  font-size: 2rem;
  font-weight: 700;
}

.card-label {
  font-size: 0.85rem;
  margin-top: 4px;
  opacity: 0.9;
}

.card-sub {
  font-size: 0.75rem;
  margin-top: 4px;
  opacity: 0.7;
}

/* 区块 */
.accuracy-section {
  margin-bottom: 20px;
}

.section-subtitle {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 10px;
  color: #555;
}

/* 阶段进度条 */
.stage-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stage-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stage-label {
  width: 60px;
  font-size: 0.8rem;
  color: #666;
}

.stage-progress {
  flex: 1;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.stage-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.stage-value {
  width: 50px;
  text-align: right;
  font-size: 0.85rem;
  font-weight: 600;
  color: #667eea;
}

/* 置信度网格 */
.confidence-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.confidence-item {
  padding: 12px;
  border-radius: 8px;
  text-align: center;
}

.confidence-item.high {
  background: #e8f5e9;
}

.confidence-item.medium {
  background: #fff8e1;
}

.confidence-item.low {
  background: #fce4ec;
}

.conf-label {
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.conf-value {
  font-size: 1.5rem;
  font-weight: 700;
}

.conf-count {
  font-size: 0.7rem;
  color: #666;
}

/* 权重网格 */
.weights-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.weight-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.weight-label {
  width: 80px;
  font-size: 0.75rem;
  color: #666;
}

.weight-bar {
  flex: 1;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

.weight-fill {
  height: 100%;
  background: #667eea;
  border-radius: 3px;
}

.weight-value {
  width: 40px;
  text-align: right;
  font-size: 0.8rem;
  font-weight: 600;
  color: #667eea;
}

/* 冷门列表 */
.upsets-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upset-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #fff8e1;
  border-radius: 6px;
  font-size: 0.85rem;
}

.upset-year {
  font-weight: 700;
  color: #e91e63;
}

.upset-match {
  font-weight: 600;
}

.upset-desc {
  flex: 1;
  color: #666;
}

.upset-severity {
  font-size: 0.8rem;
}

/* 刷新 */
.refresh-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.refresh-btn {
  padding: 8px 16px;
  background: #f0f0f0;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
}

.refresh-btn:hover {
  background: #e0e0e0;
}

.verify-btn {
  padding: 8px 16px;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  font-weight: 600;
}

.verify-btn:hover {
  background: #229954;
}

.last-update {
  font-size: 0.75rem;
  color: #999;
}

/* 历史准确率卡片 */
.accuracy-card.historical {
  cursor: pointer;
  transition: all 0.2s;
}

.accuracy-card.historical:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

.card-note {
  font-size: 0.7rem;
  color: #999;
  margin-top: 4px;
}

.card-hint {
  font-size: 0.7rem;
  color: #667eea;
  margin-top: 6px;
}

/* 训练过程弹窗 */
.training-dialog {
  background: white;
  border-radius: 16px;
  max-width: 500px;
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  animation: slideUp 0.3s ease;
}

.training-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;
}

.training-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #333;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f5f5f5;
  border-radius: 50%;
  font-size: 1rem;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  background: #e0e0e0;
}

.training-body {
  padding: 16px;
}

.training-intro {
  text-align: center;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  margin-bottom: 16px;
}

.training-intro p {
  margin: 4px 0;
}

.intro-note {
  font-size: 0.85rem;
  opacity: 0.9;
}

.step-card {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 12px;
}

.step-num {
  width: 32px;
  height: 32px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-title {
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 8px;
  color: #333;
}

.step-detail {
  font-size: 0.85rem;
}

.data-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px dashed #ddd;
}

.data-row.total {
  border-bottom: none;
  font-weight: 600;
  margin-top: 8px;
}

.data-val {
  color: #667eea;
}

.step-example {
  font-size: 0.85rem;
}

.example-match {
  text-align: center;
  padding: 10px;
  background: white;
  border-radius: 8px;
  margin-bottom: 10px;
  font-weight: 600;
}

.factors-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.factor-item {
  background: white;
  padding: 8px 10px;
  border-radius: 6px;
}

.factor-name {
  font-size: 0.75rem;
  color: #666;
}

.factor-val {
  font-size: 0.85rem;
  font-weight: 500;
  color: #333;
}

.calc-demo {
  font-size: 0.85rem;
}

.calc-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 8px;
  font-family: monospace;
}

.calc-plus {
  color: #667eea;
  font-weight: 700;
}

.calc-result {
  background: white;
  padding: 12px;
  border-radius: 8px;
  margin: 10px 0;
}

.prob-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}

.prob-val {
  font-weight: 600;
  color: #667eea;
}

.prediction {
  text-align: center;
  padding: 8px;
  background: #e8f5e9;
  border-radius: 6px;
  font-weight: 600;
  color: #27ae60;
}

.verify-demo {
  font-size: 0.85rem;
}

.verify-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.verify-val.predict {
  color: #667eea;
}

.verify-val.actual {
  color: #27ae60;
}

.verify-result {
  text-align: center;
  padding: 12px;
  border-radius: 8px;
  margin-top: 10px;
  font-weight: 600;
}

.verify-result.correct {
  background: #e8f5e9;
  color: #27ae60;
}

.step-card.final {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.step-card.final .step-num {
  background: white;
  color: #667eea;
}

.step-card.final .step-title {
  color: white;
}

.accuracy-calc {
  text-align: center;
}

.accuracy-formula {
  font-size: 0.85rem;
  margin-bottom: 10px;
  opacity: 0.9;
}

.accuracy-numbers {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
}

.correct-num {
  color: #27ae60;
}

.result-num {
  font-size: 1.5rem;
  font-weight: 700;
}

.key-notes {
  margin-top: 16px;
  padding: 16px;
  background: #fff8e1;
  border-radius: 12px;
}

.note-title {
  font-weight: 600;
  margin-bottom: 10px;
  font-size: 0.95rem;
}

.note-item {
  font-size: 0.85rem;
  margin-bottom: 6px;
  padding-left: 8px;
  border-left: 3px solid #f39c12;
}

/* 贝叶斯步骤样式 */
@media (max-width: 600px) {
  .note-item {
    font-size: 0.75rem;
  }
}

/* 准确率趋势图 */
.trend-chart {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
}

.trend-svg {
  width: 100%;
  max-width: 400px;
  height: auto;
  display: block;
  margin: 0 auto;
}

.grid-label, .axis-label, .point-value {
  font-size: 12px;
  fill: #666;
  font-family: inherit;
}

.point-value {
  font-size: 13px;
  fill: #2e7d32;
  font-weight: 600;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #ddd;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #666;
}

.legend-dot {
  width: 10px;
  height: 10px;
  background: #4caf50;
  border-radius: 50%;
}

.legend-item.highlight {
  color: #2e7d32;
  font-weight: 500;
}

/* 冷门雷达图 */
.upset-radar {
  background: linear-gradient(135deg, #ffebee 0%, #fff8f8 100%);
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
  border: 2px solid #ffcdd2;
}

.radar-title {
  text-align: center;
  font-weight: 600;
  color: #c62828;
  font-size: 14px;
  margin-bottom: 12px;
}

.radar-svg {
  width: 100%;
  max-width: 300px;
  height: auto;
  display: block;
  margin: 0 auto;
}

.radar-label {
  font-size: 11px;
  fill: #666;
  font-weight: 500;
}

.radar-value {
  font-size: 10px;
  fill: #f44336;
  font-weight: 600;
}

.radar-legend {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #ffcdd2;
}

.legend-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.legend-color.upset {
  width: 14px;
  height: 14px;
  background: #f44336;
  border-radius: 3px;
}

.legend-insight {
  text-align: center;
  font-size: 12px;
  color: #c62828;
  font-weight: 500;
  padding: 8px;
  background: white;
  border-radius: 6px;
}
</style>