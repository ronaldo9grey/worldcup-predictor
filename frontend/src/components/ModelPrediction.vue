<template>
  <div v-if="visible" class="pred-overlay" @click.self="$emit('close')">
    <div class="pred-dialog">
      <div class="pred-header">
        <div class="pred-title">📊 三模型预测对比</div>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>
      
      <div v-if="prediction" class="pred-body">
        <div class="match-title">
          {{ prediction.match?.home }} vs {{ prediction.match?.away }}
        </div>
        
        <div class="models-bars">
          <div v-for="(model, key) in prediction.predictions" :key="key" class="model-row">
            <span class="model-name">{{ getModelLabel(key) }}</span>
            <div class="prob-bars">
              <div class="prob-bar home" :style="{width: (model.home_win * 100) + '%'}">{{ (model.home_win * 100).toFixed(0) }}%</div>
              <div class="prob-bar draw" :style="{width: (model.draw * 100) + '%'}">{{ (model.draw * 100).toFixed(0) }}%</div>
              <div class="prob-bar away" :style="{width: (model.away_win * 100) + '%'}">{{ (model.away_win * 100).toFixed(0) }}%</div>
            </div>
            <span class="pred-label" :class="getResultClass(model.result)">{{ model.result }}</span>
          </div>
          
          <div class="model-row ensemble">
            <span class="model-name">🎯 集成预测</span>
            <div class="prob-bars">
              <div class="prob-bar home" :style="{width: (prediction.ensemble?.home_win * 100) + '%'}">{{ (prediction.ensemble?.home_win * 100).toFixed(0) }}%</div>
              <div class="prob-bar draw" :style="{width: (prediction.ensemble?.draw * 100) + '%'}">{{ (prediction.ensemble?.draw * 100).toFixed(0) }}%</div>
              <div class="prob-bar away" :style="{width: (prediction.ensemble?.away_win * 100) + '%'}">{{ (prediction.ensemble?.away_win * 100).toFixed(0) }}%</div>
            </div>
            <span class="pred-label final">{{ prediction.ensemble?.result }}</span>
          </div>
        </div>
        
        <div class="legend">
          <span><span class="dot home"></span>主胜</span>
          <span><span class="dot draw"></span>平局</span>
          <span><span class="dot away"></span>客胜</span>
        </div>
        
        <div v-if="prediction.analysis" class="analysis">
          <div class="analysis-title">💡 模型分析</div>
          <p>{{ prediction.analysis.consensus || '各模型预测存在差异，建议参考集成预测结果' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: Boolean,
  prediction: Object
})
defineEmits(['close'])

const modelLabels = {
  bayesian: '🧮 贝叶斯',
  neural_network: '🧠 神经网络',
  random_forest: '🌲 随机森林'
}

function getModelLabel(key) {
  return modelLabels[key] || key
}

function getResultClass(result) {
  if (result === '主胜') return 'home-win'
  if (result === '客胜') return 'away-win'
  return 'draw'
}
</script>

<style scoped>
.pred-overlay { position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.5); display:flex; align-items:center; justify-content:center; z-index:1000; padding:16px; }
.pred-dialog { background:white; border-radius:16px; width:90%; max-width:500px; max-height:90vh; overflow-y:auto; box-shadow:0 10px 40px rgba(0,0,0,0.2); }
.pred-header { display:flex; justify-content:space-between; align-items:center; padding:16px 20px; border-bottom:2px solid #e8f5e9; }
.pred-title { font-weight:700; font-size:1.1rem; color:#1a472a; }
.close-btn { background:none; border:none; font-size:1.3rem; cursor:pointer; color:#999; padding:0; width:32px; height:32px; display:flex; align-items:center; justify-content:center; border-radius:8px; }
.close-btn:hover { background:#f5f5f5; color:#666; }
.pred-body { padding:20px; }
.match-title { text-align:center; font-weight:600; font-size:1.1rem; margin-bottom:16px; color:#333; }
.models-bars { display:flex; flex-direction:column; gap:10px; margin-bottom:12px; }
.model-row { display:grid; grid-template-columns:90px 1fr 50px; gap:10px; align-items:center; padding:10px 12px; background:#f8f9fa; border-radius:10px; }
.model-row.ensemble { background:linear-gradient(135deg,#fff8e1,#ffe082); border:2px solid #ffc107; }
.model-name { font-weight:600; font-size:0.85rem; }
.prob-bars { display:flex; height:28px; background:#e0e0e0; border-radius:6px; overflow:hidden; }
.prob-bar { display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:600; color:white; min-width:24px; }
.prob-bar.home { background:linear-gradient(90deg,#4caf50,#66bb6a); }
.prob-bar.draw { background:linear-gradient(90deg,#ff9800,#ffb74d); }
.prob-bar.away { background:linear-gradient(90deg,#f44336,#e57373); }
.pred-label { font-size:0.8rem; font-weight:600; text-align:center; }
.pred-label.home-win { color:#2e7d32; }
.pred-label.draw { color:#e65100; }
.pred-label.away-win { color:#c62828; }
.pred-label.final { background:linear-gradient(135deg,#1b5e20,#2e7d32); color:white; padding:4px 10px; border-radius:6px; }
.legend { display:flex; justify-content:center; gap:24px; padding-top:16px; border-top:1px dashed #ddd; font-size:0.85rem; color:#666; }
.dot { display:inline-block; width:14px; height:14px; border-radius:4px; margin-right:6px; }
.dot.home { background:#4caf50; }
.dot.draw { background:#ff9800; }
.dot.away { background:#f44336; }
.analysis { margin-top:16px; padding:16px; background:#e8f5e9; border-radius:10px; }
.analysis-title { font-weight:600; color:#2e7d32; margin-bottom:8px; font-size:0.95rem; }
.analysis p { font-size:0.85rem; color:#333; margin:0; line-height:1.6; }
</style>
