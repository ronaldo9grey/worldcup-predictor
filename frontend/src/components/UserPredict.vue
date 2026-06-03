<template>
  <div class="user-module">
    <!-- 自定义确认弹窗 -->
    <div v-if="showConfirm" class="confirm-overlay" @click.self="cancelConfirm">
      <div class="confirm-dialog">
        <div class="confirm-icon">⚠️</div>
        <div class="confirm-title">{{ confirmTitle }}</div>
        <div class="confirm-message">{{ confirmMessage }}</div>
        <div class="confirm-buttons">
          <button class="confirm-cancel" @click="cancelConfirm">取消</button>
          <button class="confirm-ok" @click="confirmAction">确认删除</button>
        </div>
      </div>
    </div>
    
    <!-- 昵称选择器 -->
    <div class="nickname-selector">
      <div class="selector-header">
        <span class="selector-title">👥 选择昵称</span>
        <button @click="showCreateInput = !showCreateInput" class="add-btn">
          {{ showCreateInput ? '取消' : '+ 新建' }}
        </button>
      </div>
      
      <!-- 新建昵称输入 -->
      <div v-if="showCreateInput" class="create-input">
        <input 
          v-model="newNickname" 
          placeholder="输入新昵称" 
          @keyup.enter="createAndLogin"
          class="nickname-input"
        />
        <button @click="createAndLogin" class="confirm-btn">确认</button>
      </div>
      
      <!-- 昵称列表 -->
      <div class="nickname-list" v-if="allUsers.length > 0">
        <div 
          v-for="u in allUsers" 
          :key="u.user_id" 
          :class="['nickname-item', { active: user && user.user_id === u.user_id }]"
          @click="selectUser(u)"
        >
          <div class="nickname-avatar">{{ u.nickname[0] }}</div>
          <div class="nickname-info">
            <div class="nickname-name">{{ u.nickname }}</div>
            <div class="nickname-stats">{{ u.total_predictions }}场预测 · {{ u.total_points }}分</div>
          </div>
          <div class="nickname-actions">
            <div v-if="user && user.user_id === u.user_id" class="check-icon">✓</div>
            <button v-else class="delete-btn" @click.stop="confirmDelete(u)">🗑</button>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-else class="empty-users">
        还没有任何昵称，快创建一个吧！
      </div>
    </div>

    <!-- 子导航 -->
    <div class="sub-tabs" v-if="user">
      <div :class="['sub-tab', { active: activeTab === 'predict' }]" @click="activeTab = 'predict'">🎯 我的预测</div>
      <div :class="['sub-tab', { active: activeTab === 'leaderboard' }]" @click="activeTab = 'leaderboard'">🏆 排行榜</div>
    </div>

    <!-- 我的预测 -->
    <div v-if="user && activeTab === 'predict'" class="predict-section">
      <div class="section-title">已预测 {{ myPredictions.length }} 场比赛</div>
      
      <div v-if="myPredictions.length === 0" class="empty-tip">
        前往「小组赛」页面，点击比赛卡片进行预测
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
          <div class="pred-footer">
            <div class="pred-result">
              <span class="pred-prediction" :class="pred.prediction">
                {{ getResultLabel(pred.prediction) }}
              </span>
              <span class="pred-confidence" :class="pred.confidence">
                {{ getConfidenceLabel(pred.confidence) }}
              </span>
            </div>
            <div v-if="pred.verified_at" class="pred-verified">
              <span v-if="pred.is_correct" class="correct">✓ 正确 +{{ pred.points_earned }}分</span>
              <span v-else class="wrong">✗ 错误</span>
            </div>
            <div v-else class="pred-status">待验证</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 排行榜 -->
    <div v-if="user && activeTab === 'leaderboard'" class="leaderboard-section">
      <div class="section-title">预测排行榜</div>
      <div class="leaderboard-list">
        <div v-for="entry in leaderboard" :key="entry.user_id" 
             :class="['leaderboard-row', { me: user && entry.user_id === user.user_id }]">
          <div class="lb-rank" :class="getRankClass(entry.rank)">
            {{ entry.rank <= 3 ? ['🥇','🥈','🥉'][entry.rank-1] : entry.rank }}
          </div>
          <div class="lb-name">{{ entry.nickname }}</div>
          <div class="lb-accuracy">{{ entry.accuracy }}%</div>
          <div class="lb-points">{{ entry.total_points }}分</div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  setup() {
    const user = ref(null)
    const allUsers = ref([])
    const showCreateInput = ref(false)
    const newNickname = ref('')
    const activeTab = ref('predict')
    const myPredictions = ref([])
    const leaderboard = ref([])
    
    // 确认弹窗状态
    const showConfirm = ref(false)
    const confirmTitle = ref('')
    const confirmMessage = ref('')
    const pendingAction = ref(null)
    
    // Cookie 操作
    function setCookie(name, value, days = 30) {
      const expires = new Date(Date.now() + days * 864e5).toUTCString()
      document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/`
    }
    
    function getCookie(name) {
      const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'))
      return match ? decodeURIComponent(match[2]) : null
    }
    
    async function loadAllUsers() {
      try {
        const resp = await fetch('/worldcup/api/user/all-users')
        const data = await resp.json()
        allUsers.value = data.users || []
      } catch (e) {
        console.error('加载用户列表失败', e)
      }
    }
    
    async function checkLogin() {
      const userId = getCookie('user_id')
      if (!userId) return
      
      try {
        const resp = await fetch('/worldcup/api/user/me', { credentials: 'include' })
        const data = await resp.json()
        
        if (data.logged_in) {
          user.value = data.user
          loadMyPredictions()
        }
      } catch (e) {
        console.error('检查登录失败', e)
      }
    }
    
    async function selectUser(u) {
      // 设置cookie并刷新
      setCookie('user_id', u.user_id)
      user.value = u
      loadMyPredictions()
    }
    
    async function confirmDelete(u) {
      // 显示自定义确认弹窗
      confirmTitle.value = '删除用户'
      confirmMessage.value = `确定要删除「${u.nickname}」吗？此操作将删除所有预测记录，不可恢复。`
      pendingAction.value = async () => {
        try {
          const resp = await fetch(`/worldcup/api/user/delete/${u.user_id}`, {
            method: 'DELETE'
          })
          const data = await resp.json()
          
          if (data.success) {
            loadAllUsers()
          } else {
            showError('删除失败: ' + (data.error || '未知错误'))
          }
        } catch (e) {
          console.error('删除用户失败', e)
          showError('删除失败')
        }
      }
      showConfirm.value = true
    }
    
    function cancelConfirm() {
      showConfirm.value = false
      pendingAction.value = null
    }
    
    async function confirmAction() {
      showConfirm.value = false
      if (pendingAction.value) {
        await pendingAction.value()
        pendingAction.value = null
      }
    }
    
    function showError(msg) {
      confirmTitle.value = '错误'
      confirmMessage.value = msg
      pendingAction.value = null
      showConfirm.value = true
    }
    
    async function createAndLogin() {
      if (!newNickname.value.trim()) {
        alert('请输入昵称')
        return
      }
      
      try {
        const resp = await fetch(`/worldcup/api/user/login?nickname=${encodeURIComponent(newNickname.value.trim())}`, {
          method: 'POST',
          credentials: 'include'
        })
        const data = await resp.json()
        
        if (data.success) {
          setCookie('user_id', data.user.user_id)
          user.value = data.user
          newNickname.value = ''
          showCreateInput.value = false
          loadMyPredictions()
          loadLeaderboard()
          loadAllUsers()  // 刷新用户列表
        } else {
          alert('登录失败: ' + (data.message || '未知错误'))
        }
      } catch (e) {
        console.error('登录失败', e)
        alert('登录失败: ' + e.message)
      }
    }
    
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
    
    async function loadLeaderboard() {
      try {
        const resp = await fetch('/worldcup/api/user/leaderboard')
        const data = await resp.json()
        leaderboard.value = data.leaderboard || []
      } catch (e) {
        console.error('加载排行榜失败', e)
      }
    }
    
    function getResultLabel(result) {
      const labels = { 'HOME_WIN': '主胜', 'DRAW': '平局', 'AWAY_WIN': '客胜' }
      return labels[result] || result
    }
    
    function getConfidenceLabel(conf) {
      const labels = { 'HIGH': '高信心', 'MEDIUM': '中信心', 'LOW': '博冷门' }
      return labels[conf] || conf
    }
    
    function getRankClass(rank) {
      if (rank === 1) return 'gold'
      if (rank === 2) return 'silver'
      if (rank === 3) return 'bronze'
      return ''
    }
    
    onMounted(() => {
      loadAllUsers()
      checkLogin()
      loadLeaderboard()
    })
    
    return {
      user, allUsers, showCreateInput, newNickname, activeTab,
      myPredictions, leaderboard,
      showConfirm, confirmTitle, confirmMessage,
      loadAllUsers, selectUser, confirmDelete, cancelConfirm, confirmAction, createAndLogin, loadMyPredictions, loadLeaderboard,
      getResultLabel, getConfidenceLabel, getRankClass
    }
  }
}
</script>

<style scoped>
.user-module { padding: 16px; }

/* 确认弹窗 */
.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.confirm-dialog {
  background: white;
  border-radius: 16px;
  padding: 24px;
  max-width: 360px;
  width: 90%;
  text-align: center;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.confirm-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.confirm-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.confirm-message {
  font-size: 0.95rem;
  color: #666;
  line-height: 1.5;
  margin-bottom: 24px;
}

.confirm-buttons {
  display: flex;
  gap: 12px;
}

.confirm-cancel,
.confirm-ok {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.confirm-cancel {
  background: #f0f0f0;
  color: #666;
}

.confirm-cancel:hover {
  background: #e0e0e0;
}

.confirm-ok {
  background: #e74c3c;
  color: white;
}

.confirm-ok:hover {
  background: #c0392b;
}

/* 昵称选择器 */
.nickname-selector { 
  background: white;
  border-radius: 12px; 
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.selector-title {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.add-btn {
  padding: 6px 12px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
}

.create-input {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.nickname-input { 
  flex: 1; 
  padding: 10px 14px; 
  border: 1px solid #ddd; 
  border-radius: 8px; 
  font-size: 0.95rem;
  outline: none;
}

.nickname-input:focus {
  border-color: #667eea;
}

.confirm-btn { 
  padding: 10px 20px; 
  background: #667eea; 
  color: white; 
  border: none; 
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.nickname-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nickname-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  border: 2px solid transparent;
}

.nickname-item:hover {
  background: #f0f0f0;
}

.nickname-item.active {
  background: #e8f0ff;
  border-color: #667eea;
}

.nickname-avatar { 
  width: 40px; height: 40px; 
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.nickname-info { flex: 1; }
.nickname-name { font-size: 0.95rem; font-weight: 600; color: #333; }
.nickname-stats { font-size: 0.8rem; color: #888; margin-top: 2px; }

.check-icon {
  width: 24px;
  height: 24px;
  background: #27ae60;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
}

.nickname-actions {
  display: flex;
  align-items: center;
}

.delete-btn {
  padding: 4px 8px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.15s;
}

.delete-btn:hover {
  opacity: 1;
}

.empty-users {
  text-align: center;
  padding: 30px;
  color: #888;
  font-size: 0.9rem;
}

/* 子导航 */
.sub-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.sub-tab { 
  padding: 8px 16px; 
  border-radius: 6px; 
  background: #f5f5f5; 
  cursor: pointer; 
  font-size: 0.9rem;
}
.sub-tab.active { background: #667eea; color: white; }

/* 通用 */
.section-title { font-size: 1rem; font-weight: 600; margin: 12px 0; }
.empty-tip { 
  text-align: center; 
  padding: 40px 20px; 
  color: #888;
  background: #f8f9fa;
  border-radius: 8px;
}

/* 预测列表 */
.predictions-list { display: flex; flex-direction: column; gap: 10px; }
.prediction-card { 
  padding: 12px 14px; 
  background: #f8f9fa; 
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.pred-header { display: flex; justify-content: space-between; align-items: center; }
.pred-group { font-size: 0.75rem; color: #667eea; font-weight: 600; }
.pred-time { font-size: 0.75rem; color: #888; }
.pred-match { display: flex; justify-content: center; }
.pred-teams { font-weight: 500; font-size: 0.95rem; text-align: center; }
.pred-footer { display: flex; justify-content: space-between; align-items: center; }
.pred-result { display: flex; gap: 8px; }
.pred-prediction { 
  padding: 4px 10px; 
  border-radius: 4px; 
  font-size: 0.85rem;
  font-weight: 500;
}
.pred-prediction.HOME_WIN { background: #e8f5e9; color: #27ae60; }
.pred-prediction.DRAW { background: #fff8e1; color: #f39c12; }
.pred-prediction.AWAY_WIN { background: #e3f2fd; color: #3498db; }
.pred-confidence { 
  padding: 4px 8px; 
  border-radius: 4px; 
  font-size: 0.75rem;
  background: #f0f0f0;
  color: #666;
}
.pred-confidence.LOW { background: #fce4ec; color: #e91e63; }
.pred-verified { font-size: 0.85rem; font-weight: 600; }
.pred-verified .correct { color: #27ae60; }
.pred-verified .wrong { color: #e74c3c; }
.pred-status { font-size: 0.75rem; color: #999; padding: 2px 8px; background: #f0f0f0; border-radius: 4px; }

/* 排行榜 */
.leaderboard-list { display: flex; flex-direction: column; gap: 6px; }
.leaderboard-row { 
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; 
  background: #f8f9fa; 
  border-radius: 6px;
}
.leaderboard-row.me { background: #e8f5e9; border: 1px solid #27ae60; }
.lb-rank { 
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
}
.lb-name { flex: 1; font-weight: 500; }
.lb-accuracy { 
  width: 50px; 
  text-align: right;
  font-size: 0.85rem;
  color: #666;
}
.lb-points { 
  width: 60px; 
  text-align: right;
  font-weight: 600;
  color: #667eea;
}
</style>