$(document).ready(function () {
    //When the Add button is pressed the selected item is appended to the end of the dynamic list
    $(".dynamic-list-add").click(function(){
        //Need to find closest container element
        var dynamicContainer = $(this).closest('div.dynamic-list-container');
        
        //Select input field within this container which contains the new item to add
        var dynamicInput = $('.dynamic-list-new-item', dynamicContainer);     //selector-context - http://api.jquery.com/jquery/#selector-context
        
        //Append new item to list and clear input field 
        dynamicList_addNewItem(dynamicInput.val(), dynamicContainer);
        dynamicInput.val("");
    });   
});

function dynamicList_addNewItem(item, dynamicContainer){
    dynamicList = dynamicContainer.find(".dynamic-list");
    console.log(dynamicList)
    dynamicSelect = dynamicContainer.find(".dynamic-list-select");
    console.log(dynamicSelect)
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
        dynamicSelect.find("option[value='" + item + "']").remove();
    }; 
    new_span_button.appendChild(new_button);
    new_div.appendChild(new_span);
    new_div.appendChild(new_span_button);    
    new_li.appendChild(new_div);
    dynamicList.append(new_li);

    var new_option = document.createElement("option");
    new_option.text = item;
    new_option.value = item;
    dynamicSelect.append(new_option);
    new_option.selected = true;        //DJG - Works as long as you edit the choices of the select multiple form element in the view function before validating.
    
}


function dynamicList_addList(list, dynamicContainer) {
    var num_items = list.length;
    for (var i = 0; i < num_items; i++) {
        dynamicList_addNewItem(list[i], dynamicContainer); 
    }
}