"use strict";
var reprovisioning = false;

function onAddProviderButtonClick(){
    window.location.href = "/modal/show/providers/add.html";
}
function onRemoveProviderButtonClick(elt){
    var $box = $(elt).parents("li.inset-box").remove()
    var identifier = $box.children(".provider-identifier").html()
    var id = $box.children(".provider-id").html()
    $.get("/remove_provider", {"identifier": identifier, "id": id})
}
function reprovision(){
    if (reprovisioning)
        return
    reprovisioning = true;
    $.get("/reprovision")
    .done(function(){
        reprovisioning = false;
    })
}

function refresh(){
    $.getJSON("/get_state")
    .done(function(data){
        refresh_providers(data);

        if (data["instance"]["needs_reprovision"]){
            if (data["instance"]["status"] == "GREEN"){
                statusMessage = "Redistributing files"
                data["instance"]["status"] = "YELLOW"
            }
            reprovision()
            $("#system-status").html(statusMessage)
            $("#header").removeClass()
            $("#header").addClass('status-' + data["instance"]["status"].toLowerCase())
        }

    })
}

refresh()
setInterval(refresh, 1000)