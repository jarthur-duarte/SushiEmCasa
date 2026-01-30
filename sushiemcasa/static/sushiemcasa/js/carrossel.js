document.addEventListener('DOMContentLoaded', function () {
    const track = document.getElementById('track');
    const container = document.querySelector('.carrossel-viewport'); 
    
    if (!track || !container) return;

    const slides = Array.from(track.children);
    if (slides.length === 0) return;

    let currentIndex = 0;
    let autoRotateInterval = null;
    const getSlideWidth = () => {
        return container.getBoundingClientRect().width; 
    };

    const updateTrackPosition = () => {
        const currentWidth = getSlideWidth();
        track.style.transform = 'translateX(-' + (currentWidth * currentIndex) + 'px)';
    };

    const goToIndex = (targetIndex) => {
        if (targetIndex >= slides.length) targetIndex = 0;
        if (targetIndex < 0) targetIndex = slides.length - 1;

        currentIndex = targetIndex;
        updateTrackPosition();
    };

    window.moveSlide = function(direction) {
        goToIndex(currentIndex + direction);
        resetAutoRotate();
    };

    const startAutoRotate = () => {
        clearInterval(autoRotateInterval);
        autoRotateInterval = setInterval(() => {
            window.moveSlide(1);
        }, 5000);
    };

    const resetAutoRotate = () => {
        clearInterval(autoRotateInterval);
        startAutoRotate();
    };

    startAutoRotate();

    window.addEventListener('resize', updateTrackPosition);

    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;
    const minSwipeDistance = 30; 

    container.addEventListener('touchstart', e => {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
    }, {passive: true});

    container.addEventListener('touchend', e => {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleSwipe();
    }, {passive: true});

    function handleSwipe() {
        const deltaX = touchEndX - touchStartX;
        const deltaY = touchEndY - touchStartY;

        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            if (Math.abs(deltaX) > minSwipeDistance) {
                if (deltaX < 0) {
                    window.moveSlide(1); 
                } else {
                    window.moveSlide(-1);
                }
            }
        }
    }
});