#!/usr/bin/env python3
"""
Script para incrementar a versão do projeto seguindo o padrão de Semantic Versioning.
Atualiza a versão no arquivo pyproject.toml e opcionalmente gera uma tag Git.
"""

import argparse
import re
import subprocess
import sys
from typing import Tuple, Optional


def get_current_version() -> str:
    """Lê a versão atual do projeto a partir do pyproject.toml."""
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
            match = re.search(r'version\s*=\s*"([^"]+)"', content)
            if match:
                return match.group(1)
            else:
                print("Erro: Não foi possível encontrar a versão no arquivo pyproject.toml.")
                sys.exit(1)
    except FileNotFoundError:
        print("Erro: O arquivo pyproject.toml não foi encontrado.")
        sys.exit(1)


def bump_version(current_version: str, part: str) -> str:
    """
    Incrementa uma parte específica da versão.
    
    Args:
        current_version: A versão atual no formato x.y.z
        part: A parte a incrementar ('major', 'minor', ou 'patch')
    
    Returns:
        A nova versão
    """
    # Verifica se a versão atual está no formato correto
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$", current_version)
    if not match:
        print(f"Erro: Formato de versão inválido: {current_version}")
        sys.exit(1)
    
    major, minor, patch = map(int, match.groups()[:3])
    prerelease = match.group(4)
    build = match.group(5)
    
    # Incrementa a parte especificada
    if part == "major":
        major += 1
        minor = 0
        patch = 0
        prerelease = None
    elif part == "minor":
        minor += 1
        patch = 0
        prerelease = None
    elif part == "patch":
        patch += 1
        prerelease = None
    elif part.startswith("pre"):
        # Incrementa a versão pre-release (alpha, beta, rc, etc)
        pre_type = part[4:]  # alpha, beta, rc
        if not prerelease or not prerelease.startswith(pre_type):
            prerelease = f"{pre_type}.1"
        else:
            pre_parts = prerelease.split(".")
            if len(pre_parts) >= 2 and pre_parts[-1].isdigit():
                pre_num = int(pre_parts[-1]) + 1
                prerelease = f"{pre_type}.{pre_num}"
            else:
                prerelease = f"{pre_type}.1"
    else:
        print(f"Erro: Parte de versão inválida: {part}")
        print("Valores válidos: major, minor, patch, prealpha, prebeta, prerc")
        sys.exit(1)
    
    # Monta a nova versão
    new_version = f"{major}.{minor}.{patch}"
    if prerelease:
        new_version += f"-{prerelease}"
    if build:
        new_version += f"+{build}"
    
    return new_version


def update_version_in_files(new_version: str) -> None:
    """Atualiza a versão no arquivo pyproject.toml."""
    # Atualiza pyproject.toml
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
        
        updated_content = re.sub(
            r'(version\s*=\s*)"[^"]+"',
            f'\\1"{new_version}"',
            content
        )
        
        with open("pyproject.toml", "w") as f:
            f.write(updated_content)
        
        print(f"Arquivo pyproject.toml atualizado com a versão {new_version}")
    except Exception as e:
        print(f"Erro ao atualizar a versão no arquivo pyproject.toml: {e}")
        sys.exit(1)


def create_git_tag(version: str) -> None:
    """Cria uma tag Git para a versão."""
    tag_name = f"v{version}"
    try:
        # Adiciona os arquivos modificados
        subprocess.run(["git", "add", "pyproject.toml"], check=True)
        
        # Cria o commit
        commit_message = f"release: bump version to {tag_name}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Cria a tag
        subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Version {version}"], check=True)
        
        print(f"Tag Git {tag_name} criada com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar a tag Git: {e}")
        sys.exit(1)


def main() -> None:
    """Função principal do script."""
    parser = argparse.ArgumentParser(description="Incrementa a versão do projeto seguindo Semantic Versioning.")
    parser.add_argument("part", choices=["major", "minor", "patch", "prealpha", "prebeta", "prerc"], 
                      help="Parte da versão a incrementar")
    parser.add_argument("--no-git", action="store_true", 
                      help="Não criar tag Git para a nova versão")
    parser.add_argument("--no-changelog", action="store_true",
                      help="Não gerar entrada no changelog")
    
    args = parser.parse_args()
    
    current_version = get_current_version()
    print(f"Versão atual: {current_version}")
    
    new_version = bump_version(current_version, args.part)
    print(f"Nova versão: {new_version}")
    
    update_version_in_files(new_version)
    
    if not args.no_changelog:
        try:
            print("Gerando entrada no changelog...")
            subprocess.run(["python", "scripts/generate_changelog.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Aviso: Não foi possível gerar a entrada no changelog: {e}")
    
    if not args.no_git:
        create_git_tag(new_version)
        print(f"Para enviar a tag ao repositório remoto, execute: git push origin v{new_version}")
    
    print(f"Versão atualizada com sucesso para {new_version}!")


if __name__ == "__main__":
    main() 