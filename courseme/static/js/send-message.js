$(document).ready(function () {
    $("#send_message").click(function(event){
        event.preventDefault();
        
        var data = $("#send_message_form").serializeArray();     //DJG - http://stackoverflow.com/questions/6627936/jquery-post-with-serialize-and-extra-data
        
        $.post(  
            flask_util.url_for('send_message'),  
            data,  
            function(json) {
                
                console.log(json);
                
                var result = $.parseJSON(json);
                console.log(result);
                console.log(result["savedsuccess"]);
                console.log(result.savedsuccess);                
                
                $("#send_message_form").find(".help-block").text("");
                            
                if(result.savedsuccess)
                {
                    $("#send_message_modal").modal('hide');
                    location.reload();
                }
                else
                {       
                    if(result.message_type!=undefined) {
                        $("#error_message_type").text(result.message_type[0]);
                        $("#message_type_form_group").addClass("has-error");
                    }
                    if(result.message_to!=undefined) {
                        $("#error_message_to").text(result.message_to[0]);
                        $("#message_to_form_group").addClass("has-error");
                    }    
                    if(result.message_subject!=undefined) {
                        $("#error_message_subject").text(result.message_subject[0]);
                        $("#message_subject_form_group").addClass("has-error");
                    }
                    if(result.message_body!=undefined) {
                        $("#error_message_body").text(result.message_body[0]);
                        $("#message_body_form_group").addClass("has-error");
                    }
                    if(result.recommended_material!=undefined) {
                        $("#error_recommended_material").text(result.recommended_material[0]);
                        $("#recommended_material_form_group").addClass("has-error");
                    }
                    if(result.request_access!=undefined) {
                        $("#error_request_access").text(result.request_access[0]);
                        $("#request_access_form_group").addClass("has-error");
                    }    
                }
            }
        );
    });   
});