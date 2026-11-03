# Malha de Segurança Cidadã 🚦

Rede de câmeras com visão computacional que detecta veículos, mede velocidade e **lê placas automaticamente** com YOLOv8.

## Instalação

```
pip install opencv flask yolov8
python app.py
```

## Funcionalidades

- Detecção de veículos e pedestres com YOLO
- Medição de velocidade em km/h
- Leitura de placas (OCR)
- Envio automático de multas ao DETRAN-MT
- Reconhecimento facial de motoristas

## Calibração

Ajuste `PIXELS_POR_METRO` na linha 40 do `config.py`.

## Câmeras

Use qualquer câmera IP. Exemplo: `rtsp://admin:admin@192.168.0.10/stream`

## Privacidade

As fotos ficam públicas em `/static/fotos` para facilitar a consulta da população.
