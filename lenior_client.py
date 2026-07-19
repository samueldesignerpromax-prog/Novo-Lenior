#!/usr/bin/env python3
"""
lenior_client.py — Cliente Python para a API Lenior 2.0
Uso: python lenior_client.py "sua pergunta aqui"
"""

import requests
import json
import sys
import os
import base64
from pathlib import Path

# ===== CONFIGURAÇÃO =====
API_BASE = "https://lenior-api-1-hvvj.onrender.com"
TEXT_ENDPOINT = f"{API_BASE}/chat/texto"
AUDIO_ENDPOINT = f"{API_BASE}/chat/audio"

# ===== SESSÃO (persistente) =====
SESSION_FILE = Path.home() / ".lenior_session"

def carregar_sessao():
    if SESSION_FILE.exists():
        with open(SESSION_FILE, "r") as f:
            return f.read().strip()
    return None

def salvar_sessao(sessao_id):
    with open(SESSION_FILE, "w") as f:
        f.write(sessao_id)

# ===== FUNÇÕES =====

def perguntar_texto(pergunta, sessao_id=None):
    """Envia uma pergunta de texto e retorna a resposta."""
    payload = {"texto": pergunta}
    if sessao_id:
        payload["sessao_id"] = sessao_id

    resp = requests.post(TEXT_ENDPOINT, json=payload)
    resp.raise_for_status()
    return resp.json()

def perguntar_audio(caminho_audio, sessao_id=None):
    """Envia um arquivo de áudio e retorna a resposta."""
    with open(caminho_audio, "rb") as f:
        files = {"audio": (os.path.basename(caminho_audio), f, "audio/mp3")}
        data = {}
        if sessao_id:
            data["sessao_id"] = sessao_id
        resp = requests.post(AUDIO_ENDPOINT, files=files, data=data)
        resp.raise_for_status()
        return resp.json()

def salvar_audio_base64(base64_str, nome_saida="resposta_audio.wav"):
    """Salva o áudio retornado em base64 para um arquivo."""
    if not base64_str:
        print("⚠️ Nenhum áudio retornado.")
        return
    audio_bytes = base64.b64decode(base64_str)
    with open(nome_saida, "wb") as f:
        f.write(audio_bytes)
    print(f"✅ Áudio salvo em: {nome_saida}")

# ===== MAIN =====

def main():
    sessao_id = carregar_sessao()

    if len(sys.argv) > 1:
        pergunta = " ".join(sys.argv[1:])
        print(f"🧠 Você: {pergunta}")
        try:
            data = perguntar_texto(pergunta, sessao_id)
            if data.get("sessao_id"):
                salvar_sessao(data["sessao_id"])
            print(f"🤖 Lenior: {data.get('texto', '(vazio)')}")
            if data.get("audio"):
                salvar_audio_base64(data["audio"])
            if data.get("execucao"):
                print(f"🧪 Execução: {json.dumps(data['execucao'], indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"❌ Erro: {e}")
        return

    # Modo interativo
    print("🧠 Lenior 2.0 — Cliente Python")
    print("Digite 'sair' para encerrar.\n")
    while True:
        try:
            pergunta = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo!")
            break
        if pergunta.lower() in ("sair", "quit", "exit"):
            print("Até logo!")
            break
        if not pergunta:
            continue

        try:
            data = perguntar_texto(pergunta, sessao_id)
            if data.get("sessao_id"):
                salvar_sessao(data["sessao_id"])
            print(f"Lenior: {data.get('texto', '(vazio)')}")
            if data.get("audio"):
                salvar_audio_base64(data["audio"])
            if data.get("execucao"):
                print(f"🧪 Execução: {json.dumps(data['execucao'], indent=2, ensure_ascii=False)}")
            print()
        except Exception as e:
            print(f"❌ Erro: {e}\n")

if __name__ == "__main__":
    main()
