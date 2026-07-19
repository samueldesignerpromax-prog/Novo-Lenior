# gateway_lenior.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
from typing import Optional

app = FastAPI(title="Gateway Lenior", version="1.0")

LENIOR_API = "https://lenior-api-1-hvvj.onrender.com"

class Mensagem(BaseModel):
    texto: str
    sessao_id: Optional[str] = None

@app.post("/chat/texto")
async def chat_texto(mensagem: Mensagem):
    """Proxy para a Lenior com logging e cache simples."""
    print(f"[GATEWAY] Texto: {mensagem.texto[:50]}...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = mensagem.dict(exclude_none=True)
        resp = await client.post(f"{LENIOR_API}/chat/texto", json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()

@app.get("/health")
async def health():
    return {"status": "gateway ok"}
