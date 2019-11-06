$(document).ready(function () {
    $(function () {
        MathJax = {
            tex: { inlineMath: [['$', '$']] },
            svg: { 
                fontCache: 'global' ,
                displayAlign: 'left',
            },
        };
    })

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
