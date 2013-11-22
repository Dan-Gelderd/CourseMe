$(document).ready(function(){
    bindEventToNavigation();
    showBreadCrumb(); //Show the breadcrumb when you arrive on the new page
});

function bindEventToNavigation(){
    $.each($("#navigation_links > li > a"), function(index, element){
        $(element).click(function(event){
            breadcrumbStateSaver($(this).attr('href'), $(this).text());
            showBreadCrumb();
        });
    });
}

function breadcrumbStateSaver(link, text) {
    if (typeof (Storage) != "undefined") {
        if (sessionStorage.breadcrumb) {
            var breadcrumb = sessionStorage.breadcrumb;
            sessionStorage.breadcrumb = breadcrumb + " >> <a href='" + link + "'>" + text + "</a>";
        } else {
            sessionStorage.breadcrumb = "<a href='" + link + "'>" + text + "</a>";
        }
    }
}

function showBreadCrumb(){
    $("#breadcrumb").html(sessionStorage.breadcrumb);   
}
