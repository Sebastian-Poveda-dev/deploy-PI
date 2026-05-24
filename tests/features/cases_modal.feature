Feature: Gestion de casos desde el modal

  Scenario: Crear un caso con Resolucion inmediata activa los campos extra y lo cierra directamente
    Given existe una sesion iniciada como admin
    Given abre la pagina de casos
    When prepara el modal para crear un caso con resolucion inmediata
    Then ve los campos extra de resolucion inmediata
    When completa y crea el caso con resolucion inmediata
    Then el caso con resolucion inmediata aparece en la tabla
    And el caso con resolucion inmediata queda cerrado o finalizado

  Scenario: Un advisor puede aprobar un caso pendiente y el estado cambia
    Given existe un caso pendiente asignado al advisor "a.torres"
    And existe una sesion iniciada como advisor "a.torres"
    When abre la pagina de casos
    And abre el caso pendiente asignado al advisor
    Then el caso pendiente muestra estado pendiente
    When aprueba el caso pendiente desde el modal
    Then el caso aprobado muestra estado activo
