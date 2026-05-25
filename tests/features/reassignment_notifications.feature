Feature: Notificaciones de solicitudes de reasignacion

  Scenario: El advisor ve una notificacion cuando un student solicita reasignacion
    Given existe un caso activo asignado a s.vargas y a.torres para solicitar reasignacion
    When el student s.vargas solicita la reasignacion del caso preparado
    And inicia sesion como advisor a.torres para revisar notificaciones
    Then ve el panel de solicitudes de reasignacion pendientes
    And ve la notificacion de reasignacion relacionada con el caso preparado
