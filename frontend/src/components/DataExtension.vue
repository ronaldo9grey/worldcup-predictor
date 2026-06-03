<template>
  <div class="data-extension">
    <h2>📊 数据扩展面板</h2>
    
    <!-- 数据源概览 -->
    <div class="data-sources">
      <div class="source-card" v-for="(source, key) in dataSources" :key="key">
        <h3>{{ source.name }}</h3>
        <p class="description">{{ source.description }}</p>
        <p class="update">更新频率：{{ source.update_frequency }}</p>
      </div>
    </div>
    
    <!-- 球队选择 -->
    <div class="team-selector">
      <h3>选择球队查看详情</h3>
      <select v-model="selectedTeam" @change="loadTeamData">
        <option value="">请选择球队</option>
        <option v-for="team in teams" :key="team.code" :value="team.code">
          {{ team.name_cn }} ({{ team.code }})
        </option>
      </select>
    </div>
    
    <!-- 数据详情 -->
    <div v-if="selectedTeam" class="data-details">
      <!-- 伤病情况 -->
      <div class="detail-card injury-card">
        <h3>🏥 伤病情况</h3>
        <div v-if="injuryData.injury_count === 0" class="no-injury">
          ✅ 无伤病球员
        </div>
        <div v-else>
          <div class="risk-badge" :class="injuryData.risk_level">
            {{ injuryData.risk_label }}
          </div>
          <div class="injury-list">
            <div v-for="injury in injuryData.injury_list" :key="injury.player_name" class="injury-item">
              <span class="player">{{ injury.player_name_cn }}</span>
              <span class="status" :class="injury.status">{{ getStatusLabel(injury.status) }}</span>
              <span v-if="injury.injury_type" class="type">{{ getInjuryTypeLabel(injury.injury_type) }}</span>
              <span v-if="injury.notes" class="notes">{{ injury.notes }}</span>
            </div>
          </div>
          <div class="impact-score">
            影响系数：{{ injuryData.impact_coefficient.toFixed(3) }}
          </div>
        </div>
      </div>
      
      <!-- 社交情感 -->
      <div class="detail-card sentiment-card">
        <h3>💬 社交媒体情感</h3>
        <div class="sentiment-metrics">
          <div class="metric">
            <span class="label">整体情感</span>
            <div class="progress-bar">
              <div class="fill" :style="{ width: sentimentData.overall_sentiment * 100 + '%' }"></div>
              <span class="value">{{ (sentimentData.overall_sentiment * 100).toFixed(0) }}%</span>
            </div>
          </div>
          <div class="metric">
            <span class="label">球迷信心</span>
            <div class="progress-bar">
              <div class="fill" :style="{ width: sentimentData.confidence_level * 100 + '%' }"></div>
              <span class="value">{{ (sentimentData.confidence_level * 100).toFixed(0) }}%</span>
            </div>
          </div>
          <div class="metric">
            <span class="label">讨论热度</span>
            <div class="progress-bar">
              <div class="fill" :style="{ width: sentimentData.buzz_score + '%' }"></div>
              <span class="value">{{ sentimentData.buzz_score }}</span>
            </div>
          </div>
        </div>
        
        <div class="keywords">
          <div class="keyword-group">
            <span class="group-label">热议词：</span>
            <span v-for="kw in sentimentData.recent_keywords" :key="kw" class="keyword positive">
              {{ kw }}
            </span>
          </div>
          <div v-if="sentimentData.negative_keywords.length" class="keyword-group">
            <span class="group-label">担忧词：</span>
            <span v-for="kw in sentimentData.negative_keywords" :key="kw" class="keyword negative">
              {{ kw }}
            </span>
          </div>
        </div>
        
        <div class="pressure-info">
          <span class="label">球迷期望：</span>
          <span class="value">{{ getExpectationLabel(sentimentData.fan_expectation) }}</span>
          <span class="label">压力等级：</span>
          <span class="value">{{ getPressureLabel(sentimentData.pressure_level) }}</span>
        </div>
      </div>
    </div>
    
    <!-- 热门球队排名 -->
    <div class="trending-section">
      <h3>🔥 讨论热度TOP 10</h3>
      <div class="trending-list">
        <div v-for="team in trendingTeams" :key="team.team" class="trending-item">
          <span class="rank">{{ team.rank }}</span>
          <span class="team">{{ getTeamNameCn(team.team) }}</span>
          <div class="buzz-bar">
            <div class="fill" :style="{ width: team.buzz_score + '%' }"></div>
            <span class="score">{{ team.buzz_score }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 冠军赔率 -->
    <div class="outright-odds">
      <h3>🏆 冠军赔率</h3>
      <div class="odds-section">
        <h4>热门球队</h4>
        <div class="odds-list">
          <div v-for="team in championshipOdds.favorites" :key="team.team" class="odds-item">
            <span class="rank">{{ team.rank }}</span>
            <span class="team">{{ getTeamNameCn(team.team) }}</span>
            <span class="odds">{{ team.odds.toFixed(2) }}</span>
            <span class="prob">{{ (team.probability * 100).toFixed(1) }}%</span>
          </div>
        </div>
      </div>
      <div class="odds-section">
        <h4>潜在黑马</h4>
        <div class="odds-list">
          <div v-for="team in championshipOdds.dark_horses" :key="team.team" class="odds-item">
            <span class="team">{{ getTeamNameCn(team.team) }}</span>
            <span class="odds">{{ team.odds.toFixed(2) }}</span>
            <span class="prob">{{ (team.probability * 100).toFixed(1) }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'DataExtension',
  setup() {
    const selectedTeam = ref('')
    const teams = ref([])
    const injuryData = ref({
      injury_count: 0,
      injury_list: [],
      risk_level: 'low',
      risk_label: '',
      impact_coefficient: 0
    })
    const sentimentData = ref({
      overall_sentiment: 0.5,
      confidence_level: 0.5,
      buzz_score: 50,
      recent_keywords: [],
      negative_keywords: [],
      fan_expectation: 'moderate',
      pressure_level: 'low'
    })
    const trendingTeams = ref([])
    const championshipOdds = ref({ favorites: [], dark_horses: [], outsiders: [] })
    const dataSources = ref({})
    
    // 加载球队列表
    const loadTeams = async () => {
      try {
        // 获取所有小组数据
        const groups = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        const allTeams = []
        for (const group of groups) {
          const response = await fetch(`/worldcup/api/groups/${group}`)
          if (response.ok) {
            const data = await response.json()
            if (data && data.standings) {
              data.standings.forEach(team => {
                allTeams.push({
                  code: team.code,
                  name: team.name,
                  name_cn: team.name_cn,
                  rank: team.rank
                })
              })
            }
          }
        }
        teams.value = allTeams
      } catch (error) {
        console.error('加载球队失败', error)
      }
    }
    
    // 加载球队数据
    const loadTeamData = async () => {
      if (!selectedTeam.value) return
      
      try {
        // 加载伤病数据
        const injuryRes = await fetch(`/worldcup/api/data-extension/injuries/${selectedTeam.value}`)
        injuryData.value = await injuryRes.json()
        
        // 加载情感数据
        const sentimentRes = await fetch(`/worldcup/api/data-extension/sentiment/${selectedTeam.value}`)
        sentimentData.value = await sentimentRes.json()
      } catch (error) {
        console.error('加载数据失败', error)
      }
    }
    
    // 加载热度排名
    const loadTrendingTeams = async () => {
      try {
        const response = await fetch('/worldcup/api/data-extension/sentiment/trending')
        trendingTeams.value = await response.json()
      } catch (error) {
        console.error('加载热度排名失败', error)
      }
    }
    
    // 加载冠军赔率
    const loadChampionshipOdds = async () => {
      try {
        const response = await fetch('/worldcup/api/data-extension/odds/championship')
        championshipOdds.value = await response.json()
      } catch (error) {
        console.error('加载冠军赔率失败', error)
      }
    }
    
    // 加载数据源信息
    const loadDataSources = async () => {
      try {
        const response = await fetch('/worldcup/api/data-extension/data-sources')
        dataSources.value = await response.json()
      } catch (error) {
        console.error('加载数据源失败', error)
      }
    }
    
    // 辅助函数
    const getTeamNameCn = (code) => {
      const team = teams.value.find(t => t.code === code)
      if (team) return team.name_cn
      
      // 英文名映射
      const nameMap = {
        'Argentina': '阿根廷',
        'France': '法国',
        'Brazil': '巴西',
        'England': '英格兰',
        'Germany': '德国',
        'Spain': '西班牙',
        'Portugal': '葡萄牙',
        'Netherlands': '荷兰',
        'Uruguay': '乌拉圭',
        'Belgium': '比利时',
        'Croatia': '克罗地亚',
        'USA': '美国',
        'Mexico': '墨西哥',
        'Japan': '日本',
        'South Korea': '韩国',
        'Senegal': '塞内加尔',
        'Morocco': '摩洛哥',
      }
      return nameMap[code] || code
    }
    
    const getStatusLabel = (status) => {
      const labels = {
        healthy: '健康',
        doubtful: '出战成疑',
        questionable: '可能缺席',
        out: '缺席'
      }
      return labels[status] || status
    }
    
    const getInjuryTypeLabel = (type) => {
      const labels = {
        muscle: '肌肉',
        knee: '膝盖',
        ankle: '脚踝',
        hamstring: '腿筋',
        groin: '腹股沟',
        back: '背部',
        shoulder: '肩部',
        concussion: '脑震荡',
        covid: '新冠',
        fatigue: '疲劳'
      }
      return labels[type] || type
    }
    
    const getExpectationLabel = (expectation) => {
      const labels = {
        high: '高期望',
        moderate: '适中',
        low: '低期望'
      }
      return labels[expectation] || expectation
    }
    
    const getPressureLabel = (pressure) => {
      const labels = {
        extreme: '极高压力',
        high: '高压',
        moderate: '适中',
        low: '低压'
      }
      return labels[pressure] || pressure
    }
    
    onMounted(() => {
      loadTeams()
      loadTrendingTeams()
      loadChampionshipOdds()
      loadDataSources()
    })
    
    return {
      selectedTeam,
      teams,
      injuryData,
      sentimentData,
      trendingTeams,
      championshipOdds,
      dataSources,
      loadTeamData,
      getTeamNameCn,
      getStatusLabel,
      getInjuryTypeLabel,
      getExpectationLabel,
      getPressureLabel
    }
  }
}
</script>

<style scoped>
.data-extension {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

h3 {
  color: #444;
  margin-bottom: 15px;
}

/* 数据源卡片 */
.data-sources {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.source-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.source-card h3 {
  color: white;
  margin: 0 0 10px 0;
}

.source-card .description {
  opacity: 0.9;
  margin: 5px 0;
}

.source-card .update {
  font-size: 0.85em;
  opacity: 0.8;
}

/* 球队选择器 */
.team-selector {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.team-selector select {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  margin-top: 10px;
}

/* 数据详情 */
.data-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.detail-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 伤病卡片 */
.injury-card .no-injury {
  color: #4caf50;
  font-size: 18px;
  text-align: center;
  padding: 20px;
}

.risk-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  margin-bottom: 15px;
}

.risk-badge.low { background: #e8f5e9; color: #2e7d32; }
.risk-badge.moderate { background: #fff3e0; color: #f57c00; }
.risk-badge.high { background: #fce4ec; color: #c2185b; }
.risk-badge.critical { background: #ffebee; color: #d32f2f; }

.injury-list {
  margin: 15px 0;
}

.injury-item {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 8px;
}

.injury-item .player { font-weight: bold; }
.injury-item .status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.status.healthy { background: #c8e6c9; color: #2e7d32; }
.status.doubtful { background: #fff9c4; color: #f57f17; }
.status.questionable { background: #ffe0b2; color: #e65100; }
.status.out { background: #ffcdd2; color: #c62828; }

.impact-score {
  text-align: right;
  font-size: 14px;
  color: #666;
  margin-top: 10px;
}

/* 情感卡片 */
.sentiment-metrics {
  margin: 15px 0;
}

.metric {
  margin-bottom: 15px;
}

.metric .label {
  display: block;
  margin-bottom: 5px;
  color: #666;
}

.progress-bar {
  position: relative;
  height: 24px;
  background: #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
}

.progress-bar .fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 12px;
  transition: width 0.3s;
}

.progress-bar .value {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-weight: bold;
  color: #333;
}

.keywords {
  margin: 15px 0;
}

.keyword-group {
  margin-bottom: 10px;
}

.keyword-group .group-label {
  font-weight: bold;
  margin-right: 10px;
}

.keyword {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 13px;
  margin: 3px;
}

.keyword.positive { background: #e8f5e9; color: #2e7d32; }
.keyword.negative { background: #ffebee; color: #c62828; }

.pressure-info {
  display: flex;
  gap: 20px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.pressure-info .label {
  color: #666;
  margin-right: 5px;
}

/* 热门排名 */
.trending-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.trending-list {
  margin-top: 15px;
}

.trending-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.trending-item:last-child {
  border-bottom: none;
}

.trending-item .rank {
  font-weight: bold;
  color: #667eea;
  min-width: 30px;
}

.trending-item .team {
  min-width: 100px;
}

.buzz-bar {
  flex: 1;
  position: relative;
  height: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

.buzz-bar .fill {
  height: 100%;
  background: linear-gradient(90deg, #ff6b6b, #ffa500);
  border-radius: 10px;
}

.buzz-bar .score {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  font-weight: bold;
}

/* 冠军赔率 */
.outright-odds {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.odds-section {
  margin: 15px 0;
}

.odds-section h4 {
  color: #666;
  margin-bottom: 10px;
}

.odds-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.odds-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 8px;
}

.odds-item .rank {
  font-weight: bold;
  color: #667eea;
}

.odds-item .team {
  font-weight: bold;
}

.odds-item .odds {
  color: #e53935;
  font-weight: bold;
}

.odds-item .prob {
  color: #666;
  font-size: 14px;
}

/* 响应式 */
@media (max-width: 768px) {
  .data-details {
    grid-template-columns: 1fr;
  }
  
  .data-sources {
    grid-template-columns: 1fr;
  }
}
</style>
