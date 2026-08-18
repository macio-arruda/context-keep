# O método

## O problema

Arquivo de contexto é todo arquivo que o modelo lê a cada chamada: `CLAUDE.md`, `AGENTS.md`, um arquivo de estado, um changelog que você mantém no repo. Começa pequeno e útil. Meses depois está grande, e a maior parte é conteúdo velho.

Isso custa duas vezes.

Primeiro, token. O arquivo inteiro entra no contexto a cada chamada, então você paga input por conteúdo velho toda vez. Um changelog que chegou a 140 KB dá uns 35 mil tokens relidos a cada commit, o que a um preço de US$ 5 / 1M de input sai a uns 17 centavos por commit pra reler algo que ninguém lê.

Segundo, atenção. Quanto maior o contexto, pior o modelo usa o meio dele. O estudo de Stanford que nomeou isso ("Lost in the Middle", Liu et al., 2023) achou a precisão mais alta no começo e no fim do contexto e mais baixa no meio. A medição da Chroma depois ("context rot") mostrou a qualidade caindo conforme o input cresce, nos modelos atuais. Arquivo de contexto inchado é contexto longo, então piora a resposta enquanto sobe a conta.

## Por que os arquivos apodrecem

Em sistemas você não guarda dado frio no caminho quente. A RAM segura o working set; o arquivo morto fica no disco. Arquivo de contexto quebra essa regra. Ele guarda três coisas de ritmos opostos no mesmo lugar:

| Camada | O que guarda | Leitura | Escrita |
|---|---|---|---|
| **Estado** | o que é verdade agora, os itens abertos | toda sessão | frequente |
| **Racional** | por que as decisões foram tomadas | sob demanda | raro |
| **Trilha** | o que mudou e quando | quase nunca | a cada mudança |

O estado é pequeno e quente. A trilha é append-only e cresce sem limite. O racional é a referência que você abre quando precisa do "porquê". Junte os três num arquivo e o que você carrega a cada chamada leva o peso dos três. Só a trilha já garante que ele cresce pra sempre.

## A correção, em dois movimentos

**Separar por ciclo de vida.** Cada camada num arquivo. `STATE.md` guarda o que é verdade agora e fica pequeno. `DECISIONS.md` guarda o racional, lido sob demanda. `CHANGELOG.md` guarda a trilha, append-only e enxuto, rolado pra um arquivo quando passa do teto. O estado aponta para os outros dois; não repete o conteúdo deles. O racional vive uma vez, e todo o resto linka.

**Travar o tamanho por mecanismo, não por regra.** A regra "manter enxuto" quase sempre já está escrita, e é ignorada. Convenção decai porque nada a força. Uma trava no pre-commit força: avisa perto de um teto brando e barra no teto duro. A escapatória (`--no-verify`) tem que ser rara o bastante pra ser um sinal quando acontece.

## O fluxo

1. **Auditar.** Rode o `context_audit.py` pra ver tamanho, custo estimado por leitura e quais arquivos misturam ciclos de vida. Meça antes de cortar.
2. **Separar.** Pra cada arquivo que mistura camadas, mova o racional pro `DECISIONS.md`, o histórico pro `CHANGELOG.md`, e deixe só o estado no caminho quente.
3. **Travar.** Instale a trava no pre-commit nos arquivos que carregam a cada chamada. Role a trilha pra um arquivo quando ela passar do teto.

## Procedência

Os termos e as medições têm fonte, listada em [`../references.md`](../references.md). O Context Keep é um jeito de aplicar isso aos arquivos que você mantém à mão.
