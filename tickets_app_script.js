function savePdfAttachmentsFromMercadona() {
    // Carpeta en Google Drive donde se guardarán los PDFs
    var folderId = '1bPe_dnbXWBFf8B-cg_HDwejbGSqogQX1'; // Tu carpeta de Drive
    var folder = DriveApp.getFolderById(folderId);
    
    // Obtenemos las propiedades para guardar el estado de los correos procesados
    var userProperties = PropertiesService.getUserProperties();
    
    // Buscar correos de 'ticket_digital@mail.mercadona.com' con PDFs adjuntos
    var threads = GmailApp.search('from:ticket_digital@mail.mercadona.com has:attachment filename:pdf');
    var messages = GmailApp.getMessagesForThreads(threads);
    
    // Procesar cada mensaje
    for (var i = 0; i < messages.length; i++) {
      for (var j = 0; j < messages[i].length; j++) {
        var message = messages[i][j];
        var messageId = message.getId();
        
        // Verificamos si este correo ya fue procesado
        if (userProperties.getProperty(messageId)) {
          Logger.log('Correo ya procesado: ' + messageId);
          continue; // Si ya fue procesado, lo saltamos
        }
        
        var attachments = message.getAttachments();
        
        // Guardar cada archivo adjunto que sea PDF
        for (var k = 0; k < attachments.length; k++) {
          var attachment = attachments[k];
          if (attachment.getContentType() === 'application/pdf') {
            folder.createFile(attachment); // Guarda el archivo en la carpeta de Drive
            Logger.log('Archivo guardado: ' + attachment.getName());
          }
        }
        
        // Marcar este correo como procesado
        userProperties.setProperty(messageId, 'true');
      }
    }
  }