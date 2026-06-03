<template>
  <div class="team-predictor">
    <h3 style="margin-bottom:16px">🎯 自定义比赛预测</h3>
    
    <div class="selector-row">
      <select v-model="homeTeam" class="team-select">
        <option value="">选择主队</option>
        <option v-for="team in teams" :key="team.fifa_code" :value="team.fifa_code">
          {{ team.name }} ({{ team.fifa_rank }})
        </option>
      </select>

      <span class="vs-label">VS</span>

      <select v-model="awayTeam" class="team-select">
        <option value="">选择客队</option>
        <option v-for="team in teams" :key="team.fifa_code" :value="team.fifa_code">
          {{ team.name }} ({{ team.fifa_rank }})
        </option>
      </select>
    </div>

    <button 
      class="predict-btn" 
      :disabled="!homeTeam || !awayTeam || homeTeam === awayTeam || predicting"
      @click="doPredict"
    >
      {{ predicting ? '预测中...' : '开始预测' }}
    </button>

    <!-- 预测结果 -->
    <div v-if="prediction" class="prediction-result-panel">
      <h4 style="margin-bottom:12px">预测结果</h4>
      
      <div class="teams-vs">
        <div class="team">
          <div class="team-name">{{ prediction.home_team.name }}</div>
          <div class="team-rank">Elo: {{ prediction.home_team.elo_rating }}</div>
        </div>
        <div class="vs-text">VS</div>
        <div class="team">
          <div class="team-name">{{ prediction.away_team.name }}</div>
          <div class="team-rank">Elo: {{ prediction.away_team.elo_rating }}</div>
        </div>
      </div>

      <div class="prediction-bar">
        <div class="prob-segment prob-home" :style="{ width: prediction.prediction.home_win_prob * 100 + '%' }">
          {{ Math.round(prediction.prediction.home_win_prob * 100) }}%
        </div>
        <div class="prob-segment prob-draw" :style="{ width: prediction.prediction.draw_prob * 100 + '%' }">
          {{ Math.round(prediction.prediction.draw_prob * 100) }}%
        </div>
        <div class="prob-segment prob-away" :style="{ width: prediction.prediction.away_win_prob * 100 + '%' }">
          {{ Math.round(prediction.prediction.away_win_prob * 100) }}%
        </div>
      </div>

      <div style="text-align:center;margin:16px 0">
        <span style="font-size:1.5rem">{{ getPredictionIcon(prediction.prediction.prediction) }}</span>
        <span style="margin-left:8px;font-weight:600">
          {{ getPredictionText(prediction.prediction.prediction) }}
        </span>
        <span :class="['confidence-badge', `confidence-${prediction.prediction.confidence}`]" style="margin-left:12px">
          {{ prediction.prediction.confidence === 'HIGH' ? '高信心' : prediction.prediction.confidence === 'MEDIUM' ? '中信心' : '低信心' }}
        </span>
      </div>

      <div v-if="prediction.prediction.is_potential_upset" class="upset-indicator">
        <span>🔥 冷门指数: {{ prediction.prediction.upset_score }}</span>
      </div>

      <div class="analysis-panel">
        <h5 style="margin-bottom:8px;color:var(--text-muted)">分析要点</h5>
        <div v-for="(item, key) in prediction.analysis" :key="key" class="analysis-item">
          <span>{{ formatAnalysisKey(key) }}:</span>
          <span>{{ item }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

const API_BASE = '/worldcup/api'

export default {
  name: 'TeamPredictor',
  props: {
    teams: { type: Array, default: () => [] }
  },
  setup(props) {
    const homeTeam = ref('')
    const awayTeam = ref('')
    const predicting = ref(false)
    const prediction = ref(null)

    async function doPredict() {
      if (!homeTeam.value || !awayTeam.value) return
      
      predicting.value = true
      try {
        const resp = await fetch(`${API_BASE}/predict`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            home_team: homeTeam.value,
            away_team: awayTeam.value
          })
        })
        prediction.value = await resp.json()
      } catch (e) {
        console.error('预测失败:', e)
      } finally {
        predicting.value = false
      }
    }

    function getPredictionIcon(p) {
      return { 'HOME_WIN': '🏠', 'DRAW': '🤝', 'AWAY_WIN': '✈️' }[p] || '❓'
    }

    function getPredictionText(p) {
      return { 'HOME_WIN': '主队胜', 'DRAW': '平局', 'AWAY_WIN': '客队胜' }[p] || '未知'
    }

    function formatAnalysisKey(key) {
      const names = {
        'elo_diff': 'Elo差距',
        'rank_diff': '排名差距',
        'form_comparison': '近期状态对比',
        'upset_analysis': '冷门分析'
      }
      return names[key] || key
    }

    return {
      homeTeam, awayTeam, predicting, prediction,
      doPredict, getPredictionIcon, getPredictionText, formatAnalysisKey
    }
  }
}
</script>

<style scoped>
.vs-label {
  font-weight: bold;
  color: var(--primary);
  font-size: 1.1rem;
}
.predict-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.prediction-result-panel {
  margin-top: 20px;
  padding: 16px;
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.analysis-panel {
  margin-top: 16px;
  padding: 12px;
  background: var(--bg);
  border-radius: 8px;
}
.analysis-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 0.9rem;
  border-bottom: 1px solid var(--border);
}
.analysis-item:last-child {
  border-bottom: none;
}
.analysis-item span:first-child {
  color: var(--text-muted);
}
</style>