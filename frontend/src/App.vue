<template>
  <div class="app">
    <header class="header">
      <div class="header-content">
        <h1><span class="logo">⚽</span> 世界杯预测</h1>
        <span class="header-sub">2026 美加墨</span>
      </div>
    </header>

    <div class="container">
      <div class="tabs">
        <div :class="['tab', { active: activeTab === 'groups' }]" @click="activeTab = 'groups'">
          <span class="icon">🏆</span>
          <span class="text">小组赛</span>
        </div>
        <div :class="['tab', { active: activeTab === 'simulate' }]" @click="activeTab = 'simulate'">
          <span class="icon">👑</span>
          <span class="text">冠军之路</span>
        </div>
        <div :class="['tab', { active: activeTab === 'user' }]" @click="activeTab = 'user'">
          <span class="icon">🎯</span>
          <span class="text">我预测</span>
        </div>
        <div :class="['tab', { active: activeTab === 'leaderboard' }]" @click="activeTab = 'leaderboard'">
          <span class="icon">🏅</span>
          <span class="text">排行榜</span>
        </div>
        <div :class="['tab', { active: activeTab === 'accuracy' }]" @click="activeTab = 'accuracy'">
          <span class="icon">📊</span>
          <span class="text">准确率</span>
        </div>
        <div :class="['tab', { active: activeTab === 'data-extension' }]" @click="activeTab = 'data-extension'">
          <span class="icon">📈</span>
          <span class="text">数据</span>
        </div>
        <div :class="['tab', { active: activeTab === 'history' }]" @click="activeTab = 'history'">
          <span class="icon">📜</span>
          <span class="text">历史</span>
        </div>

        <div :class="['tab', { active: activeTab === 'models' }]" @click="activeTab = 'models'">
          <span class="icon">🤖</span>
          <span class="text">模型</span>
        </div>
        <div :class="['tab', { active: activeTab === 'algorithm' }]" @click="activeTab = 'algorithm'">
          <span class="icon">🔬</span>
          <span class="text">算法</span>
        </div>
      </div>

      <div v-if="activeTab === 'groups'">
        <GroupDetail @show-match="showMatchDetail" />
      </div>

      <div v-if="activeTab === 'simulate'">
        <SimulationResult />
      </div>

      <div v-if="activeTab === 'user'">
        <UserPredict />
      </div>

      <div v-if="activeTab === 'accuracy'">
        <AccuracyDashboard />
      </div>

      <div v-if="activeTab === 'history'">
        <HistoryData />
      </div>

      <div v-if="activeTab === 'algorithm'">
        <AlgorithmInfo :info="algorithmInfo" />
      </div>



      <div v-if="activeTab === 'models'">
        <ModelComparison />
      </div>

      <div v-if="activeTab === 'data-extension'">
        <DataExtension />
      </div>

      <div v-if="activeTab === 'leaderboard'">
        <Leaderboard />
      </div>

      <!-- 比赛详情弹窗 -->
      <div v-if="matchDetail" class="modal-overlay" @click="matchDetail = null">
        <div class="modal-content" @click.stop>
          <MatchDetailPanel :data="matchDetail" @close="matchDetail = null" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import GroupDetail from './components/GroupDetail.vue'
import SimulationResult from './components/SimulationResult.vue'
import UserPredict from './components/UserPredict.vue'
import AccuracyDashboard from './components/AccuracyDashboard.vue'
import HistoryData from './components/HistoryData.vue'
import AlgorithmInfo from './components/AlgorithmInfo.vue'
import ModelComparison from './components/ModelComparison.vue'
import DataExtension from './components/DataExtension.vue'
import Leaderboard from './components/Leaderboard.vue'
import MatchDetailPanel from './components/MatchDetailPanel.vue'


const activeTab = ref('groups')
const algorithmInfo = ref(null)
const matchDetail = ref(null)

async function loadAlgorithm() {
  try {
    const resp = await fetch('/worldcup/api/algorithm')
    algorithmInfo.value = await resp.json()
  } catch(e) {}
}

async function showMatchDetail({ home, away, group, idx }) {
  try {
    const resp = await fetch(`/worldcup/api/groups/${group}/match/${idx}`)
    matchDetail.value = await resp.json()
  } catch(e) {}
}

onMounted(() => { loadAlgorithm() })
</script>

<style>
/* 全局样式 */
* {
  box-sizing: border-box;
  -webkit-tap-highlight-color: transparent;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 头部 */
.header { 
  background:linear-gradient(135deg,#1a472a,#2d5a3d); 
  color:white; 
  padding:14px; 
  position:sticky; 
  top:0; 
  z-index:100; 
}

.header-content { 
  max-width:1200px; 
  margin:0 auto; 
  display:flex; 
  justify-content:space-between; 
  align-items:center; 
}

.header h1 { 
  font-size:1.2rem; 
  display:flex; 
  align-items:center; 
  gap:8px; 
}

.header-sub { 
  font-size:0.75rem; 
  opacity:0.8; 
}

.logo { 
  font-size:1.4rem; 
}

/* 容器 */
.container { 
  max-width:1200px; 
  margin:0 auto; 
  padding:12px; 
}

/* 标签页 */
.tabs { 
  display:flex; 
  background:white; 
  border-radius:10px; 
  padding:3px; 
  margin:12px 0; 
  box-shadow:0 1px 4px rgba(0,0,0,0.06); 
  flex-wrap: nowrap;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}

.tabs::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}

.tab { 
  flex: 0 0 auto;
  padding:10px 16px; 
  text-align:center; 
  border-radius:7px; 
  cursor:pointer; 
  font-weight:500; 
  color:#666; 
  font-size:0.85rem; 
  transition:all 0.2s; 
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.tab .icon {
  font-size: 1rem;
}

.tab .text {
  font-size: 0.8rem;
}

.tab.active { 
  background:#1a472a; 
  color:white; 
}

/* 模态框 */
.modal-overlay { 
  position:fixed; 
  inset:0; 
  background:rgba(0,0,0,0.5); 
  z-index:1000; 
  display:flex; 
  align-items:center; 
  justify-content:center; 
  padding:16px; 
}

.modal-content { 
  background:white; 
  padding:20px; 
  border-radius:16px; 
  max-width:90vw; 
  max-height:90vh; 
  overflow:auto; 
  width:400px; 
}

/* 移动端适配 */
@media (max-width: 768px) {
  .header {
    padding: 10px;
  }
  
  .header h1 {
    font-size: 1rem;
  }
  
  .logo {
    font-size: 1.2rem;
  }
  
  .header-sub {
    font-size: 0.65rem;
  }
  
  .container {
    padding: 8px;
  }
  
  .tabs {
    padding: 2px;
    margin: 8px 0;
    border-radius: 8px;
  }
  
  .tab {
    padding: 8px 12px;
    border-radius: 6px;
    gap: 4px;
  }
  
  .tab .icon {
    font-size: 0.9rem;
  }
  
  .tab .text {
    font-size: 0.7rem;
  }
  
  .modal-content {
    width: 95vw;
    padding: 15px;
    border-radius: 12px;
  }
}

@media (max-width: 480px) {
  .header h1 {
    font-size: 0.9rem;
  }
  
  .logo {
    font-size: 1rem;
  }
  
  .header-sub {
    display: none;
  }
  
  .container {
    padding: 6px;
  }
  
  .tabs {
    padding: 2px;
    margin: 6px 0;
  }
  
  .tab {
    padding: 7px 10px;
    gap: 3px;
  }
  
  .tab .icon {
    font-size: 0.85rem;
  }
  
  .tab .text {
    font-size: 0.65rem;
  }
}

/* 触摸优化 */
@media (hover: none) and (pointer: coarse) {
  .tab {
    min-height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  button, .button {
    min-height: 44px;
    min-width: 44px;
  }
}

/* 安全区域适配（iPhone X等） */
@supports (padding: max(0px)) {
  .container {
    padding-left: max(12px, env(safe-area-inset-left));
    padding-right: max(12px, env(safe-area-inset-right));
    padding-bottom: max(12px, env(safe-area-inset-bottom));
  }
  
  .header {
    padding-top: max(14px, env(safe-area-inset-top));
  }
}
</style>
