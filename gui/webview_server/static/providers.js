"use strict";
function onAddProviderButtonClick() {
    window.location.href = "/modal/show/providers/add.html";
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
                '<img class="provider-icon-square" src="static/logos/square/"' + provider["identifier"] + '.png">' +
                '<span class="provider-name">' + provider['name'] + '</span>' + 
                '<span class="provider-id">' + provider['id'] + '</span>' + 
                '<ul class="status-list">' + 
                    '<li>Status: <span class="status-' + provider["status"].toLowerCase() + '">' + statusMessage + '</span></li>' +
                    //'<li>Last Online: <span class="status-yellow">A week ago</span></li>' +
                    //'<li>Capacity Used: <span class="status-red">99%</span></li>' +
                '</ul>' + 
                '<fieldset class="provider-controls">' +
                    '<button type="button">Remove</button>' +
                '</fieldset>' + 
                '</li>';
    return li_str
}

var providers = []

setInterval(function(){
    $.getJSON("/get_state")
    .done(function(data){
        var new_providers = data["providers"];
        if (new_providers.length != providers.length){
            $.each(new_providers, function(i, provider){
                // TODO do something when we've added/removed a provider but not yet reprovisioned
                var li = buildProviderString(provider)
                $("#provider-list").append(li)
            })

            providers = new_providers;
        }
        var statusMessage = "";
        switch(data["instance"]["status"]){
            case "GREEN":
                statusMessage = "Fully Operational"
                break;
            case "YELLOW":
                statusMessage = "Cannot connect to a provider! Please repair or reprovision."
                break;
            case "RED":
                statusMessage = "Offline"
                break;
        }
        $("#system-status").html(statusMessage)
        $("#system-status").removeClass()
        $("#system-status").addClass('status-' + data["instance"]["status"].toLowerCase())

    })
}, 1000)