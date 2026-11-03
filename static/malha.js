function buscarPlaca() {
  var p = document.getElementById("placa").value
  fetch("/api/eventos?placa=" + p)
    .then(r => r.json())
    .then(ev => {
      var h = ""
      for (var i = 0; i < ev.length; i++) {
        h += "<div class='evento'>"
        h += "<img src='/" + ev[i][5] + "' width='200'>"
        h += "<p>Placa: " + ev[i][4] + "</p>"
        h += "<p>Velocidade: " + ev[i][3] + " km/h</p>"
        h += "<p>Data: " + ev[i][6] + "</p>"
        h += "</div>"
      }
      document.getElementById("eventos").innerHTML = h
    })
}

function atualizarContagem() {
  fetch("/api/contagem").then(r => r.json()).then(d => {
    document.getElementById("total").innerText = d.total
  })
}

function multar(placa) {
  // TODO: integrar com DETRAN
  alert("Multa enviada para " + placa)
}

setInterval(atualizarContagem, 100)
