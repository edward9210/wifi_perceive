function check_form(){
    var type = $('#type').val();
    if (type == '') {
        alert('type is null!');
        return false;
    }
    return true;
}

function init() {}

$(document).ready(init);