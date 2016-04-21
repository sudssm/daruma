"use strict";
function onAddProviderButtonClick() {
    window.location.href = "/modal/show/providers/add.html";
}

function refresh(){
    $.getJSON("/get_state")
    .done(function(data){
        if (data["instance"] != null){
            window.location.href = "dashboard.html"
        }
        refresh_providers(data)

        if (providers.length > 2){
            $("#done-adding-providers-button .tooltiptext").hide()
            $("#done-adding-providers-button").prop('disabled', false);
        }
    })
}

refresh()
setInterval(refresh, 1000)