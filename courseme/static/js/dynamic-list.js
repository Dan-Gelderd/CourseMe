$(document).ready(function () {
    //When the Add button is pressed the selected item is appended to the end of the dynamic list
    $(".dynamic-list-add").click(function(){
        //Need to find closest container element
        var $div = $(this).closest('div.dynamic-list-container');
        
        //Select input field within this container which contains the new item to add
        var $input = $('.dynamic-list-new-item', $div);    //selector-context - http://api.jquery.com/jquery/#selector-context
        
        //Select ul and select elements within this container to append new item to
        var $list = $('.dynamic-list', $div);        
        var $select = $('.dynamic-list-select', $div);
 
        //Append new item to list and clear input field 
        dynamicList_addNewItem($input.val(), $list, $select);
        $input.val("");
    });   
});

function dynamicList_addNewItem(item, $list, $select){
    new_li = document.createElement('li');
    new_li.setAttribute('class', 'list-group-item dynamic-list-item');
    new_div = document.createElement('div');
    new_div.setAttribute('class', 'input-group');
    new_span = document.createElement('span');
    new_span.setAttribute('class', 'dynamic-list-item-data');
    new_span.innerHTML = item;      //DJG - easier to have a separate span just containing the text we want as easier for jquery to read as innerText    
    new_span_button = document.createElement('span');
    new_span_button.setAttribute('class', 'input-group-btn');
    new_button = document.createElement('button');
    new_button.setAttribute('class', 'btn btn-link');
    new_button.setAttribute('type', 'button');
    new_button.innerHTML = "&times;";
    new_button.onclick = function() {
        $(this).closest('.dynamic-list-item').remove();      //DJG - passing jquery object as function parameter - http://forum.jquery.com/topic/jquery-passing-a-jquery-object-as-a-function-parameter
    };            
    new_span_button.appendChild(new_button);
    new_div.appendChild(new_span);
    new_div.appendChild(new_span_button);    
    new_li.appendChild(new_div);
    $($list).append(new_li);

    var new_option = document.createElement("option");
    new_option.text = item;
    $select.append(new_option);
    new_option.selected = false;        //DJG - Would be true. The validation fails if selecting things not defined in the choices attribute of the wtf selectmultiplefield object.
    
}