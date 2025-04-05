$(document).ready(function () {
    SphinxRtdTheme.Navigation.onScroll = function () { }
    setTimeout(function () {
        if (window.location.pathname != '/') {
            $('.wy-side-scroll').scrollTop($('.wy-side-scroll').scrollTop() - 60);
        }
        $('.wy-side-scroll').animate({ opacity: 1.0 }, 20);
    }, 20)
})
