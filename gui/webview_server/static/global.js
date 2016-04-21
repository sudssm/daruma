"use strict";

/********************
 * Slider functions *
 ********************/
function goToSlide(slideContainerId, slideNo) {
    $(slideContainerId).css("margin-left", (-100 * slideNo) + "%");
}

function onRemoveProviderButtonClick(elt){
    var $box = $(elt).parents("div.provider-tile").remove()
    var identifier = $box.children(".provider-identifier").html()
    var id = $box.children(".provider-username").html()
    console.log({"identifier": identifier, "id": id})
    $.get("/remove_provider", {"identifier": identifier, "id": id})
    .done(function(data){
        console.log(data)
    })
}

var providers = []
function buildProviderString(provider){
    var statusMessage = ""
    switch(provider["status"]){
        case "GREEN":
            statusMessage = "Fully Operational"
            break;
        case "YELLOW":
            statusMessage = "Experiencing Difficulties"
            break;
        case "RED":
            statusMessage = "Offline"
            break;
    }
    var div = '<div class="provider-tile status-' + provider["status"].toLowerCase() + '">' +
              '<button type="button" class="remove-provider-button" onclick="onRemoveProviderButtonClick(this)">X</button>' +
              '<img class="provider-icon-square" src="static/logos/square/' + provider["identifier"] + '.png"><br>' +
              '<h2 class="provider-name">' + provider['name'] + '</h2>' +
              '<span class="provider-identifier" style="display:none">' + provider['identifier'] + '</span>' + 
              '<span class="provider-username">' + provider['id'] + '</span>' + 
              '<p class="provider-status">' + statusMessage + '</p>' +
              '</div>';
    return div
}

function refresh_providers(data){
    var new_providers = data["providers"];
    if (new_providers.length != providers.length){
        $("#provider-count").html(new_providers.length)
        $("#providers").html("")
        $.each(new_providers, function(i, provider){
            $("#providers").append(buildProviderString(provider))
        })

        providers = new_providers;
    }
    var statusMessage = "";
    if (data["instance"] != null){
        switch (data["instance"]["status"]){
            case "GREEN":
                statusMessage = "System Fully Operational"
                break;
            case "YELLOW":
                statusMessage = "Cannot connect to a provider! Files are recoverable."
                break;
            case "RED":
                statusMessage = "System Failing"
                break;
        }

        $("#system-status").html(statusMessage)
        $("#header").removeClass()
        $("#header").addClass('status-' + data["instance"]["status"].toLowerCase())
    }
}