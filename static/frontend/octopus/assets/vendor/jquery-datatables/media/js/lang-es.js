$(document).ready(function() {
    $("table").DataTable( {
    	"searching" : true,
        "language": {
            "sProcessing":     "Procesando...",
            "sEmptyTable":     "Ningún dato disponible en esta tabla",
            "sLengthMenu": "Mostrando _MENU_ filas por página",
            "sZeroRecords": "No hay datos encontrados",
            "sInfoEmpty": "No hay filas disponibles",
            "sInfoFiltered": "(filtrando _MAX_ filas en total)",
            "sInfo":"Mostrando _START_ para _END_ de _TOTAL_ entradas ",
            "sSearch": "Buscar:",
            "sSearchPlaceholder": "Buscar:",
            "sUrl":            "",
            "sInfoThousands":  ",",
            "sLoadingRecords": "Cargando...",
            "oPaginate":{
            	 "sFirst":"Primero",
            	 "sLast":"Ultimo",
            	 "sNext":"Siguiente",
                 "sPrevious":"Anterior"
        },
            "oAria": {
                "sSortAscending":  ": Activar para ordenar la columna de manera ascendente",
                "sSortDescending": ": Activar para ordenar la columna de manera descendente"
            }
        }
    } );
} );
