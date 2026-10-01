# Proposta de projeto em uma página

Esta é a Ficha 8 do Caderno de Dinâmicas da Aula 7.

| Campo | Conteúdo |
|---|---|
| **Nome provisório** | MeshTracker Central |
| **Aluno ou integrantes** | Rafael Alves de Sousa Costa (RA 22304563) |
| **Usuário principal** | Organizador de operações da Federação de Airsoft do Distrito Federal e entorno: a pessoa que monta a operação, inscreve os jogadores e acompanha o que acontece em campo. A federação é o público do operational-command, sistema que eu desenvolvo. |
| **Problema observado** | Percebi, ao desenhar o operational-command, que o operador teria de se cadastrar de novo a cada operação, mesmo sendo a mesma pessoa. Além disso, pelo desenho do firmware do MeshTracker, cada dispositivo só enxerga os vizinhos que alcança e esquece quem some por 2 minutos, então ninguém tem uma visão geral de onde cada operador está. Ainda não confirmei isso com a federação: é o que enxergo olhando para o meu próprio projeto. |
| **Como o problema é enfrentado atualmente** | Não confirmei com a federação. Imagino que o cadastro seja refeito a cada operação e que o acompanhamento em campo seja feito por rádio de voz. |
| **Consequência do problema** | O organizador perde tempo recadastrando gente que já conhece, pode demorar a perceber que um operador ficou sem contato, as ordens ficam sem confirmação e as decisões são tomadas sem dados. |
| **Proposta de solução** | Uma aplicação web em que o organizador mantém o perfil permanente de cada operador, inscreve o operador em cada operação com time e classe e o acompanha ao vivo no mapa, e depois emite ordens com confirmação. Assim ninguém é recadastrado e o organizador tem a visão geral da operação sem depender de internet. Os dados vêm da rede LoRa do MeshTracker, por um gateway e pelo protocolo MQTT, e a posição se atualiza no ritmo do sinal do dispositivo, a cada 30 segundos por padrão. |
| **Escopo mínimo** | Contrato de mensagens MQTT com um simulador de gateway, cadastro permanente do operador e inscrição por operação, recebimento só dos dispositivos inscritos com o estado de cada operador, e mapa ao vivo. |
| **Fluxo da Iteração 1** | O organizador inscreve um operador já cadastrado em uma operação, escolhendo time, classe e dispositivo. O simulador publica os sinais dos inscritos, o sistema ignora dispositivos não inscritos e sinais repetidos, calcula o estado de cada operador, grava no banco e atualiza o mapa na hora, com a cor do time. |
| **Funcionalidades fora do escopo inicial** | Ordens com confirmação, objetivos com alerta de chegada e trilha de posição ficam para a Iteração 2. Gateway real com autenticação das ordens e replay da operação ficam como desejáveis. O desenho da topologia da malha fica de fora. |
| **Tecnologias inicialmente consideradas** | Vue 3 com Vite, Node.js com Express, MongoDB, Mosquitto (MQTT), WebSocket e Docker Compose, a mesma stack do operational-command. Para o mapa, Leaflet ou MapLibre; ainda não decidi. O firmware do MeshTracker (ESP32-S3, ESP-IDF e rádio SX1278) só entra a partir da Iteração 3. |
| **Risco principal** | O firmware do MeshTracker ainda está incompleto: GPS, mesh e interface são esqueletos. Por isso começo pelo contrato de mensagens e por um simulador de gateway, e a primeira iteração não depende do hardware. |
| **Como a solução será validada** | Com testes automatizados das regras de duplicidade e de estado e com uma demonstração de 5 operadores simulados ao vivo. Minha medida de sucesso é o organizador reinscrever o mesmo operador em uma segunda operação sem cadastrá-lo de novo e dizer, sem explicação, qual operador está sem sinal e há quanto tempo. A conversa com a federação ainda não aconteceu e é o que falta para validar de verdade. |
| **Referência bibliográfica inicial** | CEUBOOK. Engenharia da Computação — Desenvolvimento de Sistemas. Brasília: CEUB, 2024. Ainda não li o capítulo sobre modelo de dados. |
| **Link do repositório** | https://github.com/izrafilcst/Desenvolvimento-Sistemas |
