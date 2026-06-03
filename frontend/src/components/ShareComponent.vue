<template>
  <div class="share-component">
    <!-- 分享按钮 -->
    <div class="share-buttons">
      <button class="share-btn wechat" @click="shareToWeChat" title="分享到微信">
        <span class="icon">💬</span>
        <span class="text">微信</span>
      </button>
      <button class="btn weibo" @click="shareToWeibo" title="分享到微博">
        <span class="icon">📝</span>
        <span class="text">微博</span>
      </button>
      <button class="btn link" @click="copyLink" title="复制链接">
        <span class="icon">🔗</span>
        <span class="text">复制</span>
      </button>
      <button class="btn image" @click="generateImage" title="生成图片">
        <span class="icon">🖼️</span>
        <span class="text">图片</span>
      </button>
    </div>
    
    <!-- 分享内容预览 -->
    <div v-if="showPreview" class="share-preview">
      <div class="preview-card" ref="previewCard">
        <div class="card-header">
          <span class="logo">⚽</span>
          <span class="title">世界杯预测</span>
        </div>
        
        <div class="card-body">
          <div class="match-info">
            <div class="team home">
              <span class="flag">{{ getFlag(teams.home) }}</span>
              <span class="name">{{ teams.home }}</span>
            </div>
            <div class="vs">VS</div>
            <div class="team away">
              <span class="flag">{{ getFlag(teams.away) }}</span>
              <span class="name">{{ teams.away }}</span>
            </div>
          </div>
          
          <div class="prediction-result">
            <div class="prediction">预测：{{ predictionText }}</div>
            <div class="confidence" :class="confidenceClass">{{ confidenceEmoji }} {{ confidenceText }}</div>
          </div>
          
          <div v-if="userNickname" class="user-info">
            <span class="nickname">{{ userNickname }}</span>
            <span class="says">预测</span>
          </div>
        </div>
        
        <div class="card-footer">
          <span class="brand">世界杯预测系统</span>
          <span class="qrcode">扫码参与预测</span>
        </div>
      </div>
    </div>
    
    <!-- 复制成功提示 -->
    <div v-if="showCopied" class="copied-toast">
      ✅ 链接已复制
    </div>
    
    <!-- 图片预览弹窗 -->
    <div v-if="showImageModal" class="modal-overlay" @click="showImageModal = false">
      <div class="modal-content" @click.stop>
        <h3>分享图片</h3>
        <div class="image-preview">
          <img :src="generatedImage" alt="分享图片" />
        </div>
        <div class="modal-actions">
          <button class="btn-primary" @click="downloadImage">下载图片</button>
          <button class="btn-secondary" @click="showImageModal = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'ShareComponent',
  props: {
    teams: {
      type: Object,
      required: true
    },
    prediction: {
      type: String,
      required: true
    },
    confidence: {
      type: String,
      required: true
    },
    userNickname: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const showPreview = ref(true)
    const showCopied = ref(false)
    const showImageModal = ref(false)
    const generatedImage = ref('')
    const previewCard = ref(null)
    
    const predictionText = computed(() => {
      const texts = {
        'HOME_WIN': `${props.teams.home}胜`,
        'DRAW': '平局',
        'AWAY_WIN': `${props.teams.away}胜`
      }
      return texts[props.prediction] || props.prediction
    })
    
    const confidenceText = computed(() => {
      const texts = {
        'HIGH': '高信心',
        'MEDIUM': '中信心',
        'LOW': '低信心'
      }
      return texts[props.confidence] || props.confidence
    })
    
    const confidenceEmoji = computed(() => {
      const emojis = {
        'HIGH': '🔥',
        'MEDIUM': '⚡',
        'LOW': '🎲'
      }
      return emojis[props.confidence] || ''
    })
    
    const confidenceClass = computed(() => {
      return props.confidence.toLowerCase()
    })
    
    // 分享到微信
    const shareToWeChat = () => {
      // 微信分享需要通过微信JS-SDK
      alert('请截图分享到微信朋友圈或好友')
    }
    
    // 分享到微博
    const shareToWeibo = () => {
      const text = `我预测${props.teams.home} vs ${props.teams.away}：${predictionText.value} ${confidenceEmoji.value}${confidenceText.value}`
      const url = encodeURIComponent(window.location.href)
      const weiboUrl = `https://service.weibo.com/share/share.php?title=${encodeURIComponent(text)}&url=${url}`
      window.open(weiboUrl, '_blank')
    }
    
    // 复制链接
    const copyLink = async () => {
      const text = `${props.teams.home} vs ${props.teams.away}：我的预测是${predictionText.value} ${confidenceEmoji.value}${confidenceText.value} - 来自世界杯预测系统`
      
      try {
        await navigator.clipboard.writeText(text)
        showCopied.value = true
        setTimeout(() => {
          showCopied.value = false
        }, 2000)
      } catch (error) {
        // 降级方案
        const textarea = document.createElement('textarea')
        textarea.value = text
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
        showCopied.value = true
        setTimeout(() => {
          showCopied.value = false
        }, 2000)
      }
    }
    
    // 生成分享图片
    const generateImage = async () => {
      try {
        // 简化版：使用CSS生成样式化的卡片
        // 实际应用中需要使用html2canvas或canvas API
        showImageModal.value = true
        generatedImage.value = 'data:image/svg+xml;base64,' + btoa(`
          <svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">
            <rect width="400" height="300" fill="#667eea"/>
            <text x="200" y="50" text-anchor="middle" font-size="24" fill="white">⚽ 世界杯预测</text>
            <text x="200" y="120" text-anchor="middle" font-size="20" fill="white">${props.teams.home} vs ${props.teams.away}</text>
            <text x="200" y="170" text-anchor="middle" font-size="28" fill="white">${predictionText.value}</text>
            <text x="200" y="210" text-anchor="middle" font-size="16" fill="white">${confidenceEmoji.value} ${confidenceText.value}</text>
            <text x="200" y="280" text-anchor="middle" font-size="12" fill="white">世界杯预测系统</text>
          </svg>
        `)
      } catch (error) {
        console.error('生成图片失败', error)
      }
    }
    
    // 下载图片
    const downloadImage = () => {
      const link = document.createElement('a')
      link.download = `worldcup-prediction-${props.teams.home}-${props.teams.away}.png`
      link.href = generatedImage.value
      link.click()
    }
    
    // 获取国旗emoji
    const getFlag = (team) => {
      const flags = {
        '阿根廷': '🇦🇷',
        '巴西': '🇧🇷',
        '法国': '🇫🇷',
        '德国': '🇩🇪',
        '英格兰': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
        '西班牙': '🇪🇸',
        '葡萄牙': '🇵🇹',
        '荷兰': '🇳🇱',
        '乌拉圭': '🇺🇾',
        '比利时': '🇧🇪',
        '克罗地亚': '🇭🇷',
        '美国': '🇺🇸',
        '墨西哥': '🇲🇽',
        '日本': '🇯🇵',
        '韩国': '🇰🇷',
      }
      return flags[team] || '⚽'
    }
    
    return {
      showPreview,
      showCopied,
      showImageModal,
      generatedImage,
      previewCard,
      predictionText,
      confidenceText,
      confidenceEmoji,
      confidenceClass,
      shareToWeChat,
      shareToWeibo,
      copyLink,
      generateImage,
      downloadImage,
      getFlag
    }
  }
}
</script>

<style scoped>
.share-component {
  margin-top: 20px;
}

/* 分享按钮 */
.share-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.share-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 10px 20px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.share-btn.wechat {
  background: #07c160;
  color: white;
}

.share-btn.weibo {
  background: #e6162d;
  color: white;
}

.share-btn.link {
  background: #667eea;
  color: white;
}

.share-btn.image {
  background: #ff6b6b;
  color: white;
}

.share-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.share-btn .icon {
  font-size: 18px;
}

/* 分享预览卡片 */
.share-preview {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.preview-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 20px;
  width: 320px;
  color: white;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.card-header .logo {
  font-size: 32px;
}

.card-header .title {
  font-size: 18px;
  font-weight: bold;
}

.card-body {
  background: rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 15px;
}

.match-info {
  display: flex;
  align-items: center;
  justify-content: space-around;
  margin-bottom: 20px;
}

.team {
  text-align: center;
}

.team .flag {
  font-size: 36px;
  margin-bottom: 5px;
}

.team .name {
  font-size: 14px;
}

.vs {
  font-size: 18px;
  font-weight: bold;
  opacity: 0.8;
}

.prediction-result {
  text-align: center;
}

.prediction {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
}

.confidence {
  font-size: 16px;
  opacity: 0.9;
}

.confidence.high { color: #ffd700; }
.confidence.medium { color: #ffa500; }
.confidence.low { color: #87ceeb; }

.user-info {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid rgba(255,255,255,0.2);
  text-align: center;
}

.user-info .nickname {
  font-weight: bold;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  opacity: 0.8;
}

/* 复制成功提示 */
.copied-toast {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0,0,0,0.8);
  color: white;
  padding: 15px 30px;
  border-radius: 8px;
  z-index: 1000;
  animation: fadeInOut 2s;
}

@keyframes fadeInOut {
  0%, 100% { opacity: 0; }
  20%, 80% { opacity: 1; }
}

/* 图片预览弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 20px;
  max-width: 500px;
  width: 90%;
}

.modal-content h3 {
  margin: 0 0 15px 0;
  text-align: center;
}

.image-preview {
  text-align: center;
  margin-bottom: 15px;
}

.image-preview img {
  max-width: 100%;
  border-radius: 8px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.btn-primary {
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 25px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
  border: none;
  padding: 10px 25px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .share-buttons {
    gap: 8px;
  }
  
  .share-btn {
    padding: 8px 15px;
    font-size: 12px;
  }
  
  .share-btn .text {
    display: none;
  }
  
  .share-btn .icon {
    font-size: 20px;
  }
  
  .preview-card {
    width: 280px;
    padding: 15px;
  }
  
  .team .flag {
    font-size: 28px;
  }
  
  .team .name {
    font-size: 12px;
  }
  
  .prediction {
    font-size: 20px;
  }
}
</style>