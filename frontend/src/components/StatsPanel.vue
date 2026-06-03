<template>
  <div class="stats-panel">
    <h3 style="margin-bottom:16px">📊 预测统计</h3>
    
    <div class="stats-grid">
      <div class="stat-item">
        <div class="stat-value">{{ stats.total_predictions || 0 }}</div>
        <div class="stat-label">总预测数</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ Math.round((stats.accuracy_rate || 0) * 100) }}%</div>
        <div class="stat-label">整体准确率</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ stats.upset_predictions || 0 }}</div>
        <div class="stat-label">冷门预测</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ Math.round((stats.upset_accuracy || 0) * 100) }}%</div>
        <div class="stat-label">冷门准确率</div>
      </div>
    </div>

    <h4 style="margin:20px 0 12px">分阶段统计</h4>
    <div v-if="stats.by_stage" class="stage-stats">
      <div v-for="(data, stage) in stats.by_stage" :key="stage" class="stage-item">
        <div class="stage-header">
          <span>{{ getStageName(stage) }}</span>
          <span class="stage-accuracy">{{ Math.round(data.accuracy * 100) }}%</span>
        </div>
        <div class="stage-progress">
          <div 
            class="stage-progress-bar" 
            :style="{ width: data.accuracy * 100 + '%' }"
          ></div>
        </div>
        <div class="stage-detail">
          {{ data.correct }}/{{ data.total }} 正确
        </div>
      </div>
    </div>

    <div class="tips-panel">
      <h5 style="margin-bottom:8px">💡 使用提示</h5>
      <ul style="padding-left:20px;font-size:0.9rem;color:var(--text-muted)">
        <li>冷门指数 ≥ 50 为高冷门潜力</li>
        <li>小组赛冷门更多，淘汰赛趋于正常</li>
        <li>关注已出线球队的轮换情况</li>
        <li>赔率偏离大时值得关注</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatsPanel',
  props: {
    stats: { type: Object, default: () => ({}) }
  },
  methods: {
    getStageName(stage) {
      return {
        'GROUP': '小组赛',
        'ROUND_OF_16': '1/8决赛',
        'QUARTER_FINAL': '1/4决赛',
        'SEMI_FINAL': '半决赛',
        'FINAL': '决赛',
        'THIRD_PLACE': '季军赛'
      }[stage] || stage
    }
  }
}
</script>

<style scoped>
.stage-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.stage-item {
  background: var(--bg);
  padding: 12px;
  border-radius: 8px;
}
.stage-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.9rem;
}
.stage-accuracy {
  font-weight: 600;
  color: var(--primary);
}
.stage-progress {
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}
.stage-progress-bar {
  height: 100%;
  background: var(--primary);
  transition: width 0.3s;
}
.stage-detail {
  margin-top: 4px;
  font-size: 0.8rem;
  color: var(--text-muted);
}
.tips-panel {
  margin-top: 20px;
  padding: 12px;
  background: #f0f7ff;
  border-radius: 8px;
  border-left: 3px solid var(--primary);
}
</style>