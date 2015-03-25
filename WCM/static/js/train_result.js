function check_form(){
    var result_name = $('#result_name').val();
    if (result_name == '') {
        alert('result_name is null!');
        return false;
    }
    return true;
}

function init() {
    var tmp = $('#trees').val();
    $('#trees').val(JSON.stringify(tmp));
}

$(document).ready(init);