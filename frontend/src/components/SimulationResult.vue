<template>
  <div class="simulation-result">
    <!-- 模式切换 -->
    <div class="mode-selector">
      <button :class="['mode-btn', { active: mode === 'strict' }]" @click="setMode('strict')">
        🔬 严谨模式
      </button>
      <button :class="['mode-btn', { active: mode === 'prob' }]" @click="setMode('prob')">
        🎲 概率模式
      </button>
    </div>
    
    <button class="simulate-btn" @click="runSimulation" :disabled="simulating">
      {{ simulating ? '模拟中...' : '🚀 开始模拟' }}
    </button>

    <!-- 结果展示 -->
    <div v-if="result" class="result-container">
      <!-- 对阵图 -->
      <BracketView 
        :knockout="result.knockout"
        :championCn="result.champion_name_cn"
        :runnerUpCn="result.runner_up_name_cn"
        :thirdPlaceCn="result.third_place_name_cn"
        :mode="mode"
      />
      
      <!-- 冠军之路 -->
      <div class="champion-path">
        <h4 class="path-title">🛤️ {{ result.champion_name_cn }} 的夺冠之路</h4>
        <div class="path-steps">
          <div v-for="(step, idx) in championPath" :key="idx" class="path-step">
            <span class="step-round">{{ step.round }}</span>
            <span class="step-opp">{{ step.opponent }}</span>
            <span class="step-score">{{ step.score }}</span>
            <span class="step-check">✓</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import BracketView from './BracketView.vue'

export default {
  components: { BracketView },
  setup() {
    const mode = ref('strict')
    const simulating = ref(false)
    const result = ref(null)
    
    function setMode(m) { mode.value = m }
    
    async function runSimulation() {
      simulating.value = true
      try {
        const resp = await fetch(`/worldcup/api/simulate?mode=${mode.value}`)
        result.value = await resp.json()
      } catch(e) { console.error(e) }
      simulating.value = false
    }
    
    const championPath = computed(() => {
      if (!result.value) return []
      const champion = result.value.champion
      const path = []
      const rounds = [
        { key: 'R32', name: '32强' },
        { key: 'R16', name: '16强' },
        { key: 'QF', name: '1/4决赛' },
        { key: 'SF', name: '半决赛' },
        { key: 'FI', name: '决赛' }
      ]
      
      for (const r of rounds) {
        for (const m of result.value.knockout[r.key] || []) {
          if (m.winner === champion) {
            const opponent = m.home === champion ? m.away_name_cn : m.home_name_cn
            path.push({
              round: r.name,
              opponent: opponent,
              score: `${m.home_score}:${m.away_score}`
            })
          }
        }
      }
      return path
    })
    
    return { mode, simulating, result, setMode, runSimulation, championPath }
  }
}
</script>

<style scoped>
.mode-selector { display:flex; gap:8px; margin-bottom:12px; }
.mode-btn { padding:8px 18px; border-radius:8px; border:none; background:#e8e8e8; cursor:pointer; font-weight:500; font-size:0.9rem; }
.mode-btn.active { background:#1a472a; color:white; }
.simulate-btn { width:100%; padding:16px; background:#1a472a; color:white; border-radius:12px; font-size:1.05rem; font-weight:600; border:none; cursor:pointer; margin-bottom:16px; }
.simulate-btn:disabled { opacity:0.6; }

.path-title { font-size:0.95rem; font-weight:600; margin:16px 0 10px; }
.champion-path { background:white; border-radius:10px; padding:14px; margin-top:14px; }
.path-steps { display:flex; flex-wrap:wrap; gap:8px; }
.path-step { display:flex; align-items:center; gap:8px; background:#f0f7f0; padding:7px 11px; border-radius:6px; font-size:0.8rem; }
.step-round { color:#666; font-weight:500; }
.step-opp { flex:1; }
.step-score { font-weight:700; color:#1a472a; }
.step-check { color:#28a745; font-weight:700; }
</style>