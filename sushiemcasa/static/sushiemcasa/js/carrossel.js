/* Carrossel de promoções.
   O deslize no celular é nativo (scroll-snap); este script só liga
   as setas e os pontos e mantém o estado acessível atualizado.
   Não há troca automática de slide (evita conteúdo que se move sozinho). */
document.addEventListener('DOMContentLoaded', function () {
  'use strict';

  var carrossel = document.querySelector('[data-carrossel]');
  if (!carrossel) return;

  var trilho = carrossel.querySelector('.carrossel__trilho');
  var slides = Array.prototype.slice.call(trilho.children);
  var anterior = carrossel.querySelector('[data-carrossel-anterior]');
  var proximo = carrossel.querySelector('[data-carrossel-proximo]');
  var pontos = Array.prototype.slice.call(carrossel.querySelectorAll('.carrossel__ponto'));
  var atual = 0;

  if (slides.length < 2) return;

  function irPara(indice) {
    indice = Math.max(0, Math.min(slides.length - 1, indice));
    trilho.scrollTo({ left: slides[indice].offsetLeft - trilho.offsetLeft, behavior: 'smooth' });
  }

  function atualizar(indice) {
    atual = indice;
    anterior.disabled = indice === 0;
    proximo.disabled = indice === slides.length - 1;
    pontos.forEach(function (p, i) {
      p.setAttribute('aria-current', i === indice ? 'true' : 'false');
    });
    slides.forEach(function (s, i) {
      // slides fora da tela saem da ordem de tabulação
      s.querySelectorAll('a, button').forEach(function (el) {
        if (i === indice) el.removeAttribute('tabindex'); else el.setAttribute('tabindex', '-1');
      });
    });
  }

  anterior.addEventListener('click', function () { irPara(atual - 1); });
  proximo.addEventListener('click', function () { irPara(atual + 1); });
  pontos.forEach(function (p, i) { p.addEventListener('click', function () { irPara(i); }); });

  var espera;
  trilho.addEventListener('scroll', function () {
    clearTimeout(espera);
    espera = setTimeout(function () {
      var passo = slides[1].offsetLeft - slides[0].offsetLeft; // largura + espaço
      var indice = Math.round(trilho.scrollLeft / passo);
      if (indice !== atual) atualizar(indice);
    }, 60);
  }, { passive: true });

  trilho.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') { e.preventDefault(); irPara(atual + 1); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); irPara(atual - 1); }
  });

  atualizar(0);
});
