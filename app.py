# =============================================================================
# app.py — Diário de Estudos: CRUD Streamlit
# Faculdade Estadual Piauí — Instituto de Tecnologia (PIT)
# Disciplina: Algoritmos e Programação
#
# Autores: Breno Igo, Luiz Henrique, Raimundo Clecio
# Conversão terminal → web: Claude Sonnet 4.6
# =============================================================================

import streamlit as st
import json
import os
from datetime import date
import matplotlib.pyplot as plt

# ─── 1. CONFIGURAÇÃO DA PÁGINA ────────────────────────────────────────────────
# OBRIGATÓRIO: deve ser a PRIMEIRA chamada Streamlit do arquivo.
# Equivalente ao cabeçalho impresso pelo print() original no início do main().
st.set_page_config(
    page_title="Diário de Estudos — PIT",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── 2. CONSTANTES (idênticas ao código original — não alteradas) ─────────────
ARQUIVO_JSON = "sessoes.json"   # caminho relativo simples → funciona no Cloud
META_ACERTO  = 70.0
CORES = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#44BBA4", "#E94F37"]


# ─── 3. LÓGICA DE NEGÓCIO ─────────────────────────────────────────────────────
# Nenhuma função desta seção foi alterada em relação ao código original.
# A lógica de cálculo e persistência permanece exatamente a mesma.

def carregar_dados():
    """Lê o JSON do disco. Retorna lista vazia se arquivo inexistente/corrompido."""
    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
                if isinstance(dados, list):
                    return dados
                # Aviso vai para o log do servidor, não para a UI
                print("[AVISO] Arquivo JSON inválido. Iniciando lista vazia.")
                return []
            except json.JSONDecodeError:
                print("[AVISO] Arquivo corrompido. Iniciando lista vazia.")
    return []


def salvar_dados(sessoes):
    """Persiste a lista de sessões no arquivo JSON (caminho relativo)."""
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(sessoes, f, ensure_ascii=False, indent=2)


def calcular_taxa(acertos, questoes):
    """Retorna percentual de acertos (0.0 se nenhuma questão respondida)."""
    if questoes == 0:
        return 0.0
    return round((acertos / questoes) * 100, 2)


def proximo_id(sessoes):
    """Gera o próximo ID sequencial com base no maior ID existente."""
    if not sessoes:
        return 1
    return max(s["id"] for s in sessoes) + 1


def buscar_sessao(sessoes, id_alvo):
    """Retorna o índice da sessão com id_alvo, ou -1 se não encontrada."""
    for i, s in enumerate(sessoes):
        if s["id"] == id_alvo:
            return i
    return -1


# ─── 4. INICIALIZAÇÃO DO SESSION STATE ────────────────────────────────────────
# Streamlit reroda o script inteiro a cada interação do usuário (clique,
# digitação, etc.). O st.session_state persiste valores ENTRE esses reruns,
# funcionando como a memória RAM que a lista `sessoes` ocupava dentro do
# loop while True do main() original.

if "sessoes" not in st.session_state:
    # Carrega do disco apenas na primeira execução da sessão do browser.
    st.session_state["sessoes"] = carregar_dados()

if "feedback" not in st.session_state:
    # Canal de mensagens entre reruns:
    # operações CRUD gravam aqui → show_feedback() exibe na próxima renderização.
    st.session_state["feedback"] = None


# ─── 5. HELPER: exibir e limpar feedback ──────────────────────────────────────
def show_feedback():
    """
    Exibe a mensagem armazenada em session_state["feedback"] e a apaga.

    Por que esse padrão existe?
    st.rerun() interrompe a execução imediatamente. Se chamássemos
    st.success("✅ Sessão salva!") ANTES de st.rerun(), a mensagem nunca
    seria renderizada — o rerun aconteceria primeiro. Solução: gravar a
    mensagem no session_state, chamar st.rerun(), e exibir na próxima
    passagem do script via esta função.
    """
    fb = st.session_state.get("feedback")
    if not fb:
        return
    tipo, msg = fb
    if tipo == "success":
        st.success(msg)
    elif tipo == "error":
        st.error(msg)
    elif tipo == "info":
        st.info(msg)
    elif tipo == "warning":
        st.warning(msg)
    # Limpa imediatamente para não repetir em reruns futuros
    st.session_state["feedback"] = None


# ─── 6. SIDEBAR — NAVEGAÇÃO PRINCIPAL ─────────────────────────────────────────
# Substitui a função exibir_menu() + input("Escolha uma opção: ") do terminal.
# st.radio() retorna a string da opção selecionada; usamos if/elif para
# decidir qual seção de página renderizar.

with st.sidebar:
    st.title("📚 Diário de Estudos")
    st.caption("PIT — Algoritmos e Programação")
    st.divider()

    pagina = st.radio(
        "Navegação",
        options=[
            "📝 Nova Sessão",
            "📋 Histórico",
            "✏️ Editar Sessão",
            "🗑️ Excluir Sessão",
            "📊 Dashboard",
        ],
        key="nav_radio",
    )

    st.divider()
    # Métrica atualiza automaticamente após cada CRUD porque lê do session_state
    st.metric("Sessões registradas", len(st.session_state["sessoes"]))


# =============================================================================
# PÁGINA 1 — NOVA SESSÃO  [CREATE]
# Substitui a função criar_sessao() do original.
# =============================================================================
if pagina == "📝 Nova Sessão":
    st.title("📝 Nova Sessão de Estudo")
    st.caption("Preencha os campos e clique em **Registrar Sessão**.")

    # Exibe confirmação/erro registrado pelo submit anterior (via session_state)
    show_feedback()

    # st.form() agrupa todos os widgets em um único bloco de envio.
    # Sem ele, qualquer digitação dispararia um rerun imediato (comportamento
    # indesejado). clear_on_submit=True limpa os campos após o envio.
    with st.form("form_nova_sessao", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            # st.text_input substitui ler_texto("Disciplina")
            disciplina = st.text_input(
                "Disciplina *",
                placeholder="ex: Matemática Discreta",
                key="create_disciplina",
            )
            # st.text_input substitui ler_texto("Assunto")
            assunto = st.text_input(
                "Assunto *",
                placeholder="ex: Teoria dos Grafos",
                key="create_assunto",
            )

        with col2:
            # st.number_input substitui ler_inteiro("Tempo estudado")
            tempo = st.number_input(
                "Tempo estudado (min) *",
                min_value=1, max_value=600, value=60, step=5,
                key="create_tempo",
            )
            # st.number_input substitui ler_inteiro("Total de questões")
            questoes = st.number_input(
                "Total de questões respondidas",
                min_value=0, max_value=1000, value=0, step=1,
                key="create_questoes",
            )
            # st.number_input substitui ler_inteiro(f"Total de acertos (0 a {questoes})")
            acertos = st.number_input(
                "Total de acertos",
                min_value=0, max_value=1000, value=0, step=1,
                key="create_acertos",
            )

        # st.form_submit_button substitui o input() implícito do fluxo original
        submitted = st.form_submit_button(
            "✅ Registrar Sessão", use_container_width=True
        )

    if submitted:
        # ── Validações (equivalentes às do ler_texto / ler_inteiro originais) ──
        if not disciplina.strip():
            st.session_state["feedback"] = ("error", "❌ Disciplina é obrigatória.")
        elif not assunto.strip():
            st.session_state["feedback"] = ("error", "❌ Assunto é obrigatório.")
        elif int(acertos) > int(questoes):
            st.session_state["feedback"] = (
                "error",
                f"❌ Acertos ({int(acertos)}) não pode ser maior que "
                f"o total de questões ({int(questoes)}).",
            )
        else:
            # ── Lógica de criação idêntica ao original ──
            taxa = calcular_taxa(int(acertos), int(questoes))
            nova = {
                "id":                proximo_id(st.session_state["sessoes"]),
                "data":              str(date.today()),
                "disciplina":        disciplina.strip(),
                "assunto":           assunto.strip(),
                "tempo_liquido_min": int(tempo),
                "total_questoes":    int(questoes),
                "total_acertos":     int(acertos),
                "taxa_acerto":       taxa,
            }
            st.session_state["sessoes"].append(nova)
            salvar_dados(st.session_state["sessoes"])
            st.session_state["feedback"] = (
                "success",
                f"✅ Sessão #{nova['id']} registrada com sucesso! "
                f"Taxa de acerto: {taxa}%",
            )

        # st.rerun() força o Streamlit a rerrodar o script do início,
        # garantindo que a sidebar e o feedback sejam atualizados corretamente.
        st.rerun()


# =============================================================================
# PÁGINA 2 — HISTÓRICO  [READ]
# Substitui a função listar_sessoes() do original.
# =============================================================================
elif pagina == "📋 Histórico":
    st.title("📋 Histórico de Sessões")

    show_feedback()

    sessoes = st.session_state["sessoes"]

    if not sessoes:
        # st.info substitui o print() de "Nenhuma sessão registrada"
        st.info(
            "📭 Nenhuma sessão registrada ainda. "
            "Use **📝 Nova Sessão** para começar."
        )
    else:
        st.info(f"Total: **{len(sessoes)}** sessão(ões) registrada(s).")

        # Lista de dicionários → st.dataframe (sem necessidade de pandas!).
        # Os nomes das CHAVES do JSON original são preservados internamente;
        # apenas os cabeçalhos de exibição foram adaptados para o usuário.
        dados_display = [
            {
                "ID":          s["id"],
                "Data":        s["data"],
                "Disciplina":  s["disciplina"],
                "Assunto":     s["assunto"],
                "Tempo (min)": s["tempo_liquido_min"],
                "Questões":    s["total_questoes"],
                "Acertos":     s["total_acertos"],
                "Taxa (%)":    s["taxa_acerto"],
            }
            for s in sessoes
        ]

        # use_container_width → tabela ocupa toda a largura disponível
        # hide_index=True → oculta o índice 0,1,2,... (já temos coluna ID)
        st.dataframe(dados_display, use_container_width=True, hide_index=True)


# =============================================================================
# PÁGINA 3 — EDITAR SESSÃO  [UPDATE]
# Substitui a função atualizar_sessao() do original.
# =============================================================================
elif pagina == "✏️ Editar Sessão":
    st.title("✏️ Editar Sessão")

    show_feedback()

    sessoes = st.session_state["sessoes"]

    if not sessoes:
        st.info("📭 Nenhuma sessão registrada ainda.")
    else:
        # st.selectbox substitui o ler_inteiro("ID da sessão a atualizar:").
        # format_func exibe um rótulo legível em vez do ID bruto.
        # next(...) é um gerador que encontra o valor da disciplina/assunto/data
        # para o ID x sem precisar de pandas ou loops explícitos.
        id_selecionado = st.selectbox(
            "Selecione a sessão para editar:",
            options=[s["id"] for s in sessoes],
            format_func=lambda x: (
                f"#{x} — "
                f"{next(s['disciplina'] for s in sessoes if s['id'] == x)}"
                f" | {next(s['assunto'] for s in sessoes if s['id'] == x)}"
                f" ({next(s['data'] for s in sessoes if s['id'] == x)})"
            ),
            key="edit_id_selector",
        )

        indice       = buscar_sessao(sessoes, id_selecionado)
        sessao_atual = sessoes[indice]

        st.divider()

        # ── Chaves dinâmicas: o segredo do pré-preenchimento correto ──────────
        # Problema: se o usuário trocar de sessão no selectbox, os widgets do
        # form manteriam os valores da sessão anterior (Streamlit cacheia por key).
        # Solução: incluir o ID na chave (f"edit_disc_{id_selecionado}").
        # Quando o ID muda, a key muda → Streamlit trata como widget novo →
        # usa o parâmetro value= com os dados da nova sessão. Elegante!
        with st.form(f"form_editar_{id_selecionado}"):
            st.subheader(
                f"Sessão #{sessao_atual['id']} — registrada em {sessao_atual['data']}"
            )

            col1, col2 = st.columns(2)

            with col1:
                nova_disc = st.text_input(
                    "Disciplina *",
                    value=sessao_atual["disciplina"],
                    key=f"edit_disc_{id_selecionado}",
                )
                novo_assunto = st.text_input(
                    "Assunto *",
                    value=sessao_atual["assunto"],
                    key=f"edit_assunto_{id_selecionado}",
                )

            with col2:
                novo_tempo = st.number_input(
                    "Tempo (min) *",
                    value=sessao_atual["tempo_liquido_min"],
                    min_value=1, max_value=600, step=5,
                    key=f"edit_tempo_{id_selecionado}",
                )
                novo_questoes = st.number_input(
                    "Total de questões",
                    value=sessao_atual["total_questoes"],
                    min_value=0, max_value=1000, step=1,
                    key=f"edit_questoes_{id_selecionado}",
                )
                novo_acertos = st.number_input(
                    "Total de acertos",
                    value=sessao_atual["total_acertos"],
                    min_value=0, max_value=1000, step=1,
                    key=f"edit_acertos_{id_selecionado}",
                )

            submitted_edit = st.form_submit_button(
                "💾 Salvar Alterações", use_container_width=True
            )

        if submitted_edit:
            if not nova_disc.strip():
                st.session_state["feedback"] = ("error", "❌ Disciplina é obrigatória.")
            elif not novo_assunto.strip():
                st.session_state["feedback"] = ("error", "❌ Assunto é obrigatório.")
            elif int(novo_acertos) > int(novo_questoes):
                st.session_state["feedback"] = (
                    "error",
                    f"❌ Acertos ({int(novo_acertos)}) > "
                    f"questões ({int(novo_questoes)}).",
                )
            else:
                # ── Lógica de atualização idêntica ao original ──
                nova_taxa = calcular_taxa(int(novo_acertos), int(novo_questoes))
                st.session_state["sessoes"][indice] = {
                    "id":                sessao_atual["id"],
                    "data":              sessao_atual["data"],
                    "disciplina":        nova_disc.strip(),
                    "assunto":           novo_assunto.strip(),
                    "tempo_liquido_min": int(novo_tempo),
                    "total_questoes":    int(novo_questoes),
                    "total_acertos":     int(novo_acertos),
                    "taxa_acerto":       nova_taxa,
                }
                salvar_dados(st.session_state["sessoes"])
                st.session_state["feedback"] = (
                    "success",
                    f"✅ Sessão #{sessao_atual['id']} atualizada com sucesso! "
                    f"Nova taxa de acerto: {nova_taxa}%",
                )
            st.rerun()


# =============================================================================
# PÁGINA 4 — EXCLUIR SESSÃO  [DELETE]
# Substitui a função excluir_sessao() do original.
# =============================================================================
elif pagina == "🗑️ Excluir Sessão":
    st.title("🗑️ Excluir Sessão")

    show_feedback()

    sessoes = st.session_state["sessoes"]

    if not sessoes:
        st.info("📭 Nenhuma sessão registrada ainda.")
    else:
        id_selecionado = st.selectbox(
            "Selecione a sessão para excluir:",
            options=[s["id"] for s in sessoes],
            format_func=lambda x: (
                f"#{x} — "
                f"{next(s['disciplina'] for s in sessoes if s['id'] == x)}"
                f" | {next(s['assunto'] for s in sessoes if s['id'] == x)}"
                f" ({next(s['data'] for s in sessoes if s['id'] == x)})"
            ),
            key="delete_id_selector",
        )

        indice       = buscar_sessao(sessoes, id_selecionado)
        sessao_atual = sessoes[indice]

        # Exibe os dados da sessão selecionada antes de excluir
        # (equivalente ao exibir_sessao() do original)
        st.divider()
        st.subheader(f"Detalhes da Sessão #{sessao_atual['id']}")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"📅 **Data:** {sessao_atual['data']}")
            st.write(f"📚 **Disciplina:** {sessao_atual['disciplina']}")
            st.write(f"🔖 **Assunto:** {sessao_atual['assunto']}")
        with col2:
            st.write(f"⏱️ **Tempo:** {sessao_atual['tempo_liquido_min']} min")
            st.write(
                f"🎯 **Desempenho:** "
                f"{sessao_atual['total_acertos']}/{sessao_atual['total_questoes']}"
            )
            st.write(f"📊 **Taxa de Acerto:** {sessao_atual['taxa_acerto']}%")

        st.divider()
        st.warning("⚠️ Esta operação é **irreversível**. A sessão será permanentemente removida.")

        # st.checkbox substitui o input("Tem certeza? S/N").
        # Mantém o botão desabilitado até o usuário confirmar explicitamente.
        confirmacao = st.checkbox(
            "✅ Confirmo que desejo excluir esta sessão permanentemente",
            key="delete_confirm",
        )

        # disabled=not confirmacao → botão só fica clicável após o checkbox
        if st.button(
            "🗑️ Excluir Sessão",
            key="delete_btn",
            disabled=not confirmacao,
            type="primary",
        ):
            id_excluido = sessao_atual["id"]

            # List comprehension por ID substitui sessoes.pop(indice).
            # Em ambiente web, múltiplos rerenders podem desatualizar o índice;
            # filtrar por ID é sempre seguro e robusto.
            st.session_state["sessoes"] = [
                s for s in st.session_state["sessoes"]
                if s["id"] != id_selecionado
            ]
            salvar_dados(st.session_state["sessoes"])

            # Remove o estado do selectbox para evitar referência a ID inexistente
            # após o rerun (pop com default=None ignora se a chave não existir)
            st.session_state.pop("delete_id_selector", None)
            st.session_state.pop("delete_confirm", None)

            st.session_state["feedback"] = (
                "success", f"✅ Sessão #{id_excluido} excluída com sucesso!"
            )
            st.rerun()


# =============================================================================
# PÁGINA 5 — DASHBOARD  [READ + Matplotlib]
# Substitui a função gerar_dashboard() do original.
# =============================================================================
elif pagina == "📊 Dashboard":
    st.title("📊 Painel de Desempenho Analítico")

    show_feedback()

    sessoes = st.session_state["sessoes"]

    if not sessoes:
        st.info("📭 Sem dados ainda. Registre sessões primeiro.")
    else:
        # ── Métricas rápidas no topo (bônus: não existia no terminal) ─────
        total_tempo    = sum(s["tempo_liquido_min"] for s in sessoes)
        total_questoes = sum(s["total_questoes"]    for s in sessoes)
        total_acertos  = sum(s["total_acertos"]     for s in sessoes)
        taxa_geral     = calcular_taxa(total_acertos, total_questoes)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📋 Sessões",           len(sessoes))
        c2.metric("⏱️ Tempo Total (min)",  total_tempo)
        c3.metric("🎯 Taxa Geral",         f"{taxa_geral}%")
        c4.metric("📚 Questões",           f"{total_acertos}/{total_questoes}")

        st.divider()

        # ── Agrupamento por disciplina (lógica original intocada) ─────────
        taxas_por_disc = {}
        tempo_por_disc = {}

        for sessao in sessoes:
            disc = sessao["disciplina"]
            if disc not in taxas_por_disc:
                taxas_por_disc[disc] = []
                tempo_por_disc[disc] = 0
            taxas_por_disc[disc].append(sessao["taxa_acerto"])
            tempo_por_disc[disc] += sessao["tempo_liquido_min"]

        disciplinas   = sorted(taxas_por_disc.keys())
        medias        = [round(sum(taxas_por_disc[d]) / len(taxas_por_disc[d]), 2)
                         for d in disciplinas]
        qtd_sessoes   = [len(taxas_por_disc[d])   for d in disciplinas]
        tempos_totais = [tempo_por_disc[d]         for d in disciplinas]
        cores         = [CORES[i % len(CORES)]     for i in range(len(disciplinas))]

        # ── Figura Matplotlib (código de criação idêntico ao original) ────
        fig, (ax1, ax2) = plt.subplots(
            1, 2,
            figsize=(14, 6),
            gridspec_kw={"width_ratios": [3, 1]},
        )
        fig.patch.set_facecolor("#F4F4F4")

        # Gráfico 1 — barras verticais: taxa média por disciplina
        ax1.set_facecolor("#FAFAFA")
        barras = ax1.bar(
            disciplinas, medias, color=cores,
            width=0.55, edgecolor="white", linewidth=1.4, zorder=3,
        )
        for barra, media, n in zip(barras, medias, qtd_sessoes):
            x = barra.get_x() + barra.get_width() / 2
            ax1.text(
                x, barra.get_height() + 2,
                f"{media:.1f}%\n({n} sess.)",
                ha="center", va="bottom", fontsize=9, fontweight="bold",
            )
        ax1.axhline(
            y=META_ACERTO, color="#E63946", linestyle="--",
            linewidth=1.6, label=f"Meta ({META_ACERTO:.0f}%)", zorder=4,
        )
        ax1.set_title("Taxa Média de Acertos por Disciplina",
                      fontsize=13, fontweight="bold")
        ax1.set_xlabel("Disciplina")
        ax1.set_ylabel("Taxa Média (%)")
        ax1.set_ylim(0, 115)
        ax1.set_yticks(range(0, 101, 10))
        ax1.yaxis.grid(True, linestyle="--", alpha=0.45, zorder=0)
        ax1.set_axisbelow(True)
        ax1.legend(fontsize=10)
        labels_x = [d if len(d) <= 16 else d[:15] + "…" for d in disciplinas]
        ax1.set_xticks(range(len(disciplinas)))
        ax1.set_xticklabels(labels_x, rotation=15, ha="right", fontsize=9)

        # Gráfico 2 — barras horizontais: tempo total por disciplina
        ax2.set_facecolor("#FAFAFA")
        barras_h = ax2.barh(
            disciplinas, tempos_totais, color=cores,
            edgecolor="white", linewidth=1.2, zorder=3,
        )
        for barra_h, tempo in zip(barras_h, tempos_totais):
            ax2.text(
                barra_h.get_width() + max(tempos_totais) * 0.02,
                barra_h.get_y() + barra_h.get_height() / 2,
                f"{tempo} min",
                va="center", fontsize=8, fontweight="bold", color="#333333",
            )
        ax2.set_title("Tempo Total por Disciplina", fontsize=11, fontweight="bold")
        ax2.set_xlabel("Tempo (min)")
        ax2.xaxis.grid(True, linestyle="--", alpha=0.45, zorder=0)
        ax2.set_axisbelow(True)
        ax2.set_yticks(range(len(disciplinas)))
        ax2.set_yticklabels(labels_x, fontsize=9)
        ax2.invert_yaxis()

        plt.suptitle("Diário de Estudos — Painel Analítico",
                     fontsize=15, fontweight="bold", y=1.01)
        plt.tight_layout()

        # ── A substituição mais importante desta função: ──────────────────
        # plt.show()  →  st.pyplot(fig)
        #
        # plt.show() abre uma janela do sistema operacional.
        # No Streamlit (processo servidor sem display gráfico), isso causaria
        # erro ou travamento. st.pyplot(fig) converte a figura para imagem
        # e a renderiza diretamente no HTML do browser do usuário.
        #
        # plt.close(fig) é OBRIGATÓRIO após st.pyplot():
        # sem ele, cada rerun acumula figuras na memória do servidor
        # (memory leak), podendo causar crash em apps de longa duração.
        st.pyplot(fig)
        plt.close(fig)

        # ── Tabela resumo por disciplina (bônus: não existia no terminal) ─
        st.divider()
        st.subheader("Resumo por Disciplina")
        resumo = [
            {
                "Disciplina":        d,
                "Taxa Média (%)":    m,
                "Status":            "✅ Acima da Meta" if m >= META_ACERTO
                                     else "❌ Abaixo da Meta",
                "Sessões":           q,
                "Tempo Total (min)": t,
            }
            for d, m, q, t in zip(disciplinas, medias, qtd_sessoes, tempos_totais)
        ]
        st.dataframe(resumo, use_container_width=True, hide_index=True)