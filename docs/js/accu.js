$(document).ready(function () {
    if (document.body.getElementsByTagNameNS("http://www.w3.org/1998/Math/MathML", "math")[0]) {
        if (navigator.userAgent.indexOf("Firefox") > -1) {

        } else {
            a = document.createElement("script"),
                a.src = "https://cdn.bootcss.com/mathjax/2.7.1/MathJax.js?config=MML_HTMLorMML",
                document.head.appendChild(a)
        };
    }

    $(function () {
        $.fn.isFullyWithinViewport = function () {
            var viewport = {};
            viewport.top = $(window).scrollTop();
            viewport.bottom = viewport.top + $(window).height();
            var bounds = {};
            bounds.top = this.offset().top;
            bounds.bottom = bounds.top + this.outerHeight();
            return (!(
                (bounds.top <= viewport.top) ||
                (bounds.bottom >= viewport.bottom)
            ));
        };
        if ($('li.current').length && !$('li.current').isFullyWithinViewport()) {
            $('.wy-nav-side').scrollTop(
                $('li.current').offset().top - $('.wy-nav-side').offset().top - 60
            );
        }
    });
})
