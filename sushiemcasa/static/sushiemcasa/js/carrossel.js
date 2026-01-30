document.addEventListener('DOMContentLoaded', function () {
    const track = document.getElementById('track');
    
    if (!track) return;

    const slides = Array.from(track.children);
    
    if (slides.length === 0) return;

    let currentIndex = 0;
    let autoRotateInterval = null;

    const getSlideWidth = () => {
        return slides[0].getBoundingClientRect().width;
    };

    const goToIndex = (targetIndex) => {
        if (targetIndex >= slides.length) {
            targetIndex = 0;
        }
        if (targetIndex < 0) {
            targetIndex = slides.length - 1;
        }

        const currentWidth = getSlideWidth();
        track.style.transform = 'translateX(-' + (currentWidth * targetIndex) + 'px)';
        currentIndex = targetIndex;
    };
    window.moveSlide = function(direction) {
        goToIndex(currentIndex + direction);
        resetAutoRotate(); 
    };

    const startAutoRotate = () => {
        clearInterval(autoRotateInterval);
        autoRotateInterval = setInterval(() => {
            window.moveSlide(1);
        }, 6000); 
    };

    const resetAutoRotate = () => {
        clearInterval(autoRotateInterval);
        startAutoRotate();
    };

    startAutoRotate();

    window.addEventListener('resize', () => {
        const currentWidth = getSlideWidth();
        track.style.transform = 'translateX(-' + (currentWidth * currentIndex) + 'px)';
    });

    let touchStartX = 0;
    let touchEndX = 0;

    track.addEventListener('touchstart', e => {
        touchStartX = e.changedTouches[0].screenX;
    }, {passive: true});

    track.addEventListener('touchend', e => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, {passive: true});

    function handleSwipe() {
        if (touchEndX < touchStartX - 50) {
            window.moveSlide(1);
        }
        
        if (touchEndX > touchStartX + 50) {
            window.moveSlide(-1);
        }
    }
});