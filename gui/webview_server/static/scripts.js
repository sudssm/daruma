/*******************
 * Modal functions *
 *******************/

function hideModalById(id) {
    "use strict";
    var background = document.getElementById("click-blocker");
    var modal = document.getElementById(id);

    document.onkeypress = null;

    modal.classList.add("hidden");

    modal.addEventListener("transitionend", function hide_blocker() {
        modal.removeEventListener("transitionend", hide_blocker);
        background.style.display = "none";
    }, false);
}

function showModalById(id) {
    "use strict";
    var background = document.getElementById("click-blocker");
    var modal = document.getElementById(id);

    background.style.display = "block";

    // Need to wait for the display change to redraw before starting animation.
    setTimeout(function () {
        modal.classList.remove("hidden");

        document.onkeypress = function (evt) {
            if (evt.keyCode === 27) {
                // Hide on escape key
                hideModalById(id);
            }
        };
    }, 5);
}

