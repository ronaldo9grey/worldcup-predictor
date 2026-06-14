<template>
  <div class="leaderboard">
    <h2>🏆 排行榜</h2>
    
    <!-- 排序选项 -->
    <div class="sort-tabs">
      <div :class="['tab', { active: sortBy === 'points' }]" @click="changeSort('points')">
        积分榜
      </div>
      <div :class="['tab', { active: sortBy === 'accuracy' }]" @click="changeSort('accuracy')">
        准确率榜
      </div>
      <div :class="['tab', { active: sortBy === 'predictions' }]" @click="changeSort('predictions')">
        预测榜
      </div>
    </div>
    
    <!-- 统计概览 -->
    <div class="stats-overview">
      <div class="stat-item">
        <span class="icon">👥</span>
        <span class="label">总用户</span>
        <span class="value">{{ stats.total_users }}</span>
      </div>
      <div class="stat-item">
        <span class="icon">📊</span>
        <span class="label">总预测</span>
        <span class="value">{{ stats.total_predictions }}</span>
      </div>
      <div class="stat-item">
        <span class="icon">🎯</span>
        <span class="label">平均准确率</span>
        <span class="value">{{ stats.avg_accuracy }}%</span>
      </div>
    </div>
    
    <!-- 排行榜列表 -->
    <div class="leaderboard-list">
      <div v-for="user in leaderboard" :key="user.user_id" 
           :class="['user-item', { 'top-3': user.rank <= 3 }]">
        <!-- 排名 -->
        <div class="rank">
          <span v-if="user.rank === 1" class="medal gold">🥇</span>
          <span v-else-if="user.rank === 2" class="medal silver">🥈</span>
          <span v-else-if="user.rank === 3" class="medal bronze">🥉</span>
          <span v-else class="rank-number">{{ user.rank }}</span>
        </div>
        
        <!-- 用户信息 -->
        <div class="user-info">
          <div class="nickname">{{ user.nickname }}</div>
          <div class="badge" v-if="user.badge">{{ user.badge }}</div>
          <div class="level">
            <span class="level-icon">Lv.{{ user.level }}</span>
            <span class="level-name">{{ user.level_name }}</span>
          </div>
        </div>
        
        <!-- 数据 -->
        <div class="user-data">
          <div class="data-row">
            <span class="data-label">积分</span>
            <span class="data-value">{{ user.total_points }}</span>
          </div>
          <div class="data-row">
            <span class="data-label">预测</span>
            <span class="data-value">{{ user.total_predictions }}场</span>
          </div>
          <div class="data-row">
            <span class="data-label">准确率</span>
            <span class="data-value accuracy">{{ user.accuracy }}%</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 我的排名 -->
    <div v-if="myRanking" class="my-ranking">
      <h3>我的排名</h3>
      <div class="ranking-card">
        <div class="my-rank">
          <span class="rank-number">#{{ myRanking.rank }}</span>
          <span class="percentile">超越{{ myRanking.percentile }}%用户</span>
        </div>
        <div class="my-stats">
          <div class="stat">
            <span class="label">积分</span>
            <span class="value">{{ myRanking.total_points }}</span>
          </div>
          <div class="stat">
            <span class="label">预测</span>
            <span class="value">{{ myRanking.total_predictions }}场</span>
          </div>
          <div class="stat">
            <span class="label">准确率</span>
            <span class="value">{{ myRanking.accuracy }}%</span>
          </div>
        </div>
        <div class="my-badge" v-if="myRanking.badge">
          {{ myRanking.badge }}
        </div>
      </div>
    </div>
    
    <!-- 热门预测 -->
    <div class="hot-predictions">
      <h3>🔥 今日热门预测</h3>
      <div v-for="pred in hotPredictions" :key="pred.match" class="pred-item">
        <div class="match">{{ pred.match }}</div>
        <div class="prediction">{{ pred.prediction }}</div>
        <div class="confidence">{{ pred.confidence }}</div>
        <div class="users">{{ pred.users_count }}人预测</div>
      </div>
    </div>
    
    <!-- 等级说明 -->
    <div class="level-info">
      <h3>📊 等级说明</h3>
      <div class="level-list">
        <div class="level-item">
          <span class="level">Lv.1</span>
          <span class="name">新手球童</span>
          <span class="range">0-49积分</span>
        </div>
        <div class="level-item">
          <span class="level">Lv.2</span>
          <span class="name">替补球员</span>
          <span class="range">50-99积分</span>
        </div>
        <div class="level-item">
          <span class="level">Lv.3</span>
          <span class="name">首发球员</span>
          <span class="range">100-199积分</span>
        </div>
        <div class="level-item">
          <span class="level">Lv.4</span>
          <span class="name">主力球员</span>
          <span class="range">200-299积分</span>
        </div>
        <div class="level-item">
          <span class="level">Lv.5</span>
          <span class="name">明星球员</span>
          <span class="range">300-399积分</span>
        </div>
        <div class="level-item">
          <span class="level">Lv.6</span>
          <span class="name">超级巨星</span>
          <span class="range">400-499积分</span>
        </div>
        <div class="level-item">
          <span class="level">Lv.7</span>
          <span class="name">传奇球星</span>
          <span class="range">500-649积分</span>
        </div>
        <div class="level-item">
          <span class="level">Lv.8</span>
          <span class="name">球王</span>
          <span class="range">650-799积分</span>
        </div>
        <div class="level-item">
          <span class="level">Lv.9</span>
          <span class="name">预测大师</span>
          <span class="range">800-999积分</span>
        </div>
        <div class="level-item">
          <span class="level">Lv.10</span>
          <span class="name">神预测</span>
          <span class="range">1000+积分</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'Leaderboard',
  setup() {
    const sortBy = ref('points')
    const leaderboard = ref([])
    const stats = ref({})
    const myRanking = ref(null)
    const hotPredictions = ref([])
    
    // 加载排行榜
    const loadLeaderboard = async () => {
      try {
        const response = await fetch(`/worldcup/api/leaderboard/?sort_by=${sortBy.value}`)
        const data = await response.json()
        leaderboard.value = data.leaderboard
      } catch (error) {
        console.error('加载排行榜失败', error)
      }
    }
    
    // 加载统计
    const loadStats = async () => {
      try {
        const response = await fetch('/worldcup/api/leaderboard/stats')
        stats.value = await response.json()
      } catch (error) {
        console.error('加载统计失败', error)
      }
    }
    
    // 加载热门预测
    const loadHotPredictions = async () => {
      try {
        const response = await fetch('/worldcup/api/leaderboard/top-predictions')
        hotPredictions.value = await response.json()
      } catch (error) {
        console.error('加载热门预测失败', error)
      }
    }
    
    // 切换排序
    const changeSort = (type) => {
      sortBy.value = type
      loadLeaderboard()
    }
    
    onMounted(() => {
      loadLeaderboard()
      loadStats()
      loadHotPredictions()
    })
    
    return {
      sortBy,
      leaderboard,
      stats,
      myRanking,
      hotPredictions,
      changeSort
    }
  }
}
</script>

<style scoped>
.leaderboard {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

h3 {
  color: #444;
  margin: 20px 0 15px 0;
}

/* 排序选项 */
.sort-tabs {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.sort-tabs .tab {
  padding: 10px 20px;
  background: #f5f5f5;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.sort-tabs .tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

/* 统计概览 */
.stats-overview {
  display: flex;
  justify-content: space-around;
  background: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  border: 2px solid #1a472a;
}

.stat-item {
  text-align: center;
}

.stat-item .icon {
  font-size: 24px;
  margin-bottom: 5px;
}

.stat-item .label {
  font-size: 12px;
  color: #667eea;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.stat-item .value {
  font-size: 20px;
  font-weight: bold;
  color: #764ba2;
}

/* 排行榜列表 */
.leaderboard-list {
  background: white;
  border-radius: 12px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.user-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.3s;
}

.user-item:hover {
  background: #f9f9f9;
}

.user-item:last-child {
  border-bottom: none;
}

.user-item.top-3 {
  background: linear-gradient(to right, #fff9e6, transparent);
}

/* 排名 */
.rank {
  min-width: 40px;
  text-align: center;
}

.medal {
  font-size: 24px;
}

.rank-number {
  font-size: 18px;
  font-weight: bold;
  color: #666;
}

/* 用户信息 */
.user-info {
  flex: 1;
}

.nickname {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.badge {
  font-size: 12px;
  color: #667eea;
  margin: 3px 0;
}

.level {
  display: flex;
  gap: 5px;
  align-items: center;
}

.level-icon {
  font-size: 12px;
  color: #667eea;
  font-weight: bold;
}

.level-name {
  font-size: 12px;
  color: #999;
}

/* 用户数据 */
.user-data {
  display: flex;
  gap: 15px;
}

.data-row {
  text-align: right;
}

.data-label {
  font-size: 11px;
  color: #999;
}

.data-value {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.data-value.accuracy {
  color: #667eea;
}

/* 我的排名 */
.my-ranking {
  margin-top: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  border-radius: 12px;
  color: white;
}

.my-ranking h3 {
  color: white;
  margin-bottom: 15px;
}

.ranking-card {
  display: flex;
  align-items: center;
  gap: 20px;
}

.my-rank {
  text-align: center;
}

.my-rank .rank-number {
  font-size: 36px;
  font-weight: bold;
}

.my-rank .percentile {
  font-size: 14px;
  opacity: 0.8;
}

.my-stats {
  display: flex;
  gap: 30px;
}

.my-stats .stat {
  text-align: center;
}

.my-stats .label {
  font-size: 12px;
  opacity: 0.8;
}

.my-stats .value {
  font-size: 18px;
  font-weight: bold;
}

.my-badge {
  font-size: 24px;
}

/* 热门预测 */
.hot-predictions {
  margin-top: 30px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.pred-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.pred-item:last-child {
  border-bottom: none;
}

.pred-item .match {
  flex: 1;
  font-weight: bold;
}

.pred-item .prediction {
  color: #667eea;
  font-weight: bold;
}

.pred-item .confidence {
  font-size: 12px;
  color: #999;
}

.pred-item .users {
  font-size: 12px;
  color: #999;
}

/* 等级说明 */
.level-info {
  margin-top: 30px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.level-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.level-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 8px;
}

.level-item .level {
  color: #667eea;
  font-weight: bold;
}

.level-item .name {
  flex: 1;
}

.level-item .range {
  font-size: 12px;
  color: #999;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .leaderboard { padding: 16px; }
  
  h2 { font-size: 1.3rem; }
  
  .sort-tabs { gap: 8px; }
  
  .tab { padding: 8px 14px; font-size: 0.9rem; }
  
  .stats-overview {
    flex-wrap: wrap;
    gap: 12px;
    padding: 14px;
  }
  
  .stat-item {
    flex: 1;
    min-width: 80px;
  }
  
  .stat-item .icon { font-size: 1.3rem; }
  
  .stat-item .label { font-size: 0.8rem; }
  
  .stat-item .value { font-size: 1.1rem; }
  
  .user-item { padding: 12px; }
  
  .rank { font-size: 1.5rem; }
  
  .user-info { gap: 6px; }
  
  .nickname { font-size: 1rem; }
  
  .user-data {
    flex-direction: column;
    gap: 5px;
    padding: 10px;
  }
  
  .data-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
  }
  
  .ranking-card {
    flex-direction: column;
    text-align: center;
    padding: 16px;
    gap: 12px;
  }
  
  .ranking-card h3 { font-size: 1.1rem; }
  
  .rank-badge { font-size: 3rem; }
  
  .my-stats {
    flex-wrap: wrap;
    justify-content: center;
    gap: 12px;
  }
  
  .stat-box { padding: 10px 14px; }
  
  .stat-label { font-size: 0.8rem; }
  
  .stat-value { font-size: 1.2rem; }
  
  .pred-item {
    flex-wrap: wrap;
    padding: 10px;
    gap: 8px;
  }
  
  .pred-item .match {
    width: 100%;
    font-size: 0.95rem;
  }
  
  .pred-item .info { font-size: 0.85rem; }
}

@media (max-width: 480px) {
  .leaderboard { padding: 12px; }
  
  h2 { font-size: 1.2rem; }
  
  .sort-tabs { gap: 5px; }
  
  .tab { padding: 6px 12px; font-size: 0.85rem; }
  
  .stats-overview { padding: 12px; gap: 10px; }
  
  .stat-item { min-width: 70px; }
  
  .stat-item .icon { font-size: 1.2rem; }
  
  .stat-item .label { font-size: 0.75rem; }
  
  .stat-item .value { font-size: 1rem; }
  
  .user-item { padding: 10px; }
  
  .rank { font-size: 1.4rem; }
  
  .nickname { font-size: 0.95rem; }
  
  .user-data { padding: 8px; }
  
  .data-row { font-size: 0.85rem; }
  
  .ranking-card { padding: 14px; gap: 10px; }
  
  .ranking-card h3 { font-size: 1rem; }
  
  .rank-badge { font-size: 2.5rem; }
  
  .my-stats { gap: 10px; }
  
  .stat-box { padding: 8px 12px; }
  
  .stat-label { font-size: 0.75rem; }
  
  .stat-value { font-size: 1.1rem; }
  
  .pred-item { padding: 8px; gap: 6px; }
  
  .pred-item .match { font-size: 0.9rem; }
  
  .pred-item .info { font-size: 0.8rem; }
}
</style>