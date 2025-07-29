# 🌐 OLT Command Manager

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

*Interface gráfica moderna para gerenciamento de comandos de equipamentos OLT*

[Funcionalidades](#-funcionalidades) • [Instalação](#-instalação) • [Como Usar](#-como-usar) • [Contribuir](#-contribuindo)

</div>

---

## 📋 Sobre o Projeto

O **OLT Command Manager** é uma aplicação desktop desenvolvida em Python que facilita o gerenciamento e execução de comandos para equipamentos OLT (Optical Line Terminal) de diferentes fabricantes. Com uma interface moderna e intuitiva, o programa oferece uma solução completa para técnicos e engenheiros de telecomunicações.

### 🎯 Problema Resolvido

- **Complexidade de comandos**: Diferentes fabricantes (ZTE, Huawei, Fiberhome) possuem sintaxes distintas
- **Produtividade**: Reduz tempo de busca e digitação de comandos
- **Padronização**: Centraliza comandos em uma interface única
- **Histórico**: Mantém registro dos comandos utilizados
- **Validação**: Previne erros através de validação de parâmetros

## ✨ Funcionalidades

### 🔧 Gerenciamento de Comandos
- **Navegação em árvore** organizada por categorias
- **Busca inteligente** de comandos
- **Preenchimento automático** de parâmetros
- **Validação em tempo real** de entrada de dados
- **Preview dinâmico** do comando final

### 📊 Organizacional
- **Histórico completo** de comandos utilizados
- **Sistema de favoritos** para comandos frequentes
- **Editor JSON integrado** para personalização
- **Exportação/importação** de configurações

### 🎨 Interface
- **Tema claro/escuro** alternável
- **Design moderno** e responsivo


## 🏭 Equipamentos Suportados em modelo padrão

| Fabricante | Modelo | Descrição |
|------------|---------|-----------|
| **ZTE** | C600 (Itaum) | ZXA10 C600 |
| **ZTE** | C300 (Ullyses) | C300 Series |
| **Huawei** | MA5800 Series |
| **Fiberhome** | AN5516 | Sistema VR3.2 |

## 🚀 Instalação

### Pré-requisitos
- Python 3.7 ou superior
- Sistema operacional: Windows, Linux ou macOS

### Método 1: Executável (Recomendado)
1. Baixe o executável da [página de releases](../../releases)
2. Execute `olt_manager.exe`
3. Pronto! Não é necessária instalação adicional

### Método 2: Código Fonte
```bash
# Clone o repositório
git clone https://github.com/SeuUsuario/olt-command-manager.git

# Entre no diretório
cd olt-command-manager

# Instale as dependências (se necessário)
pip install -r requirements.txt

# Execute o programa
python olt_manager.py
```

## 📖 Como Usar

### 1. Primeira Execução
- Selecione o modelo da OLT no dropdown superior
- Navegue pela árvore de comandos organizados por categoria
- Os comandos aparecerão na área de texto à direita

### 2. Preenchendo Parâmetros
- Campos de parâmetros aparecem automaticamente
- **PON ID**: Use o formato `slot/porta/pon` (ex: `1/2/6`)
- **Serial Number**: 8-16 caracteres alfanuméricos
- **ID da ONU**: Número de 1-128

### 3. Validação e Cópia
```
✅ Parâmetros válidos    ⚠️ Formato inválido para sn
```
- Clique em **"Copiar"** para enviar para clipboard
- Use **"Validar"** para verificar parâmetros
- Acesse **"Ajuda"** para documentação

### 4. Organizando Comandos
- **Favoritos**: Salve comandos frequentes com parâmetros
- **Histórico**: Acesse comandos utilizados recentemente
- **Editor**: Personalize a estrutura de comandos (JSON)

## 🛠️ Estrutura do Projeto

```
olt-command-manager/
├── 📁 src/
│   ├── olt_manager.py          # Aplicação principal
│   ├── olt_commands.json       # Base de dados dos comandos
│   └── requirements.txt        # Dependências Python
├── 📁 extras/
│   ├── ico.ico                 # Ícone da aplicação
├── 📁 build/
│   └── executables/           # Arquivos compilados
├── README.md
├── LICENSE
└── .gitignore
```

## 🔧 Configuração Avançada

### Personalizando Comandos
O arquivo `olt_commands.json` pode ser editado para:
- Adicionar novos equipamentos
- Modificar comandos existentes  
- Criar categorias personalizadas
- Ajustar parâmetros de validação

Exemplo:
```json
{
  "olts": {
    "Novo OLT": {
      "description": "Descrição do equipamento",
      "categories": {
        "Nova Categoria": {
          "Novo Comando": "comando {parametro}"
        }
      }
    }
  }
}
```

### Temas Personalizados
Modifique as cores no código para criar temas personalizados:
```python
"custom_theme": {
    "bg": "#seu_fundo",
    "accent": "#sua_cor_destaque",
    "text": "#sua_cor_texto"
}
```


## 🔍 Casos de Uso

### Para Técnicos de Campo
- Consulta rápida de comandos durante manutenção
- Validação de parâmetros antes da execução
- Histórico para rastreamento de ações

### Para NOC/Monitoramento
- Padronização de procedimentos
- Redução de erros operacionais
- Agilidade em troubleshooting

### Para Integradores
- Base de conhecimento centralizada
- Treinamento de equipes
- Documentação de processos


### Tipos de Contribuição
- 🐛 Correção de bugs
- ✨ Novas funcionalidades
- 📝 Melhorias na documentação
- 🎨 Aprimoramentos na interface
- 🔧 Adição de novos equipamentos

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

**Dreamer*


---

<div align="center">

**⭐ Se este projeto te ajudou, considere dar uma estrela!**

</div>
