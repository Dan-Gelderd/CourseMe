$(document).ready(function () {

    $('#new_prerequisite_form_group').find('.dynamic-list-new-item-label').text("Enter new prerequisite for this objective");
    $('#new_prerequisite_form_group').find('.dynamic-list-heading').text("Prerequisites");    


    //DJG - could add choices here - but can't use jinja2 templating in js files? 
    //{% for topic in g.user.subject.topics %}
    //new_topic = document.createElement('option');
    //new_topic.setAttribute('value', 'topic.id');
    //new_topic.setAttribute('text', 'topic.name'); 
    //$("#edit_objective_topic").append(new_topic);
    //{% endfor %}
    
    //Button to bring up new empty form modal to create a new objective with prerequisites
    $("#create_objective").click(function(){
        var form = $("#edit_objective_form");
        $("#id", form).val("");
        $("#name", form).val("");
        $("#subject", form).attr("disabled", false);            
        form.find(".dynamic-list-new-item").val("");
        form.find(".help-block").text("");
        form.find(".has-error").removeClass("has-error");
        form.find(".dynamic-list-item").remove();
        $("#edit_objective_modal").modal('show');
        return false;
    });

    //Button to post the new or updated objective data to the server for validation and storage
    $("#save_objective").click(function(event){
        event.preventDefault(); 
        var prerequisites = new Array();
        $("#edit_objective_form").find("#subject").attr("disabled", false);              //Serialize array won't include disabled elements
        
        var data = $("#edit_objective_form").serializeArray();     //DJG - http://stackoverflow.com/questions/6627936/jquery-post-with-serialize-and-extra-data

        console.log(prerequisites);
        console.log(data);          //DJG - not sure why edit_objective_id is getting repeated in the data array
        //console.log($(".dynamic-list-select").serialize());
        //console.log($(".dynamic-list-select").options[0].selected);

        //data_json = JSON.stringify(data)        //DJG - Played with alternatives to passing data back that allows the list of prerequisites to be parsed as a list object by the view function. This approach leaves the wtf form unpopulated so fails validation and no csrf, needs reviewing
        //console.log(jQuery.isPlainObject( data ));
        //console.log(typeof data);
        //console.log(data_json);      
        //console.log(jQuery.isPlainObject( data_json ));
        //console.log(typeof data_json);        


        $.post(flask_util.url_for('main.objective_add_update'), data)
            .done(function(response) {  // on success
                var result = $.parseJSON(response);
                $("#edit_objective_modal").modal('hide');
                location.reload();
            })
            .fail(function(response) {  // on failure
                var result = $.parseJSON(response.responseText);
                if(result.errors.name) {
                    $("#error_edit_objective_name").text(result.errors.name);
                    $("#edit_objective_name_form_group").addClass("has-error");
                }

                if(result.errors.subject) {
                    $("#error_edit_objective_subject").text(result.errors.subject);
                    $("#edit_objective_subject_form_group").addClass("has-error");
                }

                if(result.errors.prerequisites) {
                    $("#edit_objective_form").find(".dynamic-list-help").text(result.errors.prerequisites);
                    $("#edit_objective_form").find(".dynamic-list-form").addClass("has-error");
                }
            });
    });
    
//    $(function() {            DJG - could use ajax to get the list of objectives here, better to move this bit to the individual templates as may also want to autopopulate other stuff and already have objective list there
//        
//        var availableTags = [];
//        {% for objective in objectives %}
//            availableTags.push('{{ objective.name }}')    
//        {% endfor %}    
//
//        $( "#new_prerequisite" ).autocomplete({
//            source: availableTags
//        });
//    });
//    

});

function loadEditObjectiveModal(objective) {
    var form = $("#edit_objective_form");
    $("#id", form).val(objective.id);
    $("#name", form).val(objective.name);
    $("#topic_id", form).val(objective.topic_id);
    //$("#subject", form).disabled = true;             DJG - think this is better
    form.find(".dynamic-list-new-item").val("");
    form.find(".help-block").text("");
    form.find(".has-error").removeClass("has-error");
    form.find(".dynamic-list-item").remove();
    dynamicList_addList(objective.prerequisites, form);
    $("#edit_objective_modal").modal('show');
    return false;
}
