
// PRELOADER JS
$(window).load(function(){
    $('.preloader').fadeOut(1000); // set duration in brackets    
});


/* template navigation
  -----------------------------------------------*/
 /*
 $('.main-navigation').onePageNav({
        scrollThreshold: 0.2, // Adjust if Navigation highlights too early or too late
        scrollOffset: 75, //Height of Navigation Bar
        filter: ':not(.external)',
        changeHash: true
    }); 
*/
    /* NAVIGATION VISIBLE ON SCROLL */
    mainNav();
    $(window).scroll(function () {
        mainNav();
    });

    function mainNav() {
        var top = (document.documentElement && document.documentElement.scrollTop) || document.body.scrollTop;
        if (top > 40) $('.sticky-navigation').stop().animate({
            "opacity": '1',
            "top": '0'
        });
        else $('.sticky-navigation').stop().animate({
            "opacity": '0',
            "top": '-75'
        });
    }


/* HTML document is loaded. DOM is ready. 
-------------------------------------------*/
$(document).ready(function() {

 /* Hide Mobile Menu After Click on a link
 -----------------------------------------------*/ 
    $('.navbar-collapse a').click(function(){
        $(".navbar-collapse").collapse('hide');
    }); 


  /* wow
  -------------------------------*/
  new WOW({ mobile: false }).init();
  
    });

