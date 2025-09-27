document.addEventListener('DOMContentLoaded', function() {

    const botoesFiltro = document.querySelectorAll('.botao-filtro');
    
    const paineis = document.querySelectorAll('.painel-opcoes');

   
    botoesFiltro.forEach(botao => {
        botao.addEventListener('click', () => {
            
            const filtroAlvo = botao.dataset.filter;
            const painelAlvo = document.getElementById(filtroAlvo);
            const isAtivo = botao.classList.contains('ativo');
            
            paineis.forEach(p => p.style.display = 'none');
            botoesFiltro.forEach(b => b.classList.remove('ativo'));

            if (!isAtivo) {
                
                botao.classList.add('ativo');
                painelAlvo.style.display = 'block';
            }
            
        });
    });
});