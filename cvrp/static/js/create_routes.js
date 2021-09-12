function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}

function cloneMore(selector, prefix, element_name) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + prefix + '-TOTAL_FORMS').val();
    newElement.find(':input:not([type=button]):not([type=submit]):not([type=reset])').each(function() {
      var name = $(this).attr('name').replace('-' + (total-1) + '-', '-' + total + '-');
      var id = 'id_' + name;
      $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.find('label').each(function() {
      var forValue = $(this).attr('for');
      if (forValue) {
        forValue = forValue.replace('-' + (total-1) + '-', '-' + total + '-');
        $(this).attr({'for': forValue});
      }
      console.log(forValue);
    });
    total++;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);

    updateAddButton(element_name);
    return false;
}

function updateAddButton(element_name) {
    var conditionRow = $('.' + element_name + '-row:not(:last)');
    conditionRow.find('.btn.add-' + element_name + '-row')
    .removeClass('btn-success').addClass('btn-danger')
    .removeClass('add-' + element_name + '-row').addClass('remove-' + element_name + '-row')
    .html('-');
}

function deleteForm(prefix, btn, element_name) {
    var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    if (total > 1){
        btn.closest('.' + element_name + '-row').remove();
        var forms = $('.' + element_name + '-row');
        $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
        for (var i=0, formCount=forms.length; i<formCount; i++) {
            $(forms.get(i)).find(':input').each(function() {
                updateElementIndex(this, prefix, i);
            });
        }
    }
    return false;
}

window.onload = function() {
    counter = 1
    if (counter > 1) {
        location.reload();
        document.getElementById('dataForm').reset();
        counter++;
    }
}

$(document).on('click', '.add-driver-row', function(e){
    e.preventDefault();
    cloneMore('.driver-row:last', 'drivers', 'driver');
    console.log('Clicked addition');
    return false;
});

$(document).on('click', '.remove-driver-row', function(e){
    e.preventDefault();
    deleteForm('drivers', $(this), 'driver');
    console.log('Clicked deletion');
    return false;
});

$(document).on('click', '.add-location-row', function(e){
    e.preventDefault();
    cloneMore('.location-row:last', 'locations', 'location');
    console.log('Added location');
    return false;
});

$(document).on('click', '.remove-location-row', function(e){
    e.preventDefault();
    deleteForm('locations', $(this), 'location');
    console.log('Deleted location');
    return false;
});