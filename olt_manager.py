from tkinter import ttk, messagebox, scrolledtext, simpledialog
import tkinter as tk
from datetime import datetime
import json
import os
import re
import textwrap
import sys


class CommandValidator:
    """Classe para validação de comandos"""

    @staticmethod
    def validate_params(params):
        """Validar parâmetros do comando"""
        patterns = {
            "slot": r"^\d{1,2}$",
            "porta": r"^\d{1,2}$",
            "pon": r"^\d{1,2}$",
            "id": r"^\d{1,3}$",
            "sn": r"^[A-Za-z0-9]{8,16}$",
            "mac": r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",
        }

        errors = []
        for param, value in params.items():
            param_lower = param.lower()
            if param_lower in patterns:
                if not re.match(patterns[param_lower], value):
                    errors.append(f"Formato inválido para {param}")

        return errors


class CommandDocumentation:
    """Classe para gerenciar documentação dos comandos"""

    def __init__(self):
        self.docs = {
            "slot": "Número do slot da OLT (1-16)",
            "porta": "Número da porta GPON (1-16)",
            "pon": "Número da PON (1-8)",
            "id": "ID da ONU (1-128)",
            "sn": "Número de série da ONU (8-16 caracteres)",
            "mac": "Endereço MAC da ONU (formato: XX:XX:XX:XX:XX:XX)",
            "firmware": "Nome do arquivo de firmware",
        }

        self.examples = {
            "show gpon onu by sn": {
                "desc": "Consultar ONU pelo número de série",
                "example": "show gpon onu by sn ZTEGC1234567",
            },
            "show gpon onu detail-info": {
                "desc": "Mostrar detalhes da ONU",
                "example": "show gpon onu detail-info gpon-olt_1/1/1 1",
            },
        }

        self.common_issues = {
            "sn_not_found": "ONU não encontrada - Verifique se o número de série está correto",
            "onu_offline": "ONU offline - Verifique a conexão física",
            "auth_failed": "Falha na autenticação - Verifique se a ONU está autorizada",
        }

        self.olt_specific_tips = {
            "Huawei MA5800 Araquari": [
                "🔑 Importante: Execute 'enable' primeiro para entrar no modo privilegiado",
                "📝 Após 'enable', você pode executar comandos de configuração",
                "💡 Use 'save' para salvar alterações de configuração"
            ],
            "ZTE Z600 Itaum": [
                "🔑 Execute 'enable' para modo privilegiado antes de configurações",
                "📝 Use 'configure terminal' para entrar no modo de configuração",
                "⚠️ Verifique sempre os comandos disponíveis antes de alterar configurações"
            ],
            "ZTE C300 Ullyses": [
                "🔑 Execute 'enable' para modo privilegiado",
                "📝 Use 'config' para configurações",
                "💡 Use 'save' para salvar alterações de configuração"
            ],
            "Fiberhome AN5516": [
                "🔑 Execute 'enable' para modo admin",
                "📝 Use 'cd' para navegar entre módulos",
                "💡 Execute 'save' para salvar configurações"
            ]
        }

    def get_param_help(self, param):
        """Obter ajuda para um parâmetro específico"""
        return self.docs.get(param.lower(), "Sem documentação disponível")

    def get_command_example(self, command):
        """Obter exemplo de uso para um comando"""
        for key, value in self.examples.items():
            if key in command.lower():
                return value
        return None

    def get_common_issues(self, command):
        """Obter problemas comuns relacionados ao comando"""

    def get_olt_tips(self, olt_name):
        """Obter dicas específicas para uma OLT"""
        return self.olt_specific_tips.get(olt_name, [])
        issues = []
        if "show" in command and "onu" in command:
            issues.append(self.common_issues["sn_not_found"])
            issues.append(self.common_issues["onu_offline"])
        if "auth" in command:
            issues.append(self.common_issues["auth_failed"])
        return issues


class CommandHistory:
    def __init__(self):
        self.history = []
        # Definir caminho do arquivo de histórico
        if hasattr(sys, "_MEIPASS"):
            # Se estiver rodando como executável PyInstaller
            exe_dir = os.path.dirname(sys.executable)
            self.history_file = os.path.join(exe_dir, "command_history.json")
        else:
            # Se estiver rodando como script
            self.history_file = "command_history.json"
        self.load_history()

    def add_command(self, command, olt_model, category):
        entry = {
            "command": command,
            "olt_model": olt_model,
            "category": category,
            "timestamp": datetime.now().isoformat(),
        }
        self.history.append(entry)
        self.save_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []
        else:
            self.history = []

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get_recent_commands(self, limit=20):
        return sorted(self.history, key=lambda x: x["timestamp"], reverse=True)[:limit]

    def clear_all(self):
        """Limpar todo o histórico de comandos"""
        self.history = []
        self.save_history()


class FavoriteCommands:
    def __init__(self):
        self.favorites = []
        # Definir caminho do arquivo de favoritos
        if hasattr(sys, "_MEIPASS"):
            # Se estiver rodando como executável PyInstaller
            exe_dir = os.path.dirname(sys.executable)
            self.favorites_file = os.path.join(exe_dir, "favorite_commands.json")
        else:
            # Se estiver rodando como script
            self.favorites_file = "favorite_commands.json"
        self.load_favorites()

    def add_favorite(self, command, name, olt_model, category, params=None):
        entry = {
            "name": name,
            "command": command,
            "olt_model": olt_model,
            "category": category,
            "params": params or {},
            "added_on": datetime.now().isoformat(),
        }
        self.favorites.append(entry)
        self.save_favorites()

    def remove_favorite(self, command):
        self.favorites = [f for f in self.favorites if f["command"] != command]
        self.save_favorites()

    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, "r", encoding="utf-8") as f:
                    self.favorites = json.load(f)
            except Exception:
                self.favorites = []
        else:
            self.favorites = []

    def save_favorites(self):
        try:
            with open(self.favorites_file, "w", encoding="utf-8") as f:
                json.dump(self.favorites, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def is_favorite(self, command):
        return any(f["command"] == command for f in self.favorites)


class OLTCommandManager:
    def __init__(self, root):
        self.root = root
        self.root.title("OLT Command Manager v1.6")
        self.root.geometry("1200x800")

        try:
            # Definir o ícone da janela
            if hasattr(sys, "_MEIPASS"):
                # Se estiver rodando como executável
                icon_path = os.path.join(sys._MEIPASS, "ico.ico")
            else:
                # Se estiver rodando como script
                icon_path = os.path.join("Extras", "ico.ico")
            self.root.iconbitmap(icon_path)

            # Inicializar componentes
            self.validator = CommandValidator()
            self.documentation = CommandDocumentation()
            self.history = CommandHistory()
            self.favorites = FavoriteCommands()

            # Dados dos comandos
            if hasattr(sys, "_MEIPASS"):
                # Se estiver rodando como executável PyInstaller
                exe_dir = os.path.dirname(sys.executable)
                self.data_file = os.path.join(exe_dir, "olt_commands.json")
            else:
                # Se estiver rodando como script
                self.data_file = "olt_commands.json"
            self.load_data()

            # Configuração do tema inicial antes de qualquer outra coisa
            self.theme_var = tk.StringVar(value="light")  # Default theme
            self.setup_theme()

            # Carregar preferências depois de inicializar o tema
            if hasattr(sys, "_MEIPASS"):
                # Se estiver rodando como executável PyInstaller
                exe_dir = os.path.dirname(sys.executable)
                self.config_file = os.path.join(exe_dir, "config_file.json")
            else:
                # Se estiver rodando como script
                self.config_file = os.path.join(
                    os.path.dirname(__file__), "config_file.json"
                )
            self.load_preferences()  # This will update theme_var if saved

            # Criar interface
            self.create_main_interface()

            # Aplicar tema aos widgets depois que eles existirem
            self.update_widget_colors()

            # Configurar evento de fechamento
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

            # Handle window position update on resize/move
            self.root.bind(
                "<Configure>", lambda e: self.root.after(1000, self.save_preferences)
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar a aplicação:\n{str(e)}")
            raise

    def setup_theme(self):
        """Configurar tema e estilos da interface"""
        self.theme_var = tk.StringVar(value="light")  # Tema claro como padrão

        self.themes = {
            "dark": {
                "bg": "#1a1a1a",  # Fundo escuro neutro
                "bg_medium": "#2d2d2d",  # Cards neutros
                "bg_light": "#404040",  # Elementos destacados neutros
                "accent": "#6b7280",  # Cinza médio para destaques
                "accent_light": "#9ca3af",  # Cinza claro
                "text": "#f3f4f6",  # Texto claro neutro
                "text_disabled": "#6b7280",  # Texto desabilitado neutro
                "error": "#dc2626",  # Vermelho sutil
                "success": "#059669",  # Verde sutil
                "warning": "#d97706",  # Laranja sutil
                "border": "#4b5563",  # Bordas neutras
            },
            "light": {
                "bg": "#f8fafc",  # Fundo muito claro neutro
                "bg_medium": "#ffffff",  # Branco puro
                "bg_light": "#f1f5f9",  # Cinza muito claro
                "accent": "#64748b",  # Cinza azulado neutro
                "accent_light": "#94a3b8",  # Cinza azulado claro
                "text": "#334155",  # Cinza escuro para texto
                "text_disabled": "#94a3b8",  # Cinza médio desabilitado
                "error": "#dc2626",  # Vermelho sutil
                "success": "#059669",  # Verde sutil
                "warning": "#d97706",  # Laranja sutil
                "border": "#e2e8f0",  # Bordas muito suaves
            },
        }

        self.apply_theme()

    def apply_theme(self):
        """Aplicar tema selecionado com estilo moderno"""
        try:
            theme = self.themes[self.theme_var.get()]

            style = ttk.Style()
            style.theme_use("clam")

            # Configurar estilos gerais
            style.configure(
                ".",
                background=theme["bg"],
                foreground=theme["text"],
                font=("Segoe UI", 9),
            )

            # Frames minimalistas
            style.configure("Modern.TFrame", background=theme["bg"])
            style.configure(
                "Card.TFrame",
                background=theme["bg_medium"],
                borderwidth=0,
                relief="flat",
            )


            # Labels minimalistas
            style.configure(
                "Modern.TLabel",
                background=theme["bg"],
                foreground=theme["text"],
                font=("Segoe UI", 9),
            )

            style.configure(
                "Title.TLabel",
                background=theme["bg"],
                foreground=theme["text"],
                font=("Segoe UI", 14, "bold"),
            )

            style.configure(
                "Subtitle.TLabel",
                background=theme["bg"],
                foreground=theme["text"],
                font=("Segoe UI", 11),
            )

            # Label específico para cards (fundo médio)
            style.configure(
                "Card.TLabel",
                background=theme["bg_medium"],
                foreground=theme["text"],
                font=("Segoe UI", 11),
            )

            # Botões minimalistas
            style.configure(
                "Modern.TButton",
                background=theme["bg"],
                foreground=theme["text"],
                borderwidth=0,
                relief="flat",
                font=("Segoe UI", 9),
            )

            style.map(
                "Modern.TButton",
                background=[
                    ("active", theme["bg_medium"]),
                    ("pressed", theme["bg_light"]),
                ],
                foreground=[("active", theme["text"]), ("pressed", theme["text"])],
            )

            style.configure(
                "Accent.TButton",
                background=theme["accent"],
                foreground="#ffffff",
                borderwidth=0,
                relief="flat",
                font=("Segoe UI", 9, "bold"),
            )

            style.map(
                "Accent.TButton",
                background=[
                    ("active", theme["accent_light"]),
                    ("pressed", theme["accent"]),
                ],
            )

            # Entradas minimalistas
            style.configure(
                "TEntry",
                fieldbackground=theme["bg"],
                foreground=theme["text"],
                borderwidth=0,
                relief="flat",
            )

            style.configure(
                "Error.TEntry",
                fieldbackground=theme["error"] + "20",  # 20% de opacidade
                foreground=theme["text"],
            )

            # Treeview minimalista
            style.configure(
                "Modern.Treeview",
                background=theme["bg"],
                foreground=theme["text"],
                fieldbackground=theme["bg"],
                rowheight=28,
                borderwidth=0,
                font=("Segoe UI", 9),
            )

            # Configure static heading style without hover effect
            style.configure(
                "Modern.Treeview.Heading",
                background=theme[
                    "bg_medium"
                ],  # Using background color instead of accent
                foreground=theme["text"],
                font=("Segoe UI", 10, "bold"),
                relief="flat",
            )

            # Explicitly remove any hover/active state mapping for headings
            style.map("Modern.Treeview.Heading", background=[], foreground=[])

            style.map(
                "Modern.Treeview",
                background=[("selected", theme["accent"])],
                foreground=[("selected", "#ffffff")],
            )

            # Notebook minimalista
            style.configure("TNotebook", background=theme["bg"], borderwidth=0)
            style.configure(
                "TNotebook.Tab",
                background=theme["bg"],
                foreground=theme["text"],
                padding=[12, 6],
                font=("Segoe UI", 9),
                borderwidth=0,
            )

            style.map(
                "TNotebook.Tab",
                background=[("selected", theme["bg_medium"])],
                foreground=[("selected", theme["text"])],
            )

            # Configuração específica para Comboboxes
            style.configure(
                "TCombobox",
                fieldbackground=theme["bg"],
                background=theme["bg"],
                foreground=theme["text"],
                arrowcolor=theme["text"],
                selectbackground=theme["accent"],
                selectforeground="white",
            )

            style.map(
                "TCombobox",
                fieldbackground=[("readonly", theme["bg"])],
                selectbackground=[("readonly", theme["accent"])],
                selectforeground=[("readonly", "white")],
                background=[("readonly", theme["bg"])],
                foreground=[("readonly", theme["text"])],
            )

            # Atualizar cores
            self.root.configure(bg=theme["bg"])
            self.update_widget_colors()

            # Configurar a cor do menu dropdown dos Comboboxes
            self.root.option_add("*TCombobox*Listbox.background", theme["bg_light"])
            self.root.option_add("*TCombobox*Listbox.foreground", theme["text"])
            self.root.option_add("*TCombobox*Listbox.selectBackground", theme["accent"])
            self.root.option_add("*TCombobox*Listbox.selectForeground", "white")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar tema:\n{str(e)}")

    def update_widget_colors(self):
        """Atualizar cores dos widgets com gradiente sutil"""
        if not hasattr(self, "themes") or not hasattr(self, "theme_var"):
            return

        theme = self.themes[self.theme_var.get()]

        # Lista de widgets para atualizar
        widgets = []

        # Só adiciona widgets que existem
        if hasattr(self, "command_text") and self.command_text is not None:
            widgets.append(self.command_text)
        if hasattr(self, "editor_text") and self.editor_text is not None:
            widgets.append(self.editor_text)
        if hasattr(self, "results_listbox") and self.results_listbox is not None:
            widgets.append(self.results_listbox)
        # Atualizar PanedWindow se existir
        if hasattr(self, "content_frame") and self.content_frame is not None:
            try:
                self.content_frame.configure(bg=theme["bg"])
            except:
                pass

        # Configura cada widget existente
        for widget in widgets:
            try:
                widget.configure(
                    bg=theme["bg"],
                    fg=theme["text"],
                    insertbackground=theme["text"],
                    selectbackground=theme["accent"],
                    selectforeground="white",
                    relief="flat",
                    borderwidth=0,
                    highlightthickness=0,
                )
            except (tk.TclError, AttributeError):
                continue  # Ignora erros de widgets que não suportam algumas propriedades

    def load_data(self):
        """Carregar dados dos comandos"""
        default_data = {
            "olts": {
                "ZTE Z600 Itaum": {
                    "description": "OLT ZTE ITAUM ZXA10 C600",
                    "categories": {
                        "Gerenciamento de ONU": {
                            "Consultar ONU": {
                                "Por Serial Number": "show gpon onu by sn {sn}",
                                "Detalhes da ONU": "show gpon onu detail-info gpon-olt_{slot}/{porta}/{pon} {id}",
                                "Estado das ONUs": "show gpon onu state gpon-olt_{slot}/{porta}/{pon}",
                            },
                            "Atualizar ONU": {
                                "Verificar versão": "show remote-unit information gpon_olt-{slot}/{porta}/{pon} {id}",
                                "Atualizar ZTE": "remote-unit update-and-reboot {firmware} gpon_olt-{slot}/{porta}/{pon} {id}",
                                "Atualizar FAST": "remote-unit update-and-reboot {firmware} gpon_olt-{slot}/{porta}/{pon} {id}",
                                "Status atualização": "show remote-unit update-status gpon_olt-{slot}/{porta}/{pon} {id}",
                            },
                        },
                        "Diagnóstico": {
                            "Informações Ópticas": {
                                "Info óptica PON": "show gpon optical-info gpon-olt_{slot}/{porta}/{pon}",
                                "Níveis ópticos ONU": "show gpon onu optical-info gpon-olt_{slot}/{porta}/{pon} {id}",
                            }
                        },
                        "Sistema": {
                            "Informações Gerais": {
                                "Versão sistema": "show version",
                                "Lista interfaces": "show interface brief",
                                "Arquivos firmware": "dir /datadisk0/LR0/onuver/",
                            }
                        },
                    },
                },
                "ZTE C300 Ullyses": {
                    "description": "OLT ZTE ULLYSES",
                    "categories": {
                        "Gerenciamento de ONU": {
                            "Consultar ONU": {
                                "Por Serial Number": "show gpon onu by sn {sn}",
                                "Detalhes da ONU": "show gpon onu detail-info gpon-olt_{slot}/{porta}/{pon}",
                                "MAC da ONU": "show gpon onu mac gpon-olt_{slot}/{porta}/{pon} {id}",
                                "Status PON": "show interface gpon-olt_{slot}/{porta}/{pon}",
                                "Config da PON": "show running-config interface gpon-olt_{slot}/{porta}/{pon}",
                            },
                            "Remover ONU": {
                                "Por ID": "configure terminal\ninterface gpon-olt_{slot}/{porta}/{pon}\nno onu {id}\nexit\nexit",
                                "Por Serial": "configure terminal\ninterface gpon-olt_{slot}/{porta}/{pon}\nno onu sn {sn}\nexit\nexit",
                            },
                            "Reiniciar ONU": "configure terminal\ninterface gpon-olt_{slot}/{porta}/{pon}\nonu {id} reboot\nexit\nexit",
                            "Atualizar ONU": {
                                "Verificar versão": "show cpe information gpon-olt_{slot}/{porta}/{pon} {id}",
                                "Atualizar firmware": "cpe update-and-reboot {firmware} gpon-olt_{slot}/{porta}/{pon} {id}",
                                "Status atualização": "show cpe update-status gpon-olt_{slot}/{porta}/{pon} {id}",
                            },
                        },
                        "Diagnóstico": {
                            "Informações Ópticas": {
                                "Níveis ópticos": "show gpon onu optical-info gpon-olt_{slot}/{porta}/{pon} {id}",
                                "Distância ONU": "show gpon onu distance gpon-olt_{slot}/{porta}/{pon} {id}",
                                "MACs aprendidos": "show gpon onu mac-learning gpon-olt_{slot}/{porta}/{pon} {id}",
                            },
                            "Alarmes": "show alarm active",
                        },
                    },
                },
                "Huawei MA5800 Araquari": {
                    "description": "OLT HUAWEI ARAQUARI",
                    "categories": {
                        "Gerenciamento de ONU": {
                            "Consultar ONU": {
                                "Resumo PON": "display ont info summary {slot}/{porta}/{pon}",
                                "Por Serial Number": "display ont info by-sn {sn}",
                                "Por MAC": "display ont info by-mac {mac}",
                                "Informações detalhadas": "display ont info {slot}/{porta}/{pon} {id}",
                                "Versão firmware": "display ont version {slot}/{porta}/{pon} {id}",
                            },
                            "Remover ONU": {
                                "Verificar service-ports": "display service-port port {slot}/{porta}/{pon} ont {id}",
                                "Remover service-port": "config\nundo service-port {index}",
                                "Excluir ONU": "config\ninterface gpon {slot}/{porta}\nont delete {pon} {id}\nquit\nquit\nsave",
                            },
                            "Reiniciar ONU": "ont reset {slot} {porta} {pon} {id}",
                        },
                        "Diagnóstico": {
                            "Informações Ópticas": "display ont optical-info {slot}/{porta}/{pon} {id}",
                            "Estado portas": "display ont port state {slot}/{porta}/{pon} {id}",
                            "Alarmes ONU": "display ont alarm {slot}/{porta}/{pon} {id}",
                        },
                        "Sistema": {
                            "Informações Gerais": {
                                "Versão sistema": "display version",
                                "Info placas": "display board 0",
                                "Status PON": "display interface gpon {slot}/{porta}/{pon}",
                                "Alarmes ativos": "display alarm active all",
                            },
                            "Navegação": {
                                "Modo privilegiado": "enable",
                                "Modo configuração": "configure terminal",
                                "Interface GPON": "interface gpon {slot}/{porta}",
                                "Sair": "quit",
                            },
                        },
                    },
                },
            }
        }

        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except:
                self.data = default_data
                self.save_data()
        else:
            self.data = default_data
            self.save_data()

    def save_data(self):
        """Salvar dados no arquivo JSON"""
        try:
            # Obter o conteúdo atual do editor
            json_text = self.editor_text.get(1.0, tk.END).strip()

            # Validar o JSON antes de salvar
            try:
                self.data = json.loads(json_text)
                with open(self.data_file, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)

                # Atualizar a interface após salvar
                self.populate_tree(
                    self.olt_var.get()
                    if self.olt_var.get()
                    else next(iter(self.data["olts"]))
                )
                messagebox.showinfo("Sucesso", "Alterações salvas com sucesso!")
            except json.JSONDecodeError as e:
                messagebox.showerror("Erro", f"JSON inválido: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar arquivo: {str(e)}")

    def create_main_interface(self):
        """Criar interface principal com design moderno"""
        # Frame principal com sombra sutil
        main_frame = ttk.Frame(self.root, style="Modern.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Cabeçalho minimalista
        header_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        header_frame.pack(fill="x", pady=(0, 10))

        # Título com ícone
        title_frame = ttk.Frame(header_frame, style="Modern.TFrame")
        title_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(
            title_frame, text="OLT Command Manager", style="Title.TLabel"
        ).pack(side="left")

        # Controles de tema
        theme_frame = ttk.Frame(title_frame, style="Modern.TFrame")
        theme_frame.pack(side="right", padx=10)

        ttk.Label(theme_frame, text="Tema:", style="Modern.TLabel").pack(
            side="left", padx=5
        )
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=["light", "dark"],
            state="readonly",
            width=8,
        )
        theme_combo.pack(side="left")
        theme_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_theme())

        # Container principal com abas modernas
        notebook = ttk.Notebook(main_frame, style="TNotebook")
        notebook.pack(fill="both", expand=True)

        # Abas minimalistas
        self.tree_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(self.tree_frame, text="Navegação")
        self.create_tree_interface()

        self.history_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(self.history_frame, text="Histórico")
        self.create_history_interface()

        self.favorites_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(self.favorites_frame, text="Favoritos")
        self.create_favorites_interface()

        self.editor_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(self.editor_frame, text="Editor")
        self.create_editor_interface()

    def create_tree_interface(self):
        """Criar interface de navegação com design moderno"""
        # Frame superior com seleção de OLT
        top_frame = ttk.Frame(self.tree_frame, style="Card.TFrame")
        top_frame.pack(fill="x", pady=(0, 10), padx=10)

        ttk.Label(top_frame, text="Modelo da OLT:", style="Card.TLabel").pack(
            side="left", padx=10, pady=10
        )

        self.olt_var = tk.StringVar()

        # Obter lista de modelos disponíveis
        self.available_olts = list(self.data["olts"].keys())

        # Definir o primeiro modelo disponível como padrão se houver algum
        if self.available_olts:
            self.olt_var.set(self.available_olts[0])

        olt_combo = ttk.Combobox(
            top_frame,
            textvariable=self.olt_var,
            values=self.available_olts,
            state="readonly",
            width=25,
        )
        olt_combo.pack(side="left", padx=10, pady=10)
        olt_combo.bind("<<ComboboxSelected>>", self.on_olt_selected)

        # Container com painel divisível
        self.content_frame = tk.PanedWindow(self.tree_frame, orient="horizontal", sashwidth=4, bg=self.themes[self.theme_var.get()]["bg"])
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Painel esquerdo - Árvore de comandos
        left_panel = ttk.Frame(
            self.content_frame, style="Modern.TFrame"
        )
        self.content_frame.add(left_panel)

        # Título da seção esquerda
        ttk.Label(left_panel, text="Estrutura de Comandos", style="Subtitle.TLabel").pack(
            anchor="w", padx=5, pady=(5, 10)
        )

        # Treeview com scrollbar integrada
        tree_container = ttk.Frame(left_panel, style="Modern.TFrame")
        tree_container.pack(fill="both", expand=True, padx=0, pady=(0, 5))

        self.tree = ttk.Treeview(tree_container, show="tree", style="Modern.Treeview")
        tree_scroll = ttk.Scrollbar(
            tree_container, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Painel direito - Detalhes do comando
        self.right_panel = ttk.Frame(
            self.content_frame, style="Modern.TFrame"
        )
        self.content_frame.add(self.right_panel)

        # Configurar evento para salvar posição da barra lateral
        self.content_frame.bind("<<SashMoved>>", self.save_sidebar_position)

        # Definir largura inicial do painel esquerdo (ajustável pelo usuário)
        self.root.update_idletasks()  # Forçar atualização para calcular tamanhos

        # Título da seção direita
        ttk.Label(self.right_panel, text="Comando Selecionado", style="Subtitle.TLabel").pack(
            anchor="w", padx=5, pady=(5, 10)
        )

        # Área de comando com destaque
        cmd_frame = ttk.Frame(self.right_panel, style="Modern.TFrame")
        cmd_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        self.command_text = scrolledtext.ScrolledText(
            cmd_frame, height=8, wrap="word", font=("Consolas", 10)
        )
        self.command_text.pack(fill="both", expand=True)

        # Container para parâmetros e dicas lado a lado
        params_tips_container = ttk.Frame(self.right_panel, style="Modern.TFrame")
        params_tips_container.pack(fill="x", padx=10, pady=(0, 10))

        # Frame para parâmetros (lado esquerdo)
        params_container = ttk.Frame(params_tips_container, style="Modern.TFrame")
        params_container.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Título da seção de parâmetros
        ttk.Label(params_container, text="Parâmetros", style="Modern.TLabel").pack(
            anchor="w", padx=5, pady=(5, 0)
        )

        self.params_frame = ttk.Frame(params_container, style="Modern.TFrame")
        self.params_frame.pack(fill="x", padx=5, pady=(5, 5))

        # Frame para validação
        self.validation_frame = ttk.Frame(params_container, style="Modern.TFrame")
        self.validation_frame.pack(fill="x", pady=(0, 5), padx=5)

        # Frame para dicas da OLT (lado direito)
        self.tips_frame = ttk.Frame(params_tips_container, style="Modern.TFrame")
        self.tips_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Botões de ação
        btn_frame = ttk.Frame(self.right_panel, style="Modern.TFrame")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        btn_left = ttk.Frame(btn_frame, style="Modern.TFrame")
        btn_left.pack(side="left")

        ttk.Button(
            btn_left,
            text="Copiar",
            command=self.copy_command,
            style="Accent.TButton",
        ).pack(side="left", padx=2)

        ttk.Button(
            btn_left,
            text="Validar",
            command=self.validate_current_command,
            style="Accent.TButton",
        ).pack(side="left", padx=2)

        ttk.Button(
            btn_left,
            text="Favoritar",
            command=self.add_to_favorites,
            style="Accent.TButton",
        ).pack(side="left", padx=2)

        ttk.Button(
            btn_left,
            text="Ajuda",
            command=self.show_documentation,
            style="Accent.TButton",
        ).pack(side="left", padx=2)

        # Inicializar com o primeiro modelo selecionado após todos os componentes serem criados
        if self.available_olts:
            self.on_olt_selected()

    def show_documentation(self):
        """Mostrar janela de documentação"""
        self.create_documentation_view()

    def validate_current_command(self):
        """Validar comando atual"""
        if not hasattr(self, "param_entries"):
            messagebox.showinfo("Validação", "Nenhum parâmetro para validar.")
            return

        params = {}

        # Processar PON ID se existir
        if "pon_id" in self.param_entries:
            pon_id = self.param_entries["pon_id"].get().strip()
            if pon_id:
                try:
                    slot, porta, pon = pon_id.split("/")
                    params["slot"] = slot
                    params["porta"] = porta
                    params["pon"] = pon
                except ValueError:
                    errors = [
                        "PON ID deve estar no formato: slot/porta/pon (exemplo: 1/2/2)"
                    ]
                    # Mostrar erro
                    for widget in self.validation_frame.winfo_children():
                        widget.destroy()
                    label = ttk.Label(
                        self.validation_frame,
                        text=f"⚠️ {errors[0]}",
                        style="Error.TLabel",
                        foreground=self.themes[self.theme_var.get()]["error"],
                    )
                    label.pack(anchor="w", pady=2)
                    return

        # Adicionar outros parâmetros
        for param, entry in self.param_entries.items():
            if param != "pon_id":  # Ignorar o PON ID que já foi processado
                params[param] = entry.get()

        errors = self.validator.validate_params(params)

        # Limpar mensagens anteriores
        for widget in self.validation_frame.winfo_children():
            widget.destroy()

        if errors:
            for error in errors:
                label = ttk.Label(
                    self.validation_frame,
                    text=f"⚠️ {error}",
                    style="Error.TLabel",
                    foreground=self.themes[self.theme_var.get()]["error"],
                )
                label.pack(anchor="w", pady=2)
        else:
            label = ttk.Label(
                self.validation_frame,
                text="✅ Todos os parâmetros são válidos",
                style="Modern.TLabel",
                foreground="#51cf66",
            )
            label.pack(anchor="w", pady=2)

    def create_editor_interface(self):
        """Criar interface do editor de comandos"""
        editor_top = ttk.Frame(self.editor_frame, style="Modern.TFrame")
        editor_top.pack(fill="x", pady=(0, 10), padx=5)

        ttk.Label(editor_top, text="Editor de Comandos", style="Title.TLabel").pack(
            pady=10
        )

        # Botões de ação
        btn_frame = ttk.Frame(editor_top, style="Modern.TFrame")
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Salvar Alterações", command=self.save_data).pack(
            side="left", padx=5
        )
        ttk.Button(
            btn_frame,
            text="Recarregar",
            command=lambda: self.load_editor_data(show_message=True),
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame, text="Abrir Arquivo JSON", command=self.open_json_file
        ).pack(side="left", padx=5)

        # Área de edição
        editor_text_frame = ttk.Frame(self.editor_frame, style="Modern.TFrame")
        editor_text_frame.pack(fill="both", expand=True, padx=5)

        ttk.Label(
            editor_text_frame,
            text="Editar estrutura de comandos (JSON):",
            style="Modern.TLabel",
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.editor_text = scrolledtext.ScrolledText(
            editor_text_frame,
            wrap="word",
            bg=self.themes[self.theme_var.get()]["bg"],
            fg=self.themes[self.theme_var.get()]["text"],
            insertbackground=self.themes[self.theme_var.get()]["text"],
            font=("Consolas", 9),
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
        )
        self.editor_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Carregar dados no editor
        self.load_editor_data()

    def on_olt_selected(self, event=None):
        """Quando uma OLT é selecionada"""
        selected_olt = self.olt_var.get()
        if selected_olt:
            self.populate_tree(selected_olt)
            self.update_olt_tips(selected_olt)

    def update_olt_tips(self, olt_name):
        """Atualizar dicas específicas da OLT"""
        # Limpar dicas anteriores
        for widget in self.tips_frame.winfo_children():
            widget.destroy()

        # Obter dicas da OLT
        tips = self.documentation.get_olt_tips(olt_name)

        if tips:
            # Container principal centralizado verticalmente
            main_container = ttk.Frame(self.tips_frame, style="TFrame")
            main_container.pack(fill="both", expand=True, padx=5, pady=5)

            # Título das dicas
            ttk.Label(
                main_container,
                text="ℹ️ Dicas da OLT:",
                style="Modern.TLabel",
                font=("Segoe UI", 8, "italic"),
                foreground="gray"
            ).pack(anchor="w", pady=(0, 3))

            # Container para as dicas sem quebra de linha
            tips_container = ttk.Frame(main_container, style="TFrame")
            tips_container.pack(fill="both", expand=True)

            # Mostrar cada dica sem quebra de linha
            for tip in tips:
                tip_label = ttk.Label(
                    tips_container,
                    text=f"• {tip}",
                    style="Modern.TLabel",
                    font=("Segoe UI", 8),
                    foreground="gray60",
                    anchor="w"
                )
                tip_label.pack(fill="x", pady=1)

    def populate_tree(self, olt_name):
        """Popular a árvore com os comandos da OLT selecionada"""
        self.tree.delete(*self.tree.get_children())

        if olt_name not in self.data["olts"]:
            return

        olt_data = self.data["olts"][olt_name]

        for category, cat_data in olt_data["categories"].items():
            cat_id = self.tree.insert("", "end", text=category, open=True)
            self.populate_tree_recursive(cat_id, cat_data)

    def populate_tree_recursive(self, parent, data):
        """Popular árvore recursivamente"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    folder_id = self.tree.insert(
                        parent, "end", text=key, open=False
                    )
                    self.populate_tree_recursive(folder_id, value)
                else:
                    # Se o valor é uma lista, juntar com quebras de linha
                    if isinstance(value, list):
                        value = '\n'.join(value)
                    self.tree.insert(parent, "end", text=key, values=(value,))
        else:
            self.tree.insert(parent, "end", text=f"⚡ {data}", values=(data,))

    def on_tree_select(self, event=None):
        """Quando um item da árvore é selecionado"""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.tree.item(item, "values")

        if values:
            command = values[0]
            self.display_command(command)

    def display_command(self, command):
        """Exibir comando na área de texto"""

        # Verificar se é o conversor de ONUs
        if command == "CONVERTER_ONU_TOOL":
            self.open_onu_converter()
            return

        self.command_text.delete(1.0, tk.END)

        # Se o comando é uma lista (array), juntar com quebras de linha
        if isinstance(command, list):
            command = '\n'.join(command)

        # Inserir comando (multilinha ou simples)
        self.command_text.insert(tk.END, command)

        # Atualizar o status de favorito na interface (sem adicionar ícone ao texto)
        is_favorite = hasattr(self, "favorites") and self.favorites.is_favorite(command)
        if hasattr(self, "favorite_indicator"):
            self.favorite_indicator.configure(text="⭐ Favorito" if is_favorite else "")

        # Limpar parâmetros anteriores
        for widget in self.params_frame.winfo_children():
            widget.destroy()

        # Encontrar parâmetros no comando
        params = re.findall(r"\{(\w+)\}", command)
        if params:

            self.param_entries = {}
            unique_params = set(params)

            # Se temos slot, porta e pon, vamos tratá-los especialmente
            if all(p in unique_params for p in ["slot", "porta", "pon"]):
                param_frame = ttk.Frame(self.params_frame, style="Modern.TFrame")
                param_frame.pack(fill="x", pady=2)

                ttk.Label(
                    param_frame, text="PON ID:", style="Modern.TLabel", width=15
                ).pack(side="left")
                pon_id_entry = ttk.Entry(param_frame, width=20)
                pon_id_entry.pack(side="left", padx=(5, 0))
                pon_id_entry.bind(
                    "<KeyRelease>",
                    lambda e: self.update_command_preview_pon_id(pon_id_entry),
                )

                # Remover slot, porta e pon do conjunto de parâmetros restantes
                unique_params.remove("slot")
                unique_params.remove("porta")
                unique_params.remove("pon")

                # Guardar as três entradas juntas
                self.param_entries["pon_id"] = pon_id_entry

            # Processar os parâmetros restantes
            for param in unique_params:
                param_frame = ttk.Frame(self.params_frame, style="Modern.TFrame")
                param_frame.pack(fill="x", pady=2)

                ttk.Label(
                    param_frame, text=f"{param}:", style="Modern.TLabel", width=15
                ).pack(side="left")
                entry = ttk.Entry(param_frame, width=20)
                entry.pack(side="left", padx=(5, 0))

                # Bind events for this entry
                entry.bind(
                    "<KeyRelease>", lambda e, param=param: self.update_command_preview()
                )
                entry.bind(
                    "<FocusOut>", lambda e, param=param: self.update_command_preview()
                )
                entry.bind(
                    "<<Paste>>",
                    lambda e, param=param: self.root.after(
                        50, self.update_command_preview
                    ),
                )
                entry.bind(
                    "<<Cut>>",
                    lambda e, param=param: self.root.after(
                        50, self.update_command_preview
                    ),
                )

                # Criar combobox para seleção de ONU se for o parâmetro firmware
                if param == "firmware":
                    # Remover a entry atual que será substituída
                    entry.pack_forget()

                    # Frame para modelo de ONU
                    model_frame = ttk.Frame(self.params_frame, style="Modern.TFrame")
                    model_frame.pack(fill="x", pady=2)

                    # Label para modelo
                    ttk.Label(
                        model_frame, text="Modelo ONU:", style="Modern.TLabel", width=15
                    ).pack(side="left")

                    # Combobox para seleção do modelo
                    model_combo = ttk.Combobox(
                        model_frame,
                        values=["ZTE F601", "ONU FAST"],
                        state="readonly",
                        width=20,
                    )
                    model_combo.pack(side="left", padx=(5, 0))
                    model_combo.set("ZTE F601")  # Valor padrão

                    # Criar novo frame para o campo firmware
                    firmware_entry_frame = ttk.Frame(
                        self.params_frame, style="Modern.TFrame"
                    )
                    firmware_entry_frame.pack(fill="x", pady=2)

                    # Label e entry para firmware
                    ttk.Label(
                        firmware_entry_frame,
                        text=f"{param}:",
                        style="Modern.TLabel",
                        width=15,
                    ).pack(side="left")
                    firmware_entry = ttk.Entry(firmware_entry_frame, width=20)
                    firmware_entry.pack(side="left", padx=(5, 0))

                    # Função para atualizar o firmware baseado na seleção
                    def update_firmware(event=None):
                        selected = model_combo.get()
                        if selected == "ZTE F601":
                            firmware_entry.delete(0, tk.END)
                            firmware_entry.insert(0, "F601P1N34.bin")
                        elif selected == "ONU FAST":
                            firmware_entry.delete(0, tk.END)
                            firmware_entry.insert(0, "F10-G10-NW_1.6.0.bin")
                        self.update_command_preview()  # Atualizar preview quando o firmware mudar

                    # Vincular evento de seleção
                    model_combo.bind("<<ComboboxSelected>>", update_firmware)

                    # Definir valor inicial do firmware
                    update_firmware()

                    # Usar a entry de firmware ao invés da entry original
                    entry = firmware_entry

                # Adicionar a entry aos parâmetros
                self.param_entries[param] = entry

                # logging.debug(f"Comando exibido: {command}")

    def open_onu_converter(self):
        """Abrir interface do conversor de ONUs"""
        # Criar janela do conversor
        converter_window = tk.Toplevel(self.root)
        converter_window.title("🔧 Conversor para remoção em lote - ZTE Ullyses")
        converter_window.geometry("1000x600")
        converter_window.resizable(True, True)

        # Aplicar tema da janela principal
        theme = self.themes[self.theme_var.get()]
        converter_window.configure(bg=theme["bg"])

        # Frame principal
        main_frame = ttk.Frame(converter_window, style="Modern.TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        ttk.Label(
            main_frame,
            text="Conversor para remoção em lote - ZTE Ullyses",
            style="Title.TLabel",
        ).pack(pady=(0, 20))

        # Exemplo
        example_frame = ttk.Frame(main_frame, style="Card.TFrame")
        example_frame.pack(fill="x", pady=(0, 20))

        ttk.Label(
            example_frame, text="Exemplo de entrada:", style="Card.TLabel"
        ).pack(anchor="w", padx=15, pady=(10, 5))

        example_text = "gpon-onu_1/2/6:3\ngpon-onu_1/5/5:33\ngpon-onu_1/5/6:12"
        example_label = ttk.Label(
            example_frame,
            text=example_text,
            style="Modern.TLabel",
            font=("Consolas", 9),
        )
        example_label.pack(anchor="w", padx=15, pady=(0, 10))

        # Container com dois painéis
        container = ttk.Frame(main_frame, style="Modern.TFrame")
        container.pack(fill="both", expand=True)

        # Painel esquerdo - Entrada
        left_panel = ttk.Frame(container, style="Card.TFrame")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ttk.Label(
            left_panel, text="Cole as ONUs aqui:", style="Subtitle.TLabel"
        ).pack(anchor="w", padx=15, pady=(10, 5))

        input_text = scrolledtext.ScrolledText(
            left_panel, height=15, wrap="word", font=("Consolas", 10)
        )
        input_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Painel direito - Saída
        right_panel = ttk.Frame(container, style="Card.TFrame")
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

        ttk.Label(
            right_panel, text="Comandos convertidos:", style="Subtitle.TLabel"
        ).pack(anchor="w", padx=15, pady=(10, 5))

        output_text = scrolledtext.ScrolledText(
            right_panel, height=15, wrap="word", font=("Consolas", 10)
        )
        output_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Botões
        btn_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        btn_frame.pack(fill="x", pady=(20, 0))

        def convert_onus():
            """Converter ONUs para comandos"""
            input_content = input_text.get("1.0", tk.END).strip()
            if not input_content:
                output_text.delete("1.0", tk.END)
                return

            lines = input_content.split("\n")
            commands = ["configure terminal"]

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Regex para capturar: gpon-onu_1/2/6:3
                match = re.match(r"gpon-onu_(\d+)/(\d+)/(\d+):(\d+)", line)

                if match:
                    slot, card, port, onu = match.groups()
                    commands.append(f"interface gpon-olt_{slot}/{card}/{port}")
                    commands.append(f"no onu {onu}")
                    commands.append("exit")

            output_text.delete("1.0", tk.END)
            output_text.insert("1.0", "\n".join(commands))

        def copy_output():
            """Copiar resultado para clipboard"""
            output_content = output_text.get("1.0", tk.END).strip()
            if output_content:
                converter_window.clipboard_clear()
                converter_window.clipboard_append(output_content)
                messagebox.showinfo("Sucesso", "Comandos copiados para o clipboard!")

        def clear_all():
            """Limpar entrada e saída"""
            input_text.delete("1.0", tk.END)
            output_text.delete("1.0", tk.END)

        # Botões
        ttk.Button(
            btn_frame, text="Converter", command=convert_onus, style="Accent.TButton"
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame, text="Copiar", command=copy_output, style="Modern.TButton"
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame, text="Limpar", command=clear_all, style="Modern.TButton"
        ).pack(side="left", padx=5)

        # Converter automaticamente quando digitar
        input_text.bind("<KeyRelease>", lambda e: convert_onus())

        # Converter na carga inicial
        convert_onus()

        # Centralizar janela
        converter_window.update_idletasks()
        x = (converter_window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (converter_window.winfo_screenheight() // 2) - (600 // 2)
        converter_window.geometry(f"1000x600+{x}+{y}")

        # Focar na entrada
        input_text.focus_set()

    def copy_command(self):
        """Copiar comando para clipboard e adicionar ao histórico"""
        command = self.command_text.get(1.0, tk.END).strip()

        if command:
            self.root.clipboard_clear()
            self.root.clipboard_append(command)

            # Adicionar ao histórico
            self.history.add_command(
                command=command,
                olt_model=self.olt_var.get(),
                category=self.get_current_category(),
            )

            # Atualizar lista de histórico se estiver visível
            if hasattr(self, "history_list"):
                self.update_history_list()

    def copy_history_command(self):
        """Copiar comando selecionado do histórico"""
        selection = self.history_list.selection()
        if not selection:
            messagebox.showwarning(
                "Aviso", "Selecione um comando do histórico para copiar."
            )
            return

        item = selection[0]
        values = self.history_list.item(item)["values"]
        comando = values[1]  # O comando está na segunda coluna

        if comando:
            self.root.clipboard_clear()
            self.root.clipboard_append(comando)

    def copy_favorite_command(self):
        """Copiar comando selecionado dos favoritos"""
        selection = self.favorites_list.selection()
        if not selection:
            messagebox.showwarning(
                "Aviso", "Selecione um comando dos favoritos para copiar."
            )
            return

        item = selection[0]
        values = self.favorites_list.item(item)["values"]
        comando = values[1]  # O comando está na segunda coluna

        if comando:
            self.root.clipboard_clear()
            self.root.clipboard_append(comando)

    def search_in_data(self, data, olt_name, path, search_text, results):
        """Buscar recursivamente nos dados"""
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path} → {key}" if path else key
                self.search_in_data(value, olt_name, new_path, search_text, results)
        elif isinstance(data, str):
            if (
                not search_text
                or search_text in data.lower()
                or search_text in path.lower()
            ):
                results.append({"olt": olt_name, "path": path, "command": data})

    def on_result_select(self, event=None):
        """Quando um resultado é selecionado"""
        selection = self.results_listbox.curselection()
        if not selection:
            return

        result_text = self.results_listbox.get(selection[0])
        if "Nenhum comando encontrado" in result_text:
            return

        # Extrair comando do resultado
        try:
            command_part = result_text.split(" → ")[-1]
            command = command_part.replace("...", "")

            # Copiar para clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(command)
        except:
            pass

    def load_editor_data(self, show_message=False):
        """Carregar dados no editor"""
        try:
            # Ler o arquivo diretamente
            with open(self.data_file, "r", encoding="utf-8") as f:
                json_data = f.read()

            # Limpar editor e inserir novo conteúdo
            self.editor_text.delete(1.0, tk.END)
            self.editor_text.insert(1.0, json_data)

            # Atualizar dados em memória
            self.data = json.loads(json_data)

            # Atualizar interface
            self.populate_tree(
                self.olt_var.get()
                if self.olt_var.get()
                else next(iter(self.data["olts"]))
            )

            # Mostrar mensagem apenas se solicitado (ao clicar no botão recarregar)
            if show_message:
                messagebox.showinfo("Sucesso", "Dados recarregados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")

    def open_json_file(self):
        """Abrir arquivo JSON externo"""
        try:
            os.startfile(self.data_file)
        except:
            messagebox.showinfo(
                "Info", f"Arquivo JSON localizado em: {os.path.abspath(self.data_file)}"
            )

    def create_history_interface(self):
        """Criar interface do histórico de comandos"""
        # Frame principal
        frame = ttk.Frame(self.history_frame, style="Modern.TFrame")
        frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Frame superior com título e botões
        top_frame = ttk.Frame(frame, style="Modern.TFrame")
        top_frame.pack(fill="x", pady=(0, 10))

        # Título
        ttk.Label(top_frame, text="Histórico de Comandos", style="Title.TLabel").pack(
            side="left", pady=10
        )

        # Botões no topo
        btn_frame = ttk.Frame(top_frame, style="Modern.TFrame")
        btn_frame.pack(side="right", pady=10)

        ttk.Button(
            btn_frame,
            text="Copiar Comando",
            command=self.copy_history_command,
            style="Accent.TButton",
        ).pack(side="left", padx=2)

        ttk.Button(
            btn_frame,
            text="Limpar Histórico",
            command=self.clear_history,
            style="Modern.TButton",
        ).pack(side="left", padx=2)

        # Frame para a lista
        list_frame = ttk.Frame(frame, style="Modern.TFrame")
        list_frame.pack(fill="both", expand=True)

        # Lista de histórico com suporte a múltiplas linhas
        self.history_list = ttk.Treeview(
            list_frame,
            columns=("data", "comando", "olt"),
            show="headings",
            style="Modern.Treeview",
        )

        # Configurar colunas com tamanhos proporcionais
        list_frame.update_idletasks()
        total_width = (
            list_frame.winfo_width() - 20
        )  # Margem para evitar scrollbar horizontal
        if total_width <= 0:
            total_width = 800

        self.history_list.column("data", width=int(total_width * 0.2), stretch=True)
        self.history_list.column("comando", width=int(total_width * 0.6), stretch=True)
        self.history_list.column("olt", width=int(total_width * 0.2), stretch=True)

        self.history_list.heading("data", text="Data/Hora")
        self.history_list.heading("comando", text="Comando")
        self.history_list.heading("olt", text="OLT")

        # Apenas scrollbar horizontal para comandos longos
        x_scrollbar = ttk.Scrollbar(
            list_frame, orient="horizontal", command=self.history_list.xview
        )
        self.history_list.configure(xscrollcommand=x_scrollbar.set)

        # Empacotamento otimizado
        self.history_list.pack(side="top", fill="both", expand=True, padx=5)
        x_scrollbar.pack(side="bottom", fill="x", padx=5)

        # Eventos
        self.history_list.bind("<<TreeviewSelect>>", self.on_history_select)

        # Atualizar lista
        self.update_history_list()

    def clear_history(self):
        """Limpar todo o histórico de comandos"""
        confirm = messagebox.askyesno(
            "Confirmação", "Deseja realmente limpar todo o histórico?"
        )
        if confirm:
            self.history.clear_all()
            self.update_history_list()

    def create_favorites_interface(self):
        """Criar interface dos comandos favoritos"""
        # Frame principal
        frame = ttk.Frame(self.favorites_frame, style="Modern.TFrame")
        frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Frame superior com título e botões
        top_frame = ttk.Frame(frame, style="Modern.TFrame")
        top_frame.pack(fill="x", pady=(0, 10))

        # Título
        ttk.Label(top_frame, text="Comandos Favoritos", style="Title.TLabel").pack(
            side="left", pady=10
        )

        # Botões no topo
        btn_frame = ttk.Frame(top_frame, style="Modern.TFrame")
        btn_frame.pack(side="right", pady=10)

        ttk.Button(
            btn_frame,
            text="Copiar Comando",
            command=self.copy_favorite_command,
            style="Accent.TButton",
        ).pack(side="left", padx=2)

        ttk.Button(
            btn_frame,
            text="Adicionar",
            command=self.add_to_favorites,
            style="Modern.TButton",
        ).pack(side="left", padx=2)

        ttk.Button(
            btn_frame,
            text="Remover",
            command=self.remove_from_favorites,
            style="Modern.TButton",
        ).pack(side="left", padx=2)

        # Container frame para a lista
        list_container = ttk.Frame(frame, style="Modern.TFrame")
        list_container.pack(fill="both", expand=True)

        # Lista de favoritos com suporte a múltiplas linhas
        self.favorites_list = ttk.Treeview(
            list_container,
            columns=("nome", "comando", "olt"),
            show="headings",
            style="Modern.Treeview",
            height=12,
        )

        # Configurar colunas com tamanhos relativos e ajuste automático
        self.favorites_list.pack(fill="both", expand=True, padx=5)
        list_container.update_idletasks()  # Forçar atualização de geometria

        # Calcular larguras com base no container pai
        total_width = list_container.winfo_width() - 20  # Margem para evitar scrollbar
        if total_width <= 0:  # Fallback para largura inicial
            total_width = 800

        self.favorites_list.column("nome", width=int(total_width * 0.25), stretch=True)
        self.favorites_list.column(
            "comando", width=int(total_width * 0.55), stretch=True
        )
        self.favorites_list.column("olt", width=int(total_width * 0.20), stretch=True)

        self.favorites_list.heading("nome", text="Nome")
        self.favorites_list.heading("comando", text="Comando")
        self.favorites_list.heading("olt", text="OLT")

        # Eventos
        self.favorites_list.bind("<<TreeviewSelect>>", self.on_favorite_select)
        self.favorites_list.bind(
            "<Configure>", lambda e: self.adjust_favorites_columns(e)
        )

        # Atualizar lista
        self.update_favorites_list()

    def adjust_favorites_columns(self, event=None):
        """Ajustar largura das colunas da lista de favoritos"""
        if not hasattr(self, "favorites_list"):
            return

        # Obter largura atual do container
        total_width = self.favorites_list.winfo_width() - 20
        if total_width <= 0:
            return

        # Ajustar colunas proporcionalmente
        self.favorites_list.column("nome", width=int(total_width * 0.25))
        self.favorites_list.column("comando", width=int(total_width * 0.55))
        self.favorites_list.column("olt", width=int(total_width * 0.20))

    def update_history_list(self):
        """Atualizar lista de histórico"""
        # Limpar lista atual
        for item in self.history_list.get_children():
            self.history_list.delete(item)

        # Adicionar itens do histórico
        for entry in self.history.get_recent_commands():
            date = datetime.fromisoformat(entry["timestamp"]).strftime("%d/%m/%Y %H:%M")
            self.history_list.insert(
                "", 0, values=(date, entry["command"], entry["olt_model"])
            )

    def update_favorites_list(self):
        """Atualizar lista de favoritos"""
        # Limpar lista atual
        for item in self.favorites_list.get_children():
            self.favorites_list.delete(item)

        # Definir altura da linha baseada no conteúdo maior
        line_height = 20  # Altura base em pixels

        # Adicionar favoritos
        for fav in self.favorites.favorites:
            # Criar uma versão do comando com os parâmetros preenchidos
            command = fav["command"]
            if "params" in fav:
                for param, value in fav["params"].items():
                    command = command.replace(f"{{{param}}}", value)

            # Quebrar linhas longas do comando para melhor visualização
            wrapped_command = "\n".join(textwrap.wrap(command, width=80))

            # Calcular altura necessária para o item baseado no número de linhas
            num_lines = len(wrapped_command.split("\n"))
            height = max(line_height, line_height * num_lines)

            # Inserir item com altura ajustada
            item = self.favorites_list.insert(
                "", "end", values=(fav["name"], wrapped_command, fav["olt_model"])
            )
            self.favorites_list.item(item, tags=(str(height),))

    def add_to_favorites(self):
        """Adicionar comando atual aos favoritos"""
        command = self.command_text.get(1.0, tk.END).strip()
        if not command:
            messagebox.showwarning(
                "Aviso", "Selecione um comando para adicionar aos favoritos."
            )
            return

        # Pedir nome para o favorito
        name = self.ask_favorite_name()
        if not name:
            return

        # Coletar parâmetros preenchidos se existirem
        params = {}
        if hasattr(self, "param_entries"):
            params = {
                param: entry.get()
                for param, entry in self.param_entries.items()
                if entry.get()
            }

        # Adicionar aos favoritos
        self.favorites.add_favorite(
            command=command,
            name=name,
            olt_model=self.olt_var.get(),
            category=self.get_current_category(),
            params=params,
        )

        # Atualizar lista
        self.update_favorites_list()
        messagebox.showinfo("Sucesso", "Comando adicionado aos favoritos!")

    def remove_from_favorites(self):
        """Remover comando dos favoritos"""
        selection = self.favorites_list.selection()
        if not selection:
            messagebox.showwarning(
                "Aviso", "Selecione um comando para remover dos favoritos."
            )
            return

        if messagebox.askyesno(
            "Confirmar", "Deseja remover este comando dos favoritos?"
        ):
            item = selection[0]
            values = self.favorites_list.item(item)["values"]
            name = values[0]

            # Encontrar e remover o comando
            for fav in self.favorites.favorites:
                if fav["name"] == name:
                    self.favorites.remove_favorite(fav["command"])
                    break

            # Atualizar lista
            self.update_favorites_list()
            messagebox.showinfo("Sucesso", "Comando removido dos favoritos!")

    def ask_favorite_name(self):
        """Pedir nome para o comando favorito"""
        return simpledialog.askstring(
            "Nome do Favorito", "Digite um nome para identificar este comando:"
        )

    def get_current_category(self):
        """Obter categoria do comando atual"""
        selection = self.tree.selection()
        if not selection:
            return "Geral"

        item = selection[0]
        path = []
        while item:
            text = self.tree.item(item)["text"]
            path.insert(0, text)
            item = self.tree.parent(item)

        return " > ".join(path) if path else "Geral"

    def on_history_select(self, event):
        """Quando um item do histórico é selecionado"""
        selection = self.history_list.selection()
        if not selection:
            return

        item = selection[0]
        values = self.history_list.item(item)["values"]
        date = values[0]

        # Encontrar o comando no histórico
        for entry in self.history.history:
            entry_date = datetime.fromisoformat(entry["timestamp"]).strftime(
                "%d/%m/%Y %H:%M"
            )
            if entry_date == date:
                self.display_command(entry["command"])
                break

    def on_favorite_select(self, event):
        """Quando um favorito é selecionado"""
        selection = self.favorites_list.selection()
        if not selection:
            return

        item = selection[0]
        values = self.favorites_list.item(item)["values"]
        name = values[0]

        # Encontrar o comando nos favoritos
        for fav in self.favorites.favorites:
            if fav["name"] == name:
                # Exibir o comando
                self.display_command(fav["command"])

                # Extrair parâmetros do comando
                params = set(re.findall(r"\{(\w+)\}", fav["command"]))

                # Se existem parâmetros, criar ou atualizar a interface
                if params:
                    # Criar frame para parâmetros se não existir
                    if (
                        not hasattr(self, "params_frame")
                        or not self.params_frame.winfo_exists()
                    ):
                        self.params_frame = ttk.Frame(
                            self.favorites_frame,
                            style="Modern.TFrame",
                        )
                        self.params_frame.pack(fill="x", padx=10, pady=(0, 10))
                        self.param_entries = {}

                    # Limpar parâmetros anteriores
                    for widget in self.params_frame.winfo_children():
                        widget.destroy()

                    # Criar campos para cada parâmetro
                    for param in params:
                        frame = ttk.Frame(self.params_frame, style="Modern.TFrame")
                        frame.pack(fill="x", padx=5, pady=2)

                        ttk.Label(frame, text=f"{param}:", style="Modern.TLabel").pack(
                            side="left", padx=(0, 5)
                        )
                        entry = ttk.Entry(frame)
                        entry.pack(side="left", fill="x", expand=True)

                        # Salvar referência e adicionar validação
                        self.param_entries[param] = entry
                        entry.bind("<KeyRelease>", self.update_command_preview)

                        # Preencher valor salvo se existir
                        if "params" in fav and param in fav["params"]:
                            entry.insert(0, fav["params"][param])

                    # Atualizar preview com os parâmetros
                    self.update_command_preview()
                break

    def create_documentation_view(self):
        """Criar janela de documentação"""
        doc_window = tk.Toplevel(self.root)
        doc_window.title("Documentação do Comando")
        doc_window.geometry("600x400")

        style = ttk.Style()
        theme = self.themes[self.theme_var.get()]

        # Frame principal
        main_frame = ttk.Frame(doc_window, style="Modern.TFrame")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Título
        ttk.Label(main_frame, text="📚 Documentação", style="Title.TLabel").pack(
            pady=(0, 10)
        )

        # Notebook para diferentes seções
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)

        # Aba de parâmetros
        params_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(params_frame, text="Parâmetros")

        for param, desc in self.documentation.docs.items():
            param_label = ttk.Label(
                params_frame,
                text=f"{param}: {desc}",
                style="Modern.TLabel",
                wraplength=500,
            )
            param_label.pack(anchor="w", padx=10, pady=5)

        # Aba de exemplos
        examples_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(examples_frame, text="Exemplos")

        current_command = self.command_text.get(1.0, tk.END).strip()
        example = self.documentation.get_command_example(current_command)

        if example:
            ttk.Label(
                examples_frame,
                text=f"Descrição: {example['desc']}",
                style="Modern.TLabel",
                wraplength=500,
            ).pack(anchor="w", padx=10, pady=5)

            ttk.Label(
                examples_frame,
                text=f"Exemplo: {example['example']}",
                style="Modern.TLabel",
                wraplength=500,
            ).pack(anchor="w", padx=10, pady=5)
        else:
            ttk.Label(
                examples_frame,
                text="Nenhum exemplo disponível para este comando.",
                style="Modern.TLabel",
            ).pack(anchor="w", padx=10, pady=5)

        # Aba de problemas comuns
        issues_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(issues_frame, text="Problemas Comuns")

        issues = self.documentation.get_common_issues(current_command)
        if issues:
            for issue in issues:
                ttk.Label(
                    issues_frame,
                    text=f"• {issue}",
                    style="Modern.TLabel",
                    wraplength=500,
                ).pack(anchor="w", padx=10, pady=5)
        else:
            ttk.Label(
                issues_frame,
                text="Nenhum problema comum documentado para este comando.",
                style="Modern.TLabel",
            ).pack(anchor="w", padx=10, pady=5)

    def update_command_preview(self):
        """Atualizar preview do comando com validação"""
        if not hasattr(self, "param_entries"):
            return

        # Recuperar o comando original da última seleção na árvore
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            if values:
                original_command = values[0]
            else:
                original_command = self.command_text.get(1.0, tk.END).strip()
        else:
            original_command = self.command_text.get(1.0, tk.END).strip()

        command = original_command
        params = {}

        # Processar PON ID primeiro se existir
        if "pon_id" in self.param_entries:
            pon_id = self.param_entries["pon_id"].get().strip()
            if pon_id:
                try:
                    slot, porta, pon = pon_id.split("/")
                    params["slot"] = slot
                    params["porta"] = porta
                    params["pon"] = pon
                except ValueError:
                    pass  # PON ID inválido, manter placeholders

        # Processar outros parâmetros
        for param, entry in self.param_entries.items():
            if param != "pon_id":  # Ignorar pon_id que já foi processado
                value = entry.get().strip()
                if value:
                    params[param] = value

        # Validar parâmetros não vazios
        non_empty_params = {k: v for k, v in params.items() if v}
        errors = (
            self.validator.validate_params(non_empty_params) if non_empty_params else []
        )

        # Limpar marcações de erro anteriores
        for entry in self.param_entries.values():
            entry.configure(style="TEntry")

        # Limpar mensagens de validação anteriores
        for widget in self.validation_frame.winfo_children():
            widget.destroy()

        # Mostrar feedback de validação
        if errors:
            for error in errors:
                param = error.split()[2]  # Extrair nome do parâmetro
                if param in self.param_entries:
                    self.param_entries[param].configure(style="Error.TEntry")

                label = ttk.Label(
                    self.validation_frame,
                    text=f"⚠️ {error}",
                    style="Error.TLabel",
                    foreground=self.themes[self.theme_var.get()]["error"],
                )
                label.pack(anchor="w", pady=2)
        else:
            # Mostrar feedback positivo se houver parâmetros preenchidos e válidos
            if non_empty_params:
                label = ttk.Label(
                    self.validation_frame,
                    text="✅ Parâmetros válidos",
                    style="Modern.TLabel",
                    foreground=self.themes[self.theme_var.get()]["success"],
                )
                label.pack(anchor="w", pady=2)

        # Substituir parâmetros na ordem específica
        param_order = ["firmware", "slot", "porta", "pon", "id", "sn", "mac", "index"]

        # Primeiro substituir parâmetros na ordem definida
        for param in param_order:
            if param in params:
                value = params[param]
                if value:
                    placeholder = f"{{{param}}}"
                    command = command.replace(placeholder, value)

        # Depois substituir quaisquer outros parâmetros que possam existir
        for param, value in params.items():
            if param not in param_order and value:
                placeholder = f"{{{param}}}"
                command = command.replace(placeholder, value)

        # Atualizar texto
        self.command_text.delete(1.0, tk.END)
        self.command_text.insert(1.0, command)

    def update_command_preview_pon_id(self, pon_id_entry):
        """Atualizar preview do comando quando o PON ID é alterado"""
        if not hasattr(self, "param_entries"):
            return

        # Recuperar o comando original da última seleção na árvore
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            if values:
                command = values[0]
            else:
                command = self.command_text.get(1.0, tk.END).strip()
        else:
            command = self.command_text.get(1.0, tk.END).strip()

        params = {}
        pon_id_valid = False

        # Processar o PON ID
        pon_id = pon_id_entry.get().strip()
        if pon_id:
            try:
                slot, porta, pon = pon_id.split("/")
                # Validar os valores do PON ID
                if (
                    re.match(r"^\d{1,2}$", slot)
                    and re.match(r"^\d{1,2}$", porta)
                    and re.match(r"^\d{1,2}$", pon)
                ):
                    params["slot"] = slot
                    params["porta"] = porta
                    params["pon"] = pon
                    pon_id_valid = True
            except ValueError:
                # Se o formato estiver incorreto, manter os placeholders
                pass

        # Adicionar outros parâmetros
        for param, entry in self.param_entries.items():
            if param != "pon_id":  # Ignorar o PON ID que já foi processado
                value = entry.get().strip()
                if value:
                    params[param] = value

        # Limpar mensagens anteriores
        for widget in self.validation_frame.winfo_children():
            widget.destroy()

        # Mostrar feedback de validação para PON ID
        if pon_id and not pon_id_valid:
            pon_id_entry.configure(style="Error.TEntry")
            label = ttk.Label(
                self.validation_frame,
                text="⚠️ PON ID deve estar no formato: slot/porta/pon (exemplo: 1/2/2)",
                style="Error.TLabel",
                foreground="#ff6b6b",
            )
            label.pack(anchor="w", pady=2)
        elif pon_id and pon_id_valid:
            pon_id_entry.configure(style="TEntry")
            label = ttk.Label(
                self.validation_frame,
                text="✅ PON ID válido",
                style="Modern.TLabel",
                foreground="#51cf66",
            )
            label.pack(anchor="w", pady=2)
        else:
            pon_id_entry.configure(style="TEntry")

        # Validar outros parâmetros
        non_empty_params = {k: v for k, v in params.items() if v}
        if non_empty_params:
            errors = self.validator.validate_params(non_empty_params)
            if errors:
                for error in errors:
                    label = ttk.Label(
                        self.validation_frame,
                        text=f"⚠️ {error}",
                        style="Error.TLabel",
                        foreground=self.themes[self.theme_var.get()]["error"],
                    )
                    label.pack(anchor="w", pady=2)

        # Substituir parâmetros
        for param, value in params.items():
            if value:  # Substituir apenas se tiver valor
                placeholder = f"{{{param}}}"
                command = command.replace(placeholder, value)

        # Atualizar texto
        self.command_text.delete(1.0, tk.END)
        self.command_text.insert(1.0, command)

        # Realizar validação
        if hasattr(self, "validator"):
            errors = self.validator.validate_params(
                {k: v for k, v in params.items() if v}
            )

            # Limpar mensagens anteriores
            for widget in self.validation_frame.winfo_children():
                widget.destroy()

            if errors:
                for error in errors:
                    label = ttk.Label(
                        self.validation_frame,
                        text=f"⚠️ {error}",
                        style="Error.TLabel",
                        foreground=self.themes[self.theme_var.get()]["error"],
                    )
                    label.pack(anchor="w", pady=2)

    def save_preferences(self):
        """Salvar preferências de tema e posição da janela"""
        try:
            # Get current window geometry
            geometry = self.root.geometry()

            # Parse geometry string to validate
            try:
                wh, xy = geometry.split("+", 1)
                w, h = map(int, wh.split("x"))
                x, y = map(int, xy.split("+"))

                # Get screen dimensions
                screen_w = self.root.winfo_screenwidth()
                screen_h = self.root.winfo_screenheight()

                # If window is off screen, use default position
                if x > screen_w - 100 or y > screen_h - 100:
                    geometry = "1200x800+100+100"
            except:
                geometry = "1200x800+100+100"

            # Get current theme
            theme = self.theme_var.get()
            if theme not in ["light", "dark"]:
                theme = "light"

            # Get current sidebar position
            sidebar_position = self.get_sidebar_position()

            preferences = {"theme": theme, "window_position": geometry, "sidebar_position": sidebar_position}

            # Ensure config directory exists
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)

            # Save preferences
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(preferences, f, indent=2)

        except Exception as e:
            print(f"Error saving preferences: {e}")

    def save_sidebar_position(self, event=None):
        """Salvar posição da barra lateral quando movida"""
        try:
            self.root.after(500, self.save_preferences)  # Salvar após 500ms para evitar salvamentos excessivos
        except Exception as e:
            print(f"Error scheduling sidebar position save: {e}")

    def get_sidebar_position(self):
        """Obter posição atual da barra lateral"""
        try:
            if hasattr(self, 'content_frame') and self.content_frame.winfo_exists():
                # Para tk.PanedWindow, podemos obter a posição da sash
                sash_pos = self.content_frame.sash_coord(0)
                if sash_pos:
                    return sash_pos[0]  # Retorna a coordenada X da sash
        except Exception as e:
            print(f"Error getting sidebar position: {e}")
        return None

    def set_sidebar_position(self, position):
        """Definir posição da barra lateral"""
        try:
            if hasattr(self, 'content_frame') and self.content_frame.winfo_exists() and position is not None:
                # Para tk.PanedWindow, podemos definir a posição da sash
                self.content_frame.sash_place(0, position, 0)
        except Exception as e:
            print(f"Error setting sidebar position: {e}")

    def load_preferences(self):
        """Carregar preferências de tema e posição da janela"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    preferences = json.load(f)

                # Set theme with fallback
                theme = preferences.get("theme", "light")
                if theme not in ["light", "dark"]:
                    theme = "light"
                self.theme_var.set(theme)

                # Set window position with validation
                default_geometry = "1200x800+100+100"
                geometry = preferences.get("window_position", default_geometry)
                try:
                    # Parse geometry string
                    wh, xy = geometry.split("+", 1)
                    w, h = map(int, wh.split("x"))
                    x, y = map(int, xy.split("+"))

                    # Get screen dimensions
                    screen_w = self.root.winfo_screenwidth()
                    screen_h = self.root.winfo_screenheight()

                    # Validate within screen bounds
                    if (
                        100 <= w <= screen_w
                        and 100 <= h <= screen_h
                        and 0 <= x <= screen_w - 100
                        and 0 <= y <= screen_h - 100
                    ):
                        self.root.geometry(geometry)
                    else:
                        self.root.geometry(default_geometry)
                except:
                    self.root.geometry(default_geometry)

                # Set sidebar position
                sidebar_position = preferences.get("sidebar_position")
                if sidebar_position is not None:
                    self.sidebar_position_to_restore = sidebar_position

                # Apply theme after geometry is set
                self.apply_theme()

                # Restore sidebar position after theme is applied
                if hasattr(self, 'sidebar_position_to_restore'):
                    self.root.after(100, lambda: self.set_sidebar_position(self.sidebar_position_to_restore))
        except Exception as e:
            print(f"Error loading preferences: {e}")
            # Set defaults
            self.theme_var.set("light")
            self.root.geometry("1200x800+100+100")
            self.apply_theme()

    def on_closing(self):
        """Evento ao fechar o programa"""
        self.save_preferences()
        self.root.destroy()


def main():
    """Função principal"""
    root = tk.Tk()
    app = OLTCommandManager(root)

    # Centralizar janela
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()
