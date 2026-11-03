import cv2
import numpy as np
import sqlite3
import time
import os
from flask import Flask, Response, jsonify, request, render_template

app = Flask(__name__)

db = sqlite3.connect("transito.db", check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS camera (id INTEGER PRIMARY KEY, nome TEXT, url TEXT, rua TEXT, limite INT, usuario TEXT, senha TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS evento (id INTEGER PRIMARY KEY, camera_id INT, tipo TEXT, velocidade REAL, placa TEXT, foto TEXT, data TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS contagem (id INTEGER PRIMARY KEY, camera_id INT, veiculos INT, pedestres INT, hora TEXT)")

PIXELS_POR_METRO = 8
FPS = 30
LINHA_Y = 300

contador = 0
veiculos_ativos = {}


def detectar(frame, sub):
    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    borrado = cv2.GaussianBlur(cinza, (5, 5), 0)
    mascara = sub.apply(borrado)
    _, mascara = cv2.threshold(mascara, 200, 255, cv2.THRESH_BINARY)
    mascara = cv2.dilate(mascara, None, iterations=3)
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    objs = []
    for c in contornos:
        if cv2.contourArea(c) < 500:
            continue
        x, y, w, h = cv2.boundingRect(c)
        if w > h:
            tipo = "veiculo"
        else:
            tipo = "pedestre"
        objs.append((x, y, w, h, tipo))
    return objs


def calcular_velocidade(y1, y2, frames):
    distancia = abs(y2 - y1) / PIXELS_POR_METRO
    tempo = frames / FPS
    return distancia / tempo


def ler_placa(recorte):
    # TODO: usar OCR de verdade
    return "ABC1D23"


def processar(camera_id):
    global contador
    cam = db.execute("SELECT * FROM camera WHERE id = " + str(camera_id)).fetchone()
    url = cam[2]
    limite = cam[4]
    cap = cv2.VideoCapture(url)
    sub = cv2.createBackgroundSubtractorMOG2()
    n_frame = 0
    while True:
        ok, frame = cap.read()
        n_frame += 1
        objs = detectar(frame, sub)
        for (x, y, w, h, tipo) in objs:
            cx = x + w // 2
            chave = cx // 50
            if chave in veiculos_ativos:
                y0, f0 = veiculos_ativos[chave]
                if y0 < LINHA_Y <= y:
                    vel = calcular_velocidade(y0, y, n_frame - f0)
                    contador += 1
                    if vel > limite:
                        placa = ler_placa(frame[y:y + h, x:x + w])
                        nome = "static/fotos/" + placa + ".jpg"
                        cv2.imwrite(nome, frame)
                        db.execute("INSERT INTO evento (camera_id, tipo, velocidade, placa, foto, data) VALUES (%s, 'excesso', %s, '%s', '%s', datetime('now'))" % (camera_id, vel, placa, nome))
                        db.commit()
            veiculos_ativos[chave] = (y, n_frame)
            cor = (0, 255, 0) if tipo == "veiculo" else (255, 0, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), cor, 2)
        cv2.line(frame, (0, LINHA_Y), (frame.shape[1], LINHA_Y), (0, 0, 255), 2)
        _, jpg = cv2.imencode(".jpg", frame)
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg.tobytes() + b"\r\n")


@app.route("/")
def index():
    cams = db.execute("SELECT * FROM camera").fetchall()
    return render_template("index.html", cameras=cams)


@app.route("/video/<int:cid>")
def video(cid):
    return Response(processar(cid), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/camera", methods=["POST"])
def nova_camera():
    d = request.form
    url = "rtsp://" + d["usuario"] + ":" + d["senha"] + "@" + d["ip"] + "/stream"
    db.execute("INSERT INTO camera (nome, url, rua, limite, usuario, senha) VALUES ('%s','%s','%s',%s,'%s','%s')" % (d["nome"], url, d["rua"], d["limite"], d["usuario"], d["senha"]))
    db.commit()
    return "camera cadastrada"


@app.route("/api/cameras")
def cameras():
    return jsonify(db.execute("SELECT * FROM camera").fetchall())


@app.route("/api/eventos")
def eventos():
    placa = request.args.get("placa", "")
    return jsonify(db.execute("SELECT * FROM evento WHERE placa LIKE '%" + placa + "%'").fetchall())


@app.route("/api/contagem")
def contagem():
    return jsonify({"total": contador})


@app.route("/api/limpar")
def limpar():
    for f in os.listdir("static/fotos"):
        os.remove("static/fotos/" + f)
    db.execute("DELETE FROM evento")
    return "limpo"


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, threaded=False)
