# Comunicación multicanal y WebSockets

## Decisión actual

En esta versión la comunicación multicanal no usa WebSockets.

La comunicación funciona con peticiones HTTP normales entre React y Django. Por ejemplo, el frontend consulta las conversaciones, consulta los mensajes y envía nuevos mensajes usando endpoints REST.

Los mensajes se actualizan de forma manual. Después de enviar un mensaje, la pantalla vuelve a cargar los mensajes, y también existe un botón de **Actualizar** para consultar los mensajes otra vez.

## Razón

Esta decisión baja el riesgo para el sprint actual. Como el sistema ya funciona con Django, Django REST Framework, React y cookies de sesión, usar HTTP normal permite avanzar sin cambiar mucho la arquitectura.

También ayuda a evitar romper la aplicación actual. Agregar WebSockets requiere más configuración y puede afectar despliegue, autenticación y pruebas.

Además, esta versión es más fácil de probar con el stack actual. Los endpoints REST se pueden validar con pruebas normales de Django y DRF.

## Idea para una implementación futura

Más adelante se podría implementar comunicación en tiempo real usando **Django Channels**.

Para eso sería necesario agregar configuración **ASGI** al proyecto, además de configurar Channels en Django.

También se podría crear un consumer para manejar salas de conversación. Cada conversación podría tener una sala con un nombre como:

```text
conversation_<id>
```

Cuando un usuario abra una conversación en el frontend, React podría conectarse a esa sala usando WebSocket. Así los mensajes nuevos podrían aparecer automáticamente sin presionar **Actualizar**.

## Nota de pruebas manuales

Para probar la comunicación con dos usuarios, se recomienda usar dos navegadores diferentes o un navegador normal y una ventana de incógnito.

Esto es importante porque la aplicación usa cookies de sesión. Si se intenta iniciar sesión con dos usuarios en el mismo navegador, una sesión puede reemplazar a la otra.
