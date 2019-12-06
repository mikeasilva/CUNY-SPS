$(document).ready(function () {
    $.get("api/v1/options", function (options) {
        $("#dropdown").empty().html(options);
        //$("#stacked-viz-dropdown").html(options);
    });

    // UI EVENTS

    // Prevent form submission
    $("#form").submit(function (event) {
        event.preventDefault();
    });

    // Navigation menu click event handling
    $('.menu_item').click(function () {
        var wrapper_name = $(this).attr('data-section-id');
        $('main').attr('class', '').addClass(wrapper_name);
        $('.menu_item').removeClass('current');
        $(this).addClass('current');
    });

    // Button at the bottom of page click event handling
    $('.back_or_next').click(function () {
        var name = $(this).attr('data-menu-item-name');
        $('a[data-section-id=' + name + ']').click();
    });
});