"use strict";

/********************
 * Slider functions *
 ********************/
function goToSlide(slideContainerId, slideNo) {
    $(slideContainerId).css("margin-left", (-100 * slideNo) + "%");
}

/*******************
 * Modal functions *
 *******************/

function hideModalById(id) {
    $(document).off("keypress");

    var $modal = $(id);
    $modal.addClass("hidden");
    $modal.one("transitionend", function (event) {
        $("#click-blocker").hide();
    });
}

function showModalById(id) {
    $("#click-blocker").show();

    // Need to wait for the display change to redraw before starting animation.
    setTimeout(function () {
        $(id).removeClass("hidden");

        $(document).keypress(function (event) {
            if (event.which === 27) { // Hide on escape key
                hideModalById(id);
            }
        });
    }, 5);
}
