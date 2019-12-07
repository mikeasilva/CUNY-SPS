var all_data;
var geoid;
var key = 0;
var viz_mode = "animated";
var viz_data;
var viz_plotly_data;
var viz_timeout = 1000;

var viz_plotly_layout = {
    xaxis: { range: [0, 60] },
    showlegend: false,
    title: "Share of Households by Income Level (%)"
};

var viz_plotly_options = {
    responsive: true,
    scrollZoom: false,
    showLink: false
};

function x() {
    viz_data = all_data[geoid];
    return [Math.round(viz_data[key]["low_share"] * 100, 0), Math.round(viz_data[key]["middle_share"] * 100, 0), Math.round(viz_data[key]["upper_share"] * 100, 0)];
}

function update_viz() {
    if(viz_mode == "animated"){
        Plotly.animate("viz", {
            data: [{ x: x(), }],
            traces: [0],
            layout: {}
        }, {
            transition: {
                duration: 500,
                easing: "cubic-in-out"
            },
            frame: {
                duration: 500
            }
        });
    } else {
        plot_stacked_bar_chart();
    }
}

function change_dropdown() {
    if ($("#dropdown option:selected").val() == "36123") {
        $("#dropdown option:selected").attr("selected", false);
        $("#dropdown option:first").attr("selected", "selected");
    } else {
        $("#dropdown option:selected").attr("selected", false).next().attr("selected", "selected");
    }
}

function plot_stacked_bar_chart() {
    var stacked_viz_layout = {
        barmode: "overlay",
        xaxis: {type: "category"},
        title: "Are Households Moving Up or Down?"
    };

    geoid = $("#dropdown").val();
    var high = {
        x: [],
        y: [],
        textposition: "auto",
        name: "High",
        hoverinfo: "none",
        marker: {color: "#d63031"},
        type: "bar"
    };

    var middle = {
        x: [],
        y: [],
        textposition: "auto",
        name: "Middle",
        hoverinfo: "none",
        marker: {color: "#0984e3"},
        type: "bar"
    };

    var low = {
        x: [],
        y: [],
        textposition: "auto",
        name: "Low",
        hoverinfo: "none",
        marker: {color: "#fdcb6e"},
        type: "bar"
    };

    low_vals = [];
    middle_vals = [];
    high_vals = [];

    $.each(all_data[geoid], function (index, d) {
        l = Math.round(d["low_share"] * 100, 0);
        m = Math.round(d["middle_share"] * 100, 0);
        h = Math.round(d["upper_share"] * 100, 0);
        low_vals[index] = l + "%";
        middle_vals[index] = m + "%";
        high_vals[index] = h + "%";
        low["x"][index] = middle["x"][index] = high["x"][index] = d["label"];
        low["y"][index] = l * -1;
        middle["y"][index] = m;
        high["y"][index] = m + h;
    });

    low["text"] = low_vals.map(String);
    middle["text"] = middle_vals.map(String);
    high["text"] = high_vals.map(String);

    Plotly.newPlot("viz", [high, middle, low], stacked_viz_layout, {responsive: true});
}

function plot_animated_bar_chart(){
    viz_plotly_data = [{
        type: "bar",
        x: x(),
        y: ["Low ", "Middle ", "High "],
        orientation: "h",
        marker: {color: ["#fdcb6e", "#0984e3", "#d63031"]},
    }];

    Plotly.newPlot("viz", viz_plotly_data, viz_plotly_layout, viz_plotly_options);
}

function change_viz() {
    var auto_advance = !$("#auto_advance_toggle").prop("checked");
    var chart_showing = $("main").hasClass("part_1");
    if(chart_showing){
        if(viz_mode == "animated"){
            viz_timeout = 1000;
            if (auto_advance) {
                key++;
                if (key == 5) {
                    change_dropdown();
                    key = 0;
                }
                $("#slider").val(key);
                update_viz();
            } 
        } else {
            viz_timeout = 3000;
            if(auto_advance){
                change_dropdown();
            }
            update_viz();
        }
    }
    setTimeout(change_viz, viz_timeout);
}


function init(){
    viz = $("#viz_container").addClass("viz");
    geoid = $("#dropdown").val();

    $.get("api/v1/options", function (options) {
        $("#dropdown").empty().html(options);
    });

    $.getJSON("api/v1/all-data", function (response) {
        all_data = response;
        plot_animated_bar_chart();
        // Start the auto advancer
        setTimeout(change_viz, viz_timeout);
    });
}



$(document).ready(function () {
    var geoid = $("#dropdown").val();
    // UI EVENTS
    $("#slider").change(function () {
        key = $(this).val();
        update_viz();
    });

    $("a.chart_options_button").click(function(){
        viz_mode = $(this).data("viz");
        $("#chart_options").removeClass().addClass(viz_mode);
        $('#viz_container').removeClass().addClass(viz_mode);
        if(viz_mode == "animated"){
            plot_animated_bar_chart();
        } else {
            plot_stacked_bar_chart();
        }
    });

    $("#dropdown").change(function () {
        key = 0;
        geoid = $("#dropdown").val();
        $("#slider").val(key);
        update_viz();
    });

    $("#auto_advance_toggle").change(function(){
        manual_mode = $(this).is(":checked");
        if(manual_mode){
            $("#slider").removeClass("slider_inactive").addClass("slider_active");
        } else {
            $("#slider").removeClass("slider_active").addClass("slider_inactive");
        }
    });

    // Prevent form submission
    $("#form").submit(function (event) {
        event.preventDefault();
    });

    // Navigation menu click event handling
    $(".menu_item").click(function () {
        var wrapper_name = $(this).attr("data-section-id");
        $("main").attr("class", "").addClass(wrapper_name);
        $(".menu_item").removeClass("current");
        $(this).addClass("current");
    });

    // Button at the bottom of page click event handling
    $(".back_or_next").click(function () {
        var name = $(this).attr("data-menu-item-name");
        $("a[data-section-id=" + name + "]").click();
    });

    init();
});