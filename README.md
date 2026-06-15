# Sistema_de_Controle_Pessoal_de_Estudos

O presente trabalho tem como objetivo aplicar os conhecimentos práticos e teóricos adquiridos na disciplina de Algoritmos e Programação, do 1º período do Curso de Bacharelado em Inteligência Artificial da Faculdade Estadual Piauí Instituto de Tecnologia - PIT. A finalidade central consiste em criar um sistema em linguagem Python que gerencia algo, estruturado em torno do CRUD (Create, Read, Update, Delete) e utilizando Dicionários e manipulação de arquivos locais.

No caso em tela, trata-se de um Sistema de Controle Pessoal de Estudos e Resolução de Questões. A escolha deve-se à necessidade de organização, disciplina e autorregulação para estudos de alto rendimento, em especial, para aqueles que almejam concursos públicos, vestibulares concorridos e até para estudantes universitários, em especial da área da tecnologia. Desse modo, o sistema criado permite que o usuário identifique ativamente seu esforço, evidencia o tempo investido em cada discplina e, o mais importante, monitora sua taxa de acertos em exercícios práticos de modo a identificar por meio dos dados quais matérias domina, bem como aquelas que precisam de mais atenção, otimizando seu tempo e melhorando seu desempenho.

O sistema utiliza uma Lista de Dicionários e a biblioteca nativa JSON. Foi criado funções que abrem o arquivo no modo 'r' (leitura) ao iniciar o programa, convertendo o texto em dicionários (via json.load). Ao final de qualquer alteração, o arquivo é reescrito no modo 'w' (escrita) salvando a lista atualizada (via json.dump).

Em relação ao C.R.U.D:

C (Create): Função criar_sessao(). Coleta dados através de funções de validação que impedem strings vazias ou números absurdos. Gera um ID automaticamente e calcula a taxa de acerto antes de fazer o .append() na lista.
R (Read): Função listar_sessoes(). Utiliza um laço for para percorrer a lista de dicionários e exibe o histórico formatado. Trata listas vazias com o operador lógico not.
U (Update): Função atualizar_sessao(). Busca uma sessão pelo ID. Permite que o usuário pressione apenas ENTER para manter o dado antigo intacto (usando lógicas de OR e checagem de strings vazias).
D (Delete): Função excluir_sessao(). Localiza o índice do dicionário usando enumerate e, após confirmação de segurança, remove o registro da memória utilizando o método .pop().
Dashboard Visual: Função gerar_dashboard(). Agrupa os dados processados utilizando lógica de laços for e dicionários auxiliares, enviando as médias matemáticas para a biblioteca matplotlib desenhar os gráficos.

Portanto, conta com salvamento automático de dados no disco rígido através de arquivos JSON, garantindo que o histórico não seja perdido ao fechar o programa. Indo além, foi implementado um Painel Analítico (Dashboard) utilizando a biblioteca matplotlib, que traduz os dados armazenados na lista de dicionários em gráficos visuais dinâmicos, bem como a taxa média de acertos e o tempo total dedicado a cada disciplina. Assim transforma o estudo através de um processo guiado por dados.

Durante o desenvolvimento do código, as dificuldades encontradas foram:

* O Bug da Divisão por Zero: Na regra de negócio do CREATE, percebemos que se o usuário apenas lesse um PDF e não fizesse questões (0 questões), o cálculo da taxa de acerto (acertos / questoes) causaria um erro fatal (ZeroDivisionError). Solucionamos adicionando um if de proteção na função matemática.

* Atualizar dados sem apagar o resto (Update): Foi desafiador criar uma lógica onde o usuário pudesse pular a edição de um campo. Resolvemos isso criando a função ler_inteiro_opcional, que devolve o valor antigo caso a entrada do input seja vazia (False).

* Agrupamento de Dados para o Gráfico: Como não utilizamos a biblioteca pandas, tivemos a dificuldade de agrupar as taxas de acerto por disciplina. Resolvemos isso criando um dicionário vazio que recebia as disciplinas como chaves e listas de notas como valores, fazendo as médias posteriormente através de laços de repetição.

Em relação ao uso de Inteligência Artificial, utilizamos em dois momentos:

Especificamente para a construção da interface gráfica. Toda parte do código para uso da Biblioteca matplotlib foi feita com ajuda do Claude IA, versão Sonnet 4.6;

Também utilizamos no final do código a IA do Google Gemini Pro para fazer uma análise estática do código em busca de bugs ocultos e erros lógicos. Foram identificados e corrigios 6 bugs, segue abaixo a resposta da IA:

"O código está muito bem estruturado e a lógica está quase perfeita para o 1º período.

No entanto, há 6 bugs pontuais que causariam a "quebra" do programa (erros fatais durante a execução) ou confusão para o usuário.

Fiz apenas as correções cirúrgicas e estritamente necessárias, preservando 100% da sua estrutura. Abaixo listo os 6 bugs encontrados e as correções aplicadas:

Bug Crítico: Função aninhada (salvar_dados dentro de carregar_dados) O Erro: A função def salvar_dados(sessoes): estava indentada (espaçada) para a direita, dentro da função carregar_dados(). Isso transforma ela numa "função local", invisível para o resto do programa. Se você tentasse salvar qualquer coisa (CREATE, UPDATE, DELETE), o Python diria que salvar_dados não existe. Correção: Removi o recuo (indentação) da palavra def salvar_dados e do seu bloco para alinhá-la no início da margem, tornando-a uma função global.

Bug Lógico: Retorno inalcançável (return []) O Erro: O comando return [] estava dentro do bloco if os.path.exists(). Se fosse a primeira vez que você rodasse o programa e o arquivo não existisse, a função não devolveria nada, causando um erro depois. Correção: Puxei o return [] um nível de recuo para trás, alinhando-o com o if.

Bug Físico (NameError): Variável não declarada O Erro: Na função de matemática, você definiu o parâmetro como acerto (singular), mas na conta você escreveu acertos (plural): return round((acertos / questoes) * 100, 2). O programa "explodiria" ao calcular a taxa. Correção: Alterei o nome do parâmetro para acertos na linha do def: def calcular_taxa(acertos, questoes):.

Bug de Lógica: Opção "Sair" do Menu O Erro: No seu cabeçalho visual (exibir_menu), a opção para sair é a "6. Sair". No entanto, no final do código, lá no match opcao:, quem encerra o programa é o case "0":. Se o usuário digitasse 6, cairia em "Opção inválida". Correção: Alterei a leitura do match de case "0": para case "6": para ficar sincronizado com o visual do menu.

Bug de Lógica: Erro de digitação da mensagem inválida O Erro: Como consequência do bug 4, a mensagem de erro do case _: estava dizendo para escolher entre "0 e 5". Correção: Mudei a mensagem para: "[ERRO] Opção inválida. Você deve escolher um número inteiro entre 1 e 6."

Erro Ortográfico (UX) O Erro: Na função de atualizar a sessão, a mensagem estava escrita: print("Pressionae a tecla ENTER..."). Correção: Ajustado para "Pressione a tecla ENTER..."."

Observação: não esqueça de instalar a biblioteca gráfica executando o comando no terminal: pip install matplotlib

Desde já agradecemos o interesse.

Atenciosamente,
Breno Igo B. P. de Araújo, Luiz Henrique Santos Silva e Raimundo Clécio Dantas Muniz Filho - Alunos do 1º período do Bacharelado em Inteligência Artificial do Piauí Instituto de Tecnologia
