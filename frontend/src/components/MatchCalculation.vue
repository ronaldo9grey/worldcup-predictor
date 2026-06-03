<template>
  <div v-if="visible" class="calc-overlay" @click.self="close">
    <div class="calc-dialog">
      <div class="calc-header">
        <div class="calc-title">🧠 贝叶斯预测分析</div>
        <button @click="close" class="close-btn">✕</button>
      </div>
      
      <div class="calc-body" v-if="calculation">
        <!-- 比赛信息 -->
        <div class="match-info-card">
          <div class="match-teams">
            <div class="team-block">
              <div class="team-flag">{{ getTeamFlag(calculation.home.code) }}</div>
              <div class="team-name">{{ calculation.home.name_cn }}</div>
              <div class="team-code">{{ calculation.home.code }}</div>
            </div>
            <div class="vs-text">VS</div>
            <div class="team-block">
              <div class="team-flag">{{ getTeamFlag(calculation.away.code) }}</div>
              <div class="team-name">{{ calculation.away.name_cn }}</div>
              <div class="team-code">{{ calculation.away.code }}</div>
            </div>
          </div>
          <div class="match-meta">
            <span>{{ calculation.group }}组 · 第{{ calculation.match_index + 1 }}场</span>
          </div>
        </div>

        <!-- 步骤1: 球队数据 -->
        <div class="step-section">
          <div class="step-header">
            <div class="step-badge">1</div>
            <div class="step-title">球队基础数据</div>
          </div>
          <div class="team-data-grid">
            <div class="data-item">
              <div class="data-label">Elo评分</div>
              <div class="data-values">
                <span class="home-val">{{ calculation.home.elo }}</span>
                <span class="vs-line"></span>
                <span class="away-val">{{ calculation.away.elo }}</span>
              </div>
              <div class="data-diff" :class="getDiffClass(calculation.factors.elo_diff.raw)">
                差值: {{ calculation.factors.elo_diff.raw > 0 ? '+' : '' }}{{ calculation.factors.elo_diff.raw }}
              </div>
            </div>
            <div class="data-item">
              <div class="data-label">FIFA排名</div>
              <div class="data-values">
                <span class="home-val">#{{ calculation.home.rank }}</span>
                <span class="vs-line"></span>
                <span class="away-val">#{{ calculation.away.rank }}</span>
              </div>
              <div class="data-diff" :class="getDiffClass(-calculation.factors.rank_diff.raw)">
                差值: {{ calculation.factors.rank_diff.raw > 0 ? '+' : '' }}{{ calculation.factors.rank_diff.raw }}
              </div>
            </div>
            <div class="data-item">
              <div class="data-label">近期状态</div>
              <div class="data-values">
                <span class="home-val">{{ calculation.home.form || '---' }}</span>
                <span class="vs-line"></span>
                <span class="away-val">{{ calculation.away.form || '---' }}</span>
              </div>
            </div>
            <div class="data-item">
              <div class="data-label">所属洲</div>
              <div class="data-values">
                <span class="home-val">{{ getContinent(calculation.home.continent) }}</span>
                <span class="vs-line"></span>
                <span class="away-val">{{ getContinent(calculation.away.continent) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤2: 因子标准化 -->
        <div class="step-section">
          <div class="step-header">
            <div class="step-badge">2</div>
            <div class="step-title">预测因子标准化</div>
            <div class="step-note">将原始数据转换为[-1, 1]区间</div>
          </div>
          <div class="factors-table">
            <div class="factor-row header">
              <div class="factor-name">因子名称</div>
              <div class="factor-raw">原始值</div>
              <div class="factor-norm">标准化</div>
              <div class="factor-meaning">解读</div>
            </div>
            <div class="factor-row" v-for="(factor, key) in calculation.factors" :key="key">
              <div class="factor-name">{{ getFactorName(key) }}</div>
              <div class="factor-raw">{{ factor.raw }}</div>
              <div class="factor-norm">
                <div class="norm-bar">
                  <div class="norm-fill" :style="{left: getNormPosition(factor.normalized), width: Math.abs(factor.normalized) * 50 + '%'}"></div>
                  <div class="norm-zero"></div>
                </div>
                <span class="norm-val">{{ factor.normalized.toFixed(3) }}</span>
              </div>
              <div class="factor-meaning">{{ factor.meaning }}</div>
            </div>
          </div>
        </div>

        <!-- 步骤3: 权重应用 -->
        <div class="step-section">
          <div class="step-header">
            <div class="step-badge">3</div>
            <div class="step-title">权重计算</div>
            <div class="step-note">标准化值 × 权重 = 贡献值</div>
          </div>
          <div class="weight-calc-grid">
            <div class="weight-item" v-for="(weight, key) in calculation.weights" :key="key">
              <div class="weight-header">
                <span class="weight-name">{{ getFactorName(key) }}</span>
                <span class="weight-val">权重 {{ (weight * 100).toFixed(0) }}%</span>
              </div>
              <div class="weight-bar-bg">
                <div class="weight-bar" :style="{width: weight * 100 + '%'}"></div>
              </div>
              <div class="weight-calc" v-if="calculation.factors[key]">
                <span class="calc-num">{{ calculation.factors[key].normalized.toFixed(2) }}</span>
                <span class="calc-op">×</span>
                <span class="calc-num">{{ weight.toFixed(2) }}</span>
                <span class="calc-op">=</span>
                <span class="calc-result">{{ (calculation.factors[key].normalized * weight).toFixed(3) }}</span>
              </div>
            </div>
          </div>
          <div class="total-contribution">
            <div class="total-label">主队优势累积值</div>
            <div class="total-value">{{ calculation.total_contribution.toFixed(4) }}</div>
            <div class="total-explain">
              {{ calculation.total_contribution > 0.05 ? '主队明显占优' : calculation.total_contribution > 0 ? '主队略占优势' : calculation.total_contribution > -0.05 ? '势均力敌' : calculation.total_contribution > -0.1 ? '客队略占优势' : '客队明显占优' }}
            </div>
          </div>
        </div>

        <!-- 步骤4: 概率计算 -->
        <div class="step-section">
          <div class="step-header">
            <div class="step-badge">4</div>
            <div class="step-title">预测概率</div>
            <div class="step-note">贝叶斯归一化：概率 = 后验值 / 总和</div>
          </div>
          <div class="probability-calc">
            <div class="prob-formula">
              P(主胜) = 后验概率(主胜) / [后验概率(主胜) + 后验概率(平局) + 后验概率(客胜)]
            </div>
            <div class="prob-bars">
              <div class="prob-item">
                <div class="prob-label">主胜</div>
                <div class="prob-bar-wrap">
                  <div class="prob-bar home" :style="{width: calculation.probabilities.home_win * 100 + '%'}">
                    <span class="prob-text">{{ (calculation.probabilities.home_win * 100).toFixed(1) }}%</span>
                  </div>
                </div>
              </div>
              <div class="prob-item">
                <div class="prob-label">平局</div>
                <div class="prob-bar-wrap">
                  <div class="prob-bar draw" :style="{width: calculation.probabilities.draw * 100 + '%'}">
                    <span class="prob-text">{{ (calculation.probabilities.draw * 100).toFixed(1) }}%</span>
                  </div>
                </div>
              </div>
              <div class="prob-item">
                <div class="prob-label">客胜</div>
                <div class="prob-bar-wrap">
                  <div class="prob-bar away" :style="{width: calculation.probabilities.away_win * 100 + '%'}">
                    <span class="prob-text">{{ (calculation.probabilities.away_win * 100).toFixed(1) }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤5: 预测结论 -->
        <div class="step-section final">
          <div class="step-header">
            <div class="step-badge">5</div>
            <div class="step-title">预测结论</div>
          </div>
          <div class="prediction-result">
            <div class="result-badge" :class="getPredictionClass(calculation.prediction)">
              {{ getResultLabel(calculation.prediction) }}
            </div>
            <div class="result-detail">
              <p>{{ calculation.home.name_cn }} 胜率 {{ (calculation.probabilities.home_win * 100).toFixed(1) }}%</p>
              <p class="confidence">置信度: {{ calculation.confidence }}</p>
            </div>
            <div class="result-note">
              💡 此预测基于2018+2022世界杯数据训练的模型，仅供参考
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  props: {
    visible: Boolean,
    calculation: Object
  },
  emits: ['close'],
  setup(props, { emit }) {
    function close() {
      emit('close')
    }

    function getTeamFlag(code) {
      const flags = {
        'ARG': '🇦🇷', 'BRA': '🇧🇷', 'GER': '🇩🇪', 'FRA': '🇫🇷', 'ESP': '🇪🇸',
        'ENG': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'POR': '🇵🇹', 'NED': '🇳🇱', 'BEL': '🇧🇪', 'ITA': '🇮🇹',
        'USA': '🇺🇸', 'MEX': '🇲🇽', 'CAN': '🇨🇦', 'JPN': '🇯🇵', 'KOR': '🇰🇷',
        'AUS': '🇦🇺', 'SEN': '🇸🇳', 'MAR': '🇲🇦', 'NGA': '🇳🇬', 'EGY': '🇪🇬',
        'TUN': '🇹🇳', 'CMR': '🇨🇲', 'GHA': '🇬🇭', 'CIV': '🇨🇮', 'COD': '🇨🇩',
        'CHI': '🇨🇱', 'COL': '🇨🇴', 'ECU': '🇪🇨', 'URU': '🇺🇾', 'PAR': '🇵🇾',
        'PER': '🇵🇪', 'VEN': '🇻🇪', 'CRC': '🇨🇷', 'PAN': '🇵🇦', 'JAM': '🇯🇲',
        'HON': '🇭🇳', 'SAU': '🇸🇦', 'IRN': '🇮🇷', 'QAT': '🇶🇦', 'UAE': '🇦🇪',
        'CHN': '🇨🇳', 'JOR': '🇯🇴', 'UZB': '🇺🇿', 'IRQ': '🇮🇶', 'OMA': '🇴🇲',
        'SWE': '🇸🇪', 'NOR': '🇳🇴', 'DEN': '🇩🇰', 'FIN': '🇫🇮', 'AUT': '🇦🇹',
        'POL': '🇵🇱', 'UKR': '🇺🇦', 'RUS': '🇷🇺', 'CRO': '🇭🇷', 'SRB': '🇷🇸',
        'SUI': '🇨🇭', 'CZE': '🇨🇿', 'TUR': '🇹🇷', 'WAL': '🏴󠁧󠁢󠁷󠁬󠁳󠁿', 'SCO': '🏴󠁧󠁢󠁳󠁣󠁴󠁿',
        'IRL': '🇮🇪', 'ALB': '🇦🇱', 'NZL': '🇳🇿', 'HAI': '🇭🇹'
      }
      return flags[code] || '🏳️'
    }

    function getContinent(code) {
      const continents = {
        'EU': '欧洲', 'SA': '南美', 'NA': '北美', 'AF': '非洲',
        'AS': '亚洲', 'OC': '大洋洲'
      }
      return continents[code] || code
    }

    function getFactorName(key) {
      const names = {
        'elo_diff': 'Elo实力差',
        'rank_diff': '排名差距',
        'form_diff': '状态差异',
        'stage_factor': '赛事阶段',
        'home_advantage': '主场优势',
        'continent_factor': '洲际因素',
        'h2h': '历史交锋',
        'wc_experience': '世界杯经验',
        'squad_strength': '球员阵容',
        'coach_rating': '教练能力',
        'venue_factor': '场地影响'
      }
      return names[key] || key
    }

    function getDiffClass(value) {
      if (value > 20) return 'positive'
      if (value < -20) return 'negative'
      return 'neutral'
    }

    function getNormPosition(value) {
      // 标准化值在[-1, 1]，映射到[50%, 100%]
      return 50 + (Math.min(1, Math.max(-1, value)) * 50) - Math.abs(value) * 50
    }

    function getPredictionClass(pred) {
      return {
        'HOME_WIN': 'home-win',
        'DRAW': 'draw',
        'AWAY_WIN': 'away-win'
      }[pred] || ''
    }

    function getResultLabel(pred) {
      return {
        'HOME_WIN': '主胜',
        'DRAW': '平局',
        'AWAY_WIN': '客胜'
      }[pred] || pred
    }

    return {
      close,
      getTeamFlag,
      getContinent,
      getFactorName,
      getDiffClass,
      getNormPosition,
      getPredictionClass,
      getResultLabel
    }
  }
}
</script>

<style scoped>
.calc-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 10px;
  animation: fadeIn 0.2s ease;
}

.calc-dialog {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

.calc-header {
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

.calc-title {
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

.calc-body {
  padding: 16px;
}

/* 比赛信息卡片 */
.match-info-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 20px;
  color: white;
  margin-bottom: 16px;
}

.match-teams {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.team-block {
  text-align: center;
  flex: 1;
}

.team-flag {
  font-size: 2.5rem;
  margin-bottom: 8px;
}

.team-name {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.team-code {
  font-size: 0.75rem;
  opacity: 0.8;
}

.vs-text {
  font-size: 1.2rem;
  font-weight: 700;
  opacity: 0.6;
  padding: 0 10px;
}

.match-meta {
  text-align: center;
  font-size: 0.85rem;
  opacity: 0.9;
}

/* 步骤区块 */
.step-section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.step-badge {
  width: 28px;
  height: 28px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
}

.step-title {
  font-weight: 600;
  color: #333;
  font-size: 0.95rem;
}

.step-note {
  font-size: 0.75rem;
  color: #888;
  margin-left: auto;
}

/* 球队数据网格 */
.team-data-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.data-item {
  background: white;
  padding: 10px;
  border-radius: 8px;
}

.data-label {
  font-size: 0.75rem;
  color: #888;
  margin-bottom: 6px;
}

.data-values {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.home-val, .away-val {
  font-weight: 600;
  font-size: 0.9rem;
}

.home-val { color: #27ae60; }
.away-val { color: #3498db; }

.vs-line {
  width: 1px;
  height: 12px;
  background: #ddd;
}

.data-diff {
  font-size: 0.75rem;
  text-align: center;
}

.data-diff.positive { color: #27ae60; }
.data-diff.negative { color: #e74c3c; }
.data-diff.neutral { color: #888; }

/* 因子表格 */
.factors-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.factor-row {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr 1.5fr 1fr;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #eee;
  font-size: 0.85rem;
}

.factor-row.header {
  background: #f5f5f5;
  font-weight: 600;
  color: #666;
  font-size: 0.75rem;
}

.factor-name {
  color: #333;
}

.factor-raw {
  font-family: monospace;
  color: #666;
}

.factor-norm {
  display: flex;
  align-items: center;
  gap: 6px;
}

.norm-bar {
  width: 60px;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

.norm-fill {
  position: absolute;
  height: 100%;
  background: #667eea;
  border-radius: 4px;
}

.norm-zero {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 1px;
  background: #999;
}

.norm-val {
  font-family: monospace;
  font-size: 0.75rem;
  color: #667eea;
}

.factor-meaning {
  font-size: 0.75rem;
  color: #888;
}

/* 权重计算 */
.weight-calc-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.weight-item {
  background: white;
  padding: 10px;
  border-radius: 8px;
}

.weight-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.weight-name {
  font-size: 0.8rem;
  font-weight: 500;
}

.weight-val {
  font-size: 0.75rem;
  color: #667eea;
  font-weight: 600;
}

.weight-bar-bg {
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  margin-bottom: 6px;
}

.weight-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 3px;
}

.weight-calc {
  font-size: 0.75rem;
  font-family: monospace;
  color: #666;
}

.calc-num { color: #667eea; }
.calc-op { color: #999; margin: 0 2px; }
.calc-result { color: #27ae60; font-weight: 600; }

.total-contribution {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  padding: 12px;
  text-align: center;
  color: white;
  margin-top: 12px;
}

.total-label {
  font-size: 0.85rem;
  opacity: 0.9;
  margin-bottom: 4px;
}

.total-value {
  font-size: 1.5rem;
  font-weight: 700;
}

.total-explain {
  font-size: 0.85rem;
  opacity: 0.9;
  margin-top: 4px;
}

/* 概率计算 */
.probability-calc {
  background: white;
  border-radius: 8px;
  padding: 16px;
}

.prob-formula {
  font-size: 0.75rem;
  color: #888;
  text-align: center;
  margin-bottom: 16px;
  font-family: monospace;
}

.prob-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.prob-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.prob-label {
  width: 40px;
  font-size: 0.85rem;
  font-weight: 600;
}

.prob-bar-wrap {
  flex: 1;
  height: 28px;
  background: #f0f0f0;
  border-radius: 14px;
  position: relative;
  overflow: hidden;
}

.prob-bar {
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 12px;
  transition: width 0.5s ease;
}

.prob-bar.home { background: linear-gradient(90deg, #27ae60, #2ecc71); }
.prob-bar.draw { background: linear-gradient(90deg, #f39c12, #f1c40f); }
.prob-bar.away { background: linear-gradient(90deg, #3498db, #5dade2); }

.prob-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

/* 预测结果 */
.step-section.final {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.step-section.final .step-badge {
  background: white;
  color: #667eea;
}

.step-section.final .step-title {
  color: white;
}

.prediction-result {
  text-align: center;
}

.result-badge {
  display: inline-block;
  padding: 12px 32px;
  border-radius: 12px;
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 12px;
}

.result-badge.home-win { background: #27ae60; }
.result-badge.draw { background: #f39c12; }
.result-badge.away-win { background: #3498db; }

.result-detail {
  font-size: 0.95rem;
  margin-bottom: 12px;
}

.confidence {
  font-size: 0.85rem;
  opacity: 0.9;
}

.result-note {
  font-size: 0.75rem;
  opacity: 0.8;
  padding: 10px;
  background: rgba(255,255,255,0.15);
  border-radius: 8px;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
</style>
