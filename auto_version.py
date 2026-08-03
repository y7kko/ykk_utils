import re
import subprocess
import os
from pathlib import Path

_show_commit_msg = False

def yellow(string):
    return  "\033[33m" + string + "\033[0m"

def get_latest_commit_message():
    """Obtém a mensagem do último commit"""
    try:
        result = subprocess.run(
            ['cmd','/c','git', 'log', '-1', r'--pretty=%s'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Erro ao obter mensagem do commit")
        return None

def parse_conventional_commit(message):
    """Analisa a mensagem segundo Conventional Commits"""
    # Padrao: type(scope): description
    # Tipos: feat, fix, docs, style, refactor, perf, test, chore, etc.
    pattern = r'^(?P<type>feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(?:\((?P<scope>[^)]+)\))?: (?P<description>.+)$'
    match = re.match(pattern, message, re.IGNORECASE)
    
    if match:
        return match.group('type').lower(), match.group('scope'), match.group('description')
    return None, None, None

def get_current_version(init_path):
    """Lê a versao atual do __init__.py"""
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    version_match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", content)
    if version_match:
        return version_match.group(1)
    return "0.0.0"

def bump_version(current_version, commit_type):
    """Incrementa a versao baseado no tipo de commit"""
    # Remove 'v' se existir
    if current_version.startswith('v'):
        current_version = current_version[1:]
    
    # Divide em major, minor, patch
    parts = current_version.split('.')
    if len(parts) != 3:
        parts = ['0', '0', '0']
    
    major, minor, patch = map(int, parts)
    
    # Regras de versionamento baseado no tipo de commit
    if commit_type == 'feat':
        # Nova feature: incrementa minor, zera patch
        minor += 1
        patch = 0
    elif commit_type == 'fix':
        # Bug fix: incrementa patch
        patch += 1
    elif commit_type in ['perf', 'refactor', 'style', 'docs']:
        # Melhorias: incrementa patch (opcional)
        patch += 1
    elif commit_type in ['BREAKING CHANGE', 'revert']:
        # Breaking change: incrementa major, zera minor e patch
        major += 1
        minor = 0
        patch = 0
    
    return f"{major}.{minor}.{patch}"

def update_version_file(init_path, new_version):
    """Atualiza a versao no arquivo __init__.py"""
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Atualiza a versao
    new_content = re.sub(
        r"__version__\s*=\s*['\"][^'\"]+['\"]",
        f'__version__ = "{new_version}"',
        content
    )
    
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Versao atualizada para: {new_version}")

def main():
    # Encontra o caminho do __init__.py no diretório atual
    init_path = Path.cwd() / "ykk_utils/__init__.py"
    
    if not init_path.exists():
        print("Arquivo __init__.py nao encontrado no diretorio atual")
        return
    
    # Obtém a mensagem do último commit
    commit_message = get_latest_commit_message()
    if not commit_message:
        print("Nao foi possível obter a mensagem do commit")
        return
    if _show_commit_msg:
        print(f"Mensagem do commit: {commit_message}")
    
    # Analisa o commit
    commit_type, _, _ = parse_conventional_commit(commit_message)
    
    # Verifica se é um commit convencional
    if not commit_type:
        print(yellow("Commit nao segue Conventional Commits. Versao nao alterada."))
        return
    
    # Verifica se há BREAKING CHANGE no corpo
    if 'BREAKING CHANGE' in commit_message.upper():
        commit_type = 'BREAKING CHANGE'
    
    print(f"Tipo de commit: {commit_type}")
    
    # Lê versao atual
    current_version = get_current_version(init_path)
    print(f"Versao atual: {current_version}")
    
    # Calcula nova versao
    new_version = bump_version(current_version, commit_type)
    
    if not (new_version == current_version):
        print(f":: Version Bump")
        print(f'{current_version} -> {new_version}')
    else:
        return
    
    # Atualiza o arquivo
    update_version_file(init_path, new_version)
    
    try:
        subprocess.run(['cmd','/c','git', 'add', str(init_path)], check=True)
        subprocess.run(['cmd','/c','git', 'commit', '--amend', '--no-edit', '--no-verify'], check=True)
        print("Arquivo __init__.py adicionado ao commit com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao adicionar ao commit: {e}")
        print("Você pode adicionar manualmente com: git add __init__.py && git commit --amend --no-edit")

    os.environ.pop('SKIP_VERSION_BUMP', None)


if __name__ == "__main__":
    main()
