(function($){
$(document).ready(function(){
    var linkhtml = ' <a href="#" class="delete-d2c"><img src="' + portal_url + '/delete_icon.gif" alt="X" /></a>';
    var form = $('<form><input type="submit" name="submit" value="' + $('#d2c-i18n-messages .addNewType').text() + '" /></form>');
    var submitbtn = form.find('input');
    var widget = $('.template-base_edit .kssattr-atfieldname-entryType');
    var radios = widget.find('[name=entryType]').parent();
    if(widget.size() == 1){
        $.ajax({
            url: '@@has-d2c-type-permission',
            dataType: 'json',
            success: function(data){
                if(data.hasPermission){
                    widget.append(form);          
                    radios.find('label').filter(function(){
                        var html = $(this).html();
                        return $(this).prev().is('input') && $(this).prev().attr('value') != 'FormSaveData2ContentEntry';
                    }).append(linkhtml);
                }
            }
        });
    }
    
    $('a.delete-d2c').live('click', function(){
        var link = $(this);
        if(confirm($('#d2c-i18n-messages .confirmDeletion').text())){
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
                        input.next().remove(); // one more for the BR
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
        var name = prompt($('#d2c-i18n-messages .newTypeName').text());
        if (name) {
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
                        var last = radios.find('br:last');
                        input[0].checked = true;
                        last.after('<br />');
                        last.after(' <label> ' + data.title + linkhtml + '</label>');
                        last.after(input);
                    }else{
                        if (window.console) {
                            window.console.log('An error occurred trying to add. "' + data.msg + '"');
                        }
                    }
                }
            })
        }
        return false;  
    });

    var field = $('<div id="set-workflow-field" class="field"><label class="formQuestion"><span>' + $('#d2c-i18n-messages .newWorkflow').text() + '</span>:</label><br /></div>');
    var button = $('<button>' + $('#d2c-i18n-messages .assignHere').text() + '</button>');
    var content = $('#fieldset-default');
    if($('#archetypes-fieldname-avoidSecurityChecks').size() == 1){
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
                    if (window.console) {
                        console.log('An error occurred trying to get available workflows. "' + data.msg + '"');
                    }
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
})(jQuery)