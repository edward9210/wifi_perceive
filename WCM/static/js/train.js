function click_data(event) {
    var target = event.target;
    var data_name = target.innerHTML;
    $.ajax({
        method: 'post',
        url: '/ajax_train',
        dataType: 'json',
        data: {
            name : data_name,
        },
        success: function(data) {
            $('#data_display').empty();
            $('#data_display').append('(name : ' + data.name + ' , type : ' + data.type + ')');
            $('#data_display').append('<table></table>');
            for (var i = 0; i < data.data.length - 1; i++) {
                var num = i + 1;
                $('#data_display table').append('<tr>' + '<td>' + num + '</td>' + '<td>' + JSON.stringify(data.data[i]) + '</td>' + '</tr>')
            }
        }
    });
}

function check_form(){
    if ($('#selectedToTrain').children().length == 0) {
        alert('you don\'t select data to train!');
        return false;
    }
    if ($('#selectedToTrain').children().length == 1) {
        alert('you should select >=2 data to train!');
        return false;
    }
    var percentage = $('#percentage').val();
    if (percentage == '') {
        alert('percentage is null!');
        return false;
    }
    if (Number(percentage) <= 0 || Number(percentage) >= 100){
        alert('percentage error(Please input 1-99)!');
        return false;
    }
    var tree_num = $('#tree_num').val();
    if (tree_num == '') {
        alert('tree_num is null!');
        return false;
    }
    if (Number(tree_num) <= 0){
        alert('tree_num error(Please input a number larger than 0)!');
        return false;
    }
    return true;
}

function init() {
    $( "#sampledDataList, #selectedToTrain" ).sortable({
        connectWith: ".connectedSortable"
    });
}

$(document).ready(init);