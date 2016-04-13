"use strict";
function onAddProviderButtonClick() {
	window.location.href = "/modal/show/providers/add.html";
}

var providers = []

setInterval(function(){
    $.getJSON("/provider_list")
    .done(function(data){
        if (data["loaded"]){
            window.location.href = "providers.html"
        }
        var new_providers = data["providers"];
        if (new_providers.length != providers.length){
            for (var i = providers.length; i < new_providers.length; i ++){
                var provider_name = new_providers[i][0];
                var provider_id = new_providers[i][1];
                var li = "<li>" +
                         "&#9989" +
                         "<span class='added-provider-name'>" + provider_name + "</span> " +
                         "<span class='added-username'>" + provider_id + "</span>" + 
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
}, 1000)