# ADR-003: Sinais do gateway por HTTP no lugar de MQTT

**Status:** aceito · **Data:** 01/11/2026 · **Autor:** Rafael Alves de Sousa Costa

## Contexto

Na proposta da Aula 7, os dados vinham da rede LoRa do MeshTracker por um gateway e pelo protocolo MQTT, com um broker Mosquitto. Depois do recorte da revisão (ADR-002), não há hardware nem gateway real no MVP: os sinais vêm de um simulador que escrevo no Incremento 2, em 24/11, trabalhando sozinho.

Mesmo sem gateway real, o contrato entre o gateway e o sistema precisa ser decidido agora, porque o simulador, as regras que descartam sinais de quem não está inscrito (R7) e que evitam sinais repetidos (R8) e o mapa dependem dele. A pergunta é qual é o menor contrato que leva o sinal de um dispositivo até a regra e ao mapa.

## Decisão

Adoto HTTP com JSON: o gateway envia cada sinal para `POST /api/v1/sinais`, com o corpo `{dispositivo, pacote, lat, lon, bateria}`, em que `pacote` é o número crescente de cada dispositivo. O sistema responde assim:

| Situação | Resposta |
|---|---|
| Formato inválido | 400 |
| Dispositivo sem inscrição na operação em curso, descartado e contado (R7) | 202 `{"status":"descartado"}` |
| Sinal repetido, com o mesmo dispositivo e o mesmo pacote na operação (R8) | 200 `{"status":"duplicado"}` |
| Sinal aceito | 201 `{"status":"gravado"}` |

O token do gateway chega no Incremento 3 (R11): a partir dele o endpoint exige o token, e sem token a resposta é 401. O simulador e o futuro gateway falam esse mesmo contrato.

## Alternativas que descartei

- **MQTT com Mosquitto.** Descartei por ora porque acrescentava um broker, TLS e permissões por tópico sem mudar o que o organizador vê. Fica registrada como o caminho para quando houver gateway real.

## Justificativa

Com base em SOMMERVILLE (2018, seção 2.3.2), decidi que o gateway envia os sinais por HTTP, em JSON, para POST /api/v1/sinais, porque é o menor contrato que leva o sinal até a regra e ao mapa sem infraestrutura extra. A alternativa MQTT com Mosquitto foi descartada por ora porque acrescentava um broker, TLS e permissões por tópico sem mudar o que o organizador vê; ela volta a ser considerada quando houver gateway real.

O contrato do gateway é uma interface, e o guia de ADR da AWS (KUNCE; GOBY, 2022, p. 3) inclui as interfaces (APIs e contratos publicados) entre os aspectos do software que pedem um ADR. Se eu voltar ao MQTT quando houver gateway real, o caminho pelo guia é um novo ADR, que passa este para o estado Substituído (p. 7), e não uma edição deste texto.

## Consequências

O que ganho: o simulador e o futuro gateway falam o mesmo contrato; não preciso montar broker, TLS nem permissões por tópico; e qualquer cliente HTTP, como o `curl`, consegue enviar um sinal para testar.

O que pago: perde-se o QoS do MQTT, e a deduplicação passa a ser regra da aplicação (R8); e, até o Incremento 3, o endpoint aceita sinais sem token, o que só é aceitável porque tudo roda no meu notebook com o simulador.

## Referências

- SOMMERVILLE, Ian. *Engenharia de software*. Tradução: Luiz Cláudio Queiroz. Revisão técnica: Fábio Levy Siqueira. 10. ed. São Paulo: Pearson Education do Brasil, 2018.
- KUNCE, Darius; GOBY, Dominik. *Usar registros de decisão de arquitetura para agilizar a tomada de decisões técnicas para um projeto de desenvolvimento de software*. [S. l.]: Amazon Web Services, mar. 2022. (AWS Prescriptive Guidance). Disponível em: https://docs.aws.amazon.com/pt_br/prescriptive-guidance/latest/architectural-decision-records/. Acesso em: 1 nov. 2026.
