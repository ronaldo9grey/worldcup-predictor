<template>
  <div class="groups-view">
    <div v-if="loading" class="loading"><div class="spinner"></div></div>
    <template v-else>
      <div class="groups-grid">
        <div v-for="gname in 'ABCDEFGHIJKL'.split('')" :key="gname" class="group-card" @click="toggleGroup(gname)">
          <div class="group-card-header">
            <span class="group-letter">{{ gname }}</span>
            <span class="group-label">组</span>
            <span class="expand-icon">{{ expanded === gname ? '▲' : '▼' }}</span>
          </div>
          <div v-if="groupCache[gname]" class="group-preview">
            <div v-for="t in groupCache[gname].standings.slice(0,4)" :key="t.code" class="preview-row">
              <span :class="['qualify-dot', t.position <= 2 ? 'dot-green' : t.position === 3 ? 'dot-yellow' : 'dot-gray']"></span>
              <span class="preview-name">{{ t.name_cn }}</span>
              <span class="preview-rank">#{{ t.rank }}</span>
              <span class="preview-pts">{{ t.points }}分</span>
            </div>
          </div>
          <div v-else class="preview-loading">加载中...</div>
        </div>
      </div>

      <div v-if="expanded && groupCache[expanded]" class="group-detail-panel">
        <div class="detail-header">
          <span class="detail-title">{{ expanded }}组详情</span>
          <button class="close-btn" @click="expanded = null">✕</button>
        </div>

        <div class="standings-visual">
          <div class="standings-header">
            <span class="standings-title">🏆 积分榜</span>
            <span class="standings-note">（基于预测结果，实际比赛积分）</span>
          </div>
          <div class="standings-bars">
            <div v-for="t in groupCache[expanded].standings" :key="t.code" 
                 :class="['standing-row', {'qualified': t.position <= 2}]">
              <span :class="['pos-badge', 'pos-' + t.position]">{{ t.position }}</span>
              <span class="team-flag">{{ getTeamFlag(t.code) }}</span>
              <span class="team-name">{{ t.name_cn }}</span>
              <span class="team-rank">FIFA #{{ t.rank }}</span>
              <span class="team-points">{{ t.points }}分</span>
              <span class="team-prob" v-if="qualificationData[expanded]">
                {{ getQualificationProb(t.code) }}%
              </span>
              <span class="team-prob" v-else>-</span>
            </div>
          </div>
        </div>

        <div class="detail-matches">
          <div class="detail-subtitle">赛程预测</div>
          <div v-for="(m, idx) in groupCache[expanded].matches" :key="idx" class="detail-match">
            <div class="dm-top">
              <div class="dm-teams">
                <span :class="{'dm-predicted': m.prediction === 'HOME_WIN' || m.prediction === '主胜'}">{{ m.home_name_cn }}</span>
                <span class="dm-vs">vs</span>
                <span :class="{'dm-predicted': m.prediction === 'AWAY_WIN' || m.prediction === '客胜'}">{{ m.away_name_cn }}</span>
              </div>
            </div>
            <div class="dm-bar">
              <div class="dm-bar-h" :style="{width: m.home_win_prob*100+'%'}"></div>
              <div class="dm-bar-d" :style="{width: m.draw_prob*100+'%'}"></div>
              <div class="dm-bar-a" :style="{width: m.away_win_prob*100+'%'}"></div>
            </div>
            <div class="dm-bottom">
              <span class="dm-result">{{ getPredIcon(m.prediction) }} {{ getPredText(m.prediction) }}</span>
              <span :class="['dm-conf', 'conf-'+getConfLevel(m.confidence)]">{{ getConfText(m.confidence) }}</span>
              <button class="calc-btn" @click="showCalculation(expanded, idx, m)">🧠 贝叶斯预测分析</button>
              <button class="model-btn" @click="showModelPrediction(expanded, idx)">📊 三模型对比</button>
            </div>
          </div>
        </div>
      </div>
    </template>
    
    <MatchCalculation :visible="showCalc" :calculation="currentCalc" @close="showCalc = false" />
    <ModelPrediction :visible="showModelPred" :prediction="currentModelPred" @close="showModelPred = false" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import MatchCalculation from './MatchCalculation.vue'
import ModelPrediction from './ModelPrediction.vue'

const loading = ref(false)
const expanded = ref(null)
const groupCache = reactive({})
const showCalc = ref(false)
const currentCalc = ref(null)
const showModelPred = ref(false)
const currentModelPred = ref(null)

const TEAM_FLAGS = {
  'ARG': '🇦🇷', 'BRA': '🇧🇷', 'FRA': '🇫🇷', 'ENG': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'GER': '🇩🇪', 'ESP': '🇪🇸',
  'POR': '🇵🇹', 'NED': '🇳🇱', 'BEL': '🇧🇪', 'CRO': '🇭🇷', 'SUI': '🇨🇭', 'MEX': '🇲🇽', 'JPN': '🇯🇵',
  'KOR': '🇰🇷', 'AUS': '🇦🇺', 'USA': '🇺🇸', 'CAN': '🇨🇦', 'COL': '🇨🇴', 'URU': '🇺🇾', 'ECU': '🇪🇨',
  'SEN': '🇸🇳', 'MAR': '🇲🇦', 'EGY': '🇪🇬', 'NGA': '🇳🇬', 'CMR': '🇨🇲', 'GHA': '🇬🇭', 'TUN': '🇹🇳',
  'ZAF': '🇿🇦', 'CZE': '🇨🇿', 'POL': '🇵🇱', 'SWE': '🇸🇪', 'NOR': '🇳🇴', 'AUT': '🇦🇹', 'SRB': '🇷🇸',
  'IRN': '🇮🇷', 'SAU': '🇸🇦', 'QAT': '🇶🇦', 'UZB': '🇺🇿', 'JOR': '🇯🇴', 'IRQ': '🇮🇶'
}

function getTeamFlag(code) { return TEAM_FLAGS[code] || '⚽' }
function getBarWidth(points) { return Math.min(100, (points / 9) * 100) }
function getPredIcon(p) { 
  const iconMap = { HOME_WIN: '🏠', DRAW: '🤝', AWAY_WIN: '✈️', '主胜': '🏠', '平局': '🤝', '客胜': '✈️' }
  return iconMap[p] || '' 
}
function getPredText(p) { 
  const textMap = { HOME_WIN: '主胜', DRAW: '平', AWAY_WIN: '客胜', '主胜': '主胜', '平局': '平', '客胜': '客胜' }
  return textMap[p] || p || '' 
}
function getConfLevel(c) {
  const levelMap = { HIGH: 'high', MEDIUM: 'medium', LOW: 'low', '高': 'high', '中': 'medium', '低': 'low' }
  return levelMap[c] || 'medium'
}
function getConfText(c) {
  const textMap = { HIGH: '高', MEDIUM: '中', LOW: '低', '高': '高', '中': '中', '低': '低' }
  return textMap[c] || c || '中'
}

const qualificationData = ref({})

async function loadQualificationProb(g) {
  if (qualificationData.value[g]) return
  try {
    const resp = await fetch(`/worldcup/api/groups/${g}/qualification`)
    qualificationData.value[g] = await resp.json()
  } catch (e) {
    console.error('加载出线概率失败:', e)
  }
}

function getQualificationProb(code) {
  const g = expanded.value
  if (!qualificationData.value[g]) return '-'
  const data = qualificationData.value[g]?.qualification_probability || []
  const team = data.find(t => t.code === code)
  return team ? team.qualification_prob : '-'
}

async function loadGroup(g) {
  if (groupCache[g]) return
  loading.value = true
  try {
    const resp = await fetch(`/worldcup/api/groups/${g}`)
    groupCache[g] = await resp.json()
    // 不再自动加载出线概率，改为按需加载
  } catch(e) { console.error(e) }
  loading.value = false
}


async function toggleGroup(g) {
  if (expanded.value === g) { expanded.value = null; return }
  await loadGroup(g)
  expanded.value = g
  // 展开时加载出线概率（懒加载）
  await loadQualificationProb(g)
}


async function showCalculation(group, idx, match) {
  try {
    const resp = await fetch(`/worldcup/api/calculation/match/${group}/${idx}`)
    currentCalc.value = await resp.json()
    showCalc.value = true
  } catch (e) { console.error(e) }
}

async function showModelPrediction(group, idx) {
  try {
    const resp = await fetch(`/worldcup/api/models/predict/group/${group}/${idx}`)
    currentModelPred.value = await resp.json()
    showModelPred.value = true
  } catch (e) { console.error(e) }
}

onMounted(async () => {
  const names = 'ABCDEFGHIJKL'.split('')
  await Promise.all(names.map(g => loadGroup(g)))
})
</script>

<style scoped>
.groups-grid { display:grid; grid-template-columns:repeat(4, 1fr); gap:10px; margin-bottom:16px; }
.group-card { background:white; border-radius:8px; padding:10px; cursor:pointer; transition:all 0.2s; }
.group-card:hover { box-shadow:0 2px 8px rgba(0,0,0,0.1); }
.group-card-header { display:flex; align-items:baseline; margin-bottom:8px; }
.group-letter { font-size:1.2rem; font-weight:700; color:#1a472a; }
.group-label { font-size:0.8rem; color:#666; margin-left:3px; }
.expand-icon { margin-left:auto; font-size:0.7rem; color:#999; }
.preview-row { display:flex; align-items:center; gap:5px; padding:2px 0; font-size:0.8rem; }
.qualify-dot { width:6px; height:6px; border-radius:50%; }
.dot-green { background:#28a745; }
.dot-yellow { background:#ffc107; }
.dot-gray { background:#ccc; }
.preview-loading { font-size:0.75rem; color:#999; padding:8px 0; text-align:center; }

.group-detail-panel { background:white; border-radius:10px; padding:14px; }
.detail-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
.detail-title { font-weight:700; font-size:1rem; color:#1a472a; }
.close-btn { background:none; border:none; font-size:1.1rem; cursor:pointer; color:#999; }

.standings-visual { margin-bottom:16px; }
.standings-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
.standings-title { font-weight:700; font-size:0.9rem; color:#1a472a; }
.simulate-btn { padding:4px 10px; background:#667eea; color:white; border:none; border-radius:6px; font-size:0.75rem; cursor:pointer; }
.standings-bars { display:flex; flex-direction:column; gap:6px; }
.standing-row { display:flex; align-items:center; gap:8px; padding:6px 8px; background:#f8f9fa; border-radius:6px; }
.standing-row.qualified { background:#e8f5e9; border-left:3px solid #28a745; }
.pos-badge { width:20px; height:20px; display:flex; align-items:center; justify-content:center; border-radius:50%; font-size:0.7rem; font-weight:700; }
.pos-1 { background:#ffd700; color:#000; }
.pos-2 { background:#c0c0c0; color:#000; }
.pos-3 { background:#cd7f32; color:#fff; }
.pos-4 { background:#e0e0e0; color:#666; }
.team-flag { font-size:1rem; }
.team-name { font-weight:600; font-size:0.85rem; }
.team-rank { font-size:0.7rem; color:#999; }
.standing-bar-wrap { flex:1; background:#e0e0e0; border-radius:4px; height:16px; overflow:hidden; }
.standing-bar { height:100%; background:linear-gradient(90deg,#1a472a,#2d5a3d); padding-left:8px; color:white; font-size:0.7rem; font-weight:600; }

.detail-subtitle { font-size:0.85rem; font-weight:600; margin-bottom:8px; color:#333; }
.detail-match { padding:8px; background:#f8f9fa; border-radius:6px; margin-bottom:8px; }
.dm-top { margin-bottom:4px; }
.dm-teams { display:flex; justify-content:center; align-items:center; gap:10px; font-size:0.85rem; }
.dm-predicted { font-weight:700; color:#1a472a; }
.dm-vs { color:#999; font-size:0.75rem; }
.dm-bar { display:flex; height:6px; border-radius:3px; overflow:hidden; margin-bottom:4px; }
.dm-bar-h { background:#28a745; }
.dm-bar-d { background:#999; }
.dm-bar-a { background:#dc3545; }
.dm-bottom { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:6px; }
.dm-result { font-size:0.75rem; }
.dm-conf { padding:2px 8px; border-radius:10px; font-size:0.65rem; font-weight:600; }
.conf-high { background:#28a745; color:white; }
.conf-medium { background:#ffc107; color:black; }
.conf-low { background:#999; color:white; }
.calc-btn, .model-btn { padding:4px 10px; border:none; border-radius:6px; font-size:0.75rem; cursor:pointer; }
.calc-btn { background:#667eea; color:white; }
.model-btn { background:#28a745; color:white; }

@media (max-width: 768px) {
  .groups-grid { grid-template-columns:repeat(2, 1fr); }
}
</style>
