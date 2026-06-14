<template>
  <div class="history-module">
    <!-- 子导航 -->
    <div class="sub-tabs">
      <div :class="['sub-tab', { active: activeSub === 'value' }]" @click="activeSub = 'value'">💰 身价排行</div>
      <div :class="['sub-tab', { active: activeSub === 'pedigree' }]" @click="activeSub = 'pedigree'">🏆 世界杯底蕴</div>
      <div :class="['sub-tab', { active: activeSub === 'h2h' }]" @click="activeSub = 'h2h'">⚔️ 历史交锋</div>
    </div>

    <!-- 身价排行 -->
    <div v-if="activeSub === 'value'" class="value-section">
      <div class="section-title">球队身价排行榜（百万欧元）</div>
      <div class="value-list">
        <div v-for="(team, idx) in teams" :key="team.code" class="value-row">
          <div class="value-rank">{{ idx + 1 }}</div>
          <div class="value-team">
            <span class="team-flag">{{ getFlag(team.code) }}</span>
            <span class="team-name">{{ team.name_cn }}</span>
            <span class="team-info">{{ team.rank }}位 · {{ team.elo }} Elo</span>
          </div>
          <div class="value-bar-wrap">
            <div class="value-bar" :style="{ width: (team.team_value / maxValue * 100) + '%', background: getTierColor(team.team_value) }"></div>
          </div>
          <div class="value-amount">{{ team.team_value }}M</div>
          <div class="value-tier" :class="team.tier">{{ getTierLabel(team.team_value) }}</div>
        </div>
      </div>
      <div class="tier-legend">
        <span class="tier tier1">一流强队 (≥800M)</span>
        <span class="tier tier2">二流强队 (≥400M)</span>
        <span class="tier tier3">三流球队 (≥200M)</span>
        <span class="tier tier4">弱旅 (<200M)</span>
      </div>
    </div>

    <!-- 世界杯底蕴 -->
    <div v-if="activeSub === 'pedigree'" class="pedigree-section">
      <div class="section-title">世界杯底蕴排行</div>
      <div class="pedigree-list">
        <div v-for="(team, idx) in pedigreeTeams" :key="team.code" class="pedigree-row">
          <div class="pedigree-rank">{{ idx + 1 }}</div>
          <div class="pedigree-team">
            <span class="team-flag">{{ getFlag(team.code) }}</span>
            <span class="team-name">{{ team.name_cn }}</span>
          </div>
          <div class="pedigree-stats">
            <div class="stat-item titles">
              <span class="stat-icon">🏆</span>
              <span class="stat-val">{{ team.titles }}</span>
              <span class="stat-label">冠军</span>
            </div>
            <div class="stat-item finals">
              <span class="stat-icon">🥈</span>
              <span class="stat-val">{{ team.finals }}</span>
              <span class="stat-label">决赛</span>
            </div>
            <div class="stat-item appearances">
              <span class="stat-icon">📊</span>
              <span class="stat-val">{{ team.world_cup_experience }}</span>
              <span class="stat-label">参赛</span>
            </div>
          </div>
          <div class="pedigree-badge" :class="team.pedigree">{{ getPedigreeLabel(team.pedigree) }}</div>
        </div>
      </div>
    </div>

    <!-- 历史交锋 -->
    <div v-if="activeSub === 'h2h'" class="h2h-section">
      <div class="section-title">历史交锋查询</div>
      <div class="h2h-selector">
        <select v-model="selectedTeamA" class="team-select">
          <option value="">选择球队A</option>
          <option v-for="t in teams" :key="t.code" :value="t.code">{{ t.name_cn }}</option>
        </select>
        <span class="vs-label">VS</span>
        <select v-model="selectedTeamB" class="team-select">
          <option value="">选择球队B</option>
          <option v-for="t in teams" :key="t.code" :value="t.code">{{ t.name_cn }}</option>
        </select>
        <button class="query-btn" @click="queryH2H" :disabled="!selectedTeamA || !selectedTeamB">查询</button>
      </div>
      
      <div v-if="h2hData" class="h2h-result">
        <div class="h2h-summary">
          <div class="h2h-team-block">
            <div class="team-flag large">{{ getFlag(selectedTeamA) }}</div>
            <div class="team-name-cn">{{ getTeamName(selectedTeamA) }}</div>
            <div class="h2h-wins">{{ h2hData.summary[selectedTeamA + '_wins'] }}胜</div>
          </div>
          <div class="h2h-center">
            <div class="h2h-total">{{ h2hData.summary.total }}场交锋</div>
            <div class="h2h-draws">{{ h2hData.summary.draws }}平</div>
          </div>
          <div class="h2h-team-block">
            <div class="team-flag large">{{ getFlag(selectedTeamB) }}</div>
            <div class="team-name-cn">{{ getTeamName(selectedTeamB) }}</div>
            <div class="h2h-wins">{{ h2hData.summary[selectedTeamB + '_wins'] }}胜</div>
          </div>
        </div>
        
        <div v-if="h2hData.recent_matches.length > 0" class="h2h-matches">
          <div class="matches-title">经典对决</div>
          <div v-for="m in h2hData.recent_matches" :key="m.id" class="match-record">
            <div class="match-date">{{ m.match_date }}</div>
            <div class="match-competition">{{ m.competition }}</div>
            <div class="match-score">
              <span :class="{ winner: m.home_score > m.away_score }">{{ m.home_code }} {{ m.home_score }}</span>
              <span class="score-sep">-</span>
              <span :class="{ winner: m.away_score > m.home_score }">{{ m.away_score }} {{ m.away_code }}</span>
            </div>
          </div>
        </div>
        
        <div v-else class="no-data">暂无交锋记录</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  setup() {
    const activeSub = ref('value')
    const teams = ref([])
    const selectedTeamA = ref('')
    const selectedTeamB = ref('')
    const h2hData = ref(null)
    
    const maxValue = computed(() => {
      return teams.value.reduce((max, t) => Math.max(max, t.team_value || 0), 0)
    })
    
    const pedigreeTeams = computed(() => {
      return teams.value
        .map(t => ({
          ...t,
          pedigree: getPedigreeLevel(t)
        }))
        .sort((a, b) => {
          // 先按冠军数，再按决赛数，再按参赛次数
          if (b.titles !== a.titles) return b.titles - a.titles
          if (b.finals !== a.finals) return b.finals - a.finals
          return b.world_cup_experience - a.world_cup_experience
        })
    })
    
    async function loadTeams() {
      try {
        const resp = await fetch('/worldcup/api/data/teams')
        const data = await resp.json()
        teams.value = data.teams || []
      } catch (e) {
        console.error('加载球队数据失败', e)
        teams.value = []
      }
    }
    
    async function queryH2H() {
      if (!selectedTeamA.value || !selectedTeamB.value) return
      try {
        const resp = await fetch(`/worldcup/api/data/h2h/${selectedTeamA.value}/${selectedTeamB.value}`)
        h2hData.value = await resp.json()
      } catch (e) {
        console.error('查询交锋失败', e)
        h2hData.value = null
      }
    }
    
    function getFlag(code) {
      // 简化的旗帜映射（用emoji代替）
      const flags = {
        'ARG': '🇦🇷', 'BRA': '🇧🇷', 'FRA': '🇫🇷', 'ENG': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
        'GER': '🇩🇪', 'ESP': '🇪🇸', 'ITA': '🇮🇹', 'POR': '🇵🇹',
        'NED': '🇳🇱', 'BEL': '🇧🇪', 'CRO': '🇭🇷', 'URU': '🇺🇾',
        'USA': '🇺🇸', 'MEX': '🇲🇽', 'JPN': '🇯🇵', 'KOR': '🇰🇷',
        'SEN': '🇸🇳', 'MAR': '🇲🇦', 'COL': '🇨🇴', 'CHN': '🇨🇳',
        'AUS': '🇦🇺', 'CAN': '🇨🇦', 'IRN': '🇮🇷', 'SAU': '🇸🇦',
        'QAT': '🇶🇦', 'JOR': '🇯🇴', 'UZB': '🇺🇿',
      }
      return flags[code] || '⚽'
    }
    
    function getTierColor(value) {
      if (value >= 800) return '#27ae60'
      if (value >= 400) return '#f39c12'
      if (value >= 200) return '#e67e22'
      return '#95a5a6'
    }
    
    function getTierLabel(value) {
      if (value >= 800) return '一流'
      if (value >= 400) return '二流'
      if (value >= 200) return '三流'
      return '弱旅'
    }
    
    function getPedigreeLevel(team) {
      if (team.titles >= 3) return 'legendary'
      if (team.titles >= 1) return 'champion'
      if (team.finals >= 1) return 'finalist'
      if (team.world_cup_experience >= 10) return 'regular'
      if (team.world_cup_experience >= 5) return 'occasional'
      return 'newcomer'
    }
    
    function getPedigreeLabel(level) {
      const labels = {
        'legendary': '传奇',
        'champion': '冠军底蕴',
        'finalist': '决赛经验',
        'regular': '常客',
        'occasional': '偶尔参赛',
        'newcomer': '新军'
      }
      return labels[level] || ''
    }
    
    function getTeamName(code) {
      const team = teams.value.find(t => t.code === code)
      return team ? team.name_cn : code
    }
    
    onMounted(() => { loadTeams() })
    
    return {
      activeSub, teams, maxValue, pedigreeTeams,
      selectedTeamA, selectedTeamB, h2hData,
      loadTeams, queryH2H, getFlag, getTierColor, getTierLabel,
      getPedigreeLevel, getPedigreeLabel, getTeamName
    }
  }
}
</script>

<style scoped>
.history-module { padding: 16px; }

/* 子导航 */
.sub-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.sub-tab { 
  padding: 8px 16px; 
  border-radius: 6px; 
  background: #f5f5f5; 
  cursor: pointer; 
  font-size: 0.9rem;
  transition: all 0.2s;
}
.sub-tab.active { background: #1a472a; color: white; }
.sub-tab:hover:not(.active) { background: #e8e8e8; }

/* 通用 */
.section-title { font-size: 1rem; font-weight: 600; margin: 12px 0; color: #333; }

/* 身价排行 */
.value-list { display: flex; flex-direction: column; gap: 8px; }
.value-row { 
  display: flex; align-items: center; gap: 8px; 
  padding: 8px 12px; 
  background: #f8f9fa; 
  border-radius: 6px;
}
.value-rank { 
  width: 28px; height: 28px; 
  display: flex; align-items: center; justify-content: center;
  background: #1a472a; color: white; 
  border-radius: 4px; 
  font-weight: 600;
  font-size: 0.85rem;
}
.value-team { flex: 0 0 140px; }
.team-flag { font-size: 1.2rem; margin-right: 6px; }
.team-name { font-weight: 500; }
.team-info { font-size: 0.75rem; color: #888; margin-left: 8px; }
.value-bar-wrap { flex: 1; height: 8px; background: #e0e0e0; border-radius: 4px; }
.value-bar { height: 100%; border-radius: 4px; transition: width 0.3s; }
.value-amount { width: 60px; text-align: right; font-weight: 600; font-size: 0.9rem; }
.value-tier { 
  padding: 4px 8px; 
  border-radius: 4px; 
  font-size: 0.75rem; 
  font-weight: 500;
}
.value-tier.tier1 { background: #27ae60; color: white; }
.value-tier.tier2 { background: #f39c12; color: white; }
.value-tier.tier3 { background: #e67e22; color: white; }
.value-tier.tier4 { background: #95a5a6; color: white; }

.tier-legend { display: flex; gap: 12px; margin-top: 12px; font-size: 0.8rem; }
.tier-legend .tier { padding: 4px 8px; border-radius: 4px; color: white; }
.tier-legend .tier1 { background: #27ae60; }
.tier-legend .tier2 { background: #f39c12; }
.tier-legend .tier3 { background: #e67e22; }
.tier-legend .tier4 { background: #95a5a6; }

/* 底蕴排行 */
.pedigree-list { display: flex; flex-direction: column; gap: 8px; }
.pedigree-row { 
  display: flex; align-items: center; gap: 8px; 
  padding: 10px 12px; 
  background: #f8f9fa; 
  border-radius: 6px;
}
.pedigree-rank { 
  width: 28px; height: 28px; 
  display: flex; align-items: center; justify-content: center;
  background: #ffd700; color: #333; 
  border-radius: 50%; 
  font-weight: 600;
  font-size: 0.85rem;
}
.pedigree-team { flex: 0 0 100px; }
.pedigree-stats { 
  display: flex; gap: 16px; 
  flex: 1;
}
.stat-item { 
  display: flex; align-items: center; gap: 4px;
  padding: 4px 10px;
  background: white;
  border-radius: 4px;
}
.stat-icon { font-size: 1rem; }
.stat-val { font-weight: 600; font-size: 1rem; }
.stat-label { font-size: 0.7rem; color: #888; }
.stat-item.titles { background: #fff8e8; }
.stat-item.finals { background: #f0f0f0; }
.stat-item.appearances { background: #e8f4e8; }

.pedigree-badge { 
  padding: 6px 12px; 
  border-radius: 6px; 
  font-size: 0.85rem;
  font-weight: 500;
}
.pedigree-badge.legendary { background: linear-gradient(135deg, #ffd700, #ffb700); color: #333; }
.pedigree-badge.champion { background: #27ae60; color: white; }
.pedigree-badge.finalist { background: #3498db; color: white; }
.pedigree-badge.regular { background: #9b59b6; color: white; }
.pedigree-badge.occasional { background: #7f8c8d; color: white; }
.pedigree-badge.newcomer { background: #bdc3c7; color: #333; }

/* 历史交锋 */
.h2h-selector { 
  display: flex; align-items: center; gap: 12px; 
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 8px;
}
.team-select { 
  padding: 8px 12px; 
  border-radius: 6px; 
  border: 1px solid #ddd;
  background: white;
  font-size: 0.9rem;
  min-width: 120px;
}
.vs-label { font-weight: 600; color: #e74c3c; font-size: 1rem; }
.query-btn { 
  padding: 8px 16px; 
  background: #1a472a; 
  color: white; 
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.query-btn:disabled { background: #ccc; cursor: not-allowed; }

.h2h-result { margin-top: 16px; }
.h2h-summary { 
  display: flex; 
  justify-content: space-around; 
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa, #fff);
  border-radius: 12px;
  margin-bottom: 16px;
}
.h2h-team-block { text-align: center; }
.team-flag.large { font-size: 2.5rem; }
.team-name-cn { font-weight: 500; margin: 8px 0; }
.h2h-wins { 
  font-size: 1.5rem; 
  font-weight: 700; 
  color: #27ae60;
}
.h2h-center { text-align: center; }
.h2h-total { font-size: 1.2rem; font-weight: 600; }
.h2h-draws { color: #888; font-size: 0.9rem; margin-top: 4px; }

.h2h-matches { margin-top: 16px; }
.matches-title { font-size: 0.9rem; font-weight: 600; margin-bottom: 12px; }
.match-record { 
  display: flex; align-items: center; gap: 12px;
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 8px;
}
.match-date { font-size: 0.8rem; color: #888; width: 80px; }
.match-competition { font-size: 0.85rem; color: #666; flex: 1; }
.match-score { font-weight: 600; }
.match-score .winner { color: #27ae60; }
.score-sep { margin: 0 8px; }

.no-data { 
  text-align: center; 
  padding: 40px; 
  color: #888;
  font-size: 0.9rem;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .sub-tabs {
    flex-wrap: wrap;
    gap: 6px;
  }
  
  .sub-tab {
    padding: 7px 12px;
    font-size: 0.85rem;
  }
  
  .value-row {
    flex-wrap: wrap;
    gap: 6px;
    padding: 10px;
  }
  
  .value-team {
    flex: 0 0 auto;
    width: 100%;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .team-info {
    margin-left: 0;
    font-size: 0.8rem;
  }
  
  .value-bar-wrap {
    width: 100%;
    order: 1;
  }
  
  .value-amount {
    order: 2;
    width: auto;
    padding-left: 10px;
  }
  
  .value-tier {
    order: 3;
  }
  
  .tier-legend {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .pedigree-row {
    flex-wrap: wrap;
    gap: 8px;
    padding: 12px;
  }
  
  .pedigree-team {
    flex: 0 0 auto;
    width: 100%;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .pedigree-stats {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: space-around;
  }
  
  .stat-item {
    padding: 6px 8px;
  }
  
  .stat-val {
    font-size: 0.9rem;
  }
  
  .h2h-selector {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .team-select {
    min-width: 100px;
    padding: 7px 10px;
  }
  
  .h2h-summary {
    padding: 16px;
  }
  
  .team-flag.large {
    font-size: 2rem;
  }
  
  .h2h-wins {
    font-size: 1.3rem;
  }
  
  .match-record {
    flex-wrap: wrap;
    gap: 6px;
    padding: 8px 10px;
  }
  
  .match-date {
    width: auto;
  }
  
  .match-competition {
    width: 100%;
    order: 1;
  }
}

@media (max-width: 480px) {
  .history-module {
    padding: 12px;
  }
  
  .sub-tabs {
    gap: 5px;
  }
  
  .sub-tab {
    padding: 6px 10px;
    font-size: 0.8rem;
  }
  
  .section-title {
    font-size: 0.95rem;
  }
  
  .value-row {
    padding: 8px;
  }
  
  .value-rank {
    width: 24px;
    height: 24px;
    font-size: 0.8rem;
  }
  
  .team-flag {
    font-size: 1.1rem;
  }
  
  .team-name {
    font-size: 0.9rem;
  }
  
  .team-info {
    font-size: 0.75rem;
  }
  
  .value-amount {
    font-size: 0.85rem;
  }
  
  .value-tier {
    font-size: 0.7rem;
    padding: 3px 6px;
  }
  
  .tier-legend {
    flex-direction: column;
    gap: 6px;
  }
  
  .tier-legend .tier {
    font-size: 0.75rem;
  }
  
  .pedigree-row {
    padding: 10px;
  }
  
  .pedigree-rank {
    width: 24px;
    height: 24px;
    font-size: 0.8rem;
  }
  
  .stat-item {
    padding: 5px 7px;
  }
  
  .stat-icon {
    font-size: 0.9rem;
  }
  
  .stat-val {
    font-size: 0.85rem;
  }
  
  .stat-label {
    font-size: 0.65rem;
  }
  
  .pedigree-badge {
    font-size: 0.8rem;
    padding: 5px 10px;
  }
  
  .h2h-selector {
    padding: 10px;
  }
  
  .team-select {
    min-width: 90px;
    padding: 6px 8px;
    font-size: 0.85rem;
  }
  
  .vs-label {
    font-size: 0.9rem;
  }
  
  .query-btn {
    padding: 7px 14px;
  }
  
  .h2h-summary {
    padding: 12px;
  }
  
  .team-flag.large {
    font-size: 1.8rem;
  }
  
  .team-name-cn {
    font-size: 0.9rem;
  }
  
  .h2h-wins {
    font-size: 1.2rem;
  }
  
  .h2h-total {
    font-size: 1rem;
  }
  
  .h2h-draws {
    font-size: 0.85rem;
  }
  
  .matches-title {
    font-size: 0.85rem;
  }
  
  .match-record {
    padding: 8px;
  }
  
  .match-date {
    font-size: 0.75rem;
  }
  
  .match-competition {
    font-size: 0.8rem;
  }
  
  .match-score {
    font-size: 0.9rem;
  }
}
</style>