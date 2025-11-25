import os
import sys
import shutil
from pathlib import Path

try:
    import PyInstaller.__main__ as pyinstaller_main
except ImportError:
    pyinstaller_main = None


BASE_DIR = Path(__file__).resolve().parent
SCRIPT_PATH = BASE_DIR / "monitoramento.py"
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
SPEC_NAME = "monitoramento"
BUNDLE_DIR_NAME = f"{SPEC_NAME}_app"


def build_executable():
    """
    Gera o executável de monitoramento.py usando PyInstaller.

    - Limpa as pastas dist/ e build/ antes de cada build.
    - Gera um executável único (sem depender de arquivo .spec).
    - Cria uma pasta dist/<nome> com o executável e arquivos de configuração (.env, lista_sites.json).
      No final, dist conterá apenas essa pasta de distribuição.
    """
    if pyinstaller_main is None:
        print(
            "PyInstaller não está instalado neste ambiente.\n"
            "Ative o seu virtualenv (venvautomatizacao) e rode:\n"
            "    pip install pyinstaller\n"
        )
        sys.exit(1)

    if not SCRIPT_PATH.exists():
        print(f"Arquivo não encontrado: {SCRIPT_PATH}")
        sys.exit(1)

    # Garante que estamos na pasta do projeto
    os.chdir(BASE_DIR)

    # Limpa dist/ e build/ antes de iniciar um novo build
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    # Separador de --add-data (Windows usa ';', Linux/Mac usam ':')
    data_sep = ";" if os.name == "nt" else ":"

    add_data_args = []

    # Incluir lista_sites.json se existir (dentro do bundle do PyInstaller)
    lista_sites = BASE_DIR / "lista_sites.json"
    if lista_sites.exists():
        add_data_args += ["--add-data", f"{lista_sites}{data_sep}."]

    # Incluir .env se existir (dentro do bundle do PyInstaller)
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        add_data_args += ["--add-data", f"{env_file}{data_sep}."]

    # Argumentos base do PyInstaller
    args = [
        str(SCRIPT_PATH),
        "--name",
        SPEC_NAME,
        "--onefile",   # gera um único executável
        "--console",   # mantém o console (útil para logs)
        "--clean",
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
    ] + add_data_args

    print("Executando PyInstaller com os argumentos:")
    for a in args:
        print(" ", a)

    pyinstaller_main.run(args)

    # Remover arquivo .spec gerado automaticamente (não queremos depender dele)
    spec_path = BASE_DIR / f"{SPEC_NAME}.spec"
    if spec_path.exists():
        try:
            spec_path.unlink()
        except OSError:
            # Se não conseguir apagar, apenas avisa e continua
            print(f"Aviso: não foi possível apagar {spec_path}")

    # Caminho do executável gerado pelo PyInstaller dentro de dist/
    exe_name = SPEC_NAME + (".exe" if os.name == "nt" else "")
    exe_path = DIST_DIR / exe_name

    # Pasta final de distribuição contendo tudo que o monitoramento precisa.
    # Usamos um nome fixo (ex: monitoramento_app) para evitar conflito com o
    # executável em sistemas onde o binário não tem extensão (Linux).
    final_dist_dir = DIST_DIR / BUNDLE_DIR_NAME
    final_dist_dir.mkdir(parents=True, exist_ok=True)

    # Copiar o executável
    if exe_path.exists():
        shutil.copy2(exe_path, final_dist_dir / exe_name)

    # Copiar .env e lista_sites.json para a pasta final
    if env_file.exists():
        shutil.copy2(env_file, final_dist_dir / env_file.name)
    if lista_sites.exists():
        shutil.copy2(lista_sites, final_dist_dir / lista_sites.name)

    # Remover quaisquer arquivos soltos em dist/, mantendo apenas a pasta de distribuição (ex: "monitoramento_app")
    for item in DIST_DIR.iterdir():
        if item.name == BUNDLE_DIR_NAME:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    print("\nBuild finalizado.")
    print(f"Pacote completo para distribuição: {final_dist_dir}")


if __name__ == "__main__":
    build_executable()
