document.addEventListener('DOMContentLoaded', function () {
    const track = document.querySelector('.carrossel-track');
    
    if (!track) return;

    const slides = Array.from(track.children);
    const nextButton = document.querySelector('.seta-direita');
    const prevButton = document.querySelector('.seta-esquerda');
    const slideWidth = slides[0].getBoundingClientRect().width;

    let currentIndex = 0;
    let autoRotateInterval = null; 

    
    const moveToSlide = (targetIndex) => {
       
        if (targetIndex >= slides.length) {
            targetIndex = 0;
        }
        if (targetIndex < 0) {
            targetIndex = slides.length - 1;
        }
        
        track.style.transform = 'translateX(-' + slideWidth * targetIndex + 'px)';
        currentIndex = targetIndex;
    }

    
    const advanceNext = () => {
        moveToSlide(currentIndex + 1);
    }

    
    const resetAutoRotate = () => {
        clearInterval(autoRotateInterval); 
        autoRotateInterval = setInterval(advanceNext, 6000);  
    }

    
    nextButton.addEventListener('click', () => {
        advanceNext(); 
        resetAutoRotate(); 
    });

    
    prevButton.addEventListener('click', () => {
        moveToSlide(currentIndex - 1); 
        resetAutoRotate(); // 
    });

    
    resetAutoRotate();
});