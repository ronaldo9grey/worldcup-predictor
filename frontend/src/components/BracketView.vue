<template>
  <div class="bracket-container">
    <!-- 标题 -->
    <div class="bracket-header">
      <span class="header-title">⚔️ 淘汰赛对阵图</span>
      <span class="header-mode">{{ modeText }}</span>
    </div>

    <!-- 竖向对阵图：每轮一列 -->
    <div class="bracket-columns">
      <!-- 32强 -->
      <div class="round-column">
        <div class="round-title">32强</div>
        <div class="matches-column">
          <MatchBlock v-for="m in r32" :key="m.match_num" :match="m" />
        </div>
      </div>

      <div class="connect-area">
        <div v-for="i in 16" :key="'ca1-'+i" class="conn-dot"></div>
      </div>

      <!-- 16强 -->
      <div class="round-column">
        <div class="round-title">16强</div>
        <div class="matches-column">
          <MatchBlock v-for="m in r16" :key="m.match_num" :match="m" />
        </div>
      </div>

      <div class="connect-area">
        <div v-for="i in 8" :key="'ca2-'+i" class="conn-dot"></div>
      </div>

      <!-- 1/4决赛 -->
      <div class="round-column">
        <div class="round-title">1/4决赛</div>
        <div class="matches-column">
          <MatchBlock v-for="m in qf" :key="m.match_num" :match="m" />
        </div>
      </div>

      <div class="connect-area">
        <div v-for="i in 4" :key="'ca3-'+i" class="conn-dot"></div>
      </div>

      <!-- 半决赛 -->
      <div class="round-column semi-round">
        <div class="round-title semi-title">半决赛</div>
        <div class="matches-column">
          <MatchBlock v-for="m in sf" :key="m.match_num" :match="m" semi />
        </div>
      </div>

      <div class="connect-area">
        <div v-for="i in 2" :key="'ca4-'+i" class="conn-dot"></div>
      </div>

      <!-- 决赛圈 -->
      <div class="round-column final-round">
        <div class="round-title gold-title">🏆 决赛圈</div>
        
        <!-- 季军赛 -->
        <div class="final-match" v-if="thirdMatch">
          <div class="match-subtitle bronze">🥉 季军赛</div>
          <MatchBlock :match="thirdMatch" third />
        </div>

        <!-- 决赛 -->
        <div class="final-match" v-if="finalMatch">
          <div class="match-subtitle gold">🏆 决赛</div>
          <MatchBlock :match="finalMatch" final />
        </div>

        <!-- 领奖台 -->
        <div class="podium" v-if="championCn">
          <div class="podium-second">
            <span class="medal">🥈</span>
            <span class="podium-team">{{ runnerUpCn }}</span>
          </div>
          <div class="podium-first">
            <span class="medal">🥇</span>
            <span class="podium-team champion">{{ championCn }}</span>
            <span class="trophy">🏆</span>
          </div>
          <div class="podium-third">
            <span class="medal">🥉</span>
            <span class="podium-team">{{ thirdPlaceCn || '待定' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import MatchBlock from './MatchBlock.vue'

export default {
  components: { MatchBlock },
  props: {
    knockout: Object,
    championCn: String,
    runnerUpCn: String,
    thirdPlaceCn: String,
    mode: { type: String, default: 'strict' }
  },
  setup(props) {
    const r32 = computed(() => props.knockout?.R32 || [])
    const r16 = computed(() => props.knockout?.R16 || [])
    const qf = computed(() => props.knockout?.QF || [])
    const sf = computed(() => props.knockout?.SF || [])
    const thirdMatch = computed(() => props.knockout?.THIRD?.[0])
    const finalMatch = computed(() => props.knockout?.FI?.[0])
    const modeText = computed(() => props.mode === 'strict' ? '严谨模式' : '概率模式')

    return { r32, r16, qf, sf, thirdMatch, finalMatch, modeText }
  }
}
</script>

<style scoped>
.bracket-container { background:#f5f7f5; border-radius:12px; padding:12px; }
.bracket-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; padding:0 4px; }
.header-title { font-size:1rem; font-weight:700; color:#1a472a; }
.header-mode { font-size:0.75rem; background:#e8e8e8; padding:3px 10px; border-radius:10px; color:#666; }

.bracket-columns { display:flex; gap:0; overflow-x:auto; }
.round-column { min-width:120px; display:flex; flex-direction:column; }
.round-title { font-size:0.8rem; font-weight:700; color:#666; text-align:center; padding:6px 8px; background:#e5e5e5; border-radius:6px; margin-bottom:10px; }
.semi-title { background:#1a472a; color:white; }
.gold-title { background:linear-gradient(135deg,#ffd700,#ffec80); color:#333; }

.matches-column { display:flex; flex-direction:column; gap:6px; flex:1; }

.connect-area { display:flex; flex-direction:column; justify-content:space-around; min-width:20px; padding:20px 0; }
.conn-dot { width:100%; height:2px; background:linear-gradient(to right,#c0d0c0,#e0e0e0); }

.final-round { min-width:140px; background:white; border-radius:10px; padding:10px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
.final-match { margin-bottom:12px; }
.match-subtitle { font-size:0.75rem; font-weight:600; margin-bottom:6px; text-align:center; }
.match-subtitle.bronze { color:#cd7f32; }
.match-subtitle.gold { color:#b8860b; font-size:0.85rem; }

.podium { display:flex; justify-content:center; align-items:flex-end; gap:8px; margin-top:14px; padding-top:12px; border-top:1px solid #eee; }
.podium-first, .podium-second, .podium-third { display:flex; flex-direction:column; align-items:center; padding:10px 14px; border-radius:8px 8px 0 0; }
.podium-first { background:linear-gradient(180deg,#ffd700,#ffec80); order:2; min-height:80px; }
.podium-second { background:linear-gradient(180deg,#c0c0c0,#e8e8e8); order:1; min-height:60px; }
.podium-third { background:linear-gradient(180deg,#cd7f32,#e8c8a8); order:3; min-height:50px; }
.medal { font-size:1.5rem; }
.podium-team { font-weight:600; margin-top:4px; font-size:0.8rem; text-align:center; }
.podium-team.champion { font-size:0.95rem; font-weight:700; }
.trophy { font-size:1.2rem; margin-top:4px; }
</style>