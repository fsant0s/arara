#!/usr/bin/env python3
"""
Script para gerar automaticamente entradas no CHANGELOG.md a partir dos commits do Git.
Baseia-se em conventional commits para categorizar as alterações.
"""

import os
import re
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def get_current_version() -> str:
    """Lê a versão atual do projeto a partir do pyproject.toml."""
    with open("pyproject.toml", "r") as f:
        content = f.read()
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if match:
            return match.group(1)
        else:
            return "0.0.0"  # Versão padrão se não encontrada


def get_latest_tag() -> Optional[str]:
    """Obtém a tag mais recente do repositório Git."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except subprocess.SubprocessError:
        return None


def get_commits_since_tag(tag: Optional[str]) -> List[str]:
    """Obtém todos os commits desde a tag especificada."""
    cmd = ["git", "log", "--pretty=format:%s|%h|%an|%ad", "--date=short"]
    if tag:
        cmd.append(f"{tag}..HEAD")

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip().split("\n") if result.stdout.strip() else []


def categorize_commits(commits: List[str]) -> Dict[str, List[str]]:
    """Categoriza os commits seguindo o padrão de conventional commits."""
    categories = {
        "feat": {"title": "Adicionado", "items": []},
        "fix": {"title": "Corrigido", "items": []},
        "docs": {"title": "Documentação", "items": []},
        "style": {"title": "Estilo", "items": []},
        "refactor": {"title": "Refatoração", "items": []},
        "perf": {"title": "Performance", "items": []},
        "test": {"title": "Testes", "items": []},
        "build": {"title": "Build", "items": []},
        "ci": {"title": "CI", "items": []},
        "chore": {"title": "Manutenção", "items": []},
        "revert": {"title": "Revertido", "items": []},
        "security": {"title": "Segurança", "items": []},
        "other": {"title": "Outros", "items": []},
    }

    for commit in commits:
        if not commit:
            continue

        parts = commit.split("|")
        if len(parts) < 2:
            continue

        message, hash_id = parts[0], parts[1]
        
        # Ignora commits de merge
        if message.startswith("Merge"):
            continue

        # Extrai tipo do commit (feat, fix, etc.)
        match = re.match(r'^(\w+)(\(.*\))?!?:', message)
        
        if match:
            commit_type = match.group(1)
            scope = match.group(2) if match.group(2) else ""
            
            # Remove os parênteses do escopo se existir
            if scope:
                scope = scope[1:-1]  # Remove ( e )
                formatted_message = f"{message[match.end():].strip()} [{scope}]"
            else:
                formatted_message = message[match.end():].strip()
            
            # Adiciona link para o commit
            entry = f"{formatted_message} ([{hash_id[:7]}](https://github.com/fsant0s/neuron/commit/{hash_id}))"
            
            if commit_type in categories:
                categories[commit_type]["items"].append(entry)
            else:
                categories["other"]["items"].append(entry)
        else:
            # Commits que não seguem o padrão
            entry = f"{message} ([{hash_id[:7]}](https://github.com/fsant0s/neuron/commit/{hash_id}))"
            categories["other"]["items"].append(entry)

    return categories


def generate_changelog_entry(version: str, categories: Dict[str, Dict]) -> str:
    """Gera a entrada do changelog para a versão especificada."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    lines = [f"## [{version}] - {today}\n"]
    
    for category, data in categories.items():
        if data["items"]:
            lines.append(f"### {data['title']}")
            for item in data["items"]:
                lines.append(f"- {item}")
            lines.append("")  # Linha em branco
    
    return "\n".join(lines)


def update_changelog(new_entry: str) -> None:
    """Atualiza o arquivo CHANGELOG.md com a nova entrada."""
    changelog_path = "CHANGELOG.md"
    
    if not os.path.exists(changelog_path):
        # Cria um novo arquivo CHANGELOG se não existir
        with open(changelog_path, "w") as f:
            f.write("# Changelog\n\n")
            f.write("Todas as mudanças notáveis no projeto NEURON serão documentadas neste arquivo.\n\n")
            f.write("O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),\n")
            f.write("e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).\n\n")
            f.write(new_entry)
        return
    
    with open(changelog_path, "r") as f:
        content = f.read()
    
    # Encontra onde inserir a nova entrada (após o cabeçalho)
    unreleased_match = re.search(r"## \[Não lançado\]", content)
    first_version_match = re.search(r"## \[\d+\.\d+\.\d+\]", content)
    
    if unreleased_match:
        # Insere após a seção "Não lançado"
        unreleased_section_end = content.find("\n\n", unreleased_match.end())
        if unreleased_section_end == -1:
            # Se não encontrar o fim da seção, usa o início da próxima versão
            if first_version_match:
                insertion_point = first_version_match.start()
            else:
                insertion_point = len(content)
        else:
            insertion_point = unreleased_section_end + 2
        
        new_content = content[:insertion_point] + new_entry + "\n" + content[insertion_point:]
    elif first_version_match:
        # Insere antes da primeira versão
        new_content = content[:first_version_match.start()] + new_entry + "\n" + content[first_version_match.start():]
    else:
        # Adiciona ao final
        new_content = content + "\n" + new_entry
    
    with open(changelog_path, "w") as f:
        f.write(new_content)


def main() -> None:
    """Função principal."""
    version = get_current_version()
    latest_tag = get_latest_tag()
    
    print(f"Gerando changelog para a versão {version}...")
    if latest_tag:
        print(f"Commits desde a tag {latest_tag}")
    else:
        print("Analisando todos os commits (nenhuma tag encontrada)")
    
    commits = get_commits_since_tag(latest_tag)
    
    if not commits or (len(commits) == 1 and not commits[0]):
        print("Nenhum commit encontrado para incluir no changelog.")
        return
    
    categories = categorize_commits(commits)
    
    # Conta o número total de entradas
    total_entries = sum(len(data["items"]) for data in categories.values())
    
    if total_entries == 0:
        print("Nenhuma entrada para adicionar ao changelog.")
        return
    
    print(f"Encontradas {total_entries} entradas para o changelog.")
    
    changelog_entry = generate_changelog_entry(version, categories)
    update_changelog(changelog_entry)
    
    print(f"Changelog atualizado com sucesso para a versão {version}!")


if __name__ == "__main__":
    main() 