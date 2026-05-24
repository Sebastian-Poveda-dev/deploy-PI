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

  Scenario: Un advisor puede rechazar su asignacion
    Given existe un caso asignado al advisor "a.torres"
    And existe una sesion iniciada como advisor "a.torres"
    When abre la pagina de casos
    And abre el caso asignado al advisor
    When rechaza su asignacion desde el modal
    Then el advisor ya no aparece como usuario asignado del caso

  Scenario: Un student puede solicitar reasignacion con motivo y el caso queda en estado pendiente
    Given existe un caso asignado al student "s.vargas" sin solicitud pendiente
    And existe una sesion iniciada como student "s.vargas"
    When abre la pagina de casos
    And abre el caso asignado al student
    When solicita reasignacion con motivo desde el modal
    Then el caso muestra una solicitud de reasignacion pendiente

  Scenario: Un advisor o admin puede cerrar un caso seleccionando una razon de cancelacion
    Given existe un caso activo para cerrar
    And existe una sesion iniciada como admin
    When abre la pagina de casos
    And abre el caso activo para cerrar
    When cierra el caso con la razon "Desistimiento expreso del usuario"
    Then el caso cerrado muestra estado cancelado

  Scenario: Cerrar un caso con razon Otro requiere texto adicional
    Given existe un caso activo para cerrar
    And existe una sesion iniciada como admin
    When abre la pagina de casos
    And abre el caso activo para cerrar
    When intenta cerrar el caso con la razon Otro sin texto adicional
    Then ve un error que exige describir la razon de cancelacion
    And el caso no cambia a estado cancelado

  Scenario: El boton Mas informacion del beneficiario despliega y colapsa los campos extra
    Given existe un caso activo para cerrar
    And existe una sesion iniciada como admin
    When abre la pagina de casos
    And abre el caso activo para cerrar
    Then los campos extra del beneficiario estan ocultos
    When despliega mas informacion del beneficiario
    Then los campos extra del beneficiario aparecen
    When colapsa la informacion del beneficiario
    Then los campos extra del beneficiario estan ocultos
