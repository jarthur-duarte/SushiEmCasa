# Projeto SushiEmCasa - Delivery de Sushi Web Application
<p align="center">
  <!-- Badges de tecnologias -->
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white" alt="Python Badge"/>
  <img src="https://img.shields.io/badge/Django-5.1-green?logo=django&logoColor=white" alt="Django Badge"/>
  <img src="https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql&logoColor=white" alt="PostgreSQL Badge"/>
  <img src="https://img.shields.io/badge/Azure-Deploy-blue?logo=microsoftazure&logoColor=white" alt="Azure Badge"/>
  <img src="https://img.shields.io/badge/Figma-Prototype-ff69b4?logo=figma&logoColor=white" alt="Figma Badge"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License Badge"/>
</p>

Este é um projeto desenvolvido para atender às necessidades de um cliente real, com o objetivo principal de otimizar o processo de recebimento de pedidos e melhorar a experiência do cliente no gerenciamento de suas solicitações.

<details>
  <summary><strong>📋 Funcionalidades Principais</strong></summary>


  <h3>👤 Para o Usuário (Cliente)</h3>

- Cardápio: Visualização do menu completo.

- Agenda: Consulta à agenda e disponibilidade da administradora/restaurante.

- Pedidos: Acompanhamento do status dos pedidos realizados.

- Contatos: Acesso rápido às informações de contato do restaurante.

  <h3>👩‍💼 Para a administradora</h3>

- Cardápio: Visualização do menu completo.

- Agenda: Consulta à agenda e disponibilidade da administradora/restaurante.

- Pedidos: Acompanhamento do status dos pedidos realizados.

- Contatos: Acesso rápido às informações de contato do restaurante.


  </details>


## 🧩 Estrutura do Projeto
<details>

```
SushiEmCasa
.
├── .github/
│   └── workflows/
│       └── main_sushiemcasa.yml
│
├── .vscode/
│   └── settings.json
│
├── project/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── sushi_em_casa/ # app 1
│
├── usuario/ # app 2
│
├── .gitignore
├── apoio.txt
├── CONTRIBUTING.md
├── LICENSE
├── manage.py
├── README.md
└── requirements.txt


```
</details>


## 📚 Documentação

Toda a documentação técnica do projeto — incluindo arquitetura, decisões técnicas, endpoints e padrões adotados — está disponível no Google Docs:

🔗 **Documentação Técnica:**  
https://docs.google.com/document/d/1KC3Db0AT6AEDgvPb-e6kgqTNkPvWHFwfWEnhjRgizXg/edit?usp=sharing





---



## 📦 Entregas do Projeto

<details>
  <summary><strong>Entrega 01</strong></summary>

### 📋 Backlog das Histórias
![backlog1](https://github.com/user-attachments/assets/7be62ea5-96e6-48cd-a199-e6bd32f49c05)

**📄 Documento de Histórias:**  
[👉 Acessar no Google Docs](https://docs.google.com/document/d/1KayEPV1MaKPZ35tbp7ELZTTsZCNPEVOBjSXBdGyzNq4/edit?usp=sharing)

---

### 🧭 Quadro da Sprint
![sprint1](https://github.com/user-attachments/assets/1436020e-0ea8-4a6b-9b40-537f327c8c4e)  
![quadro_sprint1](https://github.com/user-attachments/assets/b8c205c4-55c5-4d3c-91c2-3b1896264c9d)  
![quadro_sprint2](https://github.com/user-attachments/assets/4073efb8-2f2b-4b92-9a62-8bf8865c3174)  
![quadro_sprint3](https://github.com/user-attachments/assets/bdf90868-af78-4437-93ee-5e83365a4f7f)  

---

### 🎨 Protótipos no Figma

- [História 1: Home (Início / Cardápio)](https://www.figma.com/design/h5uNU0gpRIxWJsk2XRndn6/SushiEmCasa?node-id=118-664&t=lUaHGZnOo4t34knr-1)  
- [Histórias 2 e 3: Basket (Carrinho)](https://www.figma.com/design/h5uNU0gpRIxWJsk2XRndn6/SushiEmCasa?node-id=1-10&t=lUaHGZnOo4t34knr-1)  
- [História 4: Orders (Pedidos)](https://www.figma.com/design/h5uNU0gpRIxWJsk2XRndn6/SushiEmCasa?node-id=168-526&t=lUaHGZnOo4t34knr-1)  
- [História 5: Contact (Contato)](https://www.figma.com/design/h5uNU0gpRIxWJsk2XRndn6/SushiEmCasa?node-id=0-1&t=lUaHGZnOo4t34knr-1)  

💡 **Como acessar os protótipos:**
1. Clique no link da história desejada;  
2. Caso não tenha conta no Figma, crie uma gratuita;  
3. Explore as telas e interações livremente.  

---

### ▶️ Screencast do Protótipo
🎥 [Assista no YouTube](https://youtu.be/U1-svoPBy7I?si=bfKGpyERBseCtbzY)

</details>


<details>
  <summary><strong>Entrega 02</strong></summary>

### 👩‍💻 Relatório de Pair Programming

<details>
<summary>🏠 Homepage (História 1)</summary>

**Objetivo:** Exibir o cardápio dividido por categorias com descrição dos produtos.  
**Dupla:** Maria Eduarda Souza de Oliveira e Arthur Reis Gomes De Mello Queiroz  
**Ferramentas:** HTML, CSS, JavaScript, Jira  
**Aprendizados:** Comunicação e agilidade no desenvolvimento colaborativo.
</details>

---

<details>
<summary>☎️ Contato (História 7)</summary>

**Objetivo:** Criar uma página que permita contato direto com o estabelecimento.  
**Dupla:** Luiza Barbosa Almeida da Silva e João Arthur Gomes Duarte  
**Ferramentas:** Django, HTML, CSS, Discord, Jira  
**Aprendizados:** Integração eficiente entre backend e frontend.
</details>

---

<details>
<summary>🍙 Pedidos (História 9)</summary>

**Objetivo:** Exibir tempo estimado de preparo do pedido.  
**Dupla:** Bernardo Guimarães e Cauã Parente  
**Ferramentas:** Django, Jira, Discord  
**Aprendizados:** Coordenação eficaz e resolução de bugs em tempo real.
</details>

---

### 🪲 Issue Tracker  
![Issues](https://github.com/user-attachments/assets/f47d58bb-6803-4ae4-b6a4-05b4c3b34c68)  
![Issues](https://github.com/user-attachments/assets/93fe0867-aea6-4b6d-8f73-89cdcf51a76f)

---

### ▶️ Screencast da Implementação
🎥 [Assista no YouTube](https://youtu.be/cHm_dSqf8RY)

---

### 🌐 Deploy
🔗 [Acessar SushiEmCasa Online](https://sushiemcasa-atgpdfcggsdccvbs.brazilsouth-01.azurewebsites.net/)

</details>

</details>

<details>
  <summary><strong>Entrega 03</strong></summary>

  ### 👩‍💻 Relatório de Pair Programming

<details>
<summary>🛒 Carrinho de Compras (História 1)</summary>

**Objetivo:** Permitir ao usuário revisar e editar itens antes da finalização.  
**Dupla:** Luiza Barbosa Almeida da Silva e João Arthur Gomes Duarte  
**Ferramentas:** HTML, CSS (SASS), JS, Jira  
**Aprendizados:** Melhor controle de estado e otimização da experiência do usuário.
</details>

---

<details>
<summary>📅 Agendamento de Entrega (História 2)</summary>

**Objetivo:** Permitir agendar entrega com no mínimo 24h de antecedência.  
**Dupla:** Cauã Parente e Arthur Queiroz  
**Ferramentas:** Django, HTML, CSS, JS, Figma, Discord  
**Aprendizados:** Integração eficiente entre frontend e backend com validações robustas.
</details>

---

<details>
<summary>🏠 Modelagem de Produto e Home (História 3)</summary>

**Objetivo:** Exibir categorias e produtos em destaque.  
**Dupla:** Bernardo Guimarães e Maria Eduarda Souza  
**Ferramentas:** PostgreSQL, Node.js/Express, HTML, CSS, JS  
**Aprendizados:** Consistência entre banco de dados e consumo de API no frontend.
</details>

---

### 📊 Quadro da Sprint  
<img src="https://github.com/user-attachments/assets/115ed2f4-eb63-4fdf-86e6-47fd592cea2e" width="100%"/>

### 🧩 Backlog das Histórias  
<img src="https://github.com/user-attachments/assets/e3735410-7432-4868-b4b2-911eeee341fb" width="100%"/>

---

### ▶️ Screencasts  
- [Deploy e Build](https://www.youtube.com/watch?v=G5fLzXbcffI)  
- [Testes Automatizados](https://www.youtube.com/watch?v=AbHJrqiWYWs)

</details>



<details>
  <summary><strong>Entrega 04</strong></summary>

  ### 👩‍💻 Relatório de Pair Programming

<details>
<summary>✏️ Alteração de preços</summary>

**Objetivo:** Implementa uma seção de gerenciamento de preços no painel administrativo.  
**Dupla:** Arthur Reis Gomes De Mello Queiroz e Bernardo Guimarães Nunes Palhares  
**Ferramentas:** HTML, CSS, JS, Python, Django e Discord.
**Aprendizados:** Integração eficiente entre frontend e backend, gerenciando o banco de dados em paralelo.
</details>

---

<details>
<summary>⏱️ Alteração dos horários de funcionamento</summary>

**Objetivo:** Local onde a administradora poderá configurar o status de operação da loja para cada dia da semana.  
**Dupla:** Cauã parente e João Arthur Gomes Duarte  
**Ferramentas:** Django, HTML, CSS, JS, Discord, Jira  
**Aprendizados:** Desenvolvimento e integração eficiente entre backend e frontend.
</details>

---

<details>
<summary>💬 Recebimento do pedido via Whatsapp</summary>

**Objetivo:** Recebimento do pedido e seus detalhes via Whatsapp, para a administradora avaliar sua viabilidade.  
**Dupla:** Luiza Barbosa Almeida da Silva e Maria Eduarda Souza
**Ferramentas:** Django, Jira, Discord e API do Whatsapp.  
**Aprendizados:** Dominamos o redirecionamento para o Whatsapp em mensagem devidamente organizada e formatada.
</details>

---


  ### 📊 Quadro da Sprint

  ![Lista](https://github.com/user-attachments/assets/7342a618-e651-464e-87c9-dad09ad43daf)

  ![quadro_sprint4](https://github.com/user-attachments/assets/622faaea-87cc-457d-b4b6-f89b47c25739)

  ### 🧩 Backlog das Histórias  
  ![backlog](https://github.com/user-attachments/assets/fd6a1ed4-0d8c-44d2-acbd-6b22a634f8bd)

  ### 🔗 Documentação técnica

  ### Acesse aqui: https://docs.google.com/document/d/1KC3Db0AT6AEDgvPb-e6kgqTNkPvWHFwfWEnhjRgizXg/edit?usp=sharing

  ### 🪲 Issue Tracker 

  ![Issues](https://github.com/user-attachments/assets/93f0e3c6-6adb-47ca-bbd9-9da6b1893067)

  ### ▶️ Screencasts

  ### Deploy [Deployment](https://www.youtube.com/watch?v=Wg4OpnnYn_g)
- ### Testes [Testes automatizados](https://youtu.be/FJOwukHw6Ug)
- ### Workflows/Actions (CI/CD) [Deploy e Build](https://www.youtube.com/watch?v=fdReA9gsHiE)

</details>


## 👥 Equipe – Grupo 02 (FDS - 2025.2)

| Nome | E-mail | Função |
|------|---------|--------|
| Arthur Reis Gomes de Mello Queiroz | argmq@cesar.school | Frontend |
| Bernardo Guimarães Nunes Palhares | bgnp@cesar.school | Backend |
| Cauã Henrique Cardoso Carneiro Parente | chccp@cesar.school | Backend |
| João Arthur Gomes Duarte | jagb@cesar.school | Frontend |
| Luiza Barbosa Almeida da Silva | lbas2@cesar.school | Backend |
| Maria Eduarda Souza de Oliveira | meso@cesar.school | Frontend |

---

### 💬 Observação Final
O projeto **SushiEmCasa** integra **design**, **usabilidade** e **engenharia de software**, com foco em:  
- 💡 Experiência do usuário  
- 🧩 Colaboração em equipe  
- ⚙️ Boas práticas de desenvolvimento ágil  

---