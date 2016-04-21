"use strict";
function onAddProviderButtonClick() {
    window.location.href = "/modal/show/providers/add.html";
}

var providers = []

function refresh(){
    $.getJSON("/get_state")
    .done(function(data){
        if (data["instance"] != null){
            window.location.href = "dashboard.html"
        }
        var new_providers = data["providers"];
        if (new_providers.length != providers.length){
            $("#provider-count").html(new_providers.length)
            for (var i = providers.length; i < new_providers.length; i ++){
                var provider = new_providers[i];
                var li = "<li>" +
                         "&#9989" +
                         "<span class='added-provider-name'>" + provider["name"] + "</span> " +
                         "<span class='added-username'>" + provider["id"] + "</span>" +
                         "</li>"

                $("#providers").append(li)
            }

            providers = new_providers;

            if (providers.length > 2){
                $("#done-adding-providers-button .tooltiptext").hide()
                $("#done-adding-providers-button").prop('disabled', false);
            }
        }
    })
}

refresh()
setInterval(refresh, 1000)