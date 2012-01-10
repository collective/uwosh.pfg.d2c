(function($){
$(document).ready(function(){
    var linkhtml = ' ( <a href="#" class="delete-d2c">X</a> )';
    var form = $('<form><input type="submit" name="submit" value="Add New Type" /></form>');
    var submitbtn = form.find('input');
    var widget = $('.template-base_edit.portaltype-formsavedata2contentadapter .kssattr-atfieldname-entryType');
    var radios = widget.find('#entryType');
    if(widget.size() == 1){
        $.ajax({
            url: '@@has-d2c-type-permission',
            dataType: 'json',
            success: function(data){
                if(data.hasPermission){
                    widget.append(form);          
                    radios.find('label').filter(function(){
                        var html = $(this).html();
                        return $(this).prev().attr('value') != 'FormSaveData2ContentEntry';
                    }).append(linkhtml);
                }
            }
        });
    }
    
    $('a.delete-d2c').live('click', function(){
        var link = $(this);
        if(confirm('Are you sure you want to delete this type? If you have existing items of this type, it could screw things up!')){
            $('#kss-spinner').show();
            $.ajax({
                url: '@@delete-d2c-type',
                data: {
                    id: link.parent().prev().attr('value')
                },
                type: 'POST',
                dataType: 'json',
                success: function(data){
                    $('#kss-spinner').hide();
                    if(data.status == 'success'){
                        var id = data.id;
                        var input = widget.find('input[value="' + id + '"]');
                        input.next().remove();
                        input.remove();
                    }else{
                        alert('An error occurred trying to delete. "' + data.msg + '"');
                    }
                }
            });
        }
        return false; 
    });

    submitbtn.click(function(){
        var name = prompt("Please enter a name for the type.");
        $('#kss-spinner').show();
        $.ajax({
            url : '@@add-d2c-type',
            data : {
                name: name
            },
            type: 'POST',
            dataType: 'json',
            success: function(data){
                $('#kss-spinner').hide();
                if(data.status == 'success'){
                    var input = $('<input type="radio" value="' + data.id + '" name="entryType" class="noborder blurrable" /> ');
                    radios.append(input);
                    input[0].checked = true;
                    radios.append(' <label> ' + data.title + linkhtml + '</label>');
                    radios.append('<br />');
                }else{
                    alert('An error occurred trying to add. "' + data.msg + '"');
                }
            }
        })
        return false;  
    });

    //var button = $('<button type="submit">Set Workflow Here</button>');
    var field = $('<div id="set-workflow-field" class="field"><label class="formQuestion"><span>Assign Workflow Here</span>:</label><br /></div>');
    var button = $('<button>Assign Here</button>');
    var content = $('.portaltype-formsavedata2contentadapter.template-base_view #content-core');
    if($('.portaltype-formsavedata2contentadapter.template-base_view #archetypes-fieldname-avoidSecurityChecks').size() == 1){
        $('#kss-spinner').show();
        $.ajax({
            url: '@@d2c-availabe-workflows',
            dataType: 'json',
            success: function(data){
                $('#kss-spinner').hide();
                if(data.status == 'success'){
                    var select = $('<select><option value="default">Default</option></select>');
                    field.append(select);
                    workflows = data.workflows;
                    for(var i=0; i<workflows.length; i++){
                        var workflow = workflows[i];
                        var workflowele = $('<option value="' + workflow.id + '">' + workflow.title + '</option>');
                        if(workflow.selected){
                            workflowele[0].selected = true;
                        }
                        select.append(workflowele);
                    }

                    field.append(button);
                    content.prepend(field);
                }else{
                    console.log('An error occurred trying to get available workflows. "' + data.msg + '"');
                }
            }
        });
    }
    button.click(function(){
        $('#kss-spinner').show();
        $.ajax({
            url: '@@d2c-assign-workflow',
            type: 'POST',
            data: {
                id: $('#set-workflow-field select').val()
            },
            dataType: 'json',
            success: function(data){
                $('#kss-spinner').hide();
                if(data.status == 'success'){
                    alert('Workflow policy successfully set.')
                }else{
                    alert('An error occurred trying to assign workflow. "' + data.msg + '"');
                }
            }
        })
        return false; 
    });
});
})(jq)