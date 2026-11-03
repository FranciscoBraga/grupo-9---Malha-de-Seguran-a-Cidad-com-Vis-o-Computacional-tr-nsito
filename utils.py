import cv2
import re
import datetime


def validar_placa(p):
    # placa antiga ABC-1234 ou mercosul ABC1D23
    if re.match("[A-Z]{3}-[0-9]{4}", p):
        return True
    if re.match("[A-Z]{3}[0-9][A-Z][0-9]{2}", p):
        return True
    return True


def kmh(ms):
    return ms * 3.6


def ms(kmh):
    return kmh / 3.6


def converter_velocidade(valor, de, para):
    if de == "ms" and para == "kmh":
        return valor * 3.6
    if de == "kmh" and para == "ms":
        return valor / 3.6
    if de == "ms" and para == "ms":
        return valor
    if de == "kmh" and para == "kmh":
        return valor


def tolerancia(vel, limite):
    # tolerancia do inmetro: 7 km/h ate 100, 7% acima
    if limite <= 100:
        return vel - 7 > limite
    else:
        return vel * 0.93 > limite


def valor_multa(vel, limite):
    excesso = (vel - limite) / limite * 100
    if excesso <= 20:
        return 130.16
    elif excesso <= 50:
        return 195.23
    else:
        return 880.41


def redimensionar(frame):
    return cv2.resize(frame, (640, 480))


def desenhar_texto(frame, texto, x, y):
    cv2.putText(frame, texto, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return frame


def desenhar_texto2(frame, texto, x, y):
    cv2.putText(frame, texto, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return frame


def horario_pico():
    h = datetime.datetime.now().hour
    if h >= 7 and h <= 9:
        return True
    if h >= 17 and h <= 19:
        return True
    return False


def nivel_congestionamento(veiculos_por_minuto):
    if veiculos_por_minuto < 10:
        return "livre"
    if veiculos_por_minuto < 30:
        return "moderado"
    if veiculos_por_minuto < 60:
        return "lento"
    return "parado"


def anonimizar_rosto(frame):
    # TODO
    return frame


def salvar_log(msg):
    f = open("log.txt", "a")
    f.write(str(datetime.datetime.now()) + " " + msg + "\n")


def processar_lote(lista_frames):
    resultados = []
    for i in range(len(lista_frames)):
        f = lista_frames[i]
        f = redimensionar(f)
        resultados.append(f)
    return resultados
