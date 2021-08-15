
$(document).ready(function(){
    document.getElementById('btn-spinner').classList.add('not-visible');
    document.getElementById('btn-load').classList.remove('not-visible');
});

$(document).on('click', '#btn-load', function(){
    document.getElementById('btn-spinner').classList.remove('not-visible');
    document.getElementById('btn-load').classList.add('not-visible');
});
