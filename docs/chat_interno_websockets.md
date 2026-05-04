# Chat interno con WebSockets

## 1. Que se implemento

Se implemento un chat interno entre usuarios autenticados del sistema. La idea es que los usuarios puedan hablar dentro de la plataforma, parecido a Microsoft Teams, sin salir a aplicaciones externas.

En el frontend se agrego una interfaz tipo Teams:

- Una columna izquierda con la lista de conversaciones.
- Un panel central con los mensajes de la conversacion seleccionada.
- Un encabezado con el titulo y los participantes.
- Un campo inferior para escribir y enviar mensajes.
- Un boton para crear una nueva conversacion.
- Un boton para actualizar manualmente los mensajes.

En el backend se dejaron endpoints REST para cargar la informacion inicial:

- `GET /communications/users/`: carga usuarios activos disponibles para chat.
- `GET /communications/conversations/`: carga las conversaciones del usuario autenticado.
- `POST /communications/conversations/`: crea una conversacion interna.
- `GET /communications/conversations/<id>/messages/`: carga el historial de mensajes.
- `POST /communications/conversations/<id>/messages/`: envia un mensaje como respaldo si el WebSocket no esta conectado.

Tambien se agrego un endpoint WebSocket para mensajes en tiempo real:

- `ws://127.0.0.1:8000/ws/communications/conversations/<conversation_id>/`

Con esto, los mensajes se guardan en la base de datos y tambien se envian en vivo a los participantes conectados.

## 2. Que se removio

Se elimino la idea anterior de comunicacion multicanal externa. Ya no se usa el modulo de chat para abrir aplicaciones externas.

Se removio:

- Integracion externa con WhatsApp.
- Canal externo de email.
- Canal externo de llamada telefonica.
- Comportamiento basado en `external_url`.
- Botones o enlaces para abrir `wa.me`, `mailto:` o `tel:`.
- Selector de canal para WhatsApp, email o telefono.
- Reglas donde la conversacion era solamente con beneficiarios.

Ahora el chat es solo interno entre usuarios autenticados.

## 3. Explicacion tecnica

El chat usa REST y WebSockets.

REST se usa para cargar datos iniciales, como usuarios, conversaciones y mensajes anteriores. Esto sirve cuando el usuario entra a la pantalla de chats o cambia de conversacion.

WebSocket se usa para comunicacion bidireccional en tiempo real. Esto significa que el navegador puede enviar mensajes al servidor y el servidor tambien puede enviar mensajes al navegador sin que la pagina tenga que refrescarse.

WebSocket funciona sobre TCP. Por eso mantiene una conexion abierta entre el cliente y el servidor mientras el usuario esta en la conversacion.

En Django se usa Django Channels para manejar las conexiones WebSocket. Channels permite aceptar o rechazar conexiones, unir usuarios a grupos y enviar eventos a todos los usuarios conectados a una misma conversacion.

La autenticacion usa las mismas cookies de sesion de Django. No se usa JWT. Cuando el navegador abre el WebSocket, tambien envia las cookies de sesion, y el backend puede saber cual usuario esta conectado.

Para desarrollo local se usa `InMemoryChannelLayer`. Esto permite probar WebSockets sin Redis. Es suficiente para este sprint y para pruebas locales, pero en produccion normalmente se usaria una capa compartida como Redis.

## 4. Prueba manual

Para probar el chat manualmente:

1. Abrir el sistema en dos navegadores diferentes, o usar una ventana normal y una ventana incognito.
2. Iniciar sesion con dos usuarios diferentes.
3. Con el Usuario A, ir a `Chats`.
4. Crear una nueva conversacion con el Usuario B.
5. Desde el Usuario A, enviar un mensaje.
6. El Usuario B debe recibir el mensaje sin refrescar la pagina.
7. El Usuario B responde.
8. El Usuario A debe recibir la respuesta sin refrescar la pagina.

Si el estado muestra `Conectado`, los mensajes estan usando WebSocket en tiempo real.

Si el WebSocket no esta conectado, el frontend puede usar el endpoint REST como respaldo para enviar y recargar mensajes.

## 5. Comandos de validacion

Backend:

```bash
python manage.py test
```

Frontend:

```bash
npm run build
npm run lint
```

Tambien es util ejecutar solo las pruebas del modulo de comunicaciones:

```bash
python manage.py test communications
```

## 6. Como levantar el servidor ASGI

Para probar WebSockets, el backend debe correr con ASGI. Una forma es:

```bash
daphne -b 127.0.0.1 -p 8000 lawclinic.asgi:application
```

Luego se puede levantar el frontend con Vite:

```bash
npm run dev
```
