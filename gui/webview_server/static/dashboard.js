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

function buildProviderString(provider){
    var statusMessage = ""
    switch(provider["status"]){
        case "GREEN":
            statusMessage = "Fully Operational"
            break;
        case "YELLOW":
            statusMessage = "Experiencing Some Difficulties"
            break;
        case "RED":
            statusMessage = "Offline"
            break;
    }
    var li_str = '<li class="inset-box">' +
                '<img class="provider-icon-square" src="static/logos/square/' + provider["identifier"] + '.png">' +
                '<span class="provider-name">' + provider['name'] + '</span>' +
                '<span class="provider-identifier" style="display:none">' + provider['identifier'] + '</span>' + 
                '<span class="provider-id">' + provider['id'] + '</span>' + 
                '<ul class="status-list">' + 
                    '<li>Status: <span class="status-' + provider["status"].toLowerCase() + '">' + statusMessage + '</span></li>' +
                    //'<li>Last Online: <span class="status-yellow">A week ago</span></li>' +
                    //'<li>Capacity Used: <span class="status-red">99%</span></li>' +
                '</ul>' + 
                '<fieldset class="provider-controls">' +
                    '<button type="button" onclick="onRemoveProviderButtonClick(this)">Remove</button>' +
                '</fieldset>' + 
                '</li>';
    return li_str
}

var providers = []

function refresh(){
    $.getJSON("/get_state")
    .done(function(data){
        var new_providers = data["providers"];
        if (new_providers.length != providers.length){
            $("#provider-count").html(new_providers.length)
            $("#provider-list").html("")
            $.each(new_providers, function(i, provider){
                $("#provider-list").append(buildProviderString(provider))
            })

            providers = new_providers;
        }
        var statusMessage = "";
        switch (data["instance"]["status"]){
            case "GREEN":
                statusMessage = "Fully Operational"
                break;
            case "YELLOW":
                statusMessage = "Cannot connect to a provider! Files are recoverable."
                break;
            case "RED":
                statusMessage = "Offline"
                break;
        }
        if (data["instance"]["needs_reprovision"]){
            if (data["instance"]["status"] == "GREEN"){
                statusMessage = "Redistributing files"
                data["instance"]["status"] = "YELLOW"
            }
            reprovision()
        }
        $("#system-status").html(statusMessage)
        $("#header").removeClass()
        $("#header").addClass('status-' + data["instance"]["status"].toLowerCase())

    })
}

refresh()
setInterval(refresh, 1000)