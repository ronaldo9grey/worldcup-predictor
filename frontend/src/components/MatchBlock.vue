<template>
  <div :class="['match-block', { semi: semi, final: final, third: third }]" :style="heightStyle">
    <div :class="['team-line', { won: match.winner === match.home }]">
      <span class="flag">{{ getFlag(match.home) }}</span>
      <span class="team">{{ match.home_name_cn || match.home }}</span>
      <span class="score">{{ match.home_score }}</span>
      <span v-if="match.winner === match.home" class="win-mark">✓</span>
    </div>
    <div :class="['team-line', { won: match.winner === match.away }]">
      <span class="flag">{{ getFlag(match.away) }}</span>
      <span class="team">{{ match.away_name_cn || match.away }}</span>
      <span class="score">{{ match.away_score }}</span>
      <span v-if="match.winner === match.away" class="win-mark">✓</span>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    match: { type: Object, required: true },
    semi: { type: Boolean, default: false },
    final: { type: Boolean, default: false },
    third: { type: Boolean, default: false },
    height: { type: String, default: 'auto' }
  },
  computed: {
    heightStyle() {
      return this.height !== 'auto' ? { height: this.height } : {}
    }
  },
  methods: {
    getFlag(code) {
      const flags = {
        ARG:'🇦🇷',BRA:'🇧🇷',FRA:'🇫🇷',ENG:'🏴󠁧󠁢󠁥󠁮󠁧️',BEL:'🇧🇪',POR:'🇵🇹',NED:'🇳🇱',ESP:'🇪🇸',
        CRO:'🇭🇷',GER:'🇩🇪',SUI:'🇨🇭',DEN:'🇩🇰',AUT:'🇦🇹',SWE:'🇸🇪',NOR:'🇳🇴',SRB:'🇷🇸',TUR:'🇹🇷',UKR:'🇺🇦',
        MAR:'🇲🇦',SEN:'🇸🇳',CIV:'🇨🇮',NGA:'🇳🇬',ALG:'🇩🇿',EGY:'🇪🇬',TUN:'🇹🇳',CMR:'🇨🇲',GHA:'🇬🇭',COD:'🇨🇩',
        USA:'🇺🇸',MEX:'🇲🇽',CAN:'🇨🇦',PAN:'🇵🇦',HAI:'🇭🇹',CUW:'🇨🇼',
        JPN:'🇯🇵',IRN:'🇮🇷',KOR:'🇰🇷',AUS:'🇦🇺',JOR:'🇯🇴',UZB:'🇺🇿',SAU:'🇸🇦',QAT:'🇶🇦',CHN:'🇨🇳',
        COL:'🇨🇴',URU:'🇺🇾',ECU:'🇪🇨',PAR:'🇵🇾',NZL:'🇳🇿',
      }
      return flags[code] || '🏳️'
    }
  }
}
</script>

<style scoped>
.match-block { background:white; border-radius:6px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.08); display:flex; flex-direction:column; }
.match-block.semi { border:1px solid #1a472a; }
.match-block.final { border:2px solid #ffd700; background:linear-gradient(135deg,#fffef5,#fff); }
.match-block.third { border:1px solid #cd7f32; }

.team-line { display:flex; align-items:center; padding:6px 8px; border-bottom:1px solid #f0f0f0; }
.team-line:last-child { border-bottom:none; }
.team-line.won { background:#e8f5e9; font-weight:600; }
.match-block.final .team-line.won { background:#fff9e6; }

.flag { margin-right:8px; font-size:1rem; }
.team { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:0.85rem; }
.score { font-weight:700; min-width:20px; text-align:center; color:#1a472a; font-size:0.9rem; }
.win-mark { margin-left:6px; color:#28a745; font-weight:700; font-size:0.8rem; }
</style>