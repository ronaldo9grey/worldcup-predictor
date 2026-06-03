<template>
  <div class="bracket-canvas-container">
    <canvas ref="bracketCanvas" class="bracket-canvas"></canvas>
  </div>
</template>

<script>
export default {
  name: 'BracketCanvas',
  props: { knockout: Object },
  mounted() {
    this.drawBracket()
  },
  watch: {
    knockout() { this.drawBracket() }
  },
  methods: {
    drawBracket() {
      const canvas = this.$refs.bracketCanvas
      if (!canvas) return
      
      const ctx = canvas.getContext('2d')
      const width = canvas.parentElement.clientWidth || 900
      const height = 600
      canvas.width = width
      canvas.height = height
      
      // 清空画布
      ctx.fillStyle = '#f8f9fa'
      ctx.fillRect(0, 0, width, height)
      
      // 绘制对阵图
      const rounds = ['R32', 'R16', 'QF', 'SF', 'FI']
      const roundLabels = ['32强', '16强', '8强', '4强', '决赛']
      const matchCount = [16, 8, 4, 2, 1]
      const columnWidth = width / 6
      
      // 绘制标题
      ctx.fillStyle = '#1a472a'
      ctx.font = 'bold 16px sans-serif'
      ctx.fillText('⚔️ 淘汰赛对阵图', 10, 25)
      
      // 绘制每一轮
      for (let col = 0; col < 5; col++) {
        const x = col * columnWidth + 30
        const matches = this.knockout?.[rounds[col]] || []
        const count = matchCount[col]
        const spacing = height / (count + 1)
        
        // 绘制轮次标题
        ctx.fillStyle = '#1a472a'
        ctx.font = 'bold 14px sans-serif'
        ctx.fillText(roundLabels[col], x, 50)
        
        // 绘制每场比赛
        for (let i = 0; i < matches.length; i++) {
          const m = matches[i]
          const y = 70 + i * spacing
          
          this.drawMatch(ctx, m, x, y, columnWidth - 20, col)
        }
      }
      
      // 绘制季军赛（在右侧）
      const thirdMatch = this.knockout?.THIRD?.[0]
      if (thirdMatch) {
        this.drawMatch(ctx, thirdMatch, width - columnWidth + 10, 300, columnWidth - 30, -1)
        ctx.fillStyle = '#666'
        ctx.font = '12px sans-serif'
        ctx.fillText('季军赛', width - columnWidth + 10, 280)
      }
    },
    
    drawMatch(ctx, match, x, y, w, roundIdx) {
      if (!match) return
      
      const h = 40
      const homeWon = match.winner === match.home
      const awayWon = match.winner === match.away
      
      // 背景
      ctx.fillStyle = '#fff'
      ctx.strokeStyle = '#ddd'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.roundRect(x, y, w, h, 6)
      ctx.fill()
      ctx.stroke()
      
      // 主队
      ctx.fillStyle = homeWon ? '#28a745' : '#333'
      ctx.font = homeWon ? 'bold 12px sans-serif' : '12px sans-serif'
      const homeText = `${match.home_name_cn || match.home} ${match.home_score || 0}`
      ctx.fillText(homeText, x + 8, y + 16)
      
      // 分隔线
      ctx.strokeStyle = '#eee'
      ctx.beginPath()
      ctx.moveTo(x + 8, y + 20)
      ctx.lineTo(x + w - 8, y + 20)
      ctx.stroke()
      
      // 客队
      ctx.fillStyle = awayWon ? '#28a745' : '#333'
      ctx.font = awayWon ? 'bold 12px sans-serif' : '12px sans-serif'
      const awayText = `${match.away_name_cn || match.away} ${match.away_score || 0}`
      ctx.fillText(awayText, x + 8, y + 34)
      
      // 胜者标记
      if (match.winner) {
        ctx.fillStyle = '#ffd700'
        ctx.beginPath()
        ctx.arc(x + w - 12, y + (homeWon ? 14 : 30), 6, 0, Math.PI * 2)
        ctx.fill()
      }
      
      // 连接线到下一轮
      if (roundIdx >= 0 && roundIdx < 4 && match.winner) {
        const nextX = x + w + 20
        const nextSpacing = 600 / (16 / Math.pow(2, roundIdx + 1) + 1)
        // 简化：直接画一条线到右侧
        ctx.strokeStyle = '#1a472a'
        ctx.lineWidth = 2
        ctx.beginPath()
        ctx.moveTo(x + w, y + h / 2)
        ctx.lineTo(nextX - 5, y + h / 2)
        ctx.stroke()
      }
    }
  }
}
</script>

<style scoped>
.bracket-canvas-container { background: #f8f9fa; border-radius: 12px; padding: 10px; overflow-x: auto; }
.bracket-canvas { display: block; min-width: 900px; }
</style>