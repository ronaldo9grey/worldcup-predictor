<template>
  <div :class="['match-card-wrapper', { semi: semi, final: final, third: third }]">
    <div :class="['team-row', { won: match.winner === match.home }]">
      <span class="flag">{{ getFlag(match.home) }}</span>
      <span class="team-name">{{ match.home_name_cn }}</span>
      <span class="score">{{ match.home_score }}</span>
      <span v-if="match.winner === match.home && !final" class="winner-dot">✓</span>
      <span v-if="match.winner === match.home && final" class="crown-icon">👑</span>
    </div>
    <div :class="['team-row', { won: match.winner === match.away }]">
      <span class="flag">{{ getFlag(match.away) }}</span>
      <span class="team-name">{{ match.away_name_cn }}</span>
      <span class="score">{{ match.away_score }}</span>
      <span v-if="match.winner === match.away && !final" class="winner-dot">✓</span>
      <span v-if="match.winner === match.away && final" class="crown-icon">👑</span>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    match: { type: Object, required: true },
    semi: { type: Boolean, default: false },
    final: { type: Boolean, default: false },
    third: { type: Boolean, default: false }
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
.match-card-wrapper { background:white; border-radius:4px; overflow:hidden; box-shadow:0 1px 2px rgba(0,0,0,0.06); }
.match-card-wrapper.semi { border:1px solid #1a472a; }
.match-card-wrapper.final { border:2px solid #ffd700; background:linear-gradient(135deg,#fffef5,#fff); }
.match-card-wrapper.third { border:1px solid #cd7f32; }

.team-row { display:flex; align-items:center; padding:3px 6px; font-size:0.7rem; border-bottom:1px solid #f5f5f5; }
.team-row:last-child { border-bottom:none; }
.team-row.won { background:#e8f5e9; font-weight:600; }
.match-card-wrapper.final .team-row.won { background:#fff9e6; }

.flag { margin-right:4px; font-size:0.8rem; }
.team-name { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:0.65rem; }
.score { font-weight:700; min-width:14px; text-align:center; color:#1a472a; font-size:0.7rem; }
.winner-dot { margin-left:3px; color:#28a745; font-weight:700; font-size:0.6rem; }
.crown-icon { margin-left:3px; font-size:0.7rem; }
</style>