"use strict";
var reprovisioning = false;

function onAddProviderButtonClick(){
    window.location.href = "/modal/show/providers/add.html";
}
function reprovision(){
    if (reprovisioning)
        return
    reprovisioning = true;
    $.get("/reprovision")
    .done(function(data){
        console.log(data)
        reprovisioning = false;
    })
}

function refresh(){
    $.getJSON("/get_state")
    .done(function(data){
        refresh_providers(data);

        if (data["instance"]["needs_reprovision"]){
            if (data["instance"]["status"] == "GREEN"){
                var statusMessage = "Redistributing files"
                $("#system-status").html(statusMessage)
                data["instance"]["status"] = "YELLOW"
            }
            reprovision()
            $("#header").removeClass()
            $("#header").addClass('status-' + data["instance"]["status"].toLowerCase())
        }

    })
}

refresh()
setInterval(refresh, 1000)