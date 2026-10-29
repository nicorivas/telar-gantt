# telar-gantt

Un módulo de [telar](https://github.com/nicorivas/telar): los proyectos en el tiempo, como una subpestaña
«gantt» de **proyectos** en el dashboard. Dibuja lo que da `telar fechas` y nada más, así que no sabe de qué
equipo es ni de dónde vino cada fecha: cronogramas de los documentos, calendarios leídos con un mapa
(`.telar/fechas.yaml`), fuentes de otros módulos (el plazo y los hitos de un PMO), tareas con fecha.

```sh
telar modulos instalar gantt                 # del catálogo
telar modulos instalar --enlazar ./telar-gantt   # o desde aquí, para desarrollarlo
```

Necesita telar 0.8.1 (`telar fechas`, subpestañas, `window.lienzo.pedir`).

## Qué dibuja

| En el Gantt | Sale de |
|---|---|
| Una fila por proyecto | las unidades con alguna fecha entre seis meses atrás y un año adelante; no las terminadas (su `plazo` hecho o cancelado, o un estado cerrado en su documento) |
| Su nombre, cliente y área | `telar proyectos` (el color, del orden de las áreas del perfil) |
| Su barra | su fecha de clase `plazo`, si una fuente la da; si no, de su primera a su última actividad |
| Banderas y puntos sobre la barra | sus fechas de clase `hito` (rellena: hecha) y `tarea` (roja: vencida) |
| Adentro, al abrirla | sus `actividad` (barras), `sesion`, `entrega` y `evento` (un día), con su estado y su responsable |
| Abajo | los proyectos activos sin ninguna fecha, las filas que no se entendieron y las fuentes caídas |

Zoom de día, semana o mes, filtro por texto y por área, abrir y plegar todo, ir a hoy. Recuerda lo elegido.

## Mover

Lo que su fuente sabe escribir (`editable` en `telar fechas`) se arrastra: una barra entera la corre, un borde
cambia solo ese extremo, una marca de un día se mueve. Al soltar, telar lo escribe donde vive (la celda del
cronograma, con su forma; la fecha de la tarea) y aparece «deshacer» unos segundos. Si no se puede (la fila
cambió, la fuente es de solo lectura), vuelve a su lugar con el porqué.

La primera vez, la página pregunta si el módulo puede cambiar fechas (`[permisos] ordenes = ["fecha"]`). Lo
concedido se revoca con `telar modulos permisos gantt --quitar fecha`.

## El menú de un proyecto

Clic derecho sobre un proyecto (su nombre, su barra o una de sus actividades) abre su menú, el mismo que en
«proyectos» y en la barra de hilos: abrir con el agente, consolidar, el README, la carpeta, copiar su dirección.

## Archivos

| Archivo | Qué es |
|---|---|
| `modulo.toml` | el manifiesto: una subpestaña de «proyectos» (`[pestana] dentro`), y lo que pide |
| `bin/gantt.py` | junta `telar fechas` y `telar proyectos`, genera `~/.local/state/telar-gantt/gantt.html` y lo devuelve como lienzo; `datos` imprime lo que va a dibujar. Solo biblioteca estándar |
| `plantilla.html` | el Gantt: HTML, CSS y JS en línea (el lienzo no tiene red), con sus íconos de Nerd Fonts en una letra recortada |
| `bin/iconos.py` | recorta Symbols Nerd Font Mono a los íconos que usa la plantilla (unos 2 KB) y los escribe adentro: `uv run --with fonttools --with brotli python3 bin/iconos.py` |

Los íconos son de [Nerd Fonts](https://www.nerdfonts.com) (MIT): Codicons (CC BY 4.0), Material Design Icons
(Apache 2.0) y Octicons (MIT).
