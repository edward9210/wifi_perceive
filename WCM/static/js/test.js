function check_form(){
    var sampled_data = $('#sampled_data').val();
    if (sampled_data == null) {
        alert('sampled data is null!');
        return false;
    }
    var test_data = $('#test_data').val();
    if (test_data == null) {
        alert('select to test is null!');
        return false;
    }
    return true;
}

function init() {}

$(document).ready(init);