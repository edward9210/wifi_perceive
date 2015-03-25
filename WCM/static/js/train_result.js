function check_form(){
    var result_name = $('#result_name').val();
    if (result_name == '') {
        alert('result_name is null!');
        return false;
    }
    return true;
}

function init() {}

$(document).ready(init);