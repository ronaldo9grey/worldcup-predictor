<template>
  <div class="match-detail">
    <h3 style="margin-bottom:12px">{{ data.match.home.name_cn }} vs {{ data.match.away.name_cn }}</h3>
    
    <!-- 概率显示 -->
    <div class="prob-display">
      <div class="prob-item">
        <div class="prob-label">主胜</div>
        <div class="prob-value">{{ Math.round(data.prediction.home_win_prob*100) }}%</div>
      </div>
      <div class="prob-item">
        <div class="prob-label">平局</div>
        <div class="prob-value">{{ Math.round(data.prediction.draw_prob*100) }}%</div>
      </div>
      <div class="prob-item">
        <div class="prob-label">客胜</div>
        <div class="prob-value">{{ Math.round(data.prediction.away_win_prob*100) }}%</div>
      </div>
    </div>

    <!-- 因子可视化 -->
    <div class="section-title">🔍 预测因子拆解</div>
    <div class="factors-chart">
      <div v-for="factor in data.factors" :key="factor.key" class="factor-row">
        <div class="factor-left">
          <span class="factor-icon">{{ factor.icon }}</span>
          <span class="factor-name">{{ factor.name }}</span>
        </div>
        <div class="factor-bar-container">
          <div 
            class="factor-bar"
            :style="{ 
              width: Math.abs(factor.weighted_contribution)*100+'%',
              background: factor.color,
              marginLeft: factor.weighted_contribution >= 0 ? '50%' : 'auto'
            }"
          ></div>
        </div>
        <span :class="['factor-val', factor.contribution >= 0 ? 'positive' : 'negative']">
          {{ factor.contribution >= 0 ? '+' : '' }}{{ (factor.weighted_contribution*100).toFixed(1) }}
        </span>
      </div>
    </div>
    <div class="factor-legend">
      <span>← 倾向客队</span>
      <span>|</span>
      <span>倾向主队 →</span>
    </div>

    <!-- 因子说明 -->
    <div class="factor-details">
      <div v-for="factor in data.factors" :key="factor.key" class="factor-detail-item">
        <span style="color:gray">{{ factor.icon }} {{ factor.name }}:</span>
        <span>{{ factor.desc }}</span>
      </div>
    </div>

    <!-- 冷门分析 -->
    <div v-if="data.upset.is_upset" class="upset-alert">
      <span>🔥 冷门指数: {{ data.upset.score }}</span>
      <span class="upset-tag">{{ data.upset.factors.join('、') }}</span>
    </div>

    <button class="close-btn" @click="$emit('close')">关闭</button>
  </div>
</template>

<script>
export default {
  props: { data: Object },
  emits: ['close']
}
</script>

<style scoped>
.match-detail { max-height:80vh; overflow-y:auto; }
.prob-display { display:flex; gap:12px; margin-bottom:16px; }
.prob-item { flex:1; text-align:center; background:#f8f9fa; padding:12px; border-radius:8px; }
.prob-label { font-size:0.8rem; color:#666; margin-bottom:4px; }
.prob-value { font-size:1.4rem; font-weight:700; color:#1a472a; }
.section-title { font-size:0.9rem; font-weight:600; margin:12px 0; }
.factors-chart { display:flex; flex-direction:column; gap:8px; }
.factor-row { display:flex; align-items:center; gap:8px; font-size:0.85rem; }
.factor-left { display:flex; align-items:center; gap:6px; width:90px; flex-shrink:0; }
.factor-icon { font-size:1rem; }
.factor-name { font-size:0.8rem; }
.factor-bar-container { flex:1; height:14px; background:#f0f0f0; border-radius:4px; position:relative; }
.factor-bar { height:100%; border-radius:4px; position:absolute; right:50%; }
.factor-val { width:50px; text-align:right; font-size:0.8rem; font-weight:600; }
.factor-val.positive { color:#28a745; }
.factor-val.negative { color:#dc3545; }
.factor-legend { display:flex; justify-content:center; gap:20px; font-size:0.75rem; color:#999; margin-top:8px; }
.factor-details { background:#f8f9fa; border-radius:8px; padding:10px; margin-top:12px; font-size:0.8rem; }
.factor-detail-item { margin:4px 0; }
.upset-alert { background:#fff5f5; border:1px solid #dc3545; border-radius:8px; padding:10px; margin-top:12px; font-size:0.85rem; }
.upset-tag { display:block; margin-top:4px; color:#dc3545; font-size:0.8rem; }
.close-btn { width:100%; margin-top:16px; padding:10px; background:#1a472a; color:white; border:none; border-radius:8px; cursor:pointer; }
</style>