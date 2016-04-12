"use strict";

function onNewProviderSelect(provider_id) {
	$.get("providers/add/" + provider_id);
}

$(document).ready(function () {
    $(".provider-icon-wide").error(function() {
    	var new_elt = "<span class='provider-icon-wide'>" + $(this).attr("alt") + "</span>";
    	$(this).replaceWith(new_elt);
    });    
});
