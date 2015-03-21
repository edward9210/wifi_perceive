var Client, ClientFilter, Config;
var sensing_results = new Array();

$.fn.extend({
    disableSelection: function() {
        return this.each(function() {
            if (typeof this.onselectstart !== 'undefined') {
                return this.onselectstart = function() {
                    return false;
                };
            } else if (typeof this.style.MozUserSelect !== 'undefined') {
                return this.style.MozUserSelect = 'none';
            } else {
                return this.onmusedown = function() {
                    return false;
                };
            }
        });
    }
});

compare = function(a, b) {
    if (a === b) {
        return 0;
    }
    if (a < b) {
        return -1;
    }
    return 1;
};

function mac_to_id(mac) {
    var id = "mac_";
    for (var i = 0; i < mac.length; i++) {
        if (mac[i] != ':')
            id += mac[i];
    }
    return id;
}


Config = {
    item_color: '#e3e3e3',
    item_color_blink: '#afa',
    query_interval: 500
};

ClientFilter = (function() {
    function ClientFilter(id) {
        this.id = id;
        this.filter = $('#' + this.id).addClass('filter').append($('<h2>').html('Clients').css({
            display: 'inline-block',
            marginRight: '20px'
        }));
        this.bar = $('<input type="text" placeholder="input text to filter">').addClass('bar').appendTo(this.filter).change((function(_this) {
            return function() {
                return _this.on_bar_change();
            };
        })(this)).keyup((function(_this) {
            return function() {
                return _this.on_bar_change();
            };
        })(this));

        this.table = $('<div>').appendTo(this.filter);
        this.selected = null;
        this.clients = [];
        this._clients_hash = {};

    }

    ClientFilter.prototype.on_bar_change = function() {
        var client, index, key, _i, _len, _ref, _results;
        key = this.bar.val();
        if (key.length === 0 || key === null) {
            key = '';
        }
        _ref = this.clients;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            client = _ref[_i];
            index = client.mac.indexOf(key);
            if (index >= 0) {
                _results.push(client.item.show());
            } else {
                _results.push(client.item.hide());
            }
        }
        return _results;
    };

    ClientFilter.prototype.add = function(client_mac) {
        var client;
        if (this._clients_hash[client_mac] != null) {
            return false;
        }
        client = new Client(client_mac);
        client.item = $('<div>').html(client.mac).disableSelection().addClass('item').addClass('mac').click((function(_this) {
            return function() {
                if (client.selected) {
                    return client.deselect();
                } else {
                    return client.select();
                }
            };
        })(this));
        this.table.append(client.item);
        this._clients_hash[client.mac] = client;
        this.clients.push(client);
        return true;
    };

    ClientFilter.prototype.get_by_mac = function(mac) {
        return this._clients_hash[mac];
    };

    ClientFilter.prototype.update = function(client_macs) {
        var changed, client_mac, _i, _len;
        changed = false;
        for (_i = 0, _len = client_macs.length; _i < _len; _i++) {
            client_mac = client_macs[_i];
            if (this.add(client_mac)) {
                changed = true;
            }
        }
        if (changed) {
            this.sort();
            this.on_bar_change();
        }
    };

    ClientFilter.prototype.sort = function() {
        this.clients.sort(function(a, b) {
            return compare(a.mac, b.mac);
        });
        this.clients.forEach((function(_this) {
            return function(client) {
                return _this.table.append(client.item);
            };
        })(this));
    };

    ClientFilter.prototype.get_selected = function() {
        return this.clients.filter(function(c) {
            return c.selected;
        });
    };

    return ClientFilter;

})();

Client = (function() {
    function Client(mac) {
        this.mac = mac;
        this.data = {};
        this.selected = false;
    }

    Client.prototype.blink = function() {
        this.item.css('background-color', Config.item_color_blink);
        return this.item.animate({
            backgroundColor: Config.item_color
        }, {
            duration: Config.query_interval / 2
        });
    };

    Client.prototype.select = function() {
        this.selected = true;
        var c_mac = this.mac;
        $('#result').append('<table ' + 'id="' + mac_to_id(c_mac) + '"></table>');
        $('#'+ mac_to_id(c_mac)).append('<tr><td>'+c_mac+'</td></tr>');

        return this.item.addClass('selected');
    };

    Client.prototype.deselect = function() {
        this.selected = false;
        var c_mac = this.mac;
        $('#'+ mac_to_id(c_mac)).remove();
        return this.item.removeClass('selected');
    };

    return Client;

})();

function update_data() {
    var client, clients;
    clients = client_filter.get_selected();
    $.ajax({
        method: 'get',
        url: '/ajax_monitor',
        dataType: 'json',
        success: function(data) {
            client_filter.update(data.clients);
            client_filter.sort();
        }
    });
    if (clients.length > 0) {
        return $.ajax({
        method: 'post',
        url: '/ajax_monitor',
        dataType: 'json',
        data: {
          clients: JSON.stringify((function() {
            var _i, _len, _results;
            _results = [];
            for (_i = 0, _len = clients.length; _i < _len; _i++) {
              client = clients[_i];
              _results.push(client.mac);
            }
            return _results;
          })())
        },
        success: function(data) {
            result = data.result;
            $('.remove').remove();
            for (var mac in result) {
                for (var ap_mac in result[mac])
                    $('#'+ mac_to_id(mac)).append('<tr class="remove"><td>'+ap_mac+'</td>'+ '<td>' + result[mac][ap_mac] + '</td>'  + '</tr>');
            }
        }
      });
    }
}

var client_filter;

function init() {
    client_filter = new ClientFilter('client_filter');
    setInterval(function() {return update_data();}, 1000);
}

$(document).ready(init);