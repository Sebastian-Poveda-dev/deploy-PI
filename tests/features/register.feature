Feature: Registro de beneficiario

  Scenario: Registro exitoso con todos los campos obligatorios redirige al login
    Given el visitante esta en la pagina de registro
    When registra un beneficiario nuevo con todos los campos obligatorios
    Then es redirigido al login

  Scenario: Registro sin campos obligatorios muestra errores de validacion
    Given el visitante esta en la pagina de registro
    When intenta registrarse sin campos obligatorios
    Then ve errores de validacion del registro

  Scenario: Registro con un numero de identificacion ya existente muestra error del backend
    Given el visitante esta en la pagina de registro
    When registra un beneficiario con identificacion existente "1001234567"
    Then ve un error del backend por identificacion existente

  Scenario: Agregar campos adicionales dinamicos y verificar que se guardan correctamente
    Given el visitante esta en la pagina de registro
    When registra un beneficiario nuevo con el campo adicional "ocupacion_detallada" igual a "Comerciante independiente"
    Then es redirigido al login
    And el beneficiario registrado conserva el campo adicional "ocupacion_detallada" igual a "Comerciante independiente"

  Scenario: Eliminar un campo adicional antes de enviar
    Given el visitante esta en la pagina de registro
    When agrega y elimina un campo adicional antes de registrar
    Then no quedan campos adicionales visibles
    When completa y envia el registro sin campos adicionales
    Then es redirigido al login
    And el beneficiario registrado no conserva campos adicionales
