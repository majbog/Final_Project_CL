


// Time Exp Form

$(function(){



    $(".datepicker").datepicker({
    dateFormat: "yy-mm-dd"
    });

    var lists = $(".absent-clerks");
    
    lists.each(function (i, e) {
        if ($(e).children().length > 2){
            var date_th = $(this).prev();
            var span = date_th.find($("span.badge-warning"));
            span.css("display", "inline")
        }

    });


  });