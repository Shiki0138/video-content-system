// VideoAI Studio - Wizard JavaScript
class VideoAIWizard {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 6;
        this.sessionId = window.sessionId;
        this.selectedCaptionStyle = null;
        this.selectedThumbnailStyle = null;
        this.uploadedVideo = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.updateProgress();
        console.log('🎬 VideoAI Studio Wizard 初期化完了');
    }
    
    setupEventListeners() {
        // ファイルアップロード
        const uploadZone = document.getElementById('uploadZone');
        const videoInput = document.getElementById('videoInput');
        const selectFileBtn = document.getElementById('selectFileBtn');
        const uploadBtn = document.getElementById('uploadBtn');
        
        // ドラッグ&ドロップ
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });
        
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });
        
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleVideoSelect(files[0]);
            }
        });
        
        // ファイル選択
        selectFileBtn.addEventListener('click', () => {
            videoInput.click();
        });
        
        videoInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleVideoSelect(e.target.files[0]);
            }
        });
        
        // アップロードボタン
        uploadBtn.addEventListener('click', () => {
            this.uploadVideo();
        });
        
        // 文字起こしボタン
        document.getElementById('transcribeBtn').addEventListener('click', () => {
            this.processTranscribe();
        });
        
        // キャプションオプション
        document.querySelectorAll('.option-card').forEach(card => {
            card.addEventListener('click', () => {
                this.selectCaptionStyle(card);
            });
        });
        
        // キャプション生成ボタン
        document.getElementById('captionBtn').addEventListener('click', () => {
            this.processCaption();
        });
        
        // コンテンツ生成ボタン
        document.getElementById('contentBtn').addEventListener('click', () => {
            this.processContent();
        });
        
        // サムネイルオプション
        document.querySelectorAll('.thumbnail-card').forEach(card => {
            card.addEventListener('click', () => {
                this.selectThumbnailStyle(card);
            });
        });
        
        // サムネイル生成ボタン
        document.getElementById('thumbnailBtn').addEventListener('click', () => {
            this.processThumbnail();
        });
        
        // エクスポートボタン
        document.getElementById('exportBtn').addEventListener('click', () => {
            this.exportContent();
        });
        
        // プレビューボタン
        document.getElementById('previewBtn').addEventListener('click', () => {
            this.openPreview();
        });
    }
    
    handleVideoSelect(file) {
        // ファイル検証
        const allowedTypes = ['video/mp4', 'video/mov', 'video/avi', 'video/mkv'];
        if (!allowedTypes.includes(file.type)) {
            this.showError('対応していない動画形式です。MP4, MOV, AVI, MKVファイルを選択してください。');
            return;
        }
        
        const maxSize = 2 * 1024 * 1024 * 1024; // 2GB
        if (file.size > maxSize) {
            this.showError('ファイルサイズが大きすぎます。2GB以下のファイルを選択してください。');
            return;
        }
        
        this.uploadedVideo = file;
        
        // ファイル情報表示
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileSize').textContent = this.formatFileSize(file.size);
        document.getElementById('uploadInfo').classList.remove('hidden');
        
        console.log('📁 動画ファイル選択:', file.name, this.formatFileSize(file.size));
    }
    
    async uploadVideo() {
        if (!this.uploadedVideo) {
            this.showError('動画ファイルを選択してください。');
            return;
        }
        
        this.showLoading('動画アップロード中...', 'ファイルをサーバーに送信しています');
        
        const formData = new FormData();
        formData.append('session_id', this.sessionId);
        formData.append('video', this.uploadedVideo);
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('✅ アップロード完了:', result.video_info);
                this.hideLoading();
                this.nextStep();
            } else {
                throw new Error(result.message || 'アップロードに失敗しました');
            }
        } catch (error) {
            console.error('❌ アップロードエラー:', error);
            this.hideLoading();
            this.showError('アップロードに失敗しました: ' + error.message);
        }
    }
    
    async processTranscribe() {
        this.showLoading('AI音声認識中...', 'Whisper AIが動画から音声を文字起こししています');
        
        try {
            const response = await fetch('/api/process/transcribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('✅ 文字起こし完了:', result.transcript);
                
                // 結果表示
                document.getElementById('transcribeStatus').textContent = '文字起こし完了！';
                document.getElementById('transcribeDetails').innerHTML = `
                    <p>📝 ${result.transcript.word_count}語を認識</p>
                    <p>⏱️ ${Math.floor(result.transcript.duration / 60)}分${Math.floor(result.transcript.duration % 60)}秒</p>
                `;
                
                this.hideLoading();
                
                // 3秒後に次のステップへ
                setTimeout(() => {
                    this.nextStep();
                }, 3000);
            } else {
                throw new Error(result.message || '文字起こしに失敗しました');
            }
        } catch (error) {
            console.error('❌ 文字起こしエラー:', error);
            this.hideLoading();
            this.showError('文字起こしに失敗しました: ' + error.message);
        }
    }
    
    selectCaptionStyle(card) {
        // 他のカードの選択を解除
        document.querySelectorAll('.option-card').forEach(c => {
            c.classList.remove('selected');
        });
        
        // 選択されたカードをマーク
        card.classList.add('selected');
        this.selectedCaptionStyle = card.dataset.style;
        
        // ボタンを有効化
        const captionBtn = document.getElementById('captionBtn');
        captionBtn.classList.remove('disabled');
        
        console.log('📝 キャプションスタイル選択:', this.selectedCaptionStyle);
    }
    
    async processCaption() {
        if (!this.selectedCaptionStyle) {
            this.showError('キャプションスタイルを選択してください。');
            return;
        }
        
        this.showLoading('キャプション生成中...', `${this.selectedCaptionStyle}スタイルでキャプションを作成しています`);
        
        try {
            const response = await fetch('/api/process/caption', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    style: this.selectedCaptionStyle
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('✅ キャプション生成完了:', result.captions);
                this.hideLoading();
                this.nextStep();
            } else {
                throw new Error(result.message || 'キャプション生成に失敗しました');
            }
        } catch (error) {
            console.error('❌ キャプション生成エラー:', error);
            this.hideLoading();
            this.showError('キャプション生成に失敗しました: ' + error.message);
        }
    }
    
    async processContent() {
        const title = document.getElementById('videoTitle').value.trim();
        if (!title) {
            this.showError('動画タイトルを入力してください。');
            return;
        }
        
        this.showLoading('AIコンテンツ生成中...', 'ブログ記事、X投稿、YouTube説明文を生成しています');
        
        try {
            const response = await fetch('/api/process/content', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    title: title
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('✅ コンテンツ生成完了:', result.content);
                this.hideLoading();
                this.nextStep();
            } else {
                throw new Error(result.message || 'コンテンツ生成に失敗しました');
            }
        } catch (error) {
            console.error('❌ コンテンツ生成エラー:', error);
            this.hideLoading();
            this.showError('コンテンツ生成に失敗しました: ' + error.message);
        }
    }
    
    selectThumbnailStyle(card) {
        // 他のカードの選択を解除
        document.querySelectorAll('.thumbnail-card').forEach(c => {
            c.classList.remove('selected');
        });
        
        // 選択されたカードをマーク
        card.classList.add('selected');
        this.selectedThumbnailStyle = card.dataset.style;
        
        // ボタンを有効化
        const thumbnailBtn = document.getElementById('thumbnailBtn');
        thumbnailBtn.classList.remove('disabled');
        
        console.log('🎨 サムネイルスタイル選択:', this.selectedThumbnailStyle);
    }
    
    async processThumbnail() {
        if (!this.selectedThumbnailStyle) {
            this.showError('サムネイルスタイルを選択してください。');
            return;
        }
        
        this.showLoading('サムネイル生成中...', `${this.selectedThumbnailStyle}スタイルでサムネイルを作成しています`);
        
        try {
            const response = await fetch('/api/process/thumbnail', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    style: this.selectedThumbnailStyle
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('✅ サムネイル生成完了:', result.thumbnail);
                this.hideLoading();
                this.updateExportSummary();
                this.nextStep();
            } else {
                throw new Error(result.message || 'サムネイル生成に失敗しました');
            }
        } catch (error) {
            console.error('❌ サムネイル生成エラー:', error);
            this.hideLoading();
            this.showError('サムネイル生成に失敗しました: ' + error.message);
        }
    }
    
    async updateExportSummary() {
        try {
            const response = await fetch(`/api/session/${this.sessionId}`);
            const session = await response.json();
            
            if (session.data) {
                const data = session.data;
                
                // ブログサマリー
                if (data.content && data.content.blog) {
                    const blogSections = data.content.blog.sections ? data.content.blog.sections.length : 0;
                    document.getElementById('blogSummary').textContent = `${blogSections}セクション生成済み`;
                }
                
                // X投稿サマリー
                if (data.content && data.content.twitter) {
                    const xLength = data.content.twitter.length;
                    document.getElementById('xSummary').textContent = `${xLength}文字の投稿文`;
                }
                
                // YouTubeサマリー
                if (data.content && data.content.youtube) {
                    const youtubeLength = data.content.youtube.length;
                    document.getElementById('youtubeSummary').textContent = `${youtubeLength}文字の説明文`;
                }
                
                // サムネイルサマリー
                if (data.thumbnail_style) {
                    document.getElementById('thumbnailSummary').textContent = `${data.thumbnail_style}スタイル`;
                }
            }
        } catch (error) {
            console.error('❌ サマリー更新エラー:', error);
        }
    }
    
    async exportContent() {
        const exportFormats = [];
        
        if (document.getElementById('exportBlog').checked) exportFormats.push('blog');
        if (document.getElementById('exportX').checked) exportFormats.push('x');
        if (document.getElementById('exportYoutube').checked) exportFormats.push('youtube');
        
        if (exportFormats.length === 0) {
            this.showError('エクスポートする形式を選択してください。');
            return;
        }
        
        this.showLoading('エクスポート中...', '選択されたコンテンツをファイルに保存しています');
        
        try {
            const response = await fetch('/api/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    formats: exportFormats
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('✅ エクスポート完了:', result.exported_files);
                this.hideLoading();
                this.showSuccess('エクスポートが完了しました！', 'ファイルが保存されました。プレビューで確認できます。');
            } else {
                throw new Error(result.message || 'エクスポートに失敗しました');
            }
        } catch (error) {
            console.error('❌ エクスポートエラー:', error);
            this.hideLoading();
            this.showError('エクスポートに失敗しました: ' + error.message);
        }
    }
    
    openPreview() {
        // 別ウィンドウでプレビューサーバーを開く
        window.open('http://localhost:8002', '_blank');
    }
    
    nextStep() {
        if (this.currentStep < this.totalSteps) {
            // 現在のステップを非表示
            document.getElementById(`step${this.currentStep}`).classList.remove('active');
            document.querySelector(`[data-step="${this.currentStep}"]`).classList.remove('active');
            document.querySelector(`[data-step="${this.currentStep}"]`).classList.add('completed');
            
            // 次のステップを表示
            this.currentStep++;
            document.getElementById(`step${this.currentStep}`).classList.add('active');
            document.querySelector(`[data-step="${this.currentStep}"]`).classList.add('active');
            
            this.updateProgress();
            
            console.log(`📍 ステップ ${this.currentStep} に移行`);
        }
    }
    
    updateProgress() {
        const progressPercent = (this.currentStep / this.totalSteps) * 100;
        document.getElementById('progressFill').style.width = `${progressPercent}%`;
    }
    
    showLoading(title, message) {
        document.getElementById('loadingTitle').textContent = title;
        document.getElementById('loadingMessage').textContent = message;
        document.getElementById('loadingModal').classList.remove('hidden');
    }
    
    hideLoading() {
        document.getElementById('loadingModal').classList.add('hidden');
    }
    
    showError(message) {
        alert('❌ エラー: ' + message);
    }
    
    showSuccess(title, message) {
        alert('✅ ' + title + '\\n' + message);
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// アプリ初期化
document.addEventListener('DOMContentLoaded', () => {
    window.wizard = new VideoAIWizard();
});

// エラーハンドリング
window.addEventListener('error', (e) => {
    console.error('🚨 JavaScript エラー:', e.error);
});

// デバッグ用
window.DEBUG = {
    currentStep: () => window.wizard?.currentStep,
    sessionId: () => window.wizard?.sessionId,
    getSession: async () => {
        const response = await fetch(`/api/session/${window.wizard.sessionId}`);
        return await response.json();
    }
};