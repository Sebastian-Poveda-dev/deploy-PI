Feature: Notificaciones de solicitudes de reasignacion

  Scenario: El advisor ve una notificacion cuando un student solicita reasignacion
    Given existe un caso activo asignado a s.vargas y a.torres para solicitar reasignacion
    When el student s.vargas solicita la reasignacion del caso preparado
    And inicia sesion como advisor a.torres para revisar notificaciones
    Then ve el panel de solicitudes de reasignacion pendientes
    And ve la notificacion de reasignacion relacionada con el caso preparado

  Scenario: Marcar la notificacion como leida la elimina del panel
    Given existe una solicitud de reasignacion pendiente notificada a a.torres
    When inicia sesion como advisor a.torres para revisar notificaciones
    Then ve la notificacion de reasignacion relacionada con el caso preparado
    When descarta la notificacion de reasignacion del caso preparado
    Then la notificacion de reasignacion del caso preparado desaparece del panel
    When refresca el dashboard de notificaciones
    Then la notificacion de reasignacion del caso preparado no vuelve a aparecer

  Scenario: Aprobar la reasignacion desde el modal actualiza la solicitud y la asignacion
    Given existe una solicitud de reasignacion pendiente notificada a a.torres
    When inicia sesion como advisor a.torres para revisar notificaciones
    And abre el caso preparado desde la notificacion de reasignacion
    Then el modal muestra la solicitud de reasignacion pendiente
    When aprueba la reasignacion desde el modal del caso preparado
    Then el modal ya no muestra solicitud de reasignacion pendiente
    And el student solicitante ya no aparece asignado al caso preparado
