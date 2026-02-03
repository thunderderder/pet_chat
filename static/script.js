document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const uploadSection = document.getElementById('upload-section');
    const loadingSection = document.getElementById('loading-section');
    const resultSection = document.getElementById('result-section');
    const resultImage = document.getElementById('result-image');
    const resultText = document.getElementById('result-text');
    const retryBtn = document.getElementById('retry-btn');
    const saveBtn = document.getElementById('save-btn');

    fileInput.addEventListener('change', handleFileSelect);
    retryBtn.addEventListener('click', resetUI);
    saveBtn.addEventListener('click', saveCard);

    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Show loading
        uploadSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');

        // Upload and analyze
        uploadImage(file);
    }

    async function uploadImage(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Analysis failed');
            }

            const data = await response.json();
            showResult(data);
        } catch (error) {
            console.error(error);
            alert('解读失败，请重试');
            resetUI();
        }
    }

    function showResult(data) {
        loadingSection.classList.add('hidden');
        resultSection.classList.remove('hidden');

        resultImage.src = data.image_url;
        resultText.textContent = data.text;
    }

    function resetUI() {
        fileInput.value = '';
        resultSection.classList.add('hidden');
        loadingSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
    }

    function saveCard() {
        const card = document.getElementById('share-card');
        
        // Use html2canvas to capture the card
        html2canvas(card, {
            scale: 2, // Higher resolution
            useCORS: true,
            allowTaint: true,
            backgroundColor: null
        }).then(canvas => {
            const link = document.createElement('a');
            link.download = `pet-thought-${Date.now()}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
        }).catch(err => {
            console.error('Screenshot failed', err);
            alert('保存失败，请截屏保存');
        });
    }
});
