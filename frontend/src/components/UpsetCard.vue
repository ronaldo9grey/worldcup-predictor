<template>
  <div :class="['match-card', `upset-${level}`]">
    <div class="match-header">
      <span>{{ formatTime(match.match_time) }}</span>
      <span :class="['match-stage', level === 'high' ? 'stage-danger' : 'stage-warning']">
        {{ level === 'high' ? '🔴 高冷门' : '🟡 中冷门' }}
      </span>
    </div>

    <div class="teams-vs">
      <div class="team">
        <div class="team-name">{{ match.home_team_name }}</div>
        <div class="team-rank">FIFA #{{ match.home_team_rank }}</div>
      </div>
      <div class="vs-text">VS</div>
      <div class="team">
        <div class="team-name">{{ match.away_team_name }}</div>
        <div class="team-rank">FIFA #{{ match.away_team_rank }}</div>
      </div>
    </div>

    <div class="prediction-bar">
      <div class="prob-segment prob-home" :style="{ width: match.home_win_prob * 100 + '%' }">
        {{ Math.round(match.home_win_prob * 100) }}%
      </div>
      <div class="prob-segment prob-draw" :style="{ width: match.draw_prob * 100 + '%' }">
        {{ Math.round(match.draw_prob * 100) }}%
      </div>
      <div class="prob-segment prob-away" :style="{ width: match.away_win_prob * 100 + '%' }">
        {{ Math.round(match.away_win_prob * 100) }}%
      </div>
    </div>

    <div class="upset-detail">
      <div class="upset-detail-row">
        <span>冷门指数</span>
        <span class="upset-score">{{ match.upset_score }}</span>
      </div>
      <div class="upset-detail-row">
        <span>预测方向</span>
        <span>{{ getPredictionText(match.prediction) }}</span>
      </div>
    </div>

    <div v-if="match.upset_factors?.length" class="upset-factors">
      <span v-for="(factor, idx) in match.upset_factors" :key="idx" class="factor-tag">
        {{ factor }}
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UpsetCard',
  props: {
    match: { type: Object, required: true },
    level: { type: String, default: 'medium' }
  },
  methods: {
    formatTime(isoString) {
      const date = new Date(isoString)
      return `${date.getMonth()+1}月${date.getDate()}日 ${date.getHours().toString().padStart(2,'0')}:00`
    },
    getPredictionText(prediction) {
      return { 'HOME_WIN': '主胜', 'DRAW': '平局', 'AWAY_WIN': '客胜' }[prediction] || '未知'
    }
  }
}
</script>

<style scoped>
.stage-danger {
  background: var(--danger) !important;
}
.stage-warning {
  background: var(--warning) !important;
  color: black !important;
}
.upset-detail {
  display: flex;
  justify-content: space-between;
  margin: 12px 0;
  padding: 8px;
  background: var(--bg);
  border-radius: 8px;
}
.upset-detail-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 0.85rem;
}
.upset-detail-row span:first-child {
  color: var(--text-muted);
  font-size: 0.75rem;
  margin-bottom: 4px;
}
</style>