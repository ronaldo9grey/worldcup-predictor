<template>
  <div class="algorithm-info" v-if="info">
    <h3 style="margin-bottom:16px">{{ info.name }}</h3>
    
    <div class="section-title">📊 预测因子</div>
    <div class="factor-list">
      <div v-for="factor in info.factors" :key="factor.key" class="factor-item">
        <div class="factor-header">
          <span class="factor-icon">{{ factor.icon }}</span>
          <span class="factor-name">{{ factor.name }}</span>
          <span class="factor-weight">权重 {{ (factor.weight * 100).toFixed(0) }}%</span>
        </div>
        <div class="factor-desc">{{ factor.description }}</div>
        <div class="factor-how">{{ factor.how_it_works }}</div>
        <div class="factor-bar">
          <div class="bar-track" :style="{width: factor.weight*100+'%'}"></div>
        </div>
      </div>
    </div>

    <div class="section-title" style="margin-top:24px">📐 核心公式</div>
    <div class="formula-box">
      <div class="formula">{{ info.formula }}</div>
      <div class="formula">{{ info.probability }}</div>
    </div>

    <div class="section-title" style="margin-top:24px">❄️ 冷门判断</div>
    <ul class="cold-warm-list">
      <li v-for="(item, idx) in info.cold_warm" :key="idx">{{ item }}</li>
    </ul>
  </div>
</template>

<script>
export default { props: { info: Object } }
</script>

<style scoped>
.algorithm-info { background:white; border-radius:12px; padding:16px; }
.section-title { font-size:0.95rem; font-weight:600; margin-bottom:12px; color:#1a472a; }
.factor-list { display:flex; flex-direction:column; gap:12px; }
.factor-item { background:#f8f9fa; border-radius:8px; padding:12px; }
.factor-header { display:flex; align-items:center; gap:8px; margin-bottom:6px; }
.factor-icon { font-size:1.2rem; }
.factor-name { font-weight:600; flex:1; }
.factor-weight { background:#1a472a; color:white; padding:2px 8px; border-radius:10px; font-size:0.7rem; }
.factor-desc { font-size:0.85rem; color:#333; margin-bottom:4px; }
.factor-how { font-size:0.8rem; color:#666; margin-bottom:8px; }
.factor-bar { height:6px; background:#e0e0e0; border-radius:3px; }
.bar-track { height:100%; background:#1a472a; border-radius:3px; }
.formula-box { background:#f0f7f0; border-radius:8px; padding:12px; }
.formula { font-family:monospace; font-size:0.85rem; margin:4px 0; }
.cold-warm-list { padding-left:20px; font-size:0.85rem; }
.cold-warm-list li { margin:6px 0; }
</style>