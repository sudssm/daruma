"use strict";

function onGetStartedClick() {
	$("#instructions-welcome").hide();
	$("#get-started-button").hide();

	$("#instructions-add").show();
	$("#add-provider-button").show();
	$("#done-adding-providers-button").show();
	$("#added-providers-area").show();
}

function onAddProviderButtonClick() {
	window.location.href = "/modal/show/providers/add.html";
}
