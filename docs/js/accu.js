MathJax = {
    tex: { inlineMath: [['$', '$']] },
    svg: {
        fontCache: 'global',
        displayAlign: 'left',
    },
};

$(document).ready(function () {
    $(function () {
        if ($('li.current').length) {
            $('.wy-nav-side').scrollTop(
                $('li.current').offset().top - $('.wy-nav-side').offset().top - 90
            );
        }
    });
})
