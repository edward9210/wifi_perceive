function update_data() {
    var mac = $('#client_mac').val();
    $.ajax({
        method: 'post',
        url: '/ajax_sample',
        dataType: 'json',
        data: {
            client_mac : mac,
        },
        success: function(data) {
            $('#data_display_area').empty();
            $('#data_display_area').append('<table></table>');
            for (var i = data.length - 1; i >= 0; i--) {
                var num = i + 1;
                $('#data_display_area table').append('<tr>' + '<td>' + num + '</td>' + '<td>' + JSON.stringify(data[i]) + '</td>' + '</tr>')
            }
        }
    });
}

function init() {
    setInterval(function() {return update_data();}, 1000);
}

$(document).ready(init);