<template>
  <div class="user-module">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="banner-content">
        <div class="banner-icon">🎯</div>
        <div class="banner-text">
          <h2>世界杯预测大赛</h2>
          <p>预测比赛结果，比拼准确率，赢取排行榜荣耀！</p>
        </div>
      </div>
      <div class="banner-stats" v-if="globalStats">
        <div class="stat-pill">
          <span class="pill-value">{{ globalStats.total_users || 0 }}</span>
          <span class="pill-label">参与人数</span>
        </div>
        <div class="stat-pill">
          <span class="pill-value">{{ globalStats.total_predictions || 0 }}</span>
          <span class="pill-label">预测总数</span>
        </div>
      </div>
    </div>
    
    <!-- 未登录：输入昵称 -->
    <div v-if="!user" class="login-section">
      <div class="login-card">
        <div class="login-icon">🎮</div>
        <h3>欢迎参与预测</h3>
        <p>输入你的昵称，开始预测之旅</p>
        <input 
          v-model="nickname" 
          placeholder="输入昵称..." 
          class="nickname-input"
          @keyup.enter="startPredict"
        />
        <button class="start-btn" @click="startPredict">开始预测</button>
      </div>
    </div>
    
    <!-- 已登录：显示用户信息 -->
    <div v-else class="user-section">
      <!-- 用户卡片 -->
      <div class="user-card">
        <div class="user-avatar" :style="{ background: getAvatarColor(user.nickname) }">
          {{ user.nickname[0] }}
        </div>
        <div class="user-info">
          <div class="user-name">{{ user.nickname }}</div>
          <div class="user-title" :class="getTitleClass(user.total_points)">
            {{ getTitle(user.total_points, user.total_predictions, user.correct_predictions) }}
          </div>
          <div class="user-stats">
            <span class="stat">{{ user.total_predictions || 0 }}场预测</span>
            <span class="stat">{{ user.correct_predictions || 0 }}场正确</span>
            <span class="stat">{{ getAccuracy(user) }}%准确率</span>
          </div>
        </div>
        <div class="user-points">
          <div class="points-value">{{ user.total_points || 0 }}</div>
          <div class="points-label">积分</div>
        </div>
      </div>
      
      <!-- 子导航 -->
      <div class="sub-tabs">
        <div :class="['sub-tab', { active: activeTab === 'predict' }]" @click="activeTab = 'predict'">🎯 我的预测</div>
        <div :class="['sub-tab', { active: activeTab === 'leaderboard' }]" @click="activeTab = 'leaderboard'">🏆 排行榜</div>
        <div :class="['sub-tab', { active: activeTab === 'arena' }]" @click="activeTab = 'arena'">⚔️ 竞猜场</div>
      </div>

      <!-- 我的预测 -->
      <div v-if="activeTab === 'predict'" class="predict-section">
        <div class="section-header">
          <span class="section-title">已预测 {{ myPredictions.length }} 场比赛</span>
        </div>
        
        <div v-if="myPredictions.length === 0" class="empty-tip">
          <div class="empty-icon">📋</div>
          <div>还没有预测记录</div>
          <div class="empty-hint">前往「小组赛」或「竞猜场」，点击比赛进行预测</div>
        </div>
        
        <div v-else class="predictions-list">
          <div v-for="pred in myPredictions" :key="pred.id" class="prediction-card">
            <div class="pred-header">
              <span class="pred-group">{{ pred.group_name }}组</span>
              <span class="pred-time">{{ pred.match_date || '待定' }}</span>
            </div>
            <div class="pred-match">
              <span class="pred-teams">{{ pred.home_name_cn || pred.home_code }} vs {{ pred.away_name_cn || pred.away_code }}</span>
            </div>
            <!-- 显示比分（已结束的比赛） -->
            <div v-if="pred.home_score !== null && pred.away_score !== null" class="pred-score">
              <span class="score-label">比分:</span>
              <span class="score-value">{{ pred.home_score }} : {{ pred.away_score }}</span>
            </div>
            <div class="pred-footer">
              <div class="pred-result">
                <span class="pred-prediction" :class="pred.prediction">
                  {{ getResultIcon(pred.prediction) }} {{ getResultLabel(pred.prediction) }}
                </span>
                <span class="pred-confidence" :class="pred.confidence">
                  {{ getConfidenceLabel(pred.confidence) }}
                </span>
              </div>
              <div v-if="pred.verified_at" class="pred-verified">
                <span v-if="pred.is_correct" class="correct">✓ 正确 +{{ pred.points_earned }}分</span>
                <span v-else class="wrong">✗ 错误</span>
              </div>
              <div v-else-if="pred.match_status === 'finished'" class="pred-status" :class="pred.is_correct ? 'correct' : 'wrong'">
                {{ pred.is_correct ? '✅ 预测正确 +' + pred.points_earned + '分' : '❌ 预测错误 +0分' }}
              </div>
              <div v-else-if="pred.match_status === 'live'" class="pred-status live">🔴 比赛进行中</div>
              <div v-else class="pred-status">⏳ 待验证</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 排行榜 -->
      <div v-if="activeTab === 'leaderboard'" class="leaderboard-section">
        <div class="section-title">🏆 预测排行榜</div>
        <div class="leaderboard-list">
          <div v-for="entry in leaderboard" :key="entry.user_id" 
               :class="['leaderboard-row', { me: entry.user_id === user.user_id }]">
            <div class="lb-rank" :class="getRankClass(entry.rank)">
              {{ entry.rank <= 3 ? ['🥇','🥈','🥉'][entry.rank-1] : entry.rank }}
            </div>
            <div class="lb-avatar" :style="{ background: getAvatarColor(entry.nickname) }">{{ entry.nickname[0] }}</div>
            <div class="lb-info">
              <div class="lb-name">{{ entry.nickname }}</div>
              <div class="lb-detail">{{ entry.total_predictions }}场 · {{ entry.accuracy }}%准确</div>
            </div>
            <div class="lb-points">{{ entry.total_points }}<span class="lb-unit">分</span></div>
          </div>
        </div>
      </div>

      <!-- 竞猜场 -->
      <div v-if="activeTab === 'arena'" class="arena-section">
        <div class="section-title">⚔️ 竞猜场 — 快速预测所有比赛</div>
        
        <div v-if="arenaMatches.length === 0" class="empty-tip">
          <div class="empty-icon">⚽</div>
          <div>加载比赛数据中...</div>
        </div>
        
        <div v-else class="arena-list">
          <div v-for="match in arenaMatches" :key="match.key" class="arena-card">
            <div class="arena-header">
              <span class="arena-group">{{ match.group }}组</span>
              <span v-if="match.myPick" class="arena-picked">✅ 已预测</span>
            </div>
            <div class="arena-teams">
              <span class="arena-team home">{{ match.home_name }}</span>
              <span class="arena-vs">vs</span>
              <span class="arena-team away">{{ match.away_name }}</span>
            </div>
            
            <!-- 预测选项 -->
            <div class="arena-options" v-if="!match.myPick">
              <button 
                :class="['arena-btn', 'home-win', { selected: match.tempPick === 'HOME_WIN' }]"
                @click="match.tempPick = 'HOME_WIN'"
              >🏠 主胜</button>
              <button 
                :class="['arena-btn', 'draw', { selected: match.tempPick === 'DRAW' }]"
                @click="match.tempPick = 'DRAW'"
              >🤝 平局</button>
              <button 
                :class="['arena-btn', 'away-win', { selected: match.tempPick === 'AWAY_WIN' }]"
                @click="match.tempPick = 'AWAY_WIN'"
              >✈️ 客胜</button>
            </div>
            
            <!-- 已预测显示 -->
            <div class="arena-picked-result" v-else>
              <span class="picked-label">你的预测：</span>
              <span class="picked-value" :class="match.myPick">{{ getResultIcon(match.myPick) }} {{ getResultLabel(match.myPick) }}</span>
            </div>
            
            <!-- 信心选择 + 提交 -->
            <div class="arena-submit" v-if="!match.myPick && match.tempPick">
              <div class="conf-group">
                <button 
                  :class="['conf-opt', { active: match.tempConf === 'HIGH' }]"
                  @click="match.tempConf = 'HIGH'"
                >🔥 高信心</button>
                <button 
                  :class="['conf-opt', { active: match.tempConf === 'MEDIUM' }]"
                  @click="match.tempConf = 'MEDIUM'"
                >👍 中信心</button>
                <button 
                  :class="['conf-opt', { active: match.tempConf === 'LOW' }]"
                  @click="match.tempConf = 'LOW'"
                >🎲 博冷门</button>
              </div>
              <button class="arena-submit-btn" @click="submitArenaPick(match)">提交</button>
            </div>
            
            <!-- 网友预测分布 -->
            <div class="arena-stats" v-if="match.stats && match.stats.total_predictions > 0">
              <div class="mini-bar">
                <div class="mini-fill home" :style="{ width: match.stats.home_win_pct + '%' }"></div>
                <div class="mini-fill draw" :style="{ width: match.stats.draw_pct + '%' }"></div>
                <div class="mini-fill away" :style="{ width: match.stats.away_win_pct + '%' }"></div>
              </div>
              <div class="mini-labels">
                <span>主胜 {{ match.stats.home_win_pct }}%</span>
                <span>平 {{ match.stats.draw_pct }}%</span>
                <span>客胜 {{ match.stats.away_win_pct }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, onMounted, inject } from 'vue'

export default {
  setup() {
    // 注入全局状态
    const currentUser = inject('currentUser', ref(null))
    const updateUser = inject('updateUser', null)
    const showToast = inject('showToast', null)
    
    const user = ref(null)
    const nickname = ref('')
    const activeTab = ref('predict')
    const myPredictions = ref([])
    const leaderboard = ref([])
    const arenaMatches = ref([])
    const globalStats = ref(null)
    
    // Cookie 操作
    function setCookie(name, value, days = 30) {
      const expires = new Date(Date.now() + days * 864e5).toUTCString()
      document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/`
    }
    
    function getCookie(name) {
      const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'))
      return match ? decodeURIComponent(match[2]) : null
    }
    
    // 生成或获取设备密钥
    function getDeviceKey() {
      let deviceKey = localStorage.getItem('worldcup_device_key')
      if (!deviceKey) {
        deviceKey = 'dk_' + Math.random().toString(36).substr(2, 16) + Date.now().toString(36)
        localStorage.setItem('worldcup_device_key', deviceKey)
      }
      return deviceKey
    }
    
    // 验证过期检查
    function clearExpiredAuth() {
      const authTime = localStorage.getItem('worldcup_auth_time')
      if (!authTime) return
      
      const authTimestamp = parseInt(authTime)
      const now = Date.now()
      const hoursPassed = (now - authTimestamp) / (1000 * 60 * 60)
      
      if (hoursPassed >= 4) {
        localStorage.removeItem('worldcup_auth')
        localStorage.removeItem('worldcup_auth_time')
        document.cookie = 'user_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
      }
    }
    
    // 头像颜色生成
    function getAvatarColor(name) {
      const colors = [
        'linear-gradient(135deg, #667eea, #764ba2)',
        'linear-gradient(135deg, #f093fb, #f5576c)',
        'linear-gradient(135deg, #4facfe, #00f2fe)',
        'linear-gradient(135deg, #43e97b, #38f9d7)',
        'linear-gradient(135deg, #fa709a, #fee140)',
        'linear-gradient(135deg, #a18cd1, #fbc2eb)'
      ]
      let hash = 0
      for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash)
      }
      return colors[Math.abs(hash) % colors.length]
    }
    
    // 获得身份称号
    function getTitle(points, total, correct) {
      if (!total || total === 0) return '🌱 新手'
      
      const accuracy = correct / total * 100
      
      if (points >= 100 && accuracy >= 80) return '🔮 足球先知'
      if (points >= 50 && accuracy >= 70) return '🎯 预言大师'
      if (points >= 30 && accuracy >= 60) return '⭐ 预测达人'
      if (points >= 10) return '🔥 活跃玩家'
      if (total >= 5) return '📊 初级分析师'
      return '🌱 新手'
    }
    
    function getTitleClass(points) {
      if (points >= 100) return 'legend'
      if (points >= 50) return 'master'
      if (points >= 30) return 'expert'
      if (points >= 10) return 'active'
      return 'beginner'
    }
    
    function getAccuracy(user) {
      if (!user.total_predictions || user.total_predictions === 0) return 0
      return Math.round((user.correct_predictions || 0) / user.total_predictions * 100)
    }
    
    // 开始预测
    async function startPredict() {
      if (!nickname.value.trim()) {
        alert('请输入昵称')
        return
      }
      
      const deviceKey = getDeviceKey()
      
      try {
        const resp = await fetch(`/worldcup/api/user/login?nickname=${encodeURIComponent(nickname.value.trim())}&device_key=${deviceKey}`, {
          method: 'POST',
          credentials: 'include'
        })
        const data = await resp.json()
        
        if (data.success) {
          setCookie('user_id', data.user.user_id)
          user.value = data.user
          nickname.value = ''
          // 更新全局用户状态
          if (updateUser) {
            updateUser(data.user)
          }
          if (showToast) {
            showToast(data.message || '登录成功', 'success', 3000)
          }
          loadMyPredictions()
          loadLeaderboard()
          loadGlobalStats()
          loadArena()
        } else {
          if (showToast) {
            showToast(data.error || '登录失败', 'error', 4000)
          }
        }
      } catch (e) {
        console.error('登录失败', e)
      }
    }
    
    // 检查登录状态
    async function checkLogin() {
      clearExpiredAuth()
      const userId = getCookie('user_id')
      if (!userId) return
      
      try {
        const resp = await fetch('/worldcup/api/user/me', { credentials: 'include' })
        const data = await resp.json()
        
        if (data.logged_in) {
          user.value = data.user
          loadMyPredictions()
          loadArena()
        }
      } catch (e) {
        console.error('检查登录失败', e)
      }
    }
    
    // 加载全局统计
    async function loadGlobalStats() {
      try {
        const resp = await fetch('/worldcup/api/user/all-users')
        const data = await resp.json()
        globalStats.value = {
          total_users: data.total || 0,
          total_predictions: data.users ? data.users.reduce((s, u) => s + (u.total_predictions || 0), 0) : 0
        }
      } catch (e) {
        console.error('加载统计失败', e)
      }
    }
    
    // 加载我的预测
    async function loadMyPredictions() {
      if (!user.value) return
      try {
        const resp = await fetch('/worldcup/api/user/my-predictions', { credentials: 'include' })
        const data = await resp.json()
        myPredictions.value = data.predictions || []
      } catch (e) {
        console.error('加载预测失败', e)
      }
    }
    
    // 加载排行榜
    async function loadLeaderboard() {
      try {
        const resp = await fetch('/worldcup/api/leaderboard/?sort_by=points&limit=50')
        const data = await resp.json()
        leaderboard.value = data.leaderboard || []
      } catch (e) {
        console.error('加载排行榜失败', e)
      }
    }
    
    // 加载竞猜场
    async function loadArena() {
      try {
        const groups = 'ABCDEFGHIJKL'.split('')
        const matches = []
        
        for (const g of groups) {
          try {
            const resp = await fetch(`/worldcup/api/groups/${g}`)
            const data = await resp.json()
            
            if (data.matches) {
              data.matches.forEach((m, idx) => {
                // 检查比赛状态，只添加未结束的比赛
                if (m.status !== 'finished') {
                  matches.push({
                    key: `${g}_${idx}`,
                    group: g,
                    match_idx: idx,
                    home: m.home || m.home_code,
                    away: m.away || m.away_code,
                    home_name: m.home_name_cn || m.home,
                    away_name: m.away_name_cn || m.away,
                    status: m.status || 'scheduled',
                    tempPick: null,
                    tempConf: 'MEDIUM',
                    myPick: null,
                    stats: null
                  })
                }
              })
            }
          } catch (e) {}
        }
        
        arenaMatches.value = matches
        loadArenaStats()
        loadArenaMyPicks()
      } catch (e) {
        console.error('加载竞猜场失败', e)
      }
    }
    
    async function loadArenaStats() {
      const promises = arenaMatches.value.map(async (match) => {
        try {
          const resp = await fetch(`/worldcup/api/user/prediction-stats/${match.group}/${match.match_idx}`)
          match.stats = await resp.json()
        } catch (e) {}
      })
      await Promise.all(promises)
    }
    
    async function loadArenaMyPicks() {
      if (!user.value) return
      try {
        const resp = await fetch('/worldcup/api/user/my-predictions', { credentials: 'include' })
        const data = await resp.json()
        const predictions = data.predictions || []
        
        for (const pred of predictions) {
          const match = arenaMatches.value.find(m => 
            m.group === pred.group_name && m.match_idx === pred.match_idx
          )
          if (match) {
            match.myPick = pred.prediction
          }
        }
      } catch (e) {
        console.error('加载我的预测失败', e)
      }
    }
    
    async function submitArenaPick(match) {
      if (!match.tempPick || !user.value) return
      
      const deviceKey = getDeviceKey()
      
      try {
        const resp = await fetch('/worldcup/api/user/predict-simple', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            nickname: user.value.nickname,
            device_key: deviceKey,
            group: match.group,
            match_idx: match.match_idx,
            prediction: match.tempPick,
            confidence: match.tempConf || 'MEDIUM',
            home_code: match.home,
            away_code: match.away
          })
        })
        
        const data = await resp.json()
        
        if (data.success) {
          match.myPick = match.tempPick
          match.tempPick = null
          match.tempConf = 'MEDIUM'
          
          try {
            const statsResp = await fetch(`/worldcup/api/user/prediction-stats/${match.group}/${match.match_idx}`)
            match.stats = await statsResp.json()
          } catch (e) {}
          
          loadMyPredictions()
          loadLeaderboard()
          
          // 更新用户信息
          user.value.total_predictions = (user.value.total_predictions || 0) + 1
        } else {
          alert('提交失败: ' + (data.error || '未知错误'))
        }
      } catch (e) {
        console.error('提交预测失败', e)
      }
    }
    
    function getResultLabel(result) {
      const labels = { 'HOME_WIN': '主胜', 'DRAW': '平局', 'AWAY_WIN': '客胜' }
      return labels[result] || result
    }
    
    function getResultIcon(result) {
      const icons = { 'HOME_WIN': '🏠', 'DRAW': '🤝', 'AWAY_WIN': '✈️' }
      return icons[result] || '⚽'
    }
    
    function getConfidenceLabel(conf) {
      const labels = { 'HIGH': '🔥高信心', 'MEDIUM': '👍中信心', 'LOW': '🎲博冷门' }
      return labels[conf] || conf
    }
    
    function getRankClass(rank) {
      if (rank === 1) return 'gold'
      if (rank === 2) return 'silver'
      if (rank === 3) return 'bronze'
      return ''
    }
    
    onMounted(() => {
      checkLogin()
      loadLeaderboard()
      loadGlobalStats()
    })
    
    return {
      user, nickname, activeTab,
      myPredictions, leaderboard, arenaMatches, globalStats,
      startPredict, loadMyPredictions, loadLeaderboard, loadArena,
      submitArenaPick, getAvatarColor, getTitle, getTitleClass, getAccuracy,
      getResultLabel, getResultIcon, getConfidenceLabel, getRankClass
    }
  }
}
</script>

<style scoped>
.user-module { padding: 16px; max-width: 800px; margin: 0 auto; }

/* 欢迎横幅 */
.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.banner-icon { font-size: 3rem; }

.banner-text h2 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 800;
}

.banner-text p {
  margin: 4px 0 0 0;
  font-size: 0.95rem;
  opacity: 0.9;
}

.banner-stats {
  display: flex;
  gap: 12px;
}

.stat-pill {
  text-align: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 8px 16px;
}

.pill-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 800;
}

.pill-label {
  display: block;
  font-size: 0.75rem;
  opacity: 0.8;
}

/* 登录卡片 */
.login-section {
  display: flex;
  justify-content: center;
  padding: 40px 20px;
}

.login-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  max-width: 400px;
  width: 100%;
}

.login-icon {
  font-size: 4rem;
  margin-bottom: 16px;
}

.login-card h3 {
  font-size: 1.5rem;
  font-weight: 800;
  color: #333;
  margin: 0 0 8px 0;
}

.login-card p {
  font-size: 1rem;
  color: #666;
  margin: 0 0 24px 0;
}

.nickname-input {
  width: 100%;
  padding: 14px 16px;
  font-size: 1.1rem;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  outline: none;
  margin-bottom: 16px;
  box-sizing: border-box;
}

.nickname-input:focus {
  border-color: #667eea;
}

.start-btn {
  width: 100%;
  padding: 14px;
  font-size: 1.1rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

/* 用户卡片 */
.user-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.user-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 800;
  color: white;
  flex-shrink: 0;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 1.3rem;
  font-weight: 800;
  color: #333;
  margin-bottom: 4px;
}

.user-title {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.user-title.legend { background: linear-gradient(135deg, #ffd700, #ffed4e); color: #b8860b; }
.user-title.master { background: linear-gradient(135deg, #c0c0c0, #e8e8e8); color: #696969; }
.user-title.expert { background: linear-gradient(135deg, #cd7f32, #daa06d); color: #8b4513; }
.user-title.active { background: #e8f5e9; color: #2e7d32; }
.user-title.beginner { background: #f0f0f0; color: #666; }

.user-stats {
  display: flex;
  gap: 12px;
  font-size: 0.85rem;
  color: #888;
}

.user-points {
  text-align: center;
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 12px;
  color: white;
}

.points-value {
  font-size: 1.8rem;
  font-weight: 800;
}

.points-label {
  font-size: 0.8rem;
  opacity: 0.9;
}

/* 子导航 */
.sub-tabs { display: flex; gap: 8px; margin-bottom: 16px; }

.sub-tab { 
  padding: 10px 18px;
  border-radius: 10px; 
  background: #f5f5f5; 
  cursor: pointer; 
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.2s;
}

.sub-tab.active { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
.sub-tab:hover:not(.active) { background: #e8e8e8; }

/* 通用 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 12px 0;
}

.section-title { font-size: 1.1rem; font-weight: 700; color: #333; }

.empty-tip { 
  text-align: center; 
  padding: 40px 20px; 
  color: #888;
  background: #f8f9fa;
  border-radius: 12px;
}

.empty-icon { font-size: 2.5rem; margin-bottom: 8px; }
.empty-hint { font-size: 0.9rem; margin-top: 8px; color: #aaa; }

/* 预测列表 */
.predictions-list { display: flex; flex-direction: column; gap: 10px; }

.prediction-card { 
  padding: 14px 16px; 
  background: white; 
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pred-header { display: flex; justify-content: space-between; align-items: center; }
.pred-group { font-size: 0.85rem; color: #667eea; font-weight: 700; }
.pred-time { font-size: 0.85rem; color: #888; }
.pred-match { display: flex; justify-content: center; }
.pred-teams { font-weight: 600; font-size: 1.05rem; text-align: center; }

/* 比分显示 */
.pred-score {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin: 8px 0;
  padding: 6px 12px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 8px;
  font-size: 0.95rem;
}

.pred-score .score-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.85rem;
}

.pred-score .score-value {
  color: #fff;
  font-weight: 700;
  font-size: 1.1rem;
}

.pred-footer { display: flex; justify-content: space-between; align-items: center; }
.pred-result { display: flex; gap: 8px; }

.pred-prediction { 
  padding: 4px 12px; 
  border-radius: 6px; 
  font-size: 0.9rem;
  font-weight: 600;
}

.pred-prediction.HOME_WIN { background: #e8f5e9; color: #27ae60; }
.pred-prediction.DRAW { background: #fff8e1; color: #f39c12; }
.pred-prediction.AWAY_WIN { background: #e3f2fd; color: #3498db; }

.pred-confidence { 
  padding: 4px 10px; 
  border-radius: 6px; 
  font-size: 0.85rem;
  font-weight: 600;
  background: #f0f0f0;
  color: #666;
}

.pred-confidence.LOW { background: #fce4ec; color: #e91e63; }

.pred-verified { font-size: 0.9rem; font-weight: 700; }
.pred-verified .correct { color: #27ae60; }
.pred-verified .wrong { color: #e74c3c; }
.pred-status {
  font-size: 0.85rem;
  padding: 4px 12px;
  border-radius: 8px;
  font-weight: 600;
}

.pred-status.correct {
  background: #d4edda;
  color: #155724;
  border: 1px solid #28a745;
}

.pred-status.wrong {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #dc3545;
}

.pred-status.live {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffc107;
}

/* 排行榜 */
.leaderboard-list { display: flex; flex-direction: column; gap: 8px; }

.leaderboard-row { 
  display: flex; align-items: center; gap: 12px;
  padding: 12px 16px; 
  background: white; 
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}

.leaderboard-row.me { 
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9); 
  border: 2px solid #27ae60;
}

.lb-rank { 
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700;
  font-size: 1rem;
}

.lb-avatar {
  width: 40px; height: 40px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; font-weight: 700;
  color: white;
}

.lb-info { flex: 1; }
.lb-name { font-weight: 600; font-size: 1rem; }
.lb-detail { font-size: 0.8rem; color: #888; margin-top: 2px; }

.lb-points { 
  font-size: 1.3rem;
  font-weight: 800;
  color: #667eea;
}

.lb-unit { font-size: 0.8rem; font-weight: 500; }

/* 竞猜场 */
.arena-list { display: flex; flex-direction: column; gap: 12px; }

.arena-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.arena-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.arena-group {
  font-size: 0.85rem;
  font-weight: 700;
  color: #667eea;
  background: #e8f0ff;
  padding: 3px 10px;
  border-radius: 6px;
}

.arena-picked {
  font-size: 0.85rem;
  font-weight: 600;
  color: #28a745;
}

.arena-teams {
  text-align: center;
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 12px;
}

.arena-team.home { color: #1a472a; }
.arena-team.away { color: #764ba2; }
.arena-vs { color: #ccc; margin: 0 12px; font-size: 1rem; }

.arena-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 8px;
}

.arena-btn {
  padding: 12px 8px;
  font-size: 1rem;
  font-weight: 600;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.2s;
}

.arena-btn.selected.home-win { background: #e8f5e9; border-color: #28a745; color: #1a472a; }
.arena-btn.selected.draw { background: #fff8e1; border-color: #ffc107; color: #f57c00; }
.arena-btn.selected.away-win { background: #e3f2fd; border-color: #2196f3; color: #1565c0; }

.arena-picked-result {
  text-align: center;
  padding: 8px;
  background: #f0f7ff;
  border-radius: 8px;
}

.picked-label { font-size: 0.9rem; color: #888; }
.picked-value { font-size: 1rem; font-weight: 700; }
.picked-value.HOME_WIN { color: #28a745; }
.picked-value.DRAW { color: #f57c00; }
.picked-value.AWAY_WIN { color: #2196f3; }

.arena-submit {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}

.conf-group { display: flex; gap: 6px; flex: 1; }

.conf-opt {
  padding: 8px 12px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: #f5f5f5;
  cursor: pointer;
  transition: all 0.2s;
}

.conf-opt.active {
  background: #e8f0ff;
  border-color: #667eea;
  color: #667eea;
}

.arena-submit-btn {
  padding: 10px 24px;
  font-size: 1rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.arena-submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.arena-stats {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.mini-bar {
  display: flex;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  background: #e0e0e0;
}

.mini-fill { transition: width 0.3s; }
.mini-fill.home { background: #28a745; }
.mini-fill.draw { background: #ffc107; }
.mini-fill.away { background: #2196f3; }

.mini-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  font-size: 0.8rem;
  color: #888;
}

/* 响应式 */
@media (max-width: 768px) {
  .welcome-banner {
    flex-direction: column;
    gap: 12px;
    text-align: center;
    padding: 16px;
  }
  
  .banner-content {
    flex-direction: column;
    gap: 12px;
  }
  
  .banner-icon { font-size: 2.5rem; }
  
  .banner-text h2 { font-size: 1.2rem; }
  
  .banner-text p { font-size: 0.9rem; }
  
  .banner-stats {
    gap: 10px;
  }
  
  .stat-pill { padding: 6px 12px; }
  
  .pill-value { font-size: 1.3rem; }
  
  .login-section { padding: 30px 16px; }
  
  .login-card { padding: 30px 20px; }
  
  .login-icon { font-size: 3rem; }
  
  .login-card h3 { font-size: 1.3rem; }
  
  .login-card p { font-size: 0.95rem; }
  
  .nickname-input { padding: 12px 14px; font-size: 1rem; }
  
  .start-btn { padding: 12px; font-size: 1rem; }
  
  .user-card {
    flex-direction: column;
    text-align: center;
    padding: 16px;
    gap: 12px;
  }
  
  .user-avatar {
    width: 55px;
    height: 55px;
    font-size: 1.6rem;
  }
  
  .user-name { font-size: 1.3rem; }
  
  .user-title { padding: 3px 10px; font-size: 0.85rem; }
  
  .user-stats { gap: 10px; font-size: 0.8rem; }
  
  .user-points {
    padding: 6px 14px;
  }
  
  .points-value { font-size: 1.6rem; }
  
  .sub-tabs { gap: 6px; }
  
  .sub-tab { padding: 8px 14px; font-size: 0.9rem; }
  
  .arena-options {
    grid-template-columns: 1fr;
    gap: 6px;
  }
  
  .arena-submit {
    flex-direction: column;
    gap: 8px;
  }
  
  .conf-group {
    width: 100%;
    gap: 5px;
  }
  
  .arena-submit-btn {
    width: 100%;
    padding: 10px 20px;
  }
  
  .arena-card { padding: 14px; }
  
  .arena-teams { font-size: 1.1rem; }
  
  .arena-btn { padding: 10px 8px; font-size: 0.95rem; }
}

@media (max-width: 480px) {
  .welcome-banner {
    padding: 14px;
    gap: 10px;
  }
  
  .banner-icon { font-size: 2.2rem; }
  
  .banner-text h2 { font-size: 1.1rem; }
  
  .banner-text p { font-size: 0.85rem; }
  
  .stat-pill { padding: 5px 10px; }
  
  .pill-value { font-size: 1.2rem; }
  
  .pill-label { font-size: 0.7rem; }
  
  .login-section { padding: 24px 12px; }
  
  .login-card { padding: 24px 16px; }
  
  .login-icon { font-size: 2.5rem; }
  
  .login-card h3 { font-size: 1.2rem; }
  
  .login-card p { font-size: 0.9rem; }
  
  .nickname-input { padding: 11px 12px; font-size: 0.95rem; }
  
  .start-btn { padding: 11px; font-size: 0.95rem; }
  
  .user-card { padding: 14px; gap: 10px; }
  
  .user-avatar {
    width: 50px;
    height: 50px;
    font-size: 1.5rem;
  }
  
  .user-name { font-size: 1.2rem; }
  
  .user-title { font-size: 0.8rem; }
  
  .user-stats { gap: 8px; font-size: 0.75rem; }
  
  .user-points { padding: 5px 12px; }
  
  .points-value { font-size: 1.5rem; }
  
  .points-label { font-size: 0.75rem; }
  
  .sub-tabs { gap: 5px; }
  
  .sub-tab { padding: 7px 12px; font-size: 0.85rem; }
  
  .arena-card { padding: 12px; }
  
  .arena-teams { font-size: 1rem; }
  
  .arena-vs { margin: 0 10px; }
  
  .arena-btn { padding: 9px 6px; font-size: 0.9rem; }
  
  .conf-opt { padding: 7px 10px; font-size: 0.8rem; }
  
  .arena-submit-btn { padding: 9px 18px; font-size: 0.95rem; }
}
</style>
