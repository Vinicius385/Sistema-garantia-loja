import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas

# ─────────────────────────────────────────────
#  Dados da loja
# ─────────────────────────────────────────────
LOJA = "Tonimcell"
TELEFONE_LOJA = "(34) 99885-3804"
ENDERECO_LOJA = "Av. Noruega, 210 – Bairro Tibery"

DB_FILE = "clientes.json"

# ─────────────────────────────────────────────
#  Banco de dados simples (JSON)
# ─────────────────────────────────────────────

def carregar_clientes():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_clientes(clientes):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(clientes, f, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────
#  Geração do PDF de garantia
# ─────────────────────────────────────────────

PASTA_GARANTIAS = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)), "Garantia Clientes")

def gerar_pdf_garantia(cliente: dict, servico: str, valor: str, numero_os: str):
    # Cria a pasta se não existir
    os.makedirs(PASTA_GARANTIAS, exist_ok=True)

    data_hoje = datetime.now()
    data_validade = data_hoje + timedelta(days=90)
    nome_arquivo = f"garantia_{numero_os}_{cliente['nome'].replace(' ', '_')}.pdf"
    caminho = os.path.join(PASTA_GARANTIAS, nome_arquivo)

    largura, altura = A4
    c = canvas.Canvas(caminho, pagesize=A4)

    # ── Fundo do cabeçalho ──
    c.setFillColor(colors.black)
    c.rect(0, altura - 130, largura, 130, fill=True, stroke=False)

    # ── Nome da loja ──
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(colors.HexColor("#00c853"))
    c.drawCentredString(largura / 2, altura - 60, LOJA.upper())

    # ── Slogan / subtítulo ──
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.white)
    c.drawCentredString(largura / 2, altura - 82, "Assistência Técnica em Celulares")

    # ── Contato no cabeçalho ──
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#cccccc"))
    c.drawCentredString(largura / 2, altura - 100,
                        f"{ENDERECO_LOJA}   |   Tel: {TELEFONE_LOJA}")

    # ── Número da OS ──
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.HexColor("#00c853"))
    c.drawRightString(largura - 20, altura - 118, f"OS Nº {numero_os}")

    # ── Título CERTIFICADO DE GARANTIA ──
    y = altura - 160
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.black)
    c.drawCentredString(largura / 2, y, "CERTIFICADO DE GARANTIA")

    # linha decorativa
    c.setStrokeColor(colors.HexColor("#00c853"))
    c.setLineWidth(2)
    c.line(50, y - 8, largura - 50, y - 8)

    # ── Caixa de dados do cliente ──
    y -= 40
    box_x, box_w = 40, largura - 80
    box_h = 130
    c.setFillColor(colors.HexColor("#f0f0f0"))
    c.setStrokeColor(colors.HexColor("#bbbbbb"))
    c.setLineWidth(1)
    c.roundRect(box_x, y - box_h, box_w, box_h, 8, fill=True, stroke=True)

    # título da caixa
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(box_x + 15, y - 18, "DADOS DO CLIENTE")

    linha_h = 22
    campos = [
        ("Cliente",  cliente["nome"]),
        ("Telefone", cliente["telefone"]),
        ("Aparelho", cliente["aparelho"]),
    ]
    for i, (label, valor_campo) in enumerate(campos):
        yy = y - 42 - i * linha_h
        c.setFillColor(colors.HexColor("#444444"))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(box_x + 15, yy, f"{label}:")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(box_x + 90, yy, valor_campo)

    # ── Caixa de serviço ──
    y -= box_h + 20
    box_h2 = 80
    c.setFillColor(colors.HexColor("#f0f0f0"))
    c.setStrokeColor(colors.HexColor("#bbbbbb"))
    c.roundRect(box_x, y - box_h2, box_w, box_h2, 8, fill=True, stroke=True)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(box_x + 15, y - 18, "SERVIÇO EXECUTADO")

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    max_chars = 85
    linhas_servico = [servico[i:i+max_chars] for i in range(0, len(servico), max_chars)]
    for li, linha in enumerate(linhas_servico[:2]):
        c.drawString(box_x + 15, y - 40 - li * 16, linha)

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#007700"))
    c.drawString(box_x + 15, y - 72, f"Valor pago: R$ {valor}")

    # ── Período de garantia ──
    y -= box_h2 + 20
    c.setFillColor(colors.black)
    c.rect(box_x, y - 55, box_w, 55, fill=True, stroke=False)

    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#00c853"))
    c.drawCentredString(largura / 2, y - 22, "GARANTIA DE 90 DIAS")

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.white)
    c.drawCentredString(largura / 2, y - 42,
                        f"Data da emissão: {data_hoje.strftime('%d/%m/%Y')}   |   "
                        f"Válida até: {data_validade.strftime('%d/%m/%Y')}")

    # ── Condições da garantia ──
    y -= 55 + 20
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.black)
    c.drawString(box_x, y, "CONDIÇÕES DA GARANTIA")

    c.setStrokeColor(colors.HexColor("#00c853"))
    c.setLineWidth(1.5)
    c.line(box_x, y - 5, box_x + 210, y - 5)

    condicoes = [
        ("✔", "Esta garantia cobre defeitos relacionados exclusivamente ao serviço executado."),
        ("✔", "Prazo de garantia: 90 (noventa) dias a partir da data de emissão."),
        ("✗", "A garantia NAO cobre MAU USO: aparelho QUEBRADO, MOLHADO, ARRANHADO"),
        ("  ", "ou qualquer outro dano causado por acidente ou negligencia do usuario."),
        ("✗", "Danos fisicos ou liquidos identificados apos a entrega anulam a garantia."),
        ("✗", "Tentativa de reparo por terceiros invalida automaticamente esta garantia."),
    ]

    fonte_cond = 11
    espacamento = 20
    c.setFont("Helvetica", fonte_cond)
    for i, (icone, texto) in enumerate(condicoes):
        yy = y - 28 - i * espacamento
        eh_negativo = icone == "✗"
        eh_continuacao = icone == "  "
        if eh_negativo:
            cor = colors.HexColor("#cc0000")
        elif eh_continuacao:
            cor = colors.HexColor("#cc0000")
        else:
            cor = colors.HexColor("#006600")
        c.setFillColor(cor)
        if not eh_continuacao:
            c.setFont("Helvetica-Bold", fonte_cond)
            c.drawString(box_x + 5, yy, icone)
        c.setFont("Helvetica", fonte_cond)
        offset_x = box_x + 22 if not eh_continuacao else box_x + 22
        c.drawString(offset_x, yy, texto)

    # ── Rodapé ──
    c.setFillColor(colors.black)
    c.rect(0, 0, largura, 30, fill=True, stroke=False)
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#cccccc"))
    c.drawCentredString(largura / 2, 11,
                        f"{LOJA}  –  {ENDERECO_LOJA}  –  {TELEFONE_LOJA}")

    c.save()
    return caminho, nome_arquivo


# ─────────────────────────────────────────────
#  Interface gráfica
# ─────────────────────────────────────────────

COR_BG       = "#111111"
COR_CARD     = "#1c1c1c"
COR_ACCENT   = "#00c853"
COR_TEXT     = "#eaeaea"
COR_SUBTEXT  = "#aaaaaa"
COR_INPUT_BG = "#2a2a2a"
COR_BTN      = "#00a846"
COR_BTN_HV   = "#007730"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Sistema de Garantia – {LOJA}")
        self.geometry("900x620")
        self.resizable(False, False)
        self.configure(bg=COR_BG)

        self.clientes = carregar_clientes()
        self._os_counter = len(self.clientes) + 1

        self._build_ui()

    # ── Helpers de estilo ──────────────────────
    def _lbl(self, parent, text, size=10, bold=False, color=COR_TEXT, **kw):
        font = ("Helvetica", size, "bold" if bold else "normal")
        return tk.Label(parent, text=text, font=font, fg=color, bg=parent["bg"], **kw)

    def _entry(self, parent, textvariable=None, width=30):
        e = tk.Entry(parent, textvariable=textvariable, width=width,
                     bg=COR_INPUT_BG, fg=COR_TEXT, insertbackground=COR_TEXT,
                     relief="flat", font=("Helvetica", 10), bd=4)
        return e

    def _btn(self, parent, text, command, width=18):
        btn = tk.Button(parent, text=text, command=command,
                        bg=COR_BTN, fg="white", activebackground=COR_BTN_HV,
                        activeforeground="white", relief="flat",
                        font=("Helvetica", 10, "bold"), width=width, cursor="hand2",
                        bd=0, padx=8, pady=6)
        return btn

    # ── Construção da UI ───────────────────────
    def _build_ui(self):
        # Sidebar
        sidebar = tk.Frame(self, bg=COR_CARD, width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text=LOJA, font=("Helvetica", 16, "bold"),
                 fg=COR_ACCENT, bg=COR_CARD, pady=20).pack(fill="x")
        tk.Label(sidebar, text="Assistência Técnica", font=("Helvetica", 8),
                 fg=COR_SUBTEXT, bg=COR_CARD).pack()

        tk.Frame(sidebar, bg=COR_ACCENT, height=2).pack(fill="x", pady=15, padx=15)

        menus = [
            ("🏠  Início",              self._show_inicio),
            ("➕  Cadastrar Cliente",   self._show_cadastro),
            ("📄  Gerar Garantia",      self._show_garantia),
            ("👥  Clientes Cadastrados", self._show_lista),
        ]
        for texto, cmd in menus:
            b = tk.Button(sidebar, text=texto, command=cmd,
                          bg=COR_CARD, fg=COR_TEXT, activebackground=COR_ACCENT,
                          activeforeground="white", relief="flat",
                          font=("Helvetica", 10), anchor="w", padx=20, pady=10,
                          cursor="hand2", bd=0)
            b.pack(fill="x")

        tk.Frame(sidebar, bg=COR_ACCENT, height=2).pack(fill="x", pady=15, padx=15, side="bottom")
        tk.Label(sidebar, text=TELEFONE_LOJA, font=("Helvetica", 8),
                 fg=COR_SUBTEXT, bg=COR_CARD, pady=5).pack(side="bottom")

        # Área principal
        self.main = tk.Frame(self, bg=COR_BG)
        self.main.pack(side="left", fill="both", expand=True)

        self._show_inicio()

    def _clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    def _page_title(self, title, sub=""):
        tk.Label(self.main, text=title, font=("Helvetica", 18, "bold"),
                 fg=COR_ACCENT, bg=COR_BG).pack(anchor="w", padx=30, pady=(25, 0))
        if sub:
            tk.Label(self.main, text=sub, font=("Helvetica", 9),
                     fg=COR_SUBTEXT, bg=COR_BG).pack(anchor="w", padx=30)
        tk.Frame(self.main, bg=COR_ACCENT, height=2).pack(fill="x", padx=30, pady=10)

    # ── Tela Início ────────────────────────────
    def _show_inicio(self):
        self._clear_main()
        self._page_title("Bem-vindo ao Sistema", LOJA + " – Gestão de Garantias")

        frame = tk.Frame(self.main, bg=COR_BG)
        frame.pack(expand=True)

        cards = [
            ("➕", "Cadastrar Cliente",    "Registre um novo\ncliente no sistema",   self._show_cadastro),
            ("📄", "Gerar Garantia",       "Emita uma garantia\nem PDF",              self._show_garantia),
            ("👥", "Clientes Cadastrados", f"{len(self.clientes)} cliente(s)\nregistrado(s)", self._show_lista),
        ]

        for i, (icon, titulo, desc, cmd) in enumerate(cards):
            card = tk.Frame(frame, bg=COR_CARD, width=190, height=160,
                            relief="flat", bd=0)
            card.grid(row=0, column=i, padx=15, pady=20, ipadx=10, ipady=10)
            card.pack_propagate(False)

            tk.Label(card, text=icon, font=("Helvetica", 26), bg=COR_CARD,
                     fg=COR_ACCENT).pack(pady=(18, 2))
            tk.Label(card, text=titulo, font=("Helvetica", 10, "bold"),
                     bg=COR_CARD, fg=COR_TEXT).pack()
            tk.Label(card, text=desc, font=("Helvetica", 8),
                     bg=COR_CARD, fg=COR_SUBTEXT, justify="center").pack(pady=4)
            self._btn(card, "Acessar", cmd, width=14).pack(pady=6)

    # ── Tela Cadastro ──────────────────────────
    def _show_cadastro(self):
        self._clear_main()
        self._page_title("Cadastrar Cliente", "Preencha os dados do cliente")

        card = tk.Frame(self.main, bg=COR_CARD, padx=30, pady=25)
        card.pack(padx=40, pady=10, fill="x")

        self._v_nome     = tk.StringVar()
        self._v_telefone = tk.StringVar()
        self._v_aparelho = tk.StringVar()

        campos = [
            ("Nome completo",    self._v_nome,     "Ex: João da Silva"),
            ("Telefone",         self._v_telefone, "Ex: (34) 99999-9999"),
            ("Modelo do aparelho", self._v_aparelho, "Ex: Samsung Galaxy A54"),
        ]

        for label, var, placeholder in campos:
            row = tk.Frame(card, bg=COR_CARD)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=label, font=("Helvetica", 9, "bold"),
                     fg=COR_SUBTEXT, bg=COR_CARD, width=22, anchor="w").pack(side="left")
            e = self._entry(row, textvariable=var, width=38)
            e.pack(side="left", padx=(0, 10))
            tk.Label(row, text=placeholder, font=("Helvetica", 8, "italic"),
                     fg=COR_SUBTEXT, bg=COR_CARD).pack(side="left")

        tk.Frame(card, bg=COR_ACCENT, height=1).pack(fill="x", pady=12)

        btns = tk.Frame(card, bg=COR_CARD)
        btns.pack()
        self._btn(btns, "💾  Salvar Cliente", self._salvar_cliente).pack(side="left", padx=8)
        self._btn(btns, "🔄  Limpar", self._limpar_cadastro,
                  ).pack(side="left", padx=8)

        self._lbl_status_cad = tk.Label(card, text="", font=("Helvetica", 9),
                                        fg="#4caf50", bg=COR_CARD)
        self._lbl_status_cad.pack(pady=(8, 0))

    def _salvar_cliente(self):
        nome     = self._v_nome.get().strip()
        telefone = self._v_telefone.get().strip()
        aparelho = self._v_aparelho.get().strip()

        if not nome or not telefone or not aparelho:
            messagebox.showwarning("Atenção", "Preencha todos os campos!")
            return

        cliente = {"nome": nome, "telefone": telefone, "aparelho": aparelho}
        self.clientes.append(cliente)
        salvar_clientes(self.clientes)

        self._lbl_status_cad.config(
            text=f"✔  Cliente '{nome}' cadastrado com sucesso!", fg="#4caf50")
        self._limpar_cadastro()

    def _limpar_cadastro(self):
        for v in (self._v_nome, self._v_telefone, self._v_aparelho):
            v.set("")

    # ── Tela Gerar Garantia ────────────────────
    def _show_garantia(self):
        self._clear_main()
        self._page_title("Gerar Garantia", "Selecione o cliente e informe o serviço")

        if not self.clientes:
            tk.Label(self.main, text="⚠  Nenhum cliente cadastrado.\nCadastre um cliente primeiro.",
                     font=("Helvetica", 12), fg=COR_ACCENT, bg=COR_BG,
                     justify="center").pack(expand=True)
            return

        card = tk.Frame(self.main, bg=COR_CARD, padx=30, pady=25)
        card.pack(padx=40, pady=10, fill="x")

        nomes = [c["nome"] for c in self.clientes]

        # Cliente
        row1 = tk.Frame(card, bg=COR_CARD)
        row1.pack(fill="x", pady=6)
        tk.Label(row1, text="Cliente:", font=("Helvetica", 9, "bold"),
                 fg=COR_SUBTEXT, bg=COR_CARD, width=22, anchor="w").pack(side="left")
        self._v_cliente_sel = tk.StringVar(value=nomes[0])
        cb = ttk.Combobox(row1, textvariable=self._v_cliente_sel,
                          values=nomes, state="readonly", width=36,
                          font=("Helvetica", 10))
        cb.pack(side="left")

        # Serviço
        row2 = tk.Frame(card, bg=COR_CARD)
        row2.pack(fill="x", pady=6)
        tk.Label(row2, text="Serviço executado:", font=("Helvetica", 9, "bold"),
                 fg=COR_SUBTEXT, bg=COR_CARD, width=22, anchor="w").pack(side="left")
        self._v_servico = tk.StringVar()
        self._entry(row2, textvariable=self._v_servico, width=38).pack(side="left")

        # Valor
        row3 = tk.Frame(card, bg=COR_CARD)
        row3.pack(fill="x", pady=6)
        tk.Label(row3, text="Valor pago (R$):", font=("Helvetica", 9, "bold"),
                 fg=COR_SUBTEXT, bg=COR_CARD, width=22, anchor="w").pack(side="left")
        self._v_valor = tk.StringVar()
        self._entry(row3, textvariable=self._v_valor, width=18).pack(side="left")

        tk.Frame(card, bg=COR_ACCENT, height=1).pack(fill="x", pady=12)

        self._btn(card, "📄  Gerar PDF de Garantia", self._gerar_garantia, width=26).pack()

        self._lbl_status_gar = tk.Label(card, text="", font=("Helvetica", 9),
                                        fg="#4caf50", bg=COR_CARD, wraplength=500)
        self._lbl_status_gar.pack(pady=(8, 0))

    def _gerar_garantia(self):
        nome_sel = self._v_cliente_sel.get()
        servico  = self._v_servico.get().strip()
        valor    = self._v_valor.get().strip()

        if not servico:
            messagebox.showwarning("Atenção", "Informe o serviço executado!")
            return
        if not valor:
            messagebox.showwarning("Atenção", "Informe o valor pago!")
            return

        cliente = next((c for c in self.clientes if c["nome"] == nome_sel), None)
        if not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado.")
            return

        numero_os = f"{self._os_counter:04d}"
        self._os_counter += 1

        try:
            caminho, nome_arq = gerar_pdf_garantia(cliente, servico, valor, numero_os)
            self._lbl_status_gar.config(
                text=f"✔  Garantia gerada com sucesso!\nArquivo: {nome_arq}\nLocal: {caminho}",
                fg="#4caf50")
            messagebox.showinfo("Sucesso",
                                f"Garantia gerada!\n\n{caminho}")
        except Exception as ex:
            messagebox.showerror("Erro", f"Falha ao gerar PDF:\n{ex}")

    # ── Tela Lista de Clientes ─────────────────
    def _show_lista(self):
        self._clear_main()
        self._page_title("Clientes Cadastrados",
                         f"{len(self.clientes)} cliente(s) no sistema")

        frame = tk.Frame(self.main, bg=COR_BG)
        frame.pack(fill="both", expand=True, padx=30, pady=5)

        cols = ("Nome", "Telefone", "Aparelho")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=COR_CARD, foreground=COR_TEXT,
                        fieldbackground=COR_CARD, rowheight=28,
                        font=("Helvetica", 10))
        style.configure("Custom.Treeview.Heading",
                        background=COR_ACCENT, foreground="white",
                        font=("Helvetica", 10, "bold"))
        style.map("Custom.Treeview",
                  background=[("selected", COR_ACCENT)])

        tree = ttk.Treeview(frame, columns=cols, show="headings",
                            style="Custom.Treeview")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=220 if col != "Telefone" else 160, anchor="w")

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)

        for i, c in enumerate(self.clientes):
            tag = "odd" if i % 2 == 0 else "even"
            tree.insert("", "end", values=(c["nome"], c["telefone"], c["aparelho"]),
                        tags=(tag,))
        tree.tag_configure("odd",  background=COR_CARD)
        tree.tag_configure("even", background="#222222")

        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        btns = tk.Frame(self.main, bg=COR_BG)
        btns.pack(pady=10)

        def excluir():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Atenção", "Selecione um cliente para excluir.")
                return
            idx = tree.index(sel[0])
            nome = self.clientes[idx]["nome"]
            if messagebox.askyesno("Confirmar",
                                   f"Excluir '{nome}'?"):
                self.clientes.pop(idx)
                salvar_clientes(self.clientes)
                self._show_lista()

        self._btn(btns, "🔄  Atualizar", self._show_lista, width=14).pack(side="left", padx=6)
        self._btn(btns, "🗑  Excluir", excluir, width=14).pack(side="left", padx=6)


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()